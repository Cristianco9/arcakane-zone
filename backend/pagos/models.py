from django.db import models

from pedidos.models import Pedido


class EstadoIntentoPago(models.Model):
    """
    Catálogo de estados de un intento de pago.

    ``codigo`` es el identificador estable referenciado por las filas de
    ``Pago``; ``nombre`` es la etiqueta visible y editable. Regla de negocio:
    el resultado del pago no se almacena como enum en código (AZ-S1-17).
    """

    codigo = models.CharField(
        max_length=50,
        help_text="Identificador estable del estado; no es la etiqueta visible.",
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Estado de intento de pago"
        verbose_name_plural = "Estados de intento de pago"
        ordering = ["codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["codigo"],
                name="pagos_estadointentopago_codigo_unico",
            ),
        ]

    def __str__(self):
        return self.nombre


class Pago(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.PROTECT, related_name="pago")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.ForeignKey(
        EstadoIntentoPago,
        to_field="codigo",
        db_column="estado",
        db_index=False,
        on_delete=models.PROTECT,
        related_name="pagos",
        default="pendiente",
        help_text="Resultado del intento de pago (catálogo pagos.EstadoIntentoPago).",
    )
    referencia = models.CharField(max_length=100, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        constraints = [
            # Regla de negocio: un pago no puede tener monto negativo.
            models.CheckConstraint(
                condition=models.Q(monto__gte=0),
                name="pagos_pago_monto_no_negativo",
            ),
        ]

    def __str__(self):
        return f"Pago #{self.pk} — Pedido #{self.pedido_id} [{self.estado_id}]"


class Venta(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.PROTECT, related_name="venta")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    registrada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        constraints = [
            # Regla de negocio: el total consolidado de una venta no puede
            # ser negativo.
            models.CheckConstraint(
                condition=models.Q(total__gte=0),
                name="pagos_venta_total_no_negativo",
            ),
        ]
        indexes = [
            # Reportes de ventas ordenados por fecha de registro.
            models.Index(
                fields=["registrada_en"],
                name="pagos_venta_registrada_idx",
            ),
        ]

    def __str__(self):
        return f"Venta #{self.pk} — Pedido #{self.pedido_id} (${self.total})"
