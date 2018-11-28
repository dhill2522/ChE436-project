import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

while(True):
	GPIO.output(12, GPIO.HIGH)
	time.sleep(1)
	GPIO.output(12, GPIO.LOW)
	time.sleep(1)


