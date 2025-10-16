# rb_ingestor/management/commands/test_image_analysis.py
"""
Comando para testar análise de imagem de notícias
"""
from django.core.management.base import BaseCommand
from rb_ingestor.image_analyzer import image_analyzer

class Command(BaseCommand):
    help = "Testa análise de imagem de notícias"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="URL da notícia para analisar")
        parser.add_argument("--show-keywords", action="store_true", help="Mostra palavras-chave geradas")

    def handle(self, *args, **options):
        url = options['url']
        show_keywords = options['show_keywords']
        
        self.stdout.write("=== TESTE DE ANÁLISE DE IMAGEM ===")
        self.stdout.write(f"URL: {url}")
        self.stdout.write("")
        
        # Analisar imagem da notícia
        result = image_analyzer.analyze_news_image(url)
        
        if not result:
            self.stdout.write("❌ Falha na análise de imagem")
            return
        
        # Mostrar resultados
        self.stdout.write("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        self.stdout.write("")
        
        self.stdout.write("📸 IMAGEM ORIGINAL:")
        self.stdout.write(f"   {result['original_image_url']}")
        self.stdout.write("")
        
        self.stdout.write("🤖 ANÁLISE DA IA:")
        self.stdout.write(f"   {result['analysis']}")
        self.stdout.write("")
        
        if show_keywords:
            self.stdout.write("🔍 PALAVRAS-CHAVE PARA BUSCA:")
            for i, keyword in enumerate(result['search_keywords'], 1):
                self.stdout.write(f"   {i}. {keyword}")
            self.stdout.write("")
        
        self.stdout.write("🎯 PRÓXIMO PASSO:")
        self.stdout.write("   Usar essas palavras-chave para buscar imagem similar no Unsplash/Pexels")
