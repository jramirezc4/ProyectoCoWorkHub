import os
from decimal import Decimal, ROUND_HALF_UP


class ReservationCostCalculator:
    def calculate(self, espacio, fecha_inicio, fecha_fin):
        raise NotImplementedError


class MockReservationCostCalculator(ReservationCostCalculator):
    def calculate(self, espacio, fecha_inicio, fecha_fin):
        return Decimal('0.00')


class RealReservationCostCalculator(ReservationCostCalculator):
    def calculate(self, espacio, fecha_inicio, fecha_fin):
        duration_hours = Decimal(str((fecha_fin - fecha_inicio).total_seconds() / 3600))
        hours = max(Decimal('1'), duration_hours.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        return (hours * espacio.precio_por_hora).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class ReservationCostCalculatorFactory:
    def create(self):
        mode = os.getenv('COWORKHUB_COST_CALCULATOR', 'REAL').upper()
        if mode == 'MOCK':
            return MockReservationCostCalculator()
        return RealReservationCostCalculator()