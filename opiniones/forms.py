from django import forms

from .models import Resena


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ('calificacion', 'comentario')
        labels = {
            'calificacion': 'Calificación (1 a 5)',
            'comentario': 'Comentario',
        }
        widgets = {
            'calificacion': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comentario': forms.Textarea(attrs={'rows': 4}),
        }
