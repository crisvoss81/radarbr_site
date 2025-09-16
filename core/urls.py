from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from siteapp.views import home, post_detail, category_detail
from siteapp.sitemaps import PostSitemap, CategorySitemap
from django.contrib.sitemaps.views import sitemap
from siteapp.feeds import LatestPostsFeed
from siteapp.views_misc import robots_txt
from siteapp.views_search import search
from siteapp.views_news import news_sitemap

sitemaps = {"posts": PostSitemap, "categories": CategorySitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("categoria/<slug:slug>/", category_detail, name="category_detail"),
    path("post/<slug:slug>/", post_detail, name="post_detail"),
    path("buscar/", search, name="search"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("news-sitemap.xml", news_sitemap, name="news_sitemap"),
    path("rss.xml", LatestPostsFeed(), name="rss"),
    re_path(r"^robots\.txt$", robots_txt, name="robots_txt"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
