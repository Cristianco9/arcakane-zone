from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Categoria, Genero, Plataforma, Videojuego


@admin.register(Categoria)
class CategoriaAdmin(ModelAdmin):
    list_display = ["nombre", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre"]


@admin.register(Plataforma)
class PlataformaAdmin(ModelAdmin):
    list_display = ["nombre", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre"]


@admin.register(Genero)
class GeneroAdmin(ModelAdmin):
    list_display = ["nombre", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre"]


@admin.register(Videojuego)
class VideojuegoAdmin(ModelAdmin):
    list_display = ["titulo", "categoria", "plataforma", "genero", "precio", "stock", "activo"]
    list_filter = ["activo", "categoria", "plataforma", "genero"]
    search_fields = ["titulo", "descripcion"]
    list_editable = ["precio", "stock", "activo"]
    date_hierarchy = "creado_en"
