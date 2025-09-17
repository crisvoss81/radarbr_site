# siteapp/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post, Category

class PostSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.9
    def items(self):
        return Post.objects.filter(is_published=True)
    def lastmod(self, obj):
        return obj.published_at
    def location(self, obj):
        return obj.get_absolute_url()

class CategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6
    def items(self):
        return Category.objects.all()
    def location(self, obj):
        # ajuste se seu model já tiver get_absolute_url
        try:
            return obj.get_absolute_url()
        except AttributeError:
            return reverse("category_detail", args=[obj.slug])
