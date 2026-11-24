"""Utilidades compartidas por la API."""
from datetime import datetime, time

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime


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


def parse_fecha_hora(valor, campo="fecha_hora", final=False):
    """Convierte ISO 8601 en ``datetime`` aware o lanza ``ValueError``.

    Acepta fecha y hora (``2026-01-15T10:30:00Z``) y también solo fecha, que
    se interpreta como inicio o fin de día según ``final``.
    """
    texto = str(valor or "").strip()
    if not texto:
        raise ValueError(f"El campo '{campo}' no puede estar vacío.")

    fecha = parse_datetime(texto)
    if fecha is None:
        dia = parse_date(texto)
        if dia is None:
            raise ValueError(
                f"El campo '{campo}' debe tener formato ISO 8601 "
                "(YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)."
            )
        fecha = datetime.combine(dia, time.max if final else time.min)

    if timezone.is_naive(fecha):
        fecha = timezone.make_aware(fecha, timezone.get_current_timezone())
    return fecha
