from django.contrib import admin

from .models import Espacio, Reserva, Sede


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
	list_display = (
		'nombre',
		'ciudad',
		'direccion',
		'horario_apertura',
		'horario_cierre',
		'estado',
	)
	list_filter = ('estado', 'ciudad')
	search_fields = ('nombre', 'ciudad', 'direccion')
	ordering = ('ciudad', 'nombre')
	fieldsets = (
		('Información de la sede', {
			'fields': ('nombre', 'ciudad', 'direccion', 'estado'),
		}),
		('Horario de atención', {
			'fields': ('horario_apertura', 'horario_cierre'),
		}),
	)


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'sede', 'tipo', 'capacidad', 'estado', 'es_premium')
	list_filter = ('tipo', 'estado', 'es_premium', 'sede')
	search_fields = ('nombre', 'sede__nombre')
	list_select_related = ('sede',)
	ordering = ('sede__nombre', 'nombre')
	fieldsets = (
		('Información del espacio', {
			'fields': ('sede', 'nombre', 'tipo', 'descripcion'),
		}),
		('Capacidad y disponibilidad', {
			'fields': ('capacidad', 'precio_por_hora', 'estado', 'es_premium'),
		}),
	)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
	list_display = ('usuario', 'espacio', 'fecha_inicio', 'fecha_fin', 'estado', 'modalidad_pago')
	list_filter = ('estado', 'modalidad_pago', 'espacio__sede')
	search_fields = ('usuario__email', 'usuario__nombre', 'espacio__nombre')
	actions = ('mark_as_completed', 'mark_as_cancelled')

	@admin.action(description='Marcar reservas como completadas')
	def mark_as_completed(self, request, queryset):
		queryset.update(estado='COMPLETADA')

	@admin.action(description='Cancelar reservas seleccionadas')
	def mark_as_cancelled(self, request, queryset):
		queryset.update(estado='CANCELADA')
