"""Autenticación por token propio de la API, con vencimiento."""
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import NotAuthenticated

from .models import Token


class ApiTokenAuthentication(BaseAuthentication):
    """Mismo encabezado ``Authorization: Token <clave>`` de siempre.

    Un token inexistente, vencido o de un usuario inactivo se rechaza con
    ``NotAuthenticated`` (401, ``no_autenticado``). La consulta trae el usuario
    con ``select_related`` para evitar N+1 en las vistas que lo serializan.
    """

    keyword = b"Token"

    def authenticate_header(self, request):
        """Indica a DRF que debe responder 401 (no 403) cuando falte token."""
        return "Token"

    def authenticate(self, request):
        cabecera = get_authorization_header(request).split()
        if not cabecera or cabecera[0].lower() != self.keyword.lower():
            return None
        if len(cabecera) == 1:
            raise NotAuthenticated("Falta la clave del token.")
        if len(cabecera) > 2:
            raise NotAuthenticated("Encabezado de autenticación inválido.")
        try:
            clave = cabecera[1].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise NotAuthenticated("Token inválido.") from exc

        token = (
            Token.objects.select_related("usuario")
            .filter(
                key_hash=Token.hash_clave(clave),
                expira_en__gt=timezone.now(),
            )
            .first()
        )
        if token is None:
            raise NotAuthenticated("Token inválido o vencido.")
        if not token.usuario.is_active:
            raise NotAuthenticated("La cuenta está desactivada.")
        return token.usuario, token
