# rb_ingestor/management/commands/automacao_render_fixed.py
"""
Comando de automação CORRIGIDO para Render
Versão que busca notícias específicas e gera conteúdo baseado nelas
"""
import os
import sys
import django
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
from datetime import datetime, timedelta
import random
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Automação CORRIGIDA que busca notícias específicas e gera conteúdo baseado nelas"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=3, help="Número de artigos a criar")
        parser.add_argument("--force", action="store_true", help="Força execução")
        parser.add_argument("--debug", action="store_true", help="Modo debug")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        self.stdout.write("=== AUTOMACAO RENDER RADARBR CORRIGIDA ===")
        self.stdout.write(f"Executado em: {timezone.now()}")
        
        # Verificar se deve executar
        if not options["force"] and not self._should_execute():
            self.stdout.write("PULANDO - timing não otimizado")
            return
        
        # Obter notícias específicas (não apenas tópicos)
        news_articles = self._get_specific_news()
        if not news_articles:
            self.stdout.write("ERRO: Nenhuma notícia específica encontrada")
            return
        
        # Executar automação baseada em notícias reais
        created_count = self._execute_automation_from_news(news_articles, Noticia, Categoria, options["limit"])
        
        # Resultado
        self.stdout.write(self.style.SUCCESS(f"OK: {created_count} notícias criadas"))
        
        # Ping sitemap se criou algo
        if created_count > 0:
            self._ping_sitemap()

    def _should_execute(self):
        """Verifica se deve executar baseado em timing"""
        Noticia = apps.get_model("rb_noticias", "Noticia")
        
        # Verificar notícias recentes (últimas 3 horas)
        recent_count = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=3)
        ).count()
        
        # Executar se menos de 2 notícias recentes
        return recent_count < 2

    def _get_specific_news(self):
        """Busca notícias específicas do Google News"""
        try:
            from gnews import GNews
            
            # Configurar GNews
            google_news = GNews(
                language='pt', 
                country='BR', 
                period='1d', 
                max_results=10,
                exclude_websites=['youtube.com', 'instagram.com', 'facebook.com']
            )
            
            # Buscar notícias específicas
            articles = google_news.get_top_news()
            if not articles:
                return []
            
            # Filtrar e processar notícias
            processed_news = []
            for article in articles[:5]:
                if self._is_valid_news_article(article):
                    processed_news.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_date': article.get('published date', ''),
                        'source': article.get('publisher', {}).get('title', ''),
                        'topic': self._extract_main_topic(article.get('title', ''))
                    })
            
            return processed_news
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro Google News: {e}")
            return []

    def _is_valid_news_article(self, article):
        """Verifica se é uma notícia válida"""
        title = article.get('title', '')
        description = article.get('description', '')
        
        # Verificar se tem título e descrição
        if not title or not description:
            return False
        
        # Verificar tamanho mínimo
        if len(title) < 20 or len(description) < 50:
            return False
        
        # Verificar se não é muito genérico
        generic_words = ['notícias', 'últimas', 'hoje', 'agora', 'atualizações']
        if any(word in title.lower() for word in generic_words):
            return False
        
        return True

    def _extract_main_topic(self, title):
        """Extrai o tópico principal do título"""
        # Palavras comuns para remover
        common_words = [
            'no', 'do', 'da', 'em', 'para', 'com', 'por', 'que', 'é', 'foi', 
            'ser', 'ter', 'há', 'mais', 'menos', 'sobre', 'após', 'durante', 
            'entre', 'até', 'desde', 'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 
            'umas', 'de', 'e', 'ou', 'mas', 'se', 'não', 'já', 'ainda', 'também', 
            'só', 'muito', 'pouco', 'todo', 'toda', 'todos', 'todas', 'cada', 
            'qual', 'quando', 'onde', 'como', 'porque', 'porquê', 'por que', 'por quê'
        ]
        
        # Limpar título
        title_clean = title.lower()
        words = title_clean.split()
        
        # Remover palavras comuns
        relevant_words = [word for word in words if word not in common_words and len(word) > 3]
        
        if relevant_words:
            # Pegar as 2-3 palavras mais relevantes
            topic = ' '.join(relevant_words[:3])
            return topic
        
        return title[:50]  # Fallback para primeiras 50 caracteres

    def _execute_automation_from_news(self, news_articles, Noticia, Categoria, limit):
        """Executa a automação baseada em notícias específicas"""
        created_count = 0
        
        for i, article in enumerate(news_articles[:limit]):
            try:
                # Resolver URL original do Google News (se for link do GN)
                original_url = self._resolve_original_url(article.get('url', ''))
                if original_url:
                    article['url'] = original_url
                    article['original_url'] = original_url
                # Gerar conteúdo baseado na notícia específica
                title, content = self._generate_content_from_news(article)
                
                # Categorizar baseado no conteúdo da notícia
                categoria = self._get_category_from_news(article, Categoria)
                
                # Verificar duplicatas
                if self._check_duplicate(title, Noticia):
                    self.stdout.write(f"⚠ Pulando duplicata: {title}")
                    continue
                
                # Criar notícia
                # Garantir unicidade de slug e fonte_url
                ts = timezone.now().strftime('%Y%m%d%H%M%S')
                fonte_url_value = article.get('url') or f"render-automation-{ts}-{i}"
                # Se já existir, anexar sufixo único
                if Noticia.objects.filter(fonte_url=fonte_url_value).exists():
                    fonte_url_value = f"{fonte_url_value}?t={ts}{i}"

                noticia = Noticia.objects.create(
                    titulo=title,
                    slug=f"{slugify(title)[:120]}-{ts}",
                    conteudo=content,
                    publicado_em=timezone.now(),
                    categoria=categoria,
                    fonte_url=fonte_url_value,
                    fonte_nome=article.get('source', 'RadarBR Automation'),
                    status=1  # PUBLICADO
                )
                
                # Adicionar imagem específica
                self._add_specific_image(noticia, article)
                
                created_count += 1
                self.stdout.write(f"✓ Criado: {title}")
                
            except Exception as e:
                self.stdout.write(f"❌ Erro ao criar notícia: {e}")
                continue
        
        return created_count

    def _resolve_original_url(self, url: str) -> str:
        """Resolve URL do Google News para o link do veículo original."""
        try:
            if not url:
                return ""
            if 'news.google.' not in url:
                return url
            import requests
            from urllib.parse import urlparse, parse_qs
            # 1) Query param "url"
            try:
                parsed = urlparse(url)
                qs = parse_qs(parsed.query)
                if 'url' in qs and qs['url']:
                    candidate = qs['url'][0]
                    if candidate and 'news.google.' not in candidate:
                        return candidate
            except Exception:
                pass
            # 2) Follow redirects
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            resp = session.get(url, timeout=20, allow_redirects=True)
            resp.raise_for_status()
            final_url = resp.url
            if final_url and 'news.google.' not in final_url:
                return final_url
        except Exception:
            return ""
        return ""

    def _generate_content_from_news(self, article):
        """Gera conteúdo baseado na notícia específica"""
        try:
            # 1) Extrair texto base do publisher para calcular alvo por margem de 15%
            base_words = None
            try:
                from rb_ingestor.news_content_extractor import NewsContentExtractor
                extractor = NewsContentExtractor()
                data = extractor.extract_content_from_url(article.get('original_url') or article.get('url') or '')
                if data and data.get('content'):
                    base_words = len((data['content'] or '').split())
                    self.stdout.write(f"🔍 Conteúdo completo extraído: {base_words} palavras")
            except Exception as e:
                self.stdout.write(f"⚠ Falha ao extrair conteúdo base: {e}")

            # 2) Definir alvo dinâmico
            if base_words and base_words >= 80:
                target_min = int(round(base_words * 0.85))
                target_max = int(round(base_words * 1.15))
                self.stdout.write(f"📊 Notícia base completa: {base_words} palavras")
                self.stdout.write(f"🎯 Margem 15%: {target_min}-{target_max} palavras")
            else:
                target_min = 800
                target_max = 1100
                self.stdout.write("📊 Base insuficiente; usando alvo padrão 800-1100 palavras")

            # 3) Gerar com IA melhorada com retry
            from rb_ingestor.ai_enhanced import generate_enhanced_article

            def _attempt_generate() -> dict | None:
                return generate_enhanced_article(article.get('topic', ''), article, max(target_min, 600))

            for attempt in (1, 2):
                ai_content = _attempt_generate()
                if not ai_content:
                    self.stdout.write(f"⚠ Tentativa {attempt}: IA não retornou conteúdo")
                    continue

                title = strip_tags(ai_content.get("title", article.get('title', '')))[:200]
                html = ai_content.get("html", "<p></p>")
                content = f'<p class="dek">{strip_tags(ai_content.get("dek", article.get('description', '')))[:220]}</p>\n{html}'

                # Contar palavras reais do corpo
                try:
                    from django.utils.html import strip_tags as dj_strip
                    word_count = len(dj_strip(content).split())
                except Exception:
                    word_count = ai_content.get('word_count', 0)

                quality_score = ai_content.get('quality_score', 0)

                # 4) Validação: faixa alvo; tolerância 80% apenas se base muito grande
                accept = False
                if word_count >= target_min and word_count <= target_max:
                    accept = True
                else:
                    if base_words and base_words >= 1200 and word_count >= int(target_min * 0.8):
                        accept = True

                if accept and quality_score >= 40:
                    self.stdout.write(f"✅ IA gerou {word_count} palavras (qualidade: {quality_score}%) — aceito")
                    return title, content

                self.stdout.write(f"⚠ IA gerou {word_count} palavras (qualidade: {quality_score}%), fora dos critérios — retry {attempt}/2")

            # 5) Se falhar após duas tentativas, pular publicação (sem fallback)
            raise RuntimeError("IA não atingiu critérios de palavras/qualidade após retries")

        except Exception as e:
            self.stdout.write(f"❌ Publicação cancelada: {e}")
            # Propagar exceção para que o caller pule este artigo
            raise

    def _generate_title_from_news(self, article):
        """Título PRÓPRIO otimizado para SEO, inspirado no original sem copiar."""
        import re
        topic = article.get('topic', '') or ''
        original = (article.get('title') or '').strip()
        description = (article.get('description') or '').strip()

        # Limpeza de marcas/portais
        portals = ['G1','Globo','Folha','Estadão','UOL','Terra','R7','IG','Exame','Metrópoles','O Globo','CNN','BBC','Reuters']
        clean = original
        for p in portals:
            clean = clean.replace(f' - {p}', '').replace(f' | {p}', '').replace(f' ({p})', '')

        # Palavras‑chave
        stop = {'de','da','do','das','dos','para','por','com','sem','uma','um','o','a','os','as','e','ou','no','na','nos','nas','em','ao','aos','à','às','que','sobre','após','contra','entre','como','mais','menos','hoje'}
        text_ref = f"{clean} {description}".lower()
        words = [w.strip(',.:;!?"()') for w in text_ref.split()]
        keys = []
        seen = set()
        for w in words:
            if len(w) > 2 and w not in stop and w not in seen:
                seen.add(w); keys.append(w)
        keys = keys[:6]

        base_topic = topic.title().strip() or 'Notícia'
        
        # Estruturas de título mais naturais e variadas
        estruturas = []
        
        # Estrutura 1: Declaração direta (sem dois pontos)
        if any(word in text_ref for word in ['dividendos', 'juros', 'impostos']):
            estruturas.append(f"{base_topic} {keys[0].title()} — valores e datas" if keys else None)
            estruturas.append(f"{base_topic} {keys[0].title()} para acionistas" if keys else None)
        
        # Estrutura 2: Com dois pontos (apenas para explicações)
        if any(word in text_ref for word in ['acordo', 'parceria', 'medidas']):
            estruturas.append(f"{base_topic} {keys[0].title()}: entenda os detalhes" if keys else None)
            estruturas.append(f"{base_topic} {keys[0].title()}: o que muda" if keys else None)
        
        # Estrutura 3: Interrogativa (para engajamento)
        if any(word in text_ref for word in ['anuncia', 'divulga', 'confirma']):
            estruturas.append(f"O que {base_topic} anuncia sobre {keys[0].title()}?" if keys else None)
            estruturas.append(f"Como {base_topic} atua em {keys[0].title()}?" if keys else None)
        
        # Estrutura 4: Declaração simples (mais natural)
        estruturas.append(f"{base_topic} {keys[0].title()}" if keys else None)
        estruturas.append(f"{base_topic} {keys[0].title()} hoje" if keys else None)
        
        # Estrutura 5: Com traço (mais elegante)
        estruturas.append(f"{base_topic} {keys[0].title()} — análise completa" if keys else None)
        estruturas.append(f"{base_topic} {keys[0].title()} — impactos e próximos passos" if keys else None)
        
        # Padrões originais como fallback
        patterns = [
            lambda ks: f"{base_topic}: {ks[0].title()} e {ks[1].title()} — entenda" if len(ks) >= 2 else None,
            lambda ks: f"{base_topic} hoje: {ks[0].title()} em foco" if ks else None,
            lambda ks: f"{clean} — impactos e próximos passos"[:140],
        ]
        
        # Adicionar padrões originais às estruturas
        for pattern in patterns:
            estruturas.append(pattern(keys))

        def norm(s):
            return re.sub(r'\s+', ' ', s.lower()).strip()
        orig_n = norm(original)
        
        # Testar todas as estruturas
        for estrutura in estruturas:
            if not estrutura:
                continue
            if 20 <= len(estrutura) <= 140 and norm(estrutura) != orig_n:
                return estrutura
                
        fallback = f"{clean} — análise" if clean else f"{base_topic}: Últimas Notícias"
        return fallback[:140]

    def _generate_content_from_news_fallback(self, article):
        """Gera conteúdo fallback baseado na notícia específica"""
        title = article.get('title', '')
        description = article.get('description', '')
        source = article.get('source', '')
        topic = article.get('topic', '')
        
        content = f"""<p class="dek">{description}</p>

<h2>{title}</h2>

<p>Esta notícia tem ganhado destaque nos últimos dias e merece atenção especial. {description}</p>

<h3>Desenvolvimentos Recentes</h3>

<p>Os fatos relacionados a esta notícia indicam uma evolução significativa no cenário atual. A situação tem sido acompanhada de perto por especialistas e analistas que estudam o impacto dessas transformações.</p>

<p>Segundo informações da {source}, os desenvolvimentos mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema.</p>

<h3>Análise do Impacto</h3>

<p>Esta notícia tem relevância especial no contexto atual, onde as particularidades locais influenciam diretamente os resultados observados. O impacto pode ser sentido em diferentes setores da sociedade.</p>

<p>Os especialistas destacam que esta situação reflete tendências mais amplas observadas em outros contextos, mas apresenta características únicas que merecem atenção especial.</p>

<h3>Contexto Brasileiro</h3>

<p>No Brasil, esta notícia tem implicações específicas que afetam diretamente a vida dos cidadãos brasileiros. Desde as grandes metrópoles até as cidades do interior, é possível observar mudanças significativas relacionadas a esta questão.</p>

<p>As autoridades brasileiras têm acompanhado de perto os desenvolvimentos, buscando adaptar as políticas públicas às novas realidades apresentadas por esta notícia.</p>

<h3>Perspectivas Futuras</h3>

<p>As projeções para os próximos meses indicam que esta tendência deve se manter, com possíveis desenvolvimentos que podem trazer benefícios adicionais. Os analistas são cautelosamente otimistas quanto ao futuro.</p>

<p>Os investimentos planejados para os próximos anos devem acelerar ainda mais essa tendência positiva, criando novas oportunidades e consolidando avanços importantes.</p>

<h3>Recomendações</h3>

<p>Com base na análise apresentada, é possível identificar algumas recomendações importantes para o desenvolvimento futuro desta questão. Essas recomendações são fundamentadas em dados concretos e na experiência de especialistas.</p>

<p>O primeiro passo é continuar acompanhando os desenvolvimentos, garantindo que as informações mais atualizadas sejam consideradas nas tomadas de decisão.</p>

<h3>Conclusão</h3>

<p>Esta notícia sobre {topic.lower() if topic else 'o tema em questão'} foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia e manterá os leitores informados sobre novos desenvolvimentos relacionados ao tema.</p>

<p>O cenário atual é promissor e indica que estamos no caminho certo para compreender melhor esta questão. A continuidade do acompanhamento e o engajamento de todos os setores serão fundamentais para manter o ritmo de evolução observado.</p>

<p>Para mais informações sobre {topic.lower() if topic else 'este tema'} e outros assuntos relevantes para o Brasil, acompanhe nossas atualizações diárias e mantenha-se sempre bem informado sobre os temas que mais importam para o país.</p>"""

        return content

    def _get_category_from_news(self, article, Categoria):
        """Categoriza baseado no site de origem, notícia encontrada ou sistema inteligente"""
        # 1. PRIORIDADE MÁXIMA: Extrair categoria do site de origem
        try:
            from rb_ingestor.site_categorizer import SiteCategorizer
            site_categorizer = SiteCategorizer()
            
            # Escolher URL a usar: original se disponível
            url_to_use = article.get('original_url') or article.get('url') or ''
            # Evitar analisar Google News
            if url_to_use and 'news.google.' not in url_to_use:
                # Tentar extrair categoria do site
                site_category = site_categorizer.categorize_article({'url': url_to_use})
            else:
                site_category = None
            
            if site_category:
                self.stdout.write(f"🌐 Categoria do site: {site_category}")
                
                # Buscar categoria existente
                cat = Categoria.objects.filter(nome=site_category.title()).first()
                if cat:
                    self.stdout.write(f"✅ Usando categoria existente: {site_category}")
                    return cat
                
                # Criar nova categoria se não existir
                cat, created = Categoria.objects.get_or_create(
                    slug=slugify(site_category)[:140],
                    defaults={"nome": site_category.title()}
                )
                if created:
                    self.stdout.write(f"🆕 Nova categoria criada: {site_category}")
                else:
                    self.stdout.write(f"✅ Categoria encontrada: {site_category}")
                return cat
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro no categorizador de site: {e}")
        
        # 2. FALLBACK: Tentar usar categoria da notícia encontrada
        news_category = article.get('category', '').strip()
        if news_category:
            # Limpar e normalizar categoria da notícia
            clean_category = news_category.title().strip()
            self.stdout.write(f"📰 Categoria da notícia: {clean_category}")
            
            # Buscar categoria existente
            cat = Categoria.objects.filter(nome=clean_category).first()
            if cat:
                self.stdout.write(f"✅ Usando categoria existente: {clean_category}")
                return cat
            
            # Criar nova categoria se não existir
            cat, created = Categoria.objects.get_or_create(
                slug=slugify(clean_category)[:140],
                defaults={"nome": clean_category}
            )
            if created:
                self.stdout.write(f"🆕 Nova categoria criada: {clean_category}")
            else:
                self.stdout.write(f"✅ Categoria encontrada: {clean_category}")
            return cat
        
        # 3. FALLBACK FINAL: Sistema inteligente de análise de conteúdo
        self.stdout.write("🧠 Usando sistema inteligente de categorização...")
        title = article.get('title', '')
        description = article.get('description', '')
        topic = article.get('topic', '')
        
        try:
            from rb_ingestor.smart_categorizer import SmartCategorizer
            categorizer = SmartCategorizer()
            
            # Categorizar baseado no conteúdo completo
            category_name = categorizer.categorize_content(title, description, topic)
            confidence = categorizer.get_category_confidence(title, description, topic)
            
            self.stdout.write(f"🧠 Categoria detectada: {category_name} (confiança: {confidence:.2f})")
            
            # Buscar ou criar categoria
            cat = Categoria.objects.filter(nome=category_name.title()).first()
            if cat:
                return cat
            
            # Criar nova categoria se não existir
            cat, created = Categoria.objects.get_or_create(
                slug=slugify(category_name)[:140],
                defaults={"nome": category_name.title()}
            )
            return cat
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro no categorizador inteligente: {e}")
            # Fallback final para sistema simples
            return self._get_category_fallback(article, Categoria)
    
    def _get_category_fallback(self, article, Categoria):
        """Fallback para categorização simples"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        topic = article.get('topic', '').lower()
        
        all_text = f"{title} {description} {topic}"
        
        # Mapeamento simples de fallback
        if any(word in all_text for word in ['política', 'governo', 'presidente', 'eleições']):
            category_name = "Política"
        elif any(word in all_text for word in ['economia', 'mercado', 'inflação', 'dólar']):
            category_name = "Economia"
        elif any(word in all_text for word in ['esportes', 'futebol', 'copa']):
            category_name = "Esportes"
        elif any(word in all_text for word in ['saúde', 'medicina', 'hospital']):
            category_name = "Saúde"
        elif any(word in all_text for word in ['tecnologia', 'digital', 'ia']):
            category_name = "Tecnologia"
        else:
            category_name = "Brasil"
        
        cat = Categoria.objects.filter(nome=category_name).first()
        if cat:
            return cat
        
        cat, created = Categoria.objects.get_or_create(
            slug=slugify(category_name)[:140],
            defaults={"nome": category_name}
        )
        return cat

    def _add_specific_image(self, noticia, article):
        """Adiciona imagem específica baseada na notícia com sistema inteligente melhorado"""
        try:
            # LÓGICA INTELIGENTE MELHORADA:
            # 1. Figuras públicas: Detecção inteligente → Instagram oficial → Bancos gratuitos
            # 2. Artigos gerais: Bancos gratuitos
            
            # NOVA PRIORIDADE 1: Detecção inteligente de figuras públicas
            from rb_ingestor.smart_public_figure_detector import SmartPublicFigureDetector
            smart_detector = SmartPublicFigureDetector()
            
            full_text = f"{noticia.titulo} {noticia.conteudo}"
            if article:
                full_text += f" {article.get('title', '')} {article.get('description', '')}"
            
            # Detectar figura pública usando sistema inteligente
            public_figure = smart_detector.detect_public_figure(full_text)
            
            if public_figure:
                # É figura pública - seguir lógica específica
                self.stdout.write(f"🎭 Figura pública detectada: {public_figure['figure']}")
                
                # PRIORIDADE 1: Instagram oficial da figura (usando sistema inteligente)
                instagram_image = smart_detector.get_instagram_image_for_figure(public_figure)
                
                if instagram_image and instagram_image.get("url"):
                    self.stdout.write(f"📱 Imagem do Instagram oficial encontrada: {public_figure['instagram_handle']}")
                    noticia.imagem = instagram_image["url"]
                    noticia.imagem_alt = instagram_image.get("alt", f"Imagem de {public_figure['figure']}")
                    noticia.imagem_credito = instagram_image.get("credit", f"Foto: Instagram {public_figure['instagram_handle']}")
                    noticia.imagem_licenca = "Figura Pública - Unsplash"
                    noticia.imagem_fonte_url = instagram_image.get("instagram_url", "")
                    noticia.save()
                    
                    self.stdout.write("✅ Imagem do Instagram oficial adicionada com sucesso")
                    return
            
            # FALLBACK: Bancos de imagens gratuitos
            self.stdout.write("🖼️ Usando banco de imagens gratuitos...")
            from rb_ingestor.image_search import ImageSearchEngine
            
            search_engine = ImageSearchEngine()
            
            # Usar o tópico da notícia para buscar imagem específica
            topic = article.get('topic', '')
            title = article.get('title', '')
            
            # Criar termo de busca específico
            search_term = topic if topic else title[:50]
            
            image_url = search_engine.search_image(
                search_term,
                noticia.conteudo,
                noticia.categoria.nome if noticia.categoria else "geral"
            )

            if image_url:
                noticia.imagem = image_url
                noticia.imagem_alt = f"Imagem relacionada a {search_term}"
                noticia.imagem_credito = "Imagem gratuita"
                noticia.imagem_licenca = "CC"
                noticia.imagem_fonte_url = image_url
                noticia.save()

                self.stdout.write(f"✅ Imagem gratuita adicionada: {search_term}")
                return
            
            self.stdout.write("⚠️ Nenhuma imagem encontrada")

        except Exception as e:
            self.stdout.write(f"⚠️ Erro ao adicionar imagem específica: {e}")

    def _check_duplicate(self, title, Noticia):
        """Verifica se já existe notícia similar"""
        return Noticia.objects.filter(
            titulo__icontains=title[:20],
            criado_em__date=timezone.localdate()
        ).exists()

    def _ping_sitemap(self):
        """Faz ping do sitemap"""
        try:
            from core.utils import absolute_sitemap_url
            from rb_ingestor.ping import ping_search_engines
            
            sm_url = absolute_sitemap_url()
            res = ping_search_engines(sm_url)
            
            self.stdout.write(f"🔗 Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; Bing={'OK' if res['bing'] else 'NOK'}")
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro ao fazer ping do sitemap: {e}")
