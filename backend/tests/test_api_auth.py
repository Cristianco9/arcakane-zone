"""Pruebas de autenticación, sesión, token y perfil."""
import pytest
from rest_framework.test import APIClient

from cuentas.models import Usuario

pytestmark = pytest.mark.django_db

PASSWORD_FUERTE = "ClaveSegura#2026"


def _client():
    return APIClient()


def _registrar(client, username="nuevo_cliente", email="nuevo@test.com"):
    return client.post(
        "/api/v1/auth/registro/",
        {
            "username": username,
            "email": email,
            "first_name": "Nuevo",
            "last_name": "Cliente",
            "password": PASSWORD_FUERTE,
            "password_confirm": PASSWORD_FUERTE,
        },
        format="json",
    )


def test_registro_crea_usuario_con_rol_cliente_y_devuelve_token():
    response = _registrar(_client())

    assert response.status_code == 201
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["token"]
    assert payload["data"]["usuario"]["username"] == "nuevo_cliente"
    assert payload["data"]["usuario"]["rol_nombre"] == "cliente"
    assert Usuario.objects.filter(username="nuevo_cliente").exists()


def test_registro_rechaza_username_duplicado(usuario_cliente):
    response = _registrar(_client(), username=usuario_cliente.username)

    assert response.status_code == 400
    assert "username" in response.json()["error"]["details"]


def test_registro_rechaza_correo_duplicado(usuario_cliente):
    response = _registrar(_client(), email=usuario_cliente.email)

    assert response.status_code == 400
    assert "email" in response.json()["error"]["details"]


def test_registro_valida_confirmacion_y_fortaleza_de_password():
    client = _client()
    no_coincide = client.post(
        "/api/v1/auth/registro/",
        {
            "username": "otro",
            "email": "otro@test.com",
            "password": PASSWORD_FUERTE,
            "password_confirm": "OtraClave#2026",
        },
        format="json",
    )
    debil = client.post(
        "/api/v1/auth/registro/",
        {
            "username": "debil",
            "email": "debil@test.com",
            "password": "123",
            "password_confirm": "123",
        },
        format="json",
    )

    assert no_coincide.status_code == 400
    assert "password_confirm" in no_coincide.json()["error"]["details"]
    assert debil.status_code == 400
    assert "password" in debil.json()["error"]["details"]


def test_login_devuelve_token_y_permite_autenticarse(usuario_cliente):
    login = _client().post(
        "/api/v1/auth/login/",
        {"username": usuario_cliente.username, "password": "pass1234!"},
        format="json",
    )

    assert login.status_code == 200
    token = login.json()["data"]["token"]
    assert token

    autenticado = _client()
    autenticado.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    perfil = autenticado.get("/api/v1/auth/me/")

    assert perfil.status_code == 200
    assert perfil.json()["data"]["username"] == usuario_cliente.username


def test_login_credenciales_invalidas_devuelve_401():
    response = _client().post(
        "/api/v1/auth/login/",
        {"username": "noexiste", "password": "incorrecta"},
        format="json",
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "credenciales_invalidas"


def test_login_por_sesion_mantiene_cookie(usuario_cliente):
    client = _client()
    login = client.post(
        "/api/v1/auth/login/",
        {"username": usuario_cliente.username, "password": "pass1234!"},
        format="json",
    )
    perfil = client.get("/api/v1/auth/me/")

    assert login.status_code == 200
    assert perfil.status_code == 200
    assert perfil.json()["data"]["id"] == usuario_cliente.pk


def test_perfil_requiere_autenticacion():
    response = _client().get("/api/v1/auth/me/")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "no_autenticado"


def test_perfil_se_puede_actualizar(usuario_cliente):
    client = _client()
    client.force_authenticate(usuario_cliente)

    response = client.patch(
        "/api/v1/auth/me/",
        {"first_name": "Actualizado", "telefono": "3001234567"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["data"]["first_name"] == "Actualizado"
    usuario_cliente.refresh_from_db()
    assert usuario_cliente.telefono == "3001234567"


def test_perfil_no_permite_correo_de_otro_usuario(usuario_cliente, usuario_admin):
    client = _client()
    client.force_authenticate(usuario_cliente)

    response = client.patch(
        "/api/v1/auth/me/",
        {"email": usuario_admin.email},
        format="json",
    )

    assert response.status_code == 400
    assert "email" in response.json()["error"]["details"]


def test_cambio_de_password(usuario_cliente):
    client = _client()
    client.force_authenticate(usuario_cliente)

    response = client.post(
        "/api/v1/auth/me/password/",
        {
            "old_password": "pass1234!",
            "new_password": PASSWORD_FUERTE,
            "new_password_confirm": PASSWORD_FUERTE,
        },
        format="json",
    )

    assert response.status_code == 200
    usuario_cliente.refresh_from_db()
    assert usuario_cliente.check_password(PASSWORD_FUERTE) is True


def test_cambio_de_password_valida_actual_y_confirmacion(usuario_cliente):
    client = _client()
    client.force_authenticate(usuario_cliente)

    incorrecta = client.post(
        "/api/v1/auth/me/password/",
        {
            "old_password": "no-es-la-actual",
            "new_password": PASSWORD_FUERTE,
            "new_password_confirm": PASSWORD_FUERTE,
        },
        format="json",
    )
    no_coincide = client.post(
        "/api/v1/auth/me/password/",
        {
            "old_password": "pass1234!",
            "new_password": PASSWORD_FUERTE,
            "new_password_confirm": "OtraClave#2026",
        },
        format="json",
    )

    assert incorrecta.status_code == 400
    assert "old_password" in incorrecta.json()["error"]["details"]
    assert no_coincide.status_code == 400
    assert "new_password_confirm" in no_coincide.json()["error"]["details"]


def test_logout_invalida_el_token(usuario_cliente):
    login = _client().post(
        "/api/v1/auth/login/",
        {"username": usuario_cliente.username, "password": "pass1234!"},
        format="json",
    )
    token = login.json()["data"]["token"]

    client = _client()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    logout = client.post("/api/v1/auth/logout/")

    assert logout.status_code == 200

    reutilizado = _client()
    reutilizado.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    assert reutilizado.get("/api/v1/auth/me/").status_code == 401


def test_endpoint_csrf_entrega_cookie():
    response = _client().get("/api/v1/auth/csrf/")

    assert response.status_code == 200
    assert response.json()["data"]["csrfToken"]
    assert "csrftoken" in response.cookies
