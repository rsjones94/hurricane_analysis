"""
For getting the length of the storm effect and associated data
"""

import os
import shutil

import numpy as np
import pandas as pd

from read import clean_read
from effect_tools import get_effect

# par = 'Discharge Detrend'
# gag = '03027500'

results_folder = r'E:\hurricane\results'
# where the results should be written to
data_folder = r'E:\hurricane\station_data\modified'
# where the data is contained

param_effects = {'Discharge Detrend': 1,
                 'DO Detrend': 1,
                 'Gage Detrend': 1,
                 'N in situ Detrend': -1,
                 'PH Detrend': -1,
                 'SS Detrend': 1,
                 'Turb Detrend': 1
                 }
# if the value to a key is 1, then the parameter is assumed to increase (have a positive response) during the storm effect period
# if the value to a key is -1, then the parameter is assumed to decrease (have a negative response) during the storm effect period

lag_allowed = 4
# number of days after storm onset for a parameter to become perturbed or no effect will be registered
returning_gap_allowed = 1
# number of days where an increasing effect is allowed to reverse trend before it is considered to be on its reverse trend
dropthrough_allowed = (0, 0)
# number of dropthroughs allowed before termination, and number of days allowed for a dropthrough to occur
forcing_allowed = (4, 5)
# number of days where, after the returning gap has been exceeded, the trend can be reversed before forced return is started,
# and number of previous returning days used to calculate the return line
max_effect_allowed = 50
# maximum allowed length of an effect period
max_dropout_allowed = 3
# maximum number of days with no data before termination

#################################

r_files = [f for f in os.listdir(results_folder)]
params = [f[:-4] for f in r_files]
# params = [par]

r_dfs = {p: pd.read_csv(os.path.join(results_folder, f), dtype={'Gauge': str}) for p, f in zip(params, r_files)}

g_files = [f for f in os.listdir(data_folder)]
gauges = [f[:-4] for f in g_files]
g_dfs = {g: clean_read(os.path.join(data_folder, f)) for g, f in zip(gauges, g_files)}

n = len(r_dfs)
for i, (param, result_df) in enumerate(r_dfs.items()):

    print(f'On {param} ({i + 1} of {n})')

    result_df['Effect Start'] = np.nan
    result_df['Effect End'] = np.nan
    result_df['Total Effect'] = np.nan
    result_df['Effect Above'] = np.nan
    result_df['Effect Below'] = np.nan
    result_df['Effect Between'] = np.nan

    result_df['Peak Effect Index'] = np.nan
    result_df['Peak Effect Value'] = np.nan
    result_df['Peak Effect Magnitude'] = np.nan

    result_df['Termination'] = np.nan
    result_df['Forced Start'] = np.nan
    result_df['Forced Slope'] = np.nan

    h = len(result_df)
    for j, (index, line) in enumerate(result_df.iterrows()):
        if np.isnan(line['Pre-effect Window']):
            continue

        gauge = line['Gauge']

        print(f'G {gauge} ({j + 1} of {h})')
        data = g_dfs[gauge]
        start = line['Storm Index']
        mean = line['Pre-effect Mean']
        stddev = line['Pre-effect Stddev']

        ef_type = param_effects[param]
        (es, ee), (d_above, d_below, d_between, term_type, f_start, f_slope) = get_effect(data,
                                                                                          param,
                                                                                          mean,
                                                                                          stddev,
                                                                                          start,
                                                                                          lag=lag_allowed,
                                                                                          effect_type=ef_type,
                                                                                          returning_gap=returning_gap_allowed,
                                                                                          dropthrough=dropthrough_allowed,
                                                                                          forcing=forcing_allowed,
                                                                                          max_effect=max_effect_allowed,
                                                                                          max_dropout=max_dropout_allowed)

        if es is not None and ee is not None:
            e_len = ee - es

            ef_window = data[param].loc[es:ee]
            if ef_type == 1:
                peak_ind = ef_window.idxmax()
            elif ef_type == -1:
                peak_ind = ef_window.idxmin()
            else:
                raise Exception('peak_ind problem')

            line['Peak Effect Index'] = peak_ind
            line['Peak Effect Value'] = data[param].iloc[peak_ind]
            line['Peak Effect Magnitude'] = data[param].iloc[peak_ind] - mean
        else:
            e_len = None

        line['Effect Start'] = es
        line['Effect End'] = ee
        line['Total Effect'] = e_len
        line['Effect Above'] = d_above
        line['Effect Below'] = d_below
        line['Effect Between'] = d_between
        line['Termination'] = term_type
        line['Forced Start'] = f_start
        line['Forced Slope'] = f_slope

        assert r_dfs[param].loc[j]['Gauge'] == gauge
        r_dfs[param].loc[j] = line

        ret = line

n = len(r_dfs)
for i, (param, df) in enumerate(r_dfs.items()):
    print(f'Writing {param}. {i + 1} of {n}')
    out_name = os.path.join(results_folder, f'{param}.csv')
    df.to_csv(out_name, index=False)
