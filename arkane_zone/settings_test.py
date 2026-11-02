# Configuración exclusiva para la suite de pruebas automatizadas.
# Usa SQLite en memoria → jamás toca la base de datos de Supabase.
from .settings import *  # noqa: F401, F403

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
