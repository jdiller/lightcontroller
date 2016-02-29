import requests
import logging
from lightcontroller.plugins.plugin import Plugin
from lightcontroller.dataproviders.web import WebPollData

class WebPoll(Plugin):
    def _apply_settings(self, settings):
        data = WebPollData()
        data.refresh()
        red = data.get('red', None)
        blue = data.get('blue', None)
        green = data.get('green', None)

        if red or blue or green:
            logging.debug("Got web poll data. Applying to settings")
            settings.red = data.get('red', 0)
            settings.blue = data.get('blue', 0)
            settings.green = data.get('green', 0)
            settings.transition_time = 1
            settings.next_settings = None
        else:
            logging.debug("No data from web poll, passing through settings unchanged")

