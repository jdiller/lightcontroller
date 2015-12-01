import gevent
import platform

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

    def set_PWM_dutycycle(self, pin, dutycycle, transition_time=0):
        self.pi.set_PWM_dutycycle(pin, dutycycle)

    def _set_leds(self, settings):
        try:
            if settings.flashing:
                while True:
                    for led, intensity in settings.leds:
                        self.set_PWM_dutycycle(led, intensity)
                    gevent.sleep(settings.onduration)
                    for led, intensity in settings.leds:
                        self.set_PWM_dutyCyle(led, 0)
                    gevent.sleep(settings.offduration)
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
