# core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

from django.contrib.sitemaps.views import sitemap
from rb_noticias.sitemaps import NoticiasSitemap, CategoriaSitemap, StaticViewsSitemap
from core.views import robots_txt
from rb_noticias.feeds import UltimasNoticiasFeed

sitemaps = {
    "noticias": NoticiasSitemap,
    "categorias": CategoriaSitemap,
    "static": StaticViewsSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("rb_noticias.urls", namespace="rb_noticias")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("feed/", UltimasNoticiasFeed(), name="rss_feed"),
    path("ads.txt", TemplateView.as_view(template_name="ads.txt", content_type="text/plain")),
]

# Adiciona a rota para arquivos de MÍDIA (funciona em DEV e PROD)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Adiciona a rota para arquivos ESTÁTICOS (apenas em DEV)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)