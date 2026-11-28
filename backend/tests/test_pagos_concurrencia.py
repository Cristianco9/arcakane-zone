"""Carreras de pago/cancelación: solo válidas en PostgreSQL.

SQLite no bloquea con ``SELECT FOR UPDATE``, así que las pruebas de este
módulo se omiten explícitamente fuera de PostgreSQL. Se sincroniza con un
``Barrier`` (sin sleeps) y cada hilo cierra su propia conexión.
"""
import threading
from unittest.mock import patch

import pytest
from django.db import connection
from rest_framework.test import APIClient

from inventario.models import MovimientoInventarioOfertaVideojuego
from pagos.models import IntentoPago, Venta
from pedidos.models import DetallePedido, Pedido

pytestmark = [
    pytest.mark.skipif(
        connection.vendor != "postgresql",
        reason=(
            "select_for_update no bloquea en SQLite: la carrera solo se puede "
            "verificar en PostgreSQL."
        ),
    ),
    pytest.mark.django_db(transaction=True),
]


def _ejecutar_en_paralelo(*operaciones):
    """Arranca todas las operaciones a la vez y cierra la conexión de cada hilo."""
    barrera = threading.Barrier(len(operaciones))
    resultados = [None] * len(operaciones)
    errores = []

    def correr(indice, operacion):
        try:
            barrera.wait()
            resultados[indice] = operacion()
        except BaseException as exc:  # se reenvía en el hilo principal
            errores.append(exc)
        finally:
            connection.close()

    hilos = [
        threading.Thread(target=correr, args=(indice, operacion))
        for indice, operacion in enumerate(operaciones)
    ]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    if errores:
        raise errores[0]
    return resultados


def _cliente(usuario):
    client = APIClient()
    client.force_authenticate(usuario)
    return client


def _pagar(usuario, pedido_id, clave=None):
    extra = {"HTTP_IDEMPOTENCY_KEY": clave} if clave else {}
    return _cliente(usuario).post(
        "/api/v1/pagos/", {"pedido": pedido_id}, format="json", **extra
    )


def _cancelar(usuario, pedido_id):
    return _cliente(usuario).post(f"/api/v1/pedidos/{pedido_id}/cancelar/")


def test_dos_pagos_simultaneos_del_mismo_pedido(
    usuario_cliente, pedido_con_item, oferta
):
    stock_inicial = oferta.stock
    cantidad = pedido_con_item.detalles.first().cantidad

    with patch("pagos.services.random.random", return_value=0.0):
        resultados = _ejecutar_en_paralelo(
            lambda: _pagar(usuario_cliente, pedido_con_item.pk),
            lambda: _pagar(usuario_cliente, pedido_con_item.pk),
        )

    assert sorted(r.status_code for r in resultados) == [201, 409]
    perdedor = next(r for r in resultados if r.status_code == 409)
    assert perdedor.json()["error"]["code"] == "pedido_ya_pagado"
    assert IntentoPago.objects.filter(pedido=pedido_con_item).count() == 1
    assert Venta.objects.filter(pedido=pedido_con_item).count() == 1
    assert MovimientoInventarioOfertaVideojuego.objects.count() == 1
    oferta.refresh_from_db()
    assert oferta.stock == stock_inicial - cantidad


def test_dos_solicitudes_simultaneas_con_la_misma_clave(
    usuario_cliente, pedido_con_item, oferta
):
    with patch("pagos.services.random.random", return_value=0.0):
        resultados = _ejecutar_en_paralelo(
            lambda: _pagar(usuario_cliente, pedido_con_item.pk, clave="clave-carrera"),
            lambda: _pagar(usuario_cliente, pedido_con_item.pk, clave="clave-carrera"),
        )

    assert all(r.status_code == 201 for r in resultados)
    assert sum(r.get("Idempotent-Replayed") == "true" for r in resultados) == 1
    assert resultados[0].json() == resultados[1].json()
    assert IntentoPago.objects.filter(pedido=pedido_con_item).count() == 1
    assert Venta.objects.filter(pedido=pedido_con_item).count() == 1
    assert MovimientoInventarioOfertaVideojuego.objects.count() == 1
    oferta.refresh_from_db()
    assert oferta.stock == 8


def test_pago_y_cancelacion_simultaneos(usuario_cliente, pedido_con_item):
    with patch("pagos.services.random.random", return_value=0.0):
        pago, cancelacion = _ejecutar_en_paralelo(
            lambda: _pagar(usuario_cliente, pedido_con_item.pk),
            lambda: _cancelar(usuario_cliente, pedido_con_item.pk),
        )

    pedido_con_item.refresh_from_db()
    if pago.status_code == 201:
        assert cancelacion.status_code == 409
        assert cancelacion.json()["error"]["code"] == "pedido_no_cancelable"
        assert pedido_con_item.estado_id == "pagado"
        assert Venta.objects.filter(pedido=pedido_con_item).count() == 1
    else:
        assert pago.status_code == 409
        assert pago.json()["error"]["code"] == "pedido_no_pagable"
        assert cancelacion.status_code == 200
        assert pedido_con_item.estado_id == "cancelado"
        assert not Venta.objects.filter(pedido=pedido_con_item).exists()


def test_dos_pedidos_por_la_ultima_unidad(usuario_cliente, pedido_con_item, oferta):
    detalle = pedido_con_item.detalles.first()
    detalle.cantidad = 1
    detalle.save(update_fields=["cantidad"])
    oferta.stock = 1
    oferta.save(update_fields=["stock"])

    otro = Pedido.objects.create(cliente=usuario_cliente, estado_id="pendiente")
    DetallePedido.objects.create(
        pedido=otro,
        oferta=oferta,
        cantidad=1,
        precio_unitario=oferta.precio_vigente,
    )

    with patch("pagos.services.random.random", return_value=0.0):
        resultados = _ejecutar_en_paralelo(
            lambda: _pagar(usuario_cliente, pedido_con_item.pk),
            lambda: _pagar(usuario_cliente, otro.pk),
        )

    assert sorted(r.status_code for r in resultados) == [201, 409]
    perdedor = next(r for r in resultados if r.status_code == 409)
    assert perdedor.json()["error"]["code"] == "conflicto"
    oferta.refresh_from_db()
    assert oferta.stock == 0
    assert Venta.objects.count() == 1
    assert MovimientoInventarioOfertaVideojuego.objects.count() == 1
