import numpy as np
from scipy.optimize import curve_fit


def func_linear(x, m, b):
    """
    Linear function
    """
    return m*x+b


def get_r2(predicted, actual):
    """
    Gives the r^2 value for a set of predicted data against actual data.
    """
    predicted = np.array(predicted)
    actual = np.array(actual)

    mean_val = np.mean(actual)

    sse = sum((actual - predicted) ** 2)
    sst = sum((actual - mean_val) ** 2)

    return 1 - (sse / sst)


def get_line(exes, whys, start_end):
    """
    Returns m, b and r2 value for the line that best fits a subset of points.

    Args:
        exes: the x values in the series
        whys: the y values in the series
        start_end: a list of len 2 indicating the start (inclusive) and end (exclusive) of the subset.
                   Does not need to be ordered
    Returns: A tuple (m, b, r2)

    """
    slicer = start_end[:]
    slicer.sort()
    start, end = slicer[0], slicer[1]
    x = exes[start:end]
    y = whys[start:end]
    m, b = np.polyfit(x, y, 1)

    predictions = [func_linear(val, m, b) for val in x]
    r2 = get_r2(predictions, y)

    return m, b, r2


def trawl(exes, whys, start, threshhold=0.8, step=-1):
    """
    For a data series, starts at a point and begins fitting lines to an increasing number of points,
    terminating when the r2 value drops below a threshhold.

    Args:
        exes: the x values in the series
        whys: the y values in the series
        start: the start index
        threshhold: the r2 threshhold
        step: The increment value for traversing the data

    Returns: The index of the last point that meets the threshhold criteria

    """

    r2 = 1
    if step < 0:
        anchor = start + 1
        ind = start
    else:
        anchor = start
        ind = start + step

    i = 0
    while r2 > threshhold:
        ind += step
        if ind < 0 or ind > len(exes)-1:
            break
        m, b, r2 = get_line(exes, whys, [anchor, ind])
        i += 1
        print(ind, r2)

    if i == 1:
        res = [ind, start]
    else:
        res = [ind-step, start]
    res.sort()
    return res
