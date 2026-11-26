"""Cobertura del seed ampliado de videojuegos (AZ-S2-BE-16)."""
import re
from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from catalogo.catalogo_real import juegos_reales
from catalogo.management.commands.seed_catalogo import (
    MINIMO_POR_CATEGORIA,
    MINIMO_VIDEOJUEGOS,
)
from catalogo.models import (
    Categoria,
    OfertaVideojuego,
    Videojuego,
    VideojuegoCategoria,
)

pytestmark = pytest.mark.django_db


def _sembrar():
    salida = StringIO()
    call_command("seed_catalogo", stdout=salida)
    return salida.getvalue()


def test_seed_alcanza_minimos_y_muestra_evidencia():
    salida = _sembrar()

    total = Videojuego.objects.count()
    objetivo = max(
        MINIMO_VIDEOJUEGOS,
        MINIMO_POR_CATEGORIA * Categoria.objects.count(),
    )
    assert total >= objetivo
    assert total >= 100
    for categoria in Categoria.objects.all():
        assert categoria.videojuegos.count() >= MINIMO_POR_CATEGORIA

    # El propio comando imprime la evidencia de total y distribución.
    assert f"Total videojuegos: {total} (mínimo {objetivo})" in salida
    for categoria in Categoria.objects.all():
        assert f"- {categoria.nombre}: {categoria.videojuegos.count()}" in salida


def test_seed_repetido_no_crea_duplicados():
    _sembrar()
    antes = {
        "videojuegos": Videojuego.objects.count(),
        "vinculos": VideojuegoCategoria.objects.count(),
        "ofertas": OfertaVideojuego.objects.count(),
    }

    salida = _sembrar()

    assert Videojuego.objects.count() == antes["videojuegos"]
    assert VideojuegoCategoria.objects.count() == antes["vinculos"]
    assert OfertaVideojuego.objects.count() == antes["ofertas"]
    assert re.search(r"Videojuegos:\s+0 creados", salida)
    assert re.search(r"Ofertas:\s+0 creadas", salida)


def test_campos_obligatorios_y_relaciones_son_validos():
    _sembrar()

    juegos = Videojuego.objects.prefetch_related(
        "vinculos_categoria", "vinculos_genero", "ofertas"
    )
    titulos = list(juegos.values_list("titulo", flat=True))
    assert len(titulos) == len(set(titulos))

    for juego in juegos:
        assert juego.titulo.strip()
        assert juego.descripcion.strip()
        assert juego.fecha_lanzamiento is not None
        assert juego.clasificacion_edad_id is not None
        assert juego.vinculos_categoria.exists()
        assert juego.vinculos_genero.exists()
        assert juego.ofertas.exists()

    pares = list(VideojuegoCategoria.objects.values_list("videojuego_id", "categoria_id"))
    assert len(pares) == len(set(pares))

    ofertas = list(
        OfertaVideojuego.objects.values_list(
            "sku", "videojuego_id", "plataforma_id", "precio_vigente"
        )
    )
    assert len(ofertas) == len({oferta[0] for oferta in ofertas})
    assert len(ofertas) == len({(oferta[1], oferta[2]) for oferta in ofertas})
    assert all(oferta[3] >= 0 for oferta in ofertas)


def test_api_devuelve_el_catalogo_sembrado():
    _sembrar()
    client = APIClient()

    respuesta = client.get("/api/v1/catalogo/videojuegos/")
    assert respuesta.status_code == 200
    assert respuesta.json()["pagination"]["count"] >= MINIMO_VIDEOJUEGOS

    categoria = Categoria.objects.order_by("nombre").first()
    filtrado = client.get(f"/api/v1/catalogo/videojuegos/?categoria={categoria.pk}")
    assert filtrado.status_code == 200
    assert filtrado.json()["pagination"]["count"] >= MINIMO_POR_CATEGORIA


def test_seed_cubre_categorias_creadas_fuera_del_seed():
    Categoria.objects.create(nombre="Simuladores de vuelo")

    _sembrar()

    extra = Categoria.objects.get(nombre="Simuladores de vuelo")
    assert extra.videojuegos.count() >= MINIMO_POR_CATEGORIA
    assert Videojuego.objects.count() >= max(
        MINIMO_VIDEOJUEGOS,
        MINIMO_POR_CATEGORIA * Categoria.objects.count(),
    )


def test_seed_repone_un_titulo_eliminado():
    titulo = juegos_reales()[0]["titulo"]
    _sembrar()
    juego = Videojuego.objects.get(titulo=titulo)
    juego.ofertas.all().delete()  # FK protegida: primero las ofertas.
    juego.delete()

    _sembrar()

    assert Videojuego.objects.filter(titulo=titulo).exists()
    assert (
        Categoria.objects.get(nombre="Acción").videojuegos.count()
        >= MINIMO_POR_CATEGORIA
    )


def test_el_catalogo_sembrado_es_realista():
    _sembrar()

    for datos in juegos_reales():
        juego = Videojuego.objects.get(titulo=datos["titulo"])
        assert juego.descripcion == datos["descripcion"]
        assert juego.descripcion.strip()
        assert juego.desarrollador == datos["desarrollador"]
        assert juego.imagen_url.startswith("/covers/reales/")
        for oferta in datos["ofertas"]:
            fila = juego.ofertas.get(plataforma__nombre=oferta["plataforma"])
            assert fila.precio_vigente >= 19900
            assert fila.stock > 0
