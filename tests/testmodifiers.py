import unittest
from freezegun import freeze_time
from lightcontroller.modifiers.modifier import Modifier
from lightcontroller.modifiers.timeofday import TimeOfDayModifier
from lightcontroller.lightsettings import LightSettings

class TestModifier(unittest.TestCase):
    def test_can_init(self):
        mod = Modifier()
        self.assertIsNotNone(mod)

    def test_detects_cycles(self):
        ls = LightSettings()
        ls2 = LightSettings()
        ls3 = LightSettings()
        #make a cycle
        ls.next_settings = ls2
        ls2.next_settings = ls3
        ls3.next_settings = ls

        mod = Modifier()
        mod.modify(ls)
        self.assertIsNotNone(ls)

class TestTimeOfDayModifier(unittest.TestCase):
    def test_can_init(self):
        tod = TimeOfDayModifier()
        self.assertIsNotNone(tod)

    @freeze_time('2015-12-25 10:01:00')
    def test_modifies_to_off_after_10am(self):
        tod = TimeOfDayModifier()
        ls = LightSettings(red=100, blue=100, green=100)
        tod.modify(ls)
        self.assertEquals(0, ls.red)
        self.assertEquals(0, ls.blue)
        self.assertEquals(0, ls.green)

    @freeze_time('2015-12-25 22:01:00')
    def test_modifies_to_off_after_10pm(self):
        tod = TimeOfDayModifier()
        ls = LightSettings(red=100, blue=100, green=100)
        tod.modify(ls)
        self.assertEquals(0, ls.red)
        self.assertEquals(0, ls.blue)
        self.assertEquals(0, ls.green)

    @freeze_time('2015-12-25 20:01:00')
    def test_evening_dim(self):
        tod = TimeOfDayModifier()
        ls = LightSettings(red=100, blue=100, green=100)
        tod.modify(ls)
        self.assertEquals(30, ls.red)
        self.assertEquals(30, ls.blue)
        self.assertEquals(30, ls.green)

    @freeze_time('2015-12-25 07:00:00')
    def test_standard_dim(self):
        tod = TimeOfDayModifier()
        ls = LightSettings(red=100, blue=100, green=100)
        tod.modify(ls)
        self.assertEquals(70, ls.red)
        self.assertEquals(70, ls.blue)
        self.assertEquals(70, ls.green)

    @freeze_time('2015-12-26 07:00:00')
    def test_off_on_weekend(self):
        tod = TimeOfDayModifier()
        ls = LightSettings(red=100, blue=100, green=100)
        tod.modify(ls)
        self.assertEquals(0, ls.red)
        self.assertEquals(0, ls.blue)
        self.assertEquals(0, ls.green)
