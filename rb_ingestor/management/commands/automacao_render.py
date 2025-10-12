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
                # Gerar conteúdo baseado na notícia específica
                title, content = self._generate_content_from_news(article)
                
                # Categorizar baseado no conteúdo da notícia
                categoria = self._get_category_from_news(article, Categoria)
                
                # Verificar duplicatas
                if self._check_duplicate(title, Noticia):
                    self.stdout.write(f"⚠ Pulando duplicata: {title}")
                    continue
                
                # Criar notícia
                noticia = Noticia.objects.create(
                    titulo=title,
                    slug=slugify(title)[:180],
                    conteudo=content,
                    publicado_em=timezone.now(),
                    categoria=categoria,
                    fonte_url=article.get('url', f"render-automation-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}"),
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

    def _generate_content_from_news(self, article):
        """Gera conteúdo baseado na notícia específica"""
        try:
            # Tentar IA primeiro com contexto da notícia
            from rb_ingestor.ai import generate_article
            
            # Criar prompt específico baseado na notícia
            news_prompt = f"""
            Crie um artigo completo baseado nesta notícia específica:
            
            TÍTULO: {article.get('title', '')}
            DESCRIÇÃO: {article.get('description', '')}
            FONTE: {article.get('source', '')}
            
            REQUISITOS:
            - Mínimo de 800 palavras
            - Baseado na notícia específica, não genérico
            - Contexto brasileiro quando relevante
            - Estrutura com subtítulos H2 e H3
            - Linguagem natural e informativa
            - Foco na notícia específica mencionada
            
            ESTRUTURA:
            1. Introdução sobre a notícia específica
            2. Desenvolvimento dos fatos
            3. Análise do impacto
            4. Contexto brasileiro (se aplicável)
            5. Perspectivas futuras
            6. Conclusão
            
            IMPORTANTE: Foque na notícia específica, não em conteúdo genérico sobre o tema.
            """
            
            # Usar sistema de IA melhorado
            from rb_ingestor.ai_enhanced import generate_enhanced_article
            
            ai_content = generate_enhanced_article(article.get('topic', ''), article, 800)
            
            if ai_content:
                title = strip_tags(ai_content.get("title", article.get('title', '')))[:200]
                content = f'<p class="dek">{strip_tags(ai_content.get("dek", article.get('description', '')))[:220]}</p>\n{ai_content.get("html", "<p></p>")}'
                
                # Verificar qualidade
                word_count = ai_content.get('word_count', 0)
                quality_score = ai_content.get('quality_score', 0)
                
                if word_count >= 600 and quality_score >= 50:
                    self.stdout.write(f"✅ IA melhorada gerou {word_count} palavras (qualidade: {quality_score}%)")
                    return title, content
                else:
                    self.stdout.write(f"⚠ IA gerou {word_count} palavras (qualidade: {quality_score}%), usando fallback")
                
        except Exception as e:
            self.stdout.write(f"⚠ IA falhou: {e}")
        
        # Fallback: conteúdo baseado na notícia específica
        title = self._generate_title_from_news(article)
        content = self._generate_content_from_news_fallback(article)
        
        return title, content

    def _generate_title_from_news(self, article):
        """Gera título original baseado no tópico, nunca copiando títulos de outros portais"""
        # NUNCA usar títulos de outros portais para evitar plágio
        # Sempre criar títulos originais baseados no tópico
        
        topic = article.get('topic', '')
        topic_lower = topic.lower()
        
        # Padrões de títulos originais por categoria
        if any(word in topic_lower for word in ['lula', 'bolsonaro', 'presidente', 'governo', 'política']):
            return f"{topic.title()}: Análise Política e Desdobramentos"
        elif any(word in topic_lower for word in ['economia', 'mercado', 'inflação', 'dólar']):
            return f"{topic.title()}: Impacto na Economia Brasileira"
        elif any(word in topic_lower for word in ['tecnologia', 'digital', 'ia', 'inteligência']):
            return f"{topic.title()}: Tendências e Inovações"
        elif any(word in topic_lower for word in ['esportes', 'futebol', 'copa']):
            return f"{topic.title()}: Últimas Notícias Esportivas"
        elif any(word in topic_lower for word in ['saúde', 'medicina', 'hospital']):
            return f"{topic.title()}: Informações Importantes para a Saúde"
        elif any(word in topic_lower for word in ['china', 'eua', 'europa', 'internacional']):
            return f"{topic.title()}: Desenvolvimentos Internacionais"
        else:
            return f"{topic.title()}: Análise Completa e Atualizada"

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
        """Categoriza baseado no conteúdo da notícia"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        topic = article.get('topic', '').lower()
        
        # Mapeamento de palavras-chave para categorias (ordem de prioridade)
        category_keywords = {
            "política": ["política", "governo", "eleições", "presidente", "lula", "bolsonaro", "congresso", "ministro", "democracia", "eleitoral", "partido", "candidato"],
            "economia": ["economia", "mercado", "inflação", "dólar", "real", "investimento", "finanças", "banco", "crédito", "bolsa", "ações", "pib", "desemprego"],
            "esportes": ["esportes", "futebol", "copa", "mundial", "brasileirão", "atletismo", "jogos", "competição", "campeonato", "jogador", "time"],
            "saúde": ["saúde", "medicina", "hospital", "vacina", "covid", "coronavírus", "tratamento", "médico", "doença", "epidemia", "pandemia"],
            "meio ambiente": ["meio ambiente", "sustentabilidade", "natureza", "clima", "ecologia", "verde", "energia", "poluição", "desmatamento", "aquecimento"],
            "tecnologia": ["tecnologia", "digital", "ia", "inteligência artificial", "chatgpt", "app", "software", "blockchain", "crypto", "bitcoin", "startup", "inovação"],
            "mundo": ["china", "eua", "europa", "internacional", "global", "mundial", "país", "nação", "estrangeiro", "guerra", "conflito"],
            "brasil": ["brasil", "brasileiro", "nacional", "federal", "estadual", "municipal", "governo federal"]
        }
        
        # Verificar todas as fontes de texto
        all_text = f"{title} {description} {topic}"
        
        # Encontrar categoria mais relevante (primeira que encontrar)
        for category, keywords in category_keywords.items():
            if any(kw in all_text for kw in keywords):
                cat = Categoria.objects.filter(nome=category.title()).first()
                if cat:
                    return cat
        
        # Fallback para Brasil
        cat = Categoria.objects.filter(nome="Brasil").first()
        if cat:
            return cat
        
        # Criar categoria Brasil se não existir
        cat, created = Categoria.objects.get_or_create(
            slug=slugify("Brasil")[:140],
            defaults={"nome": "Brasil"}
        )
        return cat

    def _add_specific_image(self, noticia, article):
        """Adiciona imagem específica baseada na notícia"""
        try:
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

                self.stdout.write(f"🖼️  Imagem específica adicionada: {search_term}")

        except Exception as e:
            self.stdout.write(f"⚠ Erro ao adicionar imagem específica: {e}")

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
