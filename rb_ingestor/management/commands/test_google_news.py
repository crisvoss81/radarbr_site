# rb_ingestor/management/commands/test_google_news.py
"""
Comando para testar o Google News
"""
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Testa o Google News"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DO GOOGLE NEWS ===")
        
        try:
            from gnews import GNews
            
            # Configurar GNews
            google_news = GNews(
                language='pt', 
                country='BR', 
                period='1d', 
                max_results=5,
                exclude_websites=['youtube.com', 'instagram.com', 'facebook.com']
            )
            
            self.stdout.write("🔍 Buscando notícias no Google News...")
            
            # Buscar notícias
            articles = google_news.get_top_news()
            
            if articles:
                self.stdout.write(f"✅ Google News funcionando: {len(articles)} artigos encontrados")
                
                for i, article in enumerate(articles[:5], 1):
                    title = article.get('title', 'Sem título')
                    url = article.get('url', 'Sem URL')
                    published = article.get('published date', 'Sem data')
                    
                    self.stdout.write(f"\n{i}. {title}")
                    self.stdout.write(f"   📅 Data: {published}")
                    self.stdout.write(f"   🔗 URL: {url[:80]}...")
                    
                    # Extrair tópico do título
                    topic = self._extract_topic_from_title(title)
                    self.stdout.write(f"   🎯 Tópico extraído: {topic}")
            else:
                self.stdout.write("❌ Nenhum artigo encontrado no Google News")
                
        except Exception as e:
            self.stdout.write(f"❌ Erro no Google News: {e}")

    def _extract_topic_from_title(self, title):
        """Extrai tópico relevante do título"""
        common_words = [
            'no', 'do', 'da', 'em', 'para', 'com', 'por', 'que', 'é', 'foi',
            'ser', 'ter', 'há', 'mais', 'menos', 'sobre', 'a', 'o', 'as', 'os',
            'um', 'uma', 'de', 'e', 'ou', 'mas', 'se', 'não', 'já', 'ainda'
        ]
        
        title_clean = title.lower()
        words = title_clean.split()
        
        relevant_words = [word for word in words if word not in common_words and len(word) > 3]
        
        if relevant_words:
            return ' '.join(relevant_words[:3])
        
        return None
