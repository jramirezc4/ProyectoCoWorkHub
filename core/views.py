from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from reservas.models import Reserva


def home(request):
    stats = {
        'espacios': 18,
        'sedes': 5,
        'ocupacion': '96%',
    }
    return render(request, 'core/home.html', {'stats': stats})


@login_required
def dashboard(request):
    reservation_queryset = Reserva.objects.select_related('espacio__sede', 'usuario').order_by('-fecha_creacion')
    if not request.user.has_full_access():
        reservation_queryset = reservation_queryset.filter(usuario=request.user)
    reservations = reservation_queryset[:5]
    stats = {
        'reservas': reservations.count(),
        'proximas': 3,
        'ocupacion': '94%',
    }
    return render(request, 'core/dashboard.html', {
        'stats': stats,
        'reservations': reservations,
        'user': request.user,
    })
