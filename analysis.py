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

analyze = False

sf = r'E:\hurricane\dates\hurricane_data_dates.txt'
sef = r'E:\hurricane\station_nos'
gauge_dates = relate_gauges_to_storms(sf, sef)

out = r'E:\hurricane\results'

parent = r'E:\hurricane\station_data\Finished_Stations'
files = os.listdir(parent)

protect_gauge_nums = False

stddev_history = int(7*8)
stddev_window = int(7*2)
stddev_step = 2

preeffect_width = int(7*10)
preeffect_min = 5
preeffect_max = 28

#######

params_of_interest = ['PH', 'Discharge', 'Gage', 'Turb', 'DO', 'N in situ', 'SS']
output_cols = ['Gauge', 'Date', 'Storm', 'Storm Index', 'Pre-effect Window', 'Pre-effect Points',
               'Pre-effect Mean', 'Pre-effect Stddev']

outputs = {param:pd.DataFrame(columns=output_cols) for param in params_of_interest}
error_gauges = {}

for i, (gauge, storm_dates) in enumerate(gauge_dates.items()):
    print(f'Gauge {gauge}, {i+1} of {len(gauge_dates)}')
    file = os.path.join(parent,f'{gauge}.csv')
    data = clean_read(file)
    data['Date'] = pd.to_datetime(data['Date'], format='%Y/%m/%d')


    for storm, date in storm_dates.items():
        mask = data['Date'] == date
        storm_row = data[mask]
        storm_ind = int(storm_row.index[0])

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
                new_row = [gauge, date, storm, storm_ind, np.nan, np.nan, np.nan, np.nan]
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

                new_row = [gauge, date, storm, storm_ind, window_len, pre_n, pre_mean, pre_stddev]
            appender = {col:entry for col,entry in zip(output_cols,new_row)}
            outputs[param] = outputs[param].append(appender, ignore_index=True)

for param,df in outputs.items():
    if protect_gauge_nums:
        df['Gauge'] = "'" + df['Gauge'].astype(str)
    path = os.path.join(out,f'{param}.csv')
    df.to_csv(path)

'''
col = 'DO'
for i,file in enumerate(files):
    print(f'Checking {file}, file {i} of {len(files)}')
    working = os.path.join(parent, file)
    data = clean_read(working)
    sub = data[['Date', col]]

    if len(sub.dropna() != 0):
        break


data['Date'] = pd.to_datetime(data['Date'], format='%Y/%m/%d')


if analyze:
    ind = 8000

    hist = int(7*8)
    wind = int(7*1)
    dev = typical_stddev(data[col], at_index=ind, history_length=hist, window_size=wind, step=2)

    width = 7*4
    segs = segment_window(data, col, dev, ind, width=width)

    #plt.plot(data.index[start:(end)], data[col][start:(end)], linewidth=3)
    for seg in segs:
        plt.plot(data.index[seg[0]:(seg[1])], data[col][seg[0]:(seg[1])])
    plt.axvline(ind, color='red', linewidth=1, linestyle='dashed')
    plt.axvline(ind+wind, color='orange', linewidth=1, linestyle='dashed')
    plt.axvline(ind-wind, color='orange', linewidth=1, linestyle='dashed')

else:
    plt.plot(data.index, data[col])
'''