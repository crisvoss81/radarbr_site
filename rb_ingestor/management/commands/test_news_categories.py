# rb_ingestor/management/commands/test_news_categories.py
"""
Comando para testar se as APIs de notícias retornam categorias
"""
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Testa se as APIs de notícias retornam categorias"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DE CATEGORIAS DAS APIS DE NOTÍCIAS ===")
        
        # Testar diferentes temas usando GNews
        test_topics = [
            "futebol brasileiro",
            "economia brasileira", 
            "política nacional",
            "tecnologia",
            "saúde pública"
        ]
        
        for topic in test_topics:
            self.stdout.write(f"\n🔍 Testando: {topic}")
            
            try:
                from gnews import GNews
                
                # Configurar GNews
                google_news = GNews(
                    language='pt', 
                    country='BR', 
                    period='7d',
                    max_results=3
                )
                
                # Buscar notícias
                articles = google_news.get_news(topic)
                
                if articles:
                    for i, article in enumerate(articles, 1):
                        title = article.get('title', '')[:50]
                        # GNews não retorna categoria diretamente
                        # Vamos verificar outros campos disponíveis
                        available_fields = list(article.keys())
                        
                        self.stdout.write(f"  {i}. {title}...")
                        self.stdout.write(f"     Campos disponíveis: {available_fields}")
                        self.stdout.write(f"     Fonte: {article.get('publisher', {}).get('title', 'N/A')}")
                else:
                    self.stdout.write(f"  ❌ Nenhuma notícia encontrada")
                    
            except Exception as e:
                self.stdout.write(f"  ❌ Erro: {e}")
        
        self.stdout.write("\n=== CONCLUSÃO ===")
        self.stdout.write("GNews não retorna categoria diretamente.")
        self.stdout.write("Sistema inteligente será usado como fallback.")
        self.stdout.write("=== FIM DOS TESTES ===")
