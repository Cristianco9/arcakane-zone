"""Pagos simulados y ventas registradas."""
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated

from pagos.models import IntentoPago, Venta
from pagos.services import clave_idempotencia_para, procesar_pago

from ..exceptions import respuesta_error, respuesta_exitosa
from ..permissions import EsAdministrador
from ..serializers import PagoCreateSerializer, PagoSerializer, VentaSerializer
from ..utils import es_administrador, parse_fecha


class PagoViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = IntentoPago.objects.select_related("pedido", "pedido__cliente").order_by(
            "-creado_en", "-id"
        )
        if not es_administrador(self.request.user):
            queryset = queryset.filter(pedido__cliente=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return PagoCreateSerializer
        return PagoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pedido = serializer.validated_data["pedido"]

        if not es_administrador(request.user) and pedido.cliente_id != request.user.id:
            raise NotFound("El pedido no existe.")

        clave = clave_idempotencia_para(
            request.user.id, request.headers.get("Idempotency-Key")
        )
        resultado = procesar_pago(pedido, clave_idempotencia=clave)
        datos = PagoSerializer(resultado.intento, context={"request": request}).data

        if not resultado.exito:
            respuesta = respuesta_error(
                "pago_rechazado",
                resultado.mensaje,
                detalles=datos,
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
            )
        else:
            respuesta = respuesta_exitosa(
                datos,
                message=resultado.mensaje,
                status_code=status.HTTP_201_CREATED,
            )

        if resultado.repetido:
            respuesta["Idempotent-Replayed"] = "true"
        return respuesta


class VentaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VentaSerializer
    permission_classes = [EsAdministrador]

    def get_queryset(self):
        queryset = (
            Venta.objects.select_related("pedido", "pedido__cliente")
            .prefetch_related(
                "pedido__detalles__oferta__videojuego",
                "pedido__detalles__oferta__plataforma",
                "pedido__detalles__oferta__estado_publicacion",
            )
            .order_by("-registrada_en", "-id")
        )
        params = self.request.query_params
        desde = params.get("desde")
        hasta = params.get("hasta")
        cliente = params.get("cliente")

        try:
            if desde:
                queryset = queryset.filter(registrada_en__date__gte=parse_fecha(desde, "desde"))
            if hasta:
                queryset = queryset.filter(registrada_en__date__lte=parse_fecha(hasta, "hasta"))
        except ValueError as exc:
            raise ValidationError({"fechas": str(exc)}) from exc

        if cliente:
            queryset = queryset.filter(pedido__cliente_id=cliente)
        return queryset
