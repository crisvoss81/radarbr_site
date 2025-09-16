from django.contrib.sitemaps import Sitemap
from django.utils import timezone
from .models import Post, Category

class PostSitemap(Sitemap):
    changefreq="hourly"; priority=0.9
    def items(self): return Post.objects.filter(is_published=True, published_at__lte=timezone.now())
    def lastmod(self, obj): return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq="daily"; priority=0.6
    def items(self): return Category.objects.all()
