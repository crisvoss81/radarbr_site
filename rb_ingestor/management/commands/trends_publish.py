# rb_ingestor/management/commands/trends_publish.py
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from django.utils.html import strip_tags
from django.db import models
from slugify import slugify

from rb_ingestor.trends import fetch_trending_terms
from rb_ingestor.ai import generate_article
from rb_ingestor.images_free import pick_image
from rb_ingestor.categorize import route_category_for_topic


# ---------------------------------------------
# Funções auxiliares (sem alterações aqui)
# ---------------------------------------------
_NO_STATUS_SENTINEL = object()

def _flatten_choices(choices):
    flat = []
    for c in choices or []:
        if isinstance(c, (list, tuple)) and len(c) == 2 and isinstance(c[1], (list, tuple)):
            flat.extend(c[1])
        else:
            flat.append(c)
    return flat

def _pick_published_from_choices(choices):
    keys = {"published", "publicado", "publicada", "ativo", "aprovado", "online"}
    for value, label in choices:
        v = str(value).lower()
        l = str(label).lower()
        if v in keys or l in keys:
            return value
    return choices[0][0]

def _status_published(Noticia):
    try:
        f = Noticia._meta.get_field("status")
    except Exception:
        return _NO_STATUS_SENTINEL
    default = getattr(f, "default", models.fields.NOT_PROVIDED)
    if default is not models.fields.NOT_PROVIDED and default is not None and default != "":
        return default
    flat = _flatten_choices(getattr(f, "choices", None))
    if flat:
        return _pick_published_from_choices(flat)
    if isinstance(f, (models.IntegerField, models.SmallIntegerField, models.PositiveIntegerField, models.PositiveSmallIntegerField, models.BigIntegerField)):
        return 1
    return "published"


class Command(BaseCommand):
    help = "Gera artigos a partir de tópicos do Google Trends (BR) + imagem livre."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5, help="Número de artigos a serem criados.")
        parser.add_argument("--geo", default="BR")
        parser.add_argument("--debug", action="store_true", help="Mostra mais informações sobre o processo.")
        parser.add_argument("--force", action="store_true", help="Força a publicação mesmo que um tópico similar já exista hoje.")

    def handle(self, *args, **opts):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")

        cat_fallback, _ = Categoria.objects.get_or_create(slug="geral", defaults={"nome": "Geral"})

        terms = fetch_trending_terms(geo=opts["geo"], limit=opts["limit"], debug=opts["debug"])

        if opts["debug"]:
            self.stdout.write(self.style.NOTICE(f"Termos úteis encontrados ({len(terms)}): {terms}"))

        if not terms:
            self.stdout.write(self.style.WARNING("Nenhum termo útil encontrado após a filtragem. Tente novamente mais tarde."))
            return

        created = 0
        day = timezone.localdate().isoformat()

        def unique_slug(base_title: str) -> str:
            base = (slugify(base_title) or "post")[:180]
            slug = base
            i = 2
            while Noticia.objects.filter(slug=slug).exists():
                slug = f"{base[:176]}-{i}"
                i += 1
            return slug

        published_value = _status_published(Noticia)
        if opts["debug"] and published_value is not _NO_STATUS_SENTINEL:
            self.stdout.write(self.style.NOTICE(f"[status] Valor a usar = {published_value!r}"))

        for topic in terms:
            topic_clean = topic.strip()
            key = f"trend:{topic_clean.lower()}:{day}"

            if not opts["force"] and Noticia.objects.filter(fonte_url=key).exists():
                if opts["debug"]:
                    self.stdout.write(f"– Já existe hoje: {topic_clean}")
                continue
            if opts["force"] and opts["debug"]:
                self.stdout.write(self.style.WARNING(f"· Forçando publicação: {topic_clean}"))

            try:
                cat_slug = route_category_for_topic(topic_clean)
                cat = Categoria.objects.filter(slug=cat_slug).first() or cat_fallback
                if opts["debug"]:
                    self.stdout.write(self.style.NOTICE(f"[categoria] '{topic_clean}' → {cat.slug}"))

                self.stdout.write(f"Gerando artigo para: {topic_clean}...")
                art = generate_article(topic_clean) or {}
                
                title = strip_tags((art.get("title") or topic_clean).strip())[:200]
                dek = strip_tags((art.get("dek") or art.get("description") or "").strip())[:220]
                body = (art.get("html") or "<p></p>").strip()
                conteudo = f'<p class="dek">{dek}</p>\n{body}' if dek else body

                # ---------- CRIA O OBJETO NOTICIA PRIMEIRO ----------
                kwargs = dict(
                    titulo=title,
                    conteudo=conteudo,
                    publicado_em=timezone.now(),
                    fonte_url=key,
                    categoria=cat,
                    fonte_nome="RadarBR Trends",
                    imagem_alt=title
                )
                if published_value is not _NO_STATUS_SENTINEL:
                    kwargs["status"] = published_value

                obj = Noticia(**kwargs)

                # ---------- IMAGEM (AGORA COM O OBJETO JÁ EXISTENTE) ----------
                self.stdout.write(f"Buscando imagem para: {topic_clean}...")
                img_info = pick_image(topic_clean)
                if img_info and img_info.get("url"):
                    # A MÁGICA ACONTECE AQUI:
                    # Apenas atribuímos a URL diretamente ao campo CloudinaryField.
                    obj.imagem = img_info["url"]
                    
                    obj.imagem_credito = img_info.get("credito", "")
                    obj.imagem_licenca = img_info.get("licenca", "")
                    obj.imagem_fonte_url = img_info.get("fonte_url", "")
                    self.stdout.write(self.style.SUCCESS(f"✓ Imagem encontrada para: {topic_clean}"))

                # ---------- SLUG E SAVE FINAL ----------
                obj.slug = unique_slug(title)
                obj.save()
                created += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Publicado: {topic_clean}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao processar o tópico '{topic_clean}': {e}"))
                continue # Pula para o próximo tópico em caso de erro

        self.stdout.write(self.style.SUCCESS(f"Pronto. Novos artigos criados: {created}"))

        if created > 0:
            try:
                from core.utils import absolute_sitemap_url
                from rb_ingestor.ping import ping_search_engines
                sm_url = absolute_sitemap_url()
                res = ping_search_engines(sm_url)
                self.stdout.write(self.style.NOTICE(f"Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; Bing={'OK' if res['bing'] else 'NOK'}"))
            except Exception:
                pass