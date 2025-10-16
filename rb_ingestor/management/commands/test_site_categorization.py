# rb_ingestor/management/commands/test_site_categorization.py
"""
Comando para testar o sistema de extração de categorias dos sites
"""
from django.core.management.base import BaseCommand
from rb_ingestor.site_categorizer import SiteCategorizer

class Command(BaseCommand):
    help = "Testa o sistema de extração de categorias dos sites"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DE EXTRAÇÃO DE CATEGORIAS DOS SITES ===")
        
        categorizer = SiteCategorizer()
        
        # URLs de teste de diferentes sites
        test_urls = [
            "https://g1.globo.com/politica/noticia/2024/10/12/lula-anuncia-novo-pacote-economico.ghtml",
            "https://oglobo.globo.com/economia/noticia/2024/10/12/dolar-sobe-apos-decisao-banco-central.ghtml",
            "https://folha.uol.com.br/esporte/2024/10/12/flamengo-vence-corinthians.ghtml",
            "https://cnnbrasil.com.br/tecnologia/2024/10/12/startup-desenvolve-ia-diagnostico.ghtml",
            "https://infomoney.com.br/economia/2024/10/12/inflacao-brasileira-monitorada.ghtml"
        ]
        
        for i, url in enumerate(test_urls, 1):
            self.stdout.write(f"\n🔍 Teste {i}: {url}")
            
            try:
                # Simular artigo
                article = {'url': url}
                
                # Extrair categoria
                category = categorizer.categorize_article(article)
                
                if category:
                    self.stdout.write(f"✅ Categoria extraída: {category}")
                else:
                    self.stdout.write(f"❌ Não foi possível extrair categoria")
                    
            except Exception as e:
                self.stdout.write(f"❌ Erro: {e}")
        
        self.stdout.write("\n=== FIM DOS TESTES ===")

