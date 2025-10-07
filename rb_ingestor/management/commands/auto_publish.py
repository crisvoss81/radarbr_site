# rb_ingestor/management/commands/auto_publish.py
"""
Comando Django para automação de publicação de notícias
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from rb_ingestor.automation import NewsAutomation

class Command(BaseCommand):
    help = "Executa automação inteligente de publicação de notícias"

    def add_arguments(self, parser):
        parser.add_argument(
            '--quick', 
            action='store_true', 
            help='Execução rápida para testes'
        )
        parser.add_argument(
            '--strategy',
            choices=['trending', 'audience', 'mixed'],
            default='mixed',
            help='Estratégia específica para usar'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=3,
            help='Número de artigos a criar'
        )

    def handle(self, *args, **options):
        try:
            automation = NewsAutomation()
            
            if options['quick']:
                self.stdout.write(self.style.NOTICE("Executando automação rápida..."))
                automation.run_quick_update()
            else:
                self.stdout.write(self.style.NOTICE("Executando automação completa..."))
                automation.run_automation()
            
            self.stdout.write(self.style.SUCCESS("Automação concluída!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro na automação: {str(e)}"))
            raise
