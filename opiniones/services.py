from opiniones.models import EstadoResena, Resena


class ReviewService:
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