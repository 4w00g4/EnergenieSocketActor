#!/usr/bin/python
#import the required modules
import RPi.GPIO as GPIO
import time
import argparse
import logging

from modules import cbpi
from modules.core.hardware import ActorBase, SensorPassive, SensorActive
from modules.core.props import Property

global SWITCHES
SWITCHES = {}
global IO_MAPPING 
#IO_MAPPING = [13,16,15,11] # PINS
IO_MAPPING = [27,23,22,17]  # BCM
# PIN   GPIO
# 13    27
# 16    23
# 15    22
# 11    17


def EnableConsoleDebugLogging():
    logging.basicConfig(level=logging.DEBUG)

def action(code):
    i=3
    for bit in list(reversed(code)):
        logging.debug("Setting Pin {n} to {b} (bit={r})".format(n=IO_MAPPING[i], b=(bit=='1'), r=bit))
        GPIO.output(IO_MAPPING[i], bit=='1')
        i-=1
    time.sleep(0.1)
    logging.debug("Firing...")
    GPIO.output(25, True)
    time.sleep(0.25)
    logging.debug("Stopping...")
    GPIO.output(25, False)

class Switch(object):
    def __init__(self, number, oncode, offcode):
        self.number = number
        self.oncode = oncode
        self.offcode = offcode

    def turn_on(self):
        logging.debug("Turning ON switch {n} with code {c}".format(c=self.oncode, n=self.number))
        action(self.oncode)
        logging.debug("Complete")

    def turn_off(self):
        logging.debug("Turning OFF switch {n} with code {c}".format(c=self.offcode, n=self.number))
        action(self.offcode)
        logging.debug("Complete")

def initialise_board():
    logging.debug("Initialising...")
    GPIO.setmode(GPIO.BCM)
    for o in IO_MAPPING:
        GPIO.setup(o, GPIO.OUT)

#    GPIO.setup(18, GPIO.OUT)    # PIN
    GPIO.setup(24, GPIO.OUT)    # BCM
#    GPIO.setup(22, GPIO.OUT)    # PIN
    GPIO.setup(25, GPIO.OUT)    # BCM
#    GPIO.output(22, False)      # PIN
    GPIO.output(25, False)      # BCM
#    GPIO.output(18, False)      # PIN
    GPIO.output(24, False)      # BCM
    for o in IO_MAPPING:
        GPIO.output(o, False)

def load_switch_definitions():
    logging.debug("Creating dictionary of switches")
    global SWITCHES
    SWITCHES[1] = Switch(1, '1111', '0111')
    SWITCHES[2] = Switch(2, '1110', '0110')
    SWITCHES[3] = Switch(3, '1101', '0101')
    SWITCHES[4] = Switch(4, '1100', '0100')
    SWITCHES[0] = Switch('ALL', '1011', '0011')
    logging.debug("Ready")

def switch(number, on, off):
    if on and off:
        logging.error("Cannot switch both on and off")
        return False
    if not on and not off:
        logging.error("Nothing to do: on and off both false")
        return False
    if on:
        SWITCHES[number].turn_on()
    if off:
        SWITCHES[number].turn_off()

def setup_switch(number):
    logging.debug("Setting up switch {n}".format(n=number))
    switch(number, True, False)
    time.sleep(0.25)
    switch(number, False, True)
    time.sleep(0.25)
    switch(0, True, False)
    time.sleep(0.25)
    switch(0, False, True)
    time.sleep(0.25)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control Energenie switches")
    parser.add_argument("number", help="Switch number", type=int)
    parser.add_argument("--on", action="store_true", default=False)
    parser.add_argument("--off", action="store_true", default=False)
    parser.add_argument("--debug", action="store_true", default=False)
    args=parser.parse_args()

    if args.debug:
        EnableConsoleDebugLogging()

    load_switch_definitions()
    if len(SWITCHES) < args.number -1:
        logging.error("Cannot control switch {n} - only {c} defined".format(n=args.number, c=len(SWITCHES)))
        sys.exit(1)

    switch(args.number, args.on, args.off)
    GPIO.cleanup()

load_switch_definitions()
initialise_board()

@cbpi.actor
class EnergenieSocket(ActorBase):
    socket = Property.Select("socket", options=[0,1,2,3,4])

    @classmethod
    def init_global(cls):
        pass

    def on(self, power=100):
        switch(int(self.socket), True, False)

    def off(self):
        switch(int(self.socket), False, True)


