from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.html import escape
from slugify import slugify
from .models import Categoria, Noticia
import json

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    prepopulated_fields = {'slug': ('nome',)}

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'status', 'destaque', 'publicado_em', 'criado_em']
    list_filter = ['categoria', 'status', 'destaque', 'publicado_em']
    search_fields = ['titulo', 'conteudo']
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'publicado_em'
    
    fieldsets = (
        ('Conteúdo Principal', {
            'fields': ('titulo', 'slug', 'conteudo', 'categoria', 'status', 'destaque')
        }),
        ('Data e Hora', {
            'fields': ('publicado_em',)
        }),
        ('Imagem', {
            'fields': ('imagem', 'imagem_alt', 'imagem_credito', 'imagem_licenca', 'imagem_fonte_url'),
            'classes': ('collapse',)
        }),
        ('Fonte', {
            'fields': ('fonte_url', 'fonte_nome'),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        js = ('admin/js/noticia_auto_fill.js',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('auto-fill/', self.admin_site.admin_view(self.auto_fill_view), name='noticia_auto_fill'),
        ]
        return custom_urls + urls
    
    def auto_fill_view(self, request):
        """View para preenchimento automático dos campos"""
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                titulo = data.get('titulo', '').strip()
                categoria_id = data.get('categoria_id')
                
                if not titulo:
                    return JsonResponse({'error': 'Título é obrigatório'}, status=400)
                
                # Gerar slug automaticamente
                slug = slugify(titulo)[:180]
                
                # Gerar fonte URL automaticamente com foco em SEO
                from django.utils import timezone
                import random
                import string
                
                # Criar URL SEO-friendly baseada no título
                titulo_slug = slugify(titulo)[:30]
                timestamp = timezone.now().strftime('%Y%m%d')
                
                # Gerar ID único para evitar duplicatas
                unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                
                # URL otimizada para SEO
                fonte_url = f"radarbr-{titulo_slug}-{timestamp}-{unique_id}"
                
                # Verificar se já existe e gerar nova se necessário
                counter = 1
                original_fonte_url = fonte_url
                while Noticia.objects.filter(fonte_url=fonte_url).exists():
                    fonte_url = f"{original_fonte_url}-{counter}"
                    counter += 1
                
                # Gerar nome da fonte SEO-friendly
                if categoria_id:
                    try:
                        categoria = Categoria.objects.get(id=categoria_id)
                        fonte_nome = f"RadarBR - {categoria.nome}"
                    except Categoria.DoesNotExist:
                        fonte_nome = "RadarBR"
                else:
                    fonte_nome = "RadarBR"
                
                # Gerar alt text para imagem
                imagem_alt = f"Imagem relacionada a {titulo[:50]}"
                
                # Se categoria foi especificada, gerar alt text mais específico
                if categoria_id:
                    try:
                        categoria = Categoria.objects.get(id=categoria_id)
                        imagem_alt = f"Imagem sobre {categoria.nome.lower()} - {titulo[:30]}"
                    except Categoria.DoesNotExist:
                        pass
                
                return JsonResponse({
                    'success': True,
                    'data': {
                        'slug': slug,
                        'fonte_url': fonte_url,
                        'fonte_nome': fonte_nome,
                        'imagem_alt': imagem_alt,
                        'imagem_credito': 'Imagem selecionada pelo administrador',
                        'imagem_licenca': 'CC',
                    }
                })
                
            except Exception as e:
                return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)
        
        return JsonResponse({'error': 'Método não permitido'}, status=405)
