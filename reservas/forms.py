from django import forms

from reservas.models import Espacio, ModalidadPago


class CreateReservationForm(forms.Form):
    espacio = forms.ModelChoiceField(queryset=Espacio.objects.select_related('sede').all())
    fecha_inicio = forms.DateTimeField()
    fecha_fin = forms.DateTimeField()
    modalidad_pago = forms.ChoiceField(choices=ModalidadPago.choices, initial=ModalidadPago.PAGO_USO)