import unittest
from collections import defaultdict
from lightcontroller.dispatcher import Dispatcher
from lightcontroller import raspi


class MockConfig(object):

    def __init__(self):
        self.data = defaultdict(dict)

    def set(self, section, key, value):
        self.data[section][key] = value

    def get(self, section, key):
        return self.data[section].get(key)

    def getint(self, section, key):
        return int(self.data[section].get(key))


class TestDispatcher(unittest.TestCase):

    @property
    def mockconfig(self):
        ret = MockConfig()
        ret.set('main', 'plugins', 'lightcontroller.plugins.weather.Weather')
        ret.set(
            'main', 'modifiers', 'lightcontroller.modifiers.timeofday.TimeOfDayModifier')
        ret.set('lightcontroller.plugins.weather.Weather', 'interval', 90)
        ret.set('lightcontroller.plugins.weather.Weather', 'sequence', 1)
        return ret

    def test_can_init_plugin_chain(self):
        dispatcher = Dispatcher(self.mockconfig, raspi.RasPi())
        self.assertIsNotNone(dispatcher.plugin_chain)
        self.assertNotEqual(0, len(dispatcher.plugin_chain))

    def test_can_init_modifier_chain(self):
        dispatcher = Dispatcher(self.mockconfig, raspi.RasPi())
        self.assertIsNotNone(dispatcher.modifier_chain)
        self.assertNotEqual(0, len(dispatcher.modifier_chain))

    def test_plugins_initialized(self):
        dispatcher = Dispatcher(self.mockconfig, raspi.RasPi())
        plugin = dispatcher.plugin_chain[0]
        self.assertEqual(1, plugin.sequence)
        self.assertEqual(90, plugin.interval)
