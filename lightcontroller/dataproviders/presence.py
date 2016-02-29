import requests
import ast
import bluetooth
from ConfigParser import ConfigParser


class Presence(object):

    def __init__(self, devices):
        self.devices = devices

    @property
    def user_present(self):
        for device in self.devices:
            if bluetooth.lookup_name(device, timeout=1.5):
                return True

