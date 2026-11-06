from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from reservas.models import EstadoReserva, Reserva

from .forms import ReviewForm
from .models import Resena
from .services import ReviewService


class CreateReviewView(LoginRequiredMixin, View):
    template_name = 'opiniones/review_form.html'

    def get_reservation(self, request, reservation_id):
        return get_object_or_404(
            Reserva.objects.select_related('espacio__sede'),
            pk=reservation_id,
            usuario=request.user,
            estado=EstadoReserva.COMPLETADA,
        )

    def get(self, request, reservation_id):
        reservation = self.get_reservation(request, reservation_id)
        if Resena.objects.filter(reserva=reservation).exists():
            return redirect('review-edit', reservation_id=reservation.id)
        return render(request, self.template_name, {
            'form': ReviewForm(),
            'reservation': reservation,
        })

    def post(self, request, reservation_id):
        reservation = self.get_reservation(request, reservation_id)
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                ReviewService().create(
                    reserva=reservation,
                    calificacion=form.cleaned_data['calificacion'],
                    comentario=form.cleaned_data['comentario'],
                )
            except ValidationError as error:
                form.add_error(None, error.messages)
            else:
                messages.success(request, 'Reseña publicada correctamente.')
                return redirect('dashboard')
        return render(request, self.template_name, {
            'form': form,
            'reservation': reservation,
        })


class EditReviewView(LoginRequiredMixin, View):
    template_name = 'opiniones/review_form.html'

    def get_review(self, request, reservation_id):
        return get_object_or_404(
            Resena.objects.select_related('reserva__espacio'),
            reserva__pk=reservation_id,
            reserva__usuario=request.user,
        )

    def get(self, request, reservation_id):
        review = self.get_review(request, reservation_id)
        return render(request, self.template_name, {
            'form': ReviewForm(instance=review),
            'reservation': review.reserva,
            'editing': True,
        })

    def post(self, request, reservation_id):
        review = self.get_review(request, reservation_id)
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            ReviewService().edit(
                review,
                comentario=form.cleaned_data['comentario'],
                calificacion=form.cleaned_data['calificacion'],
            )
            messages.success(request, 'Reseña actualizada correctamente.')
            return redirect('dashboard')
        return render(request, self.template_name, {
            'form': form,
            'reservation': review.reserva,
            'editing': True,
        })
