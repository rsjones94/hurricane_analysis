"""
This module calculates the standard deviation of various gauge parameters during the "pre-effect window", which is an
arbitrary, variable length period of time before the impact of a given hurricane is "felt" at a gauge, and uses that to determine
the length of the effect of the hurricane on the river for each parameter. The effect length is the length of the time
the parameter stays outside the mean of the pre-effect window +/ some multiple of the  standard deviation.
"""
import warnings
import shutil

from read import *
from compression import *
from date_extraction import *

sf = r'E:\hurricane\dates\hurricane_data_dates.txt'
# "storm files'
# path to a txt file with tabular data formatted as HURRICANE,LANDFALL,DATASTART,DATAEND
sef = r'E:\hurricane\station_nos'
# 'storm effect files'
# path to a folder with txt files where each filename is the name of a hurricane, and the contents are a single
# column of gauge numbers that the hurricane's path is known to have crossed

out = r'E:\hurricane\results'
# the folder where the output will be written to

parent = r'E:\hurricane\station_data\modified'
# the parent folder that contain the data to be analyzed
# folder where each file is a csv file titled as a gauge number, contained tabular gauge data

protect_gauge_nums = False
# if True, then the gauge numbers in the output will be written as strings rather than numbers
# generally this is not needed

stddev_history = int(7 * 8)
# the number of days before storm impact to use as a subset to calculate a typical stddev for a parameter
stddev_window = int(7 * 2)
# the width of the sliding window within the subset defined by stddev_history for which a stddev will be calculated
stddev_step = 2
# the number of days the window slides per step
stddvs_for_error = 0.5
# a multiplier for the effect tolerance. The threshold for what is considered the normal perturbation of a given
# parameter. When segmenting the pre-effect window, the stddev of the stddev_history window*stddvs_for_error is used as
# the threshold for splitting a segment

preeffect_width = int(7 * 10)
# the number of days around the start of the storm impact to search for the pre-effect window
preeffect_min = 5
# minimum number of days of a pre-effect window
preeffect_max = 10
# maximum number of days of a pre-effect window

stormstart_window = 5
# the storm onset is defined as the day where the recorded rainfall is at its maximum, within a window that is
# within +/ stormstart_window days of the recorded landfall of the storm
stormstart_min = 2
# the minimum amount of recorded rainfall in mm needed within the storm window as defined by stormstart_window
# for the hurricane to be considered having an effect at all

longterm_width = 365
# a defunct parameter that was used to calculate the stddev of a long, fixed window before the storm impact


#######

if os.path.isdir(out):
    shutil.rmtree(out)

os.mkdir(out)

gauge_dates = relate_gauges_to_storms(sf, sef)
gauge_nums = list(gauge_dates.keys())
gauge_files = [f'{i}.csv' for i in gauge_nums]
print('Reading station data in')

station_dfs = {station[:-4]: clean_read(os.path.join(parent, station)) for station in gauge_files}
gauge_dates_mod = onsets_by_rain(gauge_dates, station_dfs, stormstart_window, stormstart_min)
# create a dictionary where each key is a gauge, and each entry itself is a dictionary where each key is a storm name
# and each entry is the date of the true storm onset

params_of_interest = ['PH Detrend', 'Discharge Detrend', 'Gage Detrend', 'Turb Detrend',
                      'DO Detrend', 'N in situ Detrend', 'SS Detrend']

output_cols = ['Gauge',
               'Date',
               'Storm',
               'Storm Index',
               'Naive Storm Index',
               'Pre-effect Window',
               'Pre-effect Points',
               'Pre-effect Mean',
               'Pre-effect Stddev',
               'Dropped Pre-Effect Points'  # number of dropped points due to stddev
               ]

outputs = {param: pd.DataFrame(columns=output_cols) for param in params_of_interest}
# creating a dict of empty DataFrames
error_gauges = {}

for i, (gauge, storm_dates) in enumerate(gauge_dates_mod.items()):
    print(f'Gauge {gauge}, {i + 1} of {len(gauge_dates_mod)}')
    data = station_dfs[gauge]

    for storm, date in storm_dates.items():
        mask = data['Date'] == date
        storm_row = data[mask]
        storm_ind = int(storm_row.index[0])
        # the index of the actual date of storm effect

        naive_mask = data['Date'] == gauge_dates[gauge][storm]
        naive_storm_row = data[naive_mask]
        naive_ind = int(naive_storm_row.index[0])
        # the index of the date of storm landfall (not the date of actual storm effect)

        for param in params_of_interest:
            try:
                max_error = typical_stddev(data[param], at_index=storm_ind,
                                           history_length=stddev_history,
                                           window_size=stddev_window, step=stddev_step) * stddvs_for_error
                # max_error is the maximum e^2_norm threshold allowed when recursively segmenting the pre-effect window
            except TypeError:  # happens with malformed data
                warnings.warn(f'TypeError: malformation on {gauge, param}')
                max_error = np.nan
                if gauge not in error_gauges:
                    error_gauges[gauge] = [param]
                else:
                    error_gauges[gauge].append(param)
            if np.isnan(max_error):
                new_row = [gauge,  # gauge
                           date,  # date
                           storm,  # storm
                           storm_ind,  # storm index
                           naive_ind,  # naive storm index
                           np.nan,  # pre-effect window
                           np.nan,  # pre-effect points
                           np.nan,  # pre-effect mean
                           np.nan,  # pre-effect stddev
                           np.nan,  # dropped short points
                           ]
            else:
                window = get_preeffect_window(data,
                                              why_col=param,
                                              threshold=max_error,
                                              index=storm_ind,
                                              width=preeffect_width,
                                              min_win=preeffect_min,
                                              max_win=preeffect_max)
                window_len = window[1] - window[0]
                pre_mean, pre_stddev, pre_n, dropped_short_points = analyze_window(data,
                                                                                   why_col=param,
                                                                                   window=window)

                # long_window = (window[1]-longterm_width, window[1])
                # long_mean, long_stddev, long_n, dropped_long_points = analyze_window(data,
                # why_col=param,
                # window=long_window)
                # print(f'MEAN: {long_mean}, STDDEV: {long_stddev}, N: {long_n}')
                new_row = [gauge,  # gauge
                           date,  # date
                           storm,  # storm
                           storm_ind,  # storm index
                           naive_ind,  # naive storm index
                           window_len,  # pre-effect window
                           pre_n,  # pre-effect points
                           pre_mean,  # pre-effect mean
                           pre_stddev,  # pre-effect stddev
                           dropped_short_points  # Dropped Pre-Effect Points
                           ]

            # print(len(output_cols), len(new_row))
            appender = {col: entry for col, entry in zip(output_cols, new_row)}
            # print(appender)
            outputs[param] = outputs[param].append(appender, ignore_index=True)

for param, df in outputs.items():
    if protect_gauge_nums:
        df['Gauge'] = "'" + df['Gauge'].astype(str)
    path = os.path.join(out, f'{param}.csv')
    df.to_csv(path, index=False)
