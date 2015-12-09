import datetime
import logging
from lightcontroller.modifiers.modifier import Modifier


class TimeOfDayModifier(Modifier):

    def modify(self, settings):
        super(TimeOfDayModifier, self).modify(settings)
        now = datetime.datetime.now()
        # turn off during the workday and all weekend
        if (now.hour >= 10 and now.hour <= 17) or (now.hour >= 22 or now.hour <= 6) or now.weekday() in [5, 6]:
            logging.debug("Turning everything off based on schedule")
            settings.all_off()
        elif now.hour >= 20:
            settings.dim(25)
