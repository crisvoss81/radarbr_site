# core/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap

from siteapp.views import home, post_detail, category_detail
from siteapp.views_search import search
from siteapp.views_misc import robots_txt
from siteapp.views_news import news_sitemap
from siteapp.sitemaps import sitemaps
from siteapp.feeds import LatestPostsFeed

urlpatterns = [
    path("", home, name="home"),
    path("post/<slug:slug>/", post_detail, name="post_detail"),
    path("categoria/<slug:slug>/", category_detail, name="category_detail"),
    path("buscar/", search, name="search"),

    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("news-sitemap.xml", news_sitemap, name="news_sitemap"),
    path("feed.xml", LatestPostsFeed(), name="feed"),

    # verificação do Google (Arquivo HTML)
    path(
        "googlefcd08be596689a50.html",
        TemplateView.as_view(
            template_name="googlefcd08be596689a50.html",
            content_type="text/html",
        ),
        name="google_verification",
    ),

    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
