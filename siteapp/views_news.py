# siteapp/views_news.py
from datetime import timedelta
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import escape

from .models import Post

def _iso_utc(dt):
    # garante ISO 8601 em UTC (ex.: 2025-09-17T12:34:56Z)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def news_sitemap(request):
    now = timezone.now()
    window = now - timedelta(hours=48)

    # tenta por published_at; se não houver resultados, cai para created_at
    qs = Post.objects.all()
    # se existir o campo is_published, filtra por ele
    if "is_published" in [f.name for f in Post._meta.get_fields()]:
        qs = qs.filter(is_published=True)

    if "published_at" in [f.name for f in Post._meta.get_fields()]:
        qs_recent = qs.filter(published_at__gte=window).order_by("-published_at")[:1000]
    else:
        qs_recent = qs.none()

    if not qs_recent.exists() and "created_at" in [f.name for f in Post._meta.get_fields()]:
        qs_recent = qs.filter(created_at__gte=window).order_by("-created_at")[:1000]

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
    ]

    site_name = getattr(settings, "SITE_NAME", "RadarBR")

    for p in qs_recent:
        # URL canônica do post
        loc = request.build_absolute_uri(p.get_absolute_url())

        # pega a melhor data disponível
        dt = getattr(p, "published_at", None) or getattr(p, "created_at", None) or now

        lines += [
            "<url>",
            f"<loc>{escape(loc)}</loc>",
            "<news:news>",
            "<news:publication>",
            f"<news:name>{escape(site_name)}</news:name>",
            "<news:language>pt-BR</news:language>",
            "</news:publication>",
            f"<news:publication_date>{_iso_utc(dt)}</news:publication_date>",
            f"<news:title>{escape(p.title)}</news:title>",
            "</news:news>",
            "</url>",
        ]

    lines.append("</urlset>")
    xml = "\n".join(lines)
    return HttpResponse(xml, content_type="application/xml")
