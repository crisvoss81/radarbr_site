from django.core.management.base import BaseCommand
from rb_ingestor.instagram_image_finder import InstagramImageFinder

class Command(BaseCommand):
    help = 'Testa o sistema de busca de imagens do Instagram'

    def add_arguments(self, parser):
        parser.add_argument('--topic', type=str, help='Tópico para testar')
        parser.add_argument('--title', type=str, help='Título do artigo')
        parser.add_argument('--content', type=str, help='Conteúdo do artigo')

    def handle(self, *args, **options):
        topic = options.get('topic', 'Katy Perry')
        title = options.get('title', f'Notícia sobre {topic}')
        content = options.get('content', f'Artigo sobre {topic} e suas atividades recentes')
        
        self.stdout.write(f"🧪 Testando busca de imagens do Instagram para: {topic}")
        self.stdout.write("=" * 60)
        
        instagram_finder = InstagramImageFinder()
        
        # Simular notícia original
        news_article = {
            'title': f'{topic} faz nova declaração',
            'description': f'Confira as últimas notícias sobre {topic}',
            'url': 'https://example.com/news'
        }
        
        # Testar busca de figura pública
        public_figure = instagram_finder.find_public_figure_instagram(f"{title} {content}")
        
        if public_figure:
            self.stdout.write(f"✅ Figura pública detectada: {public_figure['figure']}")
            self.stdout.write(f"📱 Instagram: {public_figure['instagram_handle']}")
            self.stdout.write(f"🔗 URL: {public_figure['instagram_url']}")
            
            # Testar extração de imagem de rede social do artigo original
            social_image = instagram_finder.extract_social_media_images_from_news(news_article)
            if social_image:
                self.stdout.write("📱 Imagem de rede social encontrada no artigo original!")
                self.stdout.write(f"🖼️ URL: {social_image.get('url', 'N/A')}")
                self.stdout.write(f"📝 Alt: {social_image.get('alt', 'N/A')}")
                self.stdout.write(f"©️ Crédito: {social_image.get('credit', 'N/A')}")
            else:
                self.stdout.write("❌ Nenhuma imagem de rede social no artigo original")
            
            # Testar busca de imagem do Instagram oficial
            instagram_image = instagram_finder.get_instagram_image_for_article(
                title, content, news_article
            )
            
            if instagram_image and instagram_image.get('url'):
                self.stdout.write("📱 Imagem do Instagram oficial encontrada!")
                self.stdout.write(f"🖼️ URL: {instagram_image.get('url', 'N/A')}")
                self.stdout.write(f"📝 Alt: {instagram_image.get('alt', 'N/A')}")
                self.stdout.write(f"©️ Crédito: {instagram_image.get('credit', 'N/A')}")
            else:
                self.stdout.write("❌ Nenhuma imagem do Instagram oficial encontrada")
                self.stdout.write("🖼️ Sistema usará banco de imagens gratuitos")
        else:
            self.stdout.write("❌ Nenhuma figura pública detectada")
            self.stdout.write("🖼️ Sistema usará banco de imagens gratuitos")
        
        self.stdout.write("\n" + "=" * 60)
        
        # Testar extração de menções
        test_text = f"Confira o que {topic} postou no Instagram @katyperry #celebridade"
        mentions = instagram_finder.extract_instagram_mentions(test_text)
        
        self.stdout.write(f"📱 Menções encontradas em '{test_text}':")
        for mention in mentions:
            self.stdout.write(f"  - {mention}")
        
        # Testar busca de figura pública
        public_figure = instagram_finder.find_public_figure_instagram(test_text)
        if public_figure:
            self.stdout.write(f"\n🎭 Figura pública encontrada: {public_figure['figure']}")
            self.stdout.write(f"📱 Instagram: {public_figure['instagram_handle']}")
            self.stdout.write(f"🔗 URL: {public_figure['instagram_url']}")
        
        self.stdout.write("\n✅ Teste concluído!")
