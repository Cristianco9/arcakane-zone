"""Trazabilidad de peticiones y logs de la API (AZ-S2-BE-09)."""
import json
import logging
import re
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from api.observabilidad import JsonFormatter

pytestmark = pytest.mark.django_db


def test_request_id_se_devuelve_y_se_acepta_del_cliente():
    cliente = APIClient()

    con_cabecera = cliente.get(
        "/api/v1/health/", HTTP_X_REQUEST_ID="traza-cliente-123"
    )
    generado = cliente.get("/api/v1/health/")

    assert con_cabecera["X-Request-ID"] == "traza-cliente-123"
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        generado["X-Request-ID"],
    )


def test_json_formatter_incluye_request_id_y_contexto():
    registro = logging.LogRecord(
        "api", logging.ERROR, __file__, 1, "fallo de prueba", (), None
    )
    registro.request_id = "traza-abc"
    registro.metodo = "GET"
    registro.ruta = "/api/v1/health/"
    registro.status_code = 500
    registro.evento = "api_error_no_controlado"

    datos = json.loads(JsonFormatter().format(registro))

    assert datos["message"] == "fallo de prueba"
    assert datos["request_id"] == "traza-abc"
    assert datos["metodo"] == "GET"
    assert datos["ruta"] == "/api/v1/health/"
    assert datos["status_code"] == 500
    assert datos["evento"] == "api_error_no_controlado"


def test_error_500_queda_registrado_con_request_id_y_ruta(caplog):
    cliente = APIClient()
    with patch(
        "api.views.base.HealthView.get", side_effect=RuntimeError("boom inesperado")
    ):
        with caplog.at_level(logging.ERROR, logger="api.middleware"):
            respuesta = cliente.get(
                "/api/v1/health/", HTTP_X_REQUEST_ID="error-123"
            )

    assert respuesta.status_code == 500
    assert respuesta.json()["error"]["code"] == "error_interno"
    assert respuesta["X-Request-ID"] == "error-123"

    registros = [
        registro
        for registro in caplog.records
        if registro.name == "api.middleware" and registro.levelno >= logging.ERROR
    ]
    assert registros, "No se registró el error 500"
    assert any(
        registro.request_id == "error-123"
        and registro.metodo == "GET"
        and registro.ruta == "/api/v1/health/"
        and registro.status_code == 500
        for registro in registros
    )
