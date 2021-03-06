import logging
class pi(object):
    """
    Simulates the pigpio interface. Used for testing and when not running on an actual RasPi
    """
    def __init__(self):
        self.pins = {}

    def set_PWM_dutycycle(self, pin, cycle):
        self.pins[pin] = cycle
        logging.info('Pin {} Duty cycle is now {}'.format(pin, cycle))

    def get_PWM_dutycycle(self, pin):
        return self.pins.get(pin, 0)
