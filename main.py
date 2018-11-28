import RPi.GPIO as GPIO
import sys
import time

GPIO.setmode(GPIO.BOARD)

def blink_rgb_leb():
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

def read_humidity_temp():




if __name__ == "__main__":
	blink_rgb_leb()