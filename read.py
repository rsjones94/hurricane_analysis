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

        devs.append(np.std(sub_y))

    return np.mean(devs)


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
    return window_stddev(subset, window_size=window_size, step=2)


def segment_window(df, why_col, threshold, index, width=56):
    """
    Recursively segments a a subset of a pandas df

    Args:
        df: a pandas df
        why_col: col name for the y values
        threshold: the maximum error threshold allowed
        index: the ABSOLUTE index of the row to center the subset on
        width: the number of rows to include in the subset, centered on index

    Returns:
        a list of tuples of the ABSOLUTE (not relative) indices (inclusive) of the segments

    """
    slicer = (index-int(width/2), index+int(width/2))
    subdf = df[why_col].loc[slicer[0]:slicer[1]]
    subdf = subdf.dropna()

    exes = subdf.index
    whys = subdf

    res = linear_recurse(exes, whys, threshold=threshold)
    starts = [exes[i[0]] for i in res]
    ends = [exes[i[1]-1] for i in res]
    #e_norms = [i[2] for i in res]

    ses = [list(i) for i in zip(starts, ends)]
    return ses

