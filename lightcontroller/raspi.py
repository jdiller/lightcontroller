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

    def __init__(self, config):
        self.green = config.getint('raspi', 'green')
        self.red = config.getint('raspi', 'red')
        self.blue = config.getint('raspi', 'blue')
        self.leds = [self.red, self.green, self.blue]
        self.pi = pigpio.pi()
        self.worker = None

    def get_PWM_dutycycle(self, pin):
        return self.pi.get_PWM_dutycycle(pin)

    def set_PWM_dutycycle(self, pin, dutycycle):
        self.pi.set_PWM_dutycycle(pin, dutycycle)

    def set_all_off(self):
        for pin in self.leds:
            self.set_PWM_dutycycle(pin, 0)

    def get_current_dutycycles(self):
        for led in self.leds:
            yield self.get_PWM_dutycycle(led)

    def dim_all(self, percentage):
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
        if self.worker and not self.worker.dead:
            self.worker.kill()
        self.worker = gevent.Greenlet(
            self._set_leds, lightsettings)
        self.worker.start()
        gevent.sleep(0)
