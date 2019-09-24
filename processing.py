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
stations_parent = r'D:\SkyJones\hurricane\station_data\modified'
station_files = os.listdir(stations_parent)

sf = r'D:\SkyJones\hurricane\dates\hurricane_data_dates.txt'
sef = r'D:\SkyJones\hurricane\station_nos'
gauge_dates = relate_gauges_to_storms(sf, sef)
gauges = list(gauge_dates.keys())
gauge_files = [os.path.join(stations_parent, gauge+'.csv') for gauge in gauges]
print('Reading station data in')

station_dfs = {gauge:clean_read(file) for gauge,file in zip(gauges,gauge_files)}
modded_gauge_dates = onsets_by_rain(gauge_dates,station_dfs)


# gauge = '02160700' # chop at index 4293 for PH
gauge = '02198950'
param = 'PH'

d = station_dfs[gauge]
plt.figure()
plt.plot(d.index,d[param])
plt.xlabel('Date')
plt.ylabel(param)
plt.title(gauge)
plt.show()

# detrending DO
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
"""

# adding PRISM rain data
"""
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
"""

# writing
"""
for gauge,df in station_dfs.items():
    print(f'On {gauge}')
    out_name = os.path.join(out_loc,f'{gauge}.csv')
    df.to_csv(out_name, index=False)
"""