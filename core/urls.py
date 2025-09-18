# core/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from siteapp.views import home, post_detail, category_detail
from siteapp.views_news import news_sitemap

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("post/<slug:slug>/", post_detail, name="post_detail"),
    path("categoria/<slug:slug>/", category_detail, name="category_detail"),
    path("news-sitemap.xml", news_sitemap, name="news_sitemap"),
]

# servir media em dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    from siteapp.views_misc import robots_txt
urlpatterns += [
    path("robots.txt", robots_txt, name="robots_txt"),
]

from django.contrib.sitemaps.views import sitemap
from siteapp.sitemaps import PostSitemap, CategorySitemap

sitemaps = {"posts": PostSitemap, "categories": CategorySitemap}

urlpatterns += [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

from django.views.generic import TemplateView

urlpatterns = [
    # ... suas outras rotas
    path(
        "googlefcd08be596689a50.html",
        TemplateView.as_view(
            template_name="googlefcd08be596689a50.html",
            content_type="text/html",
        ),
    ),
]
