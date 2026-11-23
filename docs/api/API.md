# API REST de Arcakane Zone

API JSON versionada que expone los recursos del sistema sin reemplazar la
interfaz HTML existente. El sitio con Django Templates + HTMX sigue disponible
en sus rutas de siempre.

- **Base:** `/api/v1/`
- **Raíz navegable:** `GET /api/v1/` (devuelve las URLs de todos los recursos)
- **Salud:** `GET /api/v1/health/`
- **Formato:** JSON con UTF-8 y barra final obligatoria en las rutas.
- **Postman:** [`Arcakane_Zone.postman_collection.json`](./Arcakane_Zone.postman_collection.json)
  incluye todos los endpoints con credenciales demo y variables automáticas.

`/api/` redirige a `/api/v1/` y `/api/catalogo/` redirige a
`/api/v1/catalogo/videojuegos/` por compatibilidad.

## Autenticación y autorización

La API acepta dos mecanismos:

1. **Token propio con vencimiento**

   ```http
   Authorization: Token <clave>
   ```

   La clave se obtiene en `POST /api/v1/auth/login/` o
   `POST /api/v1/auth/registro/` y se devuelve junto a `expires_at`.
   Vigencia por defecto: 7 días, configurable con `API_TOKEN_TTL_DAYS`.
   Un token inexistente o vencido responde `401 no_autenticado`.
   **Los tokens antiguos de `rest_framework.authtoken` ya no son válidos:** hay
   que iniciar sesión de nuevo para obtener una clave del modelo propio.

2. **Sesión/cookie de Django**

   Es la misma sesión del sitio HTML y del admin. Para peticiones que modifican
   datos hay que enviar la cookie `csrftoken` en la cabecera `X-CSRFToken`.
   `GET /api/v1/auth/csrf/` garantiza la creación de la cookie.

| Recurso | Acceso |
|---|---|
| Catálogo (categorías, plataformas, géneros, videojuegos, ofertas) | Lectura pública; escritura solo administrador |
| Carrito, pedidos, pagos | Usuario autenticado; dueño del recurso o administrador |
| Ventas, reportes, usuarios y roles | Solo administrador |
| Contacto | Creación pública; lectura de los propios mensajes o todos para administrador |
| Solicitud de información | Pública |

Se considera administrador al usuario con `is_staff=True` o con el rol de
negocio `administrador`.

## Sobre de respuesta

### Éxito

```json
{
  "success": true,
  "data": {},
  "message": "Texto opcional",
  "pagination": {
    "count": 15,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "next": null,
    "previous": null
  }
}
```

`message` y `pagination` solo aparecen cuando aplican.

### Error

```json
{
  "success": false,
  "error": {
    "code": "datos_invalidos",
    "message": "Datos de entrada inválidos.",
    "details": {
      "email": ["Este campo es obligatorio."]
    }
  }
}
```

`details` es opcional y contiene los errores por campo o información adicional.

| HTTP | `code` habitual | Cuándo ocurre |
|---|---|---|
| `400` | `datos_invalidos` | Validación de entrada |
| `401` | `no_autenticado` / `credenciales_invalidas` | Falta autenticación o login incorrecto |
| `402` | `pago_rechazado` | La pasarela simulada rechazó el pago |
| `403` | `permiso_denegado` | El usuario no tiene el rol requerido |
| `404` | `no_encontrado` | El recurso no existe o no pertenece al usuario |
| `405` | `metodo_no_permitido` | Método HTTP no soportado |
| `409` | `conflicto` | Regla de negocio o restricción de integridad |
| `500` | `error_interno` | Error no controlado (siempre en JSON) |

## Listados: paginación, búsqueda y orden

- Paginación por páginas: `?page=2&page_size=50` (máximo `100`, por defecto `20`).
- Búsqueda de texto: `?q=zelda` (catálogo y usuarios).
- Orden: `?ordering=titulo` o `?ordering=-precio_vigente` según los campos
  permitidos de cada recurso.

## Endpoints

### Autenticación y perfil

| Método | Ruta | Cuerpo / notas |
|---|---|---|
| `POST` | `/api/v1/auth/registro/` | `username`, `email`, `password`, `password_confirm` y datos opcionales |
| `POST` | `/api/v1/auth/login/` | `username`, `password` |
| `POST` | `/api/v1/auth/logout/` | Revoca solo el token de esta sesión y cierra la sesión |
| `POST` | `/api/v1/auth/token/refresh/` | Rota el token vigente; devuelve `token` y `expires_at` |
| `POST` | `/api/v1/auth/logout-all/` | Revoca todos los tokens del usuario y cierra la sesión |
| `GET` | `/api/v1/auth/csrf/` | Devuelve `csrfToken` y crea la cookie |
| `GET` | `/api/v1/auth/me/` | Perfil del usuario autenticado |
| `PATCH`/`PUT` | `/api/v1/auth/me/` | Actualiza el perfil |
| `POST` | `/api/v1/auth/me/password/` | `old_password`, `new_password`, `new_password_confirm` |

Respuesta de login y registro:

```json
{
  "success": true,
  "data": {
    "usuario": { "id": 1, "username": "cliente", "...": "..." },
    "token": "KiJ8mRb4K9tnGY1_3YKw8HFZqA9Ydx3v4OgbXwrH8sc",
    "expires_at": "2026-11-29T18:30:00Z"
  },
  "message": "Sesión iniciada correctamente."
}
```

### Vencimiento, renovación y cierre global

- Cada login o registro emite una clave nueva; varias sesiones pueden coexistir.
- `expires_at` indica el vencimiento en ISO 8601. La vigencia la define
  `API_TOKEN_TTL_DAYS` (días, defecto `7`, mínimo `1`).
- `POST /api/v1/auth/token/refresh/` exige un token vigente en la cabecera,
  revoca esa clave y devuelve una nueva con su `expires_at`. La clave anterior
  pasa a dar `401 no_autenticado`.
- `POST /api/v1/auth/logout-all/` revoca todos los tokens del usuario;
  `POST /api/v1/auth/logout/` solo revoca el usado en esa petición.
- Cambiar la contraseña por cualquier vía (API, formulario web, reseteo o
  admin) revoca todos los tokens del usuario. Si Django vuelve a hashear la
  contraseña al iniciar sesión por un cambio de algoritmo, también se revocan
  los tokens anteriores; la clave emitida en ese mismo login sigue válida porque
  se genera después de autenticar.

### Catálogo

| Método | Ruta | Notas |
|---|---|---|
| `GET` | `/api/v1/catalogo/categorias/` | `q`, `ordering`, `activo` (admin) |
| `GET` | `/api/v1/catalogo/plataformas/` | Igual que categorías |
| `GET` | `/api/v1/catalogo/generos/` | Igual que categorías |
| `GET` | `/api/v1/catalogo/videojuegos/` | `q`, `categoria`, `genero`, `plataforma`, `disponible`, `activo`, `ordering` |
| `GET` | `/api/v1/catalogo/videojuegos/{id}/` | Detalle con ofertas |
| `GET` | `/api/v1/catalogo/videojuegos/{id}/ofertas/` | Ofertas publicadas del título |
| `GET` | `/api/v1/catalogo/ofertas/` | `q`, `videojuego`, `plataforma`, `categoria`, `genero`, `disponible`, `estado_publicacion` (admin), `ordering` |
| `POST`/`PUT`/`PATCH`/`DELETE` | `/api/v1/catalogo/...` | Solo administrador |

### Carrito

| Método | Ruta | Cuerpo |
|---|---|---|
| `GET` | `/api/v1/carrito/` | Carrito pendiente del usuario (vacío si no existe) |
| `DELETE` | `/api/v1/carrito/` | Vacía el carrito |
| `POST` | `/api/v1/carrito/items/` | `{ "oferta": 1, "cantidad": 2 }` |
| `GET` | `/api/v1/carrito/items/{id}/` | Detalle de una línea |
| `PATCH` | `/api/v1/carrito/items/{id}/` | `{ "cantidad": 3 }`; `0` elimina la línea |
| `DELETE` | `/api/v1/carrito/items/{id}/` | Elimina la línea |

### Pedidos

| Método | Ruta | Notas |
|---|---|---|
| `GET` | `/api/v1/pedidos/` | Pedidos del usuario; admin ve todos |
| `GET` | `/api/v1/pedidos/{id}/` | Detalle con líneas, pago y venta |
| `PATCH` | `/api/v1/pedidos/{id}/` | `{ "estado": "cancelado" }` |
| `POST` | `/api/v1/pedidos/{id}/cancelar/` | Alias explícito de cancelación |

Solo se permite cancelar pedidos en estado `pendiente`; cualquier otra
transición devuelve `409 Conflict`.

### Pagos y ventas

| Método | Ruta | Notas |
|---|---|---|
| `GET` | `/api/v1/pagos/` | Pagos propios; admin ve todos |
| `GET` | `/api/v1/pagos/{id}/` | Detalle |
| `POST` | `/api/v1/pagos/` | `{ "pedido": 1 }`; procesa el pago simulado |
| `GET` | `/api/v1/ventas/` | Solo administrador; filtros `desde`, `hasta`, `cliente` |

Un pago rechazado devuelve `402 Payment Required` con el registro del intento en
`error.details`. El pedido permanece pendiente y el pago puede reintentarse.

### Reportes (solo administrador)

| Método | Ruta | Filtros |
|---|---|---|
| `GET` | `/api/v1/reportes/dashboard/` | — |
| `GET` | `/api/v1/reportes/ventas/` | `desde`, `hasta`, `cliente`, paginación |
| `GET` | `/api/v1/reportes/inventario/` | `filtro=todos\|agotados\|bajo_stock\|disponibles\|inactivas` |
| `GET` | `/api/v1/reportes/videojuegos/` | `categoria`, `genero`, `plataforma`, `estado`, `disponibilidad` |

Los reportes paginados devuelven `data.resultados` junto con `resumen`.

### Soporte

| Método | Ruta | Notas |
|---|---|---|
| `GET` | `/api/v1/soporte/contactos/` | Propios; admin ve todos |
| `POST` | `/api/v1/soporte/contactos/` | Público. Usuarios autenticados pueden omitir `nombre` y `email` |
| `GET`/`PATCH`/`DELETE` | `/api/v1/soporte/contactos/{id}/` | Dueño (lectura) o administrador |
| `POST` | `/api/v1/soporte/mayor-informacion/` | `nombre`, `email`, `telefono` opcional |

### Usuarios y roles (solo administrador)

| Método | Ruta | Filtros |
|---|---|---|
| `GET` | `/api/v1/usuarios/` | `q`, `rol`, `activo`, `ordering` |
| `GET` | `/api/v1/usuarios/{id}/` | Detalle |
| `GET` | `/api/v1/roles/` | Listado completo |

Usuarios y roles son de solo lectura a través de la API; su gestión sigue en el
admin de Django.

## Ejemplos

### Login con token y consulta del catálogo

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"cliente","password":"secreto"}'

curl -s http://localhost:8000/api/v1/catalogo/videojuegos/?q=zelda
```

### Pago con token

```bash
curl -s -X POST http://localhost:8000/api/v1/pagos/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pedido": 12}'
```

### Uso desde el frontend

El cliente TypeScript está en
[`frontend/src/api/client.ts`](../../frontend/src/api/client.ts).

```ts
import { auth, catalogo, setAuthToken } from "./api/client";

const { token } = await auth.login("cliente", "secreto");
setAuthToken(token);

const { data, pagination } = await catalogo.videojuegos({ q: "zelda", page: 1 });
console.log(data, pagination?.count);
```

## Pruebas

```bash
cd backend
SECRET_KEY=test-key DATABASE_URL=sqlite:///db.sqlite3 DEBUG=True \
  .venv/bin/python -m pytest -q
```

Las pruebas específicas de la API están en:

- `tests/test_api_catalogo.py`
- `tests/test_api_auth.py`
- `tests/test_api_carrito_pedidos_pagos.py`
- `tests/test_api_reportes_soporte.py`
- `tests/test_api_usuarios_ventas.py`

## Compatibilidad con el sitio HTML

Las rutas HTML (`/catalogo/`, `/pedidos/`, `/pagos/`, `/soporte/`, `/admin/`,
etc.) no cambian. La API reutiliza los mismos modelos, servicios y reglas de
negocio; no existe una segunda implementación de la lógica.
