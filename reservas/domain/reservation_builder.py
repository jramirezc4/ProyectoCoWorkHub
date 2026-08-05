from django.core.exceptions import ValidationError

from reservas.models import EstadoReserva, Reserva


class ReservationBuilder:
    def __init__(self):
        self._usuario = None
        self._espacio = None
        self._fecha_inicio = None
        self._fecha_fin = None
        self._modalidad_pago = None
        self._costo_total = None

    def with_usuario(self, usuario):
        self._usuario = usuario
        return self

    def with_espacio(self, espacio):
        self._espacio = espacio
        return self

    def with_fechas(self, fecha_inicio, fecha_fin):
        self._fecha_inicio = fecha_inicio
        self._fecha_fin = fecha_fin
        return self

    def with_modalidad_pago(self, modalidad_pago):
        self._modalidad_pago = modalidad_pago
        return self

    def with_costo_total(self, costo_total):
        self._costo_total = costo_total
        return self

    def build(self):
        self._validate_required_fields()
        self._validate_dates()
        reserva = Reserva(
            usuario=self._usuario,
            espacio=self._espacio,
            fecha_inicio=self._fecha_inicio,
            fecha_fin=self._fecha_fin,
            modalidad_pago=self._modalidad_pago,
            costo_total=self._costo_total,
            estado=EstadoReserva.PENDIENTE,
        )
        reserva.full_clean()
        return reserva

    def _validate_required_fields(self):
        missing_fields = [
            name for name, value in {
                'usuario': self._usuario,
                'espacio': self._espacio,
                'fecha_inicio': self._fecha_inicio,
                'fecha_fin': self._fecha_fin,
                'modalidad_pago': self._modalidad_pago,
                'costo_total': self._costo_total,
            }.items() if value is None
        ]
        if missing_fields:
            raise ValidationError(f'Campos faltantes para crear la reserva: {", ".join(missing_fields)}')

    def _validate_dates(self):
        if self._fecha_inicio >= self._fecha_fin:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin.')