from django.contrib.auth.models import AbstractUser
from django.db import models


class EstadoUsuario(models.TextChoices):
	ACTIVO = 'ACTIVO', 'Activo'
	SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'
	INACTIVO = 'INACTIVO', 'Inactivo'


class Usuario(AbstractUser):
	username = None

	nombre = models.CharField(max_length=150)
	email = models.EmailField(unique=True)
	telefono = models.CharField(max_length=20, blank=True)
	fecha_registro = models.DateTimeField(auto_now_add=True)
	estado = models.CharField(
		max_length=20,
		choices=EstadoUsuario.choices,
		default=EstadoUsuario.ACTIVO,
	)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['nombre']

	def __str__(self) -> str:
		return self.nombre or self.email
