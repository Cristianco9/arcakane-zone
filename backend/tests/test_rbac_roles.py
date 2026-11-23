"""Pruebas del sembrado de roles de negocio del RBAC (AZ-S2-BE-07)."""
import importlib

import pytest
from django.apps import apps
from cuentas.models import Rol

from catalogo.management.commands.seed_catalogo import Command as SeedCatalogo

pytestmark = pytest.mark.django_db

MIGRACION = importlib.import_module("cuentas.migrations.0008_roles_rbac")
CODIGOS_NUEVOS = ("gestor_inventario", "soporte")


def test_migracion_de_datos_es_idempotente():
    Rol.objects.filter(codigo__in=CODIGOS_NUEVOS).delete()

    MIGRACION.poblar_roles_rbac(apps, None)
    primera = {
        rol.codigo: (rol.nombre, rol.descripcion)
        for rol in Rol.objects.filter(codigo__in=CODIGOS_NUEVOS)
    }
    assert set(primera) == set(CODIGOS_NUEVOS)
    assert primera["gestor_inventario"][0] == "Gestor de inventario"
    assert primera["soporte"][0] == "Soporte"
    assert all(descripcion for _nombre, descripcion in primera.values())

    MIGRACION.poblar_roles_rbac(apps, None)
    segunda = {
        rol.codigo: (rol.nombre, rol.descripcion)
        for rol in Rol.objects.filter(codigo__in=CODIGOS_NUEVOS)
    }
    assert segunda == primera
    assert Rol.objects.filter(codigo__in=CODIGOS_NUEVOS).count() == 2


def test_migracion_de_datos_es_reversible_sin_usuarios_asignados():
    Rol.objects.filter(codigo__in=CODIGOS_NUEVOS).delete()
    MIGRACION.poblar_roles_rbac(apps, None)

    MIGRACION.revertir_roles_rbac(apps, None)
    assert not Rol.objects.filter(codigo__in=CODIGOS_NUEVOS).exists()


def test_reversion_aborta_si_hay_usuarios_asignados(usuario_soporte):
    MIGRACION.poblar_roles_rbac(apps, None)

    with pytest.raises(RuntimeError, match="tiene usuarios asignados"):
        MIGRACION.revertir_roles_rbac(apps, None)
    assert Rol.objects.filter(codigo="soporte").exists()


def test_seed_catalogo_siembra_los_roles_nuevos_de_forma_idempotente():
    Rol.objects.filter(codigo__in=CODIGOS_NUEVOS).delete()
    comando = SeedCatalogo()

    assert comando._seed_roles() == 2
    assert Rol.objects.filter(codigo__in=CODIGOS_NUEVOS).count() == 2

    assert comando._seed_roles() == 0
    assert Rol.objects.filter(codigo__in=CODIGOS_NUEVOS).count() == 2
    assert Rol.objects.get(codigo="soporte").nombre == "Soporte"
    assert Rol.objects.get(codigo="gestor_inventario").nombre == "Gestor de inventario"
