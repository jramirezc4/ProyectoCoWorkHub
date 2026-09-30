from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import MetodoPago, Plan
from .services import PaymentService


@login_required
def subscription_plans(request):
	plans = Plan.objects.filter(estado='ACTIVO').order_by('precio_mensual')
	if request.method == 'POST':
		plan = get_object_or_404(plans, pk=request.POST.get('plan_id'))
		metodo_pago = request.POST.get('metodo_pago')
		valid_methods = {value for value, _label in MetodoPago.choices if value != 'OTRO'}
		if metodo_pago not in valid_methods:
			return render(request, 'finanzas/subscription_plans.html', {
				'plans': plans,
				'error': 'Selecciona un método de pago válido.',
				'payment_methods': MetodoPago.choices,
			})

		PaymentService.create_subscription_payment(
			usuario=request.user,
			plan=plan,
			metodo_pago=metodo_pago,
		)
		messages.success(request, f'Suscripción a {plan.nombre} activada correctamente.')
		return redirect('dashboard')

	return render(request, 'finanzas/subscription_plans.html', {
		'plans': plans,
		'payment_methods': [choice for choice in MetodoPago.choices if choice[0] != 'OTRO'],
	})
