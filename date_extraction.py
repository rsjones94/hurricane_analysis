import os
from datetime import datetime

import pandas as pd

from read import clean_read


def relate_gauges_to_storms(storm_file, storm_effect_folder, ext='.txt'):
    """
    Takes finds what dates correspond to a hurricane landfall for gauges

    Args:
        storm_file: a csv that relates storm names to landfall dates, with at minimum headers 'HURRICANE'
                    and 'LANDFALL'
        storm_effect_folder: a folder full of csvs where each csv is titled after a storm name and only
                             contains the gauges that the storm affected. Headerless.
        ext: the extension for the files in storm_effect_folder

    Returns: a dictionary where each key is a gauge number, and the value is a dict that relates a storm name
             to a date

    """

    storms = pd.read_csv(storm_file)
    storm_names = storms['HURRICANE']
    storm_dates = pd.to_datetime(storms['LANDFALL'], format='%Y/%m/%d')

    storm_dict = {storm:date for storm, date in zip(storm_names, storm_dates)}

    gauges_to_storms = {}
    for storm in storm_names:
        file = storm+ext
        file = os.path.join(storm_effect_folder, file)
        gauges = pd.read_csv(file, header=None)[0]
        for gauge in gauges:
            gauge = gauge[1:-1]
            if gauge not in gauges:
                gauges_to_storms[gauge] = {storm:storm_dict[storm]}
            else:
                gauges_to_storms[gauge][storm] = storm_dict[storm]

    return gauges_to_storms


def onset_by_rain(date, df, window=5, rain_threshold=5):
    """
    Finds true storm onset by fin

    Args:
        date: the date to look around
        df: df with a date and rain column
        window: number of days around date to find max (total window size is window*2
        rain_threshold: mm of rain to consider a storm to have started

    Returns:
        a datetime object and the corresponding index

    """
    mask = df['Date'] == date
    storm_row = df[mask]
    storm_ind = int(storm_row.index[0])

    sub_df = df.iloc[(storm_ind - window):(storm_ind + window)]

    if sub_df.Rain.dropna().empty: # if there's no rain data
        return date, storm_ind

    ind = sub_df.Rain.idxmax()
    val = df.Rain.iloc[ind]
    while val > rain_threshold:
        ind -= 1
        val = df.Rain.iloc[ind]

    #ind += 1


    return df['Date'].iloc[ind], ind


def onsets_by_rain(related_gauges, station_dfs, window=5, rain_threshold=5):
    """
    Takes in the output from relate_gauges_to_storms and a dictionary of pandas dataframes representing
    gauge data and finds the true storm onset

    Args:
        related_gauges: output from relate_gauges_to_storms
        station_dfs: dictionary relating gauge number to pandas df gauge data

    Returns:
        true storm onsets as dictionary of dictionaries

    """

    gauges = list(related_gauges.keys())
    new = {g:{} for g in gauges}
    rg = related_gauges.copy()
    for gauge, storm_dicts in rg.items():
        for storm, date in storm_dicts.items():
            new_date, ind = onset_by_rain(date, station_dfs[gauge], window=window, rain_threshold=rain_threshold)
            new[gauge][storm] = new_date

    return new
