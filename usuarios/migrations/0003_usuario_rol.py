from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0002_alter_usuario_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='rol',
            field=models.CharField(
                choices=[
                    ('ADMINISTRADOR', 'Administrador'),
                    ('OPERADOR', 'Operador'),
                    ('USUARIO', 'Usuario'),
                ],
                default='USUARIO',
                max_length=20,
            ),
        ),
    ]
