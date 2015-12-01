# -*- coding: utf-8 -*-

import platform
import logging
import gevent
import sys
from weather import Weather
from gevent import Greenlet
from lightsettings import LightSettings


# dirty hack to determine if we're actually running on the rpi
if platform.machine().startswith("arm"):
    import pigpio
else:
    # dev/test mode
    import mockpigpio as pigpio

logging.basicConfig(level=logging.DEBUG)

# These are the GPIO pins that control each color
GREEN = 17
RED = 27
BLUE = 22

worker = None
pi = pigpio.pi()

# Init the GPIO, enable pulse-width modulation for brightness
# Turn all the lights off to start
pi.set_PWM_dutycycle(RED, 0)
pi.set_PWM_dutycycle(GREEN, 0)
pi.set_PWM_dutycycle(BLUE, 0)

LightSettings.red_led = RED
LightSettings.blue_led = BLUE
LightSettings.green_led = GREEN


def set_leds(settings):
    """
    Method to turn the lights on and off. Runs in a greenlet to enable
    flashing the leds while still waiting for new messages
    """
    try:
        if settings.flashing:
            while True:
                for led, intensity in settings.leds:
                    pi.set_PWM_dutycycle(led, intensity)
                gevent.sleep(settings.onduration)
                for led, intensity in settings.leds:
                    pi.set_PWM_dutyCyle(led, 0)
                gevent.sleep(settings.offduration)
        else:
            for led, intensity in settings.leds:
                pi.set_PWM_dutycycle(led, intensity)
    except gevent.GreenletExit:
        logging.debug('LED Flash Greenlet Terminated')


def set_lights_with_worker(lightsettings):
    global worker
    if worker and not worker.dead:
        worker.kill()
    worker = Greenlet(
        set_leds, lightsettings)
    worker.start()
    gevent.sleep(0)


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
    set_lights_with_worker(last_state)

try:
    while True:
        try:
            weather = Weather()
            settings = LightSettings()
            weather.apply_to_settings(settings)
            set_lights_with_worker(settings)
            gevent.sleep(100)
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
