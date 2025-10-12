# rb_ingestor/management/commands/test_database.py
"""
Comando para testar a conexão com o banco de dados
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

class Command(BaseCommand):
    help = "Testa a conexão com o banco de dados"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DE CONEXÃO COM BANCO DE DADOS ===")
        
        # Informações do banco
        db_config = settings.DATABASES['default']
        self.stdout.write(f"Engine: {db_config['ENGINE']}")
        self.stdout.write(f"Name: {db_config['NAME']}")
        self.stdout.write(f"Host: {db_config.get('HOST', 'N/A')}")
        self.stdout.write(f"Port: {db_config.get('PORT', 'N/A')}")
        self.stdout.write(f"User: {db_config.get('USER', 'N/A')}")
        
        # Teste de conexão
        try:
            with connection.cursor() as cursor:
                if 'postgresql' in db_config['ENGINE']:
                    cursor.execute('SELECT version()')
                    version = cursor.fetchone()[0]
                    self.stdout.write(f"✅ PostgreSQL conectado: {version}")
                    
                    # Teste de tabelas
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                    tables = cursor.fetchall()
                    self.stdout.write(f"📊 Tabelas encontradas: {len(tables)}")
                    for table in tables:
                        self.stdout.write(f"  - {table[0]}")
                        
                elif 'sqlite' in db_config['ENGINE']:
                    cursor.execute('SELECT sqlite_version()')
                    version = cursor.fetchone()[0]
                    self.stdout.write(f"✅ SQLite conectado: {version}")
                    
                    # Teste de tabelas
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    self.stdout.write(f"📊 Tabelas encontradas: {len(tables)}")
                    for table in tables:
                        self.stdout.write(f"  - {table[0]}")
                        
        except Exception as e:
            self.stdout.write(f"❌ Erro na conexão: {e}")
            
        # Teste de modelos Django
        try:
            from rb_noticias.models import Noticia, Categoria
            self.stdout.write(f"📰 Notícias: {Noticia.objects.count()}")
            self.stdout.write(f"🏷️ Categorias: {Categoria.objects.count()}")
        except Exception as e:
            self.stdout.write(f"❌ Erro nos modelos: {e}")
