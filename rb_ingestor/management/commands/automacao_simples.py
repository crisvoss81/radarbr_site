# rb_ingestor/management/commands/automacao_simples.py
"""
Comando de automação simplificado que funciona sem dependências externas
"""
import os
import sys
import django
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
import random

class Command(BaseCommand):
    help = "Automação simplificada de notícias (sem APIs externas)"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=3, help="Número de artigos a criar")
        parser.add_argument("--force", action="store_true", help="Força criação mesmo se similar existir")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        self.stdout.write("=== AUTOMAÇÃO SIMPLIFICADA ===")
        
        # Buscar tópicos reais do Google News
        topicos = self._get_real_topics()
        
        # Fallback para tópicos pré-definidos se não encontrar reais
        if not topicos:
            topicos = [
                "Tecnologia no Brasil",
                "Economia brasileira atual", 
                "Esportes nacionais",
                "Cultura e entretenimento",
                "Política nacional",
                "Meio ambiente",
                "Educação no Brasil",
                "Saúde pública",
                "Inovação e startups",
                "Turismo nacional"
            ]
            self.stdout.write("⚠ Usando tópicos de fallback")
        
        created_count = 0
        limit = options["limit"]
        
        for i in range(limit):
            # Escolher tópico aleatório
            topico = random.choice(topicos)
            
            # Gerar conteúdo com IA otimizada
            try:
                from rb_ingestor.ai import generate_article
                ai_content = generate_article(topico)
                title = ai_content.get("title", topico)
                conteudo = ai_content.get("html", f"## {topico}\n\nConteúdo sobre {topico.lower()}.")
            except Exception as e:
                self.stdout.write(f"⚠ Erro na IA, usando fallback: {e}")
                title = f"{topico} - Análise Completa"
                conteudo = self._gerar_conteudo_simples(topico)
            
            # Categorizar baseado no tópico
            cat = self._get_category_for_topic(topico, Categoria)
            
            slug = slugify(title)[:180]
            
            # Verificar se já existe (mais rigoroso)
            if not options["force"] and self._check_duplicate_news(title, topico, Noticia):
                self.stdout.write(f"⚠ Pulando duplicata: {title}")
                continue
            
            # Criar notícia
            try:
                noticia = Noticia.objects.create(
                    titulo=title,
                    slug=slug,
                    conteudo=conteudo,
                    publicado_em=timezone.now(),
                    categoria=cat,
                    fonte_url=f"automacao-simples-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}",
                    fonte_nome="RadarBR Automação",
                    status=1  # PUBLICADO
                )
                
                # Buscar e adicionar imagem (sem Cloudinary)
                self._adicionar_imagem(noticia, topico)
                
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Criado: {title}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Erro ao criar '{title}': {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"\n=== CONCLUÍDO ==="))
        self.stdout.write(f"Notícias criadas: {created_count}")
        self.stdout.write(f"Total no sistema: {Noticia.objects.count()}")
        
        # Ping sitemap se criou notícias
        if created_count > 0:
            try:
                from core.utils import absolute_sitemap_url
                from rb_ingestor.ping import ping_search_engines
                sm_url = absolute_sitemap_url()
                res = ping_search_engines(sm_url)
                self.stdout.write(f"Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; Bing={'OK' if res['bing'] else 'NOK'}")
            except Exception:
                self.stdout.write("⚠ Erro ao fazer ping do sitemap")

    def _gerar_conteudo_simples(self, topico):
        """Gera conteúdo simples sem usar IA (em Markdown)"""
        
        conteudos = {
            "Tecnologia no Brasil": """## Desenvolvimento Tecnológico no Brasil

O Brasil tem se destacado no cenário tecnológico mundial com inovações em diversas áreas.

### Principais Áreas de Destaque

- Fintechs e pagamentos digitais
- Agronegócio tecnológico
- E-commerce e marketplaces
- Inteligência artificial aplicada

### Desafios e Oportunidades

O país enfrenta desafios como infraestrutura digital e capacitação técnica, mas também apresenta grandes oportunidades de crescimento.
""",
            
            "Economia brasileira atual": """## Panorama da Economia Brasileira

A economia brasileira apresenta sinais de recuperação com indicadores positivos em diversos setores.

### Indicadores Principais

- Crescimento do PIB
- Controle da inflação
- Geração de empregos
- Investimentos externos

### Perspectivas Futuras

As projeções indicam um cenário positivo para os próximos trimestres, com foco em sustentabilidade e inovação.
""",
            
            "Esportes nacionais": """## Esportes no Brasil

O Brasil continua sendo uma potência esportiva mundial com destaque em diversas modalidades.

### Modalidades em Destaque

- Futebol profissional
- Vôlei e vôlei de praia
- Atletismo
- Natação

### Preparação para Competições

Os atletas brasileiros se preparam intensamente para as próximas competições internacionais.
"""
        }
        
        # Conteúdo padrão se não encontrar o tópico específico
        conteudo_padrao = f"""## {topico}

Este é um artigo sobre {topico.lower()} desenvolvido pelo sistema de automação.

### Principais Aspectos

- Aspecto importante 1
- Aspecto importante 2
- Aspecto importante 3

### Conclusão

{topico} é um tema relevante que merece atenção e análise contínua.
"""
        
        return conteudos.get(topico, conteudo_padrao)

    def _adicionar_imagem(self, noticia, topico):
        """Busca e adiciona imagem à notícia usando ImageSearchEngine"""
        try:
            from rb_ingestor.image_search import ImageSearchEngine
            
            # Usar o ImageSearchEngine que já está funcionando
            search_engine = ImageSearchEngine()
            image_url = search_engine.search_image(noticia.titulo, noticia.conteudo, noticia.categoria.nome if noticia.categoria else "geral")
            
            if image_url:
                # Salvar URL da imagem
                noticia.imagem = image_url
                noticia.imagem_alt = f"Imagem relacionada a {topico}"
                noticia.imagem_credito = "Imagem gratuita"
                noticia.imagem_licenca = "CC"
                noticia.imagem_fonte_url = image_url
                noticia.save()
                
                self.stdout.write(f"✓ Imagem adicionada: {topico}")
            else:
                self.stdout.write(f"⚠ Nenhuma imagem encontrada para: {topico}")
                
        except Exception as e:
            self.stdout.write(f"⚠ Erro ao buscar imagem para {topico}: {e}")

    def _get_category_for_topic(self, topic, Categoria):
        """Categoriza o tópico baseado em palavras-chave"""
        topic_lower = topic.lower()
        
        # Mapeamento de tópicos para categorias
        category_mapping = {
            "tecnologia": "Tecnologia",
            "inovação": "Tecnologia", 
            "digital": "Tecnologia",
            "startup": "Tecnologia",
            "app": "Tecnologia",
            "software": "Tecnologia",
            "ia": "Tecnologia",
            "inteligência artificial": "Tecnologia",
            
            "economia": "Economia",
            "mercado": "Economia",
            "negócios": "Economia",
            "investimento": "Economia",
            "finanças": "Economia",
            "pib": "Economia",
            "inflação": "Economia",
            
            "esportes": "Esportes",
            "futebol": "Esportes",
            "atletismo": "Esportes",
            "natação": "Esportes",
            "vôlei": "Esportes",
            "olimpíadas": "Esportes",
            
            "cultura": "Cultura",
            "arte": "Cultura",
            "museu": "Cultura",
            "teatro": "Cultura",
            "literatura": "Cultura",
            "folclore": "Cultura",
            "música": "Cultura",
            
            "entretenimento": "Entretenimento",
            "show": "Entretenimento",
            "festival": "Entretenimento",
            "cinema": "Entretenimento",
            "tv": "Entretenimento",
            "streaming": "Entretenimento",
            
            "lifestyle": "Lifestyle",
            "vida": "Lifestyle",
            "estilo": "Lifestyle",
            "moda": "Lifestyle",
            "gastronomia": "Lifestyle",
            "viagem": "Lifestyle",
            "turismo": "Lifestyle",
            
            "política": "Política",
            "governo": "Política",
            "eleições": "Política",
            "congresso": "Política",
            "presidente": "Política",
            
            "saúde": "Saúde",
            "medicina": "Saúde",
            "hospital": "Saúde",
            "vacina": "Saúde",
            "covid": "Saúde",
            
            "educação": "Educação",
            "escola": "Educação",
            "universidade": "Educação",
            "ensino": "Educação",
            "estudante": "Educação",
            
            "meio ambiente": "Meio Ambiente",
            "natureza": "Meio Ambiente",
            "sustentabilidade": "Meio Ambiente",
            "clima": "Meio Ambiente",
            "ecologia": "Meio Ambiente"
        }
        
        # Procurar categoria correspondente
        for keyword, category_name in category_mapping.items():
            if keyword in topic_lower:
                cat, created = Categoria.objects.get_or_create(
                    slug=slugify(category_name)[:140],
                    defaults={"nome": category_name}
                )
                return cat
        
        # Fallback para categoria geral
        cat_geral, created = Categoria.objects.get_or_create(
            slug="geral",
            defaults={"nome": "Geral"}
        )
        return cat_geral

    def _check_duplicate_news(self, title, topic, Noticia):
        """Verifica se já existe notícia similar (mais rigoroso)"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Verificar por título similar (últimas 24h)
        recent_news = Noticia.objects.filter(
            publicado_em__gte=timezone.now() - timedelta(hours=24)
        )
        
        # Verificar título similar
        for news in recent_news:
            if self._titles_similar(title, news.titulo):
                return True
        
        # Verificar por tópico similar (últimas 6h)
        recent_news_6h = Noticia.objects.filter(
            publicado_em__gte=timezone.now() - timedelta(hours=6)
        )
        
        for news in recent_news_6h:
            if self._topics_similar(topic, news.titulo):
                return True
        
        return False

    def _titles_similar(self, title1, title2):
        """Verifica se dois títulos são similares"""
        # Remover palavras comuns e comparar
        common_words = ["o", "que", "está", "no", "brasil", "análise", "completa", "tendências"]
        words1 = set(title1.lower().split()) - set(common_words)
        words2 = set(title2.lower().split()) - set(common_words)
        
        # Se mais de 50% das palavras são iguais, são similares
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        common_count = len(words1.intersection(words2))
        similarity = common_count / min(len(words1), len(words2))
        
        return similarity > 0.5

    def _topics_similar(self, topic, title):
        """Verifica se o tópico é similar ao título"""
        topic_words = set(topic.lower().split())
        title_words = set(title.lower().split())
        
        # Se o tópico está contido no título, são similares
        return topic_words.issubset(title_words)

    def _get_real_topics(self):
        """Busca tópicos reais do Google News"""
        try:
            from gnews import GNews
            
            # Configurar GNews para Brasil
            google_news = GNews(
                language='pt', 
                country='BR', 
                period='1d', 
                max_results=8,
                exclude_websites=['youtube.com', 'instagram.com', 'facebook.com']
            )
            
            # Buscar top news
            articles = google_news.get_top_news()
            if not articles:
                return []
            
            # Extrair tópicos dos títulos
            topics = []
            for article in articles[:6]:  # Limitar a 6 artigos
                title = article.get('title', '')
                if title and len(title) > 10:
                    # Limpar e extrair tópico do título
                    topic = self._extract_topic_from_title(title)
                    if topic and topic not in topics:
                        topics.append(topic)
            
            if topics:
                self.stdout.write(f"✓ Tópicos do Google News: {len(topics)} encontrados")
                return topics[:5]  # Retornar até 5 tópicos
            
            return []
            
        except Exception as e:
            self.stdout.write(f"⚠ Erro no Google News: {e}")
            return []

    def _extract_topic_from_title(self, title):
        """Extrai tópico relevante do título da notícia"""
        # Remover palavras comuns e extrair tópico principal
        common_words = ['no', 'do', 'da', 'em', 'para', 'com', 'por', 'que', 'é', 'foi', 'ser', 'ter', 'há', 'mais', 'menos', 'sobre', 'após', 'durante', 'entre', 'até', 'desde', 'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 'umas', 'de', 'e', 'ou', 'mas', 'se', 'não', 'já', 'ainda', 'também', 'só', 'muito', 'pouco', 'todo', 'toda', 'todos', 'todas', 'cada', 'qual', 'quando', 'onde', 'como', 'porque', 'porquê', 'por que', 'por quê']
        
        # Limpar título
        title_clean = title.lower()
        words = title_clean.split()
        
        # Remover palavras comuns
        relevant_words = [word for word in words if word not in common_words and len(word) > 3]
        
        if relevant_words:
            # Pegar as 2-3 palavras mais relevantes
            topic = ' '.join(relevant_words[:3])
            return topic
        
        return None
