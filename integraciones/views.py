from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from zoneinfo import ZoneInfo

from .adapters import weather_provider
from reservas.models import EstadoReserva, Espacio, Sede, Reserva


@login_required
def available_spaces(request):
    now = timezone.now()
    weather = weather_provider()
    active_reservations = Reserva.objects.filter(
        estado__in=(EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA),
        fecha_inicio__lt=now,
        fecha_fin__gt=now,
    ).values_list('espacio_id', flat=True)
    venues = []
    for venue in Sede.objects.filter(estado='ACTIVO').prefetch_related('espacios'):
        try:
            venue_weather = weather.current_for(venue.ciudad)
            weather_error = None
        except RuntimeError as error:
            venue_weather = None
            weather_error = str(error)
        venues.append({
            'sede': venue,
            'hora': timezone.localtime(now, ZoneInfo('America/Bogota')),
            'weather': venue_weather,
            'weather_error': weather_error,
            'spaces': [
                space for space in venue.espacios.all()
                if space.estado == 'DISPONIBLE'
            ],
            'occupied_ids': set(active_reservations),
        })
    return render(request, 'integraciones/demo.html', {'venues': venues})
