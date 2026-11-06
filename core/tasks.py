import logging

from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task
def send_reservation_confirmation(reservation_id):
    from reservas.models import Reserva
    from core.models import Notification

    reservation = Reserva.objects.select_related('usuario').get(pk=reservation_id)
    notification = Notification.objects.create(
        usuario=reservation.usuario,
        tipo='RESERVA_CONFIRMADA',
        mensaje=f'Reserva #{reservation.id} confirmada correctamente.',
    )
    logger.info('reservation_confirmation_queued reservation_id=%s', reservation_id)
    return {'reservation_id': reservation_id, 'notification_id': notification.id}
