import os
from datetime import datetime
import time

import gdal
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from read import clean_read
from detrend import *
from raster_extraction import *
from date_extraction import *

#out_loc = r'E:\hurricane\station_data\modified'
stations_parent = r'E:\hurricane\station_data\modified'
station_files = os.listdir(stations_parent)
print('Reading station data in')

station_dfs = {station[:-4]:clean_read(os.path.join(stations_parent,station)) for station in station_files}

has_rain = []
for gauge, df in station_dfs.items():
    rain = df.Rain.dropna()
    if not rain.empty:
        has_rain.append(gauge)

sf = r'E:\hurricane\dates\hurricane_data_dates.txt'
sef = r'E:\hurricane\station_nos'
gauge_dates = relate_gauges_to_storms(sf, sef)
has_storm = list(gauge_dates.keys())

modded_gauge_dates = onsets_by_rain(gauge_dates,station_dfs)


storm_and_rain = [i for i in has_storm if i in has_rain]
rain_but_no_storm = [i for i in has_rain if i not in has_storm]
storm_but_no_rain = [i for i in has_storm if i not in has_rain]


"""
plt.ioff()
for i in storm_and_rain:
    gauge = i
    df = station_dfs[gauge]

    indices = []
    for storm in gauge_dates[gauge]:
        date = gauge_dates[gauge][storm]
        mask = df['Date'] == date
        storm_row = df[mask]
        storm_ind = int(storm_row.index[0])
        indices.append(storm_ind)


    y = df.Rain
    x = df.index

    plt.figure()
    plt.plot(x,y)

    for i in indices:
        plt.axvline(i, color='red')

    new_date, ind = onset_by_rain(date, df, window=5, rain_threshold=5)
    plt.axvline(ind, color='orange', linestyle='dashed')
    plt.xlim(ind-10,ind+10)
    plt.title(gauge)
    #plt.show()
    out = os.path.join(r'E:\hurricane\test_plots', f'{gauge}.pdf')
    plt.savefig(out)
    plt.close()

plt.ion()
"""




"""
val_err, type_err = [], []
n = len(station_dfs)
for i,(gauge, df) in enumerate(station_dfs.items()):
    print(f'On {i+1} of {n}')
    try:
        dt = detrend_discontinuous(df.index, df['DO'], 1, 180, 'high', max_gap=56)
        station_dfs[gauge]['DO Detrend'] = dt
    except TypeError:
        print(f'TypeError on {gauge}')
        station_dfs[gauge]['DO Detrend'] = np.nan
        type_err.append(gauge)
    except ValueError:
        print(f'ValueError on {gauge}')
        station_dfs[gauge]['DO Detrend'] = np.nan
        val_err.append(gauge)



gauge_file = r'E:\hurricane\station_coords.csv'

col_names = pd.read_csv(gauge_file, nrows=0).columns
types_dict = {'gauge': str, 'x': float, 'y':float}

gauges = pd.read_csv(gauge_file, dtype=types_dict)

parent = r'E:\hurricane\prism'
bils = get_bils(parent)

dates, rows = extract_timeseries(gauges.x, gauges.y, bils)


rain_df = unpack_timeseries(gauges.gauge,dates,rows)

station_dfs = {station:df.set_index('Date') for station, df in station_dfs.items()}
print('Joining rain data')
for gauge_no, gauge_df in station_dfs.items():
    print(f'On {gauge_no}')
    try:
        rain = rain_df[gauge_no]
        rain.name = 'Rain'
        new = pd.merge(gauge_df, rain, how='left', left_index=True, right_index=True)
        station_dfs[gauge_no] = new
        print(f'success on {gauge_no}')
    except KeyError:
        station_dfs[gauge_no]['Rain'] = np.nan
        print(f'no rain data for {gauge_no}')
        pass

station_dfs = {station:df.reset_index(level='Date') for station, df in station_dfs.items()}



for gauge,df in station_dfs.items():
    print(f'On {gauge}')
    out_name = os.path.join(out_loc,f'{gauge}.csv')
    df.to_csv(out_name, index=False)
"""