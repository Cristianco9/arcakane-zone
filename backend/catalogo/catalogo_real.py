"""Fixture del catálogo realista usado por ``seed_catalogo``.

Los datos se obtuvieron de la tienda de Steam (título, desarrollador, fecha,
precio y portada) y de Wikipedia en español (ficha descriptiva). Se guardan en
el repositorio para que el seed sea determinista y no dependa de servicios
externos al arrancar el contenedor.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

RUTA_FIXTURE = Path(__file__).resolve().parent / "datos" / "catalogo_real.json"


@lru_cache(maxsize=1)
def juegos_reales() -> tuple[dict, ...]:
    """Devuelve los 140 títulos reales del catálogo de demostración."""
    datos = json.loads(RUTA_FIXTURE.read_text(encoding="utf-8"))
    return tuple(datos)


@lru_cache(maxsize=1)
def indice_portadas() -> dict[str, str]:
    """Mapa de título normalizado a URL de portada local."""
    from django.utils.text import slugify

    return {
        slugify(juego["titulo"]): juego["imagen_url"] for juego in juegos_reales()
    }
