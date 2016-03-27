import ast
import logging
from lightcontroller.modifiers.modifier import Modifier
from lightcontroller.dataproviders.presence import Presence as PresenceProvider

class Presence(Modifier):

    def __init__(self):
        self._devices = []

    def _modify(self, lightsettings):
        pp = PresenceProvider(self.devices)
        if not pp.user_present:
            logging.debug("Turning everything off because nobody is home")
            lightsettings.all_off()
            lightsettings.next_settings = None
        else:
            logging.debug("User presence detected. No changes to be made")

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, value):
        self._devices = ast.literal_eval(value)
