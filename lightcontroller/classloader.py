import pkgutil
import sys
import os
import logging

class ClassLoader(object):
    def __init__(self):
        base_path = os.path.abspath(os.path.dirname(__file__))
        logging.debug('Searching ({}) for plugins and modifiers'.format(base_path))
        self._plugin_path = os.path.join(base_path, "plugins")
        logging.debug('Plugin path: {}'.format(self._plugin_path))
        self._modifier_path = os.path.join(base_path, "modifiers")
        logging.debug('Modifier path: {}'.format(self._modifier_path))
        self._plugin_modules = list(pkgutil.iter_modules([self._plugin_path]))
        self._modifier_modules = list(pkgutil.iter_modules([self._modifier_path]))

    def get_modifier_class(self, modifier_name):
        return self._get_class('modifier', modifier_name, self._modifier_modules)

    def get_plugin_class(self, plugin_name):
        return self._get_class('plugin', plugin_name, self._plugin_modules)

    def _get_class(self, type_name, class_name, module_list):
        logging.debug('Attempting to load {} "{}"'.format(type_name, class_name))
        for loader, modname, is_package in module_list:
            if modname.lower() in [class_name.lower(), class_name.lower() + type_name]:
                logging.debug("Found module '{}', trying to get {} class".format(modname, type_name))
                mod = loader.find_module(modname).load_module(modname)
                cls = getattr(mod, class_name)
                if not cls:
                    logging.warn('Tried to load {} class "{}" from module "{}" but it wasn not found'.format(type_name, class_name, modname))
                return cls

