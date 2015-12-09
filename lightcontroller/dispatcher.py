import sys
import logging
from collections import namedtuple
from ConfigParser import ConfigParser
import plugins
import modifiers
from lightsettings import LightSettings

PluginRunner = namedtuple('PluginRunner', 'plugin greenlet')


class Dispatcher(object):

    def __init__(self, config):
        self.config = config
        self._build_plugin_chain()
        self._build_modifier_chain()

    def _build_plugin_chain(self):
        plugins = self.config.get('main', 'plugins') 
        self.plugin_chain = self._load_object_chain(plugins)

    def _build_modifier_chain(self):
        modifiers = self.config.get('main', 'modifiers') 
        self.modifier_chain = self._load_object_chain(modifiers)

    def _load_object_chain(self, class_list):
        classes = []
        for class_path in class_list.split(','):
            cls = self._get_class(class_path)
            logging.debug("Loading a {}, {}".format(class_path, cls))
            loaded_class = cls()
            classes.append(loaded_class)
        logging.debug("Classes loaded: {}".format(classes))
        return classes

    def _get_class(self, class_path):
        parts = class_path.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def plugin_callback(self, plugin, lightsettings):
        for modifier in self.modifier_chain:
            modifier.modift(lightsettings)
        self.apply_settings(lightsettings)

