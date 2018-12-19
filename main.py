import runs
import optimization
import first_principles_model as fp
import utils

if __name__ == "__main__":
	# sol = optimization.optimize_parameters(data_file_path='first_run_data.csv')
	# PID_parameters = (sol['Kp'], sol['tauP'], sol['thetaP'])
	PID_parameters = (2.88, 221.925, 0)
	# sol = fp.optimize_parameters(data_file='first_run_data.csv')
	# FP_parameters = (sol['UA'], sol['alpha'])
	FP_parameters = (94.999, 0.0024)

	fp.run_model(60, PID_parameters, FP_parameters, data_file='test.csv')
	utils.plot_data(data_file='test.csv', saved_image='data.png',show_plots=False)	
