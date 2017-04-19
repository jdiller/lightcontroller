import requests
import logging
from ConfigParser import ConfigParser


class WebPollData(object):

    def __init__(self):
        cp = ConfigParser()
        cp.read('config.cfg')
        self.url = cp.get('WebPoll', 'url')
        self.data = {}

    @property
    def request_url(self):
        return self.url

    def refresh(self):
        logging.debug("Refreshing WebPoll data")
        resp = requests.get(self.request_url)
        self.data = resp.json()
        logging.debug("Got WebPoll data: {}".format(self.data))

    def get(self, value, default=None):
        if self.data is None:
            self.refresh()
        return self.data.get(value, default)
