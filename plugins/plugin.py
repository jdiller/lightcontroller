from lightsettings import LightSettings

class Plugin(object):

    def execute(self):
        settings = LightSettings()
        self._apply_settings(settings)
        return settings

    def _apply_settings(self, settings):
        pass

