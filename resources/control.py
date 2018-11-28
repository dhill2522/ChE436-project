import tclab  # pip install tclab
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.integrate import odeint



if __name__ == '__main__':
    # FOPDT model
    Tss = 23      # degC (ambient temperature)
    Qss = 0       # % heater

    K_c = 0.10
    tau_i = 148
    tau_D = 2

    # Connect to Arduino
    a = tclab.TCLab()

    # Turn LED on
    print('LED On')
    a.LED(100)

    # Run time in minutes
    run_time = 10.0

    # Number of cycles
    n = int(60.0*run_time)

    T1 = np.ones(n) * Tss
    t = np.zeros(n)
    u = np.zeros(n)
    P_array = np.zeros(n)
    I_array = np.zeros(n)
    D_array = np.zeros(n)
    err = np.zeros(n)
    sp = np.zeros(n)
    sp[0:300] = 320 - 273.15
    sp[300:600] = 315 - 273.15


    # Create plot
    plt.figure(figsize=(10, 7))
    plt.ion()
    plt.show()

    # Main Loop
    start_time = time.time()
    prev_time = start_time

    err_sum = 0
    try:
        for i in range(1, n):
            # Sleep time
            sleep_max = 1.0
            sleep = sleep_max - (time.time() - prev_time)
            if sleep >= 0.01:
                time.sleep(sleep-0.01)
            else:
                time.sleep(0.01)

            # Record time and change in time
            tn = time.time()
            prev_time = tn
            t[i] = tn - start_time
            ddt = t[i] - t[i-1]

            # Read temperatures in Kelvin
            T1[i] = a.T1
            err[i] = sp[i] - T1[i]

            # Determine the new control value
            P = K_c * err[i]
            P_array[i] = P
            I = K_c/tau_i * err_sum
            I_array[i] = I
            D = - K_c * tau_D * ddt
            D_array[i] = D

            control = (Qss + P + I + D) * 100
            control = max(0, control)
            control = min(100, control)
            u[i] = control

            a.Q1(u[i])

            err_sum += err[i]

            # Plot
            plt.clf()
            ax = plt.subplot(3, 1, 1)
            ax.grid()
            plt.plot(t[0:i], T1[0:i], 'ro')
            plt.plot(t[0:i], sp[0:i], 'b-')
            plt.ylabel('Temperature (C)')
            ax = plt.subplot(3, 1, 2)
            ax.grid()
            plt.plot(t[0:i], P_array[0:i], 'k-', label='P')
            plt.plot(t[0:i], I_array[0:i], 'b-', label='I')
            plt.plot(t[0:i], D_array[0:i], 'r-', label='D')
            plt.ylabel('Parameters')
            plt.legend()
            ax = plt.subplot(3, 1, 3)
            ax.grid()
            plt.plot(t[0:i], u[0:i], 'r-', label=r'$Q$')
            plt.ylabel('Heater output')
            plt.xlabel('Time (sec)')
            plt.draw()
            plt.pause(0.05)

        # Turn off heaters
        a.Q1(0)
        a.Q2(0)
        # Save text file
        # Save figure
        plt.savefig('control.eps', format='eps', dpi=1000)

    # Allow user to end loop with Ctrl-C
    except KeyboardInterrupt:
        # Disconnect from Arduino
        a.Q1(0)
        a.Q2(0)
        print('Shutting down')
        a.close()
        plt.savefig('control.eps', format='eps', dpi=1000)

    # Make sure serial connection still closes when there's an error
    except:
        # Disconnect from Arduino
        a.Q1(0)
        a.Q2(0)
        print('Error: Shutting down')
        a.close()
        plt.savefig('control.eps', format='eps', dpi=1000)
        raise
