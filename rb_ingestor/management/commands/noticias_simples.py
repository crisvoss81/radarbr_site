# rb_ingestor/management/commands/noticias_simples.py
"""
Comando ultra-simples para gerar notícias no Render
Sem dependências externas, apenas Django puro
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from slugify import slugify
import random

class Command(BaseCommand):
    help = "Gerador ultra-simples de notícias"

    def add_arguments(self, parser):
        parser.add_argument("--num", type=int, default=3, help="Número de notícias")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        print("=== GERADOR ULTRA-SIMPLES ===")
        
        # Criar categoria se não existir
        cat, created = Categoria.objects.get_or_create(
            slug="geral",
            defaults={"nome": "Geral"}
        )
        
        if created:
            print(f"OK Categoria criada: {cat.nome}")
        
        # Tópicos simples
        topicos = [
            "Tecnologia",
            "Economia", 
            "Esportes",
            "Cultura",
            "Política",
            "Meio Ambiente",
            "Educação",
            "Saúde",
            "Inovação",
            "Turismo"
        ]
        
        criadas = 0
        num = options["num"]
        
        for i in range(num):
            topico = random.choice(topicos)
            timestamp = timezone.now().strftime('%d/%m %H:%M')
            titulo = f"{topico} - {timestamp}"
            slug = slugify(titulo)[:180]
            
            # Verificar se já existe
            if Noticia.objects.filter(slug=slug).exists():
                print(f"AVISO Pulando: {titulo} (ja existe)")
                continue
            
            # Conteúdo simples
            conteudo = f"""
            <h2>{topico}</h2>
            <p>Artigo sobre {topico} gerado automaticamente.</p>
            <p>Este conteúdo aborda aspectos importantes relacionados ao tema.</p>
            <p><em>Gerado pelo RadarBR em {timestamp}</em></p>
            """
            
            try:
                noticia = Noticia.objects.create(
                    titulo=titulo,
                    slug=slug,
                    conteudo=conteudo,
                    publicado_em=timezone.now(),
                    categoria=cat,
                    fonte_url=f"simples-{timezone.now().strftime('%Y%m%d-%H%M')}-{i}",
                    fonte_nome="RadarBR Simples",
                    status=1
                )
                
                criadas += 1
                print(f"OK Criado: {titulo}")
                
            except Exception as e:
                print(f"ERRO: {e}")
        
        print(f"\nCONCLUIDO: {criadas} noticias criadas")
        print(f"Total no sistema: {Noticia.objects.count()}")
