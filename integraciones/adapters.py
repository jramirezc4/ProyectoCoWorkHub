import json
import os
from urllib.parse import quote
from abc import ABC, abstractmethod
from urllib.error import URLError
from urllib.request import Request, urlopen


class WeatherProvider(ABC):
    @abstractmethod
    def current_for(self, city):
        raise NotImplementedError


class DemoWeatherAdapter(WeatherProvider):
    def current_for(self, city):
        return {'city': city, 'condition': 'Soleado', 'temperature_c': 22}


class HttpWeatherAdapter(WeatherProvider):
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def current_for(self, city):
        request = Request(f'{self.base_url}?city={city}')
        try:
            with urlopen(request, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError('El proveedor meteorológico no está disponible.') from error
        return {
            'city': city,
            'condition': data['condition'],
            'temperature_c': data['temperature_c'],
        }


class WttrWeatherAdapter(WeatherProvider):
    """Adapter for the public wttr.in JSON API; no API key is required."""

    CITY_COORDINATES = {
        'medellin': '6.2442,-75.5812',
        'medellín': '6.2442,-75.5812',
    }

    def __init__(self, base_url='https://wttr.in'):
        self.base_url = base_url.rstrip('/')

    def current_for(self, city):
        location = self.CITY_COORDINATES.get(city.strip().lower(), city)
        request = Request(
            f'{self.base_url}/{quote(location)}?format=j1',
            headers={'User-Agent': 'Coworkhub-academic-demo/1.0'},
        )
        try:
            with urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            current = data['current_condition'][0]
            return {
                'city': city,
                'condition': current['weatherDesc'][0]['value'],
                'temperature_c': int(current['temp_C']),
            }
        except (URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, ValueError) as error:
            raise RuntimeError('El proveedor meteorológico no está disponible.') from error


def weather_provider():
    url = os.getenv('THIRD_PARTY_WEATHER_URL', '')
    if url:
        return HttpWeatherAdapter(url)
    if os.getenv('USE_DEMO_WEATHER', '0') == '1':
        return DemoWeatherAdapter()
    return WttrWeatherAdapter()
