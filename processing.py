"""
For detrending gauge data and adding rain data to the detrended data
"""

import os
import shutil

from read import clean_read
from detrend import *
from date_extraction import *
from raster_extraction import *

out_loc = r'E:\hurricane\station_data\modified'  # folder where output will go. will be created if it doesn't exist
stations_parent = r'E:\hurricane\station_data\rain'  # folder of rain data
station_files = os.listdir(stations_parent)  # stations you want to operate on

detrend_note_loc = r'E:\hurricane\station_data\detrend_methods.csv'
# the full path of a csv that will be written to record the detrending method used for each parameter


params = ['PH', 'Discharge', 'Gage', 'Turb', 'DO', 'N in situ', 'SS']
detr_meth = {'PH': None,
             'Discharge': None,
             'Gage': None,
             'Turb': None,
             'DO': 28,
             'N in situ': None,
             'SS': None
             }  # detrending method: 'linear',  maximum allowable period for sinusoidal signals, or None

gauge_file = r'E:\hurricane\station_coords.csv'
# csv that gives that latitude and longitude of each gauge

maxg = 56  # max detrending gap in days. if there are over maxg days of no data, then the time series will be
# split at that point and each segment will be detrended separately

sf = r'E:\hurricane\dates\hurricane_data_dates.txt'
# "storm files'
# path to a txt file with tabular data formatted as HURRICANE,LANDFALL,DATASTART,DATAEND
sef = r'E:\hurricane\station_nos'
# 'storm effect files'
# path to a folder with txt files where each filename is the name of a hurricane, and the contents are a single
# column of gauge numbers that the hurricane's path is known to have crossed

parent = r'E:\hurricane\prism'
# folder where prism rain data is stores

###############################

if os.path.isdir(out_loc):
    shutil.rmtree(out_loc)

if os.path.exists(detrend_note_loc):
    os.remove(detrend_note_loc)

os.mkdir(out_loc)
pd.Series(detr_meth).to_csv(detrend_note_loc)

gauge_dates = relate_gauges_to_storms(sf, sef)
gauges = list(gauge_dates.keys())
gauge_files = [os.path.join(stations_parent, gauge + '.csv') for gauge in gauges]
print('Reading station data in')

station_dfs = {gauge: clean_read(file) for gauge, file in zip(gauges, gauge_files)}
# modded_gauge_dates = onsets_by_rain(gauge_dates,station_dfs)

# custom mods
# gauge = '02160700' # chop at index 4293 for PH
station_dfs['02160700']['PH'].loc[:4293] = np.nan

# detrending
val_err, type_err = [], []
n = len(station_dfs)
out_par = [p + ' Detrend' for p in params]
for par, out_p in zip(params, out_par):
    print(f'\n--------- Detrending {par} ---------\n')
    for i, (gauge, df) in enumerate(station_dfs.items()):
        print(f'On {i + 1} of {n}')
        try:
            if detr_meth[par] is None:
                dt = df[par]
            elif detr_meth[par] != 'lin':
                t_max = detr_meth[par]
                dt = detrend_discontinuous(df.index, df[par], 1, t_max, 'high', max_gap=maxg)
            else:
                dt = detrend_discontinuous_linear(df.index, df[par], max_gap=365)
            station_dfs[gauge][out_p] = dt
        except TypeError:  # malformed data
            print(f'TypeError on {gauge}')
            station_dfs[gauge][out_p] = np.nan
            type_err.append(gauge)
        except ValueError:  # data too gappy to detrend
            print(f'ValueError on {gauge}')
            station_dfs[gauge][out_p] = np.nan
            val_err.append(gauge)

# adding PRISM rain data


bils = get_bils(parent)

col_names = pd.read_csv(gauge_file, nrows=0).columns
types_dict = {'gauge': str, 'x': float, 'y':float}

gauges = pd.read_csv(gauge_file, dtype=types_dict)


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

# writing

n = len(station_dfs)
for i, (gauge, df) in enumerate(station_dfs.items()):
    print(f'Writing {gauge}. {i + 1} of {n}')
    out_name = os.path.join(out_loc, f'{gauge}.csv')
    df.to_csv(out_name, index=False)
