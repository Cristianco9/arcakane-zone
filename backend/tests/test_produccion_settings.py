"""Endurecimiento de la configuración de producción (AZ-S2-BE-09)."""
import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings

BASE_DIR = Path(__file__).resolve().parents[1]
SECRET_KEY_SEGURA = (
    "produccion-clave-de-prueba-con-mas-de-cincuenta-caracteres-y-unica-1234567890"
)


def _check_deploy(**variables):
    entorno = os.environ.copy()
    entorno.update(
        {
            "DJANGO_SETTINGS_MODULE": "arkane_zone.settings",
            "DEBUG": "False",
            "DATABASE_URL": "sqlite:///db.sqlite3",
            "ALLOWED_HOSTS": "localhost,127.0.0.1",
            "SECRET_KEY": SECRET_KEY_SEGURA,
            "SECURE_SSL_REDIRECT": "True",
        }
    )
    entorno.update(variables)
    resultado = subprocess.run(
        [sys.executable, "manage.py", "check", "--deploy"],
        cwd=BASE_DIR,
        env=entorno,
        capture_output=True,
        text=True,
        check=False,
    )
    return resultado, resultado.stdout + resultado.stderr


def test_check_deploy_esta_limpio_con_debug_false():
    resultado, salida = _check_deploy()

    assert resultado.returncode == 0, salida
    assert "System check identified no issues" in salida
    assert "warning" not in salida.lower()


def test_arranque_falla_si_secret_key_esta_vacia():
    resultado, salida = _check_deploy(SECRET_KEY="")

    assert resultado.returncode != 0
    assert "SECRET_KEY está vacía" in salida


def test_arranque_falla_si_secret_key_es_de_ejemplo():
    resultado, salida = _check_deploy(
        SECRET_KEY="cambia-esto-por-una-clave-larga-y-aleatoria"
    )

    assert resultado.returncode != 0
    assert "SECRET_KEY" in salida
    assert "ejemplo" in salida or "débil" in salida


def test_cabeceras_y_cookies_endurecidas_estan_definidas():
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert settings.SECURE_REFERRER_POLICY == "same-origin"
    assert settings.SESSION_COOKIE_SAMESITE == "Lax"
    assert settings.CSRF_COOKIE_SAMESITE == "Lax"
    assert settings.SECURE_HSTS_SECONDS == 31536000
    assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert settings.SECURE_HSTS_PRELOAD is True
