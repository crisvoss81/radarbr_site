# rb_noticias/urls.py
from django.urls import path
from . import views

app_name = "rb_noticias"

urlpatterns = [
    path("", views.home, name="home"),
    path("categoria/<slug:slug>/", views.category_list, name="categoria"),
    path("noticia/<slug:slug>/", views.post_detail, name="noticia"),
]
