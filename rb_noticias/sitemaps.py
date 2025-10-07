# rb_noticias/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.db.models import Max

from .models import Noticia, Categoria

class NoticiasSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.9
    protocol = "https"

    def items(self):
        # Apenas notícias publicadas
        return Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by("-publicado_em")[:5000]

    def lastmod(self, obj: Noticia):
        return obj.publicado_em
    
    def priority(self, obj: Noticia):
        # Prioridade mais alta para notícias recentes (últimas 24h)
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        if obj.publicado_em >= now - timedelta(hours=24):
            return 0.9
        elif obj.publicado_em >= now - timedelta(days=7):
            return 0.8
        else:
            return 0.7


class CategoriaSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6
    protocol = "https"

    def items(self):
        return Categoria.objects.all()

    def location(self, obj: Categoria):
        return obj.get_absolute_url()

    def lastmod(self, obj: Categoria):
        return (
            Noticia.objects.filter(categoria=obj, status=Noticia.Status.PUBLICADO)
            .aggregate(m=Max("publicado_em"))
            .get("m")
        )


class StaticViewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    protocol = "https"

    def items(self):
        # home e outras rotas "estáticas" que você quiser expor
        return ["home"]

    def location(self, name: str):
        return reverse(name)
