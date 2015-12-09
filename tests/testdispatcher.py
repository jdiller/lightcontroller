import unittest
from collections import defaultdict
from alights.dispatcher import Dispatcher


class MockConfig(object):
    def __init__(self):
        self.data = defaultdict(dict)

    def set(self, section, key, value):
        self.data[section][key] = value

    def get(self, section, key):
        return self.data[section].get(key)

class TestDispatcher(unittest.TestCase):
    @property
    def mockconfig(self):
        ret = MockConfig()
        ret.set('main', 'plugins', 'alights.plugins.weather.Weather')
        ret.set('main', 'modifiers', 'alights.modifiers.timeofday.TimeOfDayModifier')
        return ret

    def test_can_init_plugin_chain(self):
        dispatcher = Dispatcher(self.mockconfig)
        self.assertIsNotNone(dispatcher.plugin_chain)
        self.assertNotEqual(0, len(dispatcher.plugin_chain))

    def test_can_init_modifier_chain(self):
        dispatcher = Dispatcher(self.mockconfig)
        self.assertIsNotNone(dispatcher.modifier_chain)
        self.assertNotEqual(0, len(dispatcher.modifier_chain))
