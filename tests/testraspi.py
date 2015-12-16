import unittest
import gevent
from lightcontroller.lightsettings import LightSettings
from lightcontroller.raspi import RasPi
from mockconfig import MockConfig
class TestRaspi(unittest.TestCase):
    @property
    def mockconfig(self):
        ret = MockConfig()
        ret.set('raspi', 'red', 17)
        ret.set('raspi', 'green', 18)
        ret.set('raspi', 'blue', 19)
        return ret

    def test_can_init(self):
        raspi = RasPi(self.mockconfig)
        self.assertIsNotNone(raspi.pi)

    def test_can_set_duty_cycle(self):
        raspi = RasPi(self.mockconfig)
        raspi.set_PWM_dutycycle(raspi.leds[0], 100)
        self.assertEquals(100, raspi.get_PWM_dutycycle(raspi.leds[0]))

    def test_can_set_all_off(self):
        raspi = RasPi(self.mockconfig)
        for led in raspi.leds:
            raspi.set_PWM_dutycycle(led, 50)
        raspi.set_all_off()
        for led in raspi.leds:
            self.assertEquals(0, raspi.get_PWM_dutycycle(led))


    def test_can_get_all_dutycyles(self):
        raspi = RasPi(self.mockconfig)
        a = 10
        for led in raspi.leds:
            raspi.set_PWM_dutycycle(led, a)
            a += 10
        red, green, blue = raspi.get_current_dutycycles()
        self.assertEquals(10, red)
        self.assertEquals(20, green)
        self.assertEquals(30, blue)

    def test_can_dim_all(self):
        raspi = RasPi(self.mockconfig)
        for led in raspi.leds:
            raspi.set_PWM_dutycycle(led, 100)
        raspi.dim_all(50)
        for led in raspi.leds:
            self.assertEquals(50, raspi.get_PWM_dutycycle(led))

    def test_can_set_from_simple_settings(self):
        raspi = RasPi(self.mockconfig)
        settings = LightSettings(red=10, green=20, blue=30)
        raspi.apply_settings(settings)
        red, green, blue = raspi.get_current_dutycycles()
        self.assertEquals(10, red)
        self.assertEquals(20, green)
        self.assertEquals(30, blue)

    def test_can_create_transition_range(self):
        raspi = RasPi(self.mockconfig)
        steps = raspi._get_steps(0, 10, 10)
        for i in range(11):
            self.assertEquals(i, steps[i])

    def test_can_transition_one_way(self):
        raspi = RasPi(self.mockconfig)
        settings = LightSettings(red=0, green=0, blue=0)
        settings2 = LightSettings(red=255, green=255, blue=255)
        settings.next_settings = settings2
        settings.on_duration = 0.015
        settings2.transition_time = 0.015
        raspi.apply_settings(settings)
        for led in raspi.leds:
            self.assertEquals(0, raspi.get_PWM_dutycycle(led))
        gevent.sleep(0.07)
        for led in raspi.leds:
            self.assertEquals(255, raspi.get_PWM_dutycycle(led))
