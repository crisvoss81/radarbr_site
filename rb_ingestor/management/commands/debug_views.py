# rb_ingestor/management/commands/debug_views.py
"""
Comando para debugar views e identificar erros 500
"""
from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from rb_portal.views import home, category_list
from rb_noticias.models import Noticia, Categoria
from django.conf import settings
import traceback

class Command(BaseCommand):
    help = "Debuga views para identificar erros 500"

    def handle(self, *args, **options):
        self.stdout.write("=== DEBUG DE VIEWS ===")
        
        factory = RequestFactory()
        
        # Teste da view home
        try:
            self.stdout.write("🔍 Testando view HOME...")
            request = factory.get('/')
            request.user = AnonymousUser()
            
            # Simular configurações de produção
            settings.DEBUG = False
            
            response = home(request)
            self.stdout.write(f"✅ HOME: Status {response.status_code}")
            
        except Exception as e:
            self.stdout.write(f"❌ HOME: ERRO - {e}")
            self.stdout.write(f"📋 Traceback: {traceback.format_exc()}")
            
        # Teste de queries do banco
        try:
            self.stdout.write("🔍 Testando queries do banco...")
            
            # Teste básico
            noticias_count = Noticia.objects.count()
            self.stdout.write(f"✅ Notícias: {noticias_count}")
            
            # Teste da query da home
            qs = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by("-publicado_em")
            self.stdout.write(f"✅ Query home: {qs.count()} notícias")
            
            # Teste de categorias
            categorias = Categoria.objects.all()
            self.stdout.write(f"✅ Categorias: {categorias.count()}")
            
        except Exception as e:
            self.stdout.write(f"❌ Queries: ERRO - {e}")
            self.stdout.write(f"📋 Traceback: {traceback.format_exc()}")
            
        # Teste de templates
        try:
            self.stdout.write("🔍 Testando templates...")
            from django.template.loader import get_template
            template = get_template('rb_portal/home.html')
            self.stdout.write("✅ Template home.html: OK")
            
        except Exception as e:
            self.stdout.write(f"❌ Templates: ERRO - {e}")
            self.stdout.write(f"📋 Traceback: {traceback.format_exc()}")
            
        self.stdout.write("=== FIM DO DEBUG ===")
