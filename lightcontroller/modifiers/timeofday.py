import datetime
import logging
import ast
from lightcontroller.modifiers.modifier import Modifier


class TimeOfDay(Modifier):

    """
    Modifies light behavior based on time of day. (e.g. Turns everything off at night and when nobody is home). 
    """

    def __init__(self):
        self._off_between = []
        self._off_days = []
        self._dim_between = []
        self._dim_level = 100

    def _modify(self, settings):
        now = datetime.datetime.now()
        off_by_hour = reduce(lambda r, x: True if self._is_between(
            now.hour, x[0], x[1]) or r else False, self.off_between, False)
        off_by_day = now.weekday() in self._off_days
        dim_by_hour = reduce(lambda r, x: True if self._is_between(
            now.hour, x[0], x[1]) or r else False, self.dim_between, False)
        if off_by_hour or off_by_day:
            logging.debug(
                "Off days: {}; Current Day: {}".format(self._off_days, now.weekday()))
            logging.debug(
                "Off hours: {}; Current Hour: {}".format(self.off_between, now.hour))
            logging.debug("Turning everything off based on " +
                          ('time of day' if off_by_hour else 'day of week'))
            settings.all_off()
        elif dim_by_hour:
            logging.debug("Dimming lights based on schedule")
            settings.dim(self.dim_level)
        else:
            logging.debug("No modifications based on schedule required")

    @property
    def off_between(self):
        return self._off_between

    @off_between.setter
    def off_between(self, value):
        self._off_between = ast.literal_eval(value)

    @property
    def off_days(self):
        return self._off_days

    @off_days.setter
    def off_days(self, value):
        self._off_days = ast.literal_eval(value)

    @property
    def dim_between(self):
        return self._dim_between

    @dim_between.setter
    def dim_between(self, value):
        self._dim_between = ast.literal_eval(value)

    @property
    def dim_level(self):
        return self._dim_level

    @dim_level.setter
    def dim_level(self, value):
        self._dim_level = int(value)

    def _is_between(self, now, start, end):
        ret = None
        logging.debug(
            "Checking if {}:00 is between {}:00 and {}:00".format(now, start, end))
        if start <= end:
            logging.debug("No midnight span, straightforward comparison")
            ret = start <= now < end
        else:  # over midnight e.g., 23:30-04:15
            logging.debug("Range spans midnight")
            ret = start <= now or now < end
        logging.debug("it is between" if ret else "it is not between")
        return ret
