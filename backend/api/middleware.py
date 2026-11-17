"""Respuestas JSON incluso para errores que no pasan por una vista DRF."""
import logging

from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)

API_PREFIX = "/api/"


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
            logger.exception("Error no controlado en %s %s", request.method, request.path)
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
