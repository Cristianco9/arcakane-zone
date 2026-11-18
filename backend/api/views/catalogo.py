"""Recursos del catálogo: categorías, plataformas, géneros, títulos y ofertas."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny

from catalogo.models import Categoria, Genero, OfertaVideojuego, Plataforma, Videojuego

from ..exceptions import respuesta_exitosa
from ..filters import BusquedaFilter
from ..permissions import LecturaPublicaEscrituraAdmin
from ..serializers import (
    CategoriaSerializer,
    GeneroSerializer,
    OfertaVideojuegoSerializer,
    PlataformaSerializer,
    VideojuegoSerializer,
)
from ..utils import es_administrador, parse_bool


class _CatalogoBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [LecturaPublicaEscrituraAdmin]
    filter_backends = [BusquedaFilter, OrderingFilter]

    def _solo_activos_para_publico(self, queryset, campo="activo"):
        if es_administrador(self.request.user):
            valor = self.request.query_params.get(campo)
            if valor is not None:
                return queryset.filter(**{campo: parse_bool(valor)})
            return queryset
        return queryset.filter(**{campo: True})


class CategoriaViewSet(_CatalogoBaseViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre", "id"]
    ordering = ["nombre"]

    def get_queryset(self):
        return self._solo_activos_para_publico(Categoria.objects.all())


class PlataformaViewSet(_CatalogoBaseViewSet):
    queryset = Plataforma.objects.all()
    serializer_class = PlataformaSerializer
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre", "id"]
    ordering = ["nombre"]

    def get_queryset(self):
        return self._solo_activos_para_publico(Plataforma.objects.all())


class GeneroViewSet(_CatalogoBaseViewSet):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre", "id"]
    ordering = ["nombre"]

    def get_queryset(self):
        return self._solo_activos_para_publico(Genero.objects.all())


class VideojuegoViewSet(_CatalogoBaseViewSet):
    serializer_class = VideojuegoSerializer
    search_fields = ["titulo", "descripcion", "categoria__nombre", "genero__nombre"]
    ordering_fields = ["titulo", "fecha_lanzamiento", "creado_en", "id"]
    ordering = ["titulo"]

    def get_queryset(self):
        queryset = Videojuego.objects.select_related("categoria", "genero").prefetch_related(
            "ofertas__plataforma"
        )
        queryset = self._solo_activos_para_publico(queryset)

        params = self.request.query_params
        categoria = params.get("categoria")
        genero = params.get("genero")
        plataforma = params.get("plataforma")
        disponible = params.get("disponible")

        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        if genero:
            queryset = queryset.filter(genero_id=genero)
        if plataforma:
            queryset = queryset.filter(ofertas__plataforma_id=plataforma).distinct()
        if disponible is not None:
            if parse_bool(disponible):
                queryset = queryset.filter(
                    ofertas__estado_publicacion=OfertaVideojuego.EstadoPublicacion.PUBLICADO,
                    ofertas__stock__gt=0,
                ).distinct()
            else:
                queryset = queryset.exclude(
                    ofertas__estado_publicacion=OfertaVideojuego.EstadoPublicacion.PUBLICADO,
                    ofertas__stock__gt=0,
                ).distinct()
        return queryset

    @action(detail=True, methods=["get"], url_path="ofertas")
    def ofertas(self, request, pk=None):
        videojuego = self.get_object()
        ofertas = videojuego.ofertas.select_related("plataforma", "videojuego")
        if not es_administrador(request.user):
            ofertas = ofertas.publicadas().filter(videojuego__activo=True)
        ofertas = ofertas.order_by("precio_vigente")
        pagina = self.paginate_queryset(ofertas)
        if pagina is not None:
            serializer = OfertaVideojuegoSerializer(
                pagina, many=True, context=self.get_serializer_context()
            )
            return self.get_paginated_response(serializer.data)
        serializer = OfertaVideojuegoSerializer(
            ofertas, many=True, context=self.get_serializer_context()
        )
        return respuesta_exitosa(serializer.data)


class OfertaVideojuegoViewSet(_CatalogoBaseViewSet):
    serializer_class = OfertaVideojuegoSerializer
    search_fields = ["sku", "videojuego__titulo", "plataforma__nombre"]
    ordering_fields = ["precio_vigente", "stock", "creado_en", "id"]
    ordering = ["videojuego__titulo", "plataforma__nombre"]

    def get_queryset(self):
        queryset = OfertaVideojuego.objects.select_related(
            "videojuego", "videojuego__categoria", "videojuego__genero", "plataforma"
        )
        admin = es_administrador(self.request.user)

        if not admin:
            queryset = queryset.publicadas().filter(videojuego__activo=True)

        params = self.request.query_params
        videojuego = params.get("videojuego")
        plataforma = params.get("plataforma")
        categoria = params.get("categoria")
        genero = params.get("genero")
        estado = params.get("estado_publicacion")
        disponible = params.get("disponible")

        if videojuego:
            queryset = queryset.filter(videojuego_id=videojuego)
        if plataforma:
            queryset = queryset.filter(plataforma_id=plataforma)
        if categoria:
            queryset = queryset.filter(videojuego__categoria_id=categoria)
        if genero:
            queryset = queryset.filter(videojuego__genero_id=genero)
        if estado and admin:
            if estado not in OfertaVideojuego.EstadoPublicacion.values:
                raise ValidationError(
                    {
                        "estado_publicacion": (
                            "Valor inválido. Opciones: "
                            + ", ".join(OfertaVideojuego.EstadoPublicacion.values)
                        )
                    }
                )
            queryset = queryset.filter(estado_publicacion=estado)
        if disponible is not None:
            if parse_bool(disponible):
                queryset = queryset.filter(stock__gt=0)
            else:
                queryset = queryset.filter(stock=0)
        return queryset
