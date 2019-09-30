import os
import shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from read import clean_read
from detrend import *

choice_param = 'Turb Detrend'
choice_gauge = '07263296'

results_folder = r'E:\hurricane\results'
data_folder = r'E:\hurricane\station_data\modified'

def get_effect(data, param, mean, stddev, start_index, lag=3, effect_type=1,
               dropthrough=[0,0], force_completion=None, max_effect=365, max_droput=5):
    """
    For a given parameter, finds the time it takes for the time series to return to normalcy
    after a peturbation

    Args:
        data: A DataFrame of gauge data
        param: the column in Data to use
        mean: the mean value of the pre-effect window
        stddev: the standard deviation of the pre-effect window
        start_index: the index of the storm peturbation
        lag: the number of days allowed for an effect to begin. Minimum is 1
        effect_type: the INITIAL expected effect of the peturbation. 1 indicates a positive effect, -1
                     indicates a negative effect
        dropthrough: A list (not a tuple) indicating the number of dropthroughs allowed and the number of days
                     the time series is allotted to drop through before being considered terminated
        force_completion: the number of days a returning trend can be reversed before it is forced to
                          return by calculating the best fit line for the last three returning days and
                          calculating the date of intersection. This allows an effect window to be
                          estimated even when additional storms/forcing effects follow the initial
                          peturbation. Default is None, which will never force a completion.
        max_effect: the maximum number of days an effect can continue before being terminated
        max_dropout: number of continues no signals before mandatory termination

    Returns:
        A list with two parts. The first is the index of the effect's end (or None, if there was
        no effect). The second is list, (days_above, days_below, days_between,
        termination_type, forcing_start, forcing_slope). termination_type can be "natural" or "forced".
        If not forced, forcing_start and forcing_slope will be None.
    """
    returner = [None, [0, 0, 0, 'natural', None, None]]


    comp_dict = {1:greater,-1:lesser}

    exes = np.array(data.index)
    whys = np.array(data[param])

    low = mean - stddev
    high = mean + stddev
    normalcy = (low,high)

    if effect_type == 1:
        comp_val = high
    elif effect_type == -1:
        comp_val = low
    else:
        raise Exception('effect_type must be 1 or -1')

    direction = None
    effect_begun = False
    i = start_index
    while lag > 0:
        lag -= 1
        i += 1
        val = whys[i]
        if comp_dict[effect_type](val,comp_val):
            effect_begun = True
    if not effect_begun:
        return returner

    is_returning = False
    while True:
        i += 1
        last_val = whys[i-1]
        val = whys[i]
        if comp_dict[effect_type](last_val,val): # checking to see if the data has started going back to pre-peturbation
            is_returning = True
        if is_returning:

            if comp_dict[effect_type](comp_val,val): # check to see if we've returned to normalcy
                if dropthrough[0] == 0: # if no dropthroughs left then we're done
                    break
                else:
                    if drops_through(exes,i,normalcy,dropthrough[1]: # if it does drop through, go on
                        dropthrough[0] -= 1
                    else: # if it doesn't, then we're done
                        break

            elif force_completion and comp_dict[effect_type](val,last_val):
                # check to see if the data is moving away from pre-pet again, force_completion is numeric
                if days_to_return(exes, i, max_nan=max_droput) <= force_completion: # if we return in time
                    pass # do nothing
                else: # force completion
                    pass # PLACEHOLDER


        if val > high:
            returner[1][0] += 1
        elif val < low:
            returner[1][1] += 1
        else:
            returner[1][2] += 1

    returner[0] = i




def greater(a,b):
    return a>b
def lesser(a,b):
    return a<b
def within(a,b):
    return b[1] > a > b[0]


def days_to_return(exes, i, max_nan=0):
    """
    Returns the days for a series to return to above/below the indexed value

    Args:
        exes: series of x vals
        i: index to start at
        max_nan: maximum allowable consecutive nans

    Returns:
        num of days to return

    """

    initial = exes[i]
    sec = exes[i+1]
    if sec > initial:
        func = lesser
    elif sec < initial:
        func = greater

    nas = 0
    n = 0
    while nas <= max_nan:
        i += 1
        n += 1
        val = exes[i]
        if np.isnan(val):
            nas += 1
        elif func(val,initial):
            break

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
    while within(val,window):
        i -= 1
        val = exes[i]

    if val > window[1]:
        func = lesser
        comp = window[0]
    elif val < window[0]:
        func = greater
        comp = window[1]
    else:
        raise Exception('Whoah. something weird with drop_through()')

    count = 0
    while count < allowed:
        i += 1
        count += 1
        val = exes[i]
        if func(val,comp):
            return True
    return False



###############


data = clean_read(os.path.join(data_folder,choice_gauge+'.csv'))
result_df = pd.read_csv(os.path.join(results_folder,choice_param+'.csv'), dtype={'Gauge':str})

result_df['Total Effect'] = np.nan
result_df['Effect Above'] = np.nan
result_df['Effect Below'] = np.nan
result_df['Dropthrough'] = np.nan
result_df['Termination'] = np.nan
result_df['Forced Start'] = np.nan
result_df['Forced Slope'] = np.nan
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

plt.figure()


plt.plot(data.index,data[choice_param])
plt.axvline(start, color='red')
plt.axhline(high, color='orange')
plt.axhline(low, color='orange')
plt.xlim(start-28,start+28)

plt.show()