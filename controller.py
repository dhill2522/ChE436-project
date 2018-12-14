import runs
import optimization as opt

class Controller(object):
    def __init__(self):
        # Initial PID and FOPDT parameters
        self.K_c = 1.44
        self.Tau_I = 221.925
        self.Tau_D = 44.898
        self.K_p = 0.14501294865265488
        self.Tau_p = 159.4251614964272
        self.Theta_P = 124.9997


    def auto_tune(self):
        # Run a step test
        print('Running a doublet test on the system...')
        runs.doublet_test(data_file='tuning_step_test.csv', show_plot=False)
        
        # Fit the FOPDT parameters
        print('Fitting FOPDT parameters to the data...')
        sol = opt.optimize_parameters('tuning_step_test.csv')
        self.K_p = sol['Kp']
        self.Tau_p = sol['tauP']
        self.Theta_P = sol['thetaP']
        
        # Determine the PID tuning parameters
        print('Determining initial PID tuning parameters')
        tau_c = max(self.Tau_p, 8*self.Theta_P)

        self.K_c = 1/self.K_p * (self.Tau_p + 0.5*self.Theta_P) / (tau_c + self.Theta_P)
        self.Tau_I = self.Tau_p + 0.5*self.Theta_P
        self.Tau_D = self.Tau_p*self.Theta_P / (2*self.Tau_p + self.Theta_P)
        return

    def run(self, run_time):
        runs.run_controller(run_time, (self.K_c, self.Tau_I, self.Tau_D))
        return
