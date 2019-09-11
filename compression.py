from itertools import chain

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


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


def sum_of_error(predicted, actual):
    predicted = np.array(predicted)
    actual = np.array(actual)

    error = predicted-actual
    abs_error = [abs(i) for i in error]
    return sum(abs_error)


def sum_of_square_error(predicted, actual):
    predicted = np.array(predicted)
    actual = np.array(actual)

    error = predicted-actual
    sq_error = [i**2 for i in error]
    return sum(sq_error)


def get_lin_values(exes, m, b):
    return [func_linear(x, m, b) for x in exes]


def get_line(exes, whys, start_end, return_error=False):
    """
    Returns m, b and r2 value for the line that best fits a subset of points.

    Args:
        exes: the x values in the series
        whys: the y values in the series
        start_end: a list of len 2 indicating the start (inclusive) and end (exclusive) of the subset.
                   Does not need to be ordered
    Returns: A tuple (m, b, r2) unless return_error is True, which will return only the r2 and error
    """
    slicer = start_end[:]
    slicer.sort()
    start, end = slicer[0], slicer[1]
    x = exes[start:end]
    y = whys[start:end]
    m, b = np.polyfit(x, y, 1)

    predictions = get_lin_values(x, m, b)
    r2 = get_r2(predictions, y)

    if return_error:
        return r2, sum_of_square_error(predictions, y)
    else:
        return m, b, r2


def plot_line(tup, from_x, to_x):
    exes = [from_x,to_x]
    whys = get_lin_values(exes,tup[0],tup[1])
    plt.plot(exes,whys)


def trawl(exes, whys, start, threshold=0.8, step=-1):
    """
    For a data series, starts at a point and begins fitting lines to an increasing number of points,
    terminating when the r2 value drops below a threshhold.

    Args:
        exes: the x values in the series
        whys: the y values in the series
        start: the start index
        threshold: the r2 threshold
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
    while r2 > threshold:
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


def split_segment(exes, whys, segment):
    """
    Takes a segment of a data series and splits it into two segments, where the new segments have optimal
    linear fits based on minimizing the sum of the squared errors

    Args:
        exes: the x values in the series
        whys: the y values in the series
        segment: a list of len 2 indicating the start (inclusive) and end (exclusive) of the subset

    Returns: a tuple with two sublists containing the start and end of each new segment and r2
    """
    #print(f'Splitting {segment}')
    if segment[1] - segment[0] == 3:
        seg1 = [segment[0], segment[0]+2]
        seg2 = [segment[1]-2, segment[1]]
        r1, e1 = get_line(exes, whys, seg1, return_error=True)
        r2, e2 = get_line(exes, whys, seg2, return_error=True)

        win_r1, win_r2 = r1, r2
        win_segs = [[seg1[0], seg1[1], win_r1], [seg2[0], seg2[1], win_r2]]

        #print(f'Split result: {win_segs}. Obligate result.')
        return win_segs

    win_r1, win_r2 = 0, 0
    win_e1, win_e2 = -1, -1
    win_segs = []
    for i in range(segment[0]+2, segment[1]-1):
        seg1 = [segment[0], i]
        seg2 = [i-1, segment[1]]

        r1, e1 = get_line(exes, whys, seg1, return_error=True)
        r2, e2 = get_line(exes, whys, seg2, return_error=True)
        #print(f'errors: {e1, e2}')
        if 1/sum([e1, e2]) > 1/sum([win_e1, win_e2]):
            #print(f'Winner')
            win_r1, win_r2 = r1, r2
            win_e1, win_e2 = e1, e2
            win_segs = [[seg1[0], seg1[1], win_r1], [seg2[0], seg2[1], win_r2]]
    #print(f'Split result: {win_segs}. Errors: {win_e1, win_e2}')
    return win_segs


def flatten(x):
    ''' Creates a generator object that loops through a nested list '''
    # First see if the list is iterable
    try:
        it_is = iter(x)
    # If it's not iterable return the list as is
    except TypeError:
        yield x
    # If it is iterable, loop through the list recursively
    else:
        for i in it_is:
            for j in flatten(i):
                yield j


def regroup(x, n):
    """
    Turns a flat list into a list of lists with sublength n
    Args:
        x: flat list
        i: sublist len

    Returns: list of lists

    """
    i = 0
    new_list = []
    while i < len(x):
        new_list.append(x[i:i + n])
        i += n
    return new_list


def linear_recurse(exes, whys, threshold=0.8, segments=None):
    """
    Recursively breaks a data series into segments until the r2 for all segments exceeds the threshold.

    Args:
        exes: the x values in the series
        whys: the y values in the series
        threshold: the r2 threshold to be exceeded
        segments: an optional list of lists that indicate the segment slices to start with and corresponding r2

    Returns: a tuple of lists, where each list is the start (incl), end (excl) and r2 of each segment
    """

    if segments is None:
        start_end = [0, len(exes)]
        segments = [[start_end[0], start_end[1], get_line(exes, whys, start_end)[2]]]

    #print(f'New segs: {segments}')
    segments = [split_segment(exes,whys,seg) if seg[2] < threshold else seg for seg in segments]

    flattened = [i for i in flatten(segments)]
    segments = regroup(flattened, 3)
    print(f'Segments: {segments}')
    if all(seg[2] >= threshold for seg in segments):
        print(f'Returning. Final: {segments}')
        return segments
    else:
        return linear_recurse(exes, whys, threshold=threshold, segments=segments)