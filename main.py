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
	start_time = time.time()
	while True:
		tc1.Q1(0)
		tc1.Q2(0)
		try:
			# read temp and humidity
			h, t = Adafruit_DHT.read_retry(11, 4, retries=5, delay_seconds=1)
			h_out, t_out = Adafruit_DHT.read_retry(11, 17, retries=5, delay_seconds=1)
			if time.time() > start_time + 60:
				tc1.Q1(100)
				tc1.Q2(100)

			# print current values
			print('h_in: {}, t_in: {}, h1: {}, h2: {}, h_out: {}, t_out: {}'.format(h, t, tc1.T1, tc1.T2, h_out, t_out))
			newData = pd.DataFrame({
				'box humidity': h,
				'outside humidty': h_out,
				'box temp': t,
				'outside temp': t_out,
				'heater 1 temp': tc1.T1,
				'heater 2 temp': tc1.T2
			}, index=[1])
			data = data.append(newData)
			data.to_excel('data.xlsx')

			time.sleep(1)

		except KeyboardInterrupt:
			print('Exiting...')
			tc1.LED(0)
			sys.exit()
		except ValueError as err:
			# Handles cases when the heater overheats
			print(err)

if __name__ == "__main__":
	main_loop()
