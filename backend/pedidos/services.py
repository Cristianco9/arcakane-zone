from django.conf import settings
from django.db import transaction

from catalogo.models import OfertaVideojuego

from .models import DetallePedido, Pedido


def get_or_create_carrito(usuario) -> Pedido:
    pedido, _ = Pedido.objects.get_or_create(
        cliente=usuario, estado_id="pendiente"
    )
    return pedido


def limite_cantidad_por_linea() -> int:
    """Tope configurable de unidades por línea del carrito."""
    return max(1, settings.CARRITO_MAX_CANTIDAD_POR_LINEA)


def motivo_indisponibilidad(detalle: DetallePedido) -> str | None:
    """Devuelve ``sin_stock``, ``titulo_inactivo``, ``oferta_retirada`` o ``None``."""
    oferta = detalle.oferta
    if not oferta.videojuego.activo:
        return "titulo_inactivo"
    if not oferta.esta_publicada:
        return "oferta_retirada"
    if oferta.stock < detalle.cantidad:
        return "sin_stock"
    return None


def _datos_linea(detalle: DetallePedido) -> dict:
    return {
        "detalle_id": detalle.pk,
        "titulo": detalle.titulo_snapshot,
        "plataforma": detalle.plataforma_snapshot,
        "cantidad": detalle.cantidad,
    }


@transaction.atomic
def revalidar_carrito(pedido: Pedido, sincronizar: bool = True) -> list[dict]:
    """Revisa cada línea del carrito frente al catálogo vigente.

    Con ``sincronizar=True`` (uso de ``GET /carrito/``) actualiza el precio
    congelado de las líneas pendientes para que el cliente vea el total real.
    Con ``sincronizar=False`` (checkout/pago) solo informa: cualquier cambio
    pendiente de confirmación debe bloquear la operación.
    """
    ajustes = []
    a_actualizar = []
    detalles = pedido.detalles.select_related(
        "oferta__videojuego", "oferta__plataforma"
    ).all()

    for detalle in detalles:
        oferta = detalle.oferta
        motivo = motivo_indisponibilidad(detalle)

        if motivo == "sin_stock":
            ajustes.append(
                {
                    "codigo": "sin_stock",
                    **_datos_linea(detalle),
                    "stock": oferta.stock,
                    "mensaje": (
                        f'"{detalle.titulo_snapshot}": stock insuficiente '
                        f"(tienes {detalle.cantidad} en el carrito, quedan {oferta.stock})."
                    ),
                }
            )
        elif motivo is not None:
            etiqueta = (
                "el título está dado de baja"
                if motivo == "titulo_inactivo"
                else "la oferta ya no está publicada"
            )
            ajustes.append(
                {
                    "codigo": "no_disponible",
                    **_datos_linea(detalle),
                    "motivo": motivo,
                    "mensaje": (
                        f'"{detalle.titulo_snapshot}" ya no está disponible: '
                        f"{etiqueta}."
                    ),
                }
            )

        if detalle.precio_unitario != oferta.precio_vigente:
            anterior = str(detalle.precio_unitario)
            nuevo = str(oferta.precio_vigente)
            ajustes.append(
                {
                    "codigo": "precio_cambiado",
                    **_datos_linea(detalle),
                    "precio_anterior": anterior,
                    "precio_nuevo": nuevo,
                    "mensaje": (
                        f'"{detalle.titulo_snapshot}": el precio cambió '
                        f"de {anterior} a {nuevo}."
                    ),
                }
            )
            if sincronizar and pedido.estado_id == "pendiente":
                detalle.precio_unitario = oferta.precio_vigente
                a_actualizar.append(detalle)

    if a_actualizar:
        DetallePedido.objects.bulk_update(a_actualizar, ["precio_unitario"])
    return ajustes


def validar_para_checkout(pedido: Pedido) -> list[str]:
    """Errores legibles para el checkout HTML; vacía = todo OK."""
    if not pedido.detalles.exists():
        return ["El carrito está vacío."]
    return [
        ajuste["mensaje"]
        for ajuste in revalidar_carrito(pedido, sincronizar=False)
    ]


@transaction.atomic
def agregar_o_incrementar(usuario, oferta_id: int, cantidad: int = 1) -> tuple[bool, str]:
    """Agrega una oferta al carrito o incrementa su cantidad. Valida límites y stock."""
    try:
        oferta = (
            OfertaVideojuego.objects.select_for_update()
            .select_related("videojuego", "plataforma")
            .get(pk=oferta_id)
        )
    except OfertaVideojuego.DoesNotExist:
        return False, "Oferta no encontrada."

    limite = limite_cantidad_por_linea()
    if cantidad > limite:
        return False, f"La cantidad máxima por línea es {limite}."
    if not oferta.videojuego.activo:
        return False, f'"{oferta.videojuego.titulo}" no está disponible.'
    if not oferta.esta_publicada:
        return False, f'"{oferta.videojuego.titulo}" ya no está publicada.'
    if oferta.stock <= 0:
        return False, f'"{oferta.videojuego.titulo}" no tiene stock disponible.'

    pedido = get_or_create_carrito(usuario)
    detalle = (
        DetallePedido.objects.select_for_update()
        .filter(pedido=pedido, oferta=oferta)
        .first()
    )
    cantidad_actual = detalle.cantidad if detalle is not None else 0
    nueva_cantidad = cantidad_actual + cantidad
    if nueva_cantidad > limite:
        return False, f"La cantidad máxima por línea es {limite}."
    if nueva_cantidad > oferta.stock:
        return False, f'Stock insuficiente. Máximo disponible: {oferta.stock}.'

    if detalle is None:
        # La línea nueva nace con la cantidad solicitada: nunca con 0.
        DetallePedido.objects.create(
            pedido=pedido,
            oferta=oferta,
            precio_unitario=oferta.precio_vigente,
            cantidad=cantidad,
        )
    else:
        detalle.cantidad = nueva_cantidad
        detalle.save(update_fields=["cantidad"])
    return True, (
        f'"{oferta.videojuego.titulo}" ({oferta.plataforma.nombre}) '
        "agregado al carrito."
    )


@transaction.atomic
def actualizar_cantidad(usuario, detalle_id: int, cantidad: int) -> tuple[bool, str]:
    """Cambia la cantidad de un ítem. Si cantidad <= 0, lo elimina."""
    try:
        detalle = (
            DetallePedido.objects.select_for_update()
            .select_related("oferta__videojuego")
            .get(
                pk=detalle_id,
                pedido__cliente=usuario,
                pedido__estado_id="pendiente",
            )
        )
    except DetallePedido.DoesNotExist:
        return False, "Ítem no encontrado."

    if cantidad <= 0:
        detalle.delete()
        return True, "Ítem eliminado del carrito."

    limite = limite_cantidad_por_linea()
    if cantidad > limite:
        return False, f"La cantidad máxima por línea es {limite}."
    oferta = detalle.oferta
    if not oferta.videojuego.activo or not oferta.esta_publicada:
        return False, f'"{detalle.titulo_snapshot}" ya no está disponible.'

    stock = oferta.stock
    if cantidad > stock:
        return False, f'Stock insuficiente. Máximo disponible: {stock}.'

    detalle.cantidad = cantidad
    detalle.save(update_fields=["cantidad"])
    return True, "Cantidad actualizada."


@transaction.atomic
def quitar_item(usuario, detalle_id: int) -> tuple[bool, str]:
    try:
        detalle = DetallePedido.objects.get(
            pk=detalle_id, pedido__cliente=usuario, pedido__estado_id="pendiente"
        )
        detalle.delete()
        return True, "Ítem eliminado."
    except DetallePedido.DoesNotExist:
        return False, "Ítem no encontrado."


@transaction.atomic
def cancelar_pedido(pedido: Pedido) -> tuple[bool, str]:
    """Cancela un pedido pendiente revalidando su fila bajo bloqueo."""
    bloqueado = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if bloqueado.estado_id != "pendiente":
        return False, "Solo se pueden cancelar pedidos en estado pendiente."
    bloqueado.estado_id = "cancelado"
    bloqueado.save(update_fields=["estado"])
    pedido.estado_id = "cancelado"
    return True, f"Pedido #{pedido.pk} cancelado correctamente."
