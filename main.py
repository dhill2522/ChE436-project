import sys
import tclab
import time

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

def main_loop():
	try:
		tc1 = tclab.TCLab()
		tc1.LED(100)
		while True:
			tc1.Q1(80)
			tc1.Q2(100)
			# read temp and humidity
			h, t = Adafruit_DHT.read_retry(11, 4)

			# print current values
			print('{}, {}, {}, {}'.format(h, t, tc1.T1, tc1.T2))
			time.sleep(1)

	except KeyboardInterrupt:
		print('Exiting...')
		sys.exit()

if __name__ == "__main__":
	main_loop()
