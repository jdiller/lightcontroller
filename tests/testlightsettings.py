import unittest
import json
from alights.lightsettings import LightSettings
import alights.MockRPi.GPIO as g


class TestLightSettings(unittest.TestCase):

    def test_can_init(self):
        settings = LightSettings()

    def test_values_init_to_none(self):
        s = LightSettings()
        self.assertIsNone(s.red)
        self.assertIsNone(s.blue)
        self.assertIsNone(s.green)
        self.assertIsNone(s.on_duration)
        self.assertIsNone(s.off_duration)
        self.assertIsNone(s.flashing)

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

    def test_can_set_blue(self):
        s = LightSettings()
        s.blue = 20
        self.assertEquals(s.blue, 20)

    def test_can_set_flashing(self):
        s = LightSettings()
        s.flashing = True
        self.assertTrue(s.flashing)
        s.flashing = 1
        self.assertTrue(s.flashing)
        s.flashing = "Yes"
        self.assertTrue(s.flashing)
        s.flashing = "yes"
        self.assertTrue(s.flashing)
        s.flashing = "1"
        self.assertTrue(s.flashing)

    def test_invalid_red_value_throws(self):
        s = LightSettings()
        with self.assertRaises(ValueError):
            s.red = -10
        with self.assertRaises(ValueError):
            s.red = 110

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
            s.blue = 101

    def test_can_set_on_duration(self):
        s = LightSettings()
        s.on_duration = 3
        self.assertEquals(s.on_duration, 3)

    def test_can_set_off_duration(self):
        s = LightSettings()
        s.off_duration = 4
        self.assertEquals(s.off_duration, 4)

    def test_can_serialize_to_json(self):
        s = LightSettings()
        s.red = 10
        jsonstr = s.to_json()
        self.assertEquals(jsonstr, '{"red": 10.0}')

    def test_can_initialize_via_constructor(self):
        s = LightSettings(
            red=1, blue=2, green=3, flashing=True, on_duration=99, off_duration=101)
        self.assertEquals(s.red, 1)
        self.assertEquals(s.blue, 2)
        self.assertEquals(s.green, 3)
        self.assertTrue(s.flashing)
        self.assertEquals(s.on_duration, 99)
        self.assertEquals(s.off_duration, 101)

    def test_can_load_from_json(self):
        d = {'red': 10, 'blue': 20, 'green': 30,
             'flashing': 'yes', 'on_duration': 1, 'off_duration': 3}
        json_str = json.dumps(d)
        s = LightSettings.from_json(json_str)
        self.assertTrue(s is not None)
        self.assertEquals(s.red, 10)
        self.assertEquals(s.blue, 20)
        self.assertEquals(s.green, 30)
        self.assertTrue(s.flashing)
        self.assertEquals(s.on_duration, 1)
        self.assertEquals(s.off_duration, 3)

    def test_can_iterate_led_settings(self):
        s = LightSettings(red=20, blue=20, green=20)
        mock_leds = [g.PWM(1, 200),
                     g.PWM(2, 200),
                     g.PWM(3, 200)]
        LightSettings.red_led = mock_leds[0]
        LightSettings.green_led = mock_leds[1]
        LightSettings.blue_led = mock_leds[2]
        for led, val in s.leds:
            self.assertTrue(led in mock_leds)
            self.assertEqual(val, 20)

    def test_durations_not_none_when_flash_is_on(self):
        s = LightSettings(red=10)
        s.flashing = True
        self.assertTrue(s.on_duration is not None)
        self.assertTrue(s.off_duration is not None)

    def test_can_create_from_color_tuple(self):
        color = (255, 255, 255)
        s = LightSettings(color=color)
        self.assertEquals(s.red, 100)
        self.assertEquals(s.blue, 100)
        self.assertEquals(s.green, 100)

    def can_set_via_color_tuple(self):
        color = (128, 128, 128)
        s = LightSettings()
        s.set_color(color)
        self.assertEquals(s.red, 50)
        self.assertEquals(s.blue, 50)
        self.assertEquals(s.green, 50)

    def test_raises_if_ambiguous_color_data_supplied(self):
        with self.assertRaises(ValueError):
            s = LightSettings(red=10, color=(10, 10, 10))
