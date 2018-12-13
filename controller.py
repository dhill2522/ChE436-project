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
        pass
        # Run a step test
        # main.main_loop(60)
        # Fit the FOPDT parameters
        # Determine the PID tuning parameters
        # Return PID parameters
