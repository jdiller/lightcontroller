# -*- coding: utf-8 -*-
import json


class LightSettingsEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for LightSettings objects
    """
    def default(self, s):
        ret = {}
        props = ['red', 'green', 'blue',
                 'on_duration']
        for p in props:
            if (getattr(s, p) is not None):
                ret[p] = getattr(s, p)
        return ret


class LightSettings(object):
    """
    Data class representing how RBG LEDs should be actuated.

    Settings can be combined using `on_duration`, `transition_time` and `next_settings` to make patterns
    The pattern can be looped by assigning the first settings object to the `next_settings` property of
    the last settings object.

    TODO: The r,g,b values are a stright pass through to duty cycle, but brightness is logarithmic, so
    it would be nice if the range of values did a translation to relative brightness instead
    """
    def __init__(self, red=None, blue=None, green=None, color=None):
        """
        Initialize the settings object.

        Keyword args:
        red -- initial value for the brightness of the red led (0-255)
        green -- initial value for the brightness of the green led (0-255)
        blue -- initial value for the brightness of the blue led (0-255)
        color -- a 3-tuple specifing red, green, blue all at once

        Note: if the `color` 3-tuple is provided, an exception is thrown if individual color kwargs are also provided
        """
        if color and (red or blue or green):
            raise ValueError(
                'Set individual colors or give a color tuple, not both')
        self._red = red
        self._blue = blue
        self._green = green
        self._on_duration = None
        self.next_settings = None
        self._transition_time = None
        if color:
            self.set_color(color)

    @property
    def red(self):
        """ Get or set brightness of the red led (0-255) """
        return self._red

    @red.setter
    def red(self, value):
        if value is not None and (value < 0 or value > 255):
            raise ValueError('Intensity must be between 0 and 255')
        self._red = value

    @property
    def green(self):
        """ Get or set brightness of the green led (0-255) """
        return self._green

    @green.setter
    def green(self, value):
        if value is not None and (value < 0 or value > 255):
            raise ValueError('Intensity must be between 0 and 255')
        self._green = value

    @property
    def blue(self):
        """ Get or set brightness of the blue led (0-255) """
        return self._blue

    @blue.setter
    def blue(self, value):
        if value is not None and (value < 0 or value > 255):
            raise ValueError('Intensity must be between 0 and 255')
        self._blue = value

    @property
    def transition_time(self):
        """
        Get or set the time (in seconds) to spend transitioning from the current settings to these settings.

        If transition time is 0, the transition is immediate/abrupt, otherwise a fade algorithm is used to transition
        more gently/gradually.
        """
        return self._transition_time

    @transition_time.setter
    def transition_time(self, value):
        if value is not None and value < 0:
            raise ValueError('Durations must be positive')
        self._transition_time = value


    @property
    def on_duration(self):
        """
        Get or set the time the settings are applied for (after transition is complete, see: `transition_time`)
        after which the settings in `next_settings` are applied.

        If `next_settings` are not set, this property has no effect.
        """
        return self._on_duration

    @on_duration.setter
    def on_duration(self, value):
        if value is not None and value < 0:
            raise ValueError('Durations must be positive')
        self._on_duration = value

    @property
    def is_empty(self):
        return self.red is None and self.blue is None and self.green is None

    def to_json(self):
        """ Returns a json string representing this object """
        return json.dumps(self, cls=LightSettingsEncoder)

    @classmethod
    def from_json(cls, jsonstr):
        """ (Classmethod) Creates a new lightsettings object from json """
        d = json.loads(jsonstr)
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, d):
        """ (ClassMethod) Creates a new lightsettings object from a dict """
        ret = LightSettings()
        ret.blue = d.get('blue')
        ret.red = d.get('red')
        ret.green = d.get('green')
        ret.on_duration = d.get('on_duration')
        return ret

    def set_color(self, color):
        """ Sets all three colours at once using a 3-tuple (red, green, blue) """
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]

    def dim(self, percentage):
        """ Convenience method to cut brightness to `percentage` of its former value """
        if self.red:
            self.red *= (percentage / 100.0)
        if self.blue:
            self.blue *= (percentage / 100.0)
        if self.green:
            self.green *= (percentage / 100.0)

    def all_off(self):
        """ Convenience method to set all brightnesses to 0 """
        self.red = 0
        self.blue = 0
        self.green = 0

    def __eq__(self, other):
        if isinstance(other, LightSettings):
            return (self.red == other.red and
                    self.blue == other.blue and
                    self.green == other.green)
        if isinstance(other, tuple) and len(other) == 3:
            return (self.red == other[0] and 
                    self.blue == other[1] and
                    self.green == other[2])
        return False

    def __ne__(self, other):
        return not(self == other)

    def __repr__(self):
        return self.to_json()

    def __str__(self):
        return self.to_json()
