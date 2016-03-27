# -*- coding: utf-8 -*-

import logging
import gevent
import sys
import threading
from lightcontroller.threading.stoppable import StoppableThread
from lightcontroller import raspi
from ConfigParser import ConfigParser
from lightcontroller.lightsettings import LightSettings
from lightcontroller.dispatcher import Dispatcher
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) [%(asctime)s]: %(message)s')


worker = None
try:
    cp = ConfigParser()
    cp.read('config.cfg')

    pi = raspi.RasPi(cp)

    # Init the GPIO, enable pulse-width modulation for brightness
    # Turn all the lights off to start
    pi.set_all_off()

    dispatcher = Dispatcher(cp, pi)
    dispatcher.start()
    try:
        while True:
            gevent.sleep(10)
    except KeyboardInterrupt:
        print "Exiting..."
        dispatcher.stop()
        for thread in threading.enumerate():
            if isinstance(thread, StoppableThread):
                thread.stop()
                thread.join()
        sys.exit(0)
finally:
    # try to clean everything up before exiting.
    pi.set_all_off()
