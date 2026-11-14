from django.db import models

from pedidos.models import Pedido


class Pago(models.Model):
    class Estado(models.TextChoices):
        APROBADO = "aprobado", "Aprobado"
        RECHAZADO = "rechazado", "Rechazado"
        PENDIENTE = "pendiente", "Pendiente"

    pedido = models.OneToOneField(Pedido, on_delete=models.PROTECT, related_name="pago")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
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
        return f"Pago #{self.pk} — Pedido #{self.pedido_id} [{self.estado}]"


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
