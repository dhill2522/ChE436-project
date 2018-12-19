import sys
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import odeint

def first_principles(T, t, u, parameters, T_ambient):
    '''first-principles model for the system'''

    # Appriximated parameters for the system
    UA, alpha = parameters

    # Box dimentions
    L = 0.24
    H = 0.07
    W = 0.15
    dens_air = 0.9815   # kg/m^3 ()
    m = dens_air*L*H*W     # kg
    Cp = 1.006 * 1000.0  # J/kg-K
    
    # Nonlinear Energy Balance
    dTdt = (1.0/(m*Cp))*((T_ambient - T)/UA + alpha*u)
    return dTdt


def model_error(guesses, data_file):
    '''find the total error in a first-principles simulation'''
    total_err = 0
    data = np.loadtxt(data_file, delimiter=',')
    y0 = data[0][3]
    for i, row in enumerate(data):
        y_model = odeint(first_principles, y0, [0, 1], args=(
            row[1], guesses, row[5]))
        err = (y_model[-1] - row[3])**2
        total_err += err
        y0 = y_model[-1]
    return total_err


def optimize_parameters(parameters=[95, 1.95e-3], data_file='data.csv'):
    '''optimize parameters for the first-principles model'''
    sol = minimize(model_error, parameters, args=(data_file))
    return {'UA': sol.x[0], 'alpha': sol.x[1], 'SSE': sol.fun}


def run_model(run_time, PID_parameters, FP_parameters, data_file='data.csv'):
    '''Run a controller on the first-principles model

    run_time:        total run time in minutes

    PID_parameters:  PID parameters as (K_c, tau_I, tau_D)
    
    FP_parameters:   FP parameters as (UA, alpha)
    
    data_file:       Where to store the run data
    '''
    Kc, tau_I, tau_D = PID_parameters
    # Bogus data row added to make concatenation work, never goes anywhere
    data = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 0]]
    csv_file_header = 'time,control output,box humidity,box temp,outside humidity,outside temp,heater 1 temp,heater 2 temp,P,I,D,SP,Err'

    # Initialize variables
    u = 0
    Qss = 0  # 0% heater to start
    i = 0
    err = np.zeros(run_time*60)
    sp = np.ones(run_time*60)*25
    err_sum = 0
    max_err_sum = 5
    current_time = 0
    prev_temp = 25
    new_temp = 25

    # Set up the set point
    sp[60:800] = 303.15 - 273.15  # 30 degrees C
    sp[800:] = 298.15 - 273.15  # 25 degrees C
    sp[1500:2100] = 310.15 - 273.15  # 37 degrees C
    sp[2100:3000] = 307.15 - 273.15  # 34 degrees C
    sp[3000:] = 300.15 - 273.15  # 27 degrees C

    # Main Loop
    while current_time < run_time*60:
        # read temp, humidity and time
        humid_in, temp_in = (0, new_temp)
        humid_out, temp_out = (0, 25)
        current_time += 1  # Approximates the time change with 1 second

        err[i] = sp[i] - temp_in
        ddt = temp_in - prev_temp

        # PID controller to determine u
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

        new_temp = odeint(first_principles, prev_temp, [
                    0, current_time - data[-1][0]], args=(u, FP_parameters, temp_out))[-1][0]

        # print current values
        print('time: {:.1f}, u: {:.2f} \tt_in: {:.2f}, t_out: {}, P: {:.2f}, I: {:.2f}, D: {:.2f} \tSP: {:.2f}, err: {:.2f}'
                .format(current_time, u, temp_in, temp_out, P, I, D, sp[i], err[i]))
        data = np.vstack([data, [current_time, u, humid_in,
                                    temp_in, humid_out, temp_out, 0, 0, P, I, D, sp[i], err[i]]])
        np.savetxt(data_file, data[1:],
                    delimiter=',', header=csv_file_header)
        i += 1

    print('Run Finished.')
    return


if __name__ == '__main__':
    print(optimize_parameters())
