from datetime import time

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from finanzas.services import SubscriptionLimitError, SubscriptionService
from reservas.domain.reservation_builder import ReservationBuilder
from reservas.infra.factories import ReservationCostCalculatorFactory
from reservas.models import EstadoBase, EstadoEspacio, EstadoReserva, ModalidadPago, Reserva


class ReservationConflictError(ValidationError):
    """Indicates that the requested time range cannot be reserved."""


class SubscriptionRequiredError(ValidationError):
    """Indicates that a subscription is required for this payment mode."""


class ReservationCancellationError(ValidationError):
    """Indicates that a reservation cannot be cancelled."""


class ReservationService:
    def __init__(self, calculator_factory=None):
        self.calculator_factory = calculator_factory or ReservationCostCalculatorFactory()

    @transaction.atomic
    def create_reservation(self, *, usuario, espacio, fecha_inicio, fecha_fin, modalidad_pago):
        fecha_inicio = self._coerce_datetime(fecha_inicio, 'fecha_inicio')
        fecha_fin = self._coerce_datetime(fecha_fin, 'fecha_fin')
        self._validate_schedule(espacio, fecha_inicio, fecha_fin)
        self._validate_subscription(usuario, modalidad_pago, fecha_inicio, fecha_fin)
        self._validate_availability(espacio, fecha_inicio, fecha_fin)
        calculator = self.calculator_factory.create()
        costo_total = calculator.calculate(espacio, fecha_inicio, fecha_fin)
        reserva = ReservationBuilder().with_usuario(usuario).with_espacio(espacio).with_fechas(fecha_inicio, fecha_fin).with_modalidad_pago(modalidad_pago).with_costo_total(costo_total).build()
        reserva.estado = EstadoReserva.CONFIRMADA
        reserva.save()
        from core.tasks import send_reservation_confirmation

        send_reservation_confirmation.delay(reserva.id)
        return reserva

    @transaction.atomic
    def cancel_reservation(self, *, reserva):
        if reserva.estado not in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA):
            raise ReservationCancellationError(
                'Solo se pueden cancelar reservas pendientes o confirmadas.'
            )
        if reserva.fecha_inicio <= timezone.now():
            raise ReservationCancellationError(
                'No se puede cancelar una reserva que ya comenzó.'
            )
        reserva.estado = EstadoReserva.CANCELADA
        reserva.save(update_fields=['estado'])
        return reserva

    def is_available(self, *, espacio, fecha_inicio, fecha_fin):
        fecha_inicio = self._coerce_datetime(fecha_inicio, 'fecha_inicio')
        fecha_fin = self._coerce_datetime(fecha_fin, 'fecha_fin')
        self._validate_schedule(espacio, fecha_inicio, fecha_fin)
        return not self._has_overlap(espacio, fecha_inicio, fecha_fin)

    def _validate_subscription(self, usuario, modalidad_pago, fecha_inicio, fecha_fin):
        if modalidad_pago != ModalidadPago.SUSCRIPCION or usuario.has_full_access():
            return
        try:
            SubscriptionService.validate_reservation_limits(
                usuario=usuario,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
            )
        except SubscriptionLimitError as error:
            raise SubscriptionRequiredError(str(error)) from error

    def _validate_availability(self, espacio, fecha_inicio, fecha_fin):
        if self._has_overlap(espacio, fecha_inicio, fecha_fin):
            raise ReservationConflictError('El espacio no está disponible en ese rango de fechas.')

    def _has_overlap(self, espacio, fecha_inicio, fecha_fin):
        return Reserva.objects.filter(
            espacio=espacio,
            estado__in=[EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA],
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).exists()

    def _validate_schedule(self, espacio, fecha_inicio, fecha_fin):
        if fecha_inicio >= fecha_fin:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin.')
        if (
            fecha_inicio.minute or fecha_inicio.second or fecha_inicio.microsecond
            or fecha_fin.minute or fecha_fin.second or fecha_fin.microsecond
            or (fecha_fin - fecha_inicio).total_seconds() % 3600
        ):
            raise ValidationError('Las reservas deben usar horas completas.')
        if fecha_inicio <= timezone.now():
            raise ValidationError('La reserva debe comenzar en el futuro.')
        if fecha_inicio.date() != fecha_fin.date():
            raise ValidationError('La reserva debe comenzar y terminar el mismo día.')
        if espacio.estado != EstadoEspacio.DISPONIBLE or espacio.sede.estado != EstadoBase.ACTIVO:
            raise ValidationError('El espacio o la sede no están disponibles.')
        local_start = timezone.localtime(fecha_inicio).time()
        local_end = timezone.localtime(fecha_fin).time()
        opening = self._coerce_time(espacio.sede.horario_apertura)
        closing = self._coerce_time(espacio.sede.horario_cierre)
        if local_start < opening or local_end > closing:
            raise ValidationError(
                'La reserva debe estar dentro del horario de atención de la sede.'
            )

    def _coerce_datetime(self, value, field_name):
        if hasattr(value, 'year'):
            return value
        parsed_value = parse_datetime(value)
        if parsed_value is None:
            raise ValidationError(f'El campo {field_name} debe tener un formato datetime válido.')
        return parsed_value

    def _coerce_time(self, value):
        if isinstance(value, time):
            return value
        try:
            return time.fromisoformat(value)
        except (TypeError, ValueError) as error:
            raise ValidationError('El horario de la sede no es válido.') from error