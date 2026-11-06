from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import MetodoPago, Plan
from .services import PaymentService, SubscriptionService


@login_required
def subscription_plans(request):
	SubscriptionService.expire_due_subscriptions()
	plans = Plan.objects.filter(estado='ACTIVO').order_by('precio_mensual')
	active_subscription = SubscriptionService.active_for(request.user)
	if request.method == 'POST':
		if active_subscription:
			return render(request, 'finanzas/subscription_plans.html', {
				'plans': plans,
				'active_subscription': active_subscription,
				'error': 'Ya tienes una suscripción activa. Cancélala antes de cambiar de plan.',
				'payment_methods': [choice for choice in MetodoPago.choices if choice[0] != 'OTRO'],
			})
		plan = get_object_or_404(plans, pk=request.POST.get('plan_id'))
		metodo_pago = request.POST.get('metodo_pago')
		valid_methods = {value for value, _label in MetodoPago.choices if value != 'OTRO'}
		if metodo_pago not in valid_methods:
			return render(request, 'finanzas/subscription_plans.html', {
				'plans': plans,
				'error': 'Selecciona un método de pago válido.',
				'payment_methods': MetodoPago.choices,
			})

		try:
			PaymentService.create_subscription_payment(
				usuario=request.user,
				plan=plan,
				metodo_pago=metodo_pago,
				numero_tarjeta=request.POST.get('numero_tarjeta'),
				vencimiento=request.POST.get('vencimiento'),
				cvv=request.POST.get('cvv'),
			)
		except ValueError as error:
			return render(request, 'finanzas/subscription_plans.html', {
				'plans': plans,
				'active_subscription': active_subscription,
				'error': str(error),
				'payment_methods': [choice for choice in MetodoPago.choices if choice[0] != 'OTRO'],
			})
		messages.success(request, f'Suscripción a {plan.nombre} activada correctamente.')
		messages.success(request, 'Factura simulada generada correctamente.')
		return redirect('dashboard')

	return render(request, 'finanzas/subscription_plans.html', {
		'plans': plans,
		'active_subscription': active_subscription,
		'payment_methods': [choice for choice in MetodoPago.choices if choice[0] != 'OTRO'],
	})


@login_required
def cancel_subscription(request, pk):
	if request.method != 'POST':
		return redirect('subscription_plans')
	subscription = get_object_or_404(
		request.user.suscripciones.select_related('plan'),
		pk=pk,
	)
	try:
		SubscriptionService.cancel(subscription)
	except ValueError as error:
		messages.error(request, str(error))
	else:
		messages.success(request, 'Suscripción cancelada correctamente.')
	return redirect('subscription_plans')
