from django.db import models

from reservas.models import Reserva


class EstadoResena(models.TextChoices):
	BORRADOR = 'BORRADOR', 'Borrador'
	PUBLICADA = 'PUBLICADA', 'Publicada'
	ELIMINADA = 'ELIMINADA', 'Eliminada'


class Resena(models.Model):
	reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='resena')
	calificacion = models.PositiveSmallIntegerField()
	comentario = models.TextField(blank=True)
	fecha_publicacion = models.DateTimeField(auto_now_add=True)
	estado = models.CharField(max_length=20, choices=EstadoResena.choices, default=EstadoResena.BORRADOR)

	def publicar(self) -> None:
		self.estado = EstadoResena.PUBLICADA
		self.save(update_fields=['estado'])

	def editar(self, comentario: str, calificacion: int) -> None:
		self.comentario = comentario
		self.calificacion = calificacion
		self.save(update_fields=['comentario', 'calificacion'])

	def eliminar(self) -> None:
		self.estado = EstadoResena.ELIMINADA
		self.save(update_fields=['estado'])

	def validar_calificacion(self) -> bool:
		return 1 <= self.calificacion <= 5

	def __str__(self) -> str:
		return f'Reseña de reserva {self.reserva_id}'
