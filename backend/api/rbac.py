"""Matriz declarativa de RBAC de la API (AZ-S2-BE-07).

Este módulo es la única fuente de verdad de:

- los roles de negocio (por ``Rol.codigo``);
- las reglas por vista/acción y método HTTP;
- la matriz publicada en ``docs/api/API.md`` (generada por
  :func:`generar_tabla_markdown`).

Los permisos se aplican en ``api/permissions.py`` leyendo estos datos. Para
cambiar una política, edita este archivo: la documentación y las pruebas de
concordancia se ajustan solas.
"""

PUBLICO = "PUBLICO"
AUTENTICADO = "AUTENTICADO"

ROL_ADMINISTRADOR = "administrador"
ROL_GESTOR_INVENTARIO = "gestor_inventario"
ROL_SOPORTE = "soporte"
ROL_CLIENTE = "cliente"

ROLES_NEGOCIO = (
    ROL_ADMINISTRADOR,
    ROL_GESTOR_INVENTARIO,
    ROL_SOPORTE,
    ROL_CLIENTE,
)

# Roles nuevos sembrados por la migración de datos, seed_catalogo y conftest.
ROLES_NUEVOS = (
    {
        "codigo": ROL_GESTOR_INVENTARIO,
        "nombre": "Gestor de inventario",
        "descripcion": "Gestiona el catálogo y el libro mayor de inventario.",
    },
    {
        "codigo": ROL_SOPORTE,
        "nombre": "Soporte",
        "descripcion": "Atiende y gestiona los mensajes de contacto.",
    },
)

_ADMIN = (ROL_ADMINISTRADOR,)
_CATALOGO = (ROL_ADMINISTRADOR, ROL_GESTOR_INVENTARIO)
_SOPORTE_GESTION = (ROL_ADMINISTRADOR, ROL_SOPORTE)
_SOPORTE_LECTURA = (ROL_ADMINISTRADOR, ROL_SOPORTE, ROL_CLIENTE)

# Reglas reutilizables. ``*`` aplica a cualquier método/acción.
REGLAS = {
    "publico": {"*": PUBLICO},
    "autenticado": {"*": AUTENTICADO},
    "admin": {"*": _ADMIN},
    "catalogo": {
        "GET": PUBLICO,
        "HEAD": PUBLICO,
        "OPTIONS": PUBLICO,
        "POST": _CATALOGO,
        "PUT": _CATALOGO,
        "PATCH": _CATALOGO,
        "DELETE": _CATALOGO,
        # Las acciones solo existen para GET; para otros métodos rige la regla
        # normal por verbo (y DRF responderá 405 tras el chequeo de permisos).
        "ofertas": {"GET": PUBLICO},
        "movimientos": {"GET": _CATALOGO},
    },
    "inventario": {"*": _CATALOGO},
    "contactos": {
        "GET": _SOPORTE_LECTURA,
        "HEAD": _SOPORTE_LECTURA,
        "OPTIONS": _SOPORTE_LECTURA,
        "POST": PUBLICO,
        "PUT": _SOPORTE_GESTION,
        "PATCH": _SOPORTE_GESTION,
        "DELETE": _SOPORTE_GESTION,
    },
    "reportes": {"*": _ADMIN},
    "reporte_inventario": {"*": _CATALOGO},
}


def _endpoint(nombre, ruta, regla, nota="", accion=""):
    return {
        "nombre": nombre,
        "ruta": ruta,
        "reglas": REGLAS[regla],
        "nota": nota,
        "accion": accion,
    }


# Una entrada por cada URL de ``api/urls.py`` (incluidas las de los routers).
MATRIZ = (
    _endpoint("api-root", "/api/v1/", "publico"),
    _endpoint("api-health", "/api/v1/health/", "publico"),
    _endpoint("api-not-found", "/api/v1/{ruta}", "publico", "JSON 404"),
    _endpoint("auth-registro", "/api/v1/auth/registro/", "publico"),
    _endpoint("auth-login", "/api/v1/auth/login/", "publico"),
    _endpoint("auth-logout", "/api/v1/auth/logout/", "autenticado"),
    _endpoint("auth-me", "/api/v1/auth/me/", "autenticado"),
    _endpoint("auth-cambiar-password", "/api/v1/auth/me/password/", "autenticado"),
    _endpoint("auth-csrf", "/api/v1/auth/csrf/", "publico"),
    _endpoint("carrito", "/api/v1/carrito/", "autenticado", "propietario"),
    _endpoint("carrito-items", "/api/v1/carrito/items/", "autenticado", "propietario"),
    _endpoint(
        "carrito-item-detalle",
        "/api/v1/carrito/items/{pk}/",
        "autenticado",
        "propietario",
    ),
    _endpoint("inventario-ajuste", "/api/v1/inventario/ajustes/", "inventario"),
    _endpoint("reporte-dashboard", "/api/v1/reportes/dashboard/", "reportes"),
    _endpoint("reporte-ventas", "/api/v1/reportes/ventas/", "reportes"),
    _endpoint(
        "reporte-inventario", "/api/v1/reportes/inventario/", "reporte_inventario"
    ),
    _endpoint("reporte-videojuegos", "/api/v1/reportes/videojuegos/", "reportes"),
    _endpoint(
        "soporte-mayor-informacion",
        "/api/v1/soporte/mayor-informacion/",
        "publico",
    ),
    _endpoint("categoria-list", "/api/v1/catalogo/categorias/", "catalogo"),
    _endpoint("categoria-detail", "/api/v1/catalogo/categorias/{pk}/", "catalogo"),
    _endpoint("plataforma-list", "/api/v1/catalogo/plataformas/", "catalogo"),
    _endpoint("plataforma-detail", "/api/v1/catalogo/plataformas/{pk}/", "catalogo"),
    _endpoint("genero-list", "/api/v1/catalogo/generos/", "catalogo"),
    _endpoint("genero-detail", "/api/v1/catalogo/generos/{pk}/", "catalogo"),
    _endpoint("videojuego-list", "/api/v1/catalogo/videojuegos/", "catalogo"),
    _endpoint("videojuego-detail", "/api/v1/catalogo/videojuegos/{pk}/", "catalogo"),
    _endpoint(
        "videojuego-ofertas",
        "/api/v1/catalogo/videojuegos/{pk}/ofertas/",
        "catalogo",
        "acción `ofertas` (GET público)",
        accion="ofertas",
    ),
    _endpoint("oferta-list", "/api/v1/catalogo/ofertas/", "catalogo"),
    _endpoint("oferta-detail", "/api/v1/catalogo/ofertas/{pk}/", "catalogo"),
    _endpoint(
        "oferta-movimientos",
        "/api/v1/catalogo/ofertas/{pk}/movimientos/",
        "catalogo",
        "acción `movimientos`",
        accion="movimientos",
    ),
    _endpoint(
        "movimiento-inventario-list", "/api/v1/inventario/movimientos/", "inventario"
    ),
    _endpoint(
        "movimiento-inventario-detail",
        "/api/v1/inventario/movimientos/{pk}/",
        "inventario",
    ),
    _endpoint("pedido-list", "/api/v1/pedidos/", "autenticado", "propietario"),
    _endpoint("pedido-detail", "/api/v1/pedidos/{pk}/", "autenticado", "propietario"),
    _endpoint(
        "pedido-cancelar",
        "/api/v1/pedidos/{pk}/cancelar/",
        "autenticado",
        "propietario",
    ),
    _endpoint("pago-list", "/api/v1/pagos/", "autenticado", "propietario"),
    _endpoint("pago-detail", "/api/v1/pagos/{pk}/", "autenticado", "propietario"),
    _endpoint("venta-list", "/api/v1/ventas/", "admin"),
    _endpoint("venta-detail", "/api/v1/ventas/{pk}/", "admin"),
    _endpoint("contacto-list", "/api/v1/soporte/contactos/", "contactos", "propietario"),
    _endpoint(
        "contacto-detail", "/api/v1/soporte/contactos/{pk}/", "contactos", "propietario"
    ),
    _endpoint("usuario-list", "/api/v1/usuarios/", "admin"),
    _endpoint("usuario-detail", "/api/v1/usuarios/{pk}/", "admin"),
    _endpoint("rol-list", "/api/v1/roles/", "admin"),
    _endpoint("rol-detail", "/api/v1/roles/{pk}/", "admin"),
)

MATRIZ_POR_NOMBRE = {entry["nombre"]: entry for entry in MATRIZ}

_COLUMNAS = (("GET", ("GET",)), ("POST", ("POST",)), ("PUT/PATCH", ("PUT", "PATCH")), ("DELETE", ("DELETE",)))


def etiqueta_regla(regla):
    """Texto legible de una regla para la documentación."""
    if regla == PUBLICO:
        return "público"
    if regla == AUTENTICADO:
        return "autenticado"
    return ", ".join(regla)


def regla_para_metodo(reglas, metodo):
    """Resuelve la regla efectiva para un método (``*`` como comodín)."""
    if metodo in reglas:
        return reglas[metodo]
    return reglas.get("*")


def regla_de_accion(reglas, accion, metodo):
    """Regla de una acción de ViewSet para un método, o ``None`` si no aplica.

    Las acciones GET-only declaran su regla como ``{"GET": ...}`` para no
    secuestrar el resto de verbos (que DRF rechazará con 405).
    """
    if not accion or accion not in reglas:
        return None
    regla = reglas[accion]
    if isinstance(regla, dict):
        return regla.get(metodo.upper())
    return regla


def generar_tabla_markdown():
    """Genera la tabla rol × endpoint publicada en ``docs/api/API.md``."""
    lineas = [
        "| Ruta | GET | POST | PUT/PATCH | DELETE | Nota |",
        "|---|---|---|---|---|---|",
    ]
    for entry in MATRIZ:
        celdas = []
        for _, metodos in _COLUMNAS:
            reglas = [
                entry["reglas"][metodo]
                for metodo in metodos
                if metodo in entry["reglas"]
            ]
            globales = [
                entry["reglas"]["*"]
                for metodo in metodos
                if "*" in entry["reglas"]
            ]
            usadas = reglas or globales
            celdas.append(", ".join(dict.fromkeys(etiqueta_regla(r) for r in usadas)) or "—")
        nota = entry["nota"] or ""
        regla_accion = regla_de_accion(entry["reglas"], entry.get("accion"), "GET")
        if regla_accion is not None:
            celdas[0] = etiqueta_regla(regla_accion)
        lineas.append(
            f"| `{entry['ruta']}` | " + " | ".join(celdas) + f" | {nota} |"
        )
    return "\n".join(lineas)
