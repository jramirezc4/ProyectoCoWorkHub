from django.contrib import admin

from .models import Factura, Pago, Plan, Suscripcion


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'precio_mensual', 'limite_horas', 'estado')
	search_fields = ('nombre',)


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
	list_display = ('usuario', 'plan', 'fecha_inicio', 'fecha_fin', 'estado')
	list_filter = ('estado', 'plan')
	search_fields = ('usuario__email', 'usuario__nombre')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
	list_display = ('fecha_pago', 'monto', 'metodo_pago', 'estado', 'tipo_pago')
	list_filter = ('estado', 'metodo_pago', 'tipo_pago')
	readonly_fields = ('fecha_pago', 'referencia_transaccion')


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
	list_display = ('numero_factura', 'fecha_emision', 'total')
	search_fields = ('numero_factura',)
	readonly_fields = ('numero_factura', 'fecha_emision', 'subtotal', 'impuestos', 'total')
