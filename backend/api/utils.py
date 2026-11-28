"""Utilidades compartidas por la API."""
from datetime import datetime, time

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime


def es_administrador(usuario) -> bool:
    """Regla única de administrador usada por toda la API.

    Pasan el rol de negocio ``administrador``, ``is_staff`` e ``is_superuser``.
    Así ``TieneRol`` y las comprobaciones antiguas aplican exactamente la misma
    regla (decisión AZ-S2-BE-07).
    """
    if not usuario or not usuario.is_authenticated:
        return False
    return bool(
        usuario.is_staff
        or getattr(usuario, "is_superuser", False)
        or getattr(usuario, "es_administrador", False)
    )


def tiene_rol(usuario, *codigos) -> bool:
    """``True`` si el usuario autenticado tiene cualquiera de los códigos."""
    if not usuario or not usuario.is_authenticated or not codigos:
        return False
    return usuario.roles.filter(codigo__in=codigos).exists()


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
