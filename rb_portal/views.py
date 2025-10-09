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


def test_images(request):
    """View para testar se as imagens estão funcionando"""
    from rb_noticias.models import Noticia
    
    # Notícias com imagens
    noticias_com_imagem = Noticia.objects.exclude(imagem__isnull=True).exclude(imagem='')[:10]
    
    # Últimas 5 notícias
    ultimas_noticias = Noticia.objects.all().order_by('-publicado_em')[:5]
    
    ctx = {
        "noticias_com_imagem": noticias_com_imagem,
        "ultimas_noticias": ultimas_noticias,
    }
    return render(request, "rb_portal/test_images.html", ctx)


def post_detail(request, slug):
    obj = get_object_or_404(Noticia, slug=slug)
    relacionados = (
        Noticia.objects.filter(categoria=obj.categoria)
        .exclude(pk=obj.pk)
        .order_by("-publicado_em")[:6]
    )
    ctx = {
        "object": obj,
        "related_articles": relacionados,
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