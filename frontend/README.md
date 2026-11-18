# Arcakane Zone — Frontend

Aplicación **Vite + React + TypeScript + Tailwind CSS**. El issue histórico menciona Next.js,
pero este repositorio usa Vite (issue AZ-S2-01); el stack Docker está construido sobre el
frontend real y el `Dockerfile` expone los targets `development` y `production`.

## Estructura

```text
frontend/
├── src/
│   ├── App.tsx           # Componente raíz
│   ├── main.tsx          # Punto de entrada
│   ├── index.css         # Estilos globales
│   └── App.css
├── public/
├── Dockerfile            # targets: development y production
├── .dockerignore
├── nginx.conf.template   # Proxy /api y fallback SPA en producción
├── vite.config.ts        # Host, puerto y proxy hacia el backend
├── package.json
└── package-lock.json
```

## Docker

Desde la raíz del repositorio:

```bash
cp .env.example .env      # rellena los valores "replace-with-..."
docker compose up -d --build
```

- **Desarrollo:** Vite dev server en `FRONTEND_PORT` (por defecto `8080`), publicado en
  `FRONTEND_PUBLISHED_PORT` (por defecto `5173`). Usuario `node`, sin root.
- **Producción:** `npm run build` y Nginx en `FRONTEND_PORT`, con el prefijo `/api`
  conservado hacia el servicio `backend`.
- El proxy se construye con `BACKEND_HOST` y `BACKEND_PORT`, así que el navegador
  nunca usa `localhost:8000` para la API.

Producción:

```bash
docker compose -f compose.yaml -f compose.prod.yaml up -d --build
```

### Variables que consume

| Variable | Descripción |
|---|---|
| `FRONTEND_PORT` | Puerto interno del contenedor (Vite o Nginx). |
| `FRONTEND_PUBLISHED_PORT` | Puerto publicado en el host. |
| `VITE_API_BASE_URL` | Prefijo de la API en el navegador; por defecto `/api`. |
| `BACKEND_HOST` | Nombre del servicio backend en la red Docker (`backend`). |
| `BACKEND_PORT` | Puerto interno del backend (`8000`). |

Todas están declaradas en [`.env.example`](../.env.example). No hay valores sensibles
en el Compose ni en el Dockerfile.

## Conexión con la API

El frontend llama a rutas relativas bajo `/api/v1/...`:

```ts
const respuesta = await fetch("/api/v1/health/");
```

- Desarrollo: Vite reenvía `/api/v1/...` a `http://backend:8000/api/v1/...`.
- Producción: Nginx hace lo mismo usando el nombre de servicio `backend`.
- El prefijo `/api` **no** se elimina: la API versionada vive en `/api/v1/`.

Contrato completo: [`docs/api/API.md`](../docs/api/API.md).

## Desarrollo local sin Docker

```bash
cd frontend
npm ci
FRONTEND_PORT=5173 VITE_DEV_PROXY_TARGET=http://localhost:8000 npm run dev
```

Disponible en <http://localhost:5173/>. Si omites `VITE_DEV_PROXY_TARGET`, Vite apunta a
`http://localhost:8000`, que es útil cuando el backend corre en local.

## Scripts

```bash
npm run dev       # Servidor de desarrollo con HMR
npm run build     # TypeScript + build de producción en dist/
npm run preview   # Sirve el build localmente
npm run lint      # ESLint
```
