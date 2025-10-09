# rb_ingestor/management/commands/diagnosticar_problema.py
"""
Comando para diagnosticar o problema com smart_automation
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Diagnostica problemas com comandos de automação"

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        self.stdout.write("=== DIAGNÓSTICO DO PROBLEMA ===")
        
        # Verificar últimas notícias
        self.stdout.write("\n📰 ÚLTIMAS 10 NOTÍCIAS:")
        noticias = Noticia.objects.order_by('-criado_em')[:10]
        
        for i, n in enumerate(noticias, 1):
            self.stdout.write(f"{i}. Título: {n.titulo}")
            self.stdout.write(f"   Categoria: {n.categoria.nome if n.categoria else 'Sem categoria'}")
            self.stdout.write(f"   Slug: {n.slug}")
            self.stdout.write(f"   Status: {n.status}")
            self.stdout.write(f"   Fonte: {n.fonte_nome}")
            self.stdout.write(f"   Criado: {n.criado_em}")
            self.stdout.write("")
        
        # Verificar categorias
        self.stdout.write("\n📂 CATEGORIAS EXISTENTES:")
        categorias = Categoria.objects.all()
        for cat in categorias:
            count = Noticia.objects.filter(categoria=cat).count()
            self.stdout.write(f"• {cat.nome} (slug: {cat.slug}) - {count} notícias")
        
        # Verificar notícias recentes
        recentes = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=6)
        )
        
        self.stdout.write(f"\n⏰ NOTÍCIAS ÚLTIMAS 6 HORAS: {recentes.count()}")
        for n in recentes:
            self.stdout.write(f"• {n.titulo} ({n.fonte_nome})")
        
        # Verificar se há notícias com títulos estranhos
        self.stdout.write("\n🔍 VERIFICANDO TÍTULOS SUSPEITOS:")
        suspeitas = Noticia.objects.filter(
            titulo__icontains="categoria"
        ) | Noticia.objects.filter(
            titulo__icontains="category"
        )
        
        if suspeitas.exists():
            self.stdout.write("⚠️ ENCONTRADAS NOTÍCIAS SUSPEITAS:")
            for n in suspeitas:
                self.stdout.write(f"• {n.titulo}")
        else:
            self.stdout.write("✅ Nenhuma notícia suspeita encontrada")
        
        # Verificar fonte_nome
        self.stdout.write("\n📊 ANÁLISE POR FONTE:")
        fontes = Noticia.objects.values('fonte_nome').distinct()
        for fonte in fontes:
            nome = fonte['fonte_nome']
            count = Noticia.objects.filter(fonte_nome=nome).count()
            self.stdout.write(f"• {nome}: {count} notícias")
        
        self.stdout.write("\n✅ DIAGNÓSTICO CONCLUÍDO")
