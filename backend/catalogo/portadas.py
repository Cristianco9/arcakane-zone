"""URLs deterministas de portada para los videojuegos del catálogo.

Cada título recibe una URL estable derivada de su clave primaria y de su
nombre. La URL se guarda en la base de datos (``Videojuego.imagen_url``) y la
interfaz la consume directamente, con una portada local como respaldo.
"""

from django.utils.text import slugify

ANCHO_PORTADA = 800
ALTO_PORTADA = 1000


def url_portada_videojuego(pk: int, titulo: str) -> str:
    """Devuelve una URL pública distinta y repetible para un videojuego."""
    semilla = slugify(f"arkane-{pk}-{titulo}") or f"arkane-{pk}"
    return f"https://picsum.photos/seed/{semilla}/{ANCHO_PORTADA}/{ALTO_PORTADA}"
