"""Readiness de la API: el healthcheck debe consultar la base de datos."""
from unittest.mock import patch

import pytest
from django.db.utils import OperationalError
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

URL = "/api/v1/health/ready/"


def test_health_ready_confirma_la_base_de_datos():
    respuesta = APIClient().get(URL)

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["success"] is True
    assert datos["data"] == {
        "status": "ready",
        "database": "ok",
        "version": "v1",
    }


def test_health_ready_responde_503_si_la_base_no_responde():
    with patch(
        "api.views.base.connection.cursor", side_effect=OperationalError("BD caída")
    ):
        respuesta = APIClient().get(URL)

    assert respuesta.status_code == 503
    cuerpo = respuesta.json()
    assert cuerpo["success"] is False
    assert cuerpo["error"]["code"] == "bd_no_disponible"
    assert "base de datos" in cuerpo["error"]["message"]


def test_health_ready_es_publico_y_no_requiere_autenticacion():
    # El cliente no está autenticado a propósito: Docker/Render consultan la
    # ruta sin credenciales ni sesión.
    assert APIClient().get(URL).status_code == 200
