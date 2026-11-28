"""Permisos reutilizables de la API."""
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .rbac import AUTENTICADO, PUBLICO, REGLAS, ROL_SOPORTE, regla_de_accion
from .utils import es_administrador, tiene_rol


class TieneRol(BasePermission):
    """Permite el acceso según los roles declarados en ``api/rbac.py``.

    ``roles_permitidos`` admite una lista (todos los métodos) o un mapa por
    método HTTP y/o acción de ViewSet. Los centinelas ``PUBLICO`` y
    ``AUTENTICADO`` declaran políticas sin roles. Anónimo sin sesión responde
    401 ``no_autenticado``; autenticado sin el rol responde 403
    ``permiso_denegado``. El rol ``administrador``, ``is_staff`` e
    ``is_superuser`` pasan siempre porque usan la misma regla que
    ``api.utils.es_administrador``.
    """

    message = "No tienes permiso para realizar esta operación."
    roles_permitidos = ()

    def _regla_para(self, request, view):
        reglas = self.roles_permitidos
        if isinstance(reglas, str):
            return reglas
        if isinstance(reglas, dict):
            accion = getattr(view, "action", None)
            regla_accion = regla_de_accion(reglas, accion, request.method)
            if regla_accion is not None:
                return regla_accion
            metodo = request.method.upper()
            if metodo in reglas:
                return reglas[metodo]
            return reglas.get("*", ())
        return reglas

    def has_permission(self, request, view):
        regla = self._regla_para(request, view)
        if regla == PUBLICO:
            return True

        usuario = request.user
        if not usuario or not usuario.is_authenticated:
            raise NotAuthenticated("Se requiere autenticación para realizar esta operación.")

        if regla == AUTENTICADO:
            return True
        if es_administrador(usuario):
            return True

        codigos = tuple(regla or ())
        if codigos and tiene_rol(usuario, *codigos):
            return True
        raise PermissionDenied(self.message)


class TieneRolCatalogo(TieneRol):
    roles_permitidos = REGLAS["catalogo"]


class TieneRolInventario(TieneRol):
    roles_permitidos = REGLAS["inventario"]


class TieneRolContacto(TieneRol):
    roles_permitidos = REGLAS["contactos"]


class TieneRolReporte(TieneRol):
    roles_permitidos = REGLAS["reportes"]


class TieneRolReporteInventario(TieneRol):
    roles_permitidos = REGLAS["reporte_inventario"]


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


class PermisoContacto(BasePermission):
    """
    Cualquiera puede crear un mensaje de contacto.
    Los usuarios autenticados solo ven los suyos; el staff ve y modifica todos.
    """

    message = "No tienes permiso para acceder a este recurso."

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        gestiona = es_administrador(request.user) or tiene_rol(request.user, ROL_SOPORTE)
        if request.method in SAFE_METHODS:
            return gestiona or obj.usuario_id == request.user.id
        return gestiona
