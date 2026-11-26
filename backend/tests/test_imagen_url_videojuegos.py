"""Cobertura de la URL de portada guardada en cada videojuego."""
from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from catalogo.models import Videojuego
from catalogo.portadas import PORTADAS_REALES, url_portada_videojuego

pytestmark = pytest.mark.django_db


def _sembrar():
    call_command("seed_catalogo", stdout=StringIO())


def test_seed_asigna_una_url_distinta_a_cada_videojuego():
    _sembrar()

    juegos = list(Videojuego.objects.all())
    assert len(juegos) >= 100
    assert all(juego.imagen_url.startswith("/covers/reales/") for juego in juegos)
    assert set(juego.imagen_url for juego in juegos) <= set(PORTADAS_REALES.values())
    for juego in juegos:
        assert juego.imagen_url == url_portada_videojuego(juego.pk, juego.titulo)


def test_titulos_historicos_usan_su_portada_real():
    _sembrar()

    casos = {
        "God of War Ragnarök": "/covers/reales/god-of-war-ragnarok.jpg",
        "Elden Ring": "/covers/reales/elden-ring.jpg",
        "The Legend of Zelda: Tears of the Kingdom": (
            "/covers/reales/zelda-tears-of-the-kingdom.jpg"
        ),
        "Starfield": "/covers/reales/starfield.jpg",
    }
    for titulo, url in casos.items():
        assert Videojuego.objects.get(titulo=titulo).imagen_url == url


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
    assert respuesta.json()["data"]["imagen_url"] == juego.imagen_url
