from django.contrib import admin
from .models import Category, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name","slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title","category","is_published","published_at")
    list_filter = ("is_published","category")
    search_fields = ("title","excerpt","content","source_name","source_url")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title","slug","category","excerpt","content")}),
        ("Imagem", {"fields": ("cover","cover_alt")}),
        ("Fonte", {"fields": ("source_name","source_url")}),
        ("Publicação", {"fields": ("is_published",)}),
    )

