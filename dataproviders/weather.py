import requests
from ConfigParser import ConfigParser


class WeatherData(object):
    BASE_URL = 'https://api.forecast.io/forecast/{}/{},{}?units=si'

    def __init__(self):
        cp = ConfigParser()
        cp.read('config.cfg')
        self.api_key = cp.get('forecast', 'API_KEY')
        self.latitude = cp.get('forecast', 'LATITUDE')
        self.longitude = cp.get('forecast', 'LONGITUDE')
        self.weather_data = None

    @property
    def request_url(self):
        return WeatherData.BASE_URL.format(self.api_key, self.latitude, self.longitude)

    def refresh(self):
        r = requests.get(self.request_url)
        self.weather_data = r.json()

    def get(self, value, default=None):
        if not self.weather_data:
            self.refresh()
        return self.weather_data.get(value, default)
