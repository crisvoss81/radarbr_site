# rb_ingestor/management/commands/run_scheduler.py
"""
Comando para executar o scheduler de automação
Pode ser executado via cron a cada hora
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia
from rb_ingestor.automation import NewsAutomation

class Command(BaseCommand):
    help = "Executa o scheduler de automação de notícias"

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força execução mesmo com publicações recentes'
        )

    def handle(self, *args, **options):
        try:
            automation = NewsAutomation()
            
            # Verificar se já houve publicações recentes (a menos que force)
            if not options['force']:
                recent_count = automation.check_recent_publications(6)
                if recent_count >= 5:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Já existem {recent_count} notícias recentes. "
                            "Use --force para executar mesmo assim."
                        )
                    )
                    return
            
            # Executar automação
            self.stdout.write(self.style.NOTICE("Executando automação..."))
            automation.run_automation()
            
            # Estatísticas
            total_news = Noticia.objects.count()
            recent_news = Noticia.objects.filter(
                criado_em__gte=timezone.now() - timedelta(hours=24)
            ).count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Automação concluída! "
                    f"Total: {total_news} notícias, "
                    f"Últimas 24h: {recent_news}"
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro no scheduler: {str(e)}"))
            raise