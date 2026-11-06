from datetime import timedelta
from decimal import Decimal
import re
import uuid

from django.db import transaction
from django.utils import timezone

from reservas.models import EstadoReserva

from .models import (
    EstadoPago,
    EstadoSuscripcion,
    Factura,
    Pago,
    Suscripcion,
    TipoPago,
)


DEMO_CARD_NUMBER = '4242424242424242'
DEMO_CARD_EXPIRY = '12/30'
DEMO_CARD_CVV = '123'


class SimulatedPaymentGateway:
    """Academic payment gateway that never contacts an external provider."""

    @staticmethod
    def authorize(card_number=None, card_expiry=None, card_cvv=None):
        card_number = re.sub(r'\D', '', card_number or DEMO_CARD_NUMBER)
        card_expiry = (card_expiry or '').strip()
        card_cvv = re.sub(r'\D', '', card_cvv or '')
        if (
            card_number != DEMO_CARD_NUMBER
            or card_expiry != DEMO_CARD_EXPIRY
            or card_cvv != DEMO_CARD_CVV
        ):
            raise ValueError(
                'Pago rechazado. Usa la tarjeta demo 4242 4242 4242 4242, '
                'vencimiento 12/30 y CVV 123.'
            )
        return f'SIM-{uuid.uuid4().hex[:16].upper()}'


def create_invoice(payment):
    return Factura.objects.create(
        pago=payment,
        numero_factura=f'FAC-{payment.id:06d}',
        subtotal=payment.monto,
        impuestos=Decimal('0.00'),
        total=payment.monto,
    )


class PaymentService:
    @staticmethod
    @transaction.atomic
    def create_reservation_payment(
        reserva, *, metodo_pago, numero_tarjeta=None, vencimiento=None, cvv=None
    ):
        reference = SimulatedPaymentGateway.authorize(
            numero_tarjeta, vencimiento, cvv
        )
        payment = Pago.objects.create(
            reserva=reserva,
            monto=reserva.costo_total,
            metodo_pago=metodo_pago,
            estado=EstadoPago.APROBADO,
            tipo_pago=TipoPago.RESERVA,
            referencia_transaccion=reference,
        )
        create_invoice(payment)
        return payment

    @staticmethod
    @transaction.atomic
    def create_subscription_payment(
        *, usuario, plan, metodo_pago, numero_tarjeta=None, vencimiento=None,
        cvv=None
    ):
        start = timezone.now()
        end = start + timedelta(days=30)
        subscription = Suscripcion.objects.create(
            usuario=usuario,
            plan=plan,
            fecha_inicio=start,
            fecha_fin=end,
            fecha_proxima_renovacion=end,
            estado=EstadoSuscripcion.ACTIVA,
            renovacion_automatica=True,
        )
        reference = SimulatedPaymentGateway.authorize(
            numero_tarjeta, vencimiento, cvv
        )
        payment = Pago.objects.create(
            suscripcion=subscription,
            monto=plan.precio_mensual,
            metodo_pago=metodo_pago,
            estado=EstadoPago.APROBADO,
            tipo_pago=TipoPago.SUSCRIPCION_INICIAL,
            referencia_transaccion=reference,
        )
        create_invoice(payment)
        return subscription, payment


class SubscriptionLimitError(Exception):
    """Indicates that a reservation exceeds subscription limits."""


class SubscriptionService:
    @staticmethod
    @transaction.atomic
    def expire_due_subscriptions():
        now = timezone.now()
        due_subscriptions = Suscripcion.objects.select_related('plan').filter(
            estado=EstadoSuscripcion.ACTIVA,
            fecha_fin__lte=now,
        )
        renewed = 0
        expired = 0
        for subscription in due_subscriptions:
            if subscription.renovacion_automatica:
                duration = subscription.fecha_fin - subscription.fecha_inicio
                subscription.fecha_inicio = subscription.fecha_fin
                subscription.fecha_fin = subscription.fecha_fin + duration
                subscription.fecha_proxima_renovacion = subscription.fecha_fin
                subscription.save(update_fields=[
                    'fecha_inicio', 'fecha_fin', 'fecha_proxima_renovacion',
                ])
                renewed += 1
            else:
                subscription.estado = EstadoSuscripcion.VENCIDA
                subscription.save(update_fields=['estado'])
                expired += 1
        return {'renewed': renewed, 'expired': expired}

    @classmethod
    def active_for(cls, usuario, *, at=None):
        cls.expire_due_subscriptions()
        at = at or timezone.now()
        return Suscripcion.objects.select_related('plan').filter(
            usuario=usuario,
            estado=EstadoSuscripcion.ACTIVA,
            fecha_inicio__lte=at,
            fecha_fin__gt=at,
        ).order_by('-fecha_fin').first()

    @staticmethod
    def usage(subscription):
        reservations = subscription.usuario.reservas.filter(
            estado__in=[EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA],
            fecha_inicio__gte=subscription.fecha_inicio,
            fecha_fin__lte=subscription.fecha_fin,
        )
        seconds = sum(
            (reservation.fecha_fin - reservation.fecha_inicio).total_seconds()
            for reservation in reservations
        )
        return {
            'hours_used': Decimal(str(seconds / 3600)).quantize(Decimal('0.01')),
            'active_reservations': reservations.count(),
        }

    @classmethod
    def validate_reservation_limits(cls, *, usuario, fecha_inicio, fecha_fin):
        subscription = cls.active_for(usuario, at=fecha_inicio)
        if subscription is None:
            raise SubscriptionLimitError(
                'El usuario no tiene una suscripción activa para esta reserva.'
            )
        if fecha_fin > subscription.fecha_fin:
            raise SubscriptionLimitError(
                'La reserva termina después de la suscripción activa.'
            )
        usage = cls.usage(subscription)
        duration_hours = Decimal(str(
            (fecha_fin - fecha_inicio).total_seconds() / 3600
        )).quantize(Decimal('0.01'))
        if usage['hours_used'] + duration_hours > subscription.plan.limite_horas:
            raise SubscriptionLimitError(
                'La reserva supera las horas disponibles del plan.'
            )
        if (
            subscription.plan.maximo_reservas_activas
            and usage['active_reservations'] >= subscription.plan.maximo_reservas_activas
        ):
            raise SubscriptionLimitError(
                'La reserva supera el máximo de reservas activas del plan.'
            )
        return subscription

    @staticmethod
    @transaction.atomic
    def cancel(subscription):
        if subscription.estado != EstadoSuscripcion.ACTIVA:
            raise ValueError('Solo se puede cancelar una suscripción activa.')
        subscription.estado = EstadoSuscripcion.CANCELADA
        subscription.renovacion_automatica = False
        subscription.save(update_fields=['estado', 'renovacion_automatica'])
        return subscription