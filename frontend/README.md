# Arkane Zone — Frontend

Aplicación de interfaz de usuario de Arkane Zone, inicializada con **Vite + React + TypeScript + Tailwind CSS**.

> **Nota:** el issue AZ-S1-22 menciona Next.js, pero el repositorio ya contiene este frontend Vite (issue AZ-S2-01). El stack Docker está preparado para el frontend actual. Si se migra a Next.js, solo se reemplaza el `Dockerfile` y el comando de arranque.

## Estructura

```text
frontend/
├── src/
│   ├── App.tsx           # Componente raíz
│   ├── main.tsx          # Punto de entrada
│   ├── index.css         # Tailwind
│   └── App.css
├── public/
├── Dockerfile            # Etapas development, build y production
├── .dockerignore
├── nginx.conf.template   # Configuración de producción (proxy /api/*)
├── vite.config.ts        # Puerto, host y proxy hacia el backend
├── package.json
└── package-lock.json
```

## Docker

El frontend forma parte del stack definido en la raíz del repositorio:

```bash
cp .env.example .env      # en la raíz
# editar secretos
docker compose up -d --build
```

- **Desarrollo:** contenedor con Vite dev server en `FRONTEND_PORT` (por defecto `8080`), publicado en `FRONTEND_PUBLISHED_PORT` (por defecto `5173`).
- **Producción:** `docker compose -f compose.yaml -f compose.prod.yaml up -d --build` compila el bundle y lo sirve con Nginx sin privilegios.
- El proxy `/api/*` reenvía al servicio `backend` por la red interna `arkane_net`; no usa `localhost` del host.
- El contenedor de desarrollo se ejecuta con el usuario `node`; el de producción con el usuario sin privilegios de la imagen de Nginx.

Variables que consume el frontend (definidas en el `.env` raíz):

| Variable | Descripción |
|---|---|
| `FRONTEND_PORT` | Puerto interno del contenedor (Vite o Nginx). |
| `FRONTEND_PUBLISHED_PORT` | Puerto publicado en el host. |
| `VITE_API_BASE_URL` | Ruta base de la API para el navegador; por defecto `/api`. |

El destino del proxy se construye con `BACKEND_HOST` y `BACKEND_PORT` (por defecto `backend:8000`), de modo que si cambias el puerto del backend el frontend lo sigue automáticamente. Para desarrollo local sin Docker puedes exportar `VITE_DEV_PROXY_TARGET` antes de `npm run dev`.

En producción, Nginx recibe `BACKEND_HOST`, `BACKEND_PORT` y `FRONTEND_PORT` desde el Compose y genera la configuración final con `envsubst`.

## Desarrollo local sin Docker

```bash
cd frontend
npm ci
npm run dev
```

Disponible en <http://localhost:5173/>. El proxy `/api/*` apunta por defecto a `http://backend:8000`, que solo existe dentro de la red de Docker. Para desarrollo local sin Docker, define el destino real:

```bash
VITE_DEV_PROXY_TARGET=http://localhost:8000 npm run dev
```

## Scripts

```bash
npm run dev       # Servidor de desarrollo con HMR
npm run build     # TypeScript + build de producción en dist/
npm run preview   # Sirve el build localmente
npm run lint      # ESLint
```

## Conexión con la API

El frontend debe llamar a rutas relativas bajo `/api/`:

```ts
const response = await fetch("/api/catalogo/");
```

- En desarrollo, Vite reenvía `/api/catalogo/` a `http://backend:8000/catalogo/`.
- En producción, Nginx hace el mismo reenvío usando el nombre de servicio `backend`.
- Esto evita CORS y evita depender de direcciones `localhost` del host.

## Documentación relacionada

- [README principal](../README.md)
- [Backend](../backend/README.md)
