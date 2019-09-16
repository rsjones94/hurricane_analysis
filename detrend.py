import os

from scipy import signal
import matplotlib.pyplot as plt

from read import *


def t_days_to_f_s(x):
    """
    Converts a period measured in months to its equivalent frequency in Hz

    Args:
        x: a float or int

    Returns:
        float
    """
    return 1/(x*24*60*60)

def f_days_to_f_s(x):
    """
    Converts a frequency measured in months to its equivalent frequency in Hz

    Args:
        x: a float or int

    Returns:
        float
    """
    return x/(24*60*60)


parent = r'D:\SkyJones\hurricane\station_data\Finished_Stations'
stations = os.listdir(parent)
station = stations[20]

path = os.path.join(parent,station)
gap_data = clean_read(path).DO
data = gap_data.dropna()

fs = 1

fc_high = 1/180
fc_low = 1/3
#t = np.array(data.index)[9320:10000]
#signalc = np.array(data.DO)[9320:10000]
t = np.array(data.index)
original_signal = np.array(data)

plt.plot(t, original_signal, label='signal')

w_high = fc_high / (fs / 2) # Normalize the frequency
w_low = fc_low / (fs / 2) # Normalize the frequency

b_band, a_band = signal.butter(5, [w_high, w_low], 'bandpass')
output_band = signal.filtfilt(b_band, a_band, original_signal) + np.mean(original_signal)

b_high, a_high = signal.butter(5, w_high, 'highpass')
output_high = signal.filtfilt(b_high, a_high, original_signal) + np.mean(original_signal)

plt.plot(t, output_high, label='high')
plt.plot(t, output_band, label='band')

plt.legend()
plt.show()

gap_signal = np.array(gap_data)
gap_t = np.array(gap_data.index)
resamp = signal.resample(gap_signal, len(gap_t), gap_t)

plt.plot(resamp[1],resamp[0])
