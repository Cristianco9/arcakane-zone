"""Fixtures compartidos para toda la suite de pruebas."""
import pytest
from decimal import Decimal

from catalogo.models import Categoria, Genero, Plataforma, Videojuego
from cuentas.models import Rol, Usuario
from pedidos.models import DetallePedido, Pedido


# ── Roles ────────────────────────────────────────────────────────────────────

@pytest.fixture
def rol_cliente(db):
    return Rol.objects.create(nombre="cliente")


@pytest.fixture
def rol_admin(db):
    return Rol.objects.create(nombre="administrador")


# ── Usuarios ─────────────────────────────────────────────────────────────────

@pytest.fixture
def usuario_cliente(db, rol_cliente):
    u = Usuario.objects.create_user(
        username="cliente_test",
        password="pass1234!",
        email="cliente@test.com",
        rol=rol_cliente,
    )
    return u


@pytest.fixture
def usuario_admin(db, rol_admin):
    u = Usuario.objects.create_user(
        username="admin_test",
        password="pass1234!",
        email="admin@test.com",
        rol=rol_admin,
        is_staff=True,
    )
    return u


# ── Catálogo ─────────────────────────────────────────────────────────────────

@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre="Acción")


@pytest.fixture
def plataforma(db):
    return Plataforma.objects.create(nombre="PC")


@pytest.fixture
def genero(db):
    return Genero.objects.create(nombre="RPG")


@pytest.fixture
def videojuego(db, categoria, plataforma, genero):
    return Videojuego.objects.create(
        titulo="Juego Alpha",
        precio=Decimal("80000"),
        stock=10,
        activo=True,
        categoria=categoria,
        plataforma=plataforma,
        genero=genero,
    )


@pytest.fixture
def videojuego_agotado(db, categoria, plataforma, genero):
    return Videojuego.objects.create(
        titulo="Juego Agotado",
        precio=Decimal("60000"),
        stock=0,
        activo=True,
        categoria=categoria,
        plataforma=plataforma,
        genero=genero,
    )


# ── Pedido con un ítem ────────────────────────────────────────────────────────

@pytest.fixture
def pedido_con_item(db, usuario_cliente, videojuego):
    pedido = Pedido.objects.create(cliente=usuario_cliente, estado=Pedido.Estado.PENDIENTE)
    DetallePedido.objects.create(
        pedido=pedido,
        videojuego=videojuego,
        cantidad=2,
        precio_unitario=videojuego.precio,
    )
    return pedido
