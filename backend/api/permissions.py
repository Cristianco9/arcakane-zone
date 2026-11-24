"""Permisos reutilizables de la API."""
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .rbac import (
    AUTENTICADO,
    ROLES_GESTION_CATALOGO,
    ROLES_GESTION_CONTACTO,
    ROLES_GESTION_INVENTARIO,
    ROLES_LECTURA_CONTACTO,
    ROL_ADMIN,
    PUBLICO,
    regla_de_accion,
)
from .utils import es_administrador


class EsAdministrador(BasePermission):
    """Exige staff de Django o el rol de negocio ``administrador``."""

    message = "Se requiere rol de administrador."

    def has_permission(self, request, view):
        return es_administrador(request.user)


class LecturaPublicaEscrituraAdmin(BasePermission):
    """Catálogo público para consulta; solo administradores pueden modificarlo."""

    message = "Solo un administrador puede modificar este recurso."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return es_administrador(request.user)


class TieneRol(BasePermission):
    """Exige cualquiera de los roles declarados en ``roles_permitidos``.

    Los administradores (staff, superuser o rol ``administrador``) son
    superconjunto de cualquier regla. ``PUBLICO`` y ``AUTENTICADO`` también se
    aceptan como reglas, y el mapa por método/acción permite afinar cada vista.
    """

    message = "No tienes el rol necesario para realizar esta operación."
    roles_permitidos = ()

    def _regla_para(self, request, view):
        reglas = self.roles_permitidos
        if not isinstance(reglas, dict):
            return reglas

        regla = regla_de_accion(
            reglas, getattr(view, "action", None), request.method
        )
        if regla is not None:
            return regla
        return reglas.get(request.method.upper(), reglas.get("*"))

    def has_permission(self, request, view):
        regla = self._regla_para(request, view)
        if regla == PUBLICO:
            return True

        usuario = request.user
        if not usuario or not usuario.is_authenticated:
            raise NotAuthenticated("Se requiere autenticación para esta operación.")
        if es_administrador(usuario):
            return True
        if regla == AUTENTICADO:
            return True

        codigos = regla if isinstance(regla, (list, tuple, set)) else (regla,)
        if codigos and usuario.roles.filter(codigo__in=codigos).exists():
            return True
        raise PermissionDenied(self.message)


class TieneRolCatalogo(TieneRol):
    """Lectura pública; escritura para administrador o gestor de inventario."""

    roles_permitidos = {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO}


class TieneRolInventario(TieneRol):
    """Libro mayor y ajustes: administrador o gestor de inventario."""

    roles_permitidos = ROLES_GESTION_INVENTARIO


class TieneRolReporte(TieneRol):
    """Reportes administrativos."""

    roles_permitidos = ROL_ADMIN


class TieneRolReporteInventario(TieneRol):
    """El reporte de inventario también lo puede consultar el gestor."""

    roles_permitidos = ROLES_GESTION_INVENTARIO


class TieneRolContacto(TieneRol):
    """Creación pública; lectura del propietario y gestión de soporte/admin."""

    roles_permitidos = {
        "GET": ROLES_LECTURA_CONTACTO,
        "POST": PUBLICO,
        "*": ROLES_GESTION_CONTACTO,
    }

    @staticmethod
    def _puede_gestionar(usuario):
        if es_administrador(usuario):
            return True
        return usuario.roles.filter(codigo="soporte").exists()

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if self._puede_gestionar(request.user):
                return True
            return obj.usuario_id == request.user.id
        return self._puede_gestionar(request.user)


class PermisoContacto(TieneRolContacto):
    """Alias histórico usado por ``ContactoViewSet``."""


class EsPropietarioOAdministrador(BasePermission):
    """El recurso pertenece al usuario autenticado, salvo que sea administrador."""

    message = "No tienes permiso para acceder a este recurso."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if es_administrador(request.user):
            return True
        propietario_id = getattr(obj, "cliente_id", None)
        if propietario_id is None:
            propietario_id = getattr(obj, "usuario_id", None)
        return propietario_id == request.user.id
