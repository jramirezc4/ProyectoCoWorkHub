from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from reservas.models import EstadoReserva, Espacio, ModalidadPago, Sede
from reservas.services import ReservationService, SubscriptionRequiredError
from usuarios.models import Usuario

from .models import EstadoSuscripcion, Factura, Pago, Plan, Suscripcion
from .services import PaymentService, SubscriptionService


class SubscriptionServiceTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='subscriber@example.com',
            password='password123',
            nombre='Subscriber',
        )
        self.sede = Sede.objects.create(
            nombre='Centro', direccion='Calle 1', ciudad='Bogota',
            horario_apertura='07:00', horario_cierre='20:00',
        )
        self.espacio = Espacio.objects.create(
            sede=self.sede, nombre='Sala Azul', capacidad=8,
            precio_por_hora=Decimal('25.00'),
        )
        self.plan = Plan.objects.create(
            nombre='Limitado', precio_mensual=Decimal('100.00'),
            limite_horas=2, maximo_reservas_activas=1,
        )
        now = timezone.now()
        self.subscription = Suscripcion.objects.create(
            usuario=self.user, plan=self.plan,
            fecha_inicio=now - timedelta(hours=1),
            fecha_fin=now + timedelta(days=30),
            fecha_proxima_renovacion=now + timedelta(days=30),
        )

    def reservation_times(self, hours=1):
        start = (timezone.now() + timedelta(days=1)).replace(
            hour=9, minute=0, second=0, microsecond=0,
        )
        return start, start + timedelta(hours=hours)

    def test_subscription_limits_active_reservations(self):
        start, end = self.reservation_times()
        ReservationService().create_reservation(
            usuario=self.user, espacio=self.espacio,
            fecha_inicio=start, fecha_fin=end,
            modalidad_pago=ModalidadPago.SUSCRIPCION,
        )
        next_start = end + timedelta(hours=1)

        with self.assertRaises(SubscriptionRequiredError):
            ReservationService().create_reservation(
                usuario=self.user, espacio=self.espacio,
                fecha_inicio=next_start, fecha_fin=next_start + timedelta(hours=1),
                modalidad_pago=ModalidadPago.SUSCRIPCION,
            )

    def test_subscription_usage_counts_only_active_reservations(self):
        start, end = self.reservation_times()
        reservation = ReservationService().create_reservation(
            usuario=self.user, espacio=self.espacio,
            fecha_inicio=start, fecha_fin=end,
            modalidad_pago=ModalidadPago.SUSCRIPCION,
        )
        self.assertEqual(SubscriptionService.usage(self.subscription), {
            'hours_used': Decimal('1.00'),
            'active_reservations': 1,
        })
        reservation.estado = EstadoReserva.CANCELADA
        reservation.save(update_fields=['estado'])
        self.assertEqual(SubscriptionService.usage(self.subscription)['hours_used'], Decimal('0.00'))

    def test_expired_subscription_is_marked_vencida(self):
        self.subscription.fecha_fin = timezone.now() - timedelta(minutes=1)
        self.subscription.fecha_proxima_renovacion = self.subscription.fecha_fin
        self.subscription.renovacion_automatica = False
        self.subscription.save()

        SubscriptionService.expire_due_subscriptions()

        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.estado, EstadoSuscripcion.VENCIDA)

    def test_user_can_cancel_active_subscription(self):
        SubscriptionService.cancel(self.subscription)

        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.estado, EstadoSuscripcion.CANCELADA)
        self.assertFalse(self.subscription.renovacion_automatica)

    def test_simulated_subscription_payment_creates_invoice(self):
        subscription, payment = PaymentService.create_subscription_payment(
            usuario=self.user,
            plan=self.plan,
            metodo_pago='TARJETA',
            numero_tarjeta='4242 4242 4242 4242',
            vencimiento='12/30',
            cvv='123',
        )

        self.assertEqual(payment.estado, 'APROBADO')
        self.assertTrue(Factura.objects.filter(pago=payment).exists())
        self.assertEqual(subscription.estado, EstadoSuscripcion.ACTIVA)

    def test_invalid_simulated_card_is_rejected(self):
        with self.assertRaises(ValueError):
            PaymentService.create_subscription_payment(
                usuario=self.user,
                plan=self.plan,
                metodo_pago='TARJETA',
                numero_tarjeta='4000 0000 0000 0002',
                vencimiento='12/30',
                cvv='123',
            )
        self.assertFalse(Pago.objects.filter(suscripcion__usuario=self.user).exists())

# Create your tests here.
