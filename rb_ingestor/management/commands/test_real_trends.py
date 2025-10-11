# rb_ingestor/management/commands/test_real_trends.py
"""
Comando para testar o sistema de tendências reais
"""
from django.core.management.base import BaseCommand
from rb_ingestor.trending_analyzer_real import RealTrendingAnalyzer

class Command(BaseCommand):
    help = "Testa o sistema de tendências reais"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Força atualização (ignora cache)")
        parser.add_argument("--limit", type=int, default=10, help="Número de tópicos para mostrar")

    def handle(self, *args, **options):
        analyzer = RealTrendingAnalyzer()
        
        self.stdout.write("=== TESTE DE TENDÊNCIAS REAIS ===")
        
        if options["force"]:
            self.stdout.write("🔄 Forçando atualização...")
            topics = analyzer.force_update_trends()
        else:
            self.stdout.write("📊 Buscando tendências...")
            topics = analyzer.get_optimized_topics(options["limit"])
        
        if not topics:
            self.stdout.write(self.style.ERROR("❌ Nenhum tópico encontrado"))
            return
        
        self.stdout.write(f"\n✅ Encontrados {len(topics)} tópicos:")
        self.stdout.write("=" * 60)
        
        for i, topic in enumerate(topics, 1):
            self.stdout.write(f"\n{i}. {topic['topic']}")
            self.stdout.write(f"   📊 Volume: {topic['search_volume']}")
            self.stdout.write(f"   🏷️  Categoria: {topic['category']}")
            self.stdout.write(f"   🔗 Fonte: {topic['source']}")
            self.stdout.write(f"   ⭐ Score: {topic.get('relevance_score', 'N/A')}")
            self.stdout.write(f"   🕒 Timestamp: {topic['timestamp']}")
        
        # Estatísticas por fonte
        sources = {}
        categories = {}
        
        for topic in topics:
            source = topic['source']
            category = topic['category']
            
            sources[source] = sources.get(source, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📈 ESTATÍSTICAS POR FONTE:")
        for source, count in sources.items():
            self.stdout.write(f"   {source}: {count} tópicos")
        
        self.stdout.write("\n🏷️  ESTATÍSTICAS POR CATEGORIA:")
        for category, count in categories.items():
            self.stdout.write(f"   {category}: {count} tópicos")
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("✅ Teste concluído!")
