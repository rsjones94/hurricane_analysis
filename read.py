"""
Functions for reading formatted gauge data in and extracting statistics
"""


import pandas as pd
import numpy as np

from compression import *


def clean_read(file, nodata_val=-999):
    """
    Reads in a csv file and returns a pandas df with the nodata value replaced with Null

    Args:
        file: path the the spreadsheet
        nodata_val: the value to be replaced with nan

    Returns:
        pd.df object

    """

    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d')
    df = df.replace(nodata_val, np.nan)

    return df


def window_stddev(whys, window_size, step=1):
    """
    Returns the average standard deviation for a set of data by grabbing stddevs using a moving window
    The implied x data should be evenly spaced

    Args:
        whys: y data
        window_size: index width of windows
        step: step to increment window by

    Returns:
        a float representing the average stddev

    """
    devs = []
    for i in range(0, len(whys)-window_size, step):
        sub_y = np.array(whys[i:(i + (window_size - 1))])
        sub_y = sub_y[~np.isnan(sub_y)]
        if len(sub_y) < 2:
            devs.append(np.nan)
        else:
            dev = np.std(sub_y)
            devs.append(dev)

    if not all(np.isnan(x) for x in devs):
        return np.mean(devs)
    else:
        return np.nan


def typical_stddev(whys, at_index, history_length=28, window_size=14, step=2):
    """
    Finds the representative stdev for a given history at a specified index
    
    Args:
        whys: y data
        at_index: the index of the point in question
        history_length: number of data points to include in history subset
        window_size: number of points in moving window
        step: index increment size for moving window

    Returns:
        The representative stddev for that index

    """
    subset = whys[(at_index-history_length):at_index]
    return window_stddev(subset, window_size=window_size, step=step)


def segment_view(df, why_col, threshold, index, width):
    """
    Recursively segments a a subset of a pandas df by fitting a line to data and splitting the data if an
    error theshold is exceeded

    Args:
        df: a pandas df
        why_col: col name for the y values
        threshold: the maximum error threshold allowed
        index: the ABSOLUTE index of the row to center the subset on
        width: the number of rows to include in the subset, centered on index

    Returns:
        a list of tuples of the ABSOLUTE (not relative) indices (inclusive:exclusive) of the segments

    """
    slicer = (index-int(width/2), index+int(width/2))
    subdf = df[why_col].loc[slicer[0]:slicer[1]]
    subdf = subdf.dropna()

    exes = subdf.index
    whys = subdf

    res = linear_recurse(exes, whys, threshold=threshold)
    starts = [exes[i[0]] for i in res]
    ends = [exes[i[1]-1]+1 for i in res]
    #e_norms = [i[2] for i in res]

    ses = [list(i) for i in zip(starts, ends)]
    return ses


def get_preeffect_window(df, why_col, threshold, index, width, min_win=5, max_win=28):
    """
    Gets the preeffect window for an index by subsetting a df around an index and then
    recursively splitting it. The window's end is always the index (exclusive).

    Args:
        df: a pandas df
        why_col: col name for the y values
        threshold: the maximum error threshold allowed
        index: the ABSOLUTE index of the row to center the subset on
        width: the number of rows to include in the subset, centered on index
        min_win: min window length (inclusive)
        max_win: max window length (inclusive)

    Returns:
        a list (len 2) of the ABSOLUTE (not relative) indices (inclusive:exclusive) of the window

    """

    segs = segment_view(df, why_col, threshold, index, width)
    segs.reverse()

    for seg in segs:
        if seg[0] < index:
            window = [seg[0],index]
            win_len = window[1] - window[0]
            if win_len < min_win:
                window[0] = window[1] - (min_win)
            elif win_len > max_win:
                window[0] = window[1] - (max_win)
            return window

    raise IndexError('Preeffect window error')


def analyze_window(df, why_col, window, stddev_drop=True):
    """
    Gets the mean, stddev and number of points for a window. Strips None/nans. Also, if a point falls outside of 1.5sd,
    the point is removed and the sd is recalculated if stddev_drop is True

    Args:
        df: a dataframe
        why_col: col name for the y values
        window: window as a tuple or list (inclusive:exclusive)

    Returns:
        a tuple (mean, stddev, n_points, removed_points_due_to_sd)

    """
    sub = df[why_col][window[0]:window[1]]
    sub = sub.dropna()

    mean = np.mean(sub)
    stddev = np.std(sub)
    n_window = len(sub)
    n_drop = 0

    if stddev_drop:
        ma = mean + stddev*1.5
        mi = mean - stddev*1.5

        cut_sub = sub.loc[sub.between(mi, ma)]
        stddev = np.std(cut_sub)

        n_drop = len(sub) - len(cut_sub)
        n_window = len(cut_sub)
        mean = np.mean(cut_sub)

    return mean, stddev, n_window, n_drop

