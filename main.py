import sys
import tclab
import time
import pandas as pd
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
	tc1 = tclab.TCLab()
	tc1.LED(100)
	data = pd.DataFrame()
	while True:
		tc1.Q1(45)
		tc1.Q2(80)
		try:
			# read temp and humidity
			h, t = Adafruit_DHT.read_retry(11, 4)

			# print current values
			print('{}, {}, {}, {}'.format(h, t, tc1.T1, tc1.T2))
			newData = pd.DataFrame({
				'humidity': h,
				'bow temp': t,
				'heater 1 temp': tc1.T1,
				'heater 2 temp': tc1.T2
			})
			data = data.append(newData)

			tc1.Q1()
			time.sleep(1)

		except KeyboardInterrupt:
			print('Exiting...')
			tc1.LED(0)
			data.to_excel('data.xlsx')
			print(data)
			sys.exit()
		except ValueError as err:
			# Handles cases when the heater overheats
			print(err)

if __name__ == "__main__":
	main_loop()
