# rb_noticias/feeds.py
import re
from django.contrib.syndication.views import Feed
from django.utils.html import strip_tags
from .models import Noticia

_DEK_RE = re.compile(
    r'<p[^>]*class="[^"]*\bdek\b[^"]*"[^>]*>(.*?)</p>',
    re.IGNORECASE | re.DOTALL
)

def _dek_from_html(html: str) -> str:
    if not html:
        return ""
    m = _DEK_RE.search(html)
    if m:
        return strip_tags(m.group(1)).strip()
    # fallback: primeiro parágrafo
    m2 = re.search(r"<p[^>]*>(.*?)</p>", html, re.I | re.S)
    return strip_tags(m2.group(1)).strip() if m2 else ""

class UltimasNoticiasFeed(Feed):
    title = "RadarBR — Últimas notícias"
    link = "/"
    description = "Últimos artigos publicados no RadarBR."

    def items(self):
        return Noticia.objects.order_by("-publicado_em")[:30]

    def item_title(self, item: Noticia):
        return strip_tags(item.titulo or "")

    def item_description(self, item: Noticia):
        return _dek_from_html(item.conteudo or "")[:500]

    def item_link(self, item: Noticia):
        return item.get_absolute_url()

    def item_pubdate(self, item: Noticia):
        return item.publicado_em
