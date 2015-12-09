import requests
from ConfigParser import ConfigParser


class WebEndpoint(object):

    def __init__(self, base_url):
        self.base_url = base_url
        self.data = None

    def refresh(self, params=[]):
        r = requests.get(self.base_url.format(params))
        self.data = r.json()

    def get(self, value, default=None):
        if not self.data:
            self.refresh()
        return self.data.get(value, default)
