# rb_ingestor/management/commands/test_fallback_extraction.py
"""
Comando para testar o sistema de fallback na extração de conteúdo
"""
from django.core.management.base import BaseCommand
from rb_ingestor.news_content_extractor import NewsContentExtractor

class Command(BaseCommand):
    help = "Testa o sistema de fallback na extração de conteúdo"

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="Tópico para testar")
        parser.add_argument("--max-items", type=int, default=6, help="Máximo de itens RSS para testar")

    def handle(self, *args, **options):
        topic = options["topic"]
        max_items = options["max_items"]
        
        self.stdout.write(f"=== TESTE DE FALLBACK NA EXTRAÇÃO ===")
        self.stdout.write(f"Tópico: {topic}")
        self.stdout.write(f"Máximo de itens: {max_items}")
        self.stdout.write("")
        
        extractor = NewsContentExtractor()
        
        # Testar extração com fallback
        self.stdout.write("🔍 Iniciando extração com sistema de fallback...")
        result = extractor.extract_best_for_topic(topic, max_items=max_items)
        
        if result:
            self.stdout.write("")
            self.stdout.write("✅ EXTRAÇÃO BEM-SUCEDIDA!")
            self.stdout.write(f"📰 Título: {result.get('title', 'N/A')}")
            self.stdout.write(f"🌐 URL: {result.get('url', 'N/A')}")
            self.stdout.write(f"📝 Conteúdo: {len(result.get('content', ''))} caracteres")
            self.stdout.write(f"🏢 Site: {result.get('source_domain', 'N/A')}")
            self.stdout.write(f"📂 Categoria: {result.get('category', 'N/A')}")
        else:
            self.stdout.write("")
            self.stdout.write("❌ FALHA NA EXTRAÇÃO")
            self.stdout.write("Todos os links falharam na extração de conteúdo")
        
        self.stdout.write("")
        self.stdout.write("=== TESTE CONCLUÍDO ===")
