from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Categoria,
    Genero,
    OfertaVideojuego,
    Plataforma,
    Videojuego,
    VideojuegoCategoria,
    VideojuegoGenero,
)


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


class OfertaVideojuegoInline(TabularInline):
    model = OfertaVideojuego
    extra = 0
    fields = ["plataforma", "sku", "precio_vigente", "stock", "estado_publicacion"]


class VideojuegoCategoriaInline(TabularInline):
    """Asigna categorías del catálogo a un videojuego (tabla puente explícita)."""

    model = VideojuegoCategoria
    extra = 0
    fields = ["categoria"]


class VideojuegoGeneroInline(TabularInline):
    """Asigna géneros del catálogo a un videojuego (tabla puente explícita)."""

    model = VideojuegoGenero
    extra = 0
    fields = ["genero"]


@admin.register(Videojuego)
class VideojuegoAdmin(ModelAdmin):
    list_display = ["titulo", "categorias_lista", "generos_lista", "activo", "creado_en"]
    list_filter = ["activo", "categorias", "generos"]
    search_fields = ["titulo", "descripcion"]
    date_hierarchy = "creado_en"
    inlines = [OfertaVideojuegoInline, VideojuegoCategoriaInline, VideojuegoGeneroInline]

    def get_queryset(self, request):
        # Evita una consulta por fila al pintar las columnas M2M.
        return super().get_queryset(request).prefetch_related("categorias", "generos")

    @admin.display(description="Categorías")
    def categorias_lista(self, obj):
        return ", ".join(categoria.nombre for categoria in obj.categorias.all())

    @admin.display(description="Géneros")
    def generos_lista(self, obj):
        return ", ".join(genero.nombre for genero in obj.generos.all())


@admin.register(OfertaVideojuego)
class OfertaVideojuegoAdmin(ModelAdmin):
    list_display = [
        "videojuego",
        "plataforma",
        "sku",
        "precio_vigente",
        "stock",
        "estado_publicacion",
    ]
    list_filter = [
        "estado_publicacion",
        "plataforma",
        "videojuego__categorias",
        "videojuego__generos",
    ]
    search_fields = ["sku", "videojuego__titulo"]
    list_editable = ["precio_vigente", "stock", "estado_publicacion"]
