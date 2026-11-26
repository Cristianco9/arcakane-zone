"""Cobertura de las portadas reales guardadas en cada videojuego."""
from io import StringIO
from pathlib import Path

import pytest
from django.conf import settings
from django.core.management import call_command
from rest_framework.test import APIClient

from catalogo.catalogo_real import juegos_reales
from catalogo.models import Videojuego
from catalogo.portadas import PORTADAS_REALES, url_portada_videojuego

pytestmark = pytest.mark.django_db


def _sembrar():
    call_command("seed_catalogo", stdout=StringIO())


def test_seed_asigna_la_portada_real_de_cada_titulo():
    _sembrar()

    juegos = list(Videojuego.objects.all())
    assert len(juegos) >= 100
    assert all(juego.imagen_url.startswith("/covers/reales/") for juego in juegos)
    assert set(juego.imagen_url for juego in juegos) <= set(PORTADAS_REALES.values())
    for juego in juegos:
        assert juego.imagen_url == url_portada_videojuego(juego.pk, juego.titulo)


def test_cada_titulo_del_fixture_lleva_su_imagen_y_archivo_existe():
    directorio = (
        settings.BASE_DIR.parent / "frontend" / "public" / "covers" / "reales"
    )
    _sembrar()

    for datos in juegos_reales():
        juego = Videojuego.objects.get(titulo=datos["titulo"])
        assert juego.imagen_url == datos["imagen_url"]
        assert (directorio / Path(datos["imagen_url"]).name).is_file()


def test_semilla_repetida_conserva_las_urls():
    _sembrar()
    antes = dict(Videojuego.objects.values_list("id", "imagen_url"))

    _sembrar()

    assert dict(Videojuego.objects.values_list("id", "imagen_url")) == antes


def test_la_api_devuelve_la_url_de_la_portada():
    _sembrar()
    juego = Videojuego.objects.first()

    respuesta = APIClient().get(f"/api/v1/catalogo/videojuegos/{juego.pk}/")

    assert respuesta.status_code == 200
    datos = respuesta.json()["data"]
    assert datos["imagen_url"] == juego.imagen_url
    assert datos["desarrollador"] == juego.desarrollador
