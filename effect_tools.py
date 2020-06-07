import os
import shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from read import clean_read
from detrend import *


def get_effect(data, param, mean, stddev, start_index, lag=3, effect_type=1,
               returning_gap=0, dropthrough=(0, 0), forcing=(None, None),
               max_effect=365, max_dropout=5):
    """
    For a given parameter, finds the time it takes for the time series to return to normalcy
    after a peturbation

    Args:
        data: A DataFrame of gauge data
        param: the column in data to use
        mean: the mean value of the pre-effect window
        stddev: the standard deviation of the pre-effect window
        start_index: the index of the storm peturbation
        lag: the number of days allowed for an effect to begin. Minimum is 1
        effect_type: the INITIAL expected effect of the peturbation. 1 indicates a positive effect, -1
                     indicates a negative effect
        returning_gap: number of days where an increasing effect is allowed to reverse trend
                          before it is considered to be on its reverse trend
        dropthrough: A list or tuple indicating the number of dropthroughs allowed and the number of days
                     the time series is allotted to drop through before being considered terminated.
                     A dropthrough is when a parameter is outside the normal range for that parameter and quickly
                     becomes outside the normal range but with opposite valence, e.g., it is above the normal range and
                     quickly goes to being below the normal range.
        forcing: a tuple of 1) the number of days a returning trend can be reversed before it is forced to
                          return by calculating the best fit line for the last n returning days and
                          calculating the date of intersection. This allows an effect window to be
                          estimated even when additional storms/forcing effects follow the initial
                          peturbation. Default is None, which will never force a completion.
                          2) the number of points to include in the forcing slope fit line
        max_effect: the maximum number of days an effect can continue before being terminated
        max_dropout: number of continuous days of no signal before mandatory termination

    Returns:
        A list with two parts. The first is a list of the start and end indices of the effect
        (or None, if there was no effect). The second is list, (days_above, days_below, days_between,
        termination_type, forcing_start, forcing_slope). termination_type can be "natural", "forced",
        None or 'dropout'
        If not forced, forcing_start and forcing_slope will be None.
    """
    returner = [[None, None], [0, 0, 0, 'natural', None, None]]

    force_completion = forcing[0]  # number of days to regress before completion is forced
    force_history = forcing[1]

    dropthrough = [dropthrough[0], dropthrough[1]]

    comp_dict = {1: greater, -1: lesser}

    exes = np.array(data.index)
    orig = np.array(data[param])
    whys = np.array(pd.Series(orig).interpolate(limit_direction='both'))

    low = mean - stddev
    high = mean + stddev
    normalcy = (low, high)

    if effect_type == 1:
        comp_ind = 1
        comp_val = normalcy[comp_ind]  # high
    elif effect_type == -1:
        comp_ind = 0
        comp_val = normalcy[comp_ind]  # low
    else:
        raise Exception('effect_type must be 1 or -1')

    effect_begun = False
    i = start_index - 1
    while lag > 0:
        lag -= 1
        i += 1
        val = whys[i]
        if comp_dict[effect_type](val, comp_val):
            effect_begun = True
            returner[0][0] = i
            break
    if not effect_begun:
        returner[1][3] = None
        return returner

    # print(f'Effect begins at {i} {whys[i]}')

    i -= 1
    is_returning = False
    has_real_val = False
    nan_count = 0
    ret_gap_count = 0
    while True:
        i += 1

        # print(f'Checking {i} {whys[i]}')

        if i > (i + max_effect):
            returner[1][3] = 'max_effect'

        if np.isnan(orig[i]):
            nan_count += 1
            # print(f'NANNER: {nan_count}')
            if nan_count > max_dropout:
                returner[1][3] = 'dropout'
                # print('dropping out')
                i -= nan_count - 1
                break
        else:
            has_real_val = True
            nan_count = 0

        last_val = whys[i - 1]
        val = whys[i]

        towards_pre = comp_dict[effect_type](last_val, val)
        # print(f'Towards pre: {towards_pre}')
        if towards_pre and not is_returning:  # checking to see if the data has started going back to pre-peturbation
            ret_gap_count += 1
            # print(f'Retgap: {ret_gap_count} at {i}')
            if ret_gap_count > returning_gap or comp_dict[effect_type](comp_val, val):
                # print(f'returning at {i}')
                is_returning = True
                ret_gap_count = 0
        elif not is_returning:
            ret_gap_count = 0

        # print(f'past pre-pet')

        if is_returning:

            if comp_dict[effect_type](comp_val, val):  # check to see if we've returned to normalcy
                # print(f'we normal at {i}')
                if dropthrough[0] == 0:  # if no dropthroughs left then we're done
                    # print('no dropthroughs left')
                    break
                else:
                    if within(val, normalcy):  # if we're within normalcy, check to see if we'll drop through in time
                        # print('need to check dropthrough')
                        does_drop_through, ind = drops_through(whys, i, normalcy, dropthrough[1])
                        # print(f'Drops thru? {does_drop_through}')
                        if does_drop_through:  # if it does drop through, go on
                            days_to_drop = ind - i
                            returner[1][2] += days_to_drop - 1
                            i = ind - 1
                        else:  # if it doesn't, then we're done
                            # print('did not drop thru')
                            break
                    dropthrough[0] -= 1
                    effect_type = -effect_type
                    comp_ind ^= 1  # bit flip from 0 to 1 and vice versa
                    comp_val = normalcy[comp_ind]
                    is_returning = False

            elif force_completion and comp_dict[effect_type](val, last_val):
                # print('moving away?')
                # check to see if the data is moving away from pre-pet again
                # assuming force_completion is numeric

                # print('Force completion active')
                # print(f'Func {comp_dict[effect_type]}, vals {val,last_val}. Ind {i}')
                # print('ddtr:')
                dn = days_to_return(whys, i - 1, func=comp_dict[-effect_type], max_nan=max_dropout)
                # print(f'{dn}')
                # print(dn)
                if dn <= force_completion:  # if we return in time
                    if last_val > high:
                        returner[1][0] += (dn - 2)
                    if last_val < low:
                        returner[1][1] += (dn - 2)
                    i += (dn - 2)
                else:  # force completion
                    # print(f'Forcing completion')
                    try:
                        ind, days_to_force, slope = forced_return(exes, whys, i - 1, normalcy, history=force_history)
                        # print(f'Completion forced at {ind} from {i-1}. Takes {days_to_force} days. Slope: {slope}')
                        returner[1][3] = 'forced'
                        returner[1][4] = i - 1
                        returner[1][5] = slope
                        to_add = days_to_force - 1
                        if last_val > high:
                            returner[1][0] += to_add
                        if last_val < low:
                            returner[1][1] += to_add
                        i = ind
                    except ValueError:
                        returner[1][3] = 'forcing error'
                        i -= 1
                    break
                # print('eob')

        if val > high:
            returner[1][0] += 1
        elif val < low:
            returner[1][1] += 1
        else:
            returner[1][2] += 1

    returner[0][1] = i

    if not has_real_val:
        returner = [[None, None], [0, 0, 0, 'dropout', None, None]]

    if returner[0][0] == returner[0][1]:  # happens sometimes when there is a dropout but an effect is registered due to
        # interpolation at the storm start
        returner = [[None, None], [0, 0, 0, 'natural', None, None]]

    return returner


def greater(a, b):
    return a > b


def lesser(a, b):
    return a < b


def within(a, b):
    return b[1] > a > b[0]


def forced_return(exes, whys, i, window, history=3):
    """
    Gives the index of a forced return and the slope of the return

    Args:
        exes: x vals
        whys: y vals
        i: index of the return begin
        window: the min and max of the return window
        history: number of points to include in the best fit

    Returns:
        tuple (index_of_return, days_to_return, slope)

    """
    # print('\nFORCING:')
    while True:
        x = exes[(i - history + 1):(i + 1)]
        y = whys[(i - history + 1):(i + 1)]
        m, b = np.polyfit(x, y, 1)
        # print(f'{m}')
        if whys[i] > window[1] and m >= 0:
            history -= 1
        elif whys[i] < window[0] and m <= 0:
            history -= 1
        elif np.isclose(m, 0):
            history -= 1
        else:
            break

        if history == 1:
            raise ValueError('Forced return impossible')

    def lin_func(index, y=whys[i], anchor=i, slope=m):
        r = y + (index - anchor) * slope
        return r

    # print('lin_func defined')

    if whys[i] > window[1]:
        func = lesser
        comp = window[1]
        # print('func def')
    elif whys[i] < window[0]:
        func = greater
        comp = window[0]
        # print('func def')
    else:
        Exception('Whoah. something weird with forced_return()')

    val = whys[i]
    n = 0
    while not func(val, comp):
        i += 1
        n += 1
        val = lin_func(index=i)
        # print(val)

    # print('finished')

    return i, n, m


def days_to_return(exes, i, func, max_nan=0):
    """
    Returns the number of days for a series to return to above/below the indexed value

    Args:
        exes: series of x vals
        i: index to start at
        func: a function, either lesser or greater as defined in this module
        max_nan: maximum allowable consecutive nans

    Returns:
        num of days to return

    """
    if func is lesser:
        # print('looking for when vals drop below comp')
        pass
    elif func is greater:
        # print('looking for when vals rise above comp')
        pass

    initial = exes[i]

    nas = 0
    n = 0
    try:
        while nas <= max_nan:
            i += 1
            n += 1
            val = exes[i]
            # print(f'Compare {val} to initial ({initial})')
            if np.isnan(val):
                nas += 1
            elif func(val, initial):
                break
    except IndexError:
        pass
    return n


def drops_through(exes, i, window, allowed):
    """
    Checks if exes drops through the window fast enough from index i

    Args:
        exes: the x data
        i: the index being checked
        window: the min and max of the window
        allowed: number of days allowed to pass through the window

    Returns:
        bool
    """

    val = exes[i]
    while within(val, window):
        i -= 1
        val = exes[i]

    if val > window[1]:
        func = lesser
        comp = window[0]
        # print('First val out of window is above. Checking to see when val goes below window')
    elif val < window[0]:
        func = greater
        comp = window[1]
        # print('First val out of window is below. Checking to see when val goes above window')
    else:
        raise Exception('Whoah. something weird with drop_through()')

    count = 0
    while count < allowed:
        i += 1
        count += 1
        val = exes[i]
        # print(val,comp)
        if func(val, comp):
            return True, i
    return False, -1


###############
'''
choice_param = 'Discharge Detrend'
choice_gauge = '02218565'
# 04249000
# 015765185
# 0209303205

results_folder = r'E:\hurricane\results'
data_folder = r'E:\hurricane\station_data\modified'


data = clean_read(os.path.join(data_folder,choice_gauge+'.csv'))
result_df = pd.read_csv(os.path.join(results_folder,choice_param+'.csv'), dtype={'Gauge':str})

for index,line in result_df.iterrows():
    if np.isnan(line['Pre-effect Window']):
        continue
    gauge = line['Gauge']
    start = line['Storm Index']
    mean = line['Pre-effect Mean']
    stddev = line['Pre-effect Stddev']

    if gauge == choice_gauge:
        break


low = mean - stddev
high = mean + stddev

(es, ee), stats = get_effect(data, choice_param, mean, stddev, start, lag=3, effect_type=1,
               returning_gap=1, dropthrough=[1,2], forcing=(3,4), max_effect=365, max_dropout=5)

plt.figure()


plt.plot(data.index,data[choice_param])
plt.axvline(start, color='red')
plt.axhline(high, color='orange')
plt.axhline(low, color='orange')
if stats[3] is not None:
    plt.axvline(es, color='green', linestyle='dashed')
    plt.axvline(ee, color='blue')
if stats[3] == 'forced':
    x1 = stats[4]
    x2 = ee
    y1 = data[choice_param][stats[4]]
    y2 = y1 + (x2-x1)*stats[5]

    fx = [x1,x2]
    fy = [y1,y2]

    plt.plot(fx,fy,color='black', linestyle='dashed')

plt.xlim(start-28,start+28)
plt.title(f'Above: {stats[0]}, Below: {stats[1]}, Between: {stats[2]} \n'
          f'Termination Type: {stats[3]}')

plt.show()

'''
