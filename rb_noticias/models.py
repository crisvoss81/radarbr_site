# rb_noticias/models.py
from django.db import models
from django.urls import reverse
from cloudinary.models import CloudinaryField # Adicione esta importação

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

    # AQUI ESTÁ A MUDANÇA: Substituímos ImageField por CloudinaryField
    imagem = CloudinaryField(
        'imagem',
        overwrite=True,
        resource_type='image',
        folder='noticias', # Pasta onde as imagens serão salvas no Cloudinary
        transformation={'quality': 'auto:good', 'fetch_format': 'auto'},
        blank=True,
        null=True
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