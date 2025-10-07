# rb_ingestor/management/commands/test_render.py
"""
Comando de teste para verificar se o Django está funcionando no Render
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from rb_noticias.models import Noticia
import os

class Command(BaseCommand):
    help = "Testa se o Django está funcionando no Render"

    def handle(self, *args, **options):
        try:
            self.stdout.write("=== TESTE RENDER DJANGO ===")
            self.stdout.write(f"Data/Hora: {timezone.now()}")
            self.stdout.write(f"Diretório: {os.getcwd()}")
            self.stdout.write(f"Python: {os.sys.executable}")
            
            # Testar conexão com banco
            count = Noticia.objects.count()
            self.stdout.write(f"Total de notícias no banco: {count}")
            
            # Testar criação de notícia de teste
            test_news = Noticia.objects.create(
                titulo="TESTE RENDER - " + str(timezone.now()),
                conteudo="Esta é uma notícia de teste para verificar se o Django está funcionando no Render.",
                fonte_url="https://teste-render.com",
                publicado_em=timezone.now()
            )
            
            self.stdout.write(f"Notícia de teste criada: {test_news.id}")
            
            # Deletar notícia de teste
            test_news.delete()
            self.stdout.write("Notícia de teste removida")
            
            self.stdout.write("=== TESTE CONCLUÍDO COM SUCESSO ===")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERRO NO TESTE: {str(e)}"))
            raise
