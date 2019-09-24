import os
import time
import datetime
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from read import *
from compression import *
from date_extraction import *


sf = r'E:\hurricane\dates\hurricane_data_dates.txt'
sef = r'E:\hurricane\station_nos'

out = r'E:\hurricane\results'

parent = r'E:\hurricane\station_data\modified'

protect_gauge_nums = False

stddev_history = int(7*8)
stddev_window = int(7*2)
stddev_step = 2

preeffect_width = int(7*10)
preeffect_min = 5
preeffect_max = 28

stormstart_window = 5
stormstart_min = 5

#######

gauge_dates = relate_gauges_to_storms(sf, sef)
gauge_nums = list(gauge_dates.keys())
gauge_files = [f'{i}.csv' for i in gauge_nums]
print('Reading station data in')

station_dfs = {station[:-4]:clean_read(os.path.join(parent, station)) for station in gauge_files}
gauge_dates_mod = onsets_by_rain(gauge_dates, station_dfs, stormstart_window, stormstart_min)


params_of_interest = ['PH', 'Discharge', 'Gage', 'Turb', 'DO Detrend', 'N in situ', 'SS']
output_cols = ['Gauge', 'Date', 'Storm', 'Storm Index', 'Naive Storm Index', 'Pre-effect Window', 'Pre-effect Points',
               'Pre-effect Mean', 'Pre-effect Stddev']

outputs = {param:pd.DataFrame(columns=output_cols) for param in params_of_interest}
error_gauges = {}

for i, (gauge, storm_dates) in enumerate(gauge_dates_mod.items()):
    print(f'Gauge {gauge}, {i+1} of {len(gauge_dates_mod)}')
    data = station_dfs[gauge]


    for storm, date in storm_dates.items():
        mask = data['Date'] == date
        storm_row = data[mask]
        storm_ind = int(storm_row.index[0])

        naive_mask = data['Date'] == gauge_dates[gauge][storm]
        naive_storm_row = data[naive_mask]
        naive_ind = int(naive_storm_row.index[0])

        for param in params_of_interest:
            try:
                max_error = typical_stddev(data[param], at_index=storm_ind,
                                           history_length=stddev_history,
                                           window_size=stddev_window, step=stddev_step)
            except TypeError: # happens with malformed data
                warnings.warn(f'TypeError: malformation on {gauge,param}')
                max_error = np.nan
                if gauge not in error_gauges:
                    error_gauges[gauge] = [param]
                else:
                    error_gauges[gauge].append(param)
            if np.isnan(max_error):
                new_row = [gauge, date, storm, storm_ind, naive_ind,
                           np.nan, np.nan, np.nan, np.nan]
            else:
                window = get_preeffect_window(data,
                                              why_col=param,
                                              threshold=max_error,
                                              index=storm_ind,
                                              width=preeffect_width,
                                              min_win=preeffect_min,
                                              max_win=preeffect_max)
                window_len = window[1]-window[0]
                pre_mean, pre_stddev, pre_n = analyze_window(data,
                                                             why_col=param,
                                                             window=window)

                new_row = [gauge, date, storm, storm_ind, naive_ind,
                           window_len, pre_n, pre_mean, pre_stddev]
            appender = {col:entry for col,entry in zip(output_cols,new_row)}
            outputs[param] = outputs[param].append(appender, ignore_index=True)

for param,df in outputs.items():
    if protect_gauge_nums:
        df['Gauge'] = "'" + df['Gauge'].astype(str)
    path = os.path.join(out,f'{param}.csv')
    df.to_csv(path)
