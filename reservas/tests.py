from datetime import timedelta
from decimal import Decimal

from django.test import Client, TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from finanzas.models import Pago, Plan, Suscripcion
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
		self.start = (timezone.now() + timedelta(days=1)).replace(
			hour=9, minute=0, second=0, microsecond=0
		)
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

	def test_delete_reservation_cancels_it_and_frees_the_time_range(self):
		created = self.client.post('/api/reservas/', self.payload, format='json')

		response = self.client.delete(f"/api/reservas/{created.data['id']}/")

		self.assertEqual(response.status_code, 204)
		self.assertEqual(
			self.client.get(f"/api/reservas/{created.data['id']}/").data['estado'],
			EstadoReserva.CANCELADA,
		)
		recreated = self.client.post('/api/reservas/', self.payload, format='json')
		self.assertEqual(recreated.status_code, 201)

	def test_availability_endpoint_reports_conflicts(self):
		self.client.post('/api/reservas/', self.payload, format='json')

		response = self.client.get('/api/reservas/disponibilidad/', {
			'espacio_id': self.espacio.id,
			'fecha_inicio': self.payload['fecha_inicio'],
			'fecha_fin': self.payload['fecha_fin'],
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.data['disponible'])

	def test_reservation_outside_site_hours_is_rejected(self):
		payload = {
			**self.payload,
			'fecha_inicio': self.start.replace(hour=18).isoformat(),
			'fecha_fin': self.start.replace(hour=21).isoformat(),
		}

		response = self.client.post('/api/reservas/', payload, format='json')

		self.assertEqual(response.status_code, 400)

	def test_user_cannot_cancel_another_users_reservation(self):
		created = self.client.post('/api/reservas/', self.payload, format='json')
		other_user = Usuario.objects.create_user(
			email='other@example.com', password='password123', nombre='Otra'
		)
		self.client.force_authenticate(other_user)

		response = self.client.delete(f"/api/reservas/{created.data['id']}/")

		self.assertEqual(response.status_code, 404)

	def test_login_page_exists_and_protected_reservation_redirects(self):
		client = Client()

		login_response = client.get('/accounts/login/')
		self.assertEqual(login_response.status_code, 200)

		reservation_response = client.get('/reservas/crear/')
		self.assertEqual(reservation_response.status_code, 302)
		self.assertIn('/accounts/login/', reservation_response.url)

	def test_home_page_and_reservation_form_render(self):
		client = Client()
		client.force_login(self.user)

		home_response = client.get('/')
		self.assertEqual(home_response.status_code, 200)
		self.assertContains(home_response, 'Coworkhub')
		self.assertContains(home_response, 'Mi espacio')
		self.assertNotContains(home_response, '>Ingresar<')

		form_response = client.get('/reservas/crear/')
		self.assertEqual(form_response.status_code, 200)
		self.assertContains(form_response, 'Crear reserva')

	def test_dashboard_profile_and_registration_pages_render(self):
		client = Client()
		client.force_login(self.user)

		dashboard_response = client.get('/dashboard/')
		self.assertEqual(dashboard_response.status_code, 200)
		self.assertContains(dashboard_response, 'Tu espacio de trabajo')

		profile_response = client.get('/accounts/profile/')
		self.assertEqual(profile_response.status_code, 200)
		self.assertContains(profile_response, 'Mi perfil')

		client.logout()
		register_response = client.get('/accounts/register/')
		self.assertEqual(register_response.status_code, 200)
		self.assertContains(register_response, 'Crear cuenta')

	def test_registration_creates_user_and_redirects_to_dashboard(self):
		client = Client()
		response = client.post('/accounts/register/', {
			'nombre': 'Carlos Nuevo',
			'email': 'carlos@example.com',
			'telefono': '3001234567',
			'password': 'password123',
			'password_confirm': 'password123',
		})

		self.assertRedirects(response, '/dashboard/')
		self.assertTrue(Usuario.objects.filter(email='carlos@example.com').exists())

	def test_authenticated_user_can_open_registration_page(self):
		client = Client()
		client.force_login(self.user)

		response = client.get('/accounts/register/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Actualmente estás conectado como')

	def test_subscription_creates_subscription_and_payment(self):
		client = Client()
		client.force_login(self.user)
		plan = Plan.objects.get(nombre='Flex')

		response = client.post('/pagos/suscripciones/', {
			'plan_id': plan.id,
			'metodo_pago': 'TARJETA',
			'numero_tarjeta': '4242 4242 4242 4242',
			'vencimiento': '12/30',
			'cvv': '123',
		})

		self.assertRedirects(response, '/dashboard/')
		self.assertTrue(Suscripcion.objects.filter(usuario=self.user, plan=plan).exists())
		self.assertTrue(Pago.objects.filter(suscripcion__usuario=self.user).exists())

	def test_html_reservation_creates_individual_payment(self):
		client = Client()
		client.force_login(self.user)
		start = (timezone.now() + timedelta(days=2)).replace(
			hour=9, minute=0, second=0, microsecond=0
		)
		response = client.post('/reservas/crear/', {
			'espacio': self.espacio.id,
			'fecha_inicio': start.strftime('%Y-%m-%dT%H:%M'),
			'fecha_fin': (start + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
			'modalidad_pago': ModalidadPago.PAGO_USO,
			'metodo_pago': 'TARJETA',
			'numero_tarjeta': '4242 4242 4242 4242',
			'vencimiento': '12/30',
			'cvv': '123',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Reserva creada correctamente')
		self.assertTrue(Pago.objects.filter(reserva__usuario=self.user).exists())

	def test_logout_button_ends_the_session(self):
		client = Client()
		client.force_login(self.user)

		response = client.post('/accounts/logout/')

		self.assertRedirects(response, '/')
		self.assertEqual(client.get('/dashboard/').status_code, 302)

	def test_admin_demo_can_reserve_without_subscription_or_payment(self):
		admin_user = Usuario.objects.create_superuser(
			email='admin@demo.com', password='password123', nombre='Admin Demo'
		)
		client = Client()
		client.force_login(admin_user)
		start = (timezone.now() + timedelta(days=3)).replace(
			hour=9, minute=0, second=0, microsecond=0
		)

		response = client.post('/reservas/crear/', {
			'espacio': self.espacio.id,
			'fecha_inicio': start.strftime('%Y-%m-%dT%H:%M'),
			'fecha_fin': (start + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
			'modalidad_pago': ModalidadPago.SUSCRIPCION,
			'metodo_pago': 'TARJETA',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Reserva creada correctamente')
		self.assertFalse(Pago.objects.filter(reserva__usuario=admin_user).exists())

	def test_admin_demo_email_without_domain_suffix_has_full_access(self):
		admin_user = Usuario.objects.create_user(
			email='admin@demo', password='password123', nombre='Admin Demo Alias'
		)

		self.assertTrue(admin_user.has_full_access())
