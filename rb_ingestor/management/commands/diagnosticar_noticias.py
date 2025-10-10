# rb_ingestor/management/commands/diagnosticar_noticias.py
"""
Comando para diagnosticar problemas com notícias
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone

class Command(BaseCommand):
    help = "Diagnostica problemas com notícias e categorias"

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        self.stdout.write("=== DIAGNOSTICO DE NOTICIAS ===")
        
        # Contadores
        total_noticias = Noticia.objects.count()
        total_categorias = Categoria.objects.count()
        
        self.stdout.write(f"Total de noticias: {total_noticias}")
        self.stdout.write(f"Total de categorias: {total_categorias}")
        
        # Últimas notícias
        self.stdout.write("\n=== ULTIMAS 5 NOTICIAS ===")
        ultimas_noticias = Noticia.objects.order_by('-criado_em')[:5]
        
        if ultimas_noticias.exists():
            for i, n in enumerate(ultimas_noticias, 1):
                self.stdout.write(f"{i}. Título: {n.titulo}")
                self.stdout.write(f"   Categoria: {n.categoria.nome if n.categoria else 'Sem categoria'}")
                self.stdout.write(f"   Slug: {n.slug}")
                self.stdout.write(f"   Status: {n.status}")
                self.stdout.write(f"   Criado: {n.criado_em}")
                self.stdout.write(f"   Fonte: {n.fonte_nome}")
                self.stdout.write("")
        else:
            self.stdout.write("Nenhuma notícia encontrada")
        
        # Últimas categorias
        self.stdout.write("=== ULTIMAS 5 CATEGORIAS ===")
        ultimas_categorias = Categoria.objects.order_by('-id')[:5]
        
        if ultimas_categorias.exists():
            for i, c in enumerate(ultimas_categorias, 1):
                count_noticias = Noticia.objects.filter(categoria=c).count()
                self.stdout.write(f"{i}. Nome: {c.nome}")
                self.stdout.write(f"   Slug: {c.slug}")
                self.stdout.write(f"   Notícias nesta categoria: {count_noticias}")
                self.stdout.write("")
        else:
            self.stdout.write("Nenhuma categoria encontrada")
        
        # Verificar problemas
        self.stdout.write("=== VERIFICACAO DE PROBLEMAS ===")
        
        # Notícias sem categoria
        noticias_sem_categoria = Noticia.objects.filter(categoria__isnull=True).count()
        if noticias_sem_categoria > 0:
            self.stdout.write(f"AVISO: {noticias_sem_categoria} notícias sem categoria")
        
        # Categorias sem notícias
        categorias_sem_noticias = []
        for cat in Categoria.objects.all():
            if Noticia.objects.filter(categoria=cat).count() == 0:
                categorias_sem_noticias.append(cat.nome)
        
        if categorias_sem_noticias:
            self.stdout.write(f"AVISO: Categorias sem notícias: {', '.join(categorias_sem_noticias)}")
        
        # Verificar se há notícias com títulos estranhos
        noticias_suspeitas = Noticia.objects.filter(
            titulo__icontains="categoria"
        ) | Noticia.objects.filter(
            titulo__icontains="category"
        )
        
        if noticias_suspeitas.exists():
            self.stdout.write("ERRO: Encontradas notícias suspeitas:")
            for n in noticias_suspeitas:
                self.stdout.write(f"  - {n.titulo}")
        else:
            self.stdout.write("OK: Nenhuma notícia suspeita encontrada")
        
        self.stdout.write("\n=== RESUMO ===")
        self.stdout.write(f"Notícias: {total_noticias}")
        self.stdout.write(f"Categorias: {total_categorias}")
        self.stdout.write("Diagnóstico concluído!")
