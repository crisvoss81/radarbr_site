# rb_ingestor/management/commands/test_news_search.py
"""
Comando simples para testar busca de notícias no Render
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = "Testa busca de notícias específicas no Render"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=3, help="Número de notícias a buscar")

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE BUSCA DE NOTÍCIAS ===")
        self.stdout.write(f"Executado em: {timezone.now()}")
        
        try:
            from gnews import GNews
            
            # Configurar GNews
            google_news = GNews(
                language='pt', 
                country='BR', 
                period='1d', 
                max_results=options["limit"],
                exclude_websites=['youtube.com', 'instagram.com', 'facebook.com']
            )
            
            # Buscar notícias
            articles = google_news.get_top_news()
            
            if articles:
                self.stdout.write(f"✅ Encontradas {len(articles)} notícias:")
                for i, article in enumerate(articles[:options["limit"]]):
                    title = article.get('title', '')
                    source = article.get('publisher', {}).get('title', '')
                    description = article.get('description', '')
                    
                    self.stdout.write(f"\n{i+1}. {title}")
                    self.stdout.write(f"   Fonte: {source}")
                    self.stdout.write(f"   Descrição: {description[:100]}...")
                    
                    # Extrair tópico
                    topic = self._extract_topic(title)
                    self.stdout.write(f"   Tópico: {topic}")
                    
                    # Categorizar
                    category = self._categorize_news(title, description)
                    self.stdout.write(f"   Categoria: {category}")
            else:
                self.stdout.write("❌ Nenhuma notícia encontrada")
                
        except Exception as e:
            self.stdout.write(f"❌ Erro: {e}")

    def _extract_topic(self, title):
        """Extrai tópico do título"""
        common_words = [
            'no', 'do', 'da', 'em', 'para', 'com', 'por', 'que', 'é', 'foi', 
            'ser', 'ter', 'há', 'mais', 'menos', 'sobre', 'após', 'durante', 
            'entre', 'até', 'desde', 'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 
            'umas', 'de', 'e', 'ou', 'mas', 'se', 'não', 'já', 'ainda', 'também'
        ]
        
        title_clean = title.lower()
        words = title_clean.split()
        
        relevant_words = [word for word in words if word not in common_words and len(word) > 3]
        
        if relevant_words:
            return ' '.join(relevant_words[:3])
        
        return title[:50]

    def _categorize_news(self, title, description):
        """Categoriza notícia baseada no conteúdo"""
        text = f"{title} {description}".lower()
        
        category_keywords = {
            "tecnologia": ["tecnologia", "digital", "ia", "inteligência artificial", "chatgpt", "app", "software"],
            "economia": ["economia", "mercado", "inflação", "dólar", "real", "investimento", "finanças"],
            "política": ["política", "governo", "eleições", "presidente", "lula", "bolsonaro", "congresso"],
            "esportes": ["esportes", "futebol", "copa", "mundial", "brasileirão", "atletismo"],
            "saúde": ["saúde", "medicina", "hospital", "vacina", "covid", "coronavírus"],
            "meio ambiente": ["meio ambiente", "sustentabilidade", "natureza", "clima", "ecologia"],
            "mundo": ["china", "eua", "europa", "internacional", "global", "mundial", "país"]
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in text for kw in keywords):
                return category
        
        return "brasil"
