# rb_noticias/models.py
from django.db import models
from django.urls import reverse
from slugify import slugify

class Categoria(models.Model):
    nome = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        if not self.slug:
            # Garante slug válido para evitar NoReverseMatch
            self.slug = slugify(self.nome)[:140]
            try:
                self.save(update_fields=["slug"])
            except Exception:
                pass
        return reverse("categoria", args=[self.slug])


class Noticia(models.Model):

    class Status(models.IntegerChoices):
        RASCUNHO = 0, "Rascunho"
        PUBLICADO = 1, "Publicado"

    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=180, unique=True)
    conteudo = models.TextField()
    publicado_em = models.DateTimeField()

    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True
    )
    
    status = models.IntegerField(
        default=Status.PUBLICADO,
        choices=Status.choices,
    )
    
    destaque = models.BooleanField(
        default=False,
        help_text="Se marcado, esta notícia será exibida como destaque no topo da home"
    )

    # Campo de imagem - URL externa de serviços gratuitos
    imagem = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="URL da imagem da notícia (Wikimedia, Openverse, etc.)"
    )
    
    imagem_alt = models.CharField(max_length=200, blank=True, default="")
    imagem_credito = models.CharField(max_length=200, blank=True, default="")
    imagem_licenca = models.CharField(max_length=120, blank=True, default="")
    imagem_fonte_url = models.CharField(max_length=300, blank=True, default="")

    fonte_url = models.URLField(max_length=1000, unique=True, blank=True, default="")
    fonte_nome = models.CharField(max_length=160, blank=True, default="")

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ["-publicado_em"]

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse("noticia", args=[self.slug])