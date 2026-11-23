"""Autenticación y perfil de usuario.

Se mantienen los dos mecanismos del sistema:

- Sesión/cookie de Django (el mismo que usa el sitio HTML y el admin).
- Token de DRF para clientes desacoplados (frontend, integraciones).
"""
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from ..exceptions import respuesta_exitosa
from ..throttling import (
    AnonimoRateThrottle,
    BloqueoLoginThrottle,
    LoginRateThrottle,
    RegistroRateThrottle,
    UsuarioRateThrottle,
    registrar_intento_fallido,
    reiniciar_intentos_login,
)
from ..serializers import (
    CambioPasswordSerializer,
    LoginSerializer,
    PerfilSerializer,
    RegistroSerializer,
    UsuarioSerializer,
)


def _token_de(usuario):
    token, _ = Token.objects.get_or_create(user=usuario)
    return token.key


class RegistroView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegistroRateThrottle, AnonimoRateThrottle, UsuarioRateThrottle]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        login(request, usuario)
        return respuesta_exitosa(
            {
                "usuario": UsuarioSerializer(usuario, context={"request": request}).data,
                "token": _token_de(usuario),
            },
            message="Cuenta creada exitosamente.",
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [
        BloqueoLoginThrottle,
        LoginRateThrottle,
        AnonimoRateThrottle,
        UsuarioRateThrottle,
    ]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        usuario = authenticate(
            request,
            username=username,
            password=serializer.validated_data["password"],
        )
        if usuario is None or not usuario.is_active:
            # Mensaje único: no distingue usuario inexistente de contraseña mala.
            registrar_intento_fallido(request, username)
            raise AuthenticationFailed("Usuario o contraseña incorrectos.")

        reiniciar_intentos_login(request, username)
        login(request, usuario)
        return respuesta_exitosa(
            {
                "usuario": UsuarioSerializer(usuario, context={"request": request}).data,
                "token": _token_de(usuario),
            },
            message="Sesión iniciada correctamente.",
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Si el cliente usa token, se invalida el token presentado.
        if isinstance(request.auth, Token):
            request.auth.delete()
        logout(request)
        return respuesta_exitosa(message="Sesión cerrada correctamente.")


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
