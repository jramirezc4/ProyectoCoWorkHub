from django import forms

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
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    fecha_fin = forms.DateTimeField(
        label='Fin de la reserva',
        help_text='Elige la fecha y hora de finalización.',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
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