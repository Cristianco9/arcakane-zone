"""Vistas base de la API: raíz, healthchecks y rutas no encontradas."""
import logging

from django.db import DatabaseError, connection
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from ..exceptions import respuesta_error, respuesta_exitosa

logger = logging.getLogger(__name__)


class ApiRootView(APIView):
    """Índice navegable de los recursos disponibles en la versión 1."""

    permission_classes = [AllowAny]

    def get(self, request):
        def url(nombre):
            return reverse(nombre, request=request)

        recursos = {
            "catalogo": {
                "categorias": url("categoria-list"),
                "plataformas": url("plataforma-list"),
                "generos": url("genero-list"),
                "videojuegos": url("videojuego-list"),
                "ofertas": url("oferta-list"),
            },
            "compras": {
                "carrito": url("carrito"),
                "items_carrito": url("carrito-items"),
                "pedidos": url("pedido-list"),
                "pagos": url("pago-list"),
                "ventas": url("venta-list"),
            },
            "inventario": {
                "movimientos": url("movimiento-inventario-list"),
                "ajustes": url("inventario-ajuste"),
            },
            "cuentas": {
                "registro": url("auth-registro"),
                "login": url("auth-login"),
                "logout": url("auth-logout"),
                "perfil": url("auth-me"),
                "cambiar_password": url("auth-cambiar-password"),
                "csrf": url("auth-csrf"),
                "usuarios": url("usuario-list"),
                "roles": url("rol-list"),
            },
            "soporte": {
                "contactos": url("contacto-list"),
                "mayor_informacion": url("soporte-mayor-informacion"),
            },
            "reportes": {
                "dashboard": url("reporte-dashboard"),
                "ventas": url("reporte-ventas"),
                "inventario": url("reporte-inventario"),
                "videojuegos": url("reporte-videojuegos"),
            },
            "health": {
                "live": url("api-health"),
                "ready": url("api-health-ready"),
            },
        }
        return respuesta_exitosa(
            {"version": "v1", "recursos": recursos},
            message="API REST de Arcakane Zone",
        )


class HealthView(APIView):
    """Liveness: solo confirma que el proceso de la API está respondiendo."""

    permission_classes = [AllowAny]

    def get(self, request):
        return respuesta_exitosa({"status": "ok", "version": "v1"})


class HealthReadyView(APIView):
    """Readiness: confirma que la base de datos está disponible.

    No usa autenticación ni throttling: un fallo de BD en esos mecanismos
    convertiría el healthcheck en un 500 y ocultaría la causa real.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = []

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except DatabaseError as exc:
            logger.warning(
                "health_ready: la base de datos no responde",
                extra={"evento": "health_ready_fallo", "bd_error": str(exc)},
            )
            return respuesta_error(
                "bd_no_disponible",
                "La base de datos no está disponible.",
                status_code=503,
            )
        return respuesta_exitosa(
            {"status": "ready", "database": "ok", "version": "v1"}
        )


class ApiNotFoundView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        return JsonResponse(
            {
                "success": False,
                "error": {
                    "code": "no_encontrado",
                    "message": "El recurso solicitado no existe.",
                },
            },
            status=404,
            json_dumps_params={"ensure_ascii": False},
        )
