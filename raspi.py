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

    def __init__(self):
        self.pi = pigpio.pi()
        self.worker = None
        self.gentle_transitions = True

    def set_PWM_dutycycle(self, pin, dutycycle):
        if not self.gentle_transitions:
            self.pi.set_PWM_dutycycle(pin, dutycycle)
        else:
            current_cycle = self.pi.get_PWM_dutycycle(pin)
            direction = 1 if dutycycle > current_cycle else -1
            for x in range(int(current_cycle), int(dutycycle) + direction, direction):
                self.pi.set_PWM_dutycycle(pin, x)
                gevent.sleep(0.01)

    def _set_leds(self, settings):
        try:
            if settings.flashing:
                while True:
                    for led, intensity in settings.leds:
                        self.set_PWM_dutycycle(led, intensity)
                    gevent.sleep(settings.on_duration)
                    for led, intensity in settings.leds:
                        self.set_PWM_dutycycle(led, 0)
                    gevent.sleep(settings.off_duration)
            else:
                for led, intensity in settings.leds:
                    self.set_PWM_dutycycle(led, intensity)
        except gevent.GreenletExit:
            logging.debug('LED Flash Greenlet Terminated')

    def apply_settings(self, lightsettings):
        if self.worker and not self.worker.dead:
            self.worker.kill()
        self.worker = gevent.Greenlet(
            self._set_leds, lightsettings)
        self.worker.start()
        gevent.sleep(0)
