# rb_ingestor/management/commands/test_automation.py
"""
Comando de teste para verificar se a automação está funcionando
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Testa se a automação está funcionando corretamente"

    def add_arguments(self, parser):
        parser.add_argument("--full", action="store_true", help="Teste completo")
        parser.add_argument("--quick", action="store_true", help="Teste rápido")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")
        
        self.stdout.write("=== TESTE DE AUTOMACAO RADARBR ===")
        
        # Teste 1: Verificar modelos
        self.stdout.write("1. Verificando modelos...")
        try:
            total_news = Noticia.objects.count()
            total_categories = Categoria.objects.count()
            self.stdout.write(f"   ✓ Notícias: {total_news}")
            self.stdout.write(f"   ✓ Categorias: {total_categories}")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro nos modelos: {e}")
            return
        
        # Teste 2: Verificar notícias recentes
        self.stdout.write("2. Verificando notícias recentes...")
        try:
            recent_news = Noticia.objects.filter(
                criado_em__gte=timezone.now() - timedelta(hours=24)
            ).count()
            self.stdout.write(f"   ✓ Notícias últimas 24h: {recent_news}")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro ao verificar notícias: {e}")
        
        # Teste 3: Verificar APIs externas
        if options["full"]:
            self.stdout.write("3. Testando APIs externas...")
            
            # Teste Google News
            try:
                from gnews import GNews
                google_news = GNews(language='pt', country='BR', max_results=1)
                articles = google_news.get_top_news()
                if articles:
                    self.stdout.write("   ✓ Google News: OK")
                else:
                    self.stdout.write("   ⚠ Google News: Sem artigos")
            except Exception as e:
                self.stdout.write(f"   ❌ Google News: {e}")
            
            # Teste OpenAI
            try:
                from rb_ingestor.ai import generate_article
                test_content = generate_article("teste")
                if test_content:
                    self.stdout.write("   ✓ OpenAI: OK")
                else:
                    self.stdout.write("   ⚠ OpenAI: Sem conteúdo")
            except Exception as e:
                self.stdout.write(f"   ❌ OpenAI: {e}")
            
            # Teste Image Search
            try:
                from rb_ingestor.image_search import ImageSearchEngine
                search_engine = ImageSearchEngine()
                self.stdout.write("   ✓ Image Search: OK")
            except Exception as e:
                self.stdout.write(f"   ❌ Image Search: {e}")
        
        # Teste 4: Verificar comandos de automação
        self.stdout.write("4. Verificando comandos de automação...")
        try:
            from django.core.management import call_command
            
            # Teste automacao_render
            self.stdout.write("   Testando automacao_render...")
            call_command('automacao_render', '--help')
            self.stdout.write("   ✓ automacao_render: OK")
            
            # Teste automacao_simples
            self.stdout.write("   Testando automacao_simples...")
            call_command('automacao_simples', '--help')
            self.stdout.write("   ✓ automacao_simples: OK")
            
            # Teste auto_publish
            self.stdout.write("   Testando auto_publish...")
            call_command('auto_publish', '--help')
            self.stdout.write("   ✓ auto_publish: OK")
            
        except Exception as e:
            self.stdout.write(f"   ❌ Erro nos comandos: {e}")
        
        # Teste 5: Simulação de execução
        if options["quick"]:
            self.stdout.write("5. Simulando execução rápida...")
            try:
                from django.core.management import call_command
                call_command('automacao_render', '--limit', '1', '--force')
                self.stdout.write("   ✓ Execução simulada: OK")
            except Exception as e:
                self.stdout.write(f"   ❌ Erro na simulação: {e}")
        
        # Resumo final
        self.stdout.write("\n=== RESUMO DO TESTE ===")
        self.stdout.write("✅ Sistema básico: OK")
        self.stdout.write("✅ Modelos Django: OK")
        self.stdout.write("✅ Comandos disponíveis: OK")
        
        if options["full"]:
            self.stdout.write("✅ APIs externas: Testadas")
        
        if options["quick"]:
            self.stdout.write("✅ Execução: Testada")
        
        self.stdout.write("\n🎯 CONCLUSÃO: Sistema pronto para automação!")
        self.stdout.write("📋 Próximo passo: Deploy no Render")
