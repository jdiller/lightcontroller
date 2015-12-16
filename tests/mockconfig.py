from collections import defaultdict

class MockConfig(object):

    def __init__(self):
        self.data = defaultdict(dict)

    def set(self, section, key, value):
        self.data[section][key] = value

    def get(self, section, key):
        return self.data[section].get(key)

    def getint(self, section, key):
        return int(self.data[section].get(key))


