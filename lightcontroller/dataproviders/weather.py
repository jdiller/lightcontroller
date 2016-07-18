import requests
import redis
import logging
import json
from ConfigParser import ConfigParser

class WeatherData(object):
    BASE_URL = 'https://api.forecast.io/forecast/{}/{},{}?units=si'
    REFRESH_TIMEOUT = 90

    def __init__(self):
        cp = ConfigParser()
        cp.read('config.cfg')
        self.api_key = cp.get('forecast', 'API_KEY')
        self.latitude = cp.get('forecast', 'LATITUDE')
        self.longitude = cp.get('forecast', 'LONGITUDE')
        self.weather_data = None
        self.store = redis.StrictRedis(host='localhost', port=6379, db=0)

    @property
    def request_url(self):
        return WeatherData.BASE_URL.format(self.api_key, self.latitude, self.longitude)

    def refresh(self, force=False):
        logging.debug("Weather data requested")
        weather_json = self.store.get('last_weather')
        if weather_json and not force:
            logging.debug("Using cached weather data")
            self.weather_data = json.loads(weather_json)
        else:
            logging.debug("Fetching new weather data from online provider")
            try:
                r = requests.get(self.request_url)
            except requests.ConnectionError:
                logging.warn('Failed to fetch weather data from online service')
            if r and r.text:
                self.store.setex('last_weather', WeatherData.REFRESH_TIMEOUT, r.text)
                self.weather_data = r.json()

    def get(self, value, default=None):
        while not self.weather_data:
            self.refresh()
            if not self.weather_data:
                sleep(2)
        return self.weather_data.get(value, default)
