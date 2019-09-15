import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from read import *


def pare_preeffect_df(gauge, full_preeffect_df):

    mask = full_preeffect_df['Gauge'] == gauge
    return full_preeffect_df[mask]

def resolve(row, param, gauge_dfs, view_width=int(28*2), save=False, saveloc=None):
    """
    Plots the pre-effect windows for a gauge

    Args:
        row: row of the param_df
        param:
        view_width:
        save:

    Returns:

    """
    plt.ioff()

    row = row[1]
    gauge_name = row['Gauge']
    gauge_df = gauge_dfs[gauge_name]
    ind = row['Storm Index']
    start = ind - int(view_width/2)
    end = ind + int(view_width/2) + 1
    mean = round(row['Pre-effect Mean'],3)
    stddev = round(row['Pre-effect Stddev'],3)
    pr_len = int(row['Pre-effect Window'])
    n = row['Pre-effect Points']
    if not np.isnan(n):
        storm = row['Storm']
        storm_date = row['Date']
        plt.figure()
        plt.axvline(ind, linestyle='dashed', color='red')
        plt.axhline(mean, linestyle='dashed', color='blue')
        plt.axhline(mean+stddev, linestyle='dashed', color='navy')
        plt.axhline(mean-stddev, linestyle='dashed', color='navy')

        exes = gauge_df.index[start:end]
        whys = gauge_df[param][start:end]
        plt.plot(exes, whys)
        win_x = gauge_df.index[(ind-pr_len):ind]
        win_y = gauge_df[param][(ind-pr_len):ind]
        plt.plot(win_x, win_y, color='red', linewidth=2)

        plt.title(f'{gauge_name}\n'
                  f'{param}, {storm} ({storm_date})\n'
                  f'Window: {pr_len} days (mean {mean}, stddev {stddev}, n {n})')
        if save:
            saver = os.path.join(saveloc,f'{gauge_name}_{storm}_{param}.pdf')
            plt.savefig(saver)
        else:
            plt.show()

        plt.close()
        plt.ion()


results_folder = r'E:\hurricane\results'
stations_folder = r'E:\hurricane\station_data\Finished_Stations'
plot_folder = r'E:\hurricane\plots'

params = os.listdir(results_folder)
stations = os.listdir(stations_folder)

param_dfs = {param[:-4]:pd.read_csv(os.path.join(results_folder,param), dtype={'Gauge':str}) for param in params}
station_dfs = {station[:-4]:clean_read(os.path.join(stations_folder,station)) for station in stations}


for param, df in param_dfs.items():
    n_rows = len(df)
    print(f'\nOn {param}. {n_rows} rows.\n')
    df= param_dfs[param].dropna()
    out_folder = os.path.join(plot_folder, param)
    os.mkdir(out_folder)
    for i,row in enumerate(df.iterrows()):
        print(f'Saving figure {i+1} of {n_rows}')
        resolve(row, param, station_dfs, view_width=int(28*4), save=True, saveloc=os.path.join(plot_folder,param))

"""
gauge = '02101726'
param = 'Turb'
plot_gauge(gauge, param, gauge_dfs=station_dfs, param_dfs=param_dfs, view_width=int(28*4), save=False)
"""

