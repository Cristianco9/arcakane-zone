"""Utilidades compartidas por la API."""
from django.utils.dateparse import parse_date


def es_administrador(usuario) -> bool:
    """``True`` para staff de Django o para el rol de negocio ``administrador``."""
    if not usuario or not usuario.is_authenticated:
        return False
    return bool(usuario.is_staff or getattr(usuario, "es_administrador", False))


def parse_bool(valor, default=None):
    """Convierte los valores habituales de query string en booleanos."""
    if valor is None:
        return default
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() in {"1", "true", "t", "yes", "y", "si", "sí"}


def parse_fecha(valor, campo="fecha"):
    """Convierte ``YYYY-MM-DD`` en ``date`` o lanza ``ValueError``."""
    fecha = parse_date(valor)
    if fecha is None:
        raise ValueError(f"El campo '{campo}' debe tener formato YYYY-MM-DD.")
    return fecha
