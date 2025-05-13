from ..datasource_base import DataSource
from .open_weather import get_weather_by_city
from dotenv import load_dotenv
import os

load_dotenv()
DEFAULT_API_KEY = os.getenv("API_KEY")

class OpenWeatherSource(DataSource):
    def fetch_data(self):
        city = self.inputs.get("City")
        country = self.inputs.get("Country", "")
        api_key = self.inputs.get("API key") if self.inputs.get("API key") != "" else DEFAULT_API_KEY

        weather = get_weather_by_city(city, api_key, country_code=country)
        self.cached_data = {
            "tempF": {"value": weather.temp * 9/5 + 32, "type": "float"},
            "tempC": {"value": weather.temp, "type": "float"},
            "desc": {"value": weather.desc, "type": "string"},
            "main": {"value": weather.main, "type": "string"}
        }

    def get_name(self):
        return "OpenWeather - " + self.inputs.get("City")

    def get_data(self):
        return self.cached_data or {}

    def get_update_interval(self):
        return 300  # 5 minute
