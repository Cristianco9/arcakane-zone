# syntax=docker/dockerfile:1

# Imagen base oficial de Node.js, con versión fija para builds reproducibles.
FROM node:22.14.0-alpine AS base

WORKDIR /app

ENV NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN chown -R node:node /app

# ── Desarrollo: servidor Vite con recarga en caliente ────────────────────────
FROM base AS development

ENV NODE_ENV=development
USER node
EXPOSE 8080
CMD ["npm", "run", "dev"]

# ── Build de producción ──────────────────────────────────────────────────────
FROM base AS build

ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# ── Producción: Nginx sin privilegios sirviendo el bundle estático ───────────
FROM nginxinc/nginx-unprivileged:1.27-alpine AS production

# El entrypoint oficial de Nginx sustituye estas variables en la plantilla
# y genera /etc/nginx/conf.d/default.conf.
ENV BACKEND_HOST=backend \
    BACKEND_PORT=8000 \
    FRONTEND_PORT=8080

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
