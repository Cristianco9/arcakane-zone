"""Idempotencia, revalidación e inmutabilidad de intentos (AZ-S2-BE-10)."""
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from api.exceptions import PedidoYaPagado
from cuentas.models import Usuario
from inventario.models import MovimientoInventarioOfertaVideojuego
from pagos.models import IntentoPago, Venta
from pagos.services import procesar_pago
from pedidos.models import DetallePedido, Pedido
from pedidos.services import cancelar_pedido

pytestmark = pytest.mark.django_db


def _auth(usuario):
    client = APIClient()
    client.force_authenticate(usuario)
    return client


def _pagar(usuario, pedido_id, clave=None, random_value=0.0):
    extra = {"HTTP_IDEMPOTENCY_KEY": clave} if clave is not None else {}
    with patch("pagos.services.random.random", return_value=random_value):
        return _auth(usuario).post(
            "/api/v1/pagos/", {"pedido": pedido_id}, format="json", **extra
        )


def test_misma_clave_y_pedido_repite_la_respuesta_original(
    usuario_cliente, pedido_con_item, oferta
):
    primera = _pagar(usuario_cliente, pedido_con_item.pk, clave="clave-abc")
    assert primera.status_code == 201
    assert "Idempotent-Replayed" not in primera

    # Una segunda petición con la misma clave no puede reprocesar: aunque la
    # aprobación simulada daría rechazo, debe devolver el 201 original.
    segunda = _pagar(
        usuario_cliente, pedido_con_item.pk, clave="clave-abc", random_value=0.99
    )
    assert segunda.status_code == 201
    assert segunda["Idempotent-Replayed"] == "true"
    assert segunda.json() == primera.json()

    assert IntentoPago.objects.filter(pedido=pedido_con_item).count() == 1
    assert Venta.objects.filter(pedido=pedido_con_item).count() == 1
    assert MovimientoInventarioOfertaVideojuego.objects.count() == 1
    oferta.refresh_from_db()
    assert oferta.stock == 8


def test_clave_rechazada_se_repite_con_402(usuario_cliente, pedido_con_item):
    primera = _pagar(
        usuario_cliente, pedido_con_item.pk, clave="clave-rechazo", random_value=0.95
    )
    segunda = _pagar(
        usuario_cliente, pedido_con_item.pk, clave="clave-rechazo", random_value=0.0
    )

    assert primera.status_code == 402
    assert segunda.status_code == 402
    assert segunda["Idempotent-Replayed"] == "true"
    assert segunda.json() == primera.json()
    assert IntentoPago.objects.filter(pedido=pedido_con_item).count() == 1
    assert not Venta.objects.filter(pedido=pedido_con_item).exists()


def test_misma_clave_en_otro_pedido_devuelve_409(
    usuario_cliente, pedido_con_item, oferta
):
    otro = Pedido.objects.create(cliente=usuario_cliente, estado_id="pendiente")
    DetallePedido.objects.create(
        pedido=otro,
        oferta=oferta,
        cantidad=1,
        precio_unitario=oferta.precio_vigente,
    )

    assert (
        _pagar(usuario_cliente, pedido_con_item.pk, clave="clave-compartida").status_code
        == 201
    )
    oferta.refresh_from_db()
    stock_despues = oferta.stock

    respuesta = _pagar(usuario_cliente, otro.pk, clave="clave-compartida")
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "clave_idempotencia_en_uso"
    assert not IntentoPago.objects.filter(pedido=otro).exists()
    oferta.refresh_from_db()
    assert oferta.stock == stock_despues


def test_clave_demasiado_larga_devuelve_400(usuario_cliente, pedido_con_item):
    maximo = IntentoPago._meta.get_field("clave_idempotencia").max_length

    respuesta = _pagar(usuario_cliente, pedido_con_item.pk, clave="x" * maximo)

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["code"] == "datos_invalidos"
    assert not IntentoPago.objects.exists()


def test_claves_de_usuarios_distintos_no_chocan(usuario_cliente, pedido_con_item, oferta):
    otro_usuario = Usuario.objects.create_user(
        username="otro_idempotente", password="pass1234!", email="otro@test.com"
    )
    otro_pedido = Pedido.objects.create(cliente=otro_usuario, estado_id="pendiente")
    DetallePedido.objects.create(
        pedido=otro_pedido,
        oferta=oferta,
        cantidad=1,
        precio_unitario=oferta.precio_vigente,
    )

    primera = _pagar(usuario_cliente, pedido_con_item.pk, clave="clave-igual")
    segunda = _pagar(otro_usuario, otro_pedido.pk, clave="clave-igual")

    assert primera.status_code == 201
    assert segunda.status_code == 201
    assert "Idempotent-Replayed" not in segunda
    assert IntentoPago.objects.count() == 2
    assert len(set(IntentoPago.objects.values_list("clave_idempotencia", flat=True))) == 2


def test_revalidacion_bajo_bloqueo_detecta_instancia_desactualizada(
    usuario_cliente, pedido_con_item
):
    with patch("pagos.services.random.random", return_value=0.0):
        procesar_pago(pedido_con_item)

    # Instancia desactualizada: dice "pendiente" aunque la fila ya está pagada.
    desactualizado = Pedido.objects.get(pk=pedido_con_item.pk)
    desactualizado.estado_id = "pendiente"
    with pytest.raises(PedidoYaPagado):
        procesar_pago(desactualizado)

    respuesta = _pagar(usuario_cliente, pedido_con_item.pk)
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "pedido_ya_pagado"


def test_intento_aprobado_no_se_modifica_y_rechazo_no_se_reutiliza(pedido_con_item):
    with patch("pagos.services.random.random", return_value=0.95):
        rechazado = procesar_pago(pedido_con_item).intento
    snapshot_rechazo = (
        rechazado.estado_id,
        rechazado.referencia,
        rechazado.importe,
    )

    with patch("pagos.services.random.random", return_value=0.0):
        aprobado = procesar_pago(pedido_con_item).intento
    snapshot_aprobado = (
        aprobado.estado_id,
        aprobado.referencia,
        aprobado.importe,
        aprobado.actualizado_en,
    )

    rechazado.refresh_from_db()
    assert (rechazado.estado_id, rechazado.referencia, rechazado.importe) == snapshot_rechazo
    assert aprobado.pk != rechazado.pk
    assert aprobado.referencia != rechazado.referencia
    assert IntentoPago.objects.filter(pedido=pedido_con_item).count() == 2

    with pytest.raises(PedidoYaPagado):
        procesar_pago(pedido_con_item)
    aprobado.refresh_from_db()
    assert (
        aprobado.estado_id,
        aprobado.referencia,
        aprobado.importe,
        aprobado.actualizado_en,
    ) == snapshot_aprobado


def test_pedido_cancelado_no_se_puede_pagar(usuario_cliente, pedido_con_item):
    cancelar_pedido(pedido_con_item)

    respuesta = _pagar(usuario_cliente, pedido_con_item.pk)

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "pedido_no_pagable"


def test_cancelar_pedido_pagado_devuelve_409_con_codigo(
    usuario_cliente, pedido_con_item
):
    with patch("pagos.services.random.random", return_value=0.0):
        procesar_pago(pedido_con_item)

    respuesta = _auth(usuario_cliente).post(
        f"/api/v1/pedidos/{pedido_con_item.pk}/cancelar/"
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "pedido_no_cancelable"


def test_stock_exacto_se_agota_sin_quedar_negativo(usuario_cliente, pedido_con_item, oferta):
    cantidad = pedido_con_item.detalles.first().cantidad
    oferta.stock = cantidad
    oferta.save(update_fields=["stock"])
    otro = Pedido.objects.create(cliente=usuario_cliente, estado_id="pendiente")
    DetallePedido.objects.create(
        pedido=otro,
        oferta=oferta,
        cantidad=1,
        precio_unitario=oferta.precio_vigente,
    )

    primera = _pagar(usuario_cliente, pedido_con_item.pk, clave="stock-unico")
    segunda = _pagar(usuario_cliente, otro.pk, clave="stock-segundo")

    assert primera.status_code == 201
    assert segunda.status_code == 409
    assert segunda.json()["error"]["code"] == "conflicto"
    assert not IntentoPago.objects.filter(pedido=otro).exists()
    oferta.refresh_from_db()
    assert oferta.stock == 0
    assert Venta.objects.count() == 1
    assert MovimientoInventarioOfertaVideojuego.objects.count() == 1
