from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from .models import Post

def search(request):
    q = (request.GET.get("q") or "").strip()
    qs = Post.objects.filter(is_published=True, published_at__lte=timezone.now())
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(excerpt__icontains=q) |
            Q(content__icontains=q)
        )
    page_obj = Paginator(qs, 12).get_page(request.GET.get("page"))
    return render(request, "search.html", {"q": q, "page_obj": page_obj})
