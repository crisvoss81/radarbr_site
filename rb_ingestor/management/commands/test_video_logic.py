# rb_ingestor/management/commands/test_video_logic.py
"""
Comando para testar a lógica de vídeo (só incluir quando mencionado)
"""
from django.core.management.base import BaseCommand
from rb_ingestor.youtube_integration import YouTubeIntegration

class Command(BaseCommand):
    help = "Testa a lógica de vídeo (só incluir quando mencionado)"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DA LÓGICA DE VÍDEO ===")
        
        youtube_integration = YouTubeIntegration()
        
        # Teste 1: Título menciona vídeo
        self.stdout.write("\n🎯 Teste 1: Título menciona vídeo")
        content1 = "<p>Artigo sobre pescaria.</p><p>Continue lendo...</p>"
        title1 = "VÍDEO: Guia completo de pescaria de traira"
        
        result1 = youtube_integration.integrate_video_into_content(
            content1, "pescaria", title1, None
        )
        
        if result1 != content1:
            self.stdout.write("✅ Vídeo incluído (correto - título menciona vídeo)")
        else:
            self.stdout.write("❌ Vídeo não incluído (incorreto)")
        
        # Teste 2: Conteúdo menciona vídeo
        self.stdout.write("\n🎯 Teste 2: Conteúdo menciona vídeo")
        content2 = "<p>Assista ao vídeo abaixo.</p><p>Confira as imagens.</p>"
        title2 = "Guia de pescaria"
        
        result2 = youtube_integration.integrate_video_into_content(
            content2, "pescaria", title2, None
        )
        
        if result2 != content2:
            self.stdout.write("✅ Vídeo incluído (correto - conteúdo menciona vídeo)")
        else:
            self.stdout.write("❌ Vídeo não incluído (incorreto)")
        
        # Teste 3: Nem título nem conteúdo mencionam vídeo
        self.stdout.write("\n🎯 Teste 3: Nem título nem conteúdo mencionam vídeo")
        content3 = "<p>Artigo sobre economia brasileira.</p><p>Análise do mercado.</p>"
        title3 = "Economia brasileira em análise"
        
        result3 = youtube_integration.integrate_video_into_content(
            content3, "economia", title3, None
        )
        
        if result3 == content3:
            self.stdout.write("✅ Vídeo não incluído (correto - nada menciona vídeo)")
        else:
            self.stdout.write("❌ Vídeo incluído (incorreto)")
        
        # Teste 4: Notícia original tem vídeo
        self.stdout.write("\n🎯 Teste 4: Notícia original tem vídeo")
        content4 = "<p>Artigo sobre pescaria.</p><p>Continue lendo...</p>"
        title4 = "Guia de pescaria"
        news_with_video = {
            'title': 'VÍDEO: Homem é mordido por traíra',
            'description': 'Confira: https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'url': 'https://exemplo.com/noticia-com-video'
        }
        
        result4 = youtube_integration.integrate_video_into_content(
            content4, "pescaria", title4, news_with_video
        )
        
        if result4 != content4:
            self.stdout.write("✅ Vídeo incluído (correto - notícia original tem vídeo)")
        else:
            self.stdout.write("❌ Vídeo não incluído (incorreto)")
        
        self.stdout.write("\n=== RESUMO DA LÓGICA ===")
        self.stdout.write("✅ Notícia original tem vídeo → SEMPRE incluir")
        self.stdout.write("✅ Título menciona vídeo → SEMPRE incluir")
        self.stdout.write("✅ Conteúdo menciona vídeo → SEMPRE incluir")
        self.stdout.write("❌ Nada menciona vídeo → NÃO incluir")
        self.stdout.write("\n=== FIM DOS TESTES ===")

