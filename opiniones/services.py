from django.core.exceptions import ValidationError

from opiniones.models import EstadoResena, Resena
from reservas.models import EstadoReserva


class ReviewService:
    def create(self, *, reserva, calificacion: int, comentario: str) -> Resena:
        if reserva.estado != EstadoReserva.COMPLETADA:
            raise ValidationError('Solo puedes reseñar una reserva completada.')
        if Resena.objects.filter(reserva=reserva).exists():
            raise ValidationError('Esta reserva ya tiene una reseña.')
        review = Resena(
            reserva=reserva,
            calificacion=calificacion,
            comentario=comentario,
            estado=EstadoResena.PUBLICADA,
        )
        review.full_clean()
        review.save()
        return review

    def publish(self, review: Resena) -> Resena:
        review.estado = EstadoResena.PUBLICADA
        review.save(update_fields=['estado'])
        return review

    def edit(self, review: Resena, *, comentario: str, calificacion: int) -> Resena:
        review.comentario = comentario
        review.calificacion = calificacion
        review.full_clean()
        review.save(update_fields=['comentario', 'calificacion'])
        return review

    def delete(self, review: Resena) -> Resena:
        review.estado = EstadoResena.ELIMINADA
        review.save(update_fields=['estado'])
        return review