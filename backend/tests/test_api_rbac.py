"""Pruebas de la matriz RBAC declarada en ``api/rbac.py`` (AZ-S2-BE-07)."""
import re

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.urls import URLPattern, URLResolver, reverse
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.views import APIView

from api import urls as api_urls
from api.permissions import (
    EsAdministrador,
    PermisoContacto,
    TieneRol,
    TieneRolCatalogo,
    TieneRolContacto,
    TieneRolInventario,
    TieneRolReporte,
    TieneRolReporteInventario,
)
from api.rbac import (
    AUTENTICADO,
    PUBLICO,
    MATRIZ,
    MATRIZ_POR_NOMBRE,
    generar_tabla_markdown,
    regla_de_accion,
)
from api.utils import es_administrador
from cuentas.models import Usuario

pytestmark = pytest.mark.django_db

METODOS = ("get", "post", "put", "patch", "delete")
TIPOS_USUARIO = (
    "anónimo",
    "cliente",
    "soporte",
    "gestor_inventario",
    "administrador",
    "staff_sin_rol",
)


def _patrones(patterns):
    for patron in patterns:
        if isinstance(patron, URLResolver):
            yield from _patrones(patron.url_patterns)
        else:
            yield patron


def _nombres_url():
    return {patron.name for patron in _patrones(api_urls.urlpatterns) if patron.name}


def _url_de(nombre):
    patron = next(p for p in _patrones(api_urls.urlpatterns) if p.name == nombre)
    patron_pattern = patron.pattern
    # Las rutas ``path()`` exponen ``converters``; las del SimpleRouter usan
    # RegexPattern (con ``converters`` vacío) y sus grupos están en
    # ``regex.groupindex``. Se combinan para cubrir ambos tipos.
    claves = set(getattr(patron_pattern, "converters", None) or {})
    regex = getattr(patron_pattern, "regex", None)
    if regex is not None:
        claves.update(regex.groupindex)
    kwargs = {
        clave: ("ruta-inexistente" if clave == "ruta" else 999999) for clave in claves
    }
    return reverse(nombre, kwargs=kwargs)


def _regla_efectiva(entrada, metodo):
    reglas = entrada["reglas"]
    # Igual que en ``TieneRol._regla_para``: la acción manda sobre el verbo
    # genérico solo en los métodos que la acción soporta (GET).
    regla_accion = regla_de_accion(reglas, entrada.get("accion"), metodo)
    if regla_accion is not None:
        return regla_accion
    if metodo.upper() in reglas:
        return reglas[metodo.upper()]
    return reglas.get("*")


def _permitido(regla, usuario):
    if regla == PUBLICO:
        return True
    if regla == AUTENTICADO:
        return usuario is not None
    if usuario is None:
        return False
    if es_administrador(usuario):
        return True
    return usuario.roles.filter(codigo__in=tuple(regla)).exists()


@pytest.fixture
def usuario_rbac(
    request,
    db,
    usuario_cliente,
    usuario_soporte,
    usuario_gestor_inventario,
    usuario_staff_sin_rol,
    rol_admin,
):
    tipo = request.param
    if tipo == "anónimo":
        return None
    if tipo == "cliente":
        return usuario_cliente
    if tipo == "soporte":
        return usuario_soporte
    if tipo == "gestor_inventario":
        return usuario_gestor_inventario
    if tipo == "staff_sin_rol":
        return usuario_staff_sin_rol
    administrador = Usuario.objects.create_user(
        username="rbac_administrador", password="pass1234!"
    )
    administrador.roles.add(rol_admin)
    return administrador


@pytest.mark.parametrize("nombre", sorted(MATRIZ_POR_NOMBRE))
@pytest.mark.parametrize("usuario_rbac", TIPOS_USUARIO, indirect=True)
@pytest.mark.parametrize("metodo", METODOS)
def test_respuesta_coincide_con_la_matriz(nombre, usuario_rbac, metodo):
    url = _url_de(nombre)
    cliente = APIClient()
    if usuario_rbac is not None:
        cliente.force_authenticate(usuario_rbac)

    if metodo == "get":
        respuesta = cliente.get(url)
    else:
        respuesta = cliente.generic(metodo.upper(), url, {}, format="json")

    regla = _regla_efectiva(MATRIZ_POR_NOMBRE[nombre], metodo)
    assert regla is not None, f"La ruta {nombre} no declara política para {metodo}"

    if _permitido(regla, usuario_rbac):
        assert respuesta.status_code not in (401, 403), (
            f"{metodo.upper()} {url} con {usuario_rbac}->{respuesta.status_code}"
        )
    else:
        esperado = 401 if usuario_rbac is None else 403
        codigo = "no_autenticado" if esperado == 401 else "permiso_denegado"
        assert respuesta.status_code == esperado, (
            f"{metodo.upper()} {url} con {usuario_rbac}->{respuesta.status_code}"
        )
        assert respuesta.json()["success"] is False
        assert respuesta.json()["error"]["code"] == codigo
        assert respuesta.json()["error"]["message"]


def test_todas_las_rutas_tienen_politica_explicita():
    nombres = _nombres_url()
    declarados = set(MATRIZ_POR_NOMBRE)

    assert nombres - declarados == set(), (
        "Rutas sin política explícita en api/rbac.py: " + ", ".join(sorted(nombres - declarados))
    )
    assert declarados - nombres == set(), (
        "Políticas sin ruta real en api/urls.py: " + ", ".join(sorted(declarados - nombres))
    )
    assert len(MATRIZ) == len(declarados), "Hay entradas duplicadas en la matriz RBAC"

    conocidos = {
        AllowAny,
        IsAuthenticated,
        EsAdministrador,
        PermisoContacto,
        TieneRol,
        TieneRolCatalogo,
        TieneRolInventario,
        TieneRolContacto,
        TieneRolReporte,
        TieneRolReporteInventario,
    }
    por_nombre = {p.name: p for p in _patrones(api_urls.urlpatterns) if p.name}
    for nombre in sorted(nombres):
        vista = getattr(por_nombre[nombre], "callback", None)
        cls = getattr(vista, "cls", None)
        if cls is None:
            continue
        permisos = tuple(getattr(cls, "permission_classes", ()))
        assert permisos, f"{nombre} no declara permission_classes"
        # Basta con que la declare la vista o una base de la propia API; lo
        # importante es que no se herede implícitamente de ``APIView`` (que es
        # donde DRF pone ``DEFAULT_PERMISSION_CLASSES``). Así un
        # ``[IsAuthenticated]`` escrito explícitamente es válido.
        declarado_en = [
            base.__name__
            for base in cls.__mro__
            if base is not APIView
            and base is not object
            and "permission_classes" in base.__dict__
        ]
        assert declarado_en, (
            f"{nombre} usa el permiso por defecto sin declararlo explícitamente"
        )
        desconocidos = set(permisos) - conocidos
        assert not desconocidos, (
            f"{nombre} usa permisos no reconocidos: "
            + ", ".join(p.__name__ for p in desconocidos)
        )


def test_tabla_publicada_en_api_md_coincide_con_rbac():
    ruta = settings.BASE_DIR.parent / "docs" / "api" / "API.md"
    contenido = ruta.read_text(encoding="utf-8")
    bloque = re.search(
        r"<!-- INICIO MATRIZ RBAC -->\n(.*?)\n<!-- FIN MATRIZ RBAC -->",
        contenido,
        re.DOTALL,
    )
    assert bloque, "No existe el bloque generado de la matriz RBAC en docs/api/API.md"
    assert bloque.group(1).strip() == generar_tabla_markdown().strip()


# ── Unitarias de TieneRol ────────────────────────────────────────────────────


class _Vista:
    pass


def _peticion(usuario, metodo="get"):
    peticion = getattr(APIRequestFactory(), metodo)("/api/v1/")
    peticion.user = usuario or AnonymousUser()
    return peticion


def test_tiene_rol_acepta_cualquiera_de_varios_roles(usuario_cliente, rol_soporte):
    usuario_cliente.roles.add(rol_soporte)

    class Permiso(TieneRol):
        roles_permitidos = ("soporte", "gestor_inventario")

    assert Permiso().has_permission(_peticion(usuario_cliente), _Vista()) is True


def test_tiene_rol_rechaza_usuario_autenticado_sin_el_rol(usuario_cliente):
    class Permiso(TieneRol):
        roles_permitidos = ("soporte",)

    with pytest.raises(PermissionDenied):
        Permiso().has_permission(_peticion(usuario_cliente), _Vista())


def test_tiene_rol_rechaza_roles_inexistentes(usuario_cliente):
    class Permiso(TieneRol):
        roles_permitidos = ("rol_que_no_existe",)

    with pytest.raises(PermissionDenied):
        Permiso().has_permission(_peticion(usuario_cliente), _Vista())


def test_tiene_rol_anonimo_responde_no_autenticado():
    class Permiso(TieneRol):
        roles_permitidos = ("cliente",)

    with pytest.raises(NotAuthenticated):
        Permiso().has_permission(_peticion(None), _Vista())


@pytest.mark.parametrize("tipo", ["rol", "staff", "superuser"])
def test_administrador_staff_y_superuser_son_superconjunto(
    db, rol_admin, usuario_cliente, tipo
):
    if tipo == "rol":
        usuario = usuario_cliente
        usuario.roles.add(rol_admin)
    elif tipo == "staff":
        usuario = usuario_cliente
        usuario.is_staff = True
    else:
        usuario = Usuario.objects.create_superuser(
            username="rbac_super", password="pass1234!"
        )

    class Permiso(TieneRol):
        roles_permitidos = ("soporte",)

    assert es_administrador(usuario) is True
    assert Permiso().has_permission(_peticion(usuario), _Vista()) is True


def test_tiene_rol_acepta_mapa_por_metodo_y_accion(
    usuario_cliente, usuario_soporte, rol_cliente
):
    class Permiso(TieneRol):
        roles_permitidos = {
            "GET": ("cliente",),
            "POST": ("soporte",),
            "ofertas": PUBLICO,
        }

    vista = _Vista()
    assert Permiso().has_permission(_peticion(usuario_cliente), vista) is True
    with pytest.raises(PermissionDenied):
        Permiso().has_permission(_peticion(usuario_cliente, "post"), vista)
    assert Permiso().has_permission(_peticion(usuario_soporte, "post"), vista) is True

    vista_con_accion = _Vista()
    vista_con_accion.action = "ofertas"
    assert Permiso().has_permission(_peticion(None, "get"), vista_con_accion) is True
