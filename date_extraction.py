import os

import pandas as pd


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
