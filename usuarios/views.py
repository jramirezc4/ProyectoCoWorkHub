from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from usuarios.forms import RegisterForm


@login_required
def profile(request):
    reservations = request.user.reservas.select_related('espacio__sede').order_by('-fecha_creacion')[:5]
    return render(request, 'usuarios/profile.html', {
        'user': request.user,
        'reservations': reservations,
    })


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Cuenta creada correctamente.')
        return redirect('dashboard')

    return render(request, 'usuarios/register.html', {'form': form})
