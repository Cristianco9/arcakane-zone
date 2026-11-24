"""Reglas de negocio y auditoría de usuarios/roles (AZ-S2-BE-08).

Las vistas administrativas delegan aquí las operaciones de escritura para que
las protecciones (autodesactivación, último administrador y jerarquía de roles)
se apliquen también cuando el servicio se llama desde otro punto del proyecto.
"""
import logging

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, ValidationError

from cuentas.models import AuditoriaCuenta, Rol, Usuario, UsuarioRol

from .exceptions import ErrorDeNegocio
from .rbac import JERARQUIA_ROLES
from .utils import es_administrador

logger = logging.getLogger(__name__)

# Roles base creados por las migraciones iniciales: no se pueden eliminar.
ROLES_BASE = frozenset({"cliente", "administrador"})


def _codigos_roles(usuario):
    return list(usuario.roles.order_by("codigo").values_list("codigo", flat=True))


def _nivel_del_actor(actor):
    """Nivel jerárquico del actor; staff/superuser equivalen a administrador."""
    if actor is not None and es_administrador(actor):
        return JERARQUIA_ROLES["administrador"]
    if actor is None:
        return JERARQUIA_ROLES["administrador"]  # operación interna del sistema
    return max(
        (JERARQUIA_ROLES.get(codigo, 0) for codigo in _codigos_roles(actor)),
        default=0,
    )


def _validar_roles(actor, roles):
    roles = list(roles)
    if not roles:
        raise ValidationError({"roles": "Debe asignar al menos un rol."})

    nivel_actor = _nivel_del_actor(actor)
    for rol in roles:
        if not rol.activo:
            raise ValidationError(
                {"roles": f"El rol '{rol.codigo}' no está activo."}
            )
        if JERARQUIA_ROLES.get(rol.codigo, 0) > nivel_actor:
            raise PermissionDenied(
                f"No puedes asignar el rol '{rol.codigo}' por encima de tu propio rol."
            )
    return roles


def _es_administrador_activo(usuario):
    return bool(usuario.is_active and es_administrador(usuario))


def _hay_otros_administradores(usuario):
    return (
        Usuario.objects.filter(is_active=True)
        .exclude(pk=usuario.pk)
        .filter(
            Q(is_staff=True)
            | Q(is_superuser=True)
            | Q(roles__codigo="administrador")
        )
        .distinct()
        .exists()
    )


def _validar_ultimo_administrador(usuario, is_active, roles):
    """Impide dejar el sistema sin ningún administrador activo."""
    if not _es_administrador_activo(usuario):
        return

    sigue_siendo_admin = bool(
        is_active
        and (
            usuario.is_staff
            or usuario.is_superuser
            or any(rol.codigo == "administrador" for rol in roles)
        )
    )
    if not sigue_siendo_admin and not _hay_otros_administradores(usuario):
        raise ErrorDeNegocio(
            "No se puede desactivar ni quitar el rol de administrador al "
            "último administrador activo."
        )


def _validar_no_autodesactivacion(actor, usuario, is_active):
    if (
        actor is not None
        and actor.pk == usuario.pk
        and is_active is False
    ):
        raise ErrorDeNegocio("No puedes desactivar tu propia cuenta.")


def _registrar(antes, despues):
    return {"antes": antes, "despues": despues}


def _auditar(actor, accion, usuario=None, rol=None, detalles=None, ip=None):
    registro = AuditoriaCuenta.objects.create(
        usuario_afectado=usuario,
        actor=actor,
        accion=accion,
        detalles=detalles or {},
        direccion_ip=ip or None,
    )
    objetivo = usuario.username if usuario else (rol.codigo if rol else "sistema")
    logger.info(
        "auditoria_cuentas accion=%s objetivo=%s actor=%s ip=%s fecha=%s",
        accion,
        objetivo,
        actor.username if actor else "sistema",
        ip or "-",
        registro.fecha_hora.isoformat(),
    )
    return registro


def crear_usuario(actor, datos, roles, password, ip=None):
    """Crea un usuario interno con contraseña y al menos un rol."""
    roles = _validar_roles(actor, roles)

    with transaction.atomic():
        usuario = Usuario(**datos)
        try:
            password_validation.validate_password(password, usuario)
        except DjangoValidationError as exc:
            raise ValidationError({"password": list(exc.messages)}) from exc

        usuario.set_password(password)
        usuario.save()
        usuario.roles.set(roles)

        _auditar(
            actor,
            "usuario_creado",
            usuario=usuario,
            detalles={
                "username": usuario.username,
                "roles": [rol.codigo for rol in sorted(roles, key=lambda r: r.codigo)],
                "is_active": usuario.is_active,
            },
            ip=ip,
        )
    return usuario


def actualizar_usuario(actor, usuario, datos, roles=None, ip=None):
    """Actualiza datos, roles y/o estado de un usuario ya existente."""
    campos_editables = (
        "username",
        "email",
        "first_name",
        "last_name",
        "telefono",
        "direccion",
        "is_active",
    )
    with transaction.atomic():
        objetivo = Usuario.objects.select_for_update().get(pk=usuario.pk)
        anteriores = {campo: getattr(objetivo, campo) for campo in campos_editables}
        roles_anteriores = _codigos_roles(objetivo)

        roles_finales = (
            _validar_roles(actor, roles) if roles is not None else list(objetivo.roles.all())
        )
        is_active_final = datos.get("is_active", objetivo.is_active)

        _validar_no_autodesactivacion(actor, objetivo, is_active_final)
        _validar_ultimo_administrador(
            objetivo, is_active=is_active_final, roles=roles_finales
        )

        cambios = {}
        for campo in campos_editables:
            if campo in datos and datos[campo] != anteriores[campo]:
                setattr(objetivo, campo, datos[campo])
                cambios[campo] = _registrar(anteriores[campo], datos[campo])
        if cambios:
            objetivo.save(update_fields=list(cambios))

        roles_nuevos = sorted(rol.codigo for rol in roles_finales)
        cambios_roles = roles_anteriores != roles_nuevos
        if cambios_roles:
            objetivo.roles.set(roles_finales)

        if not cambios and not cambios_roles:
            return objetivo

        if is_active_final is False and cambios.get("is_active"):
            accion = "usuario_desactivado"
        elif is_active_final is True and cambios.get("is_active"):
            accion = "usuario_activado"
        elif cambios_roles:
            accion = "roles_actualizados"
        else:
            accion = "usuario_actualizado"

        detalles = {}
        if cambios:
            detalles["datos"] = cambios
        if cambios_roles:
            detalles["roles"] = _registrar(roles_anteriores, roles_nuevos)
        _auditar(actor, accion, usuario=objetivo, detalles=detalles, ip=ip)
    return objetivo


def cambiar_estado_usuario(actor, usuario, activar, ip=None):
    """Activa o desactiva una cuenta y deja constancia del cambio."""
    with transaction.atomic():
        objetivo = Usuario.objects.select_for_update().get(pk=usuario.pk)
        is_active_final = bool(activar)
        _validar_no_autodesactivacion(actor, objetivo, is_active_final)
        _validar_ultimo_administrador(
            objetivo,
            is_active=is_active_final,
            roles=list(objetivo.roles.all()),
        )

        if objetivo.is_active == is_active_final:
            return objetivo

        anterior = objetivo.is_active
        objetivo.is_active = is_active_final
        objetivo.save(update_fields=["is_active"])
        _auditar(
            actor,
            "usuario_activado" if activar else "usuario_desactivado",
            usuario=objetivo,
            detalles={"is_active": _registrar(anterior, is_active_final)},
            ip=ip,
        )
    return objetivo


def crear_rol(actor, datos, ip=None):
    """Crea un rol de negocio."""
    with transaction.atomic():
        rol = Rol.objects.create(**datos)
        _auditar(
            actor,
            "rol_creado",
            rol=rol,
            detalles={"codigo": rol.codigo, "nombre": rol.nombre},
            ip=ip,
        )
    return rol


def actualizar_rol(actor, rol, datos, ip=None):
    """Actualiza la etiqueta, descripción o estado de un rol."""
    with transaction.atomic():
        objetivo = Rol.objects.select_for_update().get(pk=rol.pk)
        cambios = {}
        for campo in ("codigo", "nombre", "descripcion", "activo"):
            if campo in datos and datos[campo] != getattr(objetivo, campo):
                cambios[campo] = _registrar(getattr(objetivo, campo), datos[campo])
                setattr(objetivo, campo, datos[campo])
        if cambios:
            objetivo.save(update_fields=list(cambios))
            _auditar(
                actor,
                "rol_actualizado",
                rol=objetivo,
                detalles=cambios,
                ip=ip,
            )
    return objetivo


def eliminar_rol(actor, rol, ip=None):
    """Elimina un rol siempre que no esté en uso ni sea un rol base."""
    with transaction.atomic():
        objetivo = Rol.objects.select_for_update().get(pk=rol.pk)
        if objetivo.codigo in ROLES_BASE:
            raise ErrorDeNegocio(
                f"El rol base '{objetivo.codigo}' no se puede eliminar."
            )
        if UsuarioRol.objects.filter(rol=objetivo).exists():
            raise ErrorDeNegocio(
                f"No se puede eliminar el rol '{objetivo.codigo}' porque tiene "
                "usuarios asignados."
            )

        codigo = objetivo.codigo
        nombre = objetivo.nombre
        objetivo.delete()
        _auditar(
            actor,
            "rol_eliminado",
            detalles={"codigo": codigo, "nombre": nombre},
            ip=ip,
        )
