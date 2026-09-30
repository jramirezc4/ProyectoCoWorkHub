from django.db import migrations


def create_rooms_for_existing_venues(apps, schema_editor):
    Sede = apps.get_model('reservas', 'Sede')
    Espacio = apps.get_model('reservas', 'Espacio')
    for sede in Sede.objects.all():
        for room_number in (1, 2):
            Espacio.objects.get_or_create(
                sede=sede,
                nombre=f'Sala Reuniones {room_number}',
                defaults={
                    'tipo': 'SALA_REUNION',
                    'capacidad': 8 if room_number == 1 else 12,
                    'precio_por_hora': '45000.00' if room_number == 1 else '60000.00',
                    'descripcion': f'Sala equipada para reuniones en {sede.nombre}.',
                    'estado': 'DISPONIBLE',
                    'es_premium': room_number == 2,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ('reservas', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(create_rooms_for_existing_venues, migrations.RunPython.noop),
    ]