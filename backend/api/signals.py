"""Revocación de tokens cuando cambia la contraseña del usuario.

Cubre la API, el formulario web, el reseteo de Django y el admin sin tocar la
app ``cuentas``: todos esos caminos terminan en ``User.save()`` con el campo
``password`` modificado.

Nota: si Django vuelve a hashear la contraseña al iniciar sesión (cambio de
algoritmo), esta señal revoca los tokens anteriores. El login emite el token
nuevo después de autenticar, así que ese token sigue siendo válido.
"""
from django.apps import apps
from django.conf import settings
from django.db.models.signals import post_init, pre_save

from .models import Token

_PASSWORD_ORIGINAL = "_api_password_original"


def guardar_password_original(sender, instance, **kwargs):
    """Recuerda el hash con el que se cargó la instancia."""
    setattr(instance, _PASSWORD_ORIGINAL, instance.password)


def revocar_tokens_si_password_cambia(sender, instance, update_fields=None, **kwargs):
    """Borra los tokens del usuario cuando su hash de contraseña cambia."""
    if instance._state.adding:
        # Registro: todavía no puede haber tokens para este usuario.
        setattr(instance, _PASSWORD_ORIGINAL, instance.password)
        return

    campos = set(update_fields) if update_fields is not None else None
    if campos is not None and "password" not in campos:
        return

    original = getattr(instance, _PASSWORD_ORIGINAL, None)
    if original is None:
        # Instancias construidas a mano con pk: fallback a la base de datos.
        original = (
            sender._default_manager.filter(pk=instance.pk)
            .values_list("password", flat=True)
            .first()
        )
    if original is not None and original != instance.password:
        Token.objects.filter(usuario=instance).delete()

    setattr(instance, _PASSWORD_ORIGINAL, instance.password)


def conectar():
    """Registra las señales sobre el modelo de usuario configurable."""
    usuario = apps.get_model(settings.AUTH_USER_MODEL)
    post_init.connect(
        guardar_password_original,
        sender=usuario,
        dispatch_uid="api.password.original",
    )
    pre_save.connect(
        revocar_tokens_si_password_cambia,
        sender=usuario,
        dispatch_uid="api.password.revocar_tokens",
    )
