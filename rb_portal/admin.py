# rb_portal/admin.py
from django.contrib import admin
from .models import ConfiguracaoSite

@admin.register(ConfiguracaoSite)
class ConfiguracaoSiteAdmin(admin.ModelAdmin):
    list_display = ['nome_site', 'email_contato', 'atualizado_em']
    readonly_fields = ['criado_em', 'atualizado_em']
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('nome_site', 'slogan')
        }),
        ('Contato', {
            'fields': ('email_contato', 'email_redacao', 'telefone', 'endereco')
        }),
        ('Redes Sociais', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'youtube_url', 'linkedin_url', 'telegram_url'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Permitir apenas uma configuração
        return not ConfiguracaoSite.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Não permitir deletar a configuração
        return False