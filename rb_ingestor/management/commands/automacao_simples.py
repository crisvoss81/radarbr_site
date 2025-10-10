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
            
            slug = slugify(title)[:180]
            
            # Verificar se já existe
            if not options["force"] and Noticia.objects.filter(slug=slug).exists():
                self.stdout.write(f"⚠ Pulando: {title} (já existe)")
                continue
            
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
        """Busca e adiciona imagem à notícia (funciona sem Cloudinary)"""
        try:
            from rb_ingestor.images_free import pick_image
            
            # Buscar imagem gratuita
            image_info = pick_image(topico)
            
            if image_info and image_info.get("url"):
                # Salvar URL da imagem diretamente (sem Cloudinary)
                noticia.imagem = image_info["url"]
                noticia.imagem_alt = f"Imagem relacionada a {topico}"
                noticia.imagem_credito = image_info.get("credito", "Imagem gratuita")
                noticia.imagem_licenca = image_info.get("licenca", "CC")
                noticia.imagem_fonte_url = image_info.get("fonte_url", image_info["url"])
                noticia.save()
                
                self.stdout.write(f"✓ Imagem adicionada: {topico}")
            else:
                self.stdout.write(f"⚠ Nenhuma imagem encontrada para: {topico}")
                
        except Exception as e:
            self.stdout.write(f"⚠ Erro ao buscar imagem para {topico}: {e}")
