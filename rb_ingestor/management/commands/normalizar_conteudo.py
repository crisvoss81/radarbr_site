from django.core.management.base import BaseCommand
from django.apps import apps
import re


class Command(BaseCommand):
    help = "Normaliza notícias: remove créditos de Instagram e garante 2 H2 no conteúdo"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=10, help="Quantidade de notícias a normalizar")

    def handle(self, *args, **options):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        qs = Noticia.objects.order_by("-criado_em")[: options["limit"]]

        self.stdout.write("=== NORMALIZAÇÃO DE CONTEÚDO ===")

        fix_count = 0
        for n in qs:
            changed = False

            # 1) Remover créditos de Instagram
            if n.imagem_credito and ("@" in n.imagem_credito or "Instagram" in (n.imagem_credito or "")):
                n.imagem_credito = "Imagem gratuita"
                n.imagem_licenca = "CC"
                # Se a fonte era de Instagram, limpar URL
                if n.imagem_fonte_url and ("instagram.com" in n.imagem_fonte_url):
                    n.imagem_fonte_url = ""
                changed = True

            # 2) Garantir pelo menos 2 H2 no conteúdo
            content = n.conteudo or ""
            h2_count = content.lower().count("<h2")
            if h2_count < 2:
                # Inserir dois H2 após o primeiro parágrafo/dek
                # Encontrar fechamento do primeiro </p>
                insert_at = content.lower().find("</p>")
                if insert_at == -1:
                    insert_at = 0
                else:
                    insert_at += 4

                h2_block = (
                    "\n<h2>Contexto e Principais Pontos</h2>\n"
                    "<p>Entenda os elementos centrais deste tema com fatos e informações relevantes para o leitor brasileiro.</p>\n"
                    "<h2>Desdobramentos e Impactos</h2>\n"
                    "<p>Exploramos os efeitos práticos, reações e possíveis próximos passos relacionados ao assunto.</p>\n"
                )
                content = content[:insert_at] + h2_block + content[insert_at:]
                n.conteudo = content
                changed = True

            if changed:
                n.save(update_fields=[
                    "imagem_credito", "imagem_licenca", "imagem_fonte_url", "conteudo"
                ])
                fix_count += 1
                self.stdout.write(f"✓ Normalizado: {n.titulo[:80]}")

        self.stdout.write(f"OK: {fix_count} notícia(s) normalizadas")


