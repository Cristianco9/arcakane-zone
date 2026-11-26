# API REST de Arcakane Zone

API JSON versionada que expone los recursos del sistema sin reemplazar la
interfaz HTML existente. El sitio con Django Templates + HTMX sigue disponible
en sus rutas de siempre.

- **Base:** `/api/v1/`
- **Raíz navegable:** `GET /api/v1/` (devuelve las URLs de todos los recursos)
- **Salud:** `GET /api/v1/health/` (*liveness*) y `GET /api/v1/health/ready/` (*readiness*)
- **Formato:** JSON con UTF-8 y barra final obligatoria en las rutas.
- **Postman:** [`Arcakane_Zone.postman_collection.json`](./Arcakane_Zone.postman_collection.json)
  incluye todos los endpoints con credenciales demo y variables automáticas.

`/api/` redirige a `/api/v1/` y `/api/catalogo/` redirige a
`/api/v1/catalogo/videojuegos/` por compatibilidad.

El contrato v1 es aditivo: tras la normalización del modelo se añadieron campos
y se conservaron todos los existentes. Los campos históricos marcados como
*deprecated* siguen devolviendo un único valor determinista; las listas nuevas
son la forma preferida. El sobre de respuesta y los códigos HTTP de esta guía
no cambian.

## Salud y trazabilidad

| Ruta | Uso | Respuesta correcta | Respuesta con fallo |
|---|---|---|---|
| `GET /api/v1/health/` | *Liveness*: el proceso responde | `200 {"status":"ok","version":"v1"}` | — |
| `GET /api/v1/health/ready/` | *Readiness*: la base de datos responde | `200 {"status":"ready","database":"ok","version":"v1"}` | `503 bd_no_disponible` |

`health/ready/` ejecuta `SELECT 1` contra la conexión real de Django. Es pública
y no usa autenticación ni *throttling*: si la base de datos cae, esos mecanismos
no deben convertir el healthcheck en un `500` y ocultar la causa. Docker Compose
y Render la usan como healthcheck; cuando la BD no responde, el servicio se
marca no saludable y no recibe tráfico.

Todas las respuestas bajo `/api/` incluyen la cabecera `X-Request-ID`. Si el
cliente envía un `X-Request-ID` válido, se reutiliza; si no, se genera un UUID.
Ese mismo valor se registra en los logs de la petición, junto con método, ruta,
código de estado, duración, IP y usuario autenticado. Los errores `500` se
registran con ese contexto para poder correlacionar el log con la petición. En
producción (`DEBUG=False`) los logs son JSON en `stdout`; en desarrollo son texto.
El nivel se controla con `LOG_LEVEL` (`INFO` por defecto).

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
| Catálogo (categorías, plataformas, géneros, videojuegos, ofertas) | Lectura pública; escritura administrador o `gestor_inventario` |
| Inventario (movimientos y ajustes) | administrador o `gestor_inventario` |
| Carrito, pedidos, pagos | Usuario autenticado; dueño del recurso o administrador |
| Ventas, usuarios y roles | Solo administrador |
| Reportes | Solo administrador, salvo `/reportes/inventario/`, que también admite `gestor_inventario` |
| Contacto | Creación pública; lectura de los propios mensajes, o de todos para `administrador` y `soporte`; gestión administrador o `soporte` |
| Solicitud de información | Pública |

Los roles de negocio se identifican por `Rol.codigo`: `administrador`,
`gestor_inventario`, `soporte` y `cliente`. Se asignan a cada usuario mediante
la tabla puente `UsuarioRol` (`usuario.roles.add(rol)`); un usuario puede tener
varios roles y basta cualquiera de los permitidos para pasar. Los roles
`gestor_inventario` y `soporte` los crean la migración de datos
`cuentas/0008_roles_rbac.py`, el comando `seed_catalogo` y las fixtures de
pruebas, todos de forma idempotente.

Se considera administrador al usuario con `is_staff=True`, `is_superuser=True`
o con el rol de negocio `administrador`: los tres son equivalentes a efectos de
esta API (el acceso al admin de Django no cambia). Una petición anónima a una
ruta protegida responde `401 no_autenticado`; una autenticada sin el rol
necesario responde `403 permiso_denegado`, con el sobre de error descrito más
abajo. Las reglas efectivas por ruta y método son:

<!-- INICIO MATRIZ RBAC -->
| Ruta | GET | POST | PUT/PATCH | DELETE | Nota |
|---|---|---|---|---|---|
| `/api/v1/` | público | público | público | público |  |
| `/api/v1/health/` | público | público | público | público |  |
| `/api/v1/health/ready/` | público | público | público | público |  |
| `/api/v1/{ruta}` | público | público | público | público | JSON 404 |
| `/api/v1/auth/registro/` | público | público | público | público |  |
| `/api/v1/auth/login/` | público | público | público | público |  |
| `/api/v1/auth/logout/` | autenticado | autenticado | autenticado | autenticado |  |
| `/api/v1/auth/token/refresh/` | autenticado | autenticado | autenticado | autenticado |  |
| `/api/v1/auth/logout-all/` | autenticado | autenticado | autenticado | autenticado |  |
| `/api/v1/auth/me/` | autenticado | autenticado | autenticado | autenticado |  |
| `/api/v1/auth/me/password/` | autenticado | autenticado | autenticado | autenticado |  |
| `/api/v1/auth/csrf/` | público | público | público | público |  |
| `/api/v1/carrito/` | autenticado | autenticado | autenticado | autenticado | propietario |
| `/api/v1/carrito/items/` | autenticado | autenticado | autenticado | autenticado | propietario |
| `/api/v1/carrito/items/{pk}/` | autenticado | autenticado | autenticado | autenticado | propietario |
| `/api/v1/inventario/ajustes/` | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/reportes/dashboard/` | administrador | administrador | administrador | administrador |  |
| `/api/v1/reportes/ventas/` | administrador | administrador | administrador | administrador |  |
| `/api/v1/reportes/inventario/` | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/reportes/videojuegos/` | administrador | administrador | administrador | administrador |  |
| `/api/v1/soporte/mayor-informacion/` | público | público | público | público |  |
| `/api/v1/catalogo/categorias/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/catalogo/categorias/{pk}/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/catalogo/plataformas/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/catalogo/plataformas/{pk}/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/catalogo/generos/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/catalogo/generos/{pk}/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/catalogo/videojuegos/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/catalogo/videojuegos/{pk}/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/catalogo/videojuegos/{pk}/ofertas/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario | acción `ofertas` (GET público) |
| `/api/v1/catalogo/ofertas/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/catalogo/ofertas/{pk}/` | público | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/catalogo/ofertas/{pk}/movimientos/` | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario | acción `movimientos` |
| `/api/v1/inventario/movimientos/` | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/inventario/movimientos/{pk}/` | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario | administrador, gestor_inventario |  |
| `/api/v1/pedidos/` | autenticado | autenticado | autenticado | autenticado | propietario |
| `/api/v1/pedidos/{pk}/` | autenticado | autenticado | autenticado | autenticado | propietario |
| `/api/v1/pedidos/{pk}/cancelar/` | autenticado | autenticado | autenticado | autenticado | propietario |
| `/api/v1/pagos/` | autenticado | autenticado | autenticado | autenticado | propietario |
| `/api/v1/pagos/{pk}/` | autenticado | autenticado | autenticado | autenticado | propietario |
| `/api/v1/ventas/` | administrador | administrador | administrador | administrador |  |
| `/api/v1/ventas/{pk}/` | administrador | administrador | administrador | administrador |  |
| `/api/v1/soporte/contactos/` | administrador, soporte, cliente | público | administrador, soporte | administrador, soporte | propietario |
| `/api/v1/soporte/contactos/{pk}/` | administrador, soporte, cliente | público | administrador, soporte | administrador, soporte | propietario |
| `/api/v1/usuarios/` | administrador | administrador | administrador | administrador |  |
| `/api/v1/usuarios/{pk}/` | administrador | administrador | administrador | administrador |  |
| `/api/v1/usuarios/{pk}/activar/` | administrador | administrador | administrador | administrador | acción `activar` |
| `/api/v1/usuarios/{pk}/desactivar/` | administrador | administrador | administrador | administrador | acción `desactivar` |
| `/api/v1/usuarios/{pk}/auditoria/` | administrador | administrador | administrador | administrador | acción `auditoria` |
| `/api/v1/roles/` | administrador | administrador | administrador | administrador |  |
| `/api/v1/roles/{pk}/` | administrador | administrador | administrador | administrador |  |
<!-- FIN MATRIZ RBAC -->

La tabla se genera desde `api/rbac.py` con `generar_tabla_markdown()`;
`tests/test_api_rbac.py` comprueba que coincide con esta sección y que todas las
rutas tienen política explícita. Las celdas `propietario` indican que, además
del rol, el usuario solo puede actuar sobre sus propios recursos (o cualquiera
si es administrador); las acciones `ofertas` y `movimientos` se detallan en su
nota.

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

## Límites de solicitudes y bloqueo de login

Las respuestas `429` usan el sobre estándar con
`error.code = demasiadas_solicitudes` e incluyen **siempre** la cabecera
`Retry-After` con los segundos que faltan para reintentar.

| Scope | Aplica a | Tasa por defecto | Clave |
|---|---|---|---|
| `anon` | Peticiones de visitantes | `100/min` | IP |
| `user` | Peticiones autenticadas | `1000/hour` | Usuario |
| `login` | `POST /auth/login/` | `10/min` | IP |
| `registro` | `POST /auth/registro/` | `5/hour` | IP |
| `contacto` | Creación de contactos y solicitudes de información | `5/hour` | IP |

Ejemplo de respuesta `429`:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 37
Content-Type: application/json
```

```json
{
  "success": false,
  "error": {
    "code": "demasiadas_solicitudes",
    "message": "Se superó el límite de solicitudes. Intenta más tarde."
  }
}
```

Además, `POST /auth/login/` bloquea temporalmente tras
`LOGIN_MAX_FAILED_ATTEMPTS` (5) credenciales incorrectas (`401`) en
`LOGIN_FAILURE_WINDOW_SECONDS` (900 s). El intento siguiente devuelve `429`
con `Retry-After` hasta que pasa `LOGIN_LOCKOUT_SECONDS` (900 s). Durante el
bloqueo **no se verifica la contraseña**. La clave es un hash de
`usuario en minúsculas + IP`: ni la contraseña ni los datos del usuario se
guardan en caché. Un login correcto reinicia el contador; los errores de
validación (`400`) no cuentan como intentos fallidos.

La IP se toma de `REMOTE_ADDR` por defecto. `X-Forwarded-For` solo se usa
cuando `THROTTLE_NUM_PROXIES > 0` (número de proxies propios delante de
Django); con `0`, una cabecera falsificada no puede cambiar la clave.

| HTTP | `code` habitual | Cuándo ocurre |
|---|---|---|
| `400` | `datos_invalidos` | Validación de entrada |
| `401` | `no_autenticado` / `credenciales_invalidas` | Falta autenticación o login incorrecto |
| `402` | `pago_rechazado` | La pasarela simulada rechazó el pago |
| `403` | `permiso_denegado` | El usuario no tiene el rol requerido |
| `404` | `no_encontrado` | El recurso no existe o no pertenece al usuario |
| `405` | `metodo_no_permitido` | Método HTTP no soportado |
| `409` | `conflicto` | Regla de negocio o restricción de integridad |
| `429` | `demasiadas_solicitudes` | Límite de solicitudes superado o login bloqueado |
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

Los filtros `categoria`, `genero` y `plataforma` conservan su nombre y
semántica. Los dos primeros consultan ahora relaciones muchos-a-muchos y se
aplica `distinct()` para no duplicar resultados ni romper la paginación.

Tras `python manage.py seed_catalogo` el catálogo contiene 140 videojuegos
reales, 20 por cada categoría base. `GET /api/v1/catalogo/videojuegos/`
devuelve ese total en `pagination.count`, y `?categoria=<id>` permite verificar
la distribución de una categoría concreta.

Ejemplo de videojuego con los campos aditivos:

```json
{
  "id": 1,
  "titulo": "ELDEN RING",
  "desarrollador": "FromSoftware, Inc.",
  "portada": null,
  "imagen_url": "/covers/reales/1245620.jpg",
  "categoria": 3,
  "categoria_nombre": "Acción",
  "categorias": [3, 7],
  "genero": 5,
  "genero_nombre": "RPG",
  "generos": [5, 9],
  "activo": true,
  "disponible": true
}
```

`categoria`, `categoria_nombre`, `genero` y `genero_nombre` están *deprecated*:
se conservan por compatibilidad y exponen el primero por nombre de las listas
`categorias`/`generos`, cuyos IDs también se ordenan por nombre. La escritura
acepta la forma histórica (`categoria` o `genero`) y las listas nuevas; si se
envían ambas, prevalecen las listas.

`imagen_url` guarda en la base de datos la URL de la portada de cada videojuego.
Las 140 portadas reales están en `frontend/public/covers/reales` y se sirven
desde `/covers/reales/`: cada título del fixture tiene su propia imagen.
`desarrollador` expone la compañía real del juego. Las migraciones
`catalogo.0015_videojuego_imagen_url`, `catalogo.0016_portadas_reales` y
`catalogo.0017_portadas_catalogo_real` rellenan y actualizan las URLs de los
títulos ya existentes; `catalogo.0018_videojuego_desarrollador` añade y
rellena el desarrollador, y `catalogo.0019_fichas_catalogo_real` actualiza las
descripciones en español y los géneros del fixture. El frontend
usa `imagen_url` como `cover` y cae a una portada local si la URL no responde.

### Carrito

| Método | Ruta | Cuerpo |
|---|---|---|
| `GET` | `/api/v1/carrito/` | Carrito pendiente del usuario (vacío si no existe) |
| `DELETE` | `/api/v1/carrito/` | Vacía el carrito |
| `POST` | `/api/v1/carrito/items/` | `{ "oferta": 1, "cantidad": 2 }` |
| `GET` | `/api/v1/carrito/items/{id}/` | Detalle de una línea |
| `PATCH` | `/api/v1/carrito/items/{id}/` | `{ "cantidad": 3 }`; `0` elimina la línea |
| `DELETE` | `/api/v1/carrito/items/{id}/` | Elimina la línea |

`GET /carrito/` revalida el carrito: sincroniza `precio_unitario` con
`OfertaVideojuego.precio_vigente` y devuelve `advertencias` además del sobre
habitual. Cada aviso incluye `codigo`, `detalle_id`, `titulo`, `plataforma`,
`cantidad` y `mensaje`; `precio_cambiado` añade `precio_anterior` y
`precio_nuevo`, `sin_stock` añade `stock` y `no_disponible` añade `motivo`
(`titulo_inactivo` u `oferta_retirada`). Las líneas también exponen
`disponible` y `motivo_no_disponible`. Consultar el carrito es la forma en que
el cliente acepta los precios vigentes: tras la sincronización el aviso de
precio desaparece y el total se recalcula.

No se puede agregar una oferta retirada, sin stock o cuyo `videojuego.activo`
sea `False`. La cantidad por línea está limitada por
`CARRITO_MAX_CANTIDAD_POR_LINEA` (20 por defecto, mínimo 1); superarla da `400`
en la API y un `409` de regla de negocio en el servicio compartido con las
vistas HTML.

### Pedidos

| Método | Ruta | Notas |
|---|---|---|
| `GET` | `/api/v1/pedidos/` | Pedidos del usuario; admin ve todos |
| `GET` | `/api/v1/pedidos/{id}/` | Detalle con líneas, pago y venta |
| `PATCH` | `/api/v1/pedidos/{id}/` | `{ "estado": "cancelado" }` |
| `POST` | `/api/v1/pedidos/{id}/cancelar/` | Alias explícito de cancelación |

Solo se permite cancelar pedidos en estado `pendiente`; cualquier otra
transición devuelve `409 Conflict`. Los textos de `estado` (`pendiente`,
`pagado`, `cancelado`) no cambian: ahora se leen del `codigo` del catálogo de
estados. El detalle incluye `pago` —el intento aprobado, o `null` si no lo
hay— y la lista aditiva `intentos_pago` con todos los intentos.

### Pagos y ventas

| Método | Ruta | Notas |
|---|---|---|
| `GET` | `/api/v1/pagos/` | Pagos propios; admin ve todos |
| `GET` | `/api/v1/pagos/{id}/` | Detalle |
| `POST` | `/api/v1/pagos/` | `{ "pedido": 1 }`; procesa el pago simulado |
| `GET` | `/api/v1/ventas/` | Solo administrador; filtros `desde`, `hasta`, `cliente` |

Antes de cobrar se revalida el carrito **sin modificarlo**. Si el precio, el
stock, la publicación o el estado activo del título cambiaron desde la última
consulta de `/carrito/`, la respuesta es `409 Conflict` con
`error.details.ajustes` (misma forma que las `advertencias` del carrito) y
`error.details.errores` con los mensajes legibles. No se crea ningún
`IntentoPago`: el cliente debe volver a `GET /carrito/` para ver los precios
sincronizados y reintentar el pago.

Un pago rechazado devuelve `402 Payment Required` con el registro del intento en
`error.details`. El pedido permanece pendiente y el pago puede reintentarse; un
rechazo ya no bloquea los intentos posteriores. Con varios intentos para el
mismo pedido, `POST /pagos/` devuelve el último (el aprobado cuando el pago se
completó): `monto` conserva su nombre histórico y se mapea desde
`IntentoPago.importe`, mientras el pedido expone el aprobado en `pago` y todos
en `intentos_pago`. Los textos de `estado` (`aprobado`, `rechazado`,
`pendiente`) también provienen del `codigo` del catálogo.

### Inventario (solo administrador)

| Método | Ruta | Notas |
|---|---|---|
| `GET` | `/api/v1/inventario/movimientos/` | Libro mayor completo; filtros y paginación |
| `GET` | `/api/v1/inventario/movimientos/{id}/` | Detalle de un movimiento |
| `POST` | `/api/v1/inventario/ajustes/` | Ajuste manual de stock |
| `GET` | `/api/v1/catalogo/ofertas/{id}/movimientos/` | Trazabilidad de una oferta; `404` si no existe |

Los movimientos son de solo lectura: `PUT`/`PATCH`/`DELETE` responden `405`
con `error.code = metodo_no_permitido`. Los filtros comunes de la lista y de la
trazabilidad son `oferta`, `tipo`, `motivo`, `pedido`, `usuario`, `desde` y
`hasta`. `oferta`, `pedido` y `usuario` son IDs; `tipo` y `motivo` aceptan su
`codigo` (`ENTRADA`, `SALIDA`, `VENTA`, `AJUSTE_FISICO`, …) o su ID. `desde` y
`hasta` aceptan ISO 8601 con o sin hora (`2026-11-22T10:30:00Z`); si solo se da
la fecha, `desde` es medianoche y `hasta` es el final del día. Un rango
invertido o un filtro inválido responde `400` (`datos_invalidos`). El orden es
siempre determinista: más reciente primero (`-fecha_hora`, `-pk`), con la misma
paginación (`page`, `page_size`) del resto de la API.

Ejemplo de elemento del historial:

```json
{
  "id": 12,
  "oferta": 3,
  "oferta_sku": "AZ-0001-001",
  "tipo": "ENTRADA",
  "motivo": "AJUSTE_FISICO",
  "cantidad": 3,
  "unidad": "unidad",
  "saldo_anterior": 10,
  "saldo_posterior": 13,
  "fecha_hora": "2026-11-22T15:30:00Z",
  "usuario": "admin",
  "usuario_responsable": 1,
  "detalle_pedido": null,
  "pedido": null,
  "observacion": "Conteo de caja",
  "clave_idempotencia": "clave-abc"
}
```

El cuerpo del ajuste es `{ "oferta": 3, "cantidad": -2, "motivo": "AJUSTE_FISICO",
"nota": "Merma" }`. `cantidad` es un entero distinto de cero: positivo suma
(`ENTRADA`) y negativo resta (`SALIDA`); `nota` es opcional y se guarda como
`observacion`. El usuario autenticado queda registrado como responsable. El
encabezado opcional `Idempotency-Key` evita aplicar dos veces el mismo ajuste:
repetir la clave devuelve el movimiento original sin volver a cambiar el stock.

Un ajuste que dejaría el stock negativo responde `409` con
`error.code = stock_insuficiente` y un mensaje claro; no se cambia el stock ni
se crea el movimiento. Las validaciones de entrada responden `400` con
`error.code = datos_invalidos` y el detalle por campo.

Cada pago aprobado genera una `SALIDA` por línea con motivo `VENTA`, el detalle
de pedido y el cliente como responsable; los cambios de stock desde el admin
usan `AJUSTE_FISICO` (o `CARGA_INICIAL` al dar de alta una oferta). La
cancelación de pedidos pendientes no modifica el stock y, por ello, no añade
movimientos.

### Reportes (solo administrador)

| Método | Ruta | Filtros |
|---|---|---|
| `GET` | `/api/v1/reportes/dashboard/` | — |
| `GET` | `/api/v1/reportes/ventas/` | `desde`, `hasta`, `cliente`, paginación |
| `GET` | `/api/v1/reportes/inventario/` | `filtro=todos\|agotados\|bajo_stock\|disponibles\|inactivas` |
| `GET` | `/api/v1/reportes/videojuegos/` | `categoria`, `genero`, `plataforma`, `estado`, `disponibilidad` |

Los reportes paginados devuelven `data.resultados` junto con `resumen`. Los
filtros `categoria`/`genero` usan las relaciones muchos-a-muchos con
`distinct()`, de modo que un videojuego con varias categorías no duplica
ofertas paginadas. El dashboard y `seed_catalogo` emplean las mismas tablas
normalizadas sin alterar sus respuestas.

### Soporte

| Método | Ruta | Notas |
|---|---|---|
| `GET` | `/api/v1/soporte/contactos/` | Propios; admin ve todos |
| `POST` | `/api/v1/soporte/contactos/` | Público. Usuarios autenticados pueden omitir `nombre` y `email` |
| `GET`/`PATCH`/`DELETE` | `/api/v1/soporte/contactos/{id}/` | Dueño (lectura) o administrador |
| `POST` | `/api/v1/soporte/mayor-informacion/` | `nombre`, `email`, `telefono` opcional |

### Usuarios y roles (solo administrador)

| Método | Ruta | Cuerpo / efecto |
|---|---|---|
| `GET` | `/api/v1/usuarios/` | Filtros `q`, `rol`, `activo`, `ordering` |
| `POST` | `/api/v1/usuarios/` | Crea usuario interno con contraseña y roles |
| `GET` | `/api/v1/usuarios/{id}/` | Detalle |
| `PUT`/`PATCH` | `/api/v1/usuarios/{id}/` | Datos, `roles`/`rol` e `is_active` |
| `POST` | `/api/v1/usuarios/{id}/activar/` | Activa la cuenta |
| `POST` | `/api/v1/usuarios/{id}/desactivar/` | Desactiva la cuenta |
| `GET` | `/api/v1/usuarios/{id}/auditoria/` | Historial de cambios de esa cuenta |
| `GET` | `/api/v1/roles/` | Listado completo |
| `POST` | `/api/v1/roles/` | Crea un rol (`codigo`, `nombre`, `descripcion`, `activo`) |
| `PUT`/`PATCH` | `/api/v1/roles/{id}/` | Edita etiqueta, descripción o estado |
| `DELETE` | `/api/v1/roles/{id}/` | Elimina un rol sin uso (no base) |

`POST /usuarios/` acepta `username`, `email`, `first_name`, `last_name`,
`telefono`, `direccion`, `password`, `password_confirm` y la lista `roles` de
IDs (o el campo histórico `rol` con un solo ID, pero no ambos). La contraseña se
valida con las reglas de Django y nunca se devuelve ni se audita. En las
actualizaciones, `roles` sustituye todas las asignaciones; `is_active` permite
activar o desactivar sin borrar el usuario. No se exponen bajas de usuarios
para conservar el historial.

Reglas de protección (mensaje explícito en el sobre de error):

- No se puede desactivar la propia cuenta (`409`).
- No se puede desactivar ni quitar el rol al último administrador activo (`409`).
- No se puede asignar un rol por encima del propio (`403`); jerarquía:
  `cliente` < `soporte`/`gestor_inventario` < `administrador`. Staff y
  superuser equivalen a administrador según BE-07.
- No se eliminan roles con usuarios asignados ni los roles base `cliente` y
  `administrador` (`409`).

Todos los cambios crean un `AuditoriaCuenta` con actor, cuenta afectada, acción,
detalles (antes/después), IP y fecha/hora, y se envían al log
`api.cuentas_service`. El endpoint `/auditoria/` y el admin de Django permiten
consultarlos.

`rol` y `rol_nombre` se conservan: `rol` es el primer ID por nombre de
`Usuario.roles` y `rol_nombre` es el `codigo` estable (`cliente`,
`administrador`), que mantiene el texto histórico de la API. La lista aditiva
`roles` expone todos los IDs ordenados por nombre; `/roles/` añade el campo
`codigo` y su `nombre` devuelve ese mismo código. Las propiedades de negocio
`es_administrador`/`es_cliente` siguen intactas y gobiernan los permisos.

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
- `tests/test_api_contrato_modelo_normalizado.py`

## Compatibilidad con el sitio HTML

Las rutas HTML (`/catalogo/`, `/pedidos/`, `/pagos/`, `/soporte/`, `/admin/`,
etc.) no cambian. La API reutiliza los mismos modelos, servicios y reglas de
negocio; no existe una segunda implementación de la lógica.
