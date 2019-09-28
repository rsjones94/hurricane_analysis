import os
from datetime import datetime
import time

import gdal
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

from read import clean_read
from detrend import *
from raster_extraction import *
from date_extraction import *

out_loc = r'E:\hurricane\station_data\modified'
stations_parent = r'E:\hurricane\station_data\rain'
station_files = os.listdir(stations_parent)

detrend_note_loc = r'E:\hurricane\station_data\detrend_methods.csv'

gauge_file = r'E:\hurricane\station_coords.csv'

params = ['PH', 'Discharge', 'Gage', 'Turb', 'DO', 'N in situ', 'SS']
detr_meth = {'PH':'sin',
             'Discharge':'lin',
             'Gage':'lin',
             'Turb':'lin',
             'DO':'sin',
             'N in situ':'sin',
             'SS':'lin'
             } # detrending method

maxg = 56 # max detrending gap

sf = r'E:\hurricane\dates\hurricane_data_dates.txt'
sef = r'E:\hurricane\station_nos'

###############################

gauge_dates = relate_gauges_to_storms(sf, sef)
gauges = list(gauge_dates.keys())
gauge_files = [os.path.join(stations_parent, gauge+'.csv') for gauge in gauges]
print('Reading station data in')

station_dfs = {gauge:clean_read(file) for gauge,file in zip(gauges,gauge_files)}
#modded_gauge_dates = onsets_by_rain(gauge_dates,station_dfs)

# custom mods
# gauge = '02160700' # chop at index 4293 for PH
station_dfs['02160700']['PH'].loc[:4293] = np.nan

pd.Series(detr_meth).to_csv(detrend_note_loc)

# detrending
val_err, type_err = [], []
n = len(station_dfs)
out_par = [p + ' Detrend' for p in params]
for par, out_p in zip(params,out_par):
    print(f'\n--------- Detrending {par} ---------\n')
    for i,(gauge, df) in enumerate(station_dfs.items()):
        print(f'On {i+1} of {n}')
        try:
            if detr_meth[par] == 'sin':
                dt = detrend_discontinuous(df.index, df[par], 1, 180, 'high', max_gap=maxg)
            else:
                dt = detrend_discontinuous_linear(df.index, df[par], max_gap=365)
            station_dfs[gauge][out_p] = dt
        except TypeError:
            print(f'TypeError on {gauge}')
            station_dfs[gauge][out_p] = np.nan
            type_err.append(gauge)
        except ValueError:
            print(f'ValueError on {gauge}')
            station_dfs[gauge][out_p] = np.nan
            val_err.append(gauge)

"""
# adding PRISM rain data
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

for gauge,df in station_dfs.items():
    print(f'Writing {gauge}')
    out_name = os.path.join(out_loc,f'{gauge}.csv')
    df.to_csv(out_name, index=False)
