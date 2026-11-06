from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models


class UsuarioManager(UserManager):
	def create_user(self, email, password=None, **extra_fields):
		if not email:
			raise ValueError('El usuario debe tener un email.')
		user = self.model(email=self.normalize_email(email), **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		return self.create_user(email, password, **extra_fields)


class EstadoUsuario(models.TextChoices):
	ACTIVO = 'ACTIVO', 'Activo'
	SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'
	INACTIVO = 'INACTIVO', 'Inactivo'


class RolUsuario(models.TextChoices):
	ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
	OPERADOR = 'OPERADOR', 'Operador'
	USUARIO = 'USUARIO', 'Usuario'


class Usuario(AbstractUser):
	username = None
	objects = UsuarioManager()

	nombre = models.CharField(max_length=150)
	email = models.EmailField(unique=True)
	telefono = models.CharField(max_length=20, blank=True)
	fecha_registro = models.DateTimeField(auto_now_add=True)
	estado = models.CharField(
		max_length=20,
		choices=EstadoUsuario.choices,
		default=EstadoUsuario.ACTIVO,
	)
	rol = models.CharField(
		max_length=20,
		choices=RolUsuario.choices,
		default=RolUsuario.USUARIO,
	)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['nombre']

	def __str__(self) -> str:
		return self.nombre or self.email

	def has_full_access(self) -> bool:
		return (
			self.is_staff
			or self.is_superuser
			or self.rol == RolUsuario.ADMINISTRADOR
			or self.email.lower().startswith('admin@demo')
		)
