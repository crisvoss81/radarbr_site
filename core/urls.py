# core/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.contrib.sitemaps.views import sitemap

# Importe as views do rb_portal e outras ferramentas
from rb_portal import views as portal_views
from core.views import robots_txt
from core.media_views import serve_media_file
from rb_noticias.sitemaps import NoticiasSitemap, CategoriaSitemap, StaticViewsSitemap
from rb_noticias.feeds import UltimasNoticiasFeed

sitemaps = {
    "noticias": NoticiasSitemap,
    "categorias": CategoriaSitemap,
    "static": StaticViewsSitemap,
}

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Views do Portal
    path("", portal_views.home, name="home"),
    path("noticia/<slug:slug>/", portal_views.post_detail, name="noticia"),
    path("categoria/<slug:slug>/", portal_views.category_list, name="categoria"),

    # Sitemaps, Feeds, etc.
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("feed/", UltimasNoticiasFeed(), name="rss_feed"),
    path("ads.txt", TemplateView.as_view(template_name="ads.txt", content_type="text/plain")),
    
    # Fallback para arquivos de mídia (caso WhiteNoise não funcione)
    path("media/<path:path>", serve_media_file, name="media_file"),
]

# Rotas para arquivos de MÍDIA e ESTÁTICOS
# Em produção, o WhiteNoise serve os arquivos estáticos
# Para mídia, precisamos servir também em produção no Render
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)