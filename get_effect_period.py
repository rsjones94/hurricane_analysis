import os
import shutil

import numpy as np
import pandas as pd

from read import clean_read


results_folder = r'E:\hurricane\results'
data_folder = r'E:\hurricane\station_data\modified'

r_files = [f for f in os.listdir(results_folder)]
params = [f[:-4] for f in r_files]

r_dfs = {p:pd.read_csv(os.path.join(results_folder,f), dtype={'Gauge':str}) for p,f in zip(params,r_files)}

g_files = [f for f in os.listdir(data_folder)]
gauges = [f[:-4] for f in g_files]
g_dfs = {g:clean_read(os.path.join(data_folder,f)) for g,f in zip(gauges,g_files)}

for param, result_df in r_dfs.items():
    result_df['Total Effect'] = np.nan
    result_df['Effect Above'] = np.nan
    result_df['Effect Below'] = np.nan
    result_df['Dropthrough'] = np.nan
    result_df['Termination'] = np.nan
    result_df['Forced Start'] = np.nan
    result_df['Forced Slope'] = np.nan
    for index,line in result_df.iterrows():
        if np.isnan(line['Pre-effect Window']):
            continue
        gauge = line['Gauge']
        data = g_dfs[gauge]
        start = line['Storm Index']
        mean = line['Pre-effect Mean']
        stddev = line['Pre-effect Stddev']

        #effect = get_effect(data, param, mean, stddev, start) # not implemented