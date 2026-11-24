"""Matriz única de permisos RBAC de la API v1 (AZ-S2-BE-07).

Cada URL declarada en ``api/urls.py`` tiene una entrada en ``MATRIZ``. Las
vistas usan las clases de ``api.permissions`` derivadas de estas mismas reglas,
y ``generar_tabla_markdown()`` mantiene sincronizado el bloque de documentación
de ``docs/api/API.md``.
"""
from rest_framework.permissions import SAFE_METHODS

# Centinelas legibles para las reglas que no dependen de un rol concreto.
PUBLICO = "publico"
AUTENTICADO = "autenticado"

# Los administradores son superconjunto de cualquier regla (BE-07).
ROL_ADMIN = ("administrador",)
ROLES_GESTION_CATALOGO = ("administrador", "gestor_inventario")
ROLES_GESTION_INVENTARIO = ("administrador", "gestor_inventario")
ROLES_GESTION_CONTACTO = ("administrador", "soporte")
ROLES_LECTURA_CONTACTO = ("administrador", "soporte", "cliente")

# Roles de negocio añadidos por BE-07. Comparten origen con la migración de
# datos, el comando ``seed_catalogo`` y las fixtures de pruebas.
ROLES_NUEVOS = [
    {
        "codigo": "gestor_inventario",
        "nombre": "Gestor de inventario",
        "descripcion": "Gestiona el catálogo y el libro mayor de inventario.",
    },
    {
        "codigo": "soporte",
        "nombre": "Soporte",
        "descripcion": "Atiende y gestiona los mensajes de contacto.",
    },
]

# Jerarquía usada por la administración de cuentas (AZ-S2-BE-08). Un actor no
# puede asignar un rol por encima del suyo; staff/superuser equivale a
# ``administrador`` según la regla de equivalencia de BE-07.
JERARQUIA_ROLES = {
    "cliente": 0,
    "soporte": 1,
    "gestor_inventario": 1,
    "administrador": 2,
}


def regla_de_accion(reglas, accion, metodo):
    """Devuelve la regla de una acción DRF, o ``None`` si no aplica.

    La acción solo sustituye al verbo genérico en métodos de lectura: por
    ejemplo, ``GET /catalogo/videojuegos/{pk}/ofertas/`` es público mientras
    que el resto de métodos del viewset siguen exigiendo administrador o
    gestor de inventario.
    """
    if not accion or not isinstance(reglas, dict) or accion not in reglas:
        return None
    if str(metodo).upper() not in SAFE_METHODS:
        return None
    return reglas[accion]


def _regla_de_metodo(reglas, metodo):
    """Resuelve la regla efectiva de un método a partir de un mapa de reglas."""
    if not isinstance(reglas, dict):
        return reglas
    Metodo = str(metodo).upper()
    if Metodo in reglas:
        return reglas[Metodo]
    return reglas.get("*")


def _entrada(nombre, ruta, reglas, nota="", accion=None):
    return {
        "nombre": nombre,
        "ruta": f"/api/v1/{ruta}",
        "reglas": reglas,
        "nota": nota,
        "accion": accion,
    }


def _simple(nombre, ruta, regla, nota=""):
    return _entrada(nombre, ruta, {"*": regla}, nota=nota)


MATRIZ = [
    _simple("api-root", "", PUBLICO),
    _simple("api-health", "health/", PUBLICO),
    _simple("api-not-found", "{ruta}", PUBLICO, nota="JSON 404"),
    _simple("auth-registro", "auth/registro/", PUBLICO),
    _simple("auth-login", "auth/login/", PUBLICO),
    _simple("auth-logout", "auth/logout/", AUTENTICADO),
    _simple("auth-token-refresh", "auth/token/refresh/", AUTENTICADO),
    _simple("auth-logout-all", "auth/logout-all/", AUTENTICADO),
    _simple("auth-me", "auth/me/", AUTENTICADO),
    _simple("auth-cambiar-password", "auth/me/password/", AUTENTICADO),
    _simple("auth-csrf", "auth/csrf/", PUBLICO),
    _simple("carrito", "carrito/", AUTENTICADO, nota="propietario"),
    _simple("carrito-items", "carrito/items/", AUTENTICADO, nota="propietario"),
    _simple(
        "carrito-item-detalle",
        "carrito/items/{pk}/",
        AUTENTICADO,
        nota="propietario",
    ),
    _simple("inventario-ajuste", "inventario/ajustes/", ROLES_GESTION_INVENTARIO),
    _simple("reporte-dashboard", "reportes/dashboard/", ROL_ADMIN),
    _simple("reporte-ventas", "reportes/ventas/", ROL_ADMIN),
    _simple(
        "reporte-inventario",
        "reportes/inventario/",
        ROLES_GESTION_INVENTARIO,
    ),
    _simple("reporte-videojuegos", "reportes/videojuegos/", ROL_ADMIN),
    _simple("soporte-mayor-informacion", "soporte/mayor-informacion/", PUBLICO),
    _entrada(
        "categoria-list",
        "catalogo/categorias/",
        {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO},
    ),
    _entrada(
        "categoria-detail",
        "catalogo/categorias/{pk}/",
        {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO},
    ),
    _entrada(
        "plataforma-list",
        "catalogo/plataformas/",
        {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO},
    ),
    _entrada(
        "plataforma-detail",
        "catalogo/plataformas/{pk}/",
        {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO},
    ),
    _entrada(
        "genero-list",
        "catalogo/generos/",
        {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO},
    ),
    _entrada(
        "genero-detail",
        "catalogo/generos/{pk}/",
        {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO},
    ),
    _entrada(
        "videojuego-list",
        "catalogo/videojuegos/",
        {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO},
    ),
    _entrada(
        "videojuego-detail",
        "catalogo/videojuegos/{pk}/",
        {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO},
    ),
    _entrada(
        "videojuego-ofertas",
        "catalogo/videojuegos/{pk}/ofertas/",
        {
            "GET": PUBLICO,
            "*": ROLES_GESTION_CATALOGO,
            "ofertas": PUBLICO,
        },
        nota="acción `ofertas` (GET público)",
        accion="ofertas",
    ),
    _entrada(
        "oferta-list",
        "catalogo/ofertas/",
        {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO},
    ),
    _entrada(
        "oferta-detail",
        "catalogo/ofertas/{pk}/",
        {"GET": PUBLICO, "*": ROLES_GESTION_CATALOGO},
    ),
    _simple(
        "oferta-movimientos",
        "catalogo/ofertas/{pk}/movimientos/",
        ROLES_GESTION_INVENTARIO,
        nota="acción `movimientos`",
    ),
    _simple(
        "movimiento-inventario-list",
        "inventario/movimientos/",
        ROLES_GESTION_INVENTARIO,
    ),
    _simple(
        "movimiento-inventario-detail",
        "inventario/movimientos/{pk}/",
        ROLES_GESTION_INVENTARIO,
    ),
    _simple("pedido-list", "pedidos/", AUTENTICADO, nota="propietario"),
    _simple("pedido-detail", "pedidos/{pk}/", AUTENTICADO, nota="propietario"),
    _simple(
        "pedido-cancelar",
        "pedidos/{pk}/cancelar/",
        AUTENTICADO,
        nota="propietario",
    ),
    _simple("pago-list", "pagos/", AUTENTICADO, nota="propietario"),
    _simple("pago-detail", "pagos/{pk}/", AUTENTICADO, nota="propietario"),
    _simple("venta-list", "ventas/", ROL_ADMIN),
    _simple("venta-detail", "ventas/{pk}/", ROL_ADMIN),
    _entrada(
        "contacto-list",
        "soporte/contactos/",
        {
            "GET": ROLES_LECTURA_CONTACTO,
            "POST": PUBLICO,
            "*": ROLES_GESTION_CONTACTO,
        },
        nota="propietario",
    ),
    _entrada(
        "contacto-detail",
        "soporte/contactos/{pk}/",
        {
            "GET": ROLES_LECTURA_CONTACTO,
            "POST": PUBLICO,
            "*": ROLES_GESTION_CONTACTO,
        },
        nota="propietario",
    ),
    _simple("usuario-list", "usuarios/", ROL_ADMIN),
    _simple("usuario-detail", "usuarios/{pk}/", ROL_ADMIN),
    _simple("rol-list", "roles/", ROL_ADMIN),
    _simple("rol-detail", "roles/{pk}/", ROL_ADMIN),
]

MATRIZ_POR_NOMBRE = {entrada["nombre"]: entrada for entrada in MATRIZ}


def _celda(regla):
    if regla == PUBLICO:
        return "público"
    if regla == AUTENTICADO:
        return "autenticado"
    if isinstance(regla, (list, tuple, set)):
        return ", ".join(regla)
    return str(regla)


def generar_tabla_markdown():
    """Genera la tabla RBAC publicada en ``docs/api/API.md``."""
    lineas = [
        "| Ruta | GET | POST | PUT/PATCH | DELETE | Nota |",
        "|---|---|---|---|---|---|",
    ]
    for entrada in MATRIZ:
        reglas = entrada["reglas"]
        celdas = [
            _regla_de_metodo(reglas, "GET"),
            _regla_de_metodo(reglas, "POST"),
            _regla_de_metodo(reglas, "PATCH") or _regla_de_metodo(reglas, "PUT"),
            _regla_de_metodo(reglas, "DELETE"),
        ]
        fila = [f"`{entrada['ruta']}`"] + [_celda(regla) for regla in celdas]
        fila.append(entrada["nota"])
        lineas.append("| " + " | ".join(fila) + " |")
    return "\n".join(lineas)
