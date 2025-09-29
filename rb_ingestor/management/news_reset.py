from __future__ import annotations
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from django.db import transaction

class Command(BaseCommand):
    help = "Apaga notícias (trends ou todas) e, opcionalmente, publica novas via trends_publish."

    def add_arguments(self, parser):
        parser.add_argument(
            "--scope",
            choices=["trends", "all"],
            default="trends",
            help="O que apagar: 'trends' (padrão) só as geradas por Trends; 'all' apaga tudo.",
        )
        parser.add_argument(
            "--with-media",
            action="store_true",
            help="Também apaga arquivos de imagem do disco (campo 'imagem').",
        )
        parser.add_argument(
            "--no-publish",
            action="store_true",
            help="Não publica novamente (só limpar).",
        )
        parser.add_argument("--limit", type=int, default=8, help="Quantas novas publicar (se for publicar).")
        parser.add_argument("--geo", default="BR", help="País do Google Trends (ex.: BR).")
        parser.add_argument("--debug", action="store_true", help="Mais logs.")
        parser.add_argument("--force", action="store_true", help="Força publicação mesmo se já existir hoje.")

    def handle(self, *args, **opts):
        Noticia = apps.get_model("rb_noticias", "Noticia")

        if opts["scope"] == "trends":
            qs = Noticia.objects.filter(fonte_url__startswith="trend:")
        else:
            qs = Noticia.objects.all()

        total = qs.count()
        self.stdout.write(self.style.WARNING(f"Apagando {total} notícia(s) (scope={opts['scope']})..."))

        # verificar se existe campo imagem
        has_image_field = any(f.name == "imagem" for f in Noticia._meta.fields)

        with transaction.atomic():
            if opts["with-media"] and has_image_field:
                # apaga arquivos físicos antes do delete()
                for n in qs.only("id", "imagem").iterator():
                    try:
                        if getattr(n, "imagem", None):
                            n.imagem.delete(save=False)
                    except Exception:
                        pass
            qs.delete()

        self.stdout.write(self.style.SUCCESS("Limpeza concluída."))

        if opts["no-publish"]:
            return

        self.stdout.write(self.style.NOTICE("Publicando novas via trends_publish..."))
        call_command(
            "trends_publish",
            limit=opts["limit"],
            geo=opts["geo"],
            debug=opts["debug"],
            force=opts["force"],
        )
        self.stdout.write(self.style.SUCCESS("Pronto."))
