from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
import os

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("category_detail", args=[self.slug])

    def __str__(self): return self.name

class Post(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    excerpt = models.CharField(max_length=240, blank=True)
    content = models.TextField()
    cover = models.ImageField(upload_to="covers/", blank=True, null=True)
    cover_alt = models.CharField(max_length=180, blank=True)
    source_name = models.CharField("Fonte (nome)", max_length=120, blank=True)
    source_url = models.URLField("Fonte (URL)", blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_published","published_at"]),
        ]

    def clean(self):
        # conteúdo mínimo (280 palavras) apenas se for publicar
        if self.is_published:
            wc = len((self.content or "").split())
            if wc < 280:
                raise ValidationError({"content": "Para publicar exigimos pelo menos 280 palavras (definição do projeto)."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt:
            self.excerpt = (self.content or "")[:240]
        super().save(*args, **kwargs)  # salva para garantir arquivo no storage

        # WebP automático
        if self.cover and not self.cover.name.lower().endswith(".webp"):
            self._convert_cover_to_webp()

        # ALT automático
        if not self.cover_alt:
            self.cover_alt = self.title
            super().save(update_fields=["cover_alt"])

    def _convert_cover_to_webp(self):
        try:
            self.cover.open()
            img = Image.open(self.cover).convert("RGB")
            buf = BytesIO()
            img.save(buf, format="WEBP", quality=85, method=6)
            buf.seek(0)
            base, _ = os.path.splitext(os.path.basename(self.cover.name))
            webp_name = f"covers/{base}.webp"
            self.cover.save(webp_name, ContentFile(buf.read()), save=False)
            super().save(update_fields=["cover"])
        except Exception:
            # se falhar a conversão, mantém o arquivo original silenciosamente
            pass

    def get_absolute_url(self):
        return reverse("post_detail", args=[self.slug])

    def __str__(self): return self.title
