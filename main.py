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

def main_loop(run_time, show_plot=True):
	'''
	Run the main loop
	run_time		total run time in minutes
	show_plot		whether to show the dynamic plot of the system
	'''
	tc1 = tclab.TCLab()
	tc1.LED(100)
	data = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] # Bogus data row added to make concatenation work, never goes anywhere 
	csv_file_header = 'time, control output, box humidity, box temp, outside humidity, outside temp, heater 1 temp, heater 2 temp'

	start_time = time.time()
    
	u = 0
	Qss = 0  # 0% heater to start
	err = np.zeros(run_time*60)
	sp = np.zeros(run_time*60)
	sp[60:800] = 303.15 - 273.15 # 30 degrees C
	sp[800:1500] = 298.15 - 273.15 # 25 degrees C
	sp[1500:2100] = 310.15 - 273.15 # 37 degrees C
	sp[2100:3000] = 307.15 - 273.15 # 34 degrees C
	sp[3000:] = 300.15 - 273.15 #27 degrees C
	err_sum = 0
	prev_temp = 0
    
	i = 0

	tc1.Q1(u)
	tc1.Q2(u)
	while True:
		try:
			# read temp, humidity and time
			humid_in, temp_in = Adafruit_DHT.read_retry(11, 4, retries=5, delay_seconds=1)
			humid_out, temp_out = Adafruit_DHT.read_retry(11, 17, retries=5, delay_seconds=1)
			current_time = time.time() - start_time

			if humid_in > 100:
				# Corrupted data, so ignore it
				continue

			# PID controller to determine u
			print("i", i)

			err[i] = sp[i] - temp_in

			print("error", err[i])

			ddt = temp_in - prev_temp
          
			Kc = 1.44
			tau_I = 221.925
			tau_D = 44.898

			P = Kc * err[i]
			I = Kc/tau_I * err_sum
			D = - Kc * tau_D * ddt
          
			if (i > 60):
				err_sum += err[i]

			prev_temp = temp_in
			control = (Qss + P + I + D) * 100
			control = max(0, control)
			control = min(100, control)
          
			u = control
            
			i += 1

			# Set the heater outputs
			tc1.Q1(u)
			tc1.Q2(u)

			# print current values
			print('time: {:.1f}, u: {}, h_in: {}, t_in: {}, h1: {}, h2: {}, h_out: {}, t_out: {}, P: {:.2f}, I: {:.2f}, D: {:.2f}'
         			.format(current_time, u, humid_in, temp_in, tc1.T1, tc1.T2, humid_out, temp_out, P, I, D, err))
			data = np.vstack([data, [current_time, u, humid_in,
                           temp_in, humid_out, temp_out, tc1.T1, tc1.T2, P, I, D, err[i]]])
			np.savetxt('data.csv', data[1:], delimiter=',', header=csv_file_header)
			if current_time > run_time*60:
				print('Run finished. Exiting...')
				tc1.LED(0)
				sys.exit()

		except KeyboardInterrupt:
			print('Exiting...')
			tc1.LED(0)
			sys.exit()
		except ValueError as error:
			# Handles cases when the heater overheats
			print(error)

if __name__ == "__main__":
	main_loop(60)