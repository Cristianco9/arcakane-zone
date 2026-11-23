# Configuración exclusiva para la suite de pruebas automatizadas.
# Usa SQLite en memoria → jamás toca la base de datos de Supabase.
import tempfile

from .settings import *  # noqa: F401, F403

# WhiteNoise exige que STATIC_ROOT exista; en tests evitamos depender de un
# ``collectstatic`` previo creando un directorio temporal.
STATIC_ROOT = tempfile.mkdtemp(prefix="arkane-zone-static-")

# La suite debe ser independiente de las variables del entorno: con DEBUG=False
# SECURE_SSL_REDIRECT redirigiría las peticiones HTTP de las pruebas (301).
DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Hasheo rápido: hace que los tests sean 10x más veloces
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Desactiva el backend real de correo durante tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# La suite no depende del entorno: usa el TTL por defecto salvo override.
API_TOKEN_TTL_DAYS = 7

# Las vistas del admin renderizan estáticos; en tests no hay collectstatic
# ni manifiesto de WhiteNoise, así que usamos el almacenamiento simple.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
