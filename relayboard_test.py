import time, atexit
import RPi.GPIO as GPIO

relayboardpin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(relayboardpin, GPIO.OUT)

try:
    while True:
        val = input('Enter Pin State hi/lo: ')
        print('set pin: ' + str(val))
        if val == 'hi':
            GPIO.output(relayboardpin, GPIO.HIGH)
        if val == 'lo':
            GPIO.output(relayboardpin, GPIO.LOW)
except KeyboardInterrupt:
    print('quitting')
    GPIO.cleanup()
