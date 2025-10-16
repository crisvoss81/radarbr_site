# rb_ingestor/management/commands/test_news_video.py
"""
Comando para testar se o sistema extrai vídeo da notícia original
"""
from django.core.management.base import BaseCommand
from rb_ingestor.youtube_integration import YouTubeIntegration

class Command(BaseCommand):
    help = "Testa se o sistema extrai vídeo da notícia original"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DE EXTRAÇÃO DE VÍDEO DA NOTÍCIA ORIGINAL ===")
        
        youtube_integration = YouTubeIntegration()
        
        # Simular a notícia que você mencionou
        news_article = {
            'title': 'VÍDEO: Homem é mordido por traíra durante pescaria',
            'description': 'Confira o vídeo completo: https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'url': 'https://exemplo.com/noticia-com-video'
        }
        
        content = """
        <p>Um momento de lazer se transformou em um incidente surpreendente durante uma pescaria.</p>
        <p>O vídeo do ocorrido, que viralizou nas redes sociais, não apenas capturou a atenção do público.</p>
        <p>Continue lendo para mais informações sobre o assunto.</p>
        """
        
        self.stdout.write(f"\n📰 Notícia original:")
        self.stdout.write(f"   Título: {news_article['title']}")
        self.stdout.write(f"   Descrição: {news_article['description']}")
        
        # Testar extração de vídeo
        result = youtube_integration.integrate_video_into_content(
            content, "pescaria de traira", "Guia de Pescaria", news_article
        )
        
        if result != content:
            self.stdout.write("\n✅ Vídeo incluído no conteúdo!")
            self.stdout.write("📄 Conteúdo com vídeo:")
            self.stdout.write(result[:300] + "...")
        else:
            self.stdout.write("\n❌ Vídeo não foi incluído")
        
        # Testar extração direta do ID
        video_id = youtube_integration.extract_video_id(news_article['description'])
        if video_id:
            self.stdout.write(f"\n✅ ID do vídeo extraído: {video_id}")
        else:
            self.stdout.write("\n❌ Não foi possível extrair ID do vídeo")
        
        self.stdout.write("\n=== FIM DO TESTE ===")

