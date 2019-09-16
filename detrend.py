import os

from scipy import signal
import matplotlib.pyplot as plt

from read import *


def detrend(x, fs, T, ftype, recenter=True):
    """
    Removes sinusoidal signals from a CONTINUOUS, REGULARLY sampled time series. Note that signals with a frequency
        higher than the Nyquist frequency (fs/2) cannot be removed.

    Args:
        x: the data
        fs: the sampling FREQUENCY of the data
        T: the PERIOD or PERIODS (not frequency) for the filter
        ftype: the filtering type. 'highpass', 'lowpass', 'bandpass', 'bandstop'
        recenter: if True, with output will have the same mean as the input

    Returns:
        The detrended data as a np array
    """
    try:
        w = [(1/i)/(fs/2) for i in T] # convert the period to frequency and normalize
        w.sort()
    except TypeError:
        w = (1/T)/(fs/2) # convert the period to frequency and normalize

    b, a = signal.butter(5, w, ftype)
    res = signal.filtfilt(b, a, x)

    if recenter:
        return res + (np.mean(x)-np.mean(res))
    else:
        return res

parent = r'D:\SkyJones\hurricane\station_data\Finished_Stations'
stations = os.listdir(parent)
station = stations[20]

path = os.path.join(parent,station)
gap_data = clean_read(path).DO
data = gap_data.dropna()

fs = 1

fc_high = 1/180
fc_low = 1/3

t = np.array(data.index)
orig_sig = np.array(data)


plt.figure()

plt.plot(t, orig_sig, label='signal')

high = detrend(orig_sig, 1, 180, 'high')
plt.plot(t, high, label='high')

low = detrend(orig_sig, 1, 10, 'low')
plt.plot(t, low, label='low')

band = detrend(orig_sig, 1, [10,180], 'bandpass')
plt.plot(t, band, label='bandpass')

plt.legend()
plt.show()
