from django.contrib import admin

from .models import Resena


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
	list_display = ('reserva', 'calificacion', 'estado', 'fecha_publicacion')
	list_filter = ('estado', 'calificacion')
	search_fields = ('reserva__usuario__email', 'reserva__espacio__nombre')
