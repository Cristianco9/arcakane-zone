"""Revalidación de precios y disponibilidad del carrito (AZ-S2-BE-11)."""
from decimal import Decimal

import pytest
from django.test import override_settings

from pedidos.services import (
    actualizar_cantidad,
    agregar_o_incrementar,
    revalidar_carrito,
)

pytestmark = pytest.mark.django_db


def _codigos(ajustes):
    return [ajuste["codigo"] for ajuste in ajustes]


def test_revalidar_sincroniza_el_precio_cambiado(pedido_con_item, oferta):
    detalle = pedido_con_item.detalles.first()
    assert detalle.precio_unitario == Decimal("80000.00")

    oferta.precio_vigente = Decimal("90000.00")
    oferta.save(update_fields=["precio_vigente"])

    ajustes = revalidar_carrito(pedido_con_item)

    assert _codigos(ajustes) == ["precio_cambiado"]
    assert ajustes[0]["precio_anterior"] == "80000.00"
    assert ajustes[0]["precio_nuevo"] == "90000.00"
    assert ajustes[0]["detalle_id"] == detalle.pk

    detalle.refresh_from_db()
    assert detalle.precio_unitario == Decimal("90000.00")
    # Tras sincronizar, una segunda consulta no vuelve a avisar.
    assert revalidar_carrito(pedido_con_item) == []


def test_revalidar_en_checkout_no_modifica_el_precio(pedido_con_item, oferta):
    detalle = pedido_con_item.detalles.first()

    oferta.precio_vigente = Decimal("90000.00")
    oferta.save(update_fields=["precio_vigente"])

    ajustes = revalidar_carrito(pedido_con_item, sincronizar=False)

    assert "precio_cambiado" in _codigos(ajustes)
    detalle.refresh_from_db()
    assert detalle.precio_unitario == Decimal("80000.00")


def test_revalidar_avisa_si_no_hay_stock_para_la_cantidad(pedido_con_item, oferta):
    detalle = pedido_con_item.detalles.first()
    oferta.stock = detalle.cantidad - 1
    oferta.save(update_fields=["stock"])

    ajustes = revalidar_carrito(pedido_con_item, sincronizar=False)

    assert "sin_stock" in _codigos(ajustes)
    assert ajustes[0]["stock"] == detalle.cantidad - 1
    assert "stock insuficiente" in ajustes[0]["mensaje"].lower()


def test_revalidar_avisa_si_el_titulo_esta_inactivo(pedido_con_item, videojuego):
    videojuego.activo = False
    videojuego.save(update_fields=["activo"])

    ajustes = revalidar_carrito(pedido_con_item, sincronizar=False)

    assert "no_disponible" in _codigos(ajustes)
    assert ajustes[0]["motivo"] == "titulo_inactivo"


def test_revalidar_avisa_si_la_oferta_fue_retirada(pedido_con_item, oferta):
    oferta.estado_publicacion_id = "retirado"
    oferta.save(update_fields=["estado_publicacion"])

    ajustes = revalidar_carrito(pedido_con_item, sincronizar=False)

    assert "no_disponible" in _codigos(ajustes)
    assert ajustes[0]["motivo"] == "oferta_retirada"


def test_agregar_rechaza_titulo_inactivo(usuario_cliente, oferta, videojuego):
    videojuego.activo = False
    videojuego.save(update_fields=["activo"])

    exito, mensaje = agregar_o_incrementar(usuario_cliente, oferta.pk, 1)

    assert exito is False
    assert "disponible" in mensaje.lower()


def test_actualizar_cantidad_rechaza_oferta_retirada(usuario_cliente, pedido_con_item, oferta):
    detalle = pedido_con_item.detalles.first()
    oferta.estado_publicacion_id = "retirado"
    oferta.save(update_fields=["estado_publicacion"])

    exito, mensaje = actualizar_cantidad(usuario_cliente, detalle.pk, 1)

    assert exito is False
    assert "disponible" in mensaje.lower()


@override_settings(CARRITO_MAX_CANTIDAD_POR_LINEA=3)
def test_limite_configurable_se_aplica_al_agregar(usuario_cliente, oferta):
    exito, mensaje = agregar_o_incrementar(usuario_cliente, oferta.pk, 4)

    assert exito is False
    assert "máxima por línea" in mensaje.lower()


@override_settings(CARRITO_MAX_CANTIDAD_POR_LINEA=3)
def test_limite_configurable_se_aplica_al_incrementar(usuario_cliente, oferta):
    agregar_o_incrementar(usuario_cliente, oferta.pk, 2)

    exito, mensaje = agregar_o_incrementar(usuario_cliente, oferta.pk, 2)

    assert exito is False
    assert "máxima por línea" in mensaje.lower()


@override_settings(CARRITO_MAX_CANTIDAD_POR_LINEA=3)
def test_limite_configurable_se_aplica_al_actualizar(usuario_cliente, pedido_con_item):
    detalle = pedido_con_item.detalles.first()

    exito, mensaje = actualizar_cantidad(usuario_cliente, detalle.pk, 4)

    assert exito is False
    assert "máxima por línea" in mensaje.lower()
