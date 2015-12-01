import requests
from ConfigParser import ConfigParser


class Weather(object):
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
        return Weather.BASE_URL.format(self.api_key, self.latitude, self.longitude)

    def refresh(self):
        r = requests.get(self.request_url)
        self.weather_data = r.json()

    def get(self, value, default=None):
        if not self.weather_data:
            self.refresh()
        return self.weather_data.get(value, default)

    def get_color_for_temperature(self, temperature):
        # temperature colour range:
        # below -15 -> turquoise
        #-14 to 0 -> blue
        # 0 to 10 -> green
        # 10 to 20 -> yellow
        # 20 to 30 -> orange
        # over 30 -> red

        # map it
        temps = {
            (float("-inf"), -15): (0xA4, 0x48, 0xFF),
            (-14.99, 0): (0x00, 0x00, 0x80),
            (0.01, 10): (0x00, 0x80, 0x00),
            (10.01, 20): (0xF2, 0xFD, 0x2F),
            (20.01, 30): (0xF8, 0xC1, 0x1D),
            (30.01, float("inf")): (0xFC, 0x44, 0x23)
        }
        for key, value in temps.iteritems():
            if temperature >= key[0] and temperature <= key[1]:
                return value

    def apply_to_settings(self, settings):
        if not self.weather_data:
            self.refresh()
        current_weather = self.weather_data.get('currently')
        if current_weather:
            precip_probability = current_weather['precipProbability']
            precip_intensity = current_weather['precipIntensity']
            temperature = current_weather['temperature']
            temperature_color = self.get_color_for_temperature(temperature)
            settings.set_color(temperature_color)
            if precip_intensity > 0:
                settings.flashing = True
                settings.on_duration = 1
                settings.off_duration = 1

            if precip_probability > 30:
                settings.flashing = True
                settings.on_duration = 4
                settings.off_duration = 0.5

            # cut intensity so things aren't so bright
            settings.red /= 2.5
            settings.blue /= 2.5
            settings.green /= 2.5
