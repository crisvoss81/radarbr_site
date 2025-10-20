from django.core.management.base import BaseCommand
from rb_ingestor.news_image_extractor import NewsImageExtractor

class Command(BaseCommand):
    help = 'Extrai imagens de uma URL de notícia'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL da notícia')

    def handle(self, *args, **options):
        url = options['url']
        
        self.stdout.write(f"🔍 Extraindo imagens de: {url}")
        
        extractor = NewsImageExtractor()
        result = extractor.extract_images_from_news(url)
        
        if result['success']:
            self.stdout.write(f"✅ {len(result['images'])} imagens encontradas")
            self.stdout.write(f"📰 Fonte: {result['source']}")
            self.stdout.write(f"📸 Crédito: {result.get('credit', 'N/A')}")
            self.stdout.write()
            
            for i, img in enumerate(result['images'], 1):
                self.stdout.write(f"{i}. {img['alt']}")
                self.stdout.write(f"   URL: {img['url']}")
                if img['caption']:
                    self.stdout.write(f"   Legenda: {img['caption']}")
                self.stdout.write()
        else:
            self.stdout.write(f"❌ Erro: {result.get('error', 'Nenhuma imagem encontrada')}")
