from rest_framework import serializers

from reservas.models import Espacio, ModalidadPago, Reserva


class ReservationCreateSerializer(serializers.Serializer):
    espacio_id = serializers.PrimaryKeyRelatedField(
        source='espacio', queryset=Espacio.objects.select_related('sede').all()
    )
    fecha_inicio = serializers.DateTimeField()
    fecha_fin = serializers.DateTimeField()
    modalidad_pago = serializers.ChoiceField(choices=ModalidadPago.choices)


class ReservationSerializer(serializers.ModelSerializer):
    espacio = serializers.StringRelatedField()
    usuario = serializers.StringRelatedField()

    class Meta:
        model = Reserva
        fields = (
            'id', 'usuario', 'espacio', 'fecha_creacion', 'fecha_inicio',
            'fecha_fin', 'estado', 'costo_total', 'modalidad_pago',
        )
        read_only_fields = fields