# rb_ingestor/management/commands/test_fixed_automation.py
"""
Comando para testar a automação corrigida
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.apps import apps

class Command(BaseCommand):
    help = "Testa a automação corrigida que busca notícias específicas"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=1, help="Número de artigos a criar")
        parser.add_argument("--dry-run", action="store_true", help="Apenas simula")

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE AUTOMACAO CORRIGIDA ===")
        self.stdout.write(f"Executado em: {timezone.now()}")
        
        # Importar o comando corrigido
        from rb_ingestor.management.commands.automacao_render_fixed import Command as FixedCommand
        
        # Criar instância e executar
        fixed_cmd = FixedCommand()
        
        if options["dry_run"]:
            self.stdout.write("🔍 MODO DRY-RUN - Testando busca de notícias")
            
            # Testar apenas a busca de notícias
            news_articles = fixed_cmd._get_specific_news()
            
            if news_articles:
                self.stdout.write(f"✅ Encontradas {len(news_articles)} notícias específicas:")
                for i, article in enumerate(news_articles[:3]):
                    self.stdout.write(f"  {i+1}. {article.get('title', '')}")
                    self.stdout.write(f"     Fonte: {article.get('source', '')}")
                    self.stdout.write(f"     Tópico: {article.get('topic', '')}")
                    self.stdout.write("")
            else:
                self.stdout.write("❌ Nenhuma notícia específica encontrada")
        else:
            # Executar automação completa
            fixed_cmd.handle(limit=options["limit"], force=True, debug=True)
