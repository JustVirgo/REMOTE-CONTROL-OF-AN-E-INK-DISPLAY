import requests
from dataclasses import dataclass

@dataclass
class WatherWidgetData:
    main: str
    desc: str
    icon: str
    temp: float


def get_lat_lon_city(city_name, API_key, state_code="", country_code=""):
    resp = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&appid={API_key}').json()
    data = resp[0]
    #print(data)
    lat, lon = data.get('lat'), data.get('lon')
    return lat, lon

#ZIP code may be needed to have a space in it
def get_lat_lon_zip(zip_code, country_code, API_key):
    resp = requests.get(f'http://api.openweathermap.org/geo/1.0/zip?zip={zip_code},{country_code}&appid={API_key}').json()
    lat, lon = resp.get('lat'), resp.get('lon')
    return lat, lon


def get_weather_by_city(city_name, API_key, units="metric", state_code="", country_code=""):
    lat, lon = get_lat_lon_city(city_name, API_key, state_code, country_code)
    resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&units={units}').json()
    data = WatherWidgetData(
        main=resp.get('weather')[0].get('main'),
        desc=resp.get('weather')[0].get('description'),
        icon=resp.get('weather')[0].get('icon'),
        temp=resp.get('main').get('temp')
    )
    return data

def get_weather_by_zip(zip_code, country_code, API_key, units="metric", state_code=""):
    lat, lon = get_lat_lon_zip(zip_code, country_code, API_key)
    resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&units={units}').json()
    data = WatherWidgetData(
        main=resp.get('weather')[0].get('main'),
        desc=resp.get('weather')[0].get('description'),
        icon=resp.get('weather')[0].get('icon'),
        temp=resp.get('main').get('temp')
    )
    return data

#def main(zip_code, country_code):
 #   return get_weather_by_zip(zip_code, country_code, api_key)

