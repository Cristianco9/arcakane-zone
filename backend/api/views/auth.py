"""Autenticación y perfil de usuario.

Se mantienen los dos mecanismos del sistema:

- Sesión/cookie de Django (el mismo que usa el sitio HTML y el admin).
- Token propio de la API, con vencimiento, para clientes desacoplados.
"""
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from ..exceptions import respuesta_exitosa
from ..models import Token
from ..serializers import (
    CambioPasswordSerializer,
    LoginSerializer,
    PerfilSerializer,
    RegistroSerializer,
    UsuarioSerializer,
)


def _emitir_token(usuario):
    """Devuelve los datos aditivos de un token recién emitido."""
    token, clave = Token.emitir(usuario)
    return {"token": clave, "expires_at": token.expira_en.isoformat()}


class RegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        login(request, usuario)
        return respuesta_exitosa(
            {
                "usuario": UsuarioSerializer(usuario, context={"request": request}).data,
                **_emitir_token(usuario),
            },
            message="Cuenta creada exitosamente.",
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if usuario is None:
            raise AuthenticationFailed("Usuario o contraseña incorrectos.")
        if not usuario.is_active:
            raise AuthenticationFailed("La cuenta está desactivada.")

        login(request, usuario)
        return respuesta_exitosa(
            {
                "usuario": UsuarioSerializer(usuario, context={"request": request}).data,
                **_emitir_token(usuario),
            },
            message="Sesión iniciada correctamente.",
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Revoca solo el token usado en esta petición; no los demás.
        if isinstance(request.auth, Token):
            request.auth.delete()
        logout(request)
        return respuesta_exitosa(message="Sesión cerrada correctamente.")


class TokenRefreshView(APIView):
    """Rota el token vigente usado en la petición."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.auth, Token):
            raise NotAuthenticated("Se requiere un token de API vigente.")
        request.auth.delete()
        return respuesta_exitosa(
            _emitir_token(request.user), message="Token renovado correctamente."
        )


class LogoutAllView(APIView):
    """Revoca todos los tokens del usuario, en cualquier dispositivo."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(usuario=request.user).delete()
        logout(request)
        return respuesta_exitosa(
            message="Sesiones cerradas en todos los dispositivos."
        )


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    """Entrega la cookie ``csrftoken`` para clientes que usan sesión."""

    permission_classes = [AllowAny]

    def get(self, request):
        return respuesta_exitosa({"csrfToken": get_token(request)})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return respuesta_exitosa(
            PerfilSerializer(request.user, context={"request": request}).data
        )

    def patch(self, request):
        serializer = PerfilSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return respuesta_exitosa(
            serializer.data, message="Perfil actualizado correctamente."
        )

    def put(self, request):
        serializer = PerfilSerializer(
            request.user, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return respuesta_exitosa(
            serializer.data, message="Perfil actualizado correctamente."
        )


class CambioPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CambioPasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        return respuesta_exitosa(message="Contraseña actualizada correctamente.")
