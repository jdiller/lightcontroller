# -*- coding: utf-8 -*-

import logging
import gevent
import sys
import raspi
from weather import Weather
from gevent import Greenlet
from lightsettings import LightSettings


logging.basicConfig(level=logging.DEBUG)

# These are the GPIO pins that control each color
GREEN = 17
RED = 27
BLUE = 22

worker = None
pi = raspi.RasPi()

# Init the GPIO, enable pulse-width modulation for brightness
# Turn all the lights off to start
pi.set_PWM_dutycycle(RED, 0)
pi.set_PWM_dutycycle(GREEN, 0)
pi.set_PWM_dutycycle(BLUE, 0)

LightSettings.red_led = RED
LightSettings.blue_led = BLUE
LightSettings.green_led = GREEN


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
    while True:
        try:
            weather = Weather()
            settings = LightSettings()
            weather.apply_to_settings(settings)
            pi.apply_settings(settings)
            gevent.sleep(5)
        except KeyboardInterrupt:
            print "Exiting"
            sys.exit(0)
        except Exception as x:
            print x
finally:
    # try to clean everything up before exiting.
    pi.set_PWM_dutycycle(RED, 0)
    pi.set_PWM_dutycycle(BLUE, 0)
    pi.set_PWM_dutycycle(GREEN, 0)
