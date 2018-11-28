import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.optimize import minimize, Bounds
from scipy.interpolate import interp1d


def read_data_file(file_name):
    '''Read in data from the given data file'''
    data = np.loadtxt(file_name, delimiter=',', skiprows=1)
    t = data[:, 0].T  # time array
    u = data[:, 1].T  # control output
    T = data[:, 3].T # temperature array
    return (t, u, T)


def plot_results(t, T, T_eb, T_eb_nr, T_fopdt, err_db, err_eb_nr, err_fopdt, u, save_as=''):
    '''plot the given results in a standard way'''
    ax = plt.subplot(3, 1, 1)
    ax.grid()
    plt.plot(t, T, 'r.', label=r'$T$ measured')
    plt.plot(t, T_eb, 'k:', label=r'$T$ balance')
    plt.plot(t, T_eb_nr, 'g--', label=r'$T$ balance w/o radiation')
    plt.plot(t, T_fopdt, 'b--', label=r'$T$ FOPDT')
    plt.ylabel('Temperature (K)')
    plt.legend()
    ax = plt.subplot(3, 1, 2)
    ax.grid()
    plt.plot(t, err_eb, 'k-', label='Energy Balance')
    plt.plot(t, err_eb_nr, 'g-', label='Energy Balance w/o radiation')
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


def heat(y, t, u, params, include_radiation=True):
    '''First-principles non-linear heater energy balance'''
    # Parameters
    h, alpha = params  # W/m^2-K, W / % heater
    Ta = 23 + 273.15   # K
    m = 4.0/1000.0     # kg
    Cp = 0.5 * 1000.0  # J/kg-K
    A = 12.0 / 100.0**2  # Area in m^2
    eps = 0.9          # Emissivity
    sigma = 5.67e-8    # Stefan-Boltzman
    radiation = 0

    if include_radiation:
        radiation = eps * sigma * A * (Ta**4 - y**4)

    # Nonlinear Energy Balance
    return (1.0/(m*Cp))*(h*A*(Ta-y) + radiation + alpha*u)


def heat_err(guesses, u, include_radiation=True):
    '''find the total error in a first-principles simulation'''
    total_err = 0
    y0_heat = T[0]
    for i, y in enumerate(T):
        y_fopdt = odeint(heat, y0_heat, [0, 1], args=(
            u[i], guesses, include_radiation))
        err = (y_fopdt[-1] - y)**2
        total_err += err
        y0_heat = y_fopdt[-1]
    return total_err


def FOPDT(y, t, u, coeffs, time):
    '''Basic FOPDT model'''
    k, tau, theta = coeffs
    dydt = (-(y-T[0]) + k*(u(time-theta)-u_array[0])) / tau
    # print(coeffs, dydt, u(t-theta), t, y)
    return dydt


def fopdt_err(guesses, u):
    '''find the total error in a FOPDT simulation'''
    if guesses[0] <= 0 or guesses[1] < 0 or guesses[2] < 0:
        return 1e20
    total_err = 0
    y0_fopdt = T[0]
    for i, y in enumerate(T):
        y_fopdt = odeint(FOPDT, y0_fopdt, [0, 1], args=(u, guesses, t[i]))[-1]
        err = (y_fopdt - y)**2
        total_err += err
        y0_fopdt = y_fopdt
    return total_err

if __name__ == '__main__':
    t, u_array, T = read_data_file('data.txt')
    
    # Convert T to Kelvin from Celsius
    T = [v + 273.15 for v in T]

    # Generate the interpolated control values as a function of time
    u_i1d = interp1d(t, u_array)

    def u_interp(x):
        if x < 0 or x > t[-1]:
            return 0
        return u_i1d(x) 
    
    # Set the initial guess values
    Kp = 0.29      # degC/%
    tauP = 180   # seconds
    thetaP = 20   # seconds (integer)
    h = 10
    alpha = 0.009

    T_ss = 23      # degC (ambient temperature)
    Q_ss = 0       # % heater
    
    run_time = 30     # total runtime in minutes
    n = run_time*60   # number of iteration, one per second

    # Optimize the first-principles model with radiation included
    sol = minimize(heat_err, (h, alpha), args=(u_array, True))
    print(sol)
    h_rad, alpha_rad = sol.x
    rad_error = sol.fun

    # Optimize the first-principles model without radiation
    sol = minimize(heat_err, (h, alpha), args=(u_array, False))
    print(sol)
    h_nrad, alpha_nrad = sol.x
    nrad_error = sol.fun

    # Optimize the FOPDT model
    sol = minimize(fopdt_err, (Kp, tauP, thetaP), args=(u_interp))
    print(sol)
    Kp, tauP, thetaP = sol.x
    err_fopdt = sol.fun

    print(
        f'Optimized FP w/o radiation parameters: alpha: {alpha_nrad}, h: {h_nrad}, err: {nrad_error}')
    print(
        f'Optimized FP with radiation parameters: alpha: {alpha_rad}, h: {h_rad}, err: {rad_error}')
    print(f'Optimized FOPDT Parameters: Kp: {Kp}, tau_p: {tauP}, thetaP: {thetaP}, err: {err_fopdt}')

    # Initialize lists
    T_fopdt = [T[0]]        # temperature as predicted by standard FOPDT
    T_eb = [T[0]]           # temperature as predicted by energy balance
    T_eb_nr = [T[0]]        # temperature as predicted by energy balance without radiation
    err_eb = [0]         # energy balance error
    err_eb_nr = [0]      # energy balance without radiation error
    err_fopdt = [0]

    # Initialize holder variables
    T_fopdt0 = T[0]
    T_eb0 = T[0]
    T_eb_nr0 = T[0]


    for i in range(1, n-1):
        dt = t[i] - t[i-1] # time step
        # Simulate energy balance with radiation
        T1_next = odeint(heat, T_eb0, [t[i-1], t[i]], args=(u_array[i], (h_rad, alpha_rad), True))[-1]
        T_eb.append(T1_next)
        T_eb0 = T1_next
        err_eb.append(err_eb[-1] + abs(T1_next - T[i]))

        # Simulate energy balace without radiation
        T2_next = odeint(heat, T_eb_nr0, [t[i-1], t[i]], args=(u_array[i], (h_nrad, alpha_nrad), False))[-1]
        T_eb_nr.append(T2_next)
        T_eb_nr0 = T2_next
        err_eb_nr.append(err_eb_nr[-1] + abs(T2_next - T[i]))

        T3_next = odeint(FOPDT, T_fopdt0, [0, 1], args=(u_interp, (Kp, tauP, thetaP), t[i]))[-1]
        T_fopdt.append(T3_next)
        T_fopdt0 = T3_next
        err_fopdt.append(err_fopdt[-1] + abs(T3_next - T[i]))

    plot_results(t, T, T_eb, T_eb_nr, T_fopdt, err_eb, err_eb_nr, err_fopdt, u_array, 'optimized_run.png')

