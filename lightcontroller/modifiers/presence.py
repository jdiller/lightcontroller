import ast
import logging
from lightcontroller.modifiers.modifier import Modifier
from lightcontroller.dataproviders.presence import Presence as PresenceProvider

class Presence(Modifier):

    def __init__(self):
        self._devices = []

    def _modify(self, lightsettings):
        if lightsettings.red == 0 and lightsettings.blue == 0 and lightsettings.green == 0:
            pp = PresenceProvider(self.devices)
            if pp.user_present:
                logging.debug("Activating blue lights because of user presence")
                lightsettings.blue = 255

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, value):
        self._devices = ast.literal_eval(value)
