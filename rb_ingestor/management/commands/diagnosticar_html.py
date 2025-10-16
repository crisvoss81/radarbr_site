from django.core.management.base import BaseCommand
from django.apps import apps
import re


class Command(BaseCommand):
    help = "Diagnostica o HTML das últimas notícias publicadas"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5, help="Quantidade de notícias a analisar")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")

        qs = Noticia.objects.order_by("-criado_em")[: options["limit"]]

        self.stdout.write("=== DIAGNÓSTICO HTML NOTÍCIAS ===")

        for n in qs:
            c = n.conteudo or ""
            clean_snip = re.sub(r"[\t\n\r ]+", " ", c[:300])
            h2_count = c.lower().count("<h2")
            h3_count = c.lower().count("<h3")
            has_md_fence = "```" in c or "```html" in c.lower()
            has_ellipsis = c.strip().endswith("...")
            self.stdout.write("")
            self.stdout.write(f"Título: {n.titulo}")
            self.stdout.write(f"Chars: {len(c)} | H2: {h2_count} | H3: {h3_count}")
            self.stdout.write(f"Inicia: {clean_snip}")
            self.stdout.write(f"Markdown fence: {has_md_fence} | Termina com ...: {has_ellipsis}")
            self.stdout.write("-")

        self.stdout.write("\nObs: o banner do meio é inserido no template via filtro split_content_sections, não aparece salvo no campo conteudo.")


