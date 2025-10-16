# rb_ingestor/management/commands/test_news_images.py
"""
Comando para testar extração de imagens da notícia original
"""
from django.core.management.base import BaseCommand
from rb_ingestor.news_image_extractor import NewsImageExtractor

class Command(BaseCommand):
    help = "Testa extração de imagens da notícia original"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DE EXTRAÇÃO DE IMAGENS DA NOTÍCIA ORIGINAL ===")
        
        extractor = NewsImageExtractor()
        
        # Teste com a notícia do O Globo sobre Katy Perry
        test_url = "https://oglobo.globo.com/cultura/noticia/2025/10/12/katy-perry-e-justin-trudeau-saiba-como-comecou-romance-entre-a-pop-star-e-o-ex-primeiro-ministro-do-canada.ghtml"
        test_title = "Katy Perry e Justin Trudeau: saiba como começou romance"
        
        self.stdout.write(f"\n🔍 Testando extração de: {test_url}")
        
        try:
            images_data = extractor.extract_images_from_news(test_url, test_title)
            
            if images_data.get('success'):
                self.stdout.write(f"✅ Sucesso! {len(images_data['images'])} imagens encontradas")
                self.stdout.write(f"📝 Fonte: {images_data['source']}")
                self.stdout.write(f"📝 Crédito: {images_data['credit']}")
                
                for i, image in enumerate(images_data['images'], 1):
                    self.stdout.write(f"\n🖼️ Imagem {i}:")
                    self.stdout.write(f"   URL: {image['url']}")
                    self.stdout.write(f"   Alt: {image['alt']}")
                    self.stdout.write(f"   Caption: {image['caption']}")
                
                # Testar seleção da melhor imagem
                best_image = extractor.get_best_image(images_data)
                if best_image:
                    self.stdout.write(f"\n⭐ Melhor imagem selecionada:")
                    self.stdout.write(f"   URL: {best_image['url']}")
                    self.stdout.write(f"   Crédito: {best_image['credit']}")
                
            else:
                self.stdout.write("❌ Falha na extração de imagens")
                if images_data.get('error'):
                    self.stdout.write(f"   Erro: {images_data['error']}")
                    
        except Exception as e:
            self.stdout.write(f"❌ Erro no teste: {e}")
        
        self.stdout.write("\n=== FIM DO TESTE ===")



