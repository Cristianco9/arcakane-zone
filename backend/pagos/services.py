import random
import uuid
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from api.exceptions import (
    ClaveIdempotenciaEnUso,
    ErrorDeNegocio,
    PedidoNoPagable,
    PedidoYaPagado,
)
from api.inventario_service import StockInsuficiente, registrar_movimiento
from catalogo.models import OfertaVideojuego
from pedidos.models import Pedido
from pedidos.services import revalidar_carrito

from .models import IntentoPago, Venta


@dataclass(frozen=True)
class ResultadoPago:
    """Resultado del cobro: el intento guardado es la fuente de la respuesta."""

    intento: IntentoPago
    mensaje: str
    repetido: bool = False

    @property
    def exito(self) -> bool:
        return self.intento.estado_id == "aprobado"


def aprobacion_simulada() -> bool:
    """Único punto de decisión aleatoria (90% de aprobación)."""
    return random.random() < 0.9


def clave_idempotencia_para(usuario_id: int, clave: str | None) -> str:
    """Prefija la clave con el usuario y valida el máximo del modelo."""
    if clave is None:
        return ""
    valor = clave.strip()
    if not valor:
        raise ValidationError({"Idempotency-Key": "La clave no puede estar vacía."})
    prefijo = f"u{usuario_id}:"
    maximo = IntentoPago._meta.get_field("clave_idempotencia").max_length
    if len(prefijo) + len(valor) > maximo:
        raise ValidationError(
            {
                "Idempotency-Key": (
                    f"La clave es demasiado larga (máximo {maximo - len(prefijo)} caracteres)."
                )
            }
        )
    return f"{prefijo}{valor}"


def mensaje_para(intento: IntentoPago) -> str:
    """Reconstruye el mensaje original sin leer estado fuera del intento."""
    if intento.estado_id == "aprobado":
        return f"¡Pago aprobado! Referencia: {intento.referencia}"
    return f"Pago rechazado (ref: {intento.referencia}). Intenta de nuevo."


@transaction.atomic
def procesar_pago(pedido: Pedido, *, clave_idempotencia: str = "") -> ResultadoPago:
    """Cobra un pedido bajo bloqueo: primero el pedido, luego las ofertas."""
    # 1) La fila del pedido se bloquea primero y es la única fuente de verdad.
    bloqueado = (
        Pedido.objects.select_for_update()
        .select_related("cliente")
        .get(pk=pedido.pk)
    )

    # 2) Con clave, una repetición se resuelve antes de cualquier reproceso.
    if clave_idempotencia:
        repetido = (
            IntentoPago.objects.select_related("pedido", "pedido__cliente")
            .filter(clave_idempotencia=clave_idempotencia)
            .first()
        )
        if repetido is not None:
            if repetido.pedido_id != bloqueado.pk:
                raise ClaveIdempotenciaEnUso()
            return ResultadoPago(repetido, mensaje_para(repetido), repetido=True)

    # 3) Revalidar el estado leído BAJO el bloqueo, nunca la instancia de fuera.
    if bloqueado.estado_id == "pagado":
        raise PedidoYaPagado()
    if bloqueado.estado_id != "pendiente":
        raise PedidoNoPagable()

    ajustes = revalidar_carrito(bloqueado, sincronizar=False)
    if ajustes:
        raise ErrorDeNegocio(
            "El carrito cambió desde la última consulta. "
            "Vuelve a GET /carrito/ para confirmar los ajustes antes de pagar.",
            extra={
                "ajustes": ajustes,
                "errores": [ajuste["mensaje"] for ajuste in ajustes],
            },
        )

    # 4) Orden fijo de bloqueo de ofertas para no interbloquear con otros pagos.
    detalles = list(bloqueado.detalles.select_related("oferta__videojuego").all())
    ofertas_ids = sorted({detalle.oferta_id for detalle in detalles})
    ofertas = {
        oferta.pk: oferta
        for oferta in OfertaVideojuego.objects.select_for_update()
        .filter(pk__in=ofertas_ids)
        .order_by("pk")
    }
    for detalle in detalles:
        oferta = ofertas.get(detalle.oferta_id)
        if oferta is None or oferta.stock < detalle.cantidad:
            raise ErrorDeNegocio(
                f"Sin stock suficiente para '{detalle.titulo_snapshot}'."
            )

    aprobado = aprobacion_simulada()
    referencia = str(uuid.uuid4())[:8].upper()

    try:
        # Punto de salvaguarda: si la única condicional o la 1:1 de Venta
        # colisionan, se lee la fila ganadora sin romper la transacción exterior.
        with transaction.atomic():
            intento = IntentoPago.objects.create(
                pedido=bloqueado,
                importe=bloqueado.total,
                estado_id="aprobado" if aprobado else "rechazado",
                referencia=referencia,
                clave_idempotencia=clave_idempotencia,
            )
            if aprobado:
                try:
                    for detalle in detalles:
                        registrar_movimiento(
                            oferta=ofertas[detalle.oferta_id],
                            cantidad=detalle.cantidad,
                            tipo_codigo="SALIDA",
                            motivo_codigo="VENTA",
                            usuario=bloqueado.cliente,
                            detalle_pedido=detalle,
                            clave_idempotencia=f"venta-detalle-{detalle.pk}",
                            observacion=f"Venta del pedido #{bloqueado.pk}",
                        )
                except StockInsuficiente as exc:
                    raise ErrorDeNegocio(str(exc)) from exc

                bloqueado.estado_id = "pagado"
                bloqueado.save(update_fields=["estado"])
                Venta.objects.create(
                    pedido=bloqueado,
                    intento_aprobado=intento,
                    total=bloqueado.total,
                )
    except IntegrityError as exc:
        if not clave_idempotencia:
            raise
        ganador = (
            IntentoPago.objects.select_related("pedido", "pedido__cliente")
            .filter(clave_idempotencia=clave_idempotencia)
            .first()
        )
        if ganador is None:
            raise
        if ganador.pedido_id != bloqueado.pk:
            raise ClaveIdempotenciaEnUso() from exc
        return ResultadoPago(ganador, mensaje_para(ganador), repetido=True)

    return ResultadoPago(intento, mensaje_para(intento))


def procesar_pago_simulado(pedido: Pedido) -> tuple[bool, str]:
    """Firma histórica usada por el checkout HTML y las pruebas existentes."""
    try:
        resultado = procesar_pago(pedido)
    except ErrorDeNegocio as exc:
        return False, str(exc.detail)
    return resultado.exito, resultado.mensaje
