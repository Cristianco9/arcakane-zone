"""Administración de usuarios y roles por API (AZ-S2-BE-08)."""
import pytest
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIClient

from api.cuentas_service import cambiar_estado_usuario, crear_usuario
from api.exceptions import ErrorDeNegocio
from cuentas.models import AuditoriaCuenta, Rol, Usuario

pytestmark = pytest.mark.django_db

PASSWORD = "ClaveSegura#2026"
USUARIOS_URL = "/api/v1/usuarios/"
ROLES_URL = "/api/v1/roles/"


def _auth(usuario):
    cliente = APIClient()
    cliente.force_authenticate(usuario)
    return cliente


def _nuevo_usuario(**extra):
    datos = {
        "username": "nuevo_interno",
        "email": "nuevo@test.com",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
    }
    datos.update(extra)
    return datos


# ── Alta de usuarios ─────────────────────────────────────────────────────────


def test_admin_crea_usuario_con_rol_y_queda_auditado(usuario_admin, rol_soporte):
    respuesta = _auth(usuario_admin).post(
        USUARIOS_URL,
        _nuevo_usuario(roles=[rol_soporte.pk]),
        format="json",
    )

    assert respuesta.status_code == 201, respuesta.json()
    data = respuesta.json()["data"]
    assert data["username"] == "nuevo_interno"
    assert data["roles"] == [rol_soporte.pk]
    assert data["is_active"] is True

    usuario = Usuario.objects.get(username="nuevo_interno")
    assert usuario.check_password(PASSWORD)
    assert list(usuario.roles.all()) == [rol_soporte]

    auditoria = AuditoriaCuenta.objects.get(
        accion="usuario_creado", usuario_afectado=usuario
    )
    assert auditoria.actor == usuario_admin
    assert auditoria.detalles["roles"] == ["soporte"]
    assert auditoria.fecha_hora is not None


def test_alta_valida_password_duplicados_y_roles(usuario_admin, rol_cliente):
    cliente = _auth(usuario_admin)

    sin_roles = cliente.post(USUARIOS_URL, _nuevo_usuario(), format="json")
    distinto = cliente.post(
        USUARIOS_URL,
        _nuevo_usuario(
            username="otro_interno",
            roles=[rol_cliente.pk],
            password_confirm="OtraClave#2026",
        ),
        format="json",
    )
    duplicado = cliente.post(
        USUARIOS_URL,
        _nuevo_usuario(username="admin_test", roles=[rol_cliente.pk]),
        format="json",
    )

    assert sin_roles.status_code == 400
    assert "roles" in sin_roles.json()["error"]["details"]
    assert distinto.status_code == 400
    assert "password_confirm" in distinto.json()["error"]["details"]
    assert duplicado.status_code == 400
    assert "username" in duplicado.json()["error"]["details"]
    assert not Usuario.objects.filter(username="nuevo_interno").exists()


def test_alta_rechaza_ambos_formatos_de_rol(usuario_admin, rol_cliente):
    respuesta = _auth(usuario_admin).post(
        USUARIOS_URL,
        _nuevo_usuario(roles=[rol_cliente.pk], rol=rol_cliente.pk),
        format="json",
    )

    assert respuesta.status_code == 400
    assert "roles" in respuesta.json()["error"]["details"]


# ── Edición de datos, roles y estado ─────────────────────────────────────────


def test_patch_actualiza_datos_y_roles_con_auditoria(
    usuario_admin, usuario_cliente, rol_cliente, rol_soporte
):
    respuesta = _auth(usuario_admin).patch(
        f"{USUARIOS_URL}{usuario_cliente.pk}/",
        {"first_name": "Ana", "roles": [rol_soporte.pk]},
        format="json",
    )

    assert respuesta.status_code == 200, respuesta.json()
    assert respuesta.json()["data"]["first_name"] == "Ana"
    assert respuesta.json()["data"]["roles"] == [rol_soporte.pk]

    usuario_cliente.refresh_from_db()
    assert usuario_cliente.first_name == "Ana"
    assert list(usuario_cliente.roles.all()) == [rol_soporte]

    auditoria = AuditoriaCuenta.objects.get(
        accion="roles_actualizados", usuario_afectado=usuario_cliente
    )
    assert auditoria.actor == usuario_admin
    assert auditoria.detalles["roles"] == {
        "antes": [rol_cliente.codigo],
        "despues": [rol_soporte.codigo],
    }
    assert auditoria.detalles["datos"]["first_name"]["despues"] == "Ana"


def test_activar_y_desactivar_registran_quien_y_cuando(
    usuario_admin, usuario_cliente
):
    cliente = _auth(usuario_admin)
    desactivar = cliente.post(
        f"{USUARIOS_URL}{usuario_cliente.pk}/desactivar/", format="json"
    )
    assert desactivar.status_code == 200
    assert desactivar.json()["data"]["is_active"] is False

    activar = cliente.post(
        f"{USUARIOS_URL}{usuario_cliente.pk}/activar/", format="json"
    )
    assert activar.status_code == 200
    assert activar.json()["data"]["is_active"] is True

    baja = AuditoriaCuenta.objects.get(
        accion="usuario_desactivado", usuario_afectado=usuario_cliente
    )
    alta = AuditoriaCuenta.objects.get(
        accion="usuario_activado", usuario_afectado=usuario_cliente
    )
    assert baja.actor == usuario_admin
    assert alta.actor == usuario_admin
    assert baja.fecha_hora <= alta.fecha_hora
    assert baja.detalles["is_active"] == {"antes": True, "despues": False}
    assert alta.detalles["is_active"] == {"antes": False, "despues": True}


def test_patch_tambien_cambia_is_active_y_lo_audita(usuario_admin, usuario_cliente):
    cliente = _auth(usuario_admin)
    url = f"{USUARIOS_URL}{usuario_cliente.pk}/"

    baja = cliente.patch(url, {"is_active": False}, format="json")
    alta = cliente.patch(url, {"is_active": True}, format="json")

    assert baja.status_code == 200
    assert baja.json()["data"]["is_active"] is False
    assert alta.status_code == 200
    assert alta.json()["data"]["is_active"] is True
    assert AuditoriaCuenta.objects.filter(
        accion="usuario_desactivado", usuario_afectado=usuario_cliente
    ).count() == 1
    assert AuditoriaCuenta.objects.filter(
        accion="usuario_activado", usuario_afectado=usuario_cliente
    ).count() == 1


def test_no_se_puede_autodesactivar(usuario_admin):
    cliente = _auth(usuario_admin)
    url = f"{USUARIOS_URL}{usuario_admin.pk}/"

    por_accion = cliente.post(f"{url}desactivar/", format="json")
    por_patch = cliente.patch(url, {"is_active": False}, format="json")

    for respuesta in (por_accion, por_patch):
        assert respuesta.status_code == 409
        assert "tu propia cuenta" in respuesta.json()["error"]["message"]

    usuario_admin.refresh_from_db()
    assert usuario_admin.is_active is True


def test_no_se_puede_quitar_al_ultimo_administrador(rol_admin):
    # Sin is_staff: este usuario solo es administrador por su rol de negocio.
    unico_admin = Usuario.objects.create_user(
        username="admin_solo_rol", password=PASSWORD, email="adminrol@test.com"
    )
    unico_admin.roles.add(rol_admin)

    with pytest.raises(ErrorDeNegocio, match="último administrador"):
        cambiar_estado_usuario(None, unico_admin, activar=False)

    with pytest.raises(ErrorDeNegocio, match="último administrador"):
        _quitar_rol_admin(unico_admin)

    unico_admin.refresh_from_db()
    assert unico_admin.is_active is True
    assert unico_admin.roles.filter(codigo="administrador").exists()


def _quitar_rol_admin(usuario):
    from api.cuentas_service import actualizar_usuario

    roles = [
        rol for rol in usuario.roles.all() if rol.codigo != "administrador"
    ] or list(Rol.objects.filter(codigo="cliente"))
    return actualizar_usuario(None, usuario, {}, roles=roles)


def test_no_se_puede_asignar_un_rol_superior_al_propio(
    usuario_gestor_inventario, rol_admin
):
    with pytest.raises(PermissionDenied, match="por encima"):
        crear_usuario(
            actor=usuario_gestor_inventario,
            datos={
                "username": "escalado",
                "email": "escalado@test.com",
                "first_name": "",
                "last_name": "",
                "telefono": "",
                "direccion": "",
            },
            roles=[rol_admin],
            password=PASSWORD,
        )

    via_api = _auth(usuario_gestor_inventario).post(
        USUARIOS_URL,
        _nuevo_usuario(username="escalado_api", roles=[rol_admin.pk]),
        format="json",
    )
    assert via_api.status_code == 403


def test_historial_de_auditoria_esta_disponible_para_admin(
    usuario_admin, usuario_cliente
):
    cliente = _auth(usuario_admin)
    cliente.post(f"{USUARIOS_URL}{usuario_cliente.pk}/desactivar/", format="json")

    respuesta = cliente.get(f"{USUARIOS_URL}{usuario_cliente.pk}/auditoria/")

    assert respuesta.status_code == 200
    registros = respuesta.json()["data"]
    assert [registro["accion"] for registro in registros] == ["usuario_desactivado"]
    assert registros[0]["actor_username"] == usuario_admin.username
    assert registros[0]["usuario_username"] == usuario_cliente.username


def test_usuarios_solo_para_administradores(usuario_cliente, usuario_sin_rol):
    assert APIClient().post(USUARIOS_URL, _nuevo_usuario(), format="json").status_code == 401
    assert _auth(usuario_cliente).post(
        USUARIOS_URL, _nuevo_usuario(), format="json"
    ).status_code == 403
    assert _auth(usuario_sin_rol).get(USUARIOS_URL).status_code == 403


# ── CRUD limitado de roles ───────────────────────────────────────────────────


def test_admin_crea_y_edita_rol_con_auditoria(usuario_admin):
    cliente = _auth(usuario_admin)
    creado = cliente.post(
        ROLES_URL,
        {
            "codigo": "auditoria",
            "nombre": "Auditoría",
            "descripcion": "Revisa los cambios del sistema.",
        },
        format="json",
    )

    assert creado.status_code == 201, creado.json()
    rol_id = creado.json()["data"]["id"]
    assert creado.json()["data"]["activo"] is True

    editado = cliente.patch(
        f"{ROLES_URL}{rol_id}/", {"descripcion": "Revisa todas las auditorías."}, format="json"
    )
    assert editado.status_code == 200
    assert editado.json()["data"]["descripcion"] == "Revisa todas las auditorías."

    assert AuditoriaCuenta.objects.filter(accion="rol_creado").count() == 1
    assert AuditoriaCuenta.objects.filter(accion="rol_actualizado").count() == 1


def test_no_se_elimina_un_rol_en_uso_ni_un_rol_base(
    usuario_admin, usuario_cliente, rol_cliente
):
    en_uso = Rol.objects.create(codigo="en_uso", nombre="En uso")
    usuario_cliente.roles.add(en_uso)
    cliente = _auth(usuario_admin)

    respuesta_en_uso = cliente.delete(f"{ROLES_URL}{en_uso.pk}/")
    respuesta_base = cliente.delete(f"{ROLES_URL}{rol_cliente.pk}/")

    assert respuesta_en_uso.status_code == 409
    assert "usuarios asignados" in respuesta_en_uso.json()["error"]["message"]
    assert respuesta_base.status_code == 409
    assert "rol base" in respuesta_base.json()["error"]["message"]
    assert Rol.objects.filter(pk=en_uso.pk).exists()
    assert Rol.objects.filter(pk=rol_cliente.pk).exists()


def test_admin_elimina_rol_sin_usuarios_y_queda_auditado(usuario_admin):
    rol = Rol.objects.create(codigo="temporal", nombre="Temporal")
    cliente = _auth(usuario_admin)

    respuesta = cliente.delete(f"{ROLES_URL}{rol.pk}/")

    assert respuesta.status_code == 204
    assert not Rol.objects.filter(pk=rol.pk).exists()
    auditoria = AuditoriaCuenta.objects.get(accion="rol_eliminado")
    assert auditoria.actor == usuario_admin
    assert auditoria.detalles["codigo"] == "temporal"


def test_roles_rechazan_codigos_invalidos(usuario_admin):
    respuesta = _auth(usuario_admin).post(
        ROLES_URL,
        {"codigo": "Rol Con Espacios", "nombre": "Inválido"},
        format="json",
    )

    assert respuesta.status_code == 400
    assert "codigo" in respuesta.json()["error"]["details"]
