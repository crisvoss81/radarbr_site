from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post, Category

PAGE_SIZE = 12

def home(request):
    qs = Post.objects.filter(is_published=True, published_at__lte=timezone.now())
    page_obj = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "home.html", {"page_obj": page_obj})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    related = (Post.objects
               .filter(is_published=True, category=post.category)
               .exclude(id=post.id)[:6])
    return render(request, "post_detail.html", {"post": post, "related": related})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    qs = category.posts.filter(is_published=True, published_at__lte=timezone.now())
    page_obj = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "category_detail.html", {"category": category, "page_obj": page_obj})
