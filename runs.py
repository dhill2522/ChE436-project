import tclab
import time
import numpy as np
import sys
from scipy.integrate import odeint
import first_principles_model as fp

def run_model(run_time, PID_parameters, FP_parameters, data_file='data.csv'):
    '''Run a controller on the first-principles model
    run_time        total run time in minutes
    PID_parameters  PID parameters as (K_c, tau_I, tau_D)
    FP_parameters   FP parameters as (UA, alpha)
    data_file       Where to store the run data
    '''
    Kc, tau_I, tau_D = PID_parameters
    # Bogus data row added to make concatenation work, never goes anywhere
    data = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    csv_file_header = 'time,control output,box humidity,box temp,outside humidity,outside temp,heater 1 temp,heater 2 temp,P,I,D,SP,Err'

    u = 0
    Qss = 0  # 0% heater to start
    err = np.zeros(run_time*60+1)
    sp = np.zeros(run_time*60+1)
    sp[60:800] = 303.15 - 273.15  # 30 degrees C
    sp[800:1500] = 298.15 - 273.15  # 25 degrees C
    sp[1500:2100] = 310.15 - 273.15  # 37 degrees C
    sp[2100:3000] = 307.15 - 273.15  # 34 degrees C
    sp[3000:] = 300.15 - 273.15  # 27 degrees C
    temp_in_array = [25]
    err_sum = 0
    prev_temp = 0

    i = 0

    max_err_sum = 5

    while True:
        try:
            # read temp, humidity and time
            humid_in, temp_in = (0, temp_in_array[i])
            humid_out, temp_out = (0, 25)
            current_time = i # Approximates the time change with 1 second

            # PID controller to determine u
            print("i", i)

            err[i] = sp[i] - temp_in

            print("error", err[i])

            ddt = temp_in - prev_temp

            P = Kc * err[i]
            I = Kc/tau_I * err_sum
            D = - Kc * tau_D * ddt

            if (i > 60):
                err_sum += err[i]

            if err_sum > max_err_sum:
                err_sum = max_err_sum

            prev_temp = temp_in
            u = (Qss + P + I + D) * 100
            u = max(0, u)
            u = min(100, u)

            dT = odeint(fp.first_principles, temp_in_array[i], [
                        0, current_time - data[-1][0]], args=(u, FP_parameters, temp_out))[-1][0]
            print('dT:', dT)
            temp_in_array.append(temp_in_array[-1]+dT)

            i += 1

            # print current values
            print('time: {:.1f}, u: {}, h_in: {}, t_in: {}, h1: {}, h2: {}, h_out: {}, t_out: {}, P: {:.2f}, I: {:.2f}, D: {:.2f}'
                    .format(current_time, u, humid_in, temp_in, 'NA', 'NA', humid_out, temp_out, P, I, D, sp[i], err))
            data = np.vstack([data, [current_time, u, humid_in,
                                        temp_in, humid_out, temp_out, 0, 0, P, I, D, err[i]]])
            np.savetxt(data_file, data[1:],
                        delimiter=',', header=csv_file_header)
            if current_time > run_time*60:
                print('Run finished. Exiting...')
                sys.exit()

        except KeyboardInterrupt:
            print('Exiting...')
            sys.exit()

def doublet_test(data_file='step_test.csv', show_plot=True):
    '''doublet test the system and save data to given file path'''
    import Adafruit_DHT # Only importable on the Pi itself

    tc1 = tclab.TCLab()
    tc1.LED(100)
    # Bogus data row added to make concatenation work, never goes anywhere
    data = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    csv_file_header = 'time,control output,box humidity,box temp,outside humidity,outside temp,heater 1 temp,heater 2 temp,P,I,D,SP,Err'

    start_time = time.time()

    u = 0
    tc1.Q1(u)
    tc1.Q2(u)
    current_time = 0
    while current_time < 1200:
        try:
            # read temp, humidity and time
            humid_in, temp_in = Adafruit_DHT.read_retry(
                11, 4, retries=5, delay_seconds=1)
            humid_out, temp_out = Adafruit_DHT.read_retry(
                11, 17, retries=5, delay_seconds=1)
            current_time = time.time() - start_time

            if humid_in is None:
                # Rejects failed readings
                continue

            if humid_in > 100:
                # Corrupted data, so ignore it
                continue

            if current_time > 60:
                u = 100

            if current_time > 800:
                u = 50

            tc1.Q1(u)
            tc1.Q2(u)

            # print current values
            print('time: {:.1f}, u: {}, h_in: {}, t_in: {}, h1: {}, h2: {}, h_out: {}, t_out: {}, P: {:.2f}, I: {:.2f}, D: {:.2f}'
                    .format(current_time, u, humid_in, temp_in, tc1.T1, tc1.T2, humid_out, temp_out, P, I, D, sp[i], err))
            data = np.vstack([data, [current_time, u, humid_in,
                                        temp_in, humid_out, temp_out, tc1.T1, tc1.T2, P, I, D, err[i]]])
            np.savetxt(data_file, data[1:],
                        delimiter=',', header=csv_file_header)
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

def run_controller(run_time, show_plot=True):
    '''
    Run the main loop
    run_time		total run time in minutes
    show_plot		whether to show the dynamic plot of the system
    '''
    import Adafruit_DHT  # Only importable on the Pi itself

    tc1 = tclab.TCLab()
    tc1.LED(100)
    # Bogus data row added to make concatenation work, never goes anywhere
    data = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    csv_file_header = 'time,control output,box humidity,box temp,outside humidity,outside temp,heater 1 temp,heater 2 temp,P,I,D,SP,Err'

    start_time = time.time()

    u = 0
    Qss = 0  # 0% heater to start
    err = np.zeros(run_time*60)
    sp = np.zeros(run_time*60)
    sp[10:300] = 303.15 - 273.15  # 30 degrees C
    sp[300:550] = 298.15 - 273.15  # 25 degrees C
    sp[550:800] = 307.15 - 273.15  # 34 degrees C
    sp[800:] = 300.15 - 273.15  # 27 degrees C
    integral_err_sum = 0
    u_max = 100
    u_min = 0
    prev_temp = 0
    prev_time = start_time

    i = 0

    tc1.Q1(u)
    tc1.Q2(u)

    while True:
        try:
            # read temp, humidity and time
            humid_in, temp_in = Adafruit_DHT.read_retry(
                11, 4, retries=5, delay_seconds=1)
            humid_out, temp_out = Adafruit_DHT.read_retry(
                11, 17, retries=5, delay_seconds=1)
            current_time = time.time() - start_time
            dtime = current_time - prev_time

            if (humid_in is None) or (humid_out is None):
                # Rejects failed readings
                continue

            if humid_in > 100:
                # Corrupted data, so ignore it
                continue

            # PID controller to determine u
            print("i", i)

            err[i] = sp[i] - temp_in
            if i > 10:
                integral_err_sum = integral_err_sum + err[i] * dtime

            print("error", err[i])

            ddt = temp_in - prev_temp

            Kc = 1.44
            tau_I = 221.925
            tau_D = 44.898

            P = Kc * err[i]
            I = Kc/tau_I * integral_err_sum
            D = - Kc * tau_D * ddt

            prev_temp = temp_in

            u = (Qss + P + I + D) * 100

            if i > 10:

                if u > u_max:
                    u = u_max
                    integral_err_sum = integral_err_sum - err[i] * dtime
                if u < u_min:
                    u = u_min
                    integral_err_sum = integral_err_sum - err[i] * dtime

            i += 1
            prev_time = current_time
            # Set the heater outputs
            tc1.Q1(u)
            tc1.Q2(u)

            # print current values
            print('time: {:.1f}, u: {}, h_in: {}, t_in: {}, h1: {}, h2: {}, h_out: {}, t_out: {}, P: {:.2f}, I: {:.2f}, D: {:.2f}'
                    .format(current_time, u, humid_in, temp_in, tc1.T1, tc1.T2, humid_out, temp_out, P, I, D, sp[i], err))
            data = np.vstack([data, [current_time, u, humid_in,
                                        temp_in, humid_out, temp_out, tc1.T1, tc1.T2, P, I, D, sp[i], err[i]]])
            np.savetxt('data.csv', data[1:],
                        delimiter=',', header=csv_file_header)
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
