from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reservas.models import Reserva


class EstadoResena(models.TextChoices):
	BORRADOR = 'BORRADOR', 'Borrador'
	PUBLICADA = 'PUBLICADA', 'Publicada'
	ELIMINADA = 'ELIMINADA', 'Eliminada'


class Resena(models.Model):
	reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='resena')
	calificacion = models.PositiveSmallIntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(5)]
	)
	comentario = models.TextField(blank=True)
	fecha_publicacion = models.DateTimeField(auto_now_add=True)
	estado = models.CharField(max_length=20, choices=EstadoResena.choices, default=EstadoResena.BORRADOR)

	def __str__(self) -> str:
		return f'Reseña de reserva {self.reserva_id}'
