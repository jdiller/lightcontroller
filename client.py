# -*- coding: utf-8 -*-

import platform
import logging
import json
import gevent
import sys
import time
import requests
from gevent import monkey, Greenlet

#FORECAST_API_KEY = os.environ.get('FORECAST_API_KEY')
FORECAST_API_KEY='FORECAST_KEY'
LAT = 43.6462468
LONG = -79.3967172
BASE_URL='https://api.forecast.io/forecast/{}/{},{}?units=si'

if not FORECAST_API_KEY:
    print "Forecast API key needed."
    sys.exit(1)

# dirty hack to determine if we're actually running on the rpi
if platform.machine().startswith("arm"):
    import RPi.GPIO as g
else:
    # dev/test mode
    import MockRPi.GPIO as g

logging.basicConfig(level=logging.DEBUG)
monkey.patch_all()

# These are the GPIO pins that control each color
RED = 17
GREEN = 24
BLUE = 23

worker = None

# Init the GPIO, enable pulse-width modulation for brightness
g.setmode(g.BCM)
g.setup(RED, g.OUT)
g.setup(BLUE, g.OUT)
g.setup(GREEN, g.OUT)

PWM_FREQ = 200
red_led = g.PWM(RED, PWM_FREQ)
blue_led = g.PWM(BLUE, PWM_FREQ)
green_led = g.PWM(GREEN, PWM_FREQ)

# Turn all the lights off to start
red_led.start(0)
blue_led.start(0)
green_led.start(0)



def set_leds(leds, flash=False, onduration=1, offduration=1):
    """
    Method to turn the lights on and off. Runs in a greenlet to enable
    flashing the leds while still waiting for new messages
    """
    try:
        if flash:
            while True:
                for led, intensity in leds:
                    led.ChangeDutyCycle(intensity)
                gevent.sleep(onduration)
                for led, intensity in leds:
                    led.ChangeDutyCycle(0)
                gevent.sleep(offduration)
        else:
            for led, intensity in leds:
                led.ChangeDutyCycle(intensity)
    except gevent.GreenletExit:
        logging.debug('LED Flash Greenlet Terminated')


def get_instructions_from_message(settings):
    leds = []
    flash = settings.get('flash', False)
    onduration = settings.get('onduration', 1)
    offduration = settings.get('offduration', 1)
    if 'red' in settings:
        leds.append((red_led, float(settings['red'])))
    if 'blue' in settings:
        leds.append((blue_led, float(settings['blue'])))
    if 'green' in settings:
        leds.append((green_led, float(settings['green'])))
    return (leds, onduration, offduration, flash)


def set_lights_with_worker(leds, onduration, offduration, flash):
    global worker
    if worker and not worker.dead:
        worker.kill()
    worker = Greenlet(
        set_leds, leds,
        flash=flash,
        onduration=onduration,
        offduration=offduration
    )
    worker.start()
    gevent.sleep(0)


def recover_last_state():
    try:
        f = open('last_state.json')
        message = json.loads(f.read())
        f.close()
    except IOError as x:
        logging.error(x)
        message = None
    return message


def persist_last_state(message):
    try:
        f = open('last_state.json', 'w')
        f.write(json.dumps(message))
        f.close()
    except IOError as x:
        logging.error(x)


def get_color_for_temperature(temperature):
    #temperature colour range:
    #below -15 -> turquoise (A448FF)
    #-14 to 0 -> blue (4368E9)
    #0 to 10 -> green (4EDEA8)
    #10 to 20 -> yellow (F2FD2F)
    #20 to 30 -> orange (F8C11D)
    #over 30 -> red (FC4423)

    #map it
    temps = {
        (float("-inf"), -15) : (0xA4, 0x48, 0xFF),
        (-14.99, 0) : (0x43, 0x68, 0xE9),
        (0.01, 10)  : (0x4E, 0xDE, 0xA8),
        (10.01,20)  : (0xF2, 0xFD, 0x2F),
        (20.01,30)  : (0xF8, 0xC1, 0x1D),
        (30.01, float("inf")) : (0xFC, 0x44, 0x23)
    }
    for key, value in temps.iteritems():
        if temperature >= key[0] and temperature <= key[1]:
            return translate_color_to_message(value)

def translate_color_to_message(color):
    out = {'red'   : color[0] / 255.0 * 100,
           'green' : color[1] / 255.0 * 100,
           'blue'  : color[2] / 255.8 * 100}

    return out

def set_lights_with_weather_data(weather_data):
    current_weather = weather_data.get('currently')
    if current_weather:
        precip_probability = current_weather['precipProbability']
        precip_intensity = current_weather['precipIntensity']
        temperature = current_weather['temperature']
        temperature_color = get_color_for_temperature(temperature)
        instructions = get_instructions_from_message(temperature_color)
        set_lights_with_worker(*instructions)

# try to recover desired state from persisted message
message = recover_last_state()
if message:
    instructions = get_instructions_from_message(message)
    set_lights_with_worker(*instructions)

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
