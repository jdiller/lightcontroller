from plugin import Plugin
from lightcontroller.dataproviders.weather import WeatherData
from lightcontroller.adapters.weather import WeatherAdapter


class Weather(Plugin):
    """
    Plugin to use current weather data to set the light behavior.

    Current temperature determines the initial colour. Active or probable precipitation sets a warning pulse.
    See the class `WeatherAdapter` for actual data->behavior logic.
    See the class `WeatherData` for weather data fetching logic.
    """

    def _apply_settings(self, settings):
        super(Weather, self)._apply_settings(settings)
        data = WeatherData()
        adapter = WeatherAdapter(data)
        adapter.apply_to_settings(settings)
