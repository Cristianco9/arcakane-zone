"""Pruebas de tokens con vencimiento, refresh y revocación global."""
import hashlib
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import tokens as auth_tokens
from django.contrib.auth.hashers import make_password
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from api.models import Token
from arkane_zone import settings as django_settings
from cuentas.models import Usuario

pytestmark = pytest.mark.django_db

LOGIN_URL = "/api/v1/auth/login/"
REGISTRO_URL = "/api/v1/auth/registro/"
ME_URL = "/api/v1/auth/me/"
LOGOUT_URL = "/api/v1/auth/logout/"
REFRESH_URL = "/api/v1/auth/token/refresh/"
LOGOUT_ALL_URL = "/api/v1/auth/logout-all/"
PASSWORD_URL = "/api/v1/auth/me/password/"
PASSWORD_NUEVA = "NuevaClave#2026"


def _cliente():
    return APIClient()


def _login(cliente=None, password="pass1234!"):
    cliente = cliente or _cliente()
    respuesta = cliente.post(
        LOGIN_URL,
        {"username": "cliente_test", "password": password},
        format="json",
    )
    return respuesta, cliente


def _con_token(clave):
    cliente = _cliente()
    cliente.credentials(HTTP_AUTHORIZATION=f"Token {clave}")
    return cliente


def _assert_no_autenticado(respuesta):
    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["code"] == "no_autenticado"


def test_token_vigente_autentica_y_lleva_expires_at(usuario_cliente):
    respuesta, _ = _login()

    assert respuesta.status_code == 200
    datos = respuesta.json()["data"]
    assert datos["token"]
    assert datos["expires_at"]
    assert _con_token(datos["token"]).get(ME_URL).status_code == 200


def test_token_vencido_da_401_no_autenticado(usuario_cliente):
    token, clave = Token.emitir(usuario_cliente)

    with patch(
        "api.authentication.timezone.now",
        return_value=token.expira_en + timedelta(seconds=1),
    ):
        _assert_no_autenticado(_con_token(clave).get(ME_URL))


def test_token_inexistente_da_401_no_autenticado():
    respuesta = _con_token("token-que-no-existe").get(ME_URL)
    _assert_no_autenticado(respuesta)


def test_cada_login_emite_token_distinto_y_ambos_funcionan(usuario_cliente):
    primero, _ = _login()
    segundo, _ = _login()

    clave_uno = primero.json()["data"]["token"]
    clave_dos = segundo.json()["data"]["token"]
    assert clave_uno != clave_dos
    assert _con_token(clave_uno).get(ME_URL).status_code == 200
    assert _con_token(clave_dos).get(ME_URL).status_code == 200


def test_refresh_rota_el_token(usuario_cliente):
    login, _ = _login()
    anterior = login.json()["data"]["token"]

    respuesta = _con_token(anterior).post(REFRESH_URL, format="json")
    assert respuesta.status_code == 200
    datos = respuesta.json()["data"]
    assert datos["token"] != anterior
    assert datos["expires_at"]

    _assert_no_autenticado(_con_token(anterior).get(ME_URL))
    assert _con_token(datos["token"]).get(ME_URL).status_code == 200


def test_refresh_sin_token_da_401():
    _assert_no_autenticado(_cliente().post(REFRESH_URL, format="json"))


def test_refresh_con_token_vencido_da_401(usuario_cliente):
    token, clave = Token.emitir(usuario_cliente)
    token.expira_en = timezone.now() - timedelta(seconds=1)
    token.save(update_fields=["expira_en"])

    _assert_no_autenticado(_con_token(clave).post(REFRESH_URL, format="json"))


def test_logout_revoca_solo_el_token_actual(usuario_cliente):
    primero, _ = _login()
    segundo, _ = _login()
    actual = primero.json()["data"]["token"]
    otro = segundo.json()["data"]["token"]

    assert _con_token(actual).post(LOGOUT_URL, format="json").status_code == 200
    _assert_no_autenticado(_con_token(actual).get(ME_URL))
    assert _con_token(otro).get(ME_URL).status_code == 200


def test_logout_all_revoca_todos_los_tokens_del_usuario(usuario_cliente, usuario_admin):
    primero, _ = _login()
    segundo, _ = _login()
    propio_uno = primero.json()["data"]["token"]
    propio_dos = segundo.json()["data"]["token"]

    _, clave_admin = Token.emitir(usuario_admin)

    respuesta = _con_token(propio_uno).post(LOGOUT_ALL_URL, format="json")
    assert respuesta.status_code == 200

    _assert_no_autenticado(_con_token(propio_uno).get(ME_URL))
    _assert_no_autenticado(_con_token(propio_dos).get(ME_URL))
    assert _con_token(clave_admin).get(ME_URL).status_code == 200


def test_cambio_de_password_por_api_invalida_tokens(usuario_cliente):
    login, _ = _login()
    anterior = login.json()["data"]["token"]

    respuesta = _con_token(anterior).post(
        PASSWORD_URL,
        {
            "old_password": "pass1234!",
            "new_password": PASSWORD_NUEVA,
            "new_password_confirm": PASSWORD_NUEVA,
        },
        format="json",
    )
    assert respuesta.status_code == 200
    _assert_no_autenticado(_con_token(anterior).get(ME_URL))

    _, cliente = _login(password=PASSWORD_NUEVA)
    assert cliente.get(ME_URL).status_code == 200


def test_cambio_de_password_por_formulario_web_invalida_tokens(usuario_cliente):
    _, clave = Token.emitir(usuario_cliente)

    cliente = Client()
    cliente.force_login(usuario_cliente)
    respuesta = cliente.post(
        reverse("cuentas:cambiar_password"),
        {
            "old_password": "pass1234!",
            "new_password1": PASSWORD_NUEVA,
            "new_password2": PASSWORD_NUEVA,
        },
    )
    assert respuesta.status_code == 302
    _assert_no_autenticado(_con_token(clave).get(ME_URL))

    _, cliente_api = _login(password=PASSWORD_NUEVA)
    assert cliente_api.get(ME_URL).status_code == 200


def test_reseteo_de_password_invalida_tokens(usuario_cliente):
    _, clave = Token.emitir(usuario_cliente)
    uidb64 = urlsafe_base64_encode(force_bytes(usuario_cliente.pk))
    token_reset = auth_tokens.default_token_generator.make_token(usuario_cliente)
    url = reverse(
        "password_reset_confirm", kwargs={"uidb64": uidb64, "token": token_reset}
    )

    cliente = Client()
    # El primer POST redirige a la URL sin el token en la dirección.
    respuesta = cliente.post(url)
    assert respuesta.status_code == 302
    respuesta = cliente.post(
        respuesta.url,
        {"new_password1": PASSWORD_NUEVA, "new_password2": PASSWORD_NUEVA},
    )
    assert respuesta.status_code == 302
    _assert_no_autenticado(_con_token(clave).get(ME_URL))

    _, cliente_api = _login(password=PASSWORD_NUEVA)
    assert cliente_api.get(ME_URL).status_code == 200


def test_cambio_de_password_por_admin_invalida_tokens(usuario_cliente):
    _, clave = Token.emitir(usuario_cliente)
    administrador = Usuario.objects.create_superuser(
        username="root", email="root@test.com", password="pass1234!"
    )

    cliente = Client()
    cliente.force_login(administrador)
    respuesta = cliente.post(
        reverse("admin:auth_user_password_change", args=[usuario_cliente.pk]),
        {"password1": PASSWORD_NUEVA, "password2": PASSWORD_NUEVA},
    )
    assert respuesta.status_code == 302
    _assert_no_autenticado(_con_token(clave).get(ME_URL))

    _, cliente_api = _login(password=PASSWORD_NUEVA)
    assert cliente_api.get(ME_URL).status_code == 200


@override_settings(
    PASSWORD_HASHERS=[
        "django.contrib.auth.hashers.PBKDF2PasswordHasher",
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
)
def test_rehash_automatico_al_login_no_invalida_el_token_emitido(usuario_cliente):
    # Hash viejo (MD5) con PBKDF2 preferido: el login lo actualiza y llama a save().
    usuario_cliente.password = make_password("pass1234!", hasher="md5")
    usuario_cliente.save(update_fields=["password"])
    _, anterior = Token.emitir(usuario_cliente)

    respuesta, cliente = _login()
    assert respuesta.status_code == 200
    _assert_no_autenticado(_con_token(anterior).get(ME_URL))
    assert cliente.get(ME_URL).status_code == 200


def test_la_sesion_por_cookie_sigue_funcionando(usuario_cliente):
    respuesta, cliente = _login()
    assert respuesta.status_code == 200
    assert cliente.get(ME_URL).status_code == 200


def test_en_base_de_datos_solo_guarda_el_hash(usuario_cliente):
    token, clave = Token.emitir(usuario_cliente)

    assert token.key_hash != clave
    assert token.key_hash == hashlib.sha256(clave.encode("utf-8")).hexdigest()
    assert not Token.objects.filter(key_hash=clave).exists()
    assert Token.objects.filter(key_hash=token.key_hash).exists()


def test_ttl_se_lee_del_entorno(monkeypatch):
    monkeypatch.setenv("API_TOKEN_TTL_DAYS", "3")
    assert django_settings.ttl_token_desde_entorno() == 3

    monkeypatch.setenv("API_TOKEN_TTL_DAYS", "0")
    assert django_settings.ttl_token_desde_entorno() == 1


def test_el_ttl_configurado_se_aplica_al_emitir(usuario_cliente):
    with override_settings(API_TOKEN_TTL_DAYS=2):
        token, _ = Token.emitir(usuario_cliente)

    assert 1 <= (token.expira_en - token.creado_en).days <= 2
