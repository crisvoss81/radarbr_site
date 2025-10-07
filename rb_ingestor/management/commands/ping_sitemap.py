# rb_ingestor/management/commands/ping_sitemap.py
"""
Comando para fazer ping do sitemap nos motores de busca
"""
from django.core.management.base import BaseCommand
from core.utils import absolute_sitemap_url
from rb_ingestor.ping import ping_search_engines

class Command(BaseCommand):
    help = "Faz ping do sitemap nos motores de busca"

    def handle(self, *args, **options):
        try:
            sm_url = absolute_sitemap_url()
            res = ping_search_engines(sm_url)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; "
                    f"Bing={'OK' if res['bing'] else 'NOK'}"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Erro ao fazer ping do sitemap: {str(e)}")
            )
