# rb_ingestor/management/commands/trends_publish.py
import re
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

# ---------------------------
# Filtros de termos genéricos
# ---------------------------
NOISY_PATTERNS = [
    r"^\s*hoje\b",
    r"^\s*amanh(?:ã|a)\b",
    r"^\s*ontem\b",
    r"^\s*que\s+dia",
    r"^\s*que\s+horas",
    r"^\s*(vai\s+chover|chuva|previs[aã]o)\b",
    r"^\s*(tem\s+jogo|jogo\s+do|resultado\s+do\s+jogo)\b",
]
def _is_noisy(term: str) -> bool:
    t = (term or "").strip()
    if len(t) <= 3:
        return True
    for pat in NOISY_PATTERNS:
        if re.search(pat, t, flags=re.I):
            return True
    return False


# ---------------------------------------------
# Descobrir um valor válido para Noticia.status
# ---------------------------------------------
_NO_STATUS_SENTINEL = object()

def _flatten_choices(choices):
    """Suporta choices agrupados: [('Grupo', [(v,l), ...]), (v,l), ...] -> [(v,l), ...]"""
    flat = []
    for c in choices or []:
        if (
            isinstance(c, (list, tuple))
            and len(c) == 2
            and isinstance(c[1], (list, tuple))
        ):
            flat.extend(c[1])
        else:
            flat.append(c)
    return flat

def _pick_published_from_choices(choices):
    """Procura por 'published/publicado/ativo/aprovado/online'; senão, retorna o primeiro."""
    keys = {"published", "publicado", "publicada", "ativo", "aprovado", "online"}
    for value, label in choices:
        v = str(value).lower()
        l = str(label).lower()
        if v in keys or l in keys:
            return value
    return choices[0][0]

def _status_published(Noticia):
    """
    Retorna um valor aceitável para o campo NOT NULL 'status' do modelo Noticia.
    - Se o modelo não tiver 'status': retorna _NO_STATUS_SENTINEL.
    - Se tiver default: usa o default.
    - Se tiver choices: tenta 'publicado/ativo/...'; senão primeiro choice.
    - Sem choices: por tipo (bool=True, int=1, senão 'published').
    """
    try:
        f = Noticia._meta.get_field("status")
    except Exception:
        return _NO_STATUS_SENTINEL  # modelo sem 'status'

    default = getattr(f, "default", models.fields.NOT_PROVIDED)
    if default is not models.fields.NOT_PROVIDED and default is not None and default != "":
        return default

    flat = _flatten_choices(getattr(f, "choices", None))
    if flat:
        return _pick_published_from_choices(flat)

    if isinstance(f, models.BooleanField):
        return True
    if isinstance(
        f,
        (
            models.IntegerField,
            models.SmallIntegerField,
            models.PositiveIntegerField,
            models.PositiveSmallIntegerField,
            models.BigIntegerField,
        ),
    ):
        return 1
    return "published"


class Command(BaseCommand):
    help = "Gera artigos a partir de tópicos do Google Trends (BR) + imagem livre."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5)
        parser.add_argument("--geo", default="BR")
        parser.add_argument("--debug", action="store_true")
        parser.add_argument(
            "--force",
            action="store_true",
            help="força publicação mesmo se já existir hoje",
        )

    def handle(self, *args, **opts):
        Noticia = apps.get_model("rb_noticias", "Noticia")
        Categoria = apps.get_model("rb_noticias", "Categoria")

        # categoria padrão (fallback)
        cat_fallback, _ = Categoria.objects.get_or_create(
            slug="geral", defaults={"nome": "Geral"}
        )

        # Busca MAIS termos e filtra genéricos; preserva ordem e unicidade
        raw = fetch_trending_terms(geo=opts["geo"], limit=opts["limit"] * 4)
        uniq_lower, filtered = set(), []
        for t in raw:
            t = (t or "").strip()
            if not t:
                continue
            if _is_noisy(t):
                if opts["debug"]:
                    self.stdout.write(f"· filtrado (genérico): {t}")
                continue
            tl = t.lower()
            if tl not in uniq_lower:
                uniq_lower.add(tl)
                filtered.append(t)
        terms = filtered[: opts["limit"]]

        if opts["debug"]:
            self.stdout.write(self.style.NOTICE(f"Termos ({len(terms)}): {terms}"))
        if not terms:
            self.stdout.write(
                self.style.WARNING(
                    "Nenhum termo útil após filtro. Aumente --limit ou use --force."
                )
            )
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

        # valor para status (se houver campo); nunca None
        published_value = _status_published(Noticia)
        if opts["debug"] and published_value is not _NO_STATUS_SENTINEL:
            self.stdout.write(self.style.NOTICE(f"[status] valor a usar = {published_value!r}"))

        for topic in terms:
            topic_clean = topic.strip()
            key = f"trend:{topic_clean.lower()}:{day}"

            # DEDUPE por dia (pula a não ser que --force)
            if not opts["force"] and Noticia.objects.filter(fonte_url=key).exists():
                if opts["debug"]:
                    self.stdout.write(f"– já existe hoje: {topic_clean}")
                continue
            if opts["force"] and opts["debug"]:
                self.stdout.write(self.style.WARNING(f"· forçando publicação: {topic_clean}"))

            # ---------- Categoria por roteamento ----------
            try:
                cat_slug = route_category_for_topic(topic_clean)
            except Exception:
                cat_slug = "geral"
            cat = Categoria.objects.filter(slug=cat_slug).first() or cat_fallback
            if opts["debug"]:
                self.stdout.write(self.style.NOTICE(f"[categoria] '{topic_clean}' → {cat.slug}"))

            # ---------- Geração de conteúdo ----------
            try:
                art = generate_article(topic_clean) or {}
            except Exception as e:
                if opts["debug"]:
                    self.stdout.write(self.style.WARNING(f"· IA falhou para '{topic_clean}': {e}"))
                art = {}

            title = strip_tags((art.get("title") or topic_clean).strip())[:140]
            dek = strip_tags((art.get("dek") or art.get("description") or "").strip())[:220]
            body = (art.get("html") or "<p></p>").strip()
            conteudo = f'<p class="dek">{dek}</p>\n{body}' if dek else body

            # ---------- Imagem ----------
            img_info = None
            try:
                img_info = pick_image(topic_clean)
            except Exception as e:
                if opts["debug"]:
                    self.stdout.write(self.style.WARNING(f"· imagem falhou para '{topic_clean}': {e}"))
                img_info = None

            # ---------- Monta kwargs, incluindo status se existir ----------
            kwargs = dict(
                titulo=title,
                conteudo=conteudo,
                publicado_em=timezone.now(),
                fonte_url=key,
                categoria=cat,  # <- dinâmica por tópico
            )
            if published_value is not _NO_STATUS_SENTINEL:
                kwargs["status"] = published_value  # >>> chave do NOT NULL

            obj = Noticia(**kwargs)

            # redundância defensiva: se por qualquer motivo ainda estiver vazio, preenche agora
            if hasattr(obj, "status"):
                cur = getattr(obj, "status", None)
                if cur in (None, "", 0, False):
                    fallback = _status_published(Noticia)
                    if fallback is not _NO_STATUS_SENTINEL:
                        setattr(obj, "status", fallback)
                        if opts["debug"]:
                            self.stdout.write(self.style.NOTICE(f"[status] ajustado no objeto = {fallback!r}"))

            if hasattr(obj, "fonte_nome") and not getattr(obj, "fonte_nome", ""):
                obj.fonte_nome = "RadarBR Trends"
            if hasattr(obj, "imagem_alt"):
                obj.imagem_alt = title

            if img_info and img_info.get("content"):
                try:
                    obj.imagem.save(img_info["filename"], img_info["content"], save=False)
                    if hasattr(obj, "imagem_credito"):
                        obj.imagem_credito = img_info.get("credito", "")
                    if hasattr(obj, "imagem_licenca"):
                        obj.imagem_licenca = img_info.get("licenca", "")
                    if hasattr(obj, "imagem_fonte_url"):
                        obj.imagem_fonte_url = img_info.get("fonte_url", "")
                except Exception as e:
                    if opts["debug"]:
                        self.stdout.write(self.style.WARNING(f"· falha ao salvar imagem: {e}"))

            obj.slug = unique_slug(title)
            obj.save()  # <<< NÃO deve mais falhar por status nulo
            created += 1
            self.stdout.write(self.style.SUCCESS(f"✓ publicado: {topic_clean}"))

        self.stdout.write(self.style.SUCCESS(f"Pronto. novos artigos: {created}"))

        # ---------- Ping de buscadores ----------
        try:
            if created > 0:
                from core.utils import absolute_sitemap_url
                from rb_ingestor.ping import ping_search_engines

                sm_url = absolute_sitemap_url()
                res = ping_search_engines(sm_url)
                self.stdout.write(
                    self.style.NOTICE(
                        f"Ping sitemap: Google={'OK' if res['google'] else 'NOK'}; "
                        f"Bing={'OK' if res['bing'] else 'NOK'}"
                    )
                )
        except Exception:
            # silencioso em dev
            pass
