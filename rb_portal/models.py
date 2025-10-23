# rb_portal/models.py
from django.db import models

class ConfiguracaoSite(models.Model):
    """Modelo para configurações gerais do site"""
    
    # Informações de contato
    email_contato = models.EmailField(
        max_length=255,
        default="contato@radarbr.com.br",
        help_text="E-mail principal para contato"
    )
    email_redacao = models.EmailField(
        max_length=255,
        default="redacao@radarbr.com.br",
        help_text="E-mail da redação"
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Telefone de contato (opcional)"
    )
    endereco = models.TextField(
        blank=True,
        help_text="Endereço físico (opcional)"
    )
    
    # Redes sociais
    facebook_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL do Facebook"
    )
    twitter_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL do Twitter/X"
    )
    instagram_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL do Instagram"
    )
    youtube_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL do YouTube"
    )
    linkedin_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL do LinkedIn"
    )
    telegram_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL do Telegram"
    )
    
    # Configurações gerais
    nome_site = models.CharField(
        max_length=100,
        default="RadarBR",
        help_text="Nome do site"
    )
    slogan = models.CharField(
        max_length=200,
        default="Suas notícias em tempo real",
        help_text="Slogan do site"
    )
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configurações do Site"
    
    def __str__(self):
        return f"Configurações do {self.nome_site}"
    
    def save(self, *args, **kwargs):
        # Garantir que existe apenas uma configuração
        if not self.pk and ConfiguracaoSite.objects.exists():
            # Se já existe uma configuração, atualizar ela
            existing = ConfiguracaoSite.objects.first()
            existing.email_contato = self.email_contato
            existing.email_redacao = self.email_redacao
            existing.telefone = self.telefone
            existing.endereco = self.endereco
            existing.facebook_url = self.facebook_url
            existing.twitter_url = self.twitter_url
            existing.instagram_url = self.instagram_url
            existing.youtube_url = self.youtube_url
            existing.linkedin_url = self.linkedin_url
            existing.telegram_url = self.telegram_url
            existing.nome_site = self.nome_site
            existing.slogan = self.slogan
            existing.save()
            return existing
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Retorna a configuração atual do site"""
        config, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'email_contato': 'contato@radarbr.com.br',
                'email_redacao': 'redacao@radarbr.com.br',
                'nome_site': 'RadarBR',
                'slogan': 'Suas notícias em tempo real'
            }
        )
        return config