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

if __name__ == '__main__':
    print(optimize_parameters())