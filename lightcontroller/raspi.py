import gevent
import platform
import logging

# dirty hack to determine if we're actually running on the rpi
if platform.machine().startswith("arm"):
    import pigpio
else:
    # dev/test mode
    import mockpigpio as pigpio

class RasPi(object):
    """
    A wrapper class around a lower-level Raspi GPIO interface. (Currently pigpio)

    Used to switch pins on and off and set or get their duty cycle.
    """
    def __init__(self, config):
        """
        Initialize the GPIO interface.

        config -- a configuration object (configparser compatible) that specifies which GPIO pins represent which colours.
        """

        self.green = config.getint('raspi', 'green')
        self.red = config.getint('raspi', 'red')
        self.blue = config.getint('raspi', 'blue')
        self.leds = [self.red, self.green, self.blue]
        self.pi = pigpio.pi()
        self.worker = None

    def get_PWM_dutycycle(self, pin):
        """
        Query and return the current duty cycle of a GPIO pin.

        pin -- the pin to get the duty cycle for
        """

        return self.pi.get_PWM_dutycycle(pin)

    def set_PWM_dutycycle(self, pin, dutycycle):
        """
        Set the duty cycle of a specific pin to a specific value.

        pin -- the pin to set the duty cycle for
        dutycycle -- (float) value between 0.00 and 255.0 for the dutycycle
        """

        self.pi.set_PWM_dutycycle(pin, dutycycle)

    def set_all_off(self):
        """
        Shortcut method to turn all configured pins (R,G,B) off at once.
        """

        for pin in self.leds:
            self.set_PWM_dutycycle(pin, 0)

    def get_current_dutycycles(self):
        """
        Shortcut method to get all configured pins' (R,G,B) current dutycycle
        """

        for led in self.leds:
            yield self.get_PWM_dutycycle(led)

    def dim_all(self, percentage):
        """
        Shortcut method to reduce all configured pins' (R,G,B) dutycycle to a percentage of their previous value

        percentage -- the percentage to which to reduce the duty cycle
        e.g. percentage == 30 && dutycycle == 100; dutycycle 100 -> 30
        """

        for pin in self.leds:
            current_duty_cycle = self.pi.get_PWM_dutycycle(pin)
            new_duty = float(current_duty_cycle) * (float(percentage) / 100)
            self.set_PWM_dutycycle(pin, new_duty)

    def _get_steps(self, start, finish, steps):
        return [start + (x * (finish-start) / steps) for x in range(steps + 1)]

    def _transition(self, to_settings, duration):
        STEPS = 50
        current_red, current_green, current_blue = self.get_current_dutycycles()
        red_steps = self._get_steps(current_red, to_settings.red, STEPS)
        blue_steps = self._get_steps(current_blue, to_settings.blue, STEPS)
        green_steps = self._get_steps(current_green, to_settings.green, STEPS)
        logging.debug('Starting step-wise transition to new settings')
        for x in range(STEPS + 1):
            self.pi.set_PWM_dutycycle(self.red, red_steps[x])
            self.pi.set_PWM_dutycycle(self.blue, blue_steps[x])
            self.pi.set_PWM_dutycycle(self.green, green_steps[x])
            gevent.sleep(float(duration) / STEPS)
        logging.debug('Step-wise transition completed')

    def _set_leds(self, settings):
        try:
            while settings:
                logging.debug('Applying new settings')
                if settings.transition_time and settings.transition_time > 0:
                    logging.debug('Settings call for a transition to the new ones')
                    self._transition(settings, settings.transition_time)
                else:
                    logging.debug('Direct set without transition')
                    self.pi.set_PWM_dutycycle(self.green, settings.green)
                    self.pi.set_PWM_dutycycle(self.red, settings.red)
                    self.pi.set_PWM_dutycycle(self.blue, settings.blue)
                if settings.on_duration:
                    logging.debug('Sleeping for on_duration of {} seconds'.format(settings.on_duration))
                    gevent.sleep(settings.on_duration)
                settings = settings.next_settings
        except gevent.GreenletExit:
            logging.debug('LED settings Greenlet Terminated')

    def apply_settings(self, lightsettings):
        """
        Applies a lightsettings chain.

        Since lightsettings can be chained and looped, it is applied inside a greenlet i
        which will let the chain/loop continue apace until it is aborted or finishes.

        Calling this method again aborts any running greenlet and restarts it with new settings.
        """
        logging.debug("Applying settings: {}".format(lightsettings))
        if self.worker and not self.worker.dead:
            self.worker.kill()
        self.worker = gevent.Greenlet(
            self._set_leds, lightsettings)
        self.worker.start()
        gevent.sleep(0)
