"""URLs de portada reales y estables para los videojuegos del catálogo.

Cada título del fixture tiene su propia imagen descargada en
``frontend/public/covers/reales``. La URL se guarda en
``Videojuego.imagen_url`` y la SPA la consume directamente.
"""

from __future__ import annotations

from django.utils.text import slugify

from catalogo.catalogo_real import indice_portadas, juegos_reales

PORTADAS_REALES = dict(indice_portadas())
_ROTACION = tuple(dict.fromkeys(juego["imagen_url"] for juego in juegos_reales()))


def url_portada_videojuego(pk: int, titulo: str) -> str:
    """Devuelve la portada exacta del título, o una real por PK si no está."""
    return PORTADAS_REALES.get(
        slugify(titulo), _ROTACION[(pk - 1) % len(_ROTACION)]
    )
