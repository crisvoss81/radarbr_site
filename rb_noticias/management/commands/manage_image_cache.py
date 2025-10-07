# rb_noticias/management/commands/manage_image_cache.py
"""
Comando Django para gerenciar o cache de imagens.
Permite visualizar estatísticas, limpar cache e validar URLs.
"""

from django.core.management.base import BaseCommand
from rb_ingestor.image_cache import image_cache
from rb_ingestor.image_search import ImageSearchEngine
import json

class Command(BaseCommand):
    help = 'Gerencia o cache de imagens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Mostrar estatísticas do cache'
        )
        parser.add_argument(
            '--clear-expired',
            action='store_true',
            help='Remover entradas expiradas do cache'
        )
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Limpar todo o cache'
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validar URLs das imagens em cache'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='Listar entradas do cache'
        )

    def handle(self, *args, **options):
        if options['stats']:
            self.show_stats()
        
        if options['clear_expired']:
            self.clear_expired()
        
        if options['clear_all']:
            self.clear_all()
        
        if options['validate']:
            self.validate_urls()
        
        if options['list']:
            self.list_entries()
        
        if not any(options.values()):
            self.stdout.write(
                self.style.WARNING('Use --help para ver as opções disponíveis')
            )

    def show_stats(self):
        """Mostra estatísticas do cache."""
        stats = image_cache.get_stats()
        
        self.stdout.write(self.style.SUCCESS('Estatísticas do Cache de Imagens:'))
        self.stdout.write('='*40)
        self.stdout.write(f'Total de entradas: {stats["total_entries"]}')
        self.stdout.write(f'Entradas ativas: {stats["active_entries"]}')
        self.stdout.write(f'Entradas expiradas: {stats["expired_entries"]}')
        self.stdout.write(f'Idade máxima: {stats["max_age_days"]} dias')
        self.stdout.write(f'Arquivo do cache: {stats["cache_file"]}')
        
        if stats["total_entries"] > 0:
            percentage = (stats["active_entries"] / stats["total_entries"]) * 100
            self.stdout.write(f'Taxa de cache ativo: {percentage:.1f}%')

    def clear_expired(self):
        """Remove entradas expiradas."""
        before_count = image_cache.get_stats()["total_entries"]
        image_cache.clear_expired()
        after_count = image_cache.get_stats()["total_entries"]
        
        removed = before_count - after_count
        self.stdout.write(
            self.style.SUCCESS(f'Removidas {removed} entradas expiradas')
        )

    def clear_all(self):
        """Limpa todo o cache."""
        before_count = image_cache.get_stats()["total_entries"]
        image_cache.cache_data.clear()
        image_cache._save_cache()
        
        self.stdout.write(
            self.style.SUCCESS(f'Cache limpo: {before_count} entradas removidas')
        )

    def validate_urls(self):
        """Valida URLs das imagens em cache."""
        search_engine = ImageSearchEngine()
        total = len(image_cache.cache_data)
        valid_count = 0
        invalid_count = 0
        
        self.stdout.write(f'Validando {total} URLs...')
        
        for key, entry in image_cache.cache_data.items():
            url = entry['url']
            title = entry.get('title', 'N/A')[:50]
            
            if search_engine.validate_image_url(url):
                valid_count += 1
                self.stdout.write(f'✓ {title}...')
            else:
                invalid_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ {title}... (URL inválida)')
                )
                # Remover URL inválida
                del image_cache.cache_data[key]
        
        # Salvar cache atualizado
        image_cache._save_cache()
        
        self.stdout.write('\n' + '='*40)
        self.stdout.write(f'URLs válidas: {valid_count}')
        self.stdout.write(f'URLs inválidas: {invalid_count}')
        self.stdout.write(f'Total: {total}')

    def list_entries(self):
        """Lista entradas do cache."""
        if not image_cache.cache_data:
            self.stdout.write(self.style.WARNING('Cache vazio'))
            return
        
        self.stdout.write(self.style.SUCCESS('Entradas do Cache:'))
        self.stdout.write('='*60)
        
        for i, (key, entry) in enumerate(image_cache.cache_data.items(), 1):
            title = entry.get('title', 'N/A')[:40]
            category = entry.get('category', 'N/A')
            url = entry['url'][:50] + '...' if len(entry['url']) > 50 else entry['url']
            
            self.stdout.write(f'{i:3d}. {title}')
            self.stdout.write(f'     Categoria: {category}')
            self.stdout.write(f'     URL: {url}')
            self.stdout.write()
