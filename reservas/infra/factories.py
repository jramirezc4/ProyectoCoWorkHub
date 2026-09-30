import os
from decimal import Decimal, ROUND_HALF_UP
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import json


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


class RemoteReservationCostCalculator(ReservationCostCalculator):
    def __init__(self, service_url):
        self.service_url = service_url.rstrip('/') + '/'

    def calculate(self, espacio, fecha_inicio, fecha_fin):
        payload = json.dumps({
            'precio_por_hora': str(espacio.precio_por_hora),
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat(),
        }).encode('utf-8')
        request = Request(
            self.service_url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            with urlopen(request, timeout=3) as response:
                result = json.loads(response.read().decode('utf-8'))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError('El servicio de costos no está disponible.') from error
        return Decimal(result['costo_total'])


class ReservationCostCalculatorFactory:
    def create(self):
        service_url = os.getenv('COWORKHUB_COST_SERVICE_URL')
        if service_url:
            return RemoteReservationCostCalculator(service_url)
        mode = os.getenv('COWORKHUB_COST_CALCULATOR', 'REAL').upper()
        if mode == 'MOCK':
            return MockReservationCostCalculator()
        return RealReservationCostCalculator()