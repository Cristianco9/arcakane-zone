"""Modelos propios de la API REST.

El token se guarda solo como hash SHA-256; la clave en claro se devuelve
únicamente al emitirlo (login, registro o refresh).
"""
import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Token(models.Model):
    """Token de API con vencimiento; un usuario puede tener varios."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_tokens",
    )
    key_hash = models.CharField(max_length=64, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()

    class Meta:
        verbose_name = "Token de API"
        verbose_name_plural = "Tokens de API"
        indexes = [
            models.Index(
                fields=["usuario", "expira_en"],
                name="api_token_usuario_expira_idx",
            ),
        ]
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Token de API de {self.usuario}"

    @staticmethod
    def hash_clave(clave: str) -> str:
        return hashlib.sha256(clave.encode("utf-8")).hexdigest()

    @classmethod
    def emitir(cls, usuario):
        """Crea un token nuevo y devuelve ``(instancia, clave_en_claro)``."""
        clave = secrets.token_urlsafe(32)
        ttl_dias = max(1, int(getattr(settings, "API_TOKEN_TTL_DAYS", 7)))
        expira_en = timezone.now() + timedelta(days=ttl_dias)
        token = cls.objects.create(
            usuario=usuario,
            key_hash=cls.hash_clave(clave),
            expira_en=expira_en,
        )
        return token, clave

    @property
    def vigente(self) -> bool:
        return self.expira_en > timezone.now()
