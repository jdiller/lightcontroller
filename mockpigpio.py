class pi(object):

    def __init__(self):
        self.pins = {}

    def set_PWM_dutycycle(self, pin, cycle):
        self.pins[pin] = cycle
        print 'Pin {} Duty cycle is now {}'.format(pin, cycle)

    def get_PWM_dutycycle(self, pin):
        return self.pins.get(pin, 0)
