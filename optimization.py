import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.optimize import minimize
from scipy.interpolate import interp1d


def read_data_file(file_name):
    '''Read in data from the given data file'''
    data = np.loadtxt(file_name, delimiter=',', skiprows=1)
    t = data[:, 0].T  # time array
    u = data[:, 1].T
    T = data[:, 3].T # temperature array
    return (t, u, T)


def plot_results(t, T, T_fopdt, err_fopdt, u, save_as=''):
    '''plot the given results in a standard way'''
    ax = plt.subplot(3, 1, 1)
    ax.grid()
    plt.plot(t, T, 'r.', label=r'$T$ measured')
    plt.plot(t, T_fopdt, 'b--', label=r'$T$ FOPDT')
    plt.ylabel('Temperature (K)')
    plt.legend()
    ax = plt.subplot(3, 1, 2)
    ax.grid()
    plt.plot(t, err_fopdt, 'b-', label='FOPDT')
    plt.ylabel('Cumulative Error')
    plt.legend()
    ax = plt.subplot(3, 1, 3)
    ax.grid()
    plt.plot(t, u, 'r-', label=r'$Q_1$')
    plt.ylabel('Heater output')
    plt.xlabel('Time (sec)')
    plt.legend()
    if save_as:
        plt.savefig(save_as)
    plt.show()


def FOPDT(y, t, u, coeffs, time, y0, u_array):
    '''Basic FOPDT model'''
    k, tau, theta = coeffs
    dydt = (-(y-y0) + k*(u(time-theta)-u_array[0])) / tau
    # print(coeffs, dydt, u(t-theta), t, y)
    return dydt


def fopdt_err(guesses, u, T, t, u_array):
    '''find the total error in a FOPDT simulation'''
    if guesses[0] <= 0 or guesses[1] < 0 or guesses[2] < 0:
        return 1e20
    total_err = 0
    for i, y in enumerate(T):
        y_fopdt = odeint(FOPDT, T[0], [0, 1], args=(u, guesses, t[i], T[0], u_array))[-1]
        err = (y_fopdt - y)**2
        total_err += err
        y0_fopdt = y_fopdt
    return total_err


def optimize_parameters(data_file_path):
    t, u_array, T = read_data_file(data_file_path)

    # Convert T to Kelvin from Celsius
    T = [v + 273.15 for v in T]

    # Generate the interpolated control values as a function of time
    u_i1d = interp1d(t, u_array, fill_value="extrapolate")

    def u_interp(x):
        if x < 0 or x > t[-1]:
            return 0
        return u_i1d(x) 
    
    # Set the initial guess values
    Kp = 0.29      # degC/%
    tauP = 180   # seconds
    thetaP = 20   # seconds (integer)

    # Optimize the FOPDT model
    sol = minimize(fopdt_err, (Kp, tauP, thetaP), args=(u_interp, T, t, u_array))
    print(sol)
    Kp, tauP, thetaP = sol.x
    err_fopdt = sol.fun

    print(f'Optimized FOPDT Parameters: Kp: {Kp}, tau_p: {tauP}, thetaP: {thetaP}, err: {err_fopdt}')

    # Initialize lists
    T_fopdt = [T[0]]        # temperature as predicted by standard FOPDT
    err_fopdt = [0]

    # Initialize holder variables
    T_fopdt0 = T[0]

    for i in range(1, len(t)):
        dt = t[i] - t[i-1] # time step
        T3_next = odeint(FOPDT, T_fopdt0, [0, 1], args=(u_interp, (Kp, tauP, thetaP), t[i], T[0], u_array))[-1]
        T_fopdt.append(T3_next)
        T_fopdt0 = T3_next
        err_fopdt.append(err_fopdt[-1] + abs(T3_next - T[i]))

    plot_results(t, T, T_fopdt, err_fopdt, u_array, 'optimized_run.png')
    return {'Kp': Kp, 'tauP': tauP, 'thetaP': thetaP, 'SSE': err_fopdt}


if __name__ == '__main__':
    optimize_parameters('data.csv')