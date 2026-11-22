"""Permisos reutilizables de la API."""
from rest_framework.permissions import SAFE_METHODS, BasePermission

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
        if request.method in SAFE_METHODS:
            return es_administrador(request.user) or obj.usuario_id == request.user.id
        return es_administrador(request.user)
