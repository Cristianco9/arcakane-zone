"""Libro mayor de inventario: consulta de movimientos y ajustes manuales."""
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from inventario.models import (
    MotivoMovimientoInventario,
    MovimientoInventarioOfertaVideojuego,
    TipoMovimientoInventario,
)

from ..exceptions import respuesta_exitosa
from ..inventario_service import registrar_ajuste
from ..pagination import StandardResultsSetPagination
from ..permissions import EsAdministrador
from ..serializers import AjusteInventarioSerializer, MovimientoInventarioSerializer
from ..utils import parse_fecha_hora


def _id_entero(valor, campo):
    try:
        return int(valor)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            {campo: "Debe ser un identificador numérico."}
        ) from exc


def filtrar_movimientos(queryset, request):
    """Aplica los filtros comunes del libro mayor (lista y trazabilidad)."""
    params = request.query_params

    oferta = params.get("oferta")
    if oferta:
        queryset = queryset.filter(oferta_id=_id_entero(oferta, "oferta"))

    tipo = params.get("tipo")
    if tipo:
        codigos = list(TipoMovimientoInventario.objects.values_list("codigo", flat=True))
        if tipo in codigos:
            queryset = queryset.filter(tipo_movimiento__codigo=tipo)
        elif tipo.isdigit():
            queryset = queryset.filter(tipo_movimiento_id=int(tipo))
        else:
            raise ValidationError(
                {"tipo": "Valor inválido. Opciones: " + ", ".join(sorted(codigos))}
            )

    motivo = params.get("motivo")
    if motivo:
        codigos = list(
            MotivoMovimientoInventario.objects.values_list("codigo", flat=True)
        )
        if motivo in codigos:
            queryset = queryset.filter(motivo__codigo=motivo)
        elif motivo.isdigit():
            queryset = queryset.filter(motivo_id=int(motivo))
        else:
            raise ValidationError(
                {"motivo": "Valor inválido. Opciones: " + ", ".join(sorted(codigos))}
            )

    pedido = params.get("pedido")
    if pedido:
        queryset = queryset.filter(
            detalle_pedido__pedido_id=_id_entero(pedido, "pedido")
        )

    usuario = params.get("usuario")
    if usuario:
        queryset = queryset.filter(
            usuario_responsable_id=_id_entero(usuario, "usuario")
        )

    desde = params.get("desde")
    hasta = params.get("hasta")
    inicio = fin = None
    if desde:
        try:
            inicio = parse_fecha_hora(desde, "desde")
        except ValueError as exc:
            raise ValidationError({"desde": str(exc)}) from exc
    if hasta:
        try:
            fin = parse_fecha_hora(hasta, "hasta", final=True)
        except ValueError as exc:
            raise ValidationError({"hasta": str(exc)}) from exc
    if inicio and fin and inicio > fin:
        raise ValidationError(
            {"hasta": "La fecha final no puede ser anterior a la inicial."}
        )
    if inicio:
        queryset = queryset.filter(fecha_hora__gte=inicio)
    if fin:
        queryset = queryset.filter(fecha_hora__lte=fin)

    return queryset


def responder_listado_movimientos(vista, queryset):
    """Pagina y serializa el historial con el sobre habitual de la API."""
    pagina = vista.paginate_queryset(queryset)
    if pagina is not None:
        serializer = MovimientoInventarioSerializer(
            pagina, many=True, context=vista.get_serializer_context()
        )
        return vista.get_paginated_response(serializer.data)
    serializer = MovimientoInventarioSerializer(
        queryset, many=True, context=vista.get_serializer_context()
    )
    return respuesta_exitosa(serializer.data)


class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    """Historial completo del libro mayor, de solo lectura."""

    serializer_class = MovimientoInventarioSerializer
    permission_classes = [EsAdministrador]
    pagination_class = StandardResultsSetPagination
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        queryset = (
            MovimientoInventarioOfertaVideojuego.objects.select_related(
                "oferta",
                "tipo_movimiento",
                "motivo",
                "usuario_responsable",
                "detalle_pedido__pedido",
            )
            .order_by("-fecha_hora", "-pk")
        )
        return filtrar_movimientos(queryset, self.request)


class AjusteInventarioView(APIView):
    """Ajuste manual de stock: positivo suma, negativo resta."""

    permission_classes = [EsAdministrador]

    def post(self, request):
        serializer = AjusteInventarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        try:
            movimiento, creado = registrar_ajuste(
                oferta=datos["oferta"],
                cantidad=datos["cantidad"],
                motivo_codigo=datos["motivo"].codigo,
                usuario=request.user,
                nota=datos.get("nota", ""),
                clave_idempotencia=request.headers.get("Idempotency-Key"),
            )
        except ValueError as exc:
            raise ValidationError({"cantidad": str(exc)}) from exc

        mensaje = (
            "Ajuste aplicado correctamente."
            if creado
            else "El ajuste ya estaba registrado con esa clave de idempotencia."
        )
        return respuesta_exitosa(
            MovimientoInventarioSerializer(movimiento, context={"request": request}).data,
            message=mensaje,
            status_code=status.HTTP_201_CREATED,
        )
