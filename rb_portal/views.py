# rb_portal/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

# IMPORTANTE: Ajuste a importação dos modelos
from rb_noticias.models import Noticia, Categoria

def home(request):
    qs = Noticia.objects.order_by("-publicado_em")

    featured = qs.first()
    others = list(qs[1:3])

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    ctx = {
        "featured": featured,
        "others": others,
        "page_obj": page_obj,
        "cats": Categoria.objects.all().order_by("nome"),
    }
    return render(request, "rb_portal/home.html", ctx)


def post_detail(request, slug):
    obj = get_object_or_404(Noticia, slug=slug)
    relacionados = (
        Noticia.objects.filter(categoria=obj.categoria)
        .exclude(pk=obj.pk)
        .order_by("-publicado_em")[:6]
    )
    ctx = {
        "object": obj,
        "relacionados": relacionados,
        "cats": Categoria.objects.all().order_by("nome"),
    }
    return render(request, "rb_portal/post_detail.html", ctx)


def category_list(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    qs = Noticia.objects.filter(categoria=categoria).order_by("-publicado_em")
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    ctx = {
        "categoria": categoria,
        "page_obj": page_obj,
        "cats": Categoria.objects.all().order_by("nome"),
    }
    return render(request, "rb_portal/category_list.html", ctx)