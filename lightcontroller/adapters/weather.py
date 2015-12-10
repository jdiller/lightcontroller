import copy

class WeatherAdapter(object):

    def __init__(self, weather_data):
        self.weather_data = weather_data

    @property
    def color_table(self):
        # temperature colour range:
        # below -15 -> turquoise
        #-14 to 0 -> blue
        # 0 to 10 -> green
        # 10 to 20 -> yellow
        # 20 to 30 -> orange
        # over 30 -> red

        # map it
        temps = {
            (float("-inf"), -25): (0x75, 0xF4, 0xFF),
            (-24.99, -20): (0x6A, 0xFC, 0xE3),
            (-19.99, -15): (0x5F, 0xFA, 0xB9),
            (-14.99, -10): (0x55, 0xF8, 0x8B),
            (-9.99, -5): (0x4B, 0xF6, 0x58),
            (-4.99, 0): (0x5F, 0xF4, 0x41),
            (0.01, 5): (0x85, 0xF2, 0x37),
            (5.01, 10): (0xB0, 0xEF, 0x2D),
            (10.01, 15): (0xDD, 0xED, 0x24),
            (15.01, 20): (0xEB, 0xC7, 0x1B),
            (20.01, 25): (0xE9, 0x8E, 0x11),
            (25.01, 30): (0xE7, 0x51, 0x08),
            (30.01, float("inf")): (0xFC, 0x44, 0x23)
        }
        return temps

    def get_color_for_temperature(self, temperature):
        for key, value in self.color_table.iteritems():
            if temperature >= key[0] and temperature <= key[1]:
                return value

    def apply_to_settings(self, settings):
        if not self.weather_data:
            self.refresh()
        current_weather = self.weather_data.get('currently')
        if current_weather:
            temperature = current_weather['temperature']
            temperature_color = self.get_color_for_temperature(
                round(temperature, 2))
            settings.set_color(temperature_color)
            precip_intensity = current_weather.get('precipIntensity', 0)
            if precip_intensity > 0:
                precip_warning_settings = copy.copy(settings)
                precip_warning_settings.red = 255
                precip_warning_settings.blue /= 3
                precip_warning_settings.green /= 3
                precip_warning_settings.on_duration = 4
                settings.on_duration = 4
                settings.next_settings = precip_warning_settings
                precip_warning_settings.next_settings = settings

        daily_weather = self.weather_data.get('daily')
        if daily_weather:
            today_weather = daily_weather['data'][0]
            precip_probability = today_weather.get('precipProbability')
            if precip_probability > 0.30:
                precip_warning_settings = copy.copy(settings)
                precip_warning_settings.red = 255
                precip_warning_settings.blue /= 3
                precip_warning_settings.green /= 3
                precip_warning_settings.on_duration = 1
                settings.on_duration = 4
                settings.next_settings = precip_warning_settings
                precip_warning_settings.next_settings = settings
            else:
                daily_high = today_weather.get('temperatureMax')
                high_temp_settings = copy.copy(settings)
                high_temp_color = self.get_color_for_temperature(daily_high)
                high_temp_settings.set_color(high_temp_color)
                high_temp_settings.transition_time = 4
                high_temp_settings.next_settings = settings
                settings.next_settings = high_temp_settings
