import requests
import ast
try:
    import bluetooth
except ImportError:
    import lightcontroller.mockbluetooth as bluetooth
import threading
import logging
import time
from lightcontroller.threading.stoppable import StoppableThread
from ConfigParser import ConfigParser
from datetime import datetime

class Presence(object):
    last_presence_lock = None
    last_presence = None
    devices = None
    poll_thread = None
    timeout = 4
    poll_lock = None
    @classmethod
    def poll(cls):
        if not cls.poll_lock:
            cls.poll_lock = threading.Lock()
        while not cls.poll_thread.stopped:
            if cls.poll_lock.acquire(False):
                cls.poll_once()
                time.sleep(0.5)
                cls.poll_lock.release()

    @classmethod
    def poll_once(cls):
        for device in cls.devices:
            logging.debug("Looking for bluetooth devices to indicate presence")
            if bluetooth.lookup_name(device, timeout=cls.timeout):
                logging.debug("Presence detected ({})".format(device))
                with cls.last_presence_lock:
                    cls.last_presence = datetime.now()
                break

    def __init__(self, devices):
        Presence.devices = devices
        if Presence.poll_thread is None or not Presence.poll_thread.is_alive():
            Presence.poll_thread = StoppableThread(target=Presence.poll)
            Presence.last_presence_lock = threading.Lock()
            #hack - make one blocking poll so the initial check has a value
            if not Presence.last_presence and not Presence.poll_thread.is_alive():
                Presence.poll_once()
            Presence.poll_thread.start()

    @property
    def user_present(self):
        with Presence.last_presence_lock:
            if Presence.last_presence:
                return (datetime.now() - Presence.last_presence).seconds <= 2 * Presence.timeout
        return False

