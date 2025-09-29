from django.conf import settings
from django.apps import apps

# ordem oficial do menu superior (ajuste se quiser mudar a ordem)
MENU_TOP_SLUGS = [
    "brasil", "politica", "economia", "tecnologia",
    "esportes", "entretenimento", "mundo", "cidades-rs",
]

def site_constants(request):
    return {"SITE_NAME": getattr(settings, "SITE_NAME", "RadarBR")}

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
    por_slug = {c.slug: c for c in Categoria.objects.filter(slug__in=MENU_TOP_SLUGS)}
    menu_top = [por_slug[s] for s in MENU_TOP_SLUGS if s in por_slug]
    slugs_top = set(MENU_TOP_SLUGS)
    menu_more = [c for c in todas if c.slug not in slugs_top]

    return {"menu_top": menu_top, "menu_more": menu_more, "categorias_nav": todas[:20]}
