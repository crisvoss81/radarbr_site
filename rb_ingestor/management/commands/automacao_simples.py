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
        
        # Tópicos pré-definidos para teste
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
        
        # Criar categoria geral se não existir
        cat_geral, created = Categoria.objects.get_or_create(
            slug="geral",
            defaults={"nome": "Geral"}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Categoria criada: {cat_geral.nome}"))
        
        created_count = 0
        limit = options["limit"]
        
        for i in range(limit):
            # Escolher tópico aleatório
            topico = random.choice(topicos)
            
            # Gerar título único
            timestamp = timezone.now().strftime('%d/%m %H:%M')
            title = f"{topico} - {timestamp}"
            slug = slugify(title)[:180]
            
            # Verificar se já existe
            if not options["force"] and Noticia.objects.filter(slug=slug).exists():
                self.stdout.write(f"⚠ Pulando: {title} (já existe)")
                continue
            
            # Gerar conteúdo simples
            conteudo = self._gerar_conteudo_simples(topico)
            
            # Criar notícia
            try:
                noticia = Noticia.objects.create(
                    titulo=title,
                    slug=slug,
                    conteudo=conteudo,
                    publicado_em=timezone.now(),
                    categoria=cat_geral,
                    fonte_url=f"automacao-simples-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}",
                    fonte_nome="RadarBR Automação",
                    status=1  # PUBLICADO
                )
                
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
        """Gera conteúdo simples sem usar IA"""
        
        conteudos = {
            "Tecnologia no Brasil": """
            <h2>Desenvolvimento Tecnológico no Brasil</h2>
            <p>O Brasil tem se destacado no cenário tecnológico mundial com inovações em diversas áreas.</p>
            
            <h3>Principais Áreas de Destaque</h3>
            <ul>
                <li>Fintechs e pagamentos digitais</li>
                <li>Agronegócio tecnológico</li>
                <li>E-commerce e marketplaces</li>
                <li>Inteligência artificial aplicada</li>
            </ul>
            
            <h3>Desafios e Oportunidades</h3>
            <p>O país enfrenta desafios como infraestrutura digital e capacitação técnica, mas também apresenta grandes oportunidades de crescimento.</p>
            """,
            
            "Economia brasileira atual": """
            <h2>Panorama da Economia Brasileira</h2>
            <p>A economia brasileira apresenta sinais de recuperação com indicadores positivos em diversos setores.</p>
            
            <h3>Indicadores Principais</h3>
            <ul>
                <li>Crescimento do PIB</li>
                <li>Controle da inflação</li>
                <li>Geração de empregos</li>
                <li>Investimentos externos</li>
            </ul>
            
            <h3>Perspectivas Futuras</h3>
            <p>As projeções indicam um cenário positivo para os próximos trimestres, com foco em sustentabilidade e inovação.</p>
            """,
            
            "Esportes nacionais": """
            <h2>Esportes no Brasil</h2>
            <p>O Brasil continua sendo uma potência esportiva mundial com destaque em diversas modalidades.</p>
            
            <h3>Modalidades em Destaque</h3>
            <ul>
                <li>Futebol profissional</li>
                <li>Vôlei e vôlei de praia</li>
                <li>Atletismo</li>
                <li>Natação</li>
            </ul>
            
            <h3>Preparação para Competições</h3>
            <p>Os atletas brasileiros se preparam intensamente para as próximas competições internacionais.</p>
            """
        }
        
        # Conteúdo padrão se não encontrar o tópico específico
        conteudo_padrao = f"""
        <h2>{topico}</h2>
        <p>Este é um artigo sobre {topico.lower()} desenvolvido pelo sistema de automação.</p>
        
        <h3>Principais Aspectos</h3>
        <ul>
            <li>Aspecto importante 1</li>
            <li>Aspecto importante 2</li>
            <li>Aspecto importante 3</li>
        </ul>
        
        <h3>Conclusão</h3>
        <p>{topico} é um tema relevante que merece atenção e análise contínua.</p>
        """
        
        return conteudos.get(topico, conteudo_padrao)
