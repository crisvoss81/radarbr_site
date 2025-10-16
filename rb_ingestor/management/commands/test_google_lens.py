# rb_ingestor/management/commands/test_google_lens.py
"""
Comando para testar análise com Google Lens e busca de imagens similares
"""
from django.core.management.base import BaseCommand
from rb_ingestor.google_lens_analyzer import google_lens_analyzer

class Command(BaseCommand):
    help = "Testa análise com Google Lens e busca de imagens similares"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="URL da notícia para analisar")
        parser.add_argument("--max-results", type=int, default=6, help="Número máximo de imagens similares")

    def handle(self, *args, **options):
        url = options['url']
        max_results = options['max_results']
        
        self.stdout.write("=== TESTE GOOGLE LENS + BUSCA SIMILAR ===")
        self.stdout.write(f"URL: {url}")
        self.stdout.write(f"Max resultados: {max_results}")
        self.stdout.write("")
        
        # Primeiro extrair a imagem da notícia
        from rb_ingestor.image_analyzer import image_analyzer
        image_url = image_analyzer.extract_main_image_from_url(url)
        
        if not image_url:
            self.stdout.write("❌ Nenhuma imagem encontrada na notícia")
            return
        
        self.stdout.write(f"📸 Imagem encontrada: {image_url}")
        self.stdout.write("")
        
        # Analisar com Google Lens e buscar similares
        result = google_lens_analyzer.find_similar_images(image_url, max_results)
        
        if not result['success']:
            self.stdout.write(f"❌ {result['error']}")
            return
        
        # Mostrar resultados
        self.stdout.write("✅ GOOGLE LENS + BUSCA VISUAL CONCLUÍDA!")
        self.stdout.write("")
        
        self.stdout.write("🤖 ANÁLISE VISUAL DO GOOGLE LENS:")
        analysis = result['google_lens_analysis']
        self.stdout.write(f"   Objetos detectados: {', '.join(analysis['objects_detected'])}")
        self.stdout.write(f"   Características visuais: {', '.join(analysis['visual_features'])}")
        self.stdout.write(f"   Cores: {', '.join(analysis['colors'])}")
        self.stdout.write(f"   Tipo: {analysis['image_type']}")
        self.stdout.write(f"   Confiança: {analysis['confidence']:.2f}")
        self.stdout.write("")
        
        self.stdout.write("🔍 TERMOS DE BUSCA VISUAL:")
        search_terms = result['objects_detected'] + result['visual_features']
        for i, term in enumerate(search_terms[:8], 1):  # Mostrar apenas os 8 primeiros
            self.stdout.write(f"   {i}. {term}")
        self.stdout.write("")
        
        self.stdout.write(f"🖼️ IMAGENS SIMILARES ENCONTRADAS ({len(result['similar_images'])}):")
        self.stdout.write("")
        
        for i, img in enumerate(result['similar_images'], 1):
            self.stdout.write(f"   {i}. [{img['source'].upper()}] Similaridade: {img['similarity_score']:.2f}")
            self.stdout.write(f"      URL: {img['url']}")
            self.stdout.write(f"      Alt: {img['alt'][:50]}...")
            self.stdout.write(f"      Crédito: {img['credit']}")
            self.stdout.write("")
        
        self.stdout.write("🎯 PRÓXIMO PASSO:")
        self.stdout.write("   Integrar essa busca no fluxo de publicação de artigos")
