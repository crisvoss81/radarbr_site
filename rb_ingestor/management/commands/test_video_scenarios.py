# rb_ingestor/management/commands/test_video_scenarios.py
"""
Comando para testar diferentes cenários de integração de vídeos
"""
from django.core.management.base import BaseCommand
from rb_ingestor.youtube_integration import YouTubeIntegration

class Command(BaseCommand):
    help = "Testa diferentes cenários de integração de vídeos"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DE CENÁRIOS DE VÍDEO ===")
        
        youtube_integration = YouTubeIntegration()
        
        # Cenário 1: Notícia com vídeo (SEMPRE incluir)
        self.stdout.write("\n🎯 Cenário 1: Notícia com vídeo")
        news_with_video = {
            'title': 'VÍDEO: Homem é mordido por traíra durante pescaria',
            'description': 'Confira o vídeo completo: https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'url': 'https://exemplo.com/noticia-com-video'
        }
        
        content1 = "<p>Artigo sobre pescaria de traira.</p><p>Continue lendo...</p>"
        result1 = youtube_integration.integrate_video_into_content(
            content1, "pescaria de traira", "Guia de Pescaria", news_with_video
        )
        
        if result1 != content1:
            self.stdout.write("✅ Vídeo incluído (correto - notícia tem vídeo)")
        else:
            self.stdout.write("❌ Vídeo não incluído (incorreto)")
        
        # Cenário 2: Tema educativo (SEMPRE incluir)
        self.stdout.write("\n🎯 Cenário 2: Tema educativo")
        content2 = "<p>Como fazer pescaria de traira.</p><p>Passo a passo completo.</p>"
        result2 = youtube_integration.integrate_video_into_content(
            content2, "como fazer pescaria", "Tutorial de Pescaria", None
        )
        
        if result2 != content2:
            self.stdout.write("✅ Vídeo incluído (correto - tema educativo)")
        else:
            self.stdout.write("❌ Vídeo não incluído (incorreto)")
        
        # Cenário 3: Tema político (NÃO incluir)
        self.stdout.write("\n🎯 Cenário 3: Tema político")
        content3 = "<p>Análise da economia brasileira.</p><p>Inflação e mercado.</p>"
        result3 = youtube_integration.integrate_video_into_content(
            content3, "economia brasileira", "Análise Econômica", None
        )
        
        if result3 == content3:
            self.stdout.write("✅ Vídeo não incluído (correto - tema político)")
        else:
            self.stdout.write("❌ Vídeo incluído (incorreto)")
        
        # Cenário 4: Tema genérico (NÃO incluir)
        self.stdout.write("\n🎯 Cenário 4: Tema genérico")
        content4 = "<p>Notícias do Brasil.</p><p>Informações gerais.</p>"
        result4 = youtube_integration.integrate_video_into_content(
            content4, "notícias do brasil", "Notícias Gerais", None
        )
        
        if result4 == content4:
            self.stdout.write("✅ Vídeo não incluído (correto - tema genérico)")
        else:
            self.stdout.write("❌ Vídeo incluído (incorreto)")
        
        # Cenário 5: Conteúdo menciona vídeo (SEMPRE incluir)
        self.stdout.write("\n🎯 Cenário 5: Conteúdo menciona vídeo")
        content5 = "<p>Assista ao vídeo abaixo.</p><p>Confira as imagens.</p>"
        result5 = youtube_integration.integrate_video_into_content(
            content5, "tema qualquer", "Artigo com Vídeo", None
        )
        
        if result5 != content5:
            self.stdout.write("✅ Vídeo incluído (correto - conteúdo menciona vídeo)")
        else:
            self.stdout.write("❌ Vídeo não incluído (incorreto)")
        
        self.stdout.write("\n=== RESUMO DOS CENÁRIOS ===")
        self.stdout.write("✅ Notícia com vídeo → SEMPRE incluir")
        self.stdout.write("✅ Tema educativo → SEMPRE incluir")
        self.stdout.write("✅ Conteúdo menciona vídeo → SEMPRE incluir")
        self.stdout.write("❌ Tema político/econômico → NÃO incluir")
        self.stdout.write("❌ Tema genérico → NÃO incluir")
        self.stdout.write("\n=== FIM DOS TESTES ===")

