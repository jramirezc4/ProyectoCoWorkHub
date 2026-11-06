from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from reservas.models import Espacio, EstadoReserva, Reserva, Sede
from finanzas.services import SubscriptionService
from finanzas.models import Pago
from core.models import Notification


ACTIVE_RESERVATION_STATES = (
    EstadoReserva.PENDIENTE,
    EstadoReserva.CONFIRMADA,
)


def current_occupancy():
    total_spaces = Espacio.objects.filter(
        sede__estado='ACTIVO',
    ).count()
    if not total_spaces:
        return '0%'

    now = timezone.now()
    occupied_spaces = Reserva.objects.filter(
        estado__in=ACTIVE_RESERVATION_STATES,
        fecha_inicio__lt=now,
        fecha_fin__gt=now,
        espacio__sede__estado='ACTIVO',
    ).values('espacio_id').distinct().count()
    percentage = round(occupied_spaces * 100 / total_spaces)
    return f'{percentage}%'


def home(request):
    stats = {
        'espacios': Espacio.objects.count(),
        'sedes': Sede.objects.filter(estado='ACTIVO').count(),
        'ocupacion': current_occupancy(),
    }
    return render(request, 'core/home.html', {'stats': stats})


@login_required
def dashboard(request):
    active_subscription = SubscriptionService.active_for(request.user)
    latest_payment = Pago.objects.filter(
        suscripcion__usuario=request.user,
    ).select_related('factura').order_by('-fecha_pago').first()
    if latest_payment is None:
        latest_payment = Pago.objects.filter(
            reserva__usuario=request.user,
        ).select_related('factura').order_by('-fecha_pago').first()
    reservation_queryset = Reserva.objects.select_related('espacio__sede', 'usuario').order_by('-fecha_creacion')
    if not request.user.has_full_access():
        reservation_queryset = reservation_queryset.filter(usuario=request.user)
    now = timezone.now()
    upcoming_reservations = reservation_queryset.filter(
        fecha_inicio__gt=now,
        estado__in=ACTIVE_RESERVATION_STATES,
    )
    reservations = reservation_queryset[:5]
    stats = {
        'reservas': reservation_queryset.count(),
        'proximas': upcoming_reservations.count(),
        'ocupacion': current_occupancy(),
    }
    return render(request, 'core/dashboard.html', {
        'stats': stats,
        'reservations': reservations,
        'user': request.user,
        'active_subscription': active_subscription,
        'subscription_usage': (
            SubscriptionService.usage(active_subscription)
            if active_subscription else None
        ),
        'latest_payment': latest_payment,
        'notifications': Notification.objects.filter(
            usuario=request.user, leida=False
        )[:5],
    })
