# rb_ingestor/management/commands/manual_publish.py
"""
Comando para publicação manual de notícias no Render
Útil para testar e executar automação quando necessário
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia
from rb_ingestor.automation import NewsAutomation

class Command(BaseCommand):
    help = "Executa publicação manual de notícias"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='Número de notícias a criar (padrão: 3)'
        )
        parser.add_argument(
            '--strategy',
            choices=['trending', 'audience', 'mixed'],
            default='mixed',
            help='Estratégia a usar (padrão: mixed)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força execução mesmo com publicações recentes'
        )

    def handle(self, *args, **options):
        try:
            count = options['count']
            strategy = options['strategy']
            force = options['force']
            
            # Verificar publicações recentes
            if not force:
                recent_count = Noticia.objects.filter(
                    criado_em__gte=timezone.now() - timedelta(hours=6)
                ).count()
                
                if recent_count >= 5:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Já existem {recent_count} notícias recentes. "
                            "Use --force para executar mesmo assim."
                        )
                    )
                    return
            
            # Executar automação
            self.stdout.write(
                self.style.NOTICE(
                    f"Executando publicação manual: {count} notícias com estratégia '{strategy}'"
                )
            )
            
            automation = NewsAutomation()
            
            # Executar comando smart_trends_publish diretamente
            from django.core.management import call_command
            
            call_command(
                'smart_trends_publish',
                '--strategy', strategy,
                '--limit', str(count),
                '--force'
            )
            
            # Estatísticas
            total_news = Noticia.objects.count()
            recent_news = Noticia.objects.filter(
                criado_em__gte=timezone.now() - timedelta(hours=24)
            ).count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Publicação concluída! "
                    f"Total: {total_news} notícias, "
                    f"Últimas 24h: {recent_news}"
                )
            )
            
            # Mostrar últimas notícias criadas
            latest_news = Noticia.objects.order_by('-criado_em')[:count]
            self.stdout.write("\n=== ÚLTIMAS NOTÍCIAS CRIADAS ===")
            for news in latest_news:
                self.stdout.write(f"• {news.titulo} ({news.criado_em.strftime('%H:%M')})")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro na publicação: {str(e)}"))
            raise
