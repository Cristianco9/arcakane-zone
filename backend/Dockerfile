# syntax=docker/dockerfile:1

# Imagen base oficial de Python, con versión fija para builds reproducibles.
FROM python:3.12.9-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# libpq es la única dependencia de sistema necesaria en tiempo de ejecución
# (psycopg2-binary ya incluye el cliente PostgreSQL compilado).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ejecución con usuario no privilegiado.
RUN useradd --create-home --uid 10001 appuser \
    && chmod +x /app/docker/entrypoint.sh \
    && mkdir -p /app/media /app/staticfiles \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "arkane_zone.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
