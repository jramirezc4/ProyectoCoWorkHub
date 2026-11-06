from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
	model = Usuario
	ordering = ('email',)
	list_display = ('email', 'nombre', 'telefono', 'rol', 'estado', 'is_staff')
	list_filter = ('rol', 'estado', 'is_staff', 'is_active')
	search_fields = ('email', 'nombre', 'telefono')

	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		('Información personal', {'fields': ('nombre', 'telefono', 'estado', 'rol')}),
		('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		('Fechas importantes', {'fields': ('last_login', 'date_joined', 'fecha_registro')}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'nombre', 'telefono', 'estado', 'rol', 'password1', 'password2', 'is_staff', 'is_active'),
		}),
	)
