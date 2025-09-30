# core/urls.py (Versão Definitiva de Depuração)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Imports para sitemap, robots.txt e RSS Feed
from django.contrib.sitemaps.views import sitemap
from rb_noticias.sitemaps import NoticiasSitemap, CategoriaSitemap, StaticViewsSitemap
from core.views import robots_txt
from rb_noticias.feeds import UltimasNoticiasFeed

# Dicionário de sitemaps
sitemaps = {
    "noticias": NoticiasSitemap,
    "categorias": CategoriaSitemap,
    "static": StaticViewsSitemap,
}

# Lista principal de URLs do projeto
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("rb_noticias.urls", namespace="rb_noticias")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("feed/", UltimasNoticiasFeed(), name="rss_feed"),
]

# Bloco explícito para servir arquivos estáticos e de mídia em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)