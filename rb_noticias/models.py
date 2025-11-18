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

    # Métricas de engajamento para sistema de trending
    views = models.PositiveIntegerField(
        default=0,
        help_text="Número de visualizações da notícia"
    )
    
    clicks = models.PositiveIntegerField(
        default=0,
        help_text="Número de cliques na notícia"
    )
    
    shares = models.PositiveIntegerField(
        default=0,
        help_text="Número de compartilhamentos"
    )
    
    trending_score = models.FloatField(
        default=0.0,
        help_text="Score calculado para trending (atualizado automaticamente)"
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

    # Vídeos do YouTube (opcional)
    show_youtube = models.BooleanField(
        default=False,
        help_text="Se marcado, exibe os vídeos do YouTube neste artigo"
    )
    youtube_urls = models.TextField(
        blank=True,
        default="",
        help_text="Cole uma ou mais URLs do YouTube, uma por linha"
    )

    fonte_url = models.URLField(max_length=1000, unique=True, blank=True, default="")
    fonte_nome = models.CharField(max_length=160, blank=True, default="")

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ["-publicado_em"]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        """Gera slug automaticamente a partir do título se não foi fornecido"""
        # 1. Gerar slug se não existir
        if not self.slug and self.titulo:
            self.slug = slugify(self.titulo)[:180]
            # Garantir que o slug seja único
            original_slug = self.slug
            counter = 1
            while Noticia.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"[:180]
                counter += 1
        elif self.slug:
            # Validar slug se foi alterado manualmente
            self.slug = slugify(self.slug)[:180]
        
        # 2. Preencher fonte_url automaticamente com o slug se estiver vazio
        if self.slug and (not self.fonte_url or self.fonte_url.strip() == ''):
            # Criar URL completa usando o slug
            from django.conf import settings
            try:
                # Tentar pegar SITE_BASE_URL das configurações
                site_url = getattr(settings, 'SITE_BASE_URL', None)
                if not site_url:
                    # Fallback: usar URL padrão
                    site_url = 'https://radarbr.com.br'
                
                # Construir URL completa
                absolute_url = self.get_absolute_url()  # Retorna: /noticia/slug
                self.fonte_url = f"{site_url.rstrip('/')}{absolute_url}"
            except Exception:
                # Fallback: usar URL padrão com o slug
                self.fonte_url = f"https://radarbr.com.br/noticia/{self.slug}"
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("noticia", args=[self.slug])
    
    def calculate_trending_score(self):
        """Calcula o score de trending baseado em engajamento e recência"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Fatores de peso
        VIEWS_WEIGHT = 1.0
        CLICKS_WEIGHT = 2.0
        SHARES_WEIGHT = 3.0
        RECENCY_WEIGHT = 0.1
        
        # Score baseado em engajamento
        engagement_score = (
            self.views * VIEWS_WEIGHT +
            self.clicks * CLICKS_WEIGHT +
            self.shares * SHARES_WEIGHT
        )
        
        # Score baseado em recência (mais recente = maior score)
        now = timezone.now()
        days_old = (now - self.publicado_em).days
        recency_score = max(0, 30 - days_old) * RECENCY_WEIGHT
        
        # Score final
        total_score = engagement_score + recency_score
        
        # Atualiza o campo trending_score
        self.trending_score = total_score
        return total_score
    
    def increment_views(self):
        """Incrementa o contador de visualizações"""
        self.views += 1
        self.calculate_trending_score()
        self.save(update_fields=['views', 'trending_score'])
    
    def increment_clicks(self):
        """Incrementa o contador de cliques"""
        self.clicks += 1
        self.calculate_trending_score()
        self.save(update_fields=['clicks', 'trending_score'])
    
    def increment_shares(self):
        """Incrementa o contador de compartilhamentos"""
        self.shares += 1
        self.calculate_trending_score()
        self.save(update_fields=['shares', 'trending_score'])