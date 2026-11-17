"""Renderer que envuelve todas las respuestas exitosas en un sobre JSON común."""
from rest_framework.renderers import JSONRenderer


class EnvelopeJSONRenderer(JSONRenderer):
    """
    Estructura de respuesta:

    - Éxito: ``{"success": true, "data": ..., "message"?: ...}``
    - Error:  ``{"success": false, "error": {...}}``

    Las respuestas que ya vienen envueltas (paginación, vistas personalizadas
    o el manejador de excepciones) se dejan intactas. Los ``204`` no llevan
    cuerpo, tal como exige HTTP.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = (renderer_context or {}).get("response")
        if response is not None and response.status_code == 204:
            return b""

        if isinstance(data, dict) and "success" in data:
            payload = data
        else:
            payload = {"success": True, "data": data}

        return super().render(payload, accepted_media_type, renderer_context)
