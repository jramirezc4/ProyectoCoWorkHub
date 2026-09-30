import unittest

from .app import app


class CostServiceTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_calculates_quote(self):
        response = self.client.post('/api/v2/cotizaciones/', json={
            'precio_por_hora': '25.00',
            'fecha_inicio': '2026-09-01T09:00:00+00:00',
            'fecha_fin': '2026-09-01T11:00:00+00:00',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['costo_total'], '50.00')

    def test_rejects_invalid_range(self):
        response = self.client.post('/api/v2/cotizaciones/', json={
            'precio_por_hora': '25.00',
            'fecha_inicio': '2026-09-01T11:00:00+00:00',
            'fecha_fin': '2026-09-01T09:00:00+00:00',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)


if __name__ == '__main__':
    unittest.main()
