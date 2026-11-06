from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.utils import timezone

from reservas.models import EstadoReserva, Espacio, Reserva, Sede
from usuarios.models import Usuario

from .models import EstadoResena, Resena
from .services import ReviewService


class ReviewTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='reviewer@example.com',
            password='password123',
            nombre='Reviewer',
        )
        sede = Sede.objects.create(
            nombre='Centro', direccion='Calle 1', ciudad='Bogota',
            horario_apertura='07:00', horario_cierre='20:00',
        )
        espacio = Espacio.objects.create(
            sede=sede, nombre='Sala Azul', capacidad=8,
            precio_por_hora=Decimal('25.00'),
        )
        start = timezone.now() - timedelta(days=1)
        self.reservation = Reserva.objects.create(
            usuario=self.user,
            espacio=espacio,
            fecha_inicio=start,
            fecha_fin=start + timedelta(hours=2),
            estado=EstadoReserva.COMPLETADA,
            costo_total=Decimal('50.00'),
        )

    def test_owner_can_create_review_for_completed_reservation(self):
        review = ReviewService().create(
            reserva=self.reservation,
            calificacion=5,
            comentario='Excelente espacio.',
        )

        self.assertEqual(review.estado, EstadoResena.PUBLICADA)
        self.assertEqual(Resena.objects.count(), 1)

    def test_pending_reservation_cannot_be_reviewed(self):
        self.reservation.estado = EstadoReserva.CONFIRMADA
        self.reservation.save(update_fields=['estado'])

        with self.assertRaises(ValidationError):
            ReviewService().create(
                reserva=self.reservation,
                calificacion=5,
                comentario='Todavía no.',
            )

    def test_review_form_is_protected_by_owner_and_completion(self):
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/opiniones/crear/{self.reservation.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Califica tu experiencia')
