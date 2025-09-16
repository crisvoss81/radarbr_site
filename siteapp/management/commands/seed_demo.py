from django.core.management.base import BaseCommand
from siteapp.models import Category, Post

class Command(BaseCommand):
    help = "Cria categorias e posts de exemplo"

    def handle(self, *args, **kwargs):
        cat, _ = Category.objects.get_or_create(name="Geral")
        for i in range(1,6):
            Post.objects.get_or_create(
                title=f"Notícia de exemplo {i}",
                defaults=dict(
                    category=cat,
                    excerpt="Resumo de exemplo para a notícia.",
                    content=("Conteúdo completo da notícia de exemplo. " * 60),  # >280 palavras
                    is_published=True,
                ),
            )
        self.stdout.write(self.style.SUCCESS("Seed concluído."))
