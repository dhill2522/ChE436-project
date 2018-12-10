import matplotlib.pyplot as plt
import pandas as pd

def plot_data(data_file='data.csv'):
    data = pd.read_csv(data_file, sep=',')
    print(data['time'])

    plt.figure()
    plt.plot(data['time'], data['P'], label='P')
    plt.plot(data['time'], data['I'], label='I')
    plt.plot(data['time'], data['D'], label='D')
    plt.plot(data['time'], data['Err'], label='Error')
    plt.show()

if __name__ == '__main__':
    plot_data()
