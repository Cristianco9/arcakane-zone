"""Portadas reales de los videojuegos del catálogo.

Los archivos viven en ``frontend/public/covers/reales`` y se sirven desde la
misma origin que la SPA. Los títulos históricos del seed tienen su portada
exacta; los títulos de relleno toman una portada real de forma determinista
según su PK.
"""

from django.utils.text import slugify

BASE_URL = "/covers/reales/"

PORTADAS_REALES = {
    "god-of-war-ragnarok": f"{BASE_URL}god-of-war-ragnarok.jpg",
    "the-legend-of-zelda-tears-of-the-kingdom": (
        f"{BASE_URL}zelda-tears-of-the-kingdom.jpg"
    ),
    "elden-ring": f"{BASE_URL}elden-ring.jpg",
    "fifa-24": f"{BASE_URL}fifa-24.jpg",
    "forza-horizon-5": f"{BASE_URL}forza-horizon-5.jpg",
    "halo-infinite": f"{BASE_URL}halo-infinite.jpg",
    "hogwarts-legacy": f"{BASE_URL}hogwarts-legacy.jpg",
    "super-mario-bros-wonder": f"{BASE_URL}super-mario-bros-wonder.png",
    "cyberpunk-2077": f"{BASE_URL}cyberpunk-2077.jpg",
    "nba-2k24": f"{BASE_URL}nba-2k24.jpg",
    "age-of-empires-iv": f"{BASE_URL}age-of-empires-iv.jpg",
    "gran-turismo-7": f"{BASE_URL}gran-turismo-7.jpg",
    "baldurs-gate-3": f"{BASE_URL}baldurs-gate-3.jpg",
    "mortal-kombat-1": f"{BASE_URL}mortal-kombat-1.jpg",
    "starfield": f"{BASE_URL}starfield.jpg",
}

_ROTACION = tuple(PORTADAS_REALES.values())


def url_portada_videojuego(pk: int, titulo: str) -> str:
    """Devuelve la URL de una portada real, estable para cada videojuego."""
    clave = slugify(titulo)
    if clave in PORTADAS_REALES:
        return PORTADAS_REALES[clave]
    return _ROTACION[(pk - 1) % len(_ROTACION)]
