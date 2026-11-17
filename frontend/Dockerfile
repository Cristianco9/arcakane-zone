# syntax=docker/dockerfile:1

# Versión fija de Node compatible con Vite 8 (requiere Node >= 20.19).
FROM node:22.14.0-alpine AS base

WORKDIR /app

RUN mkdir -p /app && chown -R node:node /app
USER node

COPY --chown=node:node package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# ── Desarrollo: Vite dev server con HMR ──────────────────────────────────────
FROM base AS development

ENV NODE_ENV=development

COPY --chown=node:node . .

EXPOSE 8080

CMD ["npm", "run", "dev"]

# ── Build: genera los archivos estáticos ─────────────────────────────────────
FROM base AS build

ENV NODE_ENV=production

COPY --chown=node:node . .

ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

# ── Producción: Nginx sirve el SPA y hace de proxy inverso de /api ───────────
FROM nginx:1.27-alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 8080
