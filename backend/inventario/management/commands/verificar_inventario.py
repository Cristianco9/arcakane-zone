"""Conciliación de solo lectura entre ``OfertaVideojuego.stock`` y el ledger."""
from django.core.management.base import BaseCommand, CommandError

from catalogo.models import OfertaVideojuego
from inventario.models import MovimientoInventarioOfertaVideojuego


class Command(BaseCommand):
    help = (
        "Concilia el stock registrado de cada oferta con la suma de sus "
        "movimientos. Solo lee: no corrige nada."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--oferta",
            type=int,
            dest="oferta_id",
            metavar="ID",
            help="Verificar únicamente la oferta con ese identificador.",
        )

    def handle(self, *args, **options):
        ofertas = OfertaVideojuego.objects.order_by("pk")
        oferta_id = options.get("oferta_id")
        if oferta_id is not None:
            ofertas = ofertas.filter(pk=oferta_id)
            if not ofertas.exists():
                raise CommandError(f"No existe la oferta con ID {oferta_id}.")

        self.stdout.write(
            "Conciliación de inventario (solo lectura). "
            "ENTRADA suma, SALIDA resta y AJUSTE/CARGA_INICIAL fija el saldo "
            "(apertura o reconteo); un stock inicial cargado fuera del libro "
            "mayor aparece como diferencia."
        )

        revisadas = 0
        discrepancias = []
        total_registrado = 0
        total_calculado = 0

        for oferta in ofertas:
            revisadas += 1
            suma, aperturas = self._suma_movimientos(oferta.pk)
            total_registrado += oferta.stock
            total_calculado += suma
            if suma != oferta.stock:
                discrepancias.append((oferta, suma, aperturas))

        self.stdout.write(f"Ofertas revisadas: {revisadas}")
        self.stdout.write(f"Stock registrado:  {total_registrado}")
        self.stdout.write(f"Suma movimientos:  {total_calculado}")
        self.stdout.write(f"Consistentes:      {revisadas - len(discrepancias)}")
        self.stdout.write(f"Discrepancias:     {len(discrepancias)}")

        for oferta, suma, aperturas in discrepancias:
            self.stdout.write(
                self.style.ERROR(
                    f"  Oferta {oferta.pk} ({oferta.sku}): "
                    f"stock registrado={oferta.stock}, suma movimientos={suma}, "
                    f"diferencia={oferta.stock - suma:+d}"
                    + (
                        f" — {aperturas} movimiento(s) de apertura/reconteo"
                        if aperturas
                        else ""
                    )
                )
            )

        if discrepancias:
            raise CommandError(
                f"Se encontraron {len(discrepancias)} discrepancia(s) de inventario."
            )
        self.stdout.write(self.style.SUCCESS("Inventario conciliado correctamente."))

    @staticmethod
    def _suma_movimientos(oferta_id):
        """Devuelve ``(saldo calculado, número de aperturas/reconteos)``."""
        movimientos = (
            MovimientoInventarioOfertaVideojuego.objects.filter(oferta_id=oferta_id)
            .select_related("tipo_movimiento")
            .order_by("fecha_hora", "pk")
            .values_list("cantidad", "tipo_movimiento__naturaleza")
        )
        saldo = 0
        aperturas = 0
        for cantidad, naturaleza in movimientos:
            if naturaleza == "entrada":
                saldo += cantidad
            elif naturaleza == "salida":
                saldo -= cantidad
            elif naturaleza == "ajuste":
                saldo = cantidad
                aperturas += 1
        return saldo, aperturas
