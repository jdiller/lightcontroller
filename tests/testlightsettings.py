import unittest
import json
from lightcontroller.lightsettings import LightSettings


class TestLightSettings(unittest.TestCase):

    def test_can_init(self):
        settings = LightSettings()
        self.assertIsNotNone(settings)

    def test_values_init_to_none(self):
        s = LightSettings()
        self.assertIsNone(s.red)
        self.assertIsNone(s.blue)
        self.assertIsNone(s.green)
        self.assertIsNone(s.on_duration)
        self.assertIsNone(s.next_settings)

    def test_can_set_blue(self):
        s = LightSettings()
        s.blue = 20
        self.assertEquals(s.blue, 20)

    def test_can_set_red(self):
        s = LightSettings()
        s.red = 10
        self.assertEquals(s.red, 10)

    def test_can_set_green(self):
        s = LightSettings()
        s.green = 80
        self.assertEquals(s.green, 80)

    def test_invalid_red_value_throws(self):
        s = LightSettings()
        with self.assertRaises(ValueError):
            s.red = -10
        with self.assertRaises(ValueError):
            s.red = 300

    def test_invalid_green_value_throws(self):
        s = LightSettings()
        with self.assertRaises(ValueError):
            s.green = -0.01
        with self.assertRaises(ValueError):
            s.green = 100000

    def test_invalid_blue_value_throws(self):
        s = LightSettings()
        with self.assertRaises(ValueError):
            s.blue = -1
        with self.assertRaises(ValueError):
            s.blue = 256

    def test_can_set_on_duration(self):
        s = LightSettings()
        s.on_duration = 3
        self.assertEquals(s.on_duration, 3)

    def test_can_serialize_to_json(self):
        s = LightSettings()
        s.red = 10
        jsonstr = s.to_json()
        self.assertEquals(jsonstr, '{"red": 10}')

    def test_can_initialize_via_constructor(self):
        s = LightSettings(
            red=1, blue=2, green=3)
        self.assertEquals(s.red, 1)
        self.assertEquals(s.blue, 2)
        self.assertEquals(s.green, 3)

    def test_can_load_from_json(self):
        d = {'red': 10, 'blue': 20, 'green': 30,
             'on_duration': 1}
        json_str = json.dumps(d)
        s = LightSettings.from_json(json_str)
        self.assertTrue(s is not None)
        self.assertEquals(s.red, 10)
        self.assertEquals(s.blue, 20)
        self.assertEquals(s.green, 30)
        self.assertEquals(s.on_duration, 1)

    def test_can_create_from_color_tuple(self):
        color = (255, 255, 255)
        s = LightSettings(color=color)
        self.assertEquals(s.red, 255)
        self.assertEquals(s.blue, 255)
        self.assertEquals(s.green, 255)

    def test_can_set_via_color_tuple(self):
        color = (128, 128, 128)
        s = LightSettings()
        s.set_color(color)
        self.assertEquals(s.red, 128)
        self.assertEquals(s.blue, 128)
        self.assertEquals(s.green, 128)

    def test_can_dim_lights_uniformly(self):
        color = (100, 100, 100)
        s = LightSettings()
        s.set_color(color)
        s.dim(75)
        self.assertEquals(s.red, 75)
        self.assertEquals(s.green, 75)
        self.assertEquals(s.blue, 75)

    def test_raises_if_ambiguous_color_data_supplied(self):
        with self.assertRaises(ValueError):
            LightSettings(red=10, color=(10, 10, 10))

    def test_can_compare_settings_for_equivalence(self):
        color = (100, 100, 100)
        s = LightSettings()
        s.set_color(color)

        s2 = LightSettings()
        s2.set_color(color)

        self.assertEquals(s, s2)
        self.assertFalse(s is s2)

    def test_can_compare_settings_to_tuple(self):
        color = (100, 100, 100)
        s = LightSettings()
        s.set_color(color)

        self.assertEquals(s, color)


