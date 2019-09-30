import os
import shutil

import numpy as np
import pandas as pd

from read import clean_read
from effect_tools import get_effect


results_folder = r'E:\hurricane\results'
data_folder = r'E:\hurricane\station_data\modified'

r_files = [f for f in os.listdir(results_folder)]
params = [f[:-4] for f in r_files]

r_dfs = {p:pd.read_csv(os.path.join(results_folder,f), dtype={'Gauge':str}) for p,f in zip(params,r_files)}

g_files = [f for f in os.listdir(data_folder)]
gauges = [f[:-4] for f in g_files]
g_dfs = {g:clean_read(os.path.join(data_folder,f)) for g,f in zip(gauges,g_files)}

n = len(r_dfs)
for i,(param, result_df) in enumerate(r_dfs.items()):

    print(f'On {param} ({i+1} of {n})')

    result_df['Effect Start'] = np.nan
    result_df['Effect End'] = np.nan
    result_df['Total Effect'] = np.nan
    result_df['Effect Above'] = np.nan
    result_df['Effect Below'] = np.nan
    result_df['Effect Between'] = np.nan
    result_df['Termination'] = np.nan
    result_df['Forced Start'] = np.nan
    result_df['Forced Slope'] = np.nan
    h = len(result_df)
    for j, (index,line) in enumerate(result_df.iterrows()):
        if np.isnan(line['Pre-effect Window']):
            continue

        gauge = line['Gauge']
        print(f'G {gauge} ({j + 1} of {h})')
        data = g_dfs[gauge]
        start = line['Storm Index']
        mean = line['Pre-effect Mean']
        stddev = line['Pre-effect Stddev']

        (es, ee), (d_above, d_below, d_between, term_type, f_start, f_slope) = \
            get_effect(data, param, mean, stddev, start, lag=4, effect_type=1,
               returning_gap=1, dropthrough=(0,0), forcing=(10,4),
               max_effect=365, max_droput=5)

        if es is not None and ee is not None:
            e_len = ee - es
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


n = len(r_dfs)
for i, (param,df) in enumerate(r_dfs.items()):
    print(f'Writing {param}. {i+1} of {n}')
    out_name = os.path.join(results_folder,f'{param}.csv')
    df.to_csv(out_name, index=False)
