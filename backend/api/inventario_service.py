"""Servicio de escritura del libro mayor de inventario (AZ-S2-BE-03).

Es el único punto de la aplicación que cambia ``OfertaVideojuego.stock`` y
escribe su movimiento asociado. El stock y el movimiento se escriben en la
MISMA transacción y la oferta se bloquea con ``select_for_update`` para que
los saldos corridos sean correctos bajo concurrencia.
"""
from uuid import uuid4

from django.db import IntegrityError, transaction
from rest_framework import status

from catalogo.models import OfertaVideojuego
from inventario.models import (
    MotivoMovimientoInventario,
    MovimientoInventarioOfertaVideojuego,
    TipoMovimientoInventario,
)

from .exceptions import ErrorDeNegocio

NATURALEZA = TipoMovimientoInventario.Naturaleza


class StockInsuficiente(ErrorDeNegocio):
    """El movimiento dejaría un saldo negativo: 409 con código estable."""

    status_code = status.HTTP_409_CONFLICT
    default_code = "stock_insuficiente"
    default_detail = (
        "No hay stock suficiente: la operación dejaría el inventario negativo."
    )

    def __init__(self, detalle=None):
        super().__init__(detalle or self.default_detail)


@transaction.atomic
def registrar_movimiento(
    oferta,
    cantidad,
    tipo_codigo,
    motivo_codigo=None,
    usuario=None,
    detalle_pedido=None,
    clave_idempotencia=None,
    observacion="",
):
    """Aplica ``cantidad`` según la naturaleza del tipo y escribe el ledger.

    Devuelve ``(movimiento, creado)``. Si la clave de idempotencia o el detalle
    de pedido ya están registrados, devuelve el movimiento existente sin volver
    a tocar el stock: el propio libro mayor es la fuente de verdad de la
    idempotencia.
    """
    if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
        raise ValueError("La cantidad del movimiento debe ser un entero positivo.")

    clave = (clave_idempotencia or "").strip() or f"auto-{uuid4().hex}"

    if detalle_pedido is not None:
        existente = MovimientoInventarioOfertaVideojuego.objects.filter(
            detalle_pedido=detalle_pedido
        ).first()
        if existente is not None:
            return existente, False

    existente = MovimientoInventarioOfertaVideojuego.objects.filter(
        clave_idempotencia=clave
    ).first()
    if existente is not None:
        return existente, False

    tipo = TipoMovimientoInventario.objects.get(codigo=tipo_codigo)
    motivo = None
    if motivo_codigo:
        motivo = MotivoMovimientoInventario.objects.get(codigo=motivo_codigo)

    # Bloquear la fila antes de leer el saldo y volver a comprobar la clave
    # bajo el bloqueo: dos peticiones concurrentes no pueden duplicar el ledger.
    oferta_bloqueada = OfertaVideojuego.objects.select_for_update().get(pk=oferta.pk)
    existente = MovimientoInventarioOfertaVideojuego.objects.filter(
        clave_idempotencia=clave
    ).first()
    if existente is not None:
        return existente, False

    anterior = oferta_bloqueada.stock
    if tipo.naturaleza == NATURALEZA.ENTRADA:
        posterior = anterior + cantidad
    elif tipo.naturaleza == NATURALEZA.SALIDA:
        posterior = anterior - cantidad
        if posterior < 0:
            raise StockInsuficiente(
                f"No hay stock suficiente en «{oferta_bloqueada}»: "
                f"hay {anterior} unidades y se requieren {cantidad}."
            )
    elif tipo.naturaleza == NATURALEZA.AJUSTE:
        # Un AJUSTE fija el saldo absoluto (apertura o reconteo); no se usa
        # para ajustes relativos, que son ENTRADA/SALIDA.
        posterior = cantidad
    else:
        raise ValueError(f"Naturaleza de movimiento no soportada: {tipo.naturaleza}")

    try:
        with transaction.atomic():
            movimiento = MovimientoInventarioOfertaVideojuego.objects.create(
                oferta=oferta_bloqueada,
                tipo_movimiento=tipo,
                motivo=motivo,
                observacion=observacion,
                cantidad=cantidad,
                saldo_anterior=anterior,
                saldo_posterior=posterior,
                usuario_responsable=usuario,
                detalle_pedido=detalle_pedido,
                clave_idempotencia=clave,
            )
            oferta_bloqueada.stock = posterior
            oferta_bloqueada.save(update_fields=["stock"])
    except IntegrityError:
        # Otra transacción ganó la carrera por la clave o por el detalle.
        existente = MovimientoInventarioOfertaVideojuego.objects.filter(
            clave_idempotencia=clave
        ).first()
        if existente is None and detalle_pedido is not None:
            existente = MovimientoInventarioOfertaVideojuego.objects.filter(
                detalle_pedido=detalle_pedido
            ).first()
        if existente is None:
            raise
        return existente, False

    oferta.stock = posterior
    return movimiento, True


def registrar_ajuste(
    oferta,
    cantidad,
    motivo_codigo="AJUSTE_FISICO",
    usuario=None,
    nota="",
    clave_idempotencia=None,
    carga_inicial=False,
):
    """Ajuste relativo: positivo suma (ENTRADA), negativo resta (SALIDA)."""
    if not isinstance(cantidad, int) or isinstance(cantidad, bool):
        raise ValueError("La cantidad del ajuste debe ser un entero.")
    if cantidad == 0:
        raise ValueError("La cantidad del ajuste debe ser distinta de cero.")

    tipo_codigo = "ENTRADA" if cantidad > 0 else "SALIDA"
    motivo = "CARGA_INICIAL" if carga_inicial else motivo_codigo
    return registrar_movimiento(
        oferta=oferta,
        cantidad=abs(cantidad),
        tipo_codigo=tipo_codigo,
        motivo_codigo=motivo,
        usuario=usuario,
        observacion=nota,
        clave_idempotencia=clave_idempotencia,
    )
