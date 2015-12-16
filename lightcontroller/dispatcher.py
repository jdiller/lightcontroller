import logging
import gevent
from collections import namedtuple

PluginRunner = namedtuple('PluginRunner', 'plugin greenlet')


class Dispatcher(object):
    """
    This class loads plugins and modifiers and starts and stops them
    """

    def __init__(self, config, raspi):
        """
        Set up the dispatcher, inject the config and raspi interface to use.

        config -- a configparser compatible object with details on which plugins and modifiers to use.
        raspi -- the raspi gpio interface
        """

        self.config = config
        self.raspi = raspi
        self._plugins = {}
        self._modifiers = {}

        self._build_plugin_chain()
        self._build_modifier_chain()

        self._configure_plugins()
        self.runners = []

    def start(self):
        """
        Starts all of the plugins in the plugin chain.
        """

        for plugin in self.plugin_chain:
            worker = gevent.Greenlet(self._plugin_loop, plugin)
            runner = PluginRunner(plugin, worker)
            self.runners.append(runner)
        self.runners.sort(key=lambda runner: runner.plugin.sequence)
        for runner in self.runners:
            runner.greenlet.start()

    def stop(self):
        """
        Stops all of the plugins in the plugin chain by killing their greenlet
        """

        for runner in self.runners:
           if not runner.greenlet.dead:
               runner.greenlet.kill()

    def _plugin_loop(self, plugin):
        """
        Executes a plugin's `execute` method in a loop. Pauses for `plugin.interval` seconds after each execution.

        plugin -- the plugin to run in the loop
        """
        try:
            while True:
                lightsettings = plugin.execute()
                self.apply_settings(lightsettings)
                gevent.sleep(plugin.interval)
        except gevent.GreenletExit:
            logging.debug('Plugin ({}) loop aborted'.format(type(plugin).__name__))

    @property
    def plugin_chain(self):
        """ All the loaded plugins """
        return self._plugins.values()

    @property
    def modifier_chain(self):
        """ All the loaded modifiers """
        return self._modifiers.values()

    def _build_plugin_chain(self):
        plugins = self.config.get('main', 'plugins')
        self._plugins = self._load_object_chain(plugins)

    def _build_modifier_chain(self):
        modifiers = self.config.get('main', 'modifiers')
        self._modifiers = self._load_object_chain(modifiers)

    def _load_object_chain(self, class_list):
        classes = {}
        for class_path in class_list.split(','):
            cls = self._get_class(class_path)
            logging.debug("Loading a {}, {}".format(class_path, cls))
            new_obj = cls()
            classes[class_path] = new_obj
        logging.debug("Classes loaded: {}".format(classes))
        return classes

    def _get_class(self, class_path):
        parts = class_path.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def _configure_plugins(self):
        for plugin, plugin_obj in self._plugins.iteritems():
            plugin_obj.interval = self.config.getint(plugin, "interval")
            plugin_obj.sequence = self.config.getint(plugin, "sequence")

    def apply_settings(self, lightsettings):
        """
        Modifies a `lightsettings` object by passing it through the chain of modifiers
        Then applies those settings to the GPIO
        """
        for modifier in self.modifier_chain:
            modifier.modify(lightsettings)
        self.raspi.apply_settings(lightsettings)
