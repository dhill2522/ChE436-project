import sys
import tclab
import time
import numpy as np
import Adafruit_DHT


def blink_rgb_leb():
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BOARD)
	print('LED should start blinking now. Ctl-C to stop.')
	GPIO.setup(12, GPIO.OUT)

	try:
		while(True):
			GPIO.output(12, GPIO.HIGH)
			time.sleep(1)
			GPIO.output(12, GPIO.LOW)
			time.sleep(1)
		
	except KeyboardInterrupt:
		sys.exit()


if __name__ == "__main__":
	pass