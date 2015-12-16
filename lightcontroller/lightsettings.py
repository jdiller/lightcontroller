# -*- coding: utf-8 -*-
import json


class LightSettingsEncoder(json.JSONEncoder):

    def default(self, s):
        ret = {}
        props = ['red', 'green', 'blue',
                 'on_duration', 'next_settings']
        for p in props:
            if (getattr(s, p) is not None):
                ret[p] = getattr(s, p)
        return ret


class LightSettings(object):

    def __init__(self, red=None, blue=None, green=None, on_duration=None, color=None):
        if color and (red or blue or green):
            raise ValueError(
                'Set individual colors or give a color tuple, not both')
        self._red = red
        self._blue = blue
        self._green = green
        self._on_duration = on_duration
        self.next_settings = None
        self._transition_time = None
        if color:
            self.set_color(color)

    @property
    def red(self):
        return self._red

    @red.setter
    def red(self, value):
        if value is not None and (value < 0 or value > 255):
            raise ValueError('Intensity must be between 0 and 255')
        self._red = value

    @property
    def green(self):
        return self._green

    @green.setter
    def green(self, value):
        if value is not None and (value < 0 or value > 255):
            raise ValueError('Intensity must be between 0 and 255')
        self._green = value

    @property
    def blue(self):
        return self._blue

    @blue.setter
    def blue(self, value):
        if value is not None and (value < 0 or value > 255):
            raise ValueError('Intensity must be between 0 and 255')
        self._blue = value

    @property
    def transition_time(self):
        return self._transition_time

    @transition_time.setter
    def transition_time(self, value):
        if value is not None and value < 0:
            raise ValueError('Durations must be positive')
        self._transition_time = value


    @property
    def on_duration(self):
        return self._on_duration

    @on_duration.setter
    def on_duration(self, value):
        if value is not None and value < 0:
            raise ValueError('Durations must be positive')
        self._on_duration = value

    def to_json(self):
        return json.dumps(self, cls=LightSettingsEncoder)

    @classmethod
    def from_json(cls, jsonstr):
        d = json.loads(jsonstr)
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, d):
        ret = LightSettings()
        ret.blue = d.get('blue')
        ret.red = d.get('red')
        ret.green = d.get('green')
        ret.on_duration = d.get('on_duration')
        return ret

    def set_color(self, color):
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]

    def dim(self, percentage):
        self.red *= (percentage / 100.0)
        self.blue *= (percentage / 100.0)
        self.green *= (percentage / 100.0)

    def all_off(self):
        self.red = 0
        self.blue = 0
        self.green = 0

