from django.shortcuts import render
from .forms import CityForm
import requests
from requests.exceptions import RequestException


def get_coordinates(city_name):
    try:
        geocode_url = f'https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1'
        response = requests.get(geocode_url)
        response.raise_for_status()
        data = response.json()

        if data:
            return data[0]['lat'], data[0]['lon']
        else:
            return None, None
    except RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None, None
    except ValueError as e:
        print(f"Ошибка обработки JSON: {e}")
        return None, None


def get_weather_data(lat, lon):
    try:
        api_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m'
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if 'hourly' in data and 'temperature_2m' in data['hourly']:
            return data['hourly']['temperature_2m'][0]
        else:
            return None
    except RequestException as e:
        print(f"error request: {e}")
        return None
    except ValueError as e:
        print(f"error JSON: {e}")
        return None


def index(request):
    form = CityForm()
    return render(request, 'weather/index.html', {'form': form})


def get_weather(request):
    form = CityForm()
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            lat, lon = get_coordinates(city)
            if lat and lon:
                temperature = get_weather_data(lat, lon)
                if temperature is not None:
                    return render(
                        request,
                        'weather/index.html',
                        {'form': form, 'weather': temperature, 'city': city}
                    )
                else:
                    form.add_error('city', 'Не удалось получить данные о погоде.')
            else:
                form.add_error('city', 'Город не найден.')
    return render(request, 'weather/index.html', {'form': form})
