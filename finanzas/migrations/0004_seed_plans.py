from decimal import Decimal

from django.db import migrations, models


def create_default_plans(apps, schema_editor):
    Plan = apps.get_model('finanzas', 'Plan')
    plans = [
        {
            'nombre': 'Flex',
            'precio_mensual': Decimal('149000.00'),
            'limite_horas': 20,
            'maximo_reservas_activas': 2,
            'acceso_premium': False,
            'prioridad_reserva': False,
        },
        {
            'nombre': 'Business',
            'precio_mensual': Decimal('299000.00'),
            'limite_horas': 50,
            'maximo_reservas_activas': 5,
            'acceso_premium': True,
            'prioridad_reserva': True,
        },
    ]
    for plan_data in plans:
        Plan.objects.get_or_create(nombre=plan_data['nombre'], defaults=plan_data)


class Migration(migrations.Migration):
    dependencies = [
        ('finanzas', '0003_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_plans, migrations.RunPython.noop),
    ]