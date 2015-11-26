# -*- coding: utf-8 -*-

import platform
import logging
import json
import gevent
import sys
import time
import requests
from gevent import monkey, Greenlet
from lightsettings import LightSettings

#FORECAST_API_KEY = os.environ.get('FORECAST_API_KEY')
FORECAST_API_KEY = 'FORECAST_KEY'
LAT = 43.6462468
LONG = -79.3967172
BASE_URL = 'https://api.forecast.io/forecast/{}/{},{}?units=si'

if not FORECAST_API_KEY:
    print "Forecast API key needed."
    sys.exit(1)

# dirty hack to determine if we're actually running on the rpi
if platform.machine().startswith("arm"):
    import pigpio
else:
    # dev/test mode
    import MockRPi.GPIO as g

logging.basicConfig(level=logging.DEBUG)
monkey.patch_all()

# These are the GPIO pins that control each color
GREEN = 17
RED = 27
BLUE = 22

worker = None
pi = pigpio.pi()

# Init the GPIO, enable pulse-width modulation for brightness
pi.set_mode(GREEN, pigpio.OUTPUT)
pi.set_mode(RED, pigpio.OUTPUT)
pi.set_mode(BLUE, pigpio.OUTPUT)

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
                for led, intensity in leds:
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


def get_color_for_temperature(temperature):
    # temperature colour range:
    # below -15 -> turquoise (A448FF)
    #-14 to 0 -> blue (4368E9)
    # 0 to 10 -> green (4EDEA8)
    # 10 to 20 -> yellow (F2FD2F)
    # 20 to 30 -> orange (F8C11D)
    # over 30 -> red (FC4423)

    # map it
    temps = {
        (float("-inf"), -15): (0xA4, 0x48, 0xFF),
        (-14.99, 0): (0x43, 0x68, 0xE9),
        (0.01, 10): (0x4E, 0xDE, 0xA8),
        (10.01, 20): (0xF2, 0xFD, 0x2F),
        (20.01, 30): (0xF8, 0xC1, 0x1D),
        (30.01, float("inf")): (0xFC, 0x44, 0x23)
    }
    for key, value in temps.iteritems():
        if temperature >= key[0] and temperature <= key[1]:
            return value


def set_lights_with_weather_data(weather_data):
    current_weather = weather_data.get('currently')
    if current_weather:
        precip_probability = current_weather['precipProbability']
        precip_intensity = current_weather['precipIntensity']
        temperature = current_weather['temperature']
        temperature_color = get_color_for_temperature(temperature)
        settings = LightSettings(color=temperature_color)

        if precip_intensity > 0:
            settings.flashing = True
            settings.on_duration = 1
            settings.off_duration = 1

        if precip_probability > 30:
            settings.flashing = True
            settings.on_duration = 4
            settins.off_duration = 0.5

        #cut intensity so things aren't so bright
        settings.red /= 2.5
        settings.blue /= 2.5
        settings.green /= 2.5
        set_lights_with_worker(settings)

# try to recover desired state from persisted message
last_state = recover_last_state()
if last_state:
    set_lights_with_worker(last_state)

try:
    while True:
        try:
            fcast_url = BASE_URL.format(FORECAST_API_KEY, LAT, LONG)
            try:
                r = requests.get(fcast_url)
                weather_data = r.json()
                set_lights_with_weather_data(weather_data)
                gevent.sleep(100)
            except Exception as x:
                print x
        except KeyboardInterrupt:
            print "Exiting"
            sys.exit(0)
finally:
    # try to clean everything up before exiting.
    # turn the lights off and relinquish control of the GPIO pins
    red_led.stop()
    green_led.stop()
    blue_led.stop()
    g.cleanup()
