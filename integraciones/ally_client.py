import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen


def fetch_ally_spaces():
    url = os.getenv(
        'ALLY_SERVICE_URL',
        'http://localhost:5000/api/v2/servicio-aliado/',
    )
    request = Request(url, headers={'Accept': 'application/json'})
    try:
        with urlopen(request, timeout=3) as response:
            return json.loads(response.read().decode('utf-8'))
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError('El servicio aliado no está disponible.') from error
