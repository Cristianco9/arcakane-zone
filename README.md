# Arkane Zone

Sistema web de gestión de una tienda de videojuegos, desarrollado con **Django 5.2**. Incluye catálogo, carrito, pedidos, pagos, reportes y soporte al cliente, con panel de administración personalizado (django-unfold).

## Módulos

| App | Descripción |
|-----|-------------|
| `cuentas` | Usuarios con modelo personalizado (`Usuario`) y roles |
| `catalogo` | Videojuegos, categorías, géneros y plataformas |
| `pedidos` | Carrito de compras, pedidos y cancelación |
| `pagos` | Pagos y ventas |
| `reportes` | Reportes del negocio |
| `soporte` | Formulario de contacto / soporte |

## Tecnologías

- Python 3.12, Django 5.2
- PostgreSQL (`psycopg2`) vía `DATABASE_URL`
- django-unfold (admin), WhiteNoise (estáticos), Gunicorn
- Almacenamiento de medios opcional en S3 compatible (`boto3`, `django-storages`)
- Pytest para pruebas
- Despliegue en Render (`render.yaml`, `build.sh`)

## Instalación local

```bash
git clone https://github.com/MiguelH/NOMBRE-DEL-REPO.git
cd NOMBRE-DEL-REPO

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # y completa los valores
python manage.py migrate
python manage.py seed_catalogo   # datos de ejemplo del catálogo
python manage.py createsuperuser
python manage.py runserver
```

## Variables de entorno

Se configuran en un archivo `.env` (no se sube al repositorio). Ver `.env.example`.

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `SECRET_KEY` | Sí | Clave secreta de Django |
| `DATABASE_URL` | Sí | Ej: `postgres://usuario:clave@host:5432/db` |
| `DEBUG` | No | `True` en desarrollo (por defecto `False`) |
| `ALLOWED_HOSTS` | No | Lista separada por comas |
| `AWS_*` | No | Solo si usas almacenamiento S3 para medios |

## Pruebas

Las pruebas usan SQLite en memoria (`settings_test.py`), así que no tocan tu base de datos real.

```bash
pytest
```

## Despliegue

El proyecto está preparado para Render: `render.yaml` define el servicio y `build.sh` instala dependencias, recolecta estáticos y ejecuta migraciones.

## Autor

Miguel Angel Herrera Lujan — [@MiguelH](https://github.com/MiguelH)
