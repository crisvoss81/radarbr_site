# rb_ingestor/management/commands/test_youtube_integration.py
"""
Comando para testar a integração automática de vídeos do YouTube
"""
from django.core.management.base import BaseCommand
from rb_ingestor.youtube_integration import YouTubeIntegration

class Command(BaseCommand):
    help = "Testa a integração automática de vídeos do YouTube"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DE INTEGRAÇÃO DO YOUTUBE ===")
        
        youtube_integration = YouTubeIntegration()
        
        # Teste 1: Detectar vídeo no texto
        self.stdout.write("\n🔍 Teste 1: Detecção de vídeo no texto")
        test_text_with_video = """
        Confira o vídeo completo no YouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        Este é um exemplo de conteúdo que menciona vídeos.
        """
        
        video_id = youtube_integration.extract_video_id(test_text_with_video)
        if video_id:
            self.stdout.write(f"✅ Vídeo detectado: {video_id}")
        else:
            self.stdout.write("❌ Nenhum vídeo detectado")
        
        # Teste 2: Verificar menção de vídeo
        self.stdout.write("\n🔍 Teste 2: Verificação de menção de vídeo")
        test_text_with_mention = "Assista ao vídeo completo para entender melhor o assunto."
        
        has_video = youtube_integration.has_video_mention(test_text_with_mention)
        if has_video:
            self.stdout.write("✅ Menção de vídeo detectada")
        else:
            self.stdout.write("❌ Nenhuma menção de vídeo")
        
        # Teste 3: Integração em conteúdo
        self.stdout.write("\n🔍 Teste 3: Integração em conteúdo")
        test_content = """
        <p>Este é um artigo sobre pescaria de traira. A pescaria é uma atividade muito popular no Brasil.</p>
        <p>Confira o vídeo abaixo para aprender mais sobre técnicas de pesca.</p>
        <p>Continue lendo para mais informações sobre o assunto.</p>
        """
        
        # Simular notícia com vídeo
        test_news_article = {
            'title': 'VÍDEO: Homem é mordido por traíra durante pescaria',
            'description': 'Confira o vídeo completo: https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'url': 'https://exemplo.com/noticia-com-video'
        }
        
        integrated_content = youtube_integration.integrate_video_into_content(
            test_content, "pescaria de traira", "Guia de Pescaria", test_news_article
        )
        
        if integrated_content != test_content:
            self.stdout.write("✅ Vídeo integrado no conteúdo")
            self.stdout.write("📄 Conteúdo com vídeo:")
            self.stdout.write(integrated_content[:200] + "...")
        else:
            self.stdout.write("❌ Nenhum vídeo foi integrado")
        
        # Teste 4: Geração de embed code
        self.stdout.write("\n🔍 Teste 4: Geração de código de embed")
        embed_code = youtube_integration.generate_embed_code("dQw4w9WgXcQ", "Vídeo de Teste")
        self.stdout.write("✅ Código de embed gerado:")
        self.stdout.write(embed_code[:100] + "...")
        
        self.stdout.write("\n=== FIM DOS TESTES ===")
