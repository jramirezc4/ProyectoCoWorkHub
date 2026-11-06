from datetime import datetime, time, timedelta

from django import forms
from django.utils import timezone

from reservas.models import Espacio, ModalidadPago


class CreateReservationForm(forms.Form):
    espacio = forms.ModelChoiceField(
        queryset=Espacio.objects.select_related('sede').filter(estado='DISPONIBLE'),
        label='Sede y sala',
        empty_label='Selecciona una sede y sala',
    )
    fecha_inicio = forms.DateTimeField(
        label='Inicio de la reserva',
        help_text='Elige la fecha y hora de inicio.',
        required=False,
        widget=forms.HiddenInput(),
    )
    fecha_fin = forms.DateTimeField(
        label='Fin de la reserva',
        help_text='Elige la fecha y hora de finalización.',
        required=False,
        widget=forms.HiddenInput(),
    )
    fecha_inicio_dia = forms.DateField(
        label='Día de inicio',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    hora_inicio = forms.ChoiceField(
        label='Hora de inicio',
        required=False,
        choices=[(f'{hour:02d}:00', f'{hour:02d}:00') for hour in range(24)],
    )
    fecha_fin_dia = forms.DateField(
        label='Día de finalización',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    hora_fin = forms.ChoiceField(
        label='Hora de finalización',
        required=False,
        choices=[(f'{hour:02d}:00', f'{hour:02d}:00') for hour in range(24)],
    )
    modalidad_pago = forms.ChoiceField(
        choices=ModalidadPago.choices,
        initial=ModalidadPago.PAGO_USO,
        label='Modalidad de pago',
        help_text='Pago por uso cobra esta reserva. Suscripción requiere un plan activo.',
    )
    metodo_pago = forms.ChoiceField(
        choices=[
            ('TARJETA', 'Tarjeta'),
            ('PSE', 'PSE'),
            ('TRANSFERENCIA', 'Transferencia bancaria'),
        ],
        initial='TARJETA',
        label='Método de pago',
    )
    numero_tarjeta = forms.CharField(
        required=False,
        label='Tarjeta demo',
        help_text='Usa 4242 4242 4242 4242 para simular un pago aprobado.',
    )
    vencimiento = forms.CharField(
        required=False,
        label='Vencimiento',
        help_text='Formato MM/AA. Tarjeta demo: 12/30.',
        widget=forms.TextInput(attrs={'placeholder': '12/30', 'maxlength': '5'}),
    )
    cvv = forms.CharField(
        required=False,
        label='CVV',
        help_text='Código de 3 dígitos. Tarjeta demo: 123.',
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'maxlength': '3'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('fecha_inicio')
        end = cleaned_data.get('fecha_fin')
        start_day = cleaned_data.get('fecha_inicio_dia')
        end_day = cleaned_data.get('fecha_fin_dia')
        start_hour = cleaned_data.get('hora_inicio')
        end_hour = cleaned_data.get('hora_fin')
        if start_day or end_day or start_hour or end_hour:
            if not all((start_day, end_day, start_hour, end_hour)):
                raise forms.ValidationError('Selecciona el día y la hora de inicio y finalización.')
            start = timezone.make_aware(
                datetime.combine(start_day, time.fromisoformat(start_hour))
            )
            end = timezone.make_aware(
                datetime.combine(end_day, time.fromisoformat(end_hour))
            )
            cleaned_data['fecha_inicio'] = start
            cleaned_data['fecha_fin'] = end
        elif not (start and end):
            raise forms.ValidationError('Selecciona el día y horario de la reserva.')
        if start and end:
            if start.minute or start.second or start.microsecond or end.minute or end.second or end.microsecond:
                raise forms.ValidationError('Selecciona horas exactas, por ejemplo 09:00 o 10:00.')
            if end - start < timedelta(hours=1) or (end - start).total_seconds() % 3600:
                raise forms.ValidationError('La reserva debe durar una o más horas completas.')
        return cleaned_data