from uuid import uuid4

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from api.inventario_service import registrar_ajuste

from .models import (
    Categoria,
    ClasificacionEdad,
    Desarrolladora,
    Distribuidora,
    Genero,
    Idioma,
    OfertaVideojuego,
    Plataforma,
    Videojuego,
    VideojuegoCategoria,
    VideojuegoDesarrolladora,
    VideojuegoDistribuidora,
    VideojuegoGenero,
    VideojuegoIdioma,
)


def _aplicar_delta_stock(request, oferta_id, delta, carga_inicial=False):
    """Enruta un cambio de stock del admin por el servicio del libro mayor."""
    if delta == 0:
        return
    oferta = OfertaVideojuego.objects.get(pk=oferta_id)
    usuario = request.user if getattr(request.user, "is_authenticated", False) else None
    registrar_ajuste(
        oferta=oferta,
        cantidad=delta,
        motivo_codigo="CARGA_INICIAL" if carga_inicial else "AJUSTE_FISICO",
        usuario=usuario,
        nota=(
            "Carga inicial de stock desde el admin"
            if carga_inicial
            else "Ajuste de stock desde el admin"
        ),
        clave_idempotencia=f"admin-stock-{uuid4().hex}",
        carga_inicial=carga_inicial,
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


@admin.register(Desarrolladora)
class DesarrolladoraAdmin(ModelAdmin):
    list_display = ["nombre", "codigo", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre", "codigo"]


@admin.register(Distribuidora)
class DistribuidoraAdmin(ModelAdmin):
    list_display = ["nombre", "codigo", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre", "codigo"]


@admin.register(ClasificacionEdad)
class ClasificacionEdadAdmin(ModelAdmin):
    list_display = ["nombre", "codigo", "orden"]
    ordering = ["orden", "codigo"]
    search_fields = ["nombre", "codigo"]


@admin.register(Idioma)
class IdiomaAdmin(ModelAdmin):
    list_display = ["nombre", "codigo"]
    search_fields = ["nombre", "codigo"]


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


class VideojuegoDesarrolladoraInline(TabularInline):
    """Asigna desarrolladoras del catálogo a un videojuego (AZ-S1-20)."""

    model = VideojuegoDesarrolladora
    extra = 0
    fields = ["desarrolladora"]


class VideojuegoDistribuidoraInline(TabularInline):
    """Asigna distribuidoras del catálogo a un videojuego (AZ-S1-20)."""

    model = VideojuegoDistribuidora
    extra = 0
    fields = ["distribuidora"]


class VideojuegoIdiomaInline(TabularInline):
    """Asigna idiomas y su tipo de presencia a un videojuego (AZ-S1-20)."""

    model = VideojuegoIdioma
    extra = 0
    fields = ["idioma", "tipo"]


@admin.register(Videojuego)
class VideojuegoAdmin(ModelAdmin):
    list_display = [
        "titulo",
        "clasificacion_edad",
        "categorias_lista",
        "generos_lista",
        "activo",
        "creado_en",
    ]
    list_filter = [
        "activo",
        "clasificacion_edad",
        "categorias",
        "generos",
        "desarrolladoras",
        "distribuidoras",
    ]
    search_fields = ["titulo", "descripcion"]
    date_hierarchy = "creado_en"
    inlines = [
        OfertaVideojuegoInline,
        VideojuegoCategoriaInline,
        VideojuegoGeneroInline,
        VideojuegoDesarrolladoraInline,
        VideojuegoDistribuidoraInline,
        VideojuegoIdiomaInline,
    ]

    def get_queryset(self, request):
        # Evita una consulta por fila al pintar las columnas M2M.
        return (
            super()
            .get_queryset(request)
            .select_related("clasificacion_edad")
            .prefetch_related(
                "categorias",
                "generos",
                "desarrolladoras",
                "distribuidoras",
                "idiomas",
            )
        )

    def save_formset(self, request, form, formset, change):
        # El inline de ofertas permite editar stock: se guarda con Django y se
        # redirige el delta por el ledger para que quede un solo movimiento.
        if getattr(formset, "model", None) is not OfertaVideojuego:
            return super().save_formset(request, form, formset, change)

        anteriores = {}
        for inline_form in formset.forms:
            if inline_form.instance.pk and "stock" in (inline_form.changed_data or []):
                anteriores[inline_form.instance.pk] = (
                    OfertaVideojuego.objects.values_list("stock", flat=True).get(
                        pk=inline_form.instance.pk
                    )
                )

        super().save_formset(request, form, formset, change)

        for oferta in getattr(formset, "new_objects", []):
            if oferta.stock:
                deseado = oferta.stock
                OfertaVideojuego.objects.filter(pk=oferta.pk).update(stock=0)
                _aplicar_delta_stock(request, oferta.pk, deseado, carga_inicial=True)

        for pk, anterior in anteriores.items():
            actual = OfertaVideojuego.objects.values_list("stock", flat=True).get(pk=pk)
            if actual != anterior:
                OfertaVideojuego.objects.filter(pk=pk).update(stock=anterior)
                _aplicar_delta_stock(request, pk, actual - anterior)

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

    def save_model(self, request, obj, form, change):
        # Tanto el formulario como el list_editable pasan por aquí. Se guarda
        # el resto de campos con Django y el stock se aplica via ledger.
        if change and obj.pk:
            anterior = OfertaVideojuego.objects.values_list("stock", flat=True).get(
                pk=obj.pk
            )
            deseado = obj.stock
            if deseado != anterior:
                obj.stock = anterior
                super().save_model(request, obj, form, change)
                _aplicar_delta_stock(request, obj.pk, deseado - anterior)
                return
        elif not change and obj.stock:
            deseado = obj.stock
            obj.stock = 0
            super().save_model(request, obj, form, change)
            _aplicar_delta_stock(request, obj.pk, deseado, carga_inicial=True)
            return
        super().save_model(request, obj, form, change)
