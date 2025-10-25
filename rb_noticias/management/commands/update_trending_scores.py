# rb_noticias/management/commands/update_trending_scores.py
from django.core.management.base import BaseCommand
from rb_noticias.models import Noticia

class Command(BaseCommand):
    help = 'Atualiza os scores de trending de todas as notícias'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria atualizado sem fazer alterações',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        noticias = Noticia.objects.filter(status=Noticia.Status.PUBLICADO)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Modo dry-run: Nenhuma alteração será feita')
            )
        
        updated_count = 0
        
        for noticia in noticias:
            old_score = noticia.trending_score
            new_score = noticia.calculate_trending_score()
            
            if old_score != new_score:
                updated_count += 1
                self.stdout.write(
                    f'Notícia "{noticia.titulo[:50]}...": '
                    f'{old_score:.2f} → {new_score:.2f}'
                )
                
                if not dry_run:
                    noticia.save(update_fields=['trending_score'])
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Dry-run concluído: {updated_count} notícias seriam atualizadas')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Atualização concluída: {updated_count} notícias atualizadas')
            )
