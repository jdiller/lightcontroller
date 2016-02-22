import unittest
import json
from lightcontroller.lightsettings import LightSettings
from lightcontroller.adapters.weather import WeatherAdapter

class MockWeatherData(object):
    def __init__(self):
        self.weather_data = None

    def refresh(self):
        f = open('fixtures/weather.json')
        self.weather_data = json.loads(f.read())
        f.close()

    def get(self, value, default=None):
        if not self.weather_data:
            self.refresh()
        return self.weather_data.get(value, default)

class TestWeatherAdapter(unittest.TestCase):

    def test_can_init(self):
        adptr = WeatherAdapter(MockWeatherData())
        self.assertIsNotNone(adptr)

    def test_can_get_color_table(self):
        adptr = WeatherAdapter(MockWeatherData())
        self.assertIsNotNone(adptr.color_table)

    def test_can_get_color_for_temperatures(self):
        adptr = WeatherAdapter(MockWeatherData())
        for x in range(-50,50):
            color = adptr.get_color_for_temperature(x)
            self.assertIsNotNone(color)
            self.assertTrue(color[0] >= 0 and color[0] <= 255)
            self.assertTrue(color[1] >= 0 and color[1] <= 255)
            self.assertTrue(color[1] >= 0 and color[1] <= 255)

    def test_no_precip_no_flashing(self):
        data = MockWeatherData()
        data.refresh()
        data.weather_data['currently']['precipIntensity'] = 0
        data.weather_data['daily']['precipPropbability'] = 0
        adptr = WeatherAdapter(data)
        settings = LightSettings()
        adptr.apply_to_settings(settings)
        self.assertTrue(settings.next_settings is None)
        self.assertTrue(settings.transition_time is None)

    def test_probable_precip_max_red(self):
        data = MockWeatherData()
        data.refresh()
        data.weather_data['currently']['precipIntensity'] = 0
        data.weather_data['currently']['precipProbability'] = 0.60
        adptr = WeatherAdapter(data)
        settings = LightSettings()
        adptr.apply_to_settings(settings)
        self.assertTrue(settings.next_settings is not None)
        self.assertEquals(4, settings.on_duration)
        self.assertEquals(255, settings.next_settings.red)

    def test_active_precip_max_red(self):
        data = MockWeatherData()
        data.refresh()
        data.weather_data['currently']['precipIntensity'] = 3
        data.weather_data['daily']['data'][0]['precipProbability'] = 0
        adptr = WeatherAdapter(data)
        settings = LightSettings()
        adptr.apply_to_settings(settings)
        self.assertTrue(settings.next_settings is not None)
        self.assertEquals(4, settings.on_duration)
        self.assertEquals(255, settings.next_settings.red)


