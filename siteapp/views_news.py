# siteapp/views_news.py
from datetime import timezone as dt_tz
from django.http import HttpResponse
from django.utils import timezone
from xml.sax.saxutils import escape
from .models import Post

def _iso_utc(dt):
    if dt is None:
        dt = timezone.now()
    # garante UTC e formato 2025-09-18T12:34:56Z
    return dt.astimezone(dt_tz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def news_sitemap(request):
    cutoff = timezone.now() - timezone.timedelta(days=2)
    posts = (
        Post.objects.filter(is_published=True, published_at__gte=cutoff)
        .order_by("-published_at")[:1000]
    )

    pub_name = "RadarBR"
    pub_lang = "pt-BR"

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
    ]

    for p in posts:
        loc = request.build_absolute_uri(p.get_absolute_url())
        pub_date = _iso_utc(p.published_at)
        title = escape(p.title or "")
        parts.append(
            "<url>"
            f"<loc>{escape(loc)}</loc>"
            "<news:news>"
            "<news:publication>"
            f"<news:name>{escape(pub_name)}</news:name>"
            f"<news:language>{escape(pub_lang)}</news:language>"
            "</news:publication>"
            f"<news:publication_date>{pub_date}</news:publication_date>"
            f"<news:title>{title}</news:title>"
            "</news:news>"
            "</url>"
        )

    parts.append("</urlset>")
    return HttpResponse("\n".join(parts), content_type="application/xml")
