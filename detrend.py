import os

from scipy import signal
from scipy import interpolate
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


def continuous_subsets(tees, whys, max_gap=0, repair=False):
    """
    Finds sampling gaps and divides the data into continuous samples

    Args:
        tees: time values
        whys: y values
        max_gap: integer indicating maximum gap allowable to be considered continuous
        repair: a boolean indicating if gaps should be filled with interpolated values

    Returns:
        A tuple of two lists of lists (t_cont, y_cont), each list representing the continuous stretches of the data

    """

    groups_why = []
    groups_tee = []
    inner_why = []
    inner_tee = []
    y_pad = []
    t_pad = []
    n_gap = 0
    for tee, why in zip(tees, whys):
        if not np.isnan(why):  # if there's a number, definitely add it
            # print(f'Good. Adding {tee,why} to inner set')
            n_gap = 0  # add the pads in case an acceptable gap preceded
            inner_why.extend(y_pad)
            inner_tee.extend(t_pad)
            y_pad, t_pad = [], []

            inner_why.append(why)
            inner_tee.append(tee)
        else:
            n_gap += 1
            # print(f'Gap: {tee,why}. Gaplen is {n_gap} ({max_gap} allowable)')
            y_pad.append(why)
            t_pad.append(tee)
            if n_gap > max_gap:
                y_pad, t_pad = [], []
                if inner_why != []:  # if we've exceeded the allowable gap
                    # print(f'Gap exceeded. Adding {inner_tee[0:3], inner_why[0:3]} etc')
                    groups_why.append(inner_why)
                    groups_tee.append(inner_tee)
                    inner_why, inner_tee = [], []

    if inner_why != []:
        groups_why.append(inner_why)
        groups_tee.append(inner_tee)
        # print('Final append')

    if repair and max_gap > 0:
        groups_why = [fill_gaps(tee,why) for tee,why in zip(groups_tee,groups_why)]

    return groups_tee, groups_why


def fill_gaps(tee, why):
    """
    Fills nans in the why argument

    Args:
        tee: t data
        why: y data

    Returns:
        an array of the filled y data

    """
    s = pd.Series(why,tee).interpolate(limit_direction='both')
    return np.array(s)


def detrend_discontinuous(t, x, fs, T, ftype, max_gap=0, recenter=True):
    """
    Like detrend, but will split discontinuous data (and interpolate small gaps) before detrending.

    Args:
        t: time data (should be continuous)
        x: x data. may be gappy (has nans)
        fs: the sampling FREQUENCY of the data
        T: the PERIOD or PERIODS (not frequency) for the filter
        max_gap: the largest gap allowable for interpolation
        ftype: the filtering type. 'highpass', 'lowpass', 'bandpass', 'bandstop'
        recenter: if True, with output will have the same mean as the input

    Returns:
        The detrended data as a pd Series. if the original data was discontinuous, there will be fewer entries in the
        returned Series, but the index will still match up

    """

    sub_tees, sub_exes = continuous_subsets(t, x, max_gap=max_gap, repair=True)
    d_exes = [detrend(sub, fs, T, ftype, recenter=False) for sub in sub_exes]

    tees = []
    exes = []
    for sub_t, sub_x in zip(sub_tees, d_exes):
        tees.extend(sub_t)
        exes.extend(sub_x)

    if recenter:
        exes = exes + (np.nanmean(x)-np.mean(exes))

    c = crush_series(t, x, tees, exes)
    return c


def crush_series(original_index, original, to_crush_index, to_crush):
    """
    Removes all values in to_crush that are nan in the original

    Args:
        original_index: index values
        original: values to validate against
        to_crush_index: index values
        to_crush: derived values that need some crushing

    Returns:
        a pd series with only the values in to_crush that aren't nan in the original data

    """
    df = pd.DataFrame({'original':original}, index=original_index)
    s = pd.Series(to_crush, to_crush_index)
    df['crushed'] = s
    df = df.dropna()
    return df['crushed']



#sta = 20 # fine
#sta = 150 # problem - data too discontinuous. need to interpolate small gaps?
#sta = 300 # same as above
sta = 500 # same as above
parent = r'D:\SkyJones\hurricane\station_data\Finished_Stations'
stations = os.listdir(parent)
station = stations[sta]

path = os.path.join(parent, station)

full = clean_read(path)

'''
t = full.index
y = full.DO
t_cont, y_cont = continuous_subsets(t,y,10000,True)
'''


plt.figure()
plt.plot(full.index, full['DO'], label='Original')
plt.title(station)

dt = detrend_discontinuous(full.index, full['DO'], 1, 180, 'high', max_gap=7)
full['DO Detrend'] = dt

plt.plot(full.index, full['DO Detrend'], label='High Pass (T>180)')

plt.xlabel('t (days)')
plt.ylabel('DO (mg/L)')
plt.legend()
plt.show()


"""
gap_data = clean_read(path).DO
gap_sig = np.array(gap_data)
gap_t = np.array(gap_data.index)

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
"""


