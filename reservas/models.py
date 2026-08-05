from django.conf import settings
from django.db import models


class EstadoBase(models.TextChoices):
	ACTIVO = 'ACTIVO', 'Activo'
	INACTIVO = 'INACTIVO', 'Inactivo'


class EstadoEspacio(models.TextChoices):
	DISPONIBLE = 'DISPONIBLE', 'Disponible'
	MANTENIMIENTO = 'MANTENIMIENTO', 'Mantenimiento'
	OCUPADO = 'OCUPADO', 'Ocupado'


class TipoEspacio(models.TextChoices):
	OFICINA_PRIVADA = 'OFICINA_PRIVADA', 'Oficina privada'
	SALA_REUNION = 'SALA_REUNION', 'Sala de reunión'
	COWORKING = 'COWORKING', 'Coworking'
	AUDITORIO = 'AUDITORIO', 'Auditorio'
	OTRO = 'OTRO', 'Otro'


class EstadoReserva(models.TextChoices):
	PENDIENTE = 'PENDIENTE', 'Pendiente'
	CONFIRMADA = 'CONFIRMADA', 'Confirmada'
	CANCELADA = 'CANCELADA', 'Cancelada'
	COMPLETADA = 'COMPLETADA', 'Completada'


class ModalidadPago(models.TextChoices):
	SUSCRIPCION = 'SUSCRIPCION', 'Suscripción'
	PAGO_USO = 'PAGO_USO', 'Pago por uso'


class Sede(models.Model):
	nombre = models.CharField(max_length=150)
	direccion = models.CharField(max_length=250)
	ciudad = models.CharField(max_length=120)
	horario_apertura = models.TimeField()
	horario_cierre = models.TimeField()
	estado = models.CharField(max_length=20, choices=EstadoBase.choices, default=EstadoBase.ACTIVO)

	def __str__(self) -> str:
		return self.nombre


class Espacio(models.Model):
	sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='espacios')
	nombre = models.CharField(max_length=150)
	tipo = models.CharField(max_length=30, choices=TipoEspacio.choices, default=TipoEspacio.COWORKING)
	capacidad = models.PositiveIntegerField()
	precio_por_hora = models.DecimalField(max_digits=10, decimal_places=2)
	descripcion = models.TextField(blank=True)
	estado = models.CharField(max_length=20, choices=EstadoEspacio.choices, default=EstadoEspacio.DISPONIBLE)
	es_premium = models.BooleanField(default=False)

	def __str__(self) -> str:
		return f'{self.nombre} - {self.sede.nombre}'


class Reserva(models.Model):
	usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservas')
	espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name='reservas')
	fecha_creacion = models.DateTimeField(auto_now_add=True)
	fecha_inicio = models.DateTimeField()
	fecha_fin = models.DateTimeField()
	estado = models.CharField(max_length=20, choices=EstadoReserva.choices, default=EstadoReserva.PENDIENTE)
	costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	modalidad_pago = models.CharField(max_length=20, choices=ModalidadPago.choices, default=ModalidadPago.PAGO_USO)

	def __str__(self) -> str:
		return f'Reserva #{self.pk or "nuevo"}'
