from plugin import Plugin
from lightcontroller.dataproviders.weather import WeatherData
from lightcontroller.adapters.weather import WeatherAdapter


class Weather(Plugin):

    def _apply_settings(self, settings):
        super(Weather, self)._apply_settings(settings)
        data = WeatherData()
        adapter = WeatherAdapter(data)
        adapter.apply_to_settings(settings)
