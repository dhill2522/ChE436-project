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

def main_loop():
	tc1 = tclab.TCLab()
	tc1.LED(100)
	data = [1, 1, 1, 1, 1, 1, 1, 1] # Bogus data row added to make concatenation work, never goes anywhere 
	csv_file_header = 'time, control output, box humidity, box temp, outside humidity, outside temp, heater 1 temp, heater 2 temp'

	start_time = time.time()
	u = 0
	tc1.Q1(u)
	tc1.Q2(u)
	while True:
		try:
			# read temp, humidity and time
			humid_in, temp_in = Adafruit_DHT.read_retry(11, 4, retries=5, delay_seconds=1)
			humid_out, temp_out = Adafruit_DHT.read_retry(11, 17, retries=5, delay_seconds=1)
			current_time = time.time() - start_time

			# FIXME: Add PID controller here to determine u
			if current_time > 60:
				u = 100

			# Set the heater outputs
			tc1.Q1(u)
			tc1.Q2(u)

			# print current values
			print('time: {:.1f}, u: {}, h_in: {}, t_in: {}, h1: {}, h2: {}, h_out: {}, t_out: {}'.format(current_time, u, humid_in, temp_in, tc1.T1, tc1.T2, humid_out, temp_out))
			data = np.vstack([data, [current_time, u, humid_in,
                           temp_in, humid_out, temp_out, tc1.T1, tc1.T2]])
			np.savetxt('data.csv', data[1:], header=csv_file_header)

		except KeyboardInterrupt:
			print('Exiting...')
			tc1.LED(0)
			sys.exit()
		except ValueError as err:
			# Handles cases when the heater overheats
			print(err)

if __name__ == "__main__":

	main_loop()
