# rb_noticias/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.db.models import Max

from .models import Noticia, Categoria

class NoticiasSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.9
    protocol = "https"   # em dev o Django usa o host atual; em prod mantenha https

    def items(self):
        # limite alto, mas evita carregar tudo de uma vez se seu banco crescer muito
        return Noticia.objects.order_by("-publicado_em")[:5000]

    def lastmod(self, obj: Noticia):
        return obj.publicado_em


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
            Noticia.objects.filter(categoria=obj)
            .aggregate(m=Max("publicado_em"))
            .get("m")
        )


class StaticViewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    protocol = "https"

    def items(self):
        # home e outras rotas “estáticas” que você quiser expor
        return ["rb_noticias:home"]

    def location(self, name: str):
        return reverse(name)
