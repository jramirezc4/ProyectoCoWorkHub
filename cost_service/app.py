from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Flask, jsonify, request


app = Flask(__name__)


def error_response(message, status_code):
    return jsonify({'error': {'code': status_code, 'message': message}}), status_code


def parse_datetime(value, field_name):
    if not isinstance(value, str):
        raise ValueError(f'{field_name} debe ser una fecha ISO-8601.')
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as error:
        raise ValueError(f'{field_name} debe ser una fecha ISO-8601 válida.') from error


@app.get('/health/')
def health():
    return jsonify({'status': 'ok', 'service': 'cost-service'})


@app.get('/api/v2/servicio-aliado/')
def allied_spaces():
    return jsonify({
        'provider': 'ally-demo',
        'spaces': [
            {'name': 'Sala Norte Aliada', 'city': 'Bogota'},
            {'name': 'Cowork Lab Aliado', 'city': 'Medellin'},
        ],
    })


@app.post('/api/v2/cotizaciones/')
def calculate_quote():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response('El cuerpo debe ser un objeto JSON.', 400)

    try:
        hourly_rate = Decimal(str(payload['precio_por_hora']))
        start = parse_datetime(payload['fecha_inicio'], 'fecha_inicio')
        end = parse_datetime(payload['fecha_fin'], 'fecha_fin')
        if hourly_rate < 0:
            raise ValueError('precio_por_hora no puede ser negativo.')
        if end <= start:
            raise ValueError('fecha_fin debe ser posterior a fecha_inicio.')
    except (KeyError, InvalidOperation, TypeError, ValueError) as error:
        return error_response(str(error), 400)

    duration_hours = Decimal(str((end - start).total_seconds() / 3600))
    billable_hours = max(Decimal('1'), duration_hours.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    total = (billable_hours * hourly_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return jsonify({
        'costo_total': str(total),
        'horas_cobradas': str(billable_hours),
        'moneda': 'COP',
    })


@app.errorhandler(500)
def internal_error(error):
    app.logger.exception('Error inesperado en cost-service', exc_info=error)
    return error_response('Error interno al calcular la cotización.', 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
