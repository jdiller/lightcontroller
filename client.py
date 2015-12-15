# -*- coding: utf-8 -*-

import logging
import gevent
import sys
from lightcontroller import raspi
from ConfigParser import ConfigParser
from lightcontroller.lightsettings import LightSettings
from lightcontroller.dispatcher import Dispatcher
logging.basicConfig(level=logging.DEBUG)


worker = None
pi = raspi.RasPi()

# Init the GPIO, enable pulse-width modulation for brightness
# Turn all the lights off to start
pi.set_all_off()

LightSettings.red_led = raspi.RED
LightSettings.blue_led = raspi.BLUE
LightSettings.green_led = raspi.GREEN

try:
    cp = ConfigParser()
    cp.read('config.cfg')
    dispatcher = Dispatcher(cp, pi)
    dispatcher.start()
    try:
        while True:
            gevent.sleep(0.1)
    except KeyboardInterrupt:
        print "Exiting..."
        dispatcher.stop()
        sys.exit(0)
finally:
    # try to clean everything up before exiting.
    pi.set_all_off()
