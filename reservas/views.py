from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from reservas.forms import CreateReservationForm
from finanzas.services import PaymentService
from reservas.models import Espacio, ModalidadPago
from reservas.services import ReservationService


class CreateReservationView(LoginRequiredMixin, View):
	service_class = ReservationService
	template_name = 'reservas/create_reservation.html'

	def get(self, request):
		form = CreateReservationForm()
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = CreateReservationForm(request.POST)
		if not form.is_valid():
			return render(request, self.template_name, {'form': form, 'error': 'Revisa los datos de la reserva.'})

		try:
			reserva = self.service_class().create_reservation(
				usuario=request.user,
				espacio=form.cleaned_data['espacio'],
				fecha_inicio=form.cleaned_data['fecha_inicio'],
				fecha_fin=form.cleaned_data['fecha_fin'],
				modalidad_pago=form.cleaned_data['modalidad_pago'],
			)
			if form.cleaned_data['modalidad_pago'] == ModalidadPago.PAGO_USO and not request.user.has_full_access():
				PaymentService.create_reservation_payment(
					reserva,
					metodo_pago=form.cleaned_data['metodo_pago'],
				)
		except Exception as exc:  # pragma: no cover - fallback UI handling
			return render(request, self.template_name, {'form': form, 'error': str(exc)})

		return render(
			request,
			self.template_name,
			{'form': CreateReservationForm(), 'success': f'Reserva creada correctamente #{reserva.id}.', 'reservation': reserva},
		)

	def api_post(self, request):
		data = request.POST
		reserva = self.service_class().create_reservation(usuario=request.user, espacio=get_object_or_404(Espacio, pk=data['espacio_id']), fecha_inicio=data['fecha_inicio'], fecha_fin=data['fecha_fin'], modalidad_pago=data['modalidad_pago'])
		return JsonResponse({'id': reserva.id, 'estado': reserva.estado}, status=201)
