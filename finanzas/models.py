from django.conf import settings
from django.db import models

from reservas.models import Reserva


class EstadoPlan(models.TextChoices):
	ACTIVO = 'ACTIVO', 'Activo'
	INACTIVO = 'INACTIVO', 'Inactivo'


class EstadoSuscripcion(models.TextChoices):
	ACTIVA = 'ACTIVA', 'Activa'
	VENCIDA = 'VENCIDA', 'Vencida'
	CANCELADA = 'CANCELADA', 'Cancelada'


class EstadoPago(models.TextChoices):
	PENDIENTE = 'PENDIENTE', 'Pendiente'
	APROBADO = 'APROBADO', 'Aprobado'
	RECHAZADO = 'RECHAZADO', 'Rechazado'
	REEMBOLSADO = 'REEMBOLSADO', 'Reembolsado'


class MetodoPago(models.TextChoices):
	TARJETA = 'TARJETA', 'Tarjeta'
	PSE = 'PSE', 'PSE'
	TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'
	OTRO = 'OTRO', 'Otro'


class TipoPago(models.TextChoices):
	RESERVA = 'RESERVA', 'Reserva'
	SUSCRIPCION_INICIAL = 'SUSCRIPCION_INICIAL', 'Suscripción inicial'
	RENOVACION = 'RENOVACION', 'Renovación'


class Plan(models.Model):
	nombre = models.CharField(max_length=120)
	precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)
	limite_horas = models.PositiveIntegerField(help_text='Horas por mes')
	maximo_reservas_activas = models.PositiveIntegerField(default=0)
	acceso_premium = models.BooleanField(default=False)
	prioridad_reserva = models.BooleanField(default=False)
	estado = models.CharField(max_length=20, choices=EstadoPlan.choices, default=EstadoPlan.ACTIVO)

	def __str__(self) -> str:
		return self.nombre


class Suscripcion(models.Model):
	usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suscripciones')
	plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='suscripciones')
	fecha_inicio = models.DateTimeField()
	fecha_fin = models.DateTimeField()
	fecha_proxima_renovacion = models.DateTimeField()
	estado = models.CharField(max_length=20, choices=EstadoSuscripcion.choices, default=EstadoSuscripcion.ACTIVA)
	renovacion_automatica = models.BooleanField(default=True)

	def __str__(self) -> str:
		return f'{self.usuario} - {self.plan}'


class Pago(models.Model):
	reserva = models.ForeignKey(Reserva, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos')
	suscripcion = models.ForeignKey(Suscripcion, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos')
	fecha_pago = models.DateTimeField(auto_now_add=True)
	monto = models.DecimalField(max_digits=10, decimal_places=2)
	metodo_pago = models.CharField(max_length=20, choices=MetodoPago.choices)
	estado = models.CharField(max_length=20, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
	referencia_transaccion = models.CharField(max_length=120, blank=True)
	tipo_pago = models.CharField(max_length=30, choices=TipoPago.choices)

	def __str__(self) -> str:
		return f'Pago #{self.pk or "nuevo"}'


class Factura(models.Model):
	pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='factura')
	numero_factura = models.CharField(max_length=50, unique=True)
	fecha_emision = models.DateTimeField(auto_now_add=True)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2)
	impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	total = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self) -> str:
		return self.numero_factura
