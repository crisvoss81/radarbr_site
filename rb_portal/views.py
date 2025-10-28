# rb_portal/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

# IMPORTANTE: Ajuste a importação dos modelos
from rb_noticias.models import Noticia, Categoria
from rb_portal.models import ConfiguracaoSite

def home(request):
    try:
        # Buscar todas as notícias publicadas ordenadas por data de publicação (mais recente primeiro)
        # IMPORTANTE: Filtrar apenas notícias com data de publicação <= agora
        from django.utils import timezone
        all_news = Noticia.objects.filter(
            status=Noticia.Status.PUBLICADO,
            publicado_em__lte=timezone.now()  # Apenas notícias já publicadas (não agendadas)
        ).order_by("-publicado_em")  # Ordenar por data de publicação
        
        # Buscar notícia em destaque primeiro
        featured = all_news.filter(destaque=True).first()
        
        # Se não houver destaque, pegar a mais recente
        if not featured:
            featured = all_news.first()
        
        # Buscar outras notícias para exibição (excluindo a featured) - sempre as mais recentes
        # IMPORTANTE: Usar todas as notícias em ordem cronológica, não apenas as 3 primeiras
        others_qs = all_news.exclude(id=featured.id) if featured else all_news

        # Sistema de trending híbrido (recência + engajamento) para sidebar
        trending = Noticia.objects.filter(
            status=Noticia.Status.PUBLICADO,
            publicado_em__lte=timezone.now()
        ).exclude(id=featured.id if featured else None).order_by(
            '-trending_score', '-publicado_em'
        )[:4]

        # Para paginação, usar TODAS as notícias (exceto a featured) em ordem cronológica
        paginator = Paginator(others_qs, 10)
        page_obj = paginator.get_page(request.GET.get("page") or 1)

        ctx = {
            "featured": featured,
            "trending": trending,
            "page_obj": page_obj,
            "cats": Categoria.objects.all().order_by("nome"),
        }
        return render(request, "rb_portal/home.html", ctx)
    except Exception as e:
        # Log do erro e retorno de fallback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro na view home: {e}")
        
        # Retorno de emergência sem filtros complexos
        from django.utils import timezone
        all_news = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by("-publicado_em")
        featured = all_news.first()
        others_qs = all_news.exclude(id=featured.id) if featured else all_news
        paginator = Paginator(others_qs, 10)
        page_obj = paginator.get_page(request.GET.get("page") or 1)
        
        ctx = {
            "featured": featured,
            "trending": [],
            "page_obj": page_obj,
            "cats": Categoria.objects.all().order_by("nome"),
        }
        return render(request, "rb_portal/home.html", ctx)


def test_images(request):
    """View para testar se as imagens estão funcionando"""
    from rb_noticias.models import Noticia
    
    # Notícias com imagens
    noticias_com_imagem = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).exclude(imagem__isnull=True).exclude(imagem='')[:10]
    
    # Últimas 5 notícias
    ultimas_noticias = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by('-publicado_em')[:5]
    
    ctx = {
        "noticias_com_imagem": noticias_com_imagem,
        "ultimas_noticias": ultimas_noticias,
    }
    return render(request, "rb_portal/test_images.html", ctx)


def post_detail(request, slug):
    obj = get_object_or_404(Noticia, slug=slug, status=Noticia.Status.PUBLICADO)
    
    # Incrementar contador de visualizações
    obj.increment_views()
    
    relacionados = (
        Noticia.objects.filter(categoria=obj.categoria, status=Noticia.Status.PUBLICADO)
        .exclude(pk=obj.pk)
        .order_by("-publicado_em")[:6]
    )
    
    # Sistema de trending híbrido para sidebar
    trending = Noticia.objects.filter(
        status=Noticia.Status.PUBLICADO
    ).exclude(id=obj.id).order_by('-trending_score', '-publicado_em')[:4]
    
    # Buscar notícias para fallback
    qs = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by("-publicado_em")
    others = list(qs.exclude(id=obj.id)[:3])
    
    ctx = {
        "object": obj,
        "related_articles": relacionados,
        "trending": trending,
        "others": others,
        "cats": Categoria.objects.all().order_by("nome"),
    }
    return render(request, "rb_portal/post_detail.html", ctx)


def category_list(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    qs = Noticia.objects.filter(categoria=categoria, status=Noticia.Status.PUBLICADO).order_by("-publicado_em")
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    ctx = {
        "categoria": categoria,
        "page_obj": page_obj,
        "cats": Categoria.objects.all().order_by("nome"),
    }
    return render(request, "rb_portal/category_list.html", ctx)


def all_categories(request):
    """View para mostrar todas as categorias"""
    categories = Categoria.objects.all().order_by("nome")
    
    # Buscar última notícia de cada categoria
    categories_with_news = []
    for category in categories:
        last_news = Noticia.objects.filter(
            categoria=category, 
            status=Noticia.Status.PUBLICADO
        ).order_by("-publicado_em").first()
        
        categories_with_news.append({
            'category': category,
            'last_news': last_news
        })
    
    # Sistema de trending híbrido para sidebar
    trending = Noticia.objects.filter(
        status=Noticia.Status.PUBLICADO
    ).order_by('-trending_score', '-publicado_em')[:4]
    
    # Buscar notícias para fallback
    qs = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by("-publicado_em")
    others = list(qs[1:3])  # Para fallback
    
    # Criar page_obj vazio para evitar erro na sidebar
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(1)
    
    ctx = {
        "categories_with_news": categories_with_news,
        "categories": categories,
        "cats": categories,  # Para manter consistência com sidebar
        "others": others,    # Para fallback
        "trending": trending,    # Sistema de trending híbrido
        "page_obj": page_obj, # Para evitar erro na sidebar
    }
    return render(request, "rb_portal/all_categories.html", ctx)


def contato(request):
    """View para página de contato"""
    # Sistema de trending híbrido para sidebar
    trending = Noticia.objects.filter(
        status=Noticia.Status.PUBLICADO
    ).order_by('-trending_score', '-publicado_em')[:4]
    
    # Buscar notícias para fallback
    qs = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by("-publicado_em")
    others = list(qs[1:3])
    
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(1)
    
    # Buscar configurações do site
    config = ConfiguracaoSite.get_config()
    
    ctx = {
        "cats": Categoria.objects.all().order_by("nome"),
        "others": others,
        "trending": trending,
        "page_obj": page_obj,
        "config": config,
    }
    return render(request, "rb_portal/contato.html", ctx)


def redes_sociais(request):
    """View para página de redes sociais"""
    # Sistema de trending híbrido para sidebar
    trending = Noticia.objects.filter(
        status=Noticia.Status.PUBLICADO
    ).order_by('-trending_score', '-publicado_em')[:4]
    
    # Buscar notícias para fallback
    qs = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by("-publicado_em")
    others = list(qs[1:3])
    
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(1)
    
    # Buscar configurações do site
    config = ConfiguracaoSite.get_config()
    
    ctx = {
        "cats": Categoria.objects.all().order_by("nome"),
        "others": others,
        "trending": trending,
        "page_obj": page_obj,
        "config": config,
    }
    return render(request, "rb_portal/redes_sociais.html", ctx)


def politicas(request):
    """View para página de políticas"""
    # Sistema de trending híbrido para sidebar
    trending = Noticia.objects.filter(
        status=Noticia.Status.PUBLICADO
    ).order_by('-trending_score', '-publicado_em')[:4]
    
    # Buscar notícias para fallback
    qs = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by("-publicado_em")
    others = list(qs[1:3])
    
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(1)
    
    # Buscar configurações do site
    config = ConfiguracaoSite.get_config()
    
    ctx = {
        "cats": Categoria.objects.all().order_by("nome"),
        "others": others,
        "trending": trending,
        "page_obj": page_obj,
        "config": config,
    }
    return render(request, "rb_portal/politicas.html", ctx)


def sobre(request):
    """View para página sobre"""
    # Sistema de trending híbrido para sidebar
    trending = Noticia.objects.filter(
        status=Noticia.Status.PUBLICADO
    ).order_by('-trending_score', '-publicado_em')[:4]
    
    # Buscar notícias para fallback
    qs = Noticia.objects.filter(status=Noticia.Status.PUBLICADO).order_by("-publicado_em")
    others = list(qs[1:3])
    
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(1)
    
    # Buscar configurações do site
    config = ConfiguracaoSite.get_config()
    
    ctx = {
        "cats": Categoria.objects.all().order_by("nome"),
        "others": others,
        "trending": trending,
        "page_obj": page_obj,
        "config": config,
    }
    return render(request, "rb_portal/sobre.html", ctx)