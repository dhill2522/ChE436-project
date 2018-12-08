import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# define energy balance model
def heat(x,t,Q):
    # Parameters
    
    #Box dimensions:
    L = .226   #m
    H = .18  #m
    W = .16  #m
    Atot = (2*W*H + 2*L*W + 2*L*H) #m^2
    Aexposed = Atot - L*W          #m^2
    thickness = 0.0001             #m
    
    Ta = 25 + 273.15   # K
    dens_air = 0.9815   # kg/m^3 ()
    m = dens_air*L*H*W     # kg
    Cp = 1.006 * 1000.0  # J/kg-K
    k_box = 0.21         #W/m-K 
    
    h1 = 1.0           # W/m^2-K
    h2 = 1.0           # W/m^2-K
    R = ((1/h1/Atot) + (thickness/Atot/k_box) + (1/h2/Aexposed)) #W/K

    # Temperature State 
    T = x[0]

    # Nonlinear Energy Balance
    dTdt = (1.0/(m*Cp))*((Ta-T)/R + Q)
    return dTdt

Q = 1  #W
T0 = 25.0 + 273.15 # Initial temperature
n = 60*10+1  # Number of second time points (10min)
time = np.linspace(0,n-1,n) # Time vector
T = odeint(heat,300.0,time,args=(Q,)) # Integrate ODE

# Plot results
plt.figure(1)
plt.plot(time/60.0,T-273.15,'b-')
plt.ylabel('Temperature (degC)')
plt.xlabel('Time (min)')
plt.legend(['Step Test (0-100% heater)'])
plt.show()
