"""Administración de usuarios y roles por API (AZ-S2-BE-08)."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from cuentas.models import AuditoriaCuenta, Rol, Usuario

from ..cuentas_service import (
    actualizar_rol,
    actualizar_usuario,
    cambiar_estado_usuario,
    crear_rol,
    crear_usuario,
    eliminar_rol,
)
from ..exceptions import respuesta_exitosa
from ..filters import BusquedaFilter
from ..permissions import EsAdministrador
from ..serializers import (
    AuditoriaCuentaSerializer,
    RolAdminSerializer,
    RolSerializer,
    UsuarioAdminCreateSerializer,
    UsuarioAdminUpdateSerializer,
    UsuarioSerializer,
)
from ..utils import parse_bool


def _ip(request):
    return request.META.get("REMOTE_ADDR")


class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    permission_classes = [EsAdministrador]
    # No se exponen bajas de usuarios: se desactivan para conservar el historial.
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    filter_backends = [BusquedaFilter, OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "date_joined", "id"]
    ordering = ["username"]

    def get_queryset(self):
        queryset = Usuario.objects.prefetch_related("roles")
        params = self.request.query_params
        if params.get("rol"):
            queryset = queryset.filter(roles__id=params["rol"]).distinct()
        if params.get("activo") is not None:
            queryset = queryset.filter(is_active=parse_bool(params.get("activo")))
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioAdminCreateSerializer
        if self.action in ("update", "partial_update"):
            return UsuarioAdminUpdateSerializer
        if self.action == "auditoria":
            return AuditoriaCuentaSerializer
        return UsuarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        usuario = crear_usuario(
            actor=request.user,
            datos={
                campo: datos[campo]
                for campo in (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "telefono",
                    "direccion",
                )
                if campo in datos
            },
            roles=datos["roles"],
            password=datos["password"],
            ip=_ip(request),
        )
        return respuesta_exitosa(
            UsuarioSerializer(usuario, context=self.get_serializer_context()).data,
            message="Usuario creado correctamente.",
            status_code=status.HTTP_201_CREATED,
        )

    def _actualizar(self, request, partial, *args, **kwargs):
        usuario = self.get_object()
        serializer = self.get_serializer(
            usuario, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        actualizado = actualizar_usuario(
            actor=request.user,
            usuario=usuario,
            datos={
                campo: datos[campo]
                for campo in (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "telefono",
                    "direccion",
                    "is_active",
                )
                if campo in datos
            },
            roles=datos.get("roles"),
            ip=_ip(request),
        )
        return respuesta_exitosa(
            UsuarioSerializer(
                actualizado, context=self.get_serializer_context()
            ).data,
            message="Usuario actualizado correctamente.",
        )

    def update(self, request, *args, **kwargs):
        return self._actualizar(request, partial=False, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self._actualizar(request, partial=True, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="activar")
    def activar(self, request, pk=None):
        usuario = cambiar_estado_usuario(
            actor=request.user,
            usuario=self.get_object(),
            activar=True,
            ip=_ip(request),
        )
        return respuesta_exitosa(
            UsuarioSerializer(usuario, context=self.get_serializer_context()).data,
            message="Usuario activado correctamente.",
        )

    @action(detail=True, methods=["post"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        usuario = cambiar_estado_usuario(
            actor=request.user,
            usuario=self.get_object(),
            activar=False,
            ip=_ip(request),
        )
        return respuesta_exitosa(
            UsuarioSerializer(usuario, context=self.get_serializer_context()).data,
            message="Usuario desactivado correctamente.",
        )

    @action(detail=True, methods=["get"], url_path="auditoria")
    def auditoria(self, request, pk=None):
        usuario = self.get_object()
        queryset = AuditoriaCuenta.objects.filter(usuario_afectado=usuario)
        pagina = self.paginate_queryset(queryset)
        serializer = self.get_serializer(pagina or queryset, many=True)
        if pagina is not None:
            return self.get_paginated_response(serializer.data)
        return respuesta_exitosa(serializer.data)


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all().order_by("nombre")
    serializer_class = RolSerializer
    permission_classes = [EsAdministrador]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RolAdminSerializer
        return RolSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rol = crear_rol(
            actor=request.user,
            datos=serializer.validated_data,
            ip=_ip(request),
        )
        return respuesta_exitosa(
            RolAdminSerializer(rol, context=self.get_serializer_context()).data,
            message="Rol creado correctamente.",
            status_code=status.HTTP_201_CREATED,
        )

    def _actualizar(self, request, partial, *args, **kwargs):
        rol = self.get_object()
        serializer = self.get_serializer(rol, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        actualizado = actualizar_rol(
            actor=request.user,
            rol=rol,
            datos=serializer.validated_data,
            ip=_ip(request),
        )
        return respuesta_exitosa(
            RolAdminSerializer(
                actualizado, context=self.get_serializer_context()
            ).data,
            message="Rol actualizado correctamente.",
        )

    def update(self, request, *args, **kwargs):
        return self._actualizar(request, partial=False, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self._actualizar(request, partial=True, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        eliminar_rol(
            actor=request.user,
            rol=self.get_object(),
            ip=_ip(request),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
