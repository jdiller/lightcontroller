BCM = 1
OUT = 1

class Pin(object):
    counter = 1
    def __init__(self):
        self.id = Pin.counter
        Pin.counter += 1

    def ChangeDutyCycle(self, cycle):
        print 'Pin {} Duty cycle is now {}'.format(self.id, cycle)
        pass

    def stop(self):
        print 'Pin {} Stopped'.format(self.id)
        pass

    def start(self, dutycycle):
        print 'Pin {} Started'.format(self.id)
        pass

def setmode(mode):
    pass

def setup(pin, pinmode):
    pass

def PWM(pin, cycle):
    return Pin()

def cleanup():
    pass
