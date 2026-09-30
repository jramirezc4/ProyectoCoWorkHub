from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.dateparse import parse_datetime

from finanzas.models import EstadoSuscripcion, Suscripcion
from reservas.domain.reservation_builder import ReservationBuilder
from reservas.infra.factories import ReservationCostCalculatorFactory
from reservas.models import EstadoReserva, ModalidadPago, Reserva


class ReservationConflictError(ValidationError):
    """Indicates that the requested time range cannot be reserved."""


class SubscriptionRequiredError(ValidationError):
    """Indicates that a subscription is required for this payment mode."""


class ReservationService:
    def __init__(self, calculator_factory=None):
        self.calculator_factory = calculator_factory or ReservationCostCalculatorFactory()

    @transaction.atomic
    def create_reservation(self, *, usuario, espacio, fecha_inicio, fecha_fin, modalidad_pago):
        fecha_inicio = self._coerce_datetime(fecha_inicio, 'fecha_inicio')
        fecha_fin = self._coerce_datetime(fecha_fin, 'fecha_fin')
        self._validate_subscription(usuario, modalidad_pago, fecha_inicio, fecha_fin)
        self._validate_availability(espacio, fecha_inicio, fecha_fin)
        calculator = self.calculator_factory.create()
        costo_total = calculator.calculate(espacio, fecha_inicio, fecha_fin)
        reserva = ReservationBuilder().with_usuario(usuario).with_espacio(espacio).with_fechas(fecha_inicio, fecha_fin).with_modalidad_pago(modalidad_pago).with_costo_total(costo_total).build()
        reserva.estado = EstadoReserva.CONFIRMADA
        reserva.save()
        return reserva

    def _validate_subscription(self, usuario, modalidad_pago, fecha_inicio, fecha_fin):
        if modalidad_pago != ModalidadPago.SUSCRIPCION or usuario.has_full_access():
            return
        exists = Suscripcion.objects.filter(
            usuario=usuario,
            estado=EstadoSuscripcion.ACTIVA,
            fecha_inicio__lte=fecha_inicio,
            fecha_fin__gte=fecha_fin,
        ).exists()
        if not exists:
            raise SubscriptionRequiredError('El usuario no tiene una suscripción activa para esta reserva.')

    def _validate_availability(self, espacio, fecha_inicio, fecha_fin):
        occupied = Reserva.objects.filter(
            espacio=espacio,
            estado__in=[EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA],
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).exists()
        if occupied:
            raise ReservationConflictError('El espacio no está disponible en ese rango de fechas.')

    def _coerce_datetime(self, value, field_name):
        if hasattr(value, 'year'):
            return value
        parsed_value = parse_datetime(value)
        if parsed_value is None:
            raise ValidationError(f'El campo {field_name} debe tener un formato datetime válido.')
        return parsed_value