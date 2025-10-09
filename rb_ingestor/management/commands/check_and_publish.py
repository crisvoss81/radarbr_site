# rb_ingestor/management/commands/check_and_publish.py
"""
Comando simples para verificar e publicar notícias se necessário
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from rb_noticias.models import Noticia

class Command(BaseCommand):
    help = "Verifica notícias recentes e publica se necessário"

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-count',
            type=int,
            default=3,
            help='Número mínimo de notícias recentes (padrão: 3)'
        )
        parser.add_argument(
            '--publish-count',
            type=int,
            default=3,
            help='Número de notícias a publicar se necessário (padrão: 3)'
        )

    def handle(self, *args, **options):
        min_count = options['min_count']
        publish_count = options['publish_count']
        
        # Verificar notícias recentes
        total = Noticia.objects.count()
        recentes = Noticia.objects.filter(
            criado_em__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        self.stdout.write(f'Total notícias: {total}')
        self.stdout.write(f'Últimas 24h: {recentes}')
        
        # Se há poucas notícias recentes, executar automação
        if recentes < min_count:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️ Poucas notícias recentes ({recentes} < {min_count}) - executando automação...'
                )
            )
            
            try:
                # Executar publicação manual
                from django.core.management import call_command
                call_command('manual_publish', '--count', str(publish_count), '--strategy', 'mixed')
                
                self.stdout.write(self.style.SUCCESS('✅ Automação executada com sucesso!'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro na automação: {str(e)}'))
                raise
                
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Quantidade adequada de notícias recentes ({recentes} >= {min_count}).'
                )
            )
        
        # Mostrar últimas notícias
        self.stdout.write('\n=== ÚLTIMAS 5 NOTÍCIAS ===')
        for n in Noticia.objects.order_by('-criado_em')[:5]:
            self.stdout.write(f'- {n.titulo} ({n.criado_em.strftime("%Y-%m-%d %H:%M")})')
        
        self.stdout.write('\n=== VERIFICAÇÃO CONCLUÍDA ===')
