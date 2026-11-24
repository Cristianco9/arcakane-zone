"""Respuestas JSON incluso para errores y contexto de trazabilidad por API."""
import logging
import time

from django.http import JsonResponse

from .observabilidad import (
    activar_contexto,
    desactivar_contexto,
    nuevo_request_id,
    request_id_actual,
)

logger = logging.getLogger(__name__)

API_PREFIX = "/api/"


def _ip(request):
    return request.META.get("REMOTE_ADDR")


def _usuario_id(request):
    usuario = getattr(request, "user", None)
    if usuario is not None and getattr(usuario, "is_authenticated", False):
        return getattr(usuario, "pk", None)
    return None


class RequestIdMiddleware:
    """Asigna un ``request_id`` a cada petición de la API y lo devuelve.

    El identificador se propaga a los logs mediante el contexto de
    ``api.observabilidad``, de modo que un 500 pueda correlacionarse con la
    petición que lo provocó. Debe ser el primer middleware de la cadena.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(API_PREFIX):
            return self.get_response(request)

        identificador = nuevo_request_id(request.META.get("HTTP_X_REQUEST_ID"))
        tokens = activar_contexto(
            identificador,
            metodo=request.method,
            ruta=request.path,
            ip=_ip(request),
            usuario_id=_usuario_id(request),
        )
        inicio = time.perf_counter()
        respuesta = None
        try:
            respuesta = self.get_response(request)
            respuesta["X-Request-ID"] = identificador
            return respuesta
        except Exception:
            logger.exception(
                "Error no controlado antes de responder %s %s",
                request.method,
                request.path,
                extra={
                    "evento": "api_error_no_controlado",
                    "request_id": identificador,
                    "metodo": request.method,
                    "ruta": request.path,
                    "status_code": 500,
                },
            )
            raise
        finally:
            estado = getattr(respuesta, "status_code", 500)
            datos = {
                "evento": "api_request",
                "request_id": identificador,
                "metodo": request.method,
                "ruta": request.path,
                "status_code": estado,
                "duracion_ms": round((time.perf_counter() - inicio) * 1000, 2),
                "ip": _ip(request),
                "usuario_id": _usuario_id(request),
            }
            if estado >= 500:
                logger.error("api_request_fallida", extra=datos)
            else:
                logger.debug("api_request_completada", extra=datos)
            desactivar_contexto(tokens)


class ApiErrorMiddleware:
    """
    Garantiza que cualquier error bajo ``/api/`` tenga el mismo sobre JSON.

    DRF ya maneja sus propias excepciones; este middleware cubre rutas
    inexistentes, errores de middleware y fallos inesperados fuera del ciclo
    de una vista DRF.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(API_PREFIX):
            return self.get_response(request)

        try:
            response = self.get_response(request)
        except Exception:
            logger.exception(
                "Error no controlado en %s %s",
                request.method,
                request.path,
                extra={
                    "evento": "api_error_no_controlado",
                    "request_id": request_id_actual(),
                    "metodo": request.method,
                    "ruta": request.path,
                    "status_code": 500,
                    "ip": _ip(request),
                    "usuario_id": _usuario_id(request),
                },
            )
            return self._json(
                "error_interno",
                "Ocurrió un error interno al procesar la solicitud.",
                500,
            )

        content_type = response.get("Content-Type", "")
        if (
            response.status_code in {403, 404, 405}
            and not content_type.startswith("application/json")
        ):
            codigo, mensaje = {
                403: ("permiso_denegado", "No tienes permiso para realizar esta operación."),
                404: ("no_encontrado", "El recurso solicitado no existe."),
                405: ("metodo_no_permitido", "El método HTTP no está permitido para este recurso."),
            }[response.status_code]
            convertida = self._json(codigo, mensaje, response.status_code)
            if response.has_header("Allow"):
                convertida["Allow"] = response["Allow"]
            return convertida

        return response

    @staticmethod
    def _json(codigo, mensaje, status_code):
        return JsonResponse(
            {"success": False, "error": {"code": codigo, "message": mensaje}},
            status=status_code,
            json_dumps_params={"ensure_ascii": False},
        )
