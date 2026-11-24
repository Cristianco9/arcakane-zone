from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.Model):
    codigo = models.CharField(
        max_length=50,
        help_text="Identificador estable del rol; no es la etiqueta visible.",
    )
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        constraints = [
            models.UniqueConstraint(
                fields=["codigo"],
                name="cuentas_rol_codigo_unico",
            ),
        ]

    def __str__(self):
        return self.nombre


class UsuarioRol(models.Model):
    """
    Asignación explícita usuario↔rol (tabla puente).

    Regla de negocio: un usuario puede tener varios roles y un rol puede
    asignarse a varios usuarios; la pareja (usuario, rol) no se repite.
    No incluye metadatos de auditoría (asignado_en, asignado_por, activo);
    si en el futuro se añade ``asignado_por`` (FK a usuario) hará falta
    declarar ``through_fields`` en el ManyToManyField.
    """

    usuario = models.ForeignKey(
        "cuentas.Usuario",
        on_delete=models.CASCADE,
        related_name="asignaciones_rol",
    )
    rol = models.ForeignKey(
        "cuentas.Rol",
        on_delete=models.PROTECT,
        related_name="asignaciones_rol",
    )

    class Meta:
        verbose_name = "Asignación de rol"
        verbose_name_plural = "Asignaciones de rol"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "rol"],
                name="cuentas_usuariorol_usuario_rol_unico",
            ),
        ]
        indexes = [
            # Búsqueda inversa rol→usuarios (usuario→roles lo cubre el UniqueConstraint).
            models.Index(
                fields=["rol"],
                name="cuentas_urol_rol_idx",
            ),
        ]

    def __str__(self):
        return f"{self.usuario} — {self.rol}"


class Usuario(AbstractUser):
    roles = models.ManyToManyField(
        "cuentas.Rol",
        through="cuentas.UsuarioRol",
        related_name="usuarios",
        blank=True,
    )
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    foto = models.ImageField(upload_to="usuarios/", null=True, blank=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def es_administrador(self) -> bool:
        """Compatibilidad transitoria: conserva el acceso si es staff o tiene rol administrador."""
        return self.is_staff or self.roles.filter(codigo="administrador").exists()

    @property
    def es_cliente(self) -> bool:
        return self.roles.filter(codigo="cliente").exists()


class AuditoriaCuenta(models.Model):
    """Registro de quién y cuándo cambió una cuenta o un rol (AZ-S2-BE-08)."""

    ACCIONES = [
        ("usuario_creado", "Usuario creado"),
        ("usuario_actualizado", "Usuario actualizado"),
        ("roles_actualizados", "Roles actualizados"),
        ("usuario_activado", "Usuario activado"),
        ("usuario_desactivado", "Usuario desactivado"),
        ("rol_creado", "Rol creado"),
        ("rol_actualizado", "Rol actualizado"),
        ("rol_eliminado", "Rol eliminado"),
    ]

    usuario_afectado = models.ForeignKey(
        "cuentas.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias",
    )
    actor = models.ForeignKey(
        "cuentas.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias_realizadas",
    )
    accion = models.CharField(max_length=40, choices=ACCIONES)
    detalles = models.JSONField(default=dict, blank=True)
    direccion_ip = models.GenericIPAddressField(null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Auditoría de cuenta"
        verbose_name_plural = "Auditorías de cuentas"
        ordering = ["-fecha_hora", "-pk"]
        indexes = [
            models.Index(fields=["fecha_hora"], name="cuentas_auditoria_fecha_idx"),
            models.Index(
                fields=["usuario_afectado", "fecha_hora"],
                name="cuentas_auditoria_usuario_idx",
            ),
        ]

    def __str__(self):
        return f"{self.get_accion_display()} — {self.actor or 'sistema'}"
