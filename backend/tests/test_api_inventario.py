"""Pruebas del libro mayor por API, integración y comando de conciliación."""
from datetime import timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.contrib import admin
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.forms import inlineformset_factory
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.test import APIClient

from api.inventario_service import registrar_ajuste, registrar_movimiento
from catalogo.admin import OfertaVideojuegoAdmin, VideojuegoAdmin
from catalogo.models import OfertaVideojuego, Videojuego
from inventario.models import MovimientoInventarioOfertaVideojuego
from pagos.services import procesar_pago_simulado
from pedidos.services import cancelar_pedido


pytestmark = pytest.mark.django_db


def _client(usuario=None):
    client = APIClient()
    if usuario is not None:
        client.force_authenticate(usuario)
    return client


def _movimiento(
    oferta,
    tipo,
    motivo=None,
    usuario=None,
    cantidad=1,
    anterior=10,
    posterior=9,
    fecha=None,
    detalle=None,
    clave=None,
):
    return MovimientoInventarioOfertaVideojuego.objects.create(
        oferta=oferta,
        tipo_movimiento=tipo,
        motivo=motivo,
        cantidad=cantidad,
        saldo_anterior=anterior,
        saldo_posterior=posterior,
        usuario_responsable=usuario,
        detalle_pedido=detalle,
        fecha_hora=fecha or timezone.now(),
        clave_idempotencia=clave or f"test-{uuid4().hex}",
    )


# ── Consulta del libro mayor ───────────────────────────────────────────────────


def test_listado_solo_administracion(usuario_cliente, usuario_admin):
    url = "/api/v1/inventario/movimientos/"

    anonimo = _client().get(url)
    cliente = _client(usuario_cliente).get(url)
    administrador = _client(usuario_admin).get(url)

    assert anonimo.status_code == 401
    assert anonimo.json()["error"]["code"] == "no_autenticado"
    assert cliente.status_code == 403
    assert cliente.json()["error"]["code"] == "permiso_denegado"
    assert administrador.status_code == 200
    assert administrador.json()["success"] is True
    assert administrador.json()["data"] == []


def test_listado_detalle_y_405_en_escritura(
    usuario_admin, oferta, tipo_entrada, motivo_ajuste_fisico
):
    movimiento = _movimiento(
        oferta, tipo_entrada, motivo_ajuste_fisico, usuario_admin, posterior=11
    )
    client = _client(usuario_admin)

    lista = client.get("/api/v1/inventario/movimientos/")
    detalle = client.get(f"/api/v1/inventario/movimientos/{movimiento.pk}/")

    assert lista.status_code == 200
    assert lista.json()["pagination"]["count"] == 1
    assert detalle.status_code == 200
    datos = detalle.json()["data"]
    assert datos["id"] == movimiento.pk
    assert datos["tipo"] == "ENTRADA"
    assert datos["motivo"] == "AJUSTE_FISICO"
    assert datos["usuario"] == usuario_admin.username
    assert datos["oferta_sku"] == oferta.sku

    url = f"/api/v1/inventario/movimientos/{movimiento.pk}/"
    for metodo in ("put", "patch", "delete"):
        respuesta = getattr(client, metodo)(url, {})
        assert respuesta.status_code == 405
        assert respuesta.json()["error"]["code"] == "metodo_no_permitido"


def test_filtros_y_combinaciones(
    usuario_admin,
    usuario_cliente,
    oferta,
    videojuego,
    plataforma_alternativa,
    tipo_entrada,
    tipo_salida,
    motivo_venta,
    motivo_ajuste_fisico,
    motivo_carga_inicial,
    pedido_con_item,
):
    otra = OfertaVideojuego.objects.create(
        videojuego=videojuego,
        plataforma=plataforma_alternativa,
        precio_vigente=Decimal("1000"),
        stock=4,
        sku="AZ-FILTRO-002",
        estado_publicacion_id="publicado",
    )
    ahora = timezone.now()
    m1 = _movimiento(
        oferta,
        tipo_entrada,
        motivo_ajuste_fisico,
        usuario_admin,
        cantidad=2,
        posterior=12,
        fecha=ahora - timedelta(days=3),
    )
    m2 = _movimiento(
        oferta,
        tipo_salida,
        motivo_venta,
        usuario_cliente,
        cantidad=2,
        posterior=8,
        fecha=ahora - timedelta(days=2),
        detalle=pedido_con_item.detalles.first(),
    )
    m3 = _movimiento(
        otra,
        tipo_entrada,
        motivo_carga_inicial,
        usuario_admin,
        cantidad=4,
        anterior=0,
        posterior=4,
        fecha=ahora - timedelta(days=1),
    )
    client = _client(usuario_admin)

    def ids(query):
        respuesta = client.get(f"/api/v1/inventario/movimientos/?{query}")
        assert respuesta.status_code == 200
        return [item["id"] for item in respuesta.json()["data"]]

    assert ids(f"oferta={oferta.pk}") == [m2.pk, m1.pk]
    assert ids("tipo=SALIDA") == [m2.pk]
    assert ids("motivo=VENTA") == [m2.pk]
    assert ids(f"pedido={pedido_con_item.pk}") == [m2.pk]
    assert ids(f"usuario={usuario_cliente.pk}") == [m2.pk]
    assert ids(f"tipo=ENTRADA&usuario={usuario_admin.pk}") == [m3.pk, m1.pk]
    assert ids(f"oferta={oferta.pk}&tipo=ENTRADA") == [m1.pk]

    desde = (ahora - timedelta(days=2, hours=1)).isoformat().replace("+00:00", "Z")
    hasta = (ahora - timedelta(days=2, hours=-1)).isoformat().replace("+00:00", "Z")
    assert ids(f"desde={desde}&hasta={hasta}") == [m2.pk]


def test_filtros_invalidos_devuelven_400(usuario_admin):
    client = _client(usuario_admin)
    url = "/api/v1/inventario/movimientos/"

    for query, campo in [
        ("desde=2026-99-99", "desde"),
        ("desde=2026-02-02T00:00:00Z&hasta=2026-01-01T00:00:00Z", "hasta"),
        ("tipo=NOEXISTE", "tipo"),
        ("pedido=abc", "pedido"),
    ]:
        respuesta = client.get(f"{url}?{query}")
        assert respuesta.status_code == 400
        assert respuesta.json()["error"]["code"] == "datos_invalidos"
        assert campo in respuesta.json()["error"]["details"]


def test_paginacion_y_orden_mas_reciente_primero(
    usuario_admin, oferta, tipo_entrada
):
    ahora = timezone.now()
    antiguo = _movimiento(
        oferta, tipo_entrada, fecha=ahora - timedelta(days=3), posterior=11
    )
    medio = _movimiento(
        oferta, tipo_entrada, fecha=ahora - timedelta(days=2), posterior=12
    )
    reciente = _movimiento(
        oferta, tipo_entrada, fecha=ahora - timedelta(days=1), posterior=13
    )
    client = _client(usuario_admin)

    primera = client.get("/api/v1/inventario/movimientos/?page_size=2").json()
    segunda = client.get(
        "/api/v1/inventario/movimientos/?page_size=2&page=2"
    ).json()

    assert primera["pagination"]["count"] == 3
    assert primera["pagination"]["total_pages"] == 2
    assert [m["id"] for m in primera["data"]] == [reciente.pk, medio.pk]
    assert [m["id"] for m in segunda["data"]] == [antiguo.pk]


def test_trazabilidad_por_oferta(
    usuario_admin,
    usuario_cliente,
    oferta,
    oferta_agotada,
    tipo_entrada,
):
    propio = _movimiento(oferta, tipo_entrada, posterior=11)
    _movimiento(oferta_agotada, tipo_entrada, anterior=0, posterior=1)
    url = f"/api/v1/catalogo/ofertas/{oferta.pk}/movimientos/"

    respuesta = _client(usuario_admin).get(url)

    assert respuesta.status_code == 200
    assert respuesta.json()["pagination"]["count"] == 1
    assert respuesta.json()["data"][0]["id"] == propio.pk
    assert _client().get(url).status_code == 401
    assert _client(usuario_cliente).get(url).status_code == 403

    inexistente = _client(usuario_admin).get(
        "/api/v1/catalogo/ofertas/999999/movimientos/"
    )
    assert inexistente.status_code == 404
    assert inexistente.json()["error"]["code"] == "no_encontrado"


# ── Ajustes manuales ──────────────────────────────────────────────────────────


def test_ajuste_positivo_y_negativo(usuario_admin, oferta):
    client = _client(usuario_admin)
    url = "/api/v1/inventario/ajustes/"

    suma = client.post(
        url,
        {
            "oferta": oferta.pk,
            "cantidad": 3,
            "motivo": "AJUSTE_FISICO",
            "nota": "Conteo de caja",
        },
        format="json",
    )
    resta = client.post(
        url,
        {"oferta": oferta.pk, "cantidad": -2, "motivo": "AJUSTE_FISICO"},
        format="json",
    )

    assert suma.status_code == 201
    assert resta.status_code == 201
    oferta.refresh_from_db()
    assert oferta.stock == 11
    movimientos = list(
        MovimientoInventarioOfertaVideojuego.objects.order_by("fecha_hora", "pk")
    )
    assert len(movimientos) == 2
    assert movimientos[0].tipo_movimiento.codigo == "ENTRADA"
    assert movimientos[0].cantidad == 3
    assert movimientos[0].observacion == "Conteo de caja"
    assert movimientos[1].tipo_movimiento.codigo == "SALIDA"
    assert movimientos[1].cantidad == 2
    assert movimientos[1].saldo_anterior == 13
    assert movimientos[1].saldo_posterior == 11
    assert all(m.usuario_responsable_id == usuario_admin.pk for m in movimientos)
    assert all(m.motivo.codigo == "AJUSTE_FISICO" for m in movimientos)


def test_ajuste_negativo_sin_stock_devuelve_409_sin_efectos(usuario_admin, oferta):
    oferta.stock = 1
    oferta.save(update_fields=["stock"])
    client = _client(usuario_admin)

    respuesta = client.post(
        "/api/v1/inventario/ajustes/",
        {"oferta": oferta.pk, "cantidad": -5, "motivo": "AJUSTE_FISICO"},
        format="json",
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "stock_insuficiente"
    assert "stock" in respuesta.json()["error"]["message"].lower()
    oferta.refresh_from_db()
    assert oferta.stock == 1
    assert MovimientoInventarioOfertaVideojuego.objects.count() == 0


def test_validaciones_del_ajuste(usuario_admin, usuario_cliente, oferta):
    client = _client(usuario_admin)
    url = "/api/v1/inventario/ajustes/"

    cases = [
        ({"oferta": oferta.pk, "cantidad": 0, "motivo": "AJUSTE_FISICO"}, "cantidad"),
        ({"oferta": oferta.pk, "cantidad": 1}, "motivo"),
        (
            {"oferta": oferta.pk, "cantidad": 1, "motivo": "MOTIVO_INEXISTENTE"},
            "motivo",
        ),
        ({"cantidad": 1, "motivo": "AJUSTE_FISICO"}, "oferta"),
    ]
    for cuerpo, campo in cases:
        respuesta = client.post(url, cuerpo, format="json")
        assert respuesta.status_code == 400
        assert respuesta.json()["error"]["code"] == "datos_invalidos"
        assert campo in respuesta.json()["error"]["details"]

    assert MovimientoInventarioOfertaVideojuego.objects.count() == 0
    assert _client(usuario_cliente).post(
        url,
        {"oferta": oferta.pk, "cantidad": 1, "motivo": "AJUSTE_FISICO"},
        format="json",
    ).status_code == 403
    assert _client().post(
        url,
        {"oferta": oferta.pk, "cantidad": 1, "motivo": "AJUSTE_FISICO"},
        format="json",
    ).status_code == 401


def test_idempotencia_del_ajuste(usuario_admin, oferta):
    client = _client(usuario_admin)
    url = "/api/v1/inventario/ajustes/"
    cuerpo = {"oferta": oferta.pk, "cantidad": 2, "motivo": "AJUSTE_FISICO"}

    primera = client.post(url, cuerpo, format="json", HTTP_IDEMPOTENCY_KEY="clave-abc")
    segunda = client.post(url, cuerpo, format="json", HTTP_IDEMPOTENCY_KEY="clave-abc")
    tercera = client.post(url, cuerpo, format="json", HTTP_IDEMPOTENCY_KEY="clave-def")

    assert primera.status_code == segunda.status_code == tercera.status_code == 201
    assert primera.json()["data"]["id"] == segunda.json()["data"]["id"]
    assert "ya estaba registrado" in segunda.json()["message"]
    assert tercera.json()["data"]["id"] != primera.json()["data"]["id"]
    oferta.refresh_from_db()
    assert oferta.stock == 14
    assert MovimientoInventarioOfertaVideojuego.objects.count() == 2


# ── Integración con pago, cancelación y admin ─────────────────────────────────


def test_pago_aprobado_escribe_un_movimiento_con_responsable(
    pedido_con_item, oferta, usuario_cliente
):
    stock_inicial = oferta.stock
    detalle = pedido_con_item.detalles.first()

    with patch("pagos.services.random.random", return_value=0.0):
        exito, _ = procesar_pago_simulado(pedido_con_item)

    assert exito is True
    oferta.refresh_from_db()
    assert oferta.stock == stock_inicial - detalle.cantidad
    movimientos = list(MovimientoInventarioOfertaVideojuego.objects.all())
    assert len(movimientos) == 1
    movimiento = movimientos[0]
    assert movimiento.usuario_responsable_id == usuario_cliente.pk
    assert movimiento.detalle_pedido_id == detalle.pk
    assert movimiento.tipo_movimiento.codigo == "SALIDA"
    assert movimiento.motivo.codigo == "VENTA"
    assert movimiento.saldo_anterior == stock_inicial
    assert movimiento.saldo_posterior == stock_inicial - detalle.cantidad


def test_pago_rechazado_no_escribe_movimiento(pedido_con_item, oferta):
    with patch("pagos.services.random.random", return_value=0.99):
        exito, _ = procesar_pago_simulado(pedido_con_item)

    assert exito is False
    oferta.refresh_from_db()
    assert oferta.stock == 10
    assert MovimientoInventarioOfertaVideojuego.objects.count() == 0


def test_cancelacion_no_cambia_stock_ni_escribe_movimiento(pedido_con_item, oferta):
    exito, _ = cancelar_pedido(pedido_con_item)

    assert exito is True
    oferta.refresh_from_db()
    assert oferta.stock == 10
    assert MovimientoInventarioOfertaVideojuego.objects.count() == 0


def test_ajuste_desde_admin_escribe_un_movimiento(
    usuario_admin, oferta, videojuego, plataforma_alternativa
):
    administrador = OfertaVideojuegoAdmin(OfertaVideojuego, admin.site)
    request = RequestFactory().post("/admin/catalogo/oferta/")
    request.user = usuario_admin

    oferta.stock = 14
    administrador.save_model(request, oferta, None, True)
    oferta.refresh_from_db()
    assert oferta.stock == 14
    movimientos = list(MovimientoInventarioOfertaVideojuego.objects.all())
    assert len(movimientos) == 1
    assert movimientos[0].usuario_responsable_id == usuario_admin.pk
    assert movimientos[0].motivo.codigo == "AJUSTE_FISICO"

    nueva = OfertaVideojuego(
        videojuego=videojuego,
        plataforma=plataforma_alternativa,
        precio_vigente=Decimal("1000"),
        stock=5,
        sku="AZ-ADMIN-NUEVA",
        estado_publicacion_id="publicado",
    )
    administrador.save_model(request, nueva, None, False)
    nueva.refresh_from_db()
    assert nueva.stock == 5
    creacion = MovimientoInventarioOfertaVideojuego.objects.get(oferta=nueva)
    assert creacion.motivo.codigo == "CARGA_INICIAL"
    assert creacion.saldo_posterior == 5


def test_ajuste_desde_inline_admin_escribe_un_movimiento(
    usuario_admin, oferta, videojuego
):
    formset_class = inlineformset_factory(
        Videojuego,
        OfertaVideojuego,
        fields=["plataforma", "sku", "precio_vigente", "stock", "estado_publicacion"],
        extra=0,
    )
    formset = formset_class(
        data={
            "ofertas-TOTAL_FORMS": "1",
            "ofertas-INITIAL_FORMS": "1",
            "ofertas-MIN_NUM_FORMS": "0",
            "ofertas-MAX_NUM_FORMS": "1000",
            "ofertas-0-id": str(oferta.pk),
            "ofertas-0-plataforma": str(oferta.plataforma_id),
            "ofertas-0-sku": oferta.sku,
            "ofertas-0-precio_vigente": "80000",
            "ofertas-0-stock": "13",
            "ofertas-0-estado_publicacion": "publicado",
        },
        instance=videojuego,
        prefix="ofertas",
    )
    assert formset.is_valid(), formset.errors

    request = RequestFactory().post("/admin/catalogo/videojuego/")
    request.user = usuario_admin
    VideojuegoAdmin(Videojuego, admin.site).save_formset(request, None, formset, True)

    oferta.refresh_from_db()
    assert oferta.stock == 13
    movimientos = list(MovimientoInventarioOfertaVideojuego.objects.all())
    assert len(movimientos) == 1
    assert movimientos[0].usuario_responsable_id == usuario_admin.pk
    assert movimientos[0].motivo.codigo == "AJUSTE_FISICO"


def test_listado_no_hace_n_plus_1(usuario_admin, oferta, tipo_entrada):
    for _ in range(3):
        _movimiento(oferta, tipo_entrada, posterior=11)
    client = _client(usuario_admin)

    with CaptureQueriesContext(connection) as consultas:
        respuesta = client.get("/api/v1/inventario/movimientos/")

    assert respuesta.status_code == 200
    assert len(consultas) <= 6


# ── Comando de conciliación ───────────────────────────────────────────────────


def test_comando_consistente(usuario_admin, oferta):
    registrar_movimiento(
        oferta=oferta,
        cantidad=10,
        tipo_codigo="AJUSTE",
        motivo_codigo="CARGA_INICIAL",
        usuario=usuario_admin,
    )
    registrar_ajuste(oferta=oferta, cantidad=2, usuario=usuario_admin)
    salida = StringIO()

    call_command("verificar_inventario", stdout=salida)

    contenido = salida.getvalue()
    assert "Ofertas revisadas: 1" in contenido
    assert "Discrepancias:     0" in contenido
    assert "Inventario conciliado correctamente." in contenido


def test_comando_con_diferencia_devuelve_error(usuario_admin, oferta):
    registrar_movimiento(
        oferta=oferta,
        cantidad=10,
        tipo_codigo="AJUSTE",
        motivo_codigo="CARGA_INICIAL",
        usuario=usuario_admin,
    )
    registrar_ajuste(oferta=oferta, cantidad=2, usuario=usuario_admin)
    OfertaVideojuego.objects.filter(pk=oferta.pk).update(stock=20)
    salida, errores = StringIO(), StringIO()

    with pytest.raises(CommandError) as excinfo:
        call_command("verificar_inventario", stdout=salida, stderr=errores)

    assert "1 discrepancia" in str(excinfo.value)
    contenido = salida.getvalue()
    assert f"Oferta {oferta.pk}" in contenido
    assert "stock registrado=20" in contenido
    assert "suma movimientos=12" in contenido
    assert "diferencia=+8" in contenido


def test_comando_filtro_por_oferta(
    usuario_admin, oferta, videojuego, plataforma_alternativa
):
    registrar_movimiento(
        oferta=oferta,
        cantidad=10,
        tipo_codigo="AJUSTE",
        motivo_codigo="CARGA_INICIAL",
        usuario=usuario_admin,
    )
    otra = OfertaVideojuego.objects.create(
        videojuego=videojuego,
        plataforma=plataforma_alternativa,
        precio_vigente=Decimal("1000"),
        stock=5,
        sku="AZ-COMANDO-002",
        estado_publicacion_id="publicado",
    )
    salida = StringIO()

    call_command("verificar_inventario", "--oferta", str(oferta.pk), stdout=salida)
    assert "Ofertas revisadas: 1" in salida.getvalue()
    assert otra.sku not in salida.getvalue()

    with pytest.raises(CommandError):
        call_command(
            "verificar_inventario", "--oferta", str(otra.pk), stdout=StringIO()
        )
    with pytest.raises(CommandError):
        call_command("verificar_inventario", "--oferta", "999999", stdout=StringIO())
