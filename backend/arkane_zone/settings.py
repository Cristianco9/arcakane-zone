from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")


def _validar_secret_key(valor: str, debug: bool) -> str:
    """Rechaza claves vacías o de ejemplo antes de arrancar en producción."""
    clave = (valor or "").strip()
    if not clave:
        raise ImproperlyConfigured(
            "SECRET_KEY está vacía. Genera una clave real con: openssl rand -hex 32"
        )

    # La suite usa settings_test.py con claves cortas a propósito; el módulo
    # de producción sí exige una clave con entropía suficiente para `check --deploy`.
    es_test = env("DJANGO_SETTINGS_MODULE", default="").endswith("settings_test")
    if debug or es_test:
        return clave

    ejemplos = {
        "cambia-esto-por-una-clave-larga-y-aleatoria",
        "replace-with-a-long-random-secret-key",
        "test-key",
        "secret",
        "changeme",
    }
    if (
        clave in ejemplos
        or clave.startswith("django-insecure-")
        or len(clave) < 50
        or len(set(clave)) < 5
    ):
        raise ImproperlyConfigured(
            "SECRET_KEY es de ejemplo o demasiado débil para producción. "
            "Genera una clave real con: openssl rand -hex 32"
        )
    return clave


SECRET_KEY = _validar_secret_key(env("SECRET_KEY", default=""), env("DEBUG"))
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "backend"])

# Render expone el hostname del servicio en esta variable; lo agregamos automáticamente.
RENDER_EXTERNAL_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME", default=None)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    # django-unfold debe ir antes de django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # API REST
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "api",
    # Apps del proyecto
    "cuentas",
    "catalogo",
    "inventario",
    "pedidos",
    "pagos",
    "reportes",
    "soporte",
]

MIDDLEWARE = [
    # Debe ir primero: cubre también a SecurityMiddleware y garantiza que
    # todo log de la API tenga un request_id y toda respuesta lo devuelva.
    "api.middleware.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # debe ir justo después de SecurityMiddleware
    # CORS debe ejecutarse antes de CommonMiddleware.
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Garantiza respuestas JSON ante errores no controlados dentro de /api/.
    "api.middleware.ApiErrorMiddleware",
]

ROOT_URLCONF = "arkane_zone.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [
                "catalogo.templatetags.arkane_filters",
            ],
        },
    },
]

WSGI_APPLICATION = "arkane_zone.wsgi.application"

_database_url = env("DATABASE_URL", default="")
if _database_url:
    _db_config = env.db_url_config(_database_url)
else:
    # En Docker Compose la configuración se pasa como variables POSTGRES_*.
    # Así se evita tener que URL-encodear contraseñas dentro de DATABASE_URL.
    _db_config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST", default="db"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
_db_config["CONN_MAX_AGE"] = 0
DATABASES = {"default": _db_config}

AUTH_USER_MODEL = "cuentas.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise: sirve estáticos comprimidos y con caché en producción.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Almacenamiento de medios ──────────────────────────────────────────────────
# Si AWS_ACCESS_KEY_ID está definida en .env → Supabase Storage (S3).
# Si no está → disco local (comportamiento por defecto de Django).
_USE_S3 = bool(env("AWS_ACCESS_KEY_ID", default=""))

if _USE_S3:
    AWS_ACCESS_KEY_ID      = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY  = env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="media")
    AWS_S3_ENDPOINT_URL    = env("AWS_S3_ENDPOINT_URL")
    AWS_S3_REGION_NAME     = env("AWS_S3_REGION_NAME", default="us-west-2")
    # Dominio público del bucket, sin protocolo. Formato esperado:
    #   <project-ref>.supabase.co/storage/v1/object/public/media
    AWS_S3_CUSTOM_DOMAIN   = env("AWS_S3_CUSTOM_DOMAIN")
    AWS_QUERYSTRING_AUTH   = False   # bucket público → URLs sin firma
    AWS_DEFAULT_ACL        = "public-read"
    AWS_S3_FILE_OVERWRITE  = False   # evita sobreescribir archivos con mismo nombre

    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    }
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/cuentas/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/cuentas/login/"

# Correo: backend de consola para desarrollo (imprime el enlace de reseteo en la terminal).
# En producción cambiar por smtp.EmailBackend y configurar SMTP.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "Arcakane Zone <noreply@arkanezone.co>"

# CSRF: permite peticiones desde el dominio de Render en producción.
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
)
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# ── Caché compartida y protección contra fuerza bruta ────────────────────────
# Por defecto los contadores de throttling viven en una tabla de PostgreSQL,
# creada por `manage.py createcachetable` (no requiere migraciones). Con
# REDIS_URL se usa Redis; el paquete `redis` debe estar instalado en el entorno.
def tasa_desde_entorno(nombre: str, defecto: str) -> str | None:
    """Lee una tasa DRF; una cadena vacía desactiva el scope indicado."""
    valor = env(f"THROTTLE_RATE_{nombre}", default=defecto)
    return str(valor).strip() or None


CACHE_TABLE = env("CACHE_TABLE", default="django_cache")
REDIS_URL = env("REDIS_URL", default=None)
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": CACHE_TABLE,
        }
    }

# 0 = confiar solo en REMOTE_ADDR; > 0 = leer X-Forwarded-For desde la derecha.
THROTTLE_NUM_PROXIES = max(0, env.int("THROTTLE_NUM_PROXIES", default=0))
LOGIN_MAX_FAILED_ATTEMPTS = max(1, env.int("LOGIN_MAX_FAILED_ATTEMPTS", default=5))
LOGIN_FAILURE_WINDOW_SECONDS = max(1, env.int("LOGIN_FAILURE_WINDOW_SECONDS", default=900))
LOGIN_LOCKOUT_SECONDS = max(1, env.int("LOGIN_LOCKOUT_SECONDS", default=900))

# Tope de unidades por línea del carrito. Se valida en la API y en el servicio
# para que la regla sea la misma en REST y en las vistas HTML.
CARRITO_MAX_CANTIDAD_POR_LINEA = max(
    1, env.int("CARRITO_MAX_CANTIDAD_POR_LINEA", default=20)
)

# ── API REST ─────────────────────────────────────────────────────────────────
# Autenticación por token propio (clientes desacoplados) y por sesión/cookie
# (misma sesión que usa el sitio y el admin de Django).
def ttl_token_desde_entorno() -> int:
    """Días de vigencia de los tokens de API; mínimo 1 día."""
    return max(1, env.int("API_TOKEN_TTL_DAYS", default=7))


API_TOKEN_TTL_DAYS = ttl_token_desde_entorno()

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Primero: un token inválido/vencido debe dar 401, no 403.
        "api.authentication.ApiTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Por defecto todo exige autenticación; cada vista pública lo declara.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "api.renderers.EnvelopeJSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "api.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "api.exceptions.api_exception_handler",
    # Throttling: globales anon/user + scopes específicos de las rutas sensibles.
    "DEFAULT_THROTTLE_CLASSES": [
        "api.throttling.AnonimoRateThrottle",
        "api.throttling.UsuarioRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": tasa_desde_entorno("ANON", "100/min"),
        "user": tasa_desde_entorno("USER", "1000/hour"),
        "login": tasa_desde_entorno("LOGIN", "10/min"),
        "registro": tasa_desde_entorno("REGISTRO", "5/hour"),
        "contacto": tasa_desde_entorno("CONTACTO", "5/hour"),
    },
    "NUM_PROXIES": THROTTLE_NUM_PROXIES,
    # Respuestas JSON legibles (tildes y eñes sin escapes).
    "UNICODE_JSON": True,
    "COMPACT_JSON": False,
    # Los importes viajan como cadenas decimales para no perder precisión.
    "COERCE_DECIMAL_TO_STRING": True,
}

# CORS: el frontend puede vivir en otro origen (por ejemplo, un dominio
# distinto en Render). Con el proxy /api de Vite/Nginx no hace falta, pero
# se deja configurable para integraciones directas.
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
)
CORS_ALLOW_CREDENTIALS = True

# Detrás de un proxy inverso (Nginx, Render, etc.) que termina TLS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST", default=False)

# ── Endurecimiento HTTP y cookies ────────────────────────────────────────────
# Detrás del proxy, Nginx/Render envían X-Forwarded-Proto: https, por lo que
# SECURE_SSL_REDIRECT puede permanecer activo sin romper el tráfico legítimo.
# El healthcheck interno envía esa misma cabecera (ver compose.yaml).
# En desarrollo (`DEBUG=True`) se desactiva para no romper el runserver local.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=not DEBUG)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = env("SESSION_COOKIE_SAMESITE", default="Lax")
CSRF_COOKIE_SAMESITE = env("CSRF_COOKIE_SAMESITE", default="Lax")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY", default="same-origin")
X_FRAME_OPTIONS = "DENY"

SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
# `preload` solo debe enviarse cuando se piensa someter el dominio a la lista
# de precarga de HSTS. Se puede desactivar con SECURE_HSTS_PRELOAD=False.
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)

# ── Observabilidad (AZ-S2-BE-09) ─────────────────────────────────────────────
# `LOG_LEVEL=DEBUG` en desarrollo; en producción se emite consola JSON por
# stdout para que la plataforma (Docker/Render) lo recolecte sin archivos.
LOG_LEVEL = env("LOG_LEVEL", default="INFO").upper()
if LOG_LEVEL not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}:
    LOG_LEVEL = "INFO"

_FORMATTER = "json" if not DEBUG else "texto"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_context": {"()": "api.observabilidad.RequestContextFilter"},
    },
    "formatters": {
        "json": {"()": "api.observabilidad.JsonFormatter"},
        "texto": {"()": "api.observabilidad.TextoFormatter"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": LOG_LEVEL,
            "formatter": _FORMATTER,
            "filters": ["request_context"],
        }
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "filters": ["request_context"],
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "filters": ["request_context"],
            "propagate": False,
        },
    },
}

# django-unfold — paleta azul eléctrico (valores en RGB sin #)
UNFOLD = {
    "SITE_TITLE": "Arcakane Zone",
    "SITE_HEADER": "Arcakane Zone Admin",
    "SITE_URL": "/",
    "COLORS": {
        "primary": {
            "50":  "224 242 254",
            "100": "186 230 253",
            "200": "125 211 252",
            "300": "56  189 248",
            "400": "14  165 233",
            "500": "2   132 199",   # acento principal admin (#0284C7)
            "600": "3   105 161",
            "700": "7   89  133",
            "800": "12  74  110",
            "900": "8   47  73",
            "950": "5   25  50",
        },
    },
}
