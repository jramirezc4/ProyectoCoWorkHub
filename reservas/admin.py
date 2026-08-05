from django.contrib import admin

from .models import Espacio, Reserva, Sede


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'ciudad', 'estado')
	search_fields = ('nombre', 'ciudad', 'direccion')


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'sede', 'tipo', 'capacidad', 'estado', 'es_premium')
	list_filter = ('tipo', 'estado', 'es_premium', 'sede')
	search_fields = ('nombre', 'sede__nombre')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
	list_display = ('usuario', 'espacio', 'fecha_inicio', 'fecha_fin', 'estado', 'modalidad_pago')
	list_filter = ('estado', 'modalidad_pago', 'espacio__sede')
	search_fields = ('usuario__email', 'usuario__nombre', 'espacio__nombre')
