from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from reservas.models import Espacio
from reservas.services import ReservationService


class CreateReservationView(LoginRequiredMixin, View):
	service_class = ReservationService

	def post(self, request):
		data = request.POST
		reserva = self.service_class().create_reservation(usuario=request.user, espacio=get_object_or_404(Espacio, pk=data['espacio_id']), fecha_inicio=data['fecha_inicio'], fecha_fin=data['fecha_fin'], modalidad_pago=data['modalidad_pago'])
		return JsonResponse({'id': reserva.id, 'estado': reserva.estado}, status=201)
