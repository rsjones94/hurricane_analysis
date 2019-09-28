import os
import shutil

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from read import *


def pare_preeffect_df(gauge, full_preeffect_df):

    mask = full_preeffect_df['Gauge'] == gauge
    return full_preeffect_df[mask]


def resolve(row, param, gauge_dfs, view_width=int(28*2), save=False, saveloc=None, complement=False):
    """
    Plots the pre-effect windows for a gauge

    Args:
        row: the row in the results df to plot
        param: the parameter name to plot
        gauge_dfs: a dictionary where each key is a gauge number pointing to gauge data
        view_width: the number of days surrounding the storm to plot
        save: if True, saves the figure. Otherwise plots interactively
        saveloc: where to save
        complement: Whether to plot the parameter's complement

    Returns:
        Nothing

    """
    plt.ioff()

    row = row[1]
    gauge_name = row['Gauge']
    gauge_df = gauge_dfs[gauge_name]
    ind = row['Storm Index']
    naive_ind = row['Naive Storm Index']
    start = ind - int(view_width/2)
    end = ind + int(view_width/2) + 1
    mean = row['Pre-effect Mean']
    stddev = row['Pre-effect Stddev']
    pr_len = int(row['Pre-effect Window'])
    n = row['Pre-effect Points']
    long_mean = row['Long Term Mean']
    long_std = row['Long Term Stddev']

    if not np.isnan(n):
        storm = row['Storm']
        storm_date = row['Date']

        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.set_xlabel('Time (d)')
        ax1.set_ylabel(param)

        ax2 = ax1.twinx()
        ax2.set_ylabel('Rainfall')

        #plt.figure()
        ax1.axvline(ind, color='forestgreen', label='Estimated Date of Storm Effect')
        ax1.axvline(naive_ind, linestyle='dashed', color='grey', label='Storm Landfall')

        ax1.axhline(mean, linestyle='dashed', color='blue', label='Pre-Effect Tolerance')
        ax1.axhline(mean + stddev, linestyle='dashed', color='navy')
        ax1.axhline(mean - stddev, linestyle='dashed', color='navy')

        """
        ax1.axhline(long_mean, linestyle='dashed', color='gold', label='Long-Term Tolerance')
        ax1.axhline(long_mean + long_std, linestyle='dashed', color='orange')
        ax1.axhline(long_mean - long_std, linestyle='dashed', color='orange')
        """

        exes = gauge_df.index[start:end]
        whys = gauge_df[param][start:end]
        rain = gauge_df['Rain'][start:end]
        ax2.plot(exes, rain, color='blue', label='Rainfall', linewidth=0.5)
        ax1.plot([], [], color='blue', label='Rainfall', linewidth=0.5) # dummy

        ax1.plot(exes, whys, color='black', label=param, linewidth=2)
        win_x = gauge_df.index[(ind-pr_len):ind]
        win_y = gauge_df[param][(ind-pr_len):ind]
        ax1.plot(win_x, win_y, color='red', linewidth=2, label='Pre-effect Window')

        if complement:
            if 'Detrend' in param:
                com = param[:-8]
            else:
                com = param + ' Detrend'

            cexes = gauge_df.index[start:end]
            cwhys = gauge_df[com][start:end]
            ax1.plot(cexes, cwhys, color='orange', label=com, linewidth=1)


        plt.title(f'{gauge_name}\n'
                  f'{param}, {storm} ({storm_date})\n'
                  f'Window: {pr_len} days (mean {round(mean,2)}, stddev {round(stddev,2)}, n {n})')

        plt.xlim(start, end)

        ax1.legend()
        #ax2.legend()
        fig.tight_layout()
        if save:
            saver = os.path.join(saveloc,f'{gauge_name}_{storm}_{param}.pdf')
            plt.savefig(saver)
        else:
            plt.show()

        plt.close()
        plt.ion()


results_folder = r'E:\hurricane\results'
stations_folder = r'E:\hurricane\station_data\modified'
plot_folder = r'E:\hurricane\plots'

params = os.listdir(results_folder)
stations = os.listdir(stations_folder)

param_dfs = {param[:-4]:pd.read_csv(os.path.join(results_folder,param), dtype={'Gauge':str}) for param in params}
station_dfs = {station[:-4]:clean_read(os.path.join(stations_folder,station)) for station in stations}

if os.path.isdir(plot_folder):
    shutil.rmtree(plot_folder)
os.mkdir(plot_folder)

for param, df in param_dfs.items():
    df = df.dropna()
    n_rows = len(df)
    print(f'\nOn {param}. {n_rows} rows.\n')
    out_folder = os.path.join(plot_folder, param)
    os.mkdir(out_folder)
    for i,row in enumerate(df.iterrows()):
        print(f'Saving figure {i+1} of {n_rows}')
        resolve(row, param, station_dfs, view_width=int(28*4),
                save=True,
                saveloc=os.path.join(plot_folder,param),
                complement=True
                )



