import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from read import *


def pare_preeffect_df(gauge, full_preeffect_df):

    mask = full_preeffect_df['Gauge'] == gauge
    return full_preeffect_df[mask]

def resolve(gauge_df, param, preeffect_df, view_width=int(28*2), gauge_name=None, save=False):
    """
    Plots the pre-effect windows for a gauge

    Args:
        gauge_df: df representing the gauge data
        preeffect_df: df representing the preeffect windows
        view_width: x axis length

    Returns:
        None
    """
    for row in preeffect_df.iterrows():
        row = row[1]
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
            plt.axvline(ind-pr_len, linestyle='dashed', color='orange')
            plt.axhline(mean, linestyle='dashed', color='blue')
            plt.axhline(mean+stddev, linestyle='dashed', color='navy')
            plt.axhline(mean-stddev, linestyle='dashed', color='navy')

            exes = gauge_df.index[start:end]
            whys = gauge_df[param][start:end]
            plt.plot(exes, whys)

            plt.title(f'{gauge_name}\n'
                      f'{param}, {storm} ({storm_date})\n'
                      f'Window: {pr_len} days (mean {mean}, stddev {stddev}, n {n})')

def plot_gauge(gauge, param, gauge_dfs, param_dfs, save=False):
    gauge_df = gauge_dfs[gauge]
    pr_df = pare_preeffect_df(gauge, param_dfs[param])
    resolve(gauge_df, param, pr_df, save=save)

results_folder = r'E:\hurricane\results'
stations_folder = r'E:\hurricane\station_data\Finished_Stations'

params = os.listdir(results_folder)
stations = os.listdir(stations_folder)

param_dfs = {param[:-4]:pd.read_csv(os.path.join(results_folder,param), dtype={'Gauge':str}) for param in params}
station_dfs = {station[:-4]:clean_read(os.path.join(stations_folder,station)) for station in stations}


gauge = '02105769'
param = 'Discharge'
plot_gauge(gauge, param, gauge_dfs=station_dfs, param_dfs=param_dfs, save=False)


