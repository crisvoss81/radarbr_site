from django.conf import settings
from django.apps import apps

# ordem oficial do menu superior (ajuste se quiser mudar a ordem)
MENU_TOP_SLUGS = [
    "brasil", "politica", "economia", "tecnologia",
    "esportes", "entretenimento", "mundo", "cidades-rs",
]

def site_constants(request):
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "RadarBR"),
        "SITE_BASE_URL": getattr(settings, "SITE_BASE_URL", "https://www.radarbr.com"),
        # Expor flags/ids importantes aos templates (GA4/Adsense/Debug)
        "GA4_ID": getattr(settings, "GA4_ID", ""),
        "ADSENSE_CLIENT": getattr(settings, "ADSENSE_CLIENT", "ca-pub-3913403142217011"),
        "debug": getattr(settings, "DEBUG", False),
    }

def site_config(_request):
    """Disponibiliza `config` (ConfiguracaoSite) globalmente aos templates."""
    try:
        ConfiguracaoSite = apps.get_model("rb_portal", "ConfiguracaoSite")
        return {"config": ConfiguracaoSite.get_config()}
    except Exception:
        # Em caso de erro (migracoes pendentes, etc), evita quebrar templates
        return {"config": None}

def categorias_nav(_request):
    Categoria = None
    for label in ("rb_noticias", "noticias"):
        try:
            Categoria = apps.get_model(label, "Categoria")
            break
        except LookupError:
            continue
    if not Categoria:
        return {"menu_top": [], "menu_more": [], "categorias_nav": []}

    todas = list(Categoria.objects.order_by("nome"))
    
    # Se não há categorias, retornar vazio
    if not todas:
        return {"menu_top": [], "menu_more": [], "categorias_nav": []}
    
    # Pegar as primeiras 8 categorias para o menu principal
    menu_top = todas[:8]
    
    # O resto vai para "Mais"
    menu_more = todas[8:]

    return {"menu_top": menu_top, "menu_more": menu_more, "categorias_nav": todas[:20]}
