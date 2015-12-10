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


def recover_last_state():
    try:
        f = open('last_state.json')
        settings = LightSettings.from_json(f.read())
        f.close()
    except IOError as x:
        logging.error(x)
        settings = None
    return settings


def persist_last_state(settings):
    try:
        f = open('last_state.json', 'w')
        f.write(settings.to_json())
        f.close()
    except IOError as x:
        logging.error(x)

# try to recover desired state from persisted message
last_state = recover_last_state()
if last_state:
    pi.apply_settings(last_state)

try:
    cp = ConfigParser()
    cp.read('config.cfg')
    dispatcher = Dispatcher(cp, pi)
    dispatcher.start()
    while True:
        try:
            gevent.sleep()
        except KeyboardInterrupt:
            print "Exiting"
            sys.exit(0)
finally:
    # try to clean everything up before exiting.
    pi.set_all_off()
