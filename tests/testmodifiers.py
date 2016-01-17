import unittest
from freezegun import freeze_time
from lightcontroller.modifiers.modifier import Modifier
from lightcontroller.modifiers.timeofday import TimeOfDay
from lightcontroller.lightsettings import LightSettings
from mockconfig import MockConfig


class TestModifier(unittest.TestCase):

    def test_can_init(self):
        mod = Modifier()
        self.assertIsNotNone(mod)

    def test_detects_cycles(self):
        ls = LightSettings()
        ls2 = LightSettings()
        ls3 = LightSettings()
        # make a cycle
        ls.next_settings = ls2
        ls2.next_settings = ls3
        ls3.next_settings = ls

        mod = Modifier()
        mod.modify(ls)
        self.assertIsNotNone(ls)


class TestTimeOfDay(unittest.TestCase):

    def test_can_init(self):
        tod = TimeOfDay()
        self.assertIsNotNone(tod)

    @property
    def mockconfig(self):
        ret = MockConfig()
        ret.set('main', 'modifiers', 'TimeOfDay')
        ret.set('TimeOfDay', 'on_after', '7,17')
        ret.set('TimeOfDay', 'off_between', '[(23,7),(10,17)]')
        ret.set('TimeOfDay', 'off_days', '[5, 6]')
        ret.set('TimeOfDay', 'dim_between', '[(20,8)]')
        ret.set('TimeOfDay', 'dim_level', '30')
        return ret

    @freeze_time('2015-12-25 10:01:00')
    def test_modifies_to_off_after_10am(self):
        tod = TimeOfDay()
        ls = LightSettings(red=100, blue=100, green=100)
        tod.configure(self.mockconfig.items('TimeOfDay'))
        tod.modify(ls)
        self.assertEquals(0, ls.red)
        self.assertEquals(0, ls.blue)
        self.assertEquals(0, ls.green)

    @freeze_time('2015-12-25 23:01:00')
    def test_modifies_to_off_after_11pm(self):
        tod = TimeOfDay()
        ls = LightSettings(red=100, blue=100, green=100)
        tod.configure(self.mockconfig.items('TimeOfDay'))
        tod.modify(ls)
        self.assertEquals(0, ls.red)
        self.assertEquals(0, ls.blue)
        self.assertEquals(0, ls.green)

    @freeze_time('2015-12-21 20:01:00')
    def test_evening_dim(self):
        tod = TimeOfDay()
        ls = LightSettings(red=100, blue=100, green=100)
        tod.configure(self.mockconfig.items('TimeOfDay'))
        tod.modify(ls)
        self.assertEquals(30, ls.red)
        self.assertEquals(30, ls.blue)
        self.assertEquals(30, ls.green)

    @freeze_time('2015-12-26 07:00:00')
    def test_off_on_weekend(self):
        tod = TimeOfDay()
        ls = LightSettings(red=100, blue=100, green=100)
        tod.configure(self.mockconfig.items('TimeOfDay'))
        tod.modify(ls)
        self.assertEquals(0, ls.red)
        self.assertEquals(0, ls.blue)
        self.assertEquals(0, ls.green)
