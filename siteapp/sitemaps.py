# siteapp/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post, Category


class PostSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.8

    def items(self):
        # só posts publicados
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        # usa published_at ou updated_at se existir
        return getattr(obj, "published_at", None) or getattr(obj, "updated_at", None)

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse("category_detail", args=[obj.slug])


# ESTE é o dict que o core/urls.py importa
sitemaps = {
    "posts": PostSitemap,
    "categories": CategorySitemap,
}
