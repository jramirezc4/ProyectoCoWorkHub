from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import EstadoPago, EstadoSuscripcion, Pago, Suscripcion, TipoPago


class PaymentService:
    @staticmethod
    @transaction.atomic
    def create_reservation_payment(reserva, *, metodo_pago):
        return Pago.objects.create(
            reserva=reserva,
            monto=reserva.costo_total,
            metodo_pago=metodo_pago,
            estado=EstadoPago.APROBADO,
            tipo_pago=TipoPago.RESERVA,
            referencia_transaccion=f'RESERVA-{reserva.id}',
        )

    @staticmethod
    @transaction.atomic
    def create_subscription_payment(*, usuario, plan, metodo_pago):
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
        payment = Pago.objects.create(
            suscripcion=subscription,
            monto=plan.precio_mensual,
            metodo_pago=metodo_pago,
            estado=EstadoPago.APROBADO,
            tipo_pago=TipoPago.SUSCRIPCION_INICIAL,
            referencia_transaccion=f'SUSCRIPCION-{subscription.id}',
        )
        return subscription, payment