from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from reservas.models import EstadoReserva, Espacio, Sede, ModalidadPago
from usuarios.models import Usuario


class ReservationApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = Usuario.objects.create_user(
			email='ana@example.com', password='password123', nombre='Ana'
		)
		self.sede = Sede.objects.create(
			nombre='Centro', direccion='Calle 1', ciudad='Bogota',
			horario_apertura='07:00', horario_cierre='20:00',
		)
		self.espacio = Espacio.objects.create(
			sede=self.sede, nombre='Sala Azul', capacidad=8,
			precio_por_hora=Decimal('25.00'),
		)
		self.start = timezone.now() + timedelta(days=1)
		self.payload = {
			'espacio_id': self.espacio.id,
			'fecha_inicio': self.start.isoformat(),
			'fecha_fin': (self.start + timedelta(hours=2)).isoformat(),
			'modalidad_pago': ModalidadPago.PAGO_USO,
		}
		self.client.force_authenticate(self.user)

	def test_create_reservation_returns_201_and_calculates_cost(self):
		response = self.client.post('/api/reservas/', self.payload, format='json')

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['estado'], EstadoReserva.CONFIRMADA)
		self.assertEqual(response.data['costo_total'], '50.00')

	def test_overlapping_reservation_returns_409(self):
		self.client.post('/api/reservas/', self.payload, format='json')

		response = self.client.post('/api/reservas/', self.payload, format='json')

		self.assertEqual(response.status_code, 409)

	def test_invalid_payload_returns_400(self):
		response = self.client.post('/api/reservas/', {'espacio_id': self.espacio.id}, format='json')

		self.assertEqual(response.status_code, 400)

	def test_missing_reservation_returns_404(self):
		response = self.client.get('/api/reservas/9999/')

		self.assertEqual(response.status_code, 404)
