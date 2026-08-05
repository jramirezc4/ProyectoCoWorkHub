from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
	model = Usuario
	ordering = ('email',)
	list_display = ('email', 'nombre', 'telefono', 'estado', 'is_staff')
	search_fields = ('email', 'nombre', 'telefono')

	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		('Información personal', {'fields': ('nombre', 'telefono', 'estado')}),
		('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		('Fechas importantes', {'fields': ('last_login', 'date_joined', 'fecha_registro')}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'nombre', 'telefono', 'estado', 'password1', 'password2', 'is_staff', 'is_active'),
		}),
	)
