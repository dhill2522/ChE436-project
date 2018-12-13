import matplotlib.pyplot as plt
import pandas as pd

def plot_data(data_file='data.csv', show_plots=True):
    data = pd.read_csv(data_file, sep=',')

    plt.figure()
    plt.plot(data['# time'], data['P'], label='P')
    plt.plot(data['# time'], data['I'], label='I')
    plt.plot(data['# time'], data['D'], label='D')
    plt.plot(data['# time'], data['Err'], label='Error')
    plt.legend()
    plt.savefig('PID.png')
    if show_plots:
        plt.show()
    else:
        plt.clf()

    plt.plot(data['# time'], data['box temp'], label='box temp')
    plt.plot(data['# time'], data['outside temp'], label='outside temp')
    plt.plot(data['# time'], data['SP'], label='setpoint')
    plt.legend()
    plt.savefig('temperatures.png')
    if show_plots:
        plt.show()
    else:
        plt.clf()


def blink_rgb_leb():
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BOARD)
	print('LED should start blinking now. Ctl-C to stop.')
	GPIO.setup(12, GPIO.OUT)

	try:
		while(True):
			GPIO.output(12, GPIO.HIGH)
			time.sleep(1)
			GPIO.output(12, GPIO.LOW)
			time.sleep(1)

	except KeyboardInterrupt:
		sys.exit()


if __name__ == '__main__':
    plot_data(data_file='test.csv')
