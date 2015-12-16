from lightcontroller.lightsettings import LightSettings


class Plugin(object):
    """
    Base class for plugins. Derived classes should override _apply_settings.
    """

    def execute(self):
        settings = LightSettings()
        self._apply_settings(settings)
        return settings

    def _apply_settings(self, settings):
        pass
