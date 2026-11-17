"""Pruebas de los recursos del catálogo en la API REST."""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from catalogo.models import Categoria, Genero, OfertaVideojuego, Plataforma, Videojuego


pytestmark = pytest.mark.django_db


def _client():
    return APIClient()


def test_raiz_de_la_api_lista_recursos():
    response = _client().get("/api/v1/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["version"] == "v1"
    assert "catalogo" in payload["data"]["recursos"]


def test_healthcheck_publico():
    response = _client().get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok", "version": "v1"}


def test_catalogo_es_publico_y_paginado(categoria, genero, videojuego, oferta):
    response = _client().get("/api/v1/catalogo/videojuegos/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["pagination"]["count"] == 1
    assert payload["data"][0]["titulo"] == "Juego Alpha"
    assert payload["data"][0]["ofertas"][0]["sku"] == oferta.sku


def test_filtros_y_busqueda_del_catalogo(categoria, genero, videojuego, oferta):
    otra_categoria = Categoria.objects.create(nombre="Deportes")
    otro_genero = Genero.objects.create(nombre="Shooter")
    otro = Videojuego.objects.create(
        titulo="Juego Beta",
        categoria=otra_categoria,
        genero=otro_genero,
    )
    OfertaVideojuego.objects.create(
        videojuego=otro,
        plataforma=oferta.plataforma,
        precio_vigente=Decimal("50000"),
        sku="AZ-0002-001",
        stock=1,
    )
    client = _client()

    por_categoria = client.get(f"/api/v1/catalogo/videojuegos/?categoria={categoria.pk}")
    por_busqueda = client.get("/api/v1/catalogo/videojuegos/?q=Beta")
    por_disponibilidad = client.get("/api/v1/catalogo/videojuegos/?disponible=true")

    assert [v["titulo"] for v in por_categoria.json()["data"]] == ["Juego Alpha"]
    assert [v["titulo"] for v in por_busqueda.json()["data"]] == ["Juego Beta"]
    assert {v["titulo"] for v in por_disponibilidad.json()["data"]} == {
        "Juego Alpha",
        "Juego Beta",
    }


def test_detalle_de_videojuego_y_ofertas_anidadas(videojuego, oferta):
    client = _client()

    detalle = client.get(f"/api/v1/catalogo/videojuegos/{videojuego.pk}/")
    ofertas = client.get(f"/api/v1/catalogo/videojuegos/{videojuego.pk}/ofertas/")

    assert detalle.status_code == 200
    assert detalle.json()["data"]["titulo"] == "Juego Alpha"
    assert ofertas.status_code == 200
    assert ofertas.json()["pagination"]["count"] == 1
    assert ofertas.json()["data"][0]["id"] == oferta.pk


def test_ofertas_publicas_ocultan_borradores(videojuego, plataforma, categoria, genero):
    otro_videojuego = Videojuego.objects.create(
        titulo="Juego Oculto",
        categoria=categoria,
        genero=genero,
    )
    OfertaVideojuego.objects.create(
        videojuego=videojuego,
        plataforma=plataforma,
        precio_vigente=Decimal("1000"),
        sku="AZ-PUB-001",
        stock=2,
        estado_publicacion=OfertaVideojuego.EstadoPublicacion.PUBLICADO,
    )
    OfertaVideojuego.objects.create(
        videojuego=otro_videojuego,
        plataforma=plataforma,
        precio_vigente=Decimal("2000"),
        sku="AZ-BOR-001",
        stock=2,
        estado_publicacion=OfertaVideojuego.EstadoPublicacion.BORRADOR,
    )

    response = _client().get("/api/v1/catalogo/ofertas/")

    assert response.status_code == 200
    assert [o["sku"] for o in response.json()["data"]] == ["AZ-PUB-001"]


def test_cliente_no_puede_modificar_catalogo(usuario_cliente, categoria, genero):
    client = _client()
    client.force_authenticate(usuario_cliente)

    response = client.post(
        "/api/v1/catalogo/videojuegos/",
        {
            "titulo": "No permitido",
            "categoria": categoria.pk,
            "genero": genero.pk,
        },
        format="json",
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "permiso_denegado"


def test_administrador_puede_crud_de_videojuego(usuario_admin, categoria, genero):
    client = _client()
    client.force_authenticate(usuario_admin)

    creado = client.post(
        "/api/v1/catalogo/videojuegos/",
        {
            "titulo": "Juego Nuevo",
            "descripcion": "Un juego de prueba",
            "categoria": categoria.pk,
            "genero": genero.pk,
            "activo": True,
        },
        format="json",
    )
    assert creado.status_code == 201
    videojuego_id = creado.json()["data"]["id"]

    actualizado = client.patch(
        f"/api/v1/catalogo/videojuegos/{videojuego_id}/",
        {"titulo": "Juego Renombrado"},
        format="json",
    )
    assert actualizado.status_code == 200
    assert actualizado.json()["data"]["titulo"] == "Juego Renombrado"

    eliminado = client.delete(f"/api/v1/catalogo/videojuegos/{videojuego_id}/")
    assert eliminado.status_code == 204
    assert not Videojuego.objects.filter(pk=videojuego_id).exists()


def test_validacion_de_entrada_devuelve_400_con_detalles(usuario_admin):
    client = _client()
    client.force_authenticate(usuario_admin)

    response = client.post(
        "/api/v1/catalogo/videojuegos/",
        {"titulo": ""},
        format="json",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "datos_invalidos"
    assert "categoria" in payload["error"]["details"]
    assert "genero" in payload["error"]["details"]


def test_admin_puede_crear_oferta_y_se_valida_la_combinacion(
    usuario_admin, videojuego, plataforma
):
    client = _client()
    client.force_authenticate(usuario_admin)

    primera = client.post(
        "/api/v1/catalogo/ofertas/",
        {
            "videojuego": videojuego.pk,
            "plataforma": plataforma.pk,
            "precio_vigente": "45000.00",
            "sku": "az-nueva-001",
            "stock": 3,
        },
        format="json",
    )
    assert primera.status_code == 201
    assert primera.json()["data"]["sku"] == "AZ-NUEVA-001"

    duplicada = client.post(
        "/api/v1/catalogo/ofertas/",
        {
            "videojuego": videojuego.pk,
            "plataforma": plataforma.pk,
            "precio_vigente": "45000.00",
            "sku": "AZ-NUEVA-002",
            "stock": 1,
        },
        format="json",
    )
    assert duplicada.status_code == 400
    assert "plataforma" in duplicada.json()["error"]["details"]


def test_paginacion_respeta_page_size():
    for indice in range(3):
        Categoria.objects.create(nombre=f"Categoría {indice}")

    response = _client().get("/api/v1/catalogo/categorias/?page_size=2")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["data"]) == 2
    assert payload["pagination"]["count"] == 3
    assert payload["pagination"]["total_pages"] == 2
    assert payload["pagination"]["next"] is not None


def test_metodo_no_permitido_responde_json(usuario_admin):
    client = _client()
    client.force_authenticate(usuario_admin)
    response = client.put("/api/v1/catalogo/categorias/", {}, format="json")

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "metodo_no_permitido"


def test_ruta_desconocida_responde_json_404():
    response = _client().get("/api/v1/ruta-inexistente/")

    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "no_encontrado"
