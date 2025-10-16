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
from rb_ingestor.title_styles import title_style_manager

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
        """Busca notícias via RSS feeds do Google News"""
        try:
            from rb_ingestor.news_content_extractor import NewsContentExtractor
            
            extractor = NewsContentExtractor()
            topics = [
                'economia', 'política', 'tecnologia', 'brasil', 'mundo', 'esportes', 'saúde', 'ciência'
            ]
            
            processed_news = []
            for topic in topics:
                self.stdout.write(f"🔍 Buscando RSS para: {topic}")
                items = extractor.get_rss_items_for_topic(topic, max_items=2)
                
                for item in items:
                    title = item.get('title') or ''
                    desc = item.get('description') or ''
                    url = item.get('link') or ''
                    
                    if title and url and self._is_valid_news_article({'title': title, 'url': url}):
                        processed_news.append({
                            'title': title,
                            'description': desc,
                            'url': url,
                            'published_date': '',
                            'source': '',
                            'topic': self._extract_main_topic(title)
                        })
                        
                        if len(processed_news) >= 8:  # Limite de artigos
                            break
                
                if len(processed_news) >= 8:
                    break
            
            self.stdout.write(f"✅ RSS retornou {len(processed_news)} notícias")
            return processed_news
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro RSS: {e}")
            return []

    def _get_specific_news_fallback_rss(self):
        """Fallback: usa RSS do Google News via NewsContentExtractor para montar artigos específicos."""
        try:
            from rb_ingestor.news_content_extractor import NewsContentExtractor
            extractor = NewsContentExtractor()
            topics = [
                'economia', 'política', 'tecnologia', 'brasil', 'mundo', 'esportes', 'saúde', 'ciência'
            ]
            processed = []
            for topic in topics:
                items = extractor.get_rss_items_for_topic(topic, max_items=3) or []
                for item in items:
                    title = item.get('title') or ''
                    desc = item.get('description') or ''
                    url = item.get('link') or ''
                    if not title or not url:
                        continue
                    processed.append({
                        'title': title,
                        'description': desc,
                        'url': url,
                        'published_date': '',
                        'source': '',
                        'topic': self._extract_main_topic(title)
                    })
                    if len(processed) >= 10:
                        break
                if len(processed) >= 10:
                    break
            return processed
        except Exception as e:
            self.stdout.write(f"⚠ Erro no fallback RSS: {e}")
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
        """Gera conteúdo usando RSS + navegador headless para extrair conteúdo real"""
        try:
            # 1) Extrair conteúdo real usando navegador headless
            base_words = None
            enhanced_article = article.copy()
            
            try:
                from rb_ingestor.news_content_extractor import NewsContentExtractor
                extractor = NewsContentExtractor()
                
                # Tentar extrair do URL do RSS
                rss_url = article.get('url', '')
                if rss_url:
                    self.stdout.write(f"🔍 Extraindo conteúdo real de: {rss_url}")
                    data = extractor.extract_content_from_url(rss_url)
                    
                    if data and data.get('content'):
                        base_words = len((data['content'] or '').split())
                        self.stdout.write(f"✅ Conteúdo completo extraído: {base_words} palavras")
                        
                        # Atualizar artigo com dados reais
                        enhanced_article.update({
                            'title': data.get('title', article.get('title', '')),
                            'description': data.get('description', article.get('description', '')),
                            'content': data.get('content', ''),
                            'author': data.get('author', ''),
                            'date': data.get('date', ''),
                            'real_content': True,
                            'source_domain': data.get('source_domain', ''),
                            'original_url': rss_url
                        })
                    else:
                        self.stdout.write("⚠ Falha ao extrair conteúdo real, usando dados RSS")
                else:
                    self.stdout.write("⚠ Sem URL RSS para extrair")
                    
            except Exception as e:
                self.stdout.write(f"⚠ Erro na extração com navegador: {e}")
            
            # 2) Definir palavras mínimas baseado no conteúdo extraído
            if base_words and base_words >= 100:
                min_words = max(600, int(base_words * 0.7))  # 70% do conteúdo original
                self.stdout.write(f"📊 Base real: {base_words} palavras → Alvo: {min_words} palavras")
            else:
                min_words = 700  # Padrão quando não há conteúdo real
                self.stdout.write(f"📊 Sem conteúdo real → Alvo padrão: {min_words} palavras")
            
            # 3) Gerar conteúdo com IA usando dados reais
            from rb_ingestor.ai_enhanced import generate_enhanced_article
            from rb_ingestor.writing_styles import writing_style_manager
            
            # Selecionar estilo aleatório
            random_style = writing_style_manager.get_random_style()
            style_info = writing_style_manager.get_style_info(random_style)
            self.stdout.write(f"🎨 Estilo selecionado: {style_info['name']}")
            
            ai_content = generate_enhanced_article(
                article.get('topic', ''), 
                enhanced_article, 
                min_words,
                random_style
            )
            
            if not ai_content:
                self.stdout.write("⚠ IA não retornou conteúdo")
                raise RuntimeError("IA não retornou conteúdo")
            
            # 4) Processar resultado
            title = strip_tags(ai_content.get("title", enhanced_article.get('title', '')))[:200]
            html = ai_content.get("html", "<p></p>")
            content = f'<p class="dek">{strip_tags(ai_content.get("dek", enhanced_article.get('description', '')))[:220]}</p>\n{html}'
            
            # 5) Contar palavras e validar
            from django.utils.html import strip_tags as dj_strip
            word_count = len(dj_strip(content).split())
            quality_score = ai_content.get('quality_score', 0)
            
            self.stdout.write(f"✅ IA gerou {word_count} palavras (qualidade: {quality_score}%)")
            
            # 6) Verificar margem de 15%
            margem_min = int(min_words * 0.85)  # 15% a menos
            margem_max = int(min_words * 1.15)  # 15% a mais
            
            if margem_min <= word_count <= margem_max:
                self.stdout.write(f"✅ Conteúdo dentro da margem de 15%: {word_count} palavras ({margem_min}-{margem_max})")
            else:
                self.stdout.write(f"⚠ Conteúdo fora da margem de 15%: {word_count} palavras (alvo: {margem_min}-{margem_max})")
            
            return title, content
            
        except Exception as e:
            self.stdout.write(f"❌ Publicação cancelada: {e}")
            # Propagar exceção para que o caller pule este artigo
            raise

    def _normalize_two_h2_sections(self, html: str) -> str:
        """Garante exatamente 2 H2: mantém os dois primeiros; H2 adicionais viram H3.
        Se não houver 2 H2, insere subtítulos padrão após o primeiro parágrafo.
        """
        try:
            if not html:
                return html
            import re
            # Demover H2 extras para H3, preservando os 2 primeiros
            positions = [m.start() for m in re.finditer(r"<h2\b", html, flags=re.IGNORECASE)]
            if len(positions) >= 2:
                # Substituir a partir do 3º <h2 ...> por <h3 ...>
                def replacer(match, _state={"count": 0}):
                    _state["count"] += 1
                    if _state["count"] <= 2:
                        return match.group(0)
                    return match.group(0).replace("<h2", "<h3").replace("</h2>", "</h3>")
                # Primeiro, marcar blocos de fechamento também
                html = re.sub(r"</h2>", "</h2>", html, flags=re.IGNORECASE)
                html = re.sub(r"<h2(?=[^>]*>)", replacer, html, flags=re.IGNORECASE)
                # Corrigir fechamentos residuais de H2 extras
                html = re.sub(r"</h2>(?=(?:[^<]|<(?!/?h2))*$)", "</h3>", html, flags=re.IGNORECASE)
                return html

            # Se houver 0 ou 1 H2, inserir dois subtítulos padrão após o primeiro </p>
            insert_at = html.lower().find("</p>")
            insert_at = (insert_at + 4) if insert_at != -1 else 0
            h2_block = (
                "\n<h2>Contexto e Principais Pontos</h2>\n"
                "<p>Entenda os elementos centrais do caso com fatos e informações claras ao leitor.</p>\n"
                "<h2>Desdobramentos e Impactos</h2>\n"
                "<p>Resumo dos efeitos práticos, reações e próximos passos relacionados ao tema.</p>\n"
            )
            return html[:insert_at] + h2_block + html[insert_at:]
        except Exception:
            return html

    def _generate_title_from_news(self, article):
        """Gera título usando sistema de estilos aleatórios mantendo a palavra-chave."""
        topic = article.get('topic', '') or ''
        original_title = (article.get('title') or '').strip()
        
        if not topic:
            return f"Últimas Notícias"
        
        # Usar o sistema de estilos para gerar título
        title = title_style_manager.generate_smart_title(topic, original_title)
        
        # Verificar se é suficientemente diferente do original
        if self._is_title_different_enough(title, original_title):
            return title
        
        # Se muito similar, tentar novamente com estilo diferente
        for _ in range(3):  # Máximo 3 tentativas
            style = title_style_manager.get_random_style()
            title = title_style_manager.generate_title(style, topic)
            if self._is_title_different_enough(title, original_title):
                return title
        
        # Fallback: título simples
        return f"O que {topic.title()} anuncia sobre {topic}?"
    
    def _is_title_different_enough(self, new_title, original_title):
        """Verifica se o novo título é suficientemente diferente do original"""
        import re
        
        if not original_title:
            return True
        
        # Normalizar ambos os títulos
        new_norm = re.sub(r'\s+', ' ', new_title.lower().strip())
        orig_norm = re.sub(r'\s+', ' ', original_title.lower().strip())
        
        # Se são idênticos, não usar
        if new_norm == orig_norm:
            return False
        
        # Se o novo título contém mais de 80% das palavras do original, evitar
        new_words = set(new_norm.split())
        orig_words = set(orig_norm.split())
        
        if len(orig_words) > 0:
            similarity = len(new_words.intersection(orig_words)) / len(orig_words)
            if similarity > 0.8:
                return False
        
        return True

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
        if any(word in all_text for word in ['prisão','preso','pf','polícia','delegado','crime','criminoso','latrocínio','assalto','tráfico','trafico','lavagem','pcc','milícia','milicia','tiroteio','homicídio','homicidio']):
            category_name = "Brasil"
        elif any(word in all_text for word in ['política', 'governo', 'presidente', 'eleições']):
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
        """Adiciona imagem usando Google Lens + bancos gratuitos."""
        try:
            # NOVO: Busca inteligente com Google Lens
            self.stdout.write("🔍 Buscando imagem com Google Lens...")
            from rb_ingestor.smart_image_search import smart_image_search
            
            # Tentar busca inteligente com Google Lens
            news_url = article.get('url', '') if article else ''
            
            if news_url:
                smart_image = smart_image_search.find_smart_image_for_article(
                    news_url, 
                    noticia.titulo
                )
                
                if smart_image:
                    noticia.imagem = smart_image['url']
                    noticia.imagem_alt = smart_image['alt']
                    noticia.imagem_credito = smart_image['credit']
                    noticia.save()
                    
                    self.stdout.write(f"✅ Imagem inteligente encontrada: {smart_image['source'].upper()} (similaridade: {smart_image['similarity_score']:.2f})")
                    return
            
            # FALLBACK: Busca tradicional em bancos gratuitos
            self.stdout.write("🔄 Google Lens falhou, usando busca tradicional...")
            from rb_ingestor.image_search import ImageSearchEngine

            search_engine = ImageSearchEngine()

            topic = (article.get('topic', '') if article else '')
            title = (article.get('title', '') if article else '')

            search_term = topic if topic else title[:50]

            image_url = search_engine.search_image(
                search_term,
                noticia.conteudo,
                (noticia.categoria.nome if noticia.categoria else "geral")
            )

            if image_url:
                noticia.imagem = image_url
                noticia.imagem_alt = f"Imagem relacionada a {search_term}"
                noticia.imagem_credito = "Imagem gratuita"
                noticia.imagem_licenca = "CC"
                noticia.imagem_fonte_url = image_url
                noticia.save()

                self.stdout.write(f"✅ Imagem tradicional encontrada: {search_term}")
                return

            self.stdout.write("⚠️ Nenhuma imagem encontrada nos bancos gratuitos")

        except Exception as e:
            self.stdout.write(f"⚠️ Erro ao adicionar imagem: {e}")

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
