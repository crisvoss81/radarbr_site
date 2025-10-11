# rb_ingestor/management/commands/manual_article.py
"""
Comando simples para publicar artigo manual
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from slugify import slugify
from django.apps import apps

class Command(BaseCommand):
    help = "Publica artigo com tópico manual"

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="Tópico para o artigo")
        parser.add_argument("--category", type=str, default="tecnologia", help="Categoria")
        parser.add_argument("--dry-run", action="store_true", help="Apenas simula")

    def handle(self, *args, **options):
        self.stdout.write("=== ARTIGO MANUAL ===")
        
        topic = options["topic"]
        category = options["category"]
        
        self.stdout.write(f"📝 Tópico: {topic}")
        self.stdout.write(f"🏷️  Categoria: {category}")
        
        # Gerar título
        title = f"{topic}: Análise Completa 2025"
        
        # Gerar conteúdo básico
        content = f"""<p class="dek">Análise completa sobre {topic.lower()}, oferecendo informações atualizadas e insights valiosos.</p>

<h2>{topic}: Análise Completa</h2>

<p>Uma análise detalhada sobre {topic.lower()} e seu impacto no cenário atual brasileiro. Este tema tem ganhado cada vez mais relevância no Brasil, merecendo atenção especial dos profissionais e interessados na área.</p>

<h3>Introdução</h3>

<p>Para compreender completamente a importância de {topic.lower()}, é fundamental analisar seu contexto histórico e sua evolução ao longo do tempo. O Brasil, com sua rica diversidade cultural e geográfica, apresenta características únicas que influenciam diretamente como este tema se desenvolve em nosso país.</p>

<h3>Desenvolvimento Principal</h3>

<p>Os especialistas brasileiros destacam que {topic.lower()} tem ganhado cada vez mais relevância no cenário nacional. As mudanças observadas nos últimos meses indicam uma tendência consistente que merece atenção especial dos profissionais da área.</p>

<p>Esta evolução tem sido acompanhada de perto por analistas e pesquisadores que estudam o impacto dessas transformações na sociedade brasileira. Os dados mais recentes mostram uma evolução positiva em diversos indicadores relacionados ao tema.</p>

<h3>Impacto no Brasil</h3>

<p>A população brasileira tem sentido diretamente os efeitos das transformações relacionadas a {topic.lower()}. Desde as grandes metrópoles como São Paulo e Rio de Janeiro até as cidades do interior, é possível observar mudanças significativas que afetam o dia a dia das pessoas.</p>

<p>Estas alterações têm sido recebidas de forma positiva pela maioria da população brasileira, que vê nas mudanças uma oportunidade de melhoria na qualidade de vida e desenvolvimento do país.</p>

<h3>Perspectivas Futuras</h3>

<p>As projeções para {topic.lower()} indicam que esta tendência deve se manter nos próximos anos, com possíveis desenvolvimentos que podem trazer benefícios adicionais para o Brasil. Os analistas são cautelosamente otimistas quanto ao futuro.</p>

<h3>Conclusão</h3>

<p>Esta matéria sobre {topic.lower()} foi desenvolvida com base em informações atualizadas e análises de especialistas da área. O RadarBR continua acompanhando os desdobramentos desta notícia e manterá os leitores informados sobre novos desenvolvimentos relacionados ao tema.</p>

<p>O cenário atual é promissor e indica que o Brasil está no caminho certo para se consolidar como uma referência em {topic.lower()}.</p>"""

        # Contar palavras
        word_count = len(strip_tags(content).split())
        
        self.stdout.write(f"📰 Título: {title}")
        self.stdout.write(f"📊 Palavras: {word_count}")
        
        if options["dry_run"]:
            self.stdout.write("🔍 MODO DRY-RUN - Simulação apenas")
            return
        
        # Criar notícia
        try:
            Noticia = apps.get_model("rb_noticias", "Noticia")
            Categoria = apps.get_model("rb_noticias", "Categoria")
            
            # Obter categoria
            cat = Categoria.objects.filter(nome=category.title()).first()
            if not cat:
                cat, created = Categoria.objects.get_or_create(
                    slug=slugify(category)[:140],
                    defaults={"nome": category.title()}
                )
            
            slug = slugify(f"{title}-{timezone.now().strftime('%Y%m%d-%H%M%S')}")[:180]
            
            noticia = Noticia.objects.create(
                titulo=title,
                slug=slug,
                conteudo=content,
                publicado_em=timezone.now(),
                categoria=cat,
                fonte_url=f"manual-{timezone.now().strftime('%Y%m%d-%H%M%S')}-{topic[:20].replace(' ', '-')}",
                fonte_nome="RadarBR Manual",
                status=1
            )
            
            self.stdout.write(f"✅ Artigo publicado: {title}")
            self.stdout.write(f"🔗 URL: /noticia/{slug}/")
            
        except Exception as e:
            self.stdout.write(f"❌ Erro: {e}")
