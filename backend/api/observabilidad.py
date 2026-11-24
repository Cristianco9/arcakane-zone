"""Contexto y formateadores de observabilidad de la API (AZ-S2-BE-09).

El ``request_id`` viaja en la cabecera ``X-Request-ID`` y se guarda en un
``ContextVar`` para que cualquier log emitido durante la petición lo incluya,
incluso los errores 500. Los formateadores no dependen de paquetes externos: en
producción escriben JSON en stdout y en desarrollo un texto legible.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from contextvars import ContextVar, Token
from datetime import datetime, timezone

CAMPOS_CONTEXTUALES = (
    "request_id",
    "metodo",
    "ruta",
    "status_code",
    "duracion_ms",
    "usuario_id",
    "ip",
)

_request_id = ContextVar("arkane_zone_request_id", default="-")
_contexto = ContextVar("arkane_zone_request_contexto", default={})

_CABECERA_PERMITIDA = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")


def nuevo_request_id(cabecera: str | None = None) -> str:
    """Reutiliza un ``X-Request-ID`` válido o genera uno nuevo."""
    valor = (cabecera or "").strip()
    if _CABECERA_PERMITIDA.fullmatch(valor):
        return valor
    return str(uuid.uuid4())


def activar_contexto(request_id: str, **contexto) -> list[tuple[ContextVar, Token]]:
    """Activa el contexto de la petición y devuelve los tokens a restaurar."""
    datos = {"request_id": request_id, **contexto}
    return [
        (_request_id, _request_id.set(request_id)),
        (_contexto, _contexto.set(datos)),
    ]


def desactivar_contexto(tokens: list[tuple[ContextVar, Token]]) -> None:
    """Restaura el contexto anterior para no filtrar datos entre peticiones."""
    for variable, token in reversed(tokens):
        variable.reset(token)


def request_id_actual() -> str:
    return _request_id.get()


def contexto_actual() -> dict:
    return {**_contexto.get(), "request_id": _request_id.get()}


class RequestContextFilter(logging.Filter):
    """Inyecta el contexto de la petición en todos los ``LogRecord``."""

    def filter(self, record: logging.LogRecord) -> bool:
        for clave, valor in contexto_actual().items():
            if not hasattr(record, clave):
                setattr(record, clave, valor)

        peticion = getattr(record, "request", None)
        if peticion is not None:
            if not hasattr(record, "metodo"):
                record.metodo = getattr(peticion, "method", None)
            if not hasattr(record, "ruta"):
                record.ruta = getattr(peticion, "path", None)
            if not hasattr(record, "status_code"):
                record.status_code = getattr(record, "status_code", None)
            usuario = getattr(peticion, "user", None)
            if usuario is not None and getattr(usuario, "is_authenticated", False):
                record.usuario_id = getattr(usuario, "pk", None)
            if not hasattr(record, "ip"):
                record.ip = getattr(peticion, "META", {}).get("REMOTE_ADDR")
        return True


class JsonFormatter(logging.Formatter):
    """Un registro por línea, con los campos de contexto en el mismo objeto."""

    _BASE = set(logging.makeLogRecord({}).__dict__) | {
        "message",
        "asctime",
        "request",
        "exc_info",
        "exc_text",
        "stack_info",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for campo in CAMPOS_CONTEXTUALES:
            if hasattr(record, campo):
                payload[campo] = getattr(record, campo)

        # Campos enviados con ``extra=`` (por ejemplo ``evento`` o ``bd_error``).
        for clave, valor in record.__dict__.items():
            if clave in self._BASE or clave in CAMPOS_CONTEXTUALES or clave.startswith("_"):
                continue
            if isinstance(valor, (str, int, float, bool, type(None))):
                payload[clave] = valor
            else:
                payload[clave] = str(valor)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        elif record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        return json.dumps(payload, ensure_ascii=False)


class TextoFormatter(logging.Formatter):
    """Formato legible para desarrollo, también con ``request_id``."""

    def __init__(self) -> None:
        super().__init__(
            "%(asctime)s %(levelname)-8s [%(request_id)s] %(name)s: %(message)s"
        )

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "request_id"):
            record.request_id = request_id_actual()
        return super().format(record)
