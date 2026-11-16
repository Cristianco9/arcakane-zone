"""Fixtures compartidos para toda la suite de pruebas."""
import uuid
from decimal import Decimal

import pytest
from django.db import DatabaseError, transaction

from catalogo.models import (
    Categoria,
    EstadoPublicacion,
    Genero,
    OfertaVideojuego,
    Plataforma,
    Videojuego,
    VideojuegoCategoria,
    VideojuegoGenero,
)
from cuentas.models import Rol, Usuario
from inventario.models import (
    MotivoMovimientoInventario,
    MovimientoInventarioOfertaVideojuego,
    TipoMovimientoInventario,
)
from pagos.models import EstadoIntentoPago
from pedidos.models import DetallePedido, EstadoPedido, Pedido


# ── Catálogos de estado (AZ-S1-17) ────────────────────────────────────────────

ESTADOS_PEDIDO = [
    ("pendiente", "Pendiente"),
    ("pagado", "Pagado"),
    ("cancelado", "Cancelado"),
]
ESTADOS_INTENTO_PAGO = [
    ("aprobado", "Aprobado"),
    ("rechazado", "Rechazado"),
    ("pendiente", "Pendiente"),
]
ESTADOS_PUBLICACION = [
    ("borrador", "Borrador"),
    ("publicado", "Publicado"),
    ("retirado", "Retirado"),
]


@pytest.fixture(autouse=True)
def estados_catalogo(db):
    """Siembra idempotente de los catálogos de estado.

    Las pruebas transaccionales hacen flush y los vacían; esta fixture los
    repone antes de cada prueba (AZ-S1-17). Si el esquema aún no tiene las
    tablas (p. ej. durante pruebas de migraciones intermedias), no hace nada.
    """
    for modelo, filas in [
        (EstadoPedido, ESTADOS_PEDIDO),
        (EstadoIntentoPago, ESTADOS_INTENTO_PAGO),
        (EstadoPublicacion, ESTADOS_PUBLICACION),
    ]:
        try:
            with transaction.atomic():
                for codigo, nombre in filas:
                    modelo.objects.get_or_create(
                        codigo=codigo, defaults={"nombre": nombre}
                    )
        except DatabaseError:
            # La tabla del catálogo no existe en este estado de migración.
            pass


# ── Roles (AZ-S1-18) ─────────────────────────────────────────────────────────

ROLES_BASE = [("cliente", "Cliente"), ("administrador", "Administrador")]


@pytest.fixture(autouse=True)
def roles_catalogo(db):
    """Siembra idempotente de roles base.

    Las pruebas transaccionales hacen flush y los vacían; esta fixture los
    repone. Tolerante a esquemas intermedios durante pruebas de migraciones.
    """
    for codigo, nombre in ROLES_BASE:
        try:
            with transaction.atomic():
                Rol.objects.get_or_create(
                    codigo=codigo, defaults={"nombre": nombre}
                )
        except (DatabaseError, TypeError):
            # Esquema intermedio (p. ej. sin columna codigo) o tabla inexistente.
            pass


@pytest.fixture
def rol_cliente(db):
    try:
        return Rol.objects.get(codigo="cliente")
    except Exception:
        return Rol.objects.create(codigo="cliente", nombre="Cliente")


@pytest.fixture
def rol_admin(db):
    try:
        return Rol.objects.get(codigo="administrador")
    except Exception:
        return Rol.objects.create(codigo="administrador", nombre="Administrador")


# ── Usuarios ─────────────────────────────────────────────────────────────────

@pytest.fixture
def usuario_cliente(db, rol_cliente):
    u = Usuario.objects.create_user(
        username="cliente_test",
        password="pass1234!",
        email="cliente@test.com",
    )
    u.roles.add(rol_cliente)
    return u


@pytest.fixture
def usuario_admin(db, rol_admin):
    u = Usuario.objects.create_user(
        username="admin_test",
        password="pass1234!",
        email="admin@test.com",
        is_staff=True,
    )
    u.roles.add(rol_admin)
    return u


# ── Catálogo ─────────────────────────────────────────────────────────────────

@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre="Acción")


@pytest.fixture
def plataforma(db):
    return Plataforma.objects.create(nombre="PC")


@pytest.fixture
def plataforma_alternativa(db):
    return Plataforma.objects.create(nombre="PlayStation 5")


@pytest.fixture
def genero(db):
    return Genero.objects.create(nombre="RPG")


@pytest.fixture
def videojuego(db, categoria, genero):
    juego = Videojuego.objects.create(titulo="Juego Alpha", activo=True)
    VideojuegoCategoria.objects.create(videojuego=juego, categoria=categoria)
    VideojuegoGenero.objects.create(videojuego=juego, genero=genero)
    return juego


@pytest.fixture
def oferta(db, videojuego, plataforma):
    """Oferta publicada con stock: la unidad vendible por defecto."""
    return OfertaVideojuego.objects.create(
        videojuego=videojuego,
        plataforma=plataforma,
        precio_vigente=Decimal("80000"),
        stock=10,
        sku="AZ-0001-001",
        estado_publicacion_id="publicado",
    )


@pytest.fixture
def oferta_agotada(db, videojuego, plataforma):
    """Oferta publicada pero sin stock."""
    return OfertaVideojuego.objects.create(
        videojuego=videojuego,
        plataforma=plataforma,
        precio_vigente=Decimal("60000"),
        stock=0,
        sku="AZ-0002-001",
        estado_publicacion_id="publicado",
    )


# ── Pedido con un ítem ────────────────────────────────────────────────────────

@pytest.fixture
def pedido_con_item(db, usuario_cliente, oferta):
    pedido = Pedido.objects.create(cliente=usuario_cliente, estado_id="pendiente")
    DetallePedido.objects.create(
        pedido=pedido,
        oferta=oferta,
        cantidad=2,
        precio_unitario=oferta.precio_vigente,
    )
    return pedido


# ── Inventario (AZ-S1-14) ──────────────────────────────────────────────────────


@pytest.fixture
def tipo_entrada(db):
    """Tipo de movimiento de entrada (get_or_create: tolera la semilla 0002)."""
    return TipoMovimientoInventario.objects.get_or_create(
        codigo="ENTRADA",
        defaults={"nombre": "Entrada", "naturaleza": "entrada"},
    )[0]


@pytest.fixture
def tipo_salida(db):
    return TipoMovimientoInventario.objects.get_or_create(
        codigo="SALIDA",
        defaults={"nombre": "Salida", "naturaleza": "salida"},
    )[0]


@pytest.fixture
def tipo_ajuste(db):
    return TipoMovimientoInventario.objects.get_or_create(
        codigo="AJUSTE",
        defaults={"nombre": "Ajuste", "naturaleza": "ajuste"},
    )[0]


@pytest.fixture
def motivo_venta(db):
    return MotivoMovimientoInventario.objects.get_or_create(
        codigo="VENTA", defaults={"nombre": "Venta"}
    )[0]


@pytest.fixture
def movimiento_entrada(oferta, tipo_entrada):
    """Movimiento válido del ledger sobre la oferta con stock 10."""
    return MovimientoInventarioOfertaVideojuego.objects.create(
        oferta=oferta,
        tipo_movimiento=tipo_entrada,
        cantidad=5,
        saldo_anterior=10,
        saldo_posterior=15,
        clave_idempotencia=f"test-entrada-{uuid.uuid4()}",
    )
