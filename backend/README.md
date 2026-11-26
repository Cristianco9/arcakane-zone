# Arcakane Zone — Backend (Django)

Aplicación backend del sistema Arcakane Zone. Contiene el modelo de datos, las reglas de negocio, la autenticación, el panel administrativo y la lógica de catálogo, carrito, pedidos, pagos, reportes y soporte.

> **Estado actual:** el backend sirve la interfaz existente con Django Templates + HTMX **y** una API REST/JSON versionada en `/api/v1/`. Ambas capas comparten modelos, servicios, permisos y reglas de negocio. La documentación del contrato está en [`docs/api/API.md`](../docs/api/API.md).

## Docker

El backend forma parte del stack Docker Compose definido en la raíz del repositorio. Para levantar todo (PostgreSQL, backend, frontend y pgAdmin):

```bash
cp .env.example .env      # en la raíz del repositorio
# editar secretos
docker compose up -d --build
```

La guía completa —variables, puertos, migraciones, superusuario, logs, respaldos y diferencias entre desarrollo y producción— está en el [README principal](../README.md).

Archivos relevantes de esta carpeta:

- `Dockerfile`: imagen de producción basada en `python:3.12.9-slim`, usuario no privilegiado y Gunicorn por defecto.
- `.dockerignore`: excluye `.env`, `.venv`, pruebas, medios y estáticos locales del contexto de build.
- `docker/entrypoint.sh`: espera a PostgreSQL, crea la tabla de caché si hace falta, aplica migraciones, recolecta estáticos y opcionalmente ejecuta `seed_catalogo`.

Comandos habituales dentro del contenedor:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_catalogo
docker compose exec backend python manage.py shell
```

### Throttling y caché

Los límites de la API (`anon`, `user`, `login`, `registro`, `contacto`) se
guardan en caché. Por defecto se usa la tabla `django_cache` de PostgreSQL;
el entrypoint la crea con `python manage.py createcachetable` de forma
idempotente. Para usar Redis, define `REDIS_URL` (requiere el paquete `redis`).
Las tasas y el bloqueo de login se configuran con las variables
`THROTTLE_RATE_*`, `THROTTLE_NUM_PROXIES` y `LOGIN_*` documentadas en
[`.env.example`](.env.example) y en [`docs/api/API.md`](../docs/api/API.md).

## Estructura

```text
backend/
├── arkane_zone/          # Configuración: settings.py, settings_test.py, urls.py, wsgi.py, asgi.py
├── catalogo/             # Categorías, plataformas, géneros y videojuegos
├── cuentas/              # Usuario personalizado, roles, registro y perfil
├── pedidos/              # Carrito, pedidos, detalle y cancelación
├── pagos/                # Pago simulado, pagos y ventas
├── reportes/             # Dashboard y reportes (solo staff)
├── soporte/              # Contacto, solicitud de información y ayuda
├── api/                  # API REST: serializers, vistas, rutas, permisos y errores
├── templates/            # Templates Django (interfaz HTML)
├── tests/                # Pruebas de API, carrito, pagos, cancelación y autorización
├── manage.py
├── requirements.txt
├── pytest.ini
├── build.sh              # Build de Render
├── Dockerfile            # Imagen para Docker Compose
├── .dockerignore
├── docker/
│   └── entrypoint.sh     # Espera DB, migra, recolecta estáticos y arranca
└── .env.example
```

## Requisitos

- Python 3.12 o superior.
- PostgreSQL 14 o superior para un entorno similar a producción.
- `pip` y un entorno virtual.
- Opcional: SQLite para pruebas locales rápidas o smoke tests.

## Configuración local

```bash
cd backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Editar .env con valores reales
```

### Variables de entorno

`arkane_zone/settings.py` lee `backend/.env` mediante `django-environ`.

| Variable | Obligatoria | Descripción |
|---|---|---|
| `SECRET_KEY` | Sí | Clave secreta de Django. No debe compartirse ni versionarse. Con `DEBUG=False` se exige una clave real de al menos 50 caracteres; la arranque falla si está vacía o es de ejemplo (`openssl rand -hex 32`). |
| `DATABASE_URL` | Condicional | URL de conexión PostgreSQL, por ejemplo `postgres://usuario:clave@host:5432/db`. Si no se define, se usan las variables `POSTGRES_*`. |
| `API_TOKEN_TTL_DAYS` | No | Días de vigencia de los tokens de API; por defecto `7` (mínimo `1`). |
| `CARRITO_MAX_CANTIDAD_POR_LINEA` | No | Unidades máximas por línea del carrito; por defecto `20` (mínimo `1`). Aplica a API y vistas HTML. |
| `POSTGRES_DB` | Condicional | Nombre de la base de datos cuando se usa el fallback de Docker Compose. |
| `POSTGRES_USER` | Condicional | Usuario de PostgreSQL cuando se usa el fallback de Docker Compose. |
| `POSTGRES_PASSWORD` | Condicional | Contraseña de PostgreSQL cuando se usa el fallback de Docker Compose. |
| `POSTGRES_HOST` | No | Host de PostgreSQL; por defecto `db` en Docker. |
| `POSTGRES_PORT` | No | Puerto de PostgreSQL; por defecto `5432`. |
| `DEBUG` | No | `True` en desarrollo; por defecto `False`. |
| `ALLOWED_HOSTS` | No | Lista separada por comas. Por defecto `localhost,127.0.0.1,backend`. |
| `CSRF_TRUSTED_ORIGINS` | No | Orígenes permitidos para CSRF. En Render se agrega automáticamente el host público. |
| `CORS_ALLOWED_ORIGINS` | No | Orígenes permitidos para CORS (lista separada por comas). Solo hace falta si el frontend llama a la API sin el proxy `/api`. |
| `SECURE_SSL_REDIRECT` | No | Fuerza HTTPS cuando `DEBUG=False`; por defecto `True` en producción y `False` en desarrollo. El proxy debe enviar `X-Forwarded-Proto: https`. |
| `USE_X_FORWARDED_HOST` | No | Usa `X-Forwarded-Host` detrás de un proxy; por defecto `False`. |
| `SECURE_REFERRER_POLICY` | No | Política de `Referrer-Policy`; por defecto `same-origin`. |
| `SESSION_COOKIE_SAMESITE` | No | Política `SameSite` de la cookie de sesión; por defecto `Lax`. |
| `SECURE_HSTS_PRELOAD` | No | Añade `preload` a HSTS; por defecto `True`. Desactívalo si el dominio no se va a someter a la lista de precarga. |
| `LOG_LEVEL` | No | Nivel de logs (`INFO` por defecto). Con `DEBUG=False` se emite JSON en `stdout`. |
| `RENDER_EXTERNAL_HOSTNAME` | No | La define Render; se agrega a `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`. |
| `AWS_ACCESS_KEY_ID` | No | Si se define, activa almacenamiento S3 para medios. |
| `AWS_SECRET_ACCESS_KEY` | No | Credencial S3. |
| `AWS_STORAGE_BUCKET_NAME` | No | Bucket de medios; por defecto `media`. |
| `AWS_S3_ENDPOINT_URL` | No | Endpoint S3 compatible (por ejemplo, Supabase Storage). |
| `AWS_S3_REGION_NAME` | No | Región S3; por defecto `us-west-2`. |
| `AWS_S3_CUSTOM_DOMAIN` | No | Dominio público del bucket, sin protocolo. |

No se deben subir `.env` ni credenciales al repositorio. El archivo `.env.example` solo contiene placeholders.

### Base de datos y datos iniciales

Con PostgreSQL configurado en `DATABASE_URL`:

```bash
python manage.py migrate
python manage.py seed_catalogo
python manage.py createsuperuser
```

`seed_catalogo` crea roles, las seis categorías base, plataformas, géneros y
**120 videojuegos de ejemplo** (20 por categoría). Si hay categorías adicionales,
también siembra 20 títulos para cada una: el objetivo global es
`max(100, 20 × número_de_categorías)`. Es idempotente: repetirlo no crea
duplicados y solo completa las relaciones que falten.

Al terminar imprime la evidencia de carga:

```text
  Videojuegos:    120 creados
  Ofertas:        167 creadas
  Total videojuegos: 120 (mínimo 120)
    - Acción: 20
    - Aventura: 20
    - Carreras: 20
    - Deportes: 20
    - Estrategia: 20
    - RPG: 20
```

Para **restablecer** solo los datos semilla (borra también usuarios y pedidos):

```bash
python manage.py flush --noinput
python manage.py migrate
python manage.py seed_catalogo
python manage.py createsuperuser
```

### Conciliación de inventario

`verificar_inventario` es de solo lectura: compara `OfertaVideojuego.stock` con la suma de movimientos del libro mayor, imprime un resumen y las discrepancias (oferta, stock registrado, suma y diferencia), y termina con código distinto de cero si hay diferencias.

```bash
python manage.py verificar_inventario
python manage.py verificar_inventario --oferta 12
```

La suma aplica `ENTRADA` (`+`), `SALIDA` (`-`) y `AJUSTE`/`CARGA_INICIAL` (fija el saldo de apertura o reconteo). Un stock inicial cargado fuera del libro mayor aparece como diferencia; el comando nunca corrige nada.

Para un smoke test local con SQLite se puede usar una URL temporal, sin modificar `.env`:

```bash
SECRET_KEY=test-key DATABASE_URL=sqlite:///db.sqlite3 DEBUG=True python manage.py migrate
SECRET_KEY=test-key DATABASE_URL=sqlite:///db.sqlite3 DEBUG=True python manage.py seed_catalogo
```

### Ejecutar el servidor

```bash
python manage.py runserver
```

- Aplicación: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## Pruebas

La suite usa `arkane_zone/settings_test.py`, que cambia la base de datos a SQLite en memoria y usa hashing rápido de contraseñas.

```bash
# Dependencias de desarrollo y pruebas
pip install -r requirements-dev.txt

SECRET_KEY=test-key DATABASE_URL=sqlite:///db.sqlite3 DEBUG=True pytest
```

Estado verificado de la suite: **1871 pruebas**, todas pasan. Incluye pruebas de
la API REST (`tests/test_api_*.py`), la matriz RBAC, la administración de
usuarios/roles por API y las pruebas originales de la interfaz HTML.

`settings_test.py` fuerza `DEBUG=True`, desactiva las redirecciones HTTPS y usa
SQLite en memoria, por lo que la suite es independiente del entorno.

## Rutas principales

| Ruta | Descripción |
|---|---|
| `/` y `/catalogo/` | Catálogo con filtros por categoría, plataforma, género y búsqueda |
| `/catalogo/<id>/` | Detalle de videojuego |
| `/cuentas/registro/` | Registro de clientes |
| `/cuentas/login/` | Inicio de sesión (auth de Django) |
| `/cuentas/perfil/` | Perfil del usuario autenticado |
| `/cuentas/perfil/cambiar-password/` | Cambio de contraseña |
| `/pedidos/carrito/` | Carrito del usuario |
| `/pedidos/mis-pedidos/` | Historial de pedidos |
| `/pedidos/<id>/` | Detalle de pedido |
| `/pagos/checkout/<pedido_id>/` | Resumen previo al pago |
| `/pagos/procesar/<pedido_id>/` | Procesamiento del pago simulado |
| `/reportes/*` | Dashboard, ventas, inventario y videojuegos (solo staff) |
| `/soporte/contacto/` | Formulario de contacto |
| `/soporte/mayor-informacion/` | Solicitud de información |
| `/soporte/ayuda/` | Centro de ayuda |
| `/admin/` | Panel administrativo con django-unfold |

## API REST

- **Base:** `/api/v1/` (raíz navegable en `GET /api/v1/`).
- **Salud:** `GET /api/v1/health/` (*liveness*) y `GET /api/v1/health/ready/` (*readiness*, consulta la BD y responde `503` si falla).
- **Trazabilidad:** cada respuesta `/api/` devuelve `X-Request-ID` (se acepta la cabecera del cliente); el mismo valor se incluye en los logs JSON de producción y en los errores `500`.
- **Carrito:** `GET /carrito/` sincroniza precios y devuelve `advertencias` (`precio_cambiado`, `sin_stock`, `no_disponible`); el pago responde `409` con `error.details.ajustes` si el carrito cambió después de esa consulta.
- **Autenticación:** token propio con vencimiento
  (`Authorization: Token <clave>`) o sesión de Django con `X-CSRFToken`.
  Login y registro devuelven `token` y `expires_at`; existen
  `POST /api/v1/auth/token/refresh/` y `POST /api/v1/auth/logout-all/`.
  Los tokens antiguos de DRF ya no autentican: vuelve a iniciar sesión.
- **Respuestas:** sobre uniforme `{"success": true, "data": ...}` y errores
  `{"success": false, "error": {"code", "message", "details"}}`.
- **Paginación:** `?page=1&page_size=20`; búsqueda `?q=`; orden `?ordering=`.

Recursos principales: catálogo, carrito, pedidos, pagos, ventas, inventario
(movimientos y ajustes), reportes, soporte, usuarios y roles. La administración
de cuentas (solo administradores) permite crear/editar usuarios con roles,
activarlos o desactivarlos y mantener el CRUD de roles; las reglas de
autodesactivación, último administrador y jerarquía de roles se aplican en
`api/cuentas_service.py`, y cada cambio queda en `AuditoriaCuenta`. El detalle
de rutas, cuerpos y códigos de estado está
en [`docs/api/API.md`](../docs/api/API.md).

```bash
# Token
curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"cliente","password":"secreto"}'

# Catálogo público
curl -s "http://localhost:8000/api/v1/catalogo/videojuegos/?q=zelda"
```

La API y el sitio HTML comparten servicios, por lo que una regla de negocio
(cancelación, checkout, descuento de stock) se comporta igual por ambas vías.

## Despliegue en Render

El blueprint está en la raíz del repositorio: [`../render.yaml`](../render.yaml).

- `rootDir: backend`: Render ejecuta los comandos dentro de esta carpeta.
- Build: `./build.sh`.
  - Instala `requirements.txt`.
  - Ejecuta `python manage.py check --deploy`.
  - Ejecuta `collectstatic --no-input`.
  - Ejecuta `migrate`.
- Start: `gunicorn arkane_zone.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`.
- Healthcheck: `healthCheckPath: /api/v1/health/ready/`.
- Estáticos: WhiteNoise con `CompressedManifestStaticFilesStorage`.
- Variables sensibles: `SECRET_KEY`, `DATABASE_URL` y `ALLOWED_HOSTS` se configuran manualmente en Render (`sync: false`).

### Consideraciones de producción

- **Medios:** si no se configuran las variables `AWS_*`, las portadas y fotos se guardan en el sistema de archivos local de Render, que es efímero. Además, `/media/` solo se sirve con `DEBUG=True`. Para producción se debe configurar S3/Supabase Storage o aceptar explícitamente la limitación.
- **Correo:** `EMAIL_BACKEND` está fijado al backend de consola. El reseteo de contraseña no envía correos reales y los enlaces quedan en los logs. Configurar SMTP antes de habilitar recuperación de contraseña en producción.
- **Proxy HTTPS:** `SECURE_PROXY_SSL_HEADER` está configurado para confiar en `X-Forwarded-Proto`. Con `DEBUG=False`, `SECURE_SSL_REDIRECT` queda activo; el proxy (y el healthcheck interno de Compose) debe enviar esa cabecera con valor `https`.
- **Readiness:** `healthCheckPath` de Render y el healthcheck de Compose apuntan a `/api/v1/health/ready/`; no a `/health/`.
- **Migraciones:** actualmente se ejecutan durante el build. Evaluar un `preDeployCommand` antes de un despliegue con más de una instancia.
- **Validación:** `build.sh` y la CI ejecutan `python manage.py check --deploy` con `DEBUG=False`; debe terminar sin advertencias.

## Convivencia con el frontend

La API está disponible para que el frontend React consuma los recursos de forma
desacoplada, mientras las plantillas HTML siguen funcionando como respaldo y
para el panel administrativo:

1. El frontend usa `/api/v1/...` mediante el proxy de Vite/Nginx, sin CORS en
   el flujo normal.
2. Los clientes externos pueden autenticarse con el token propio de la API.
3. La administración interna permanece en `/admin/` con django-unfold.
4. Las plantillas se pueden retirar gradualmente sin tocar la lógica de negocio.

## Documentación relacionada

- [README principal](../README.md)
- [API REST](../docs/api/API.md)
- [Auditoría inicial](../docs/audit/INITIAL-AUDIT.md)
- [Plan del Sprint 1](../docs/sprints/SPRINT-1.md)
- [Frontend](../frontend/README.md)
