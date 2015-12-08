import gevent
import platform
import logging

# dirty hack to determine if we're actually running on the rpi
if platform.machine().startswith("arm"):
    import pigpio
else:
    # dev/test mode
    import mockpigpio as pigpio

# These are the GPIO pins that control each color
GREEN = 17
RED = 27
BLUE = 22


class RasPi(object):
    leds = [RED, GREEN, BLUE]

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

    def set_all_off(self):
        for pin in RasPi.leds:
            self.set_PWM_dutycycle(pin, 0)

    def dim_all(self, percentage):
        for pin in RasPi.leds:
            current_duty_cycle = self.pi.get_PWM_dutycycle(pin)
            new_duty = current_duty_cycle * (percentage / 100)
            self.set_PWM_dutycycle(pin, new_duty)

    def _set_leds(self, settings):
        try:
            if settings.flashing:
                while True:
                    self.pi.set_PWM_dutycycle(GREEN, settings.green)
                    self.pi.set_PWM_dutycycle(RED, settings.red)
                    self.pi.set_PWM_dutycycle(BLUE, settings.blue)
                    gevent.sleep(settings.on_duration)
                    self.set_all_off()
                    gevent.sleep(settings.off_duration)
            else:
                self.pi.set_PWM_dutycycle(GREEN, settings.green)
                self.pi.set_PWM_dutycycle(RED, settings.red)
                self.pi.set_PWM_dutycycle(BLUE, settings.blue)
        except gevent.GreenletExit:
            logging.debug('LED Flash Greenlet Terminated')

    def apply_settings(self, lightsettings):
        if self.worker and not self.worker.dead:
            self.worker.kill()
        self.worker = gevent.Greenlet(
            self._set_leds, lightsettings)
        self.worker.start()
        gevent.sleep(0)
