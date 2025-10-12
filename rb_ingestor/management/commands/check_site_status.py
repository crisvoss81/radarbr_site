# rb_ingestor/management/commands/check_site_status.py
"""
Comando para verificar o status do site
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
import os

class Command(BaseCommand):
    help = "Verifica o status do site e configurações"

    def handle(self, *args, **options):
        self.stdout.write("=== VERIFICAÇÃO DE STATUS DO SITE ===")
        
        # Informações do ambiente
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"RENDER: {os.getenv('RENDER', 'False')}")
        
        # Teste de banco
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                self.stdout.write("✅ Banco de dados: OK")
        except Exception as e:
            self.stdout.write(f"❌ Banco de dados: ERRO - {e}")
            
        # Teste de modelos
        try:
            from rb_noticias.models import Noticia, Categoria
            noticias_count = Noticia.objects.count()
            categorias_count = Categoria.objects.count()
            self.stdout.write(f"✅ Modelos: OK ({noticias_count} notícias, {categorias_count} categorias)")
        except Exception as e:
            self.stdout.write(f"❌ Modelos: ERRO - {e}")
            
        # Teste de configurações críticas
        try:
            secret_key = settings.SECRET_KEY
            if secret_key and len(secret_key) > 10:
                self.stdout.write("✅ SECRET_KEY: OK")
            else:
                self.stdout.write("❌ SECRET_KEY: PROBLEMA")
        except Exception as e:
            self.stdout.write(f"❌ SECRET_KEY: ERRO - {e}")
            
        # Teste de arquivos estáticos
        try:
            static_root = settings.STATIC_ROOT
            if static_root:
                self.stdout.write(f"✅ STATIC_ROOT: {static_root}")
            else:
                self.stdout.write("❌ STATIC_ROOT: NÃO CONFIGURADO")
        except Exception as e:
            self.stdout.write(f"❌ STATIC_ROOT: ERRO - {e}")
            
        self.stdout.write("=== FIM DA VERIFICAÇÃO ===")
