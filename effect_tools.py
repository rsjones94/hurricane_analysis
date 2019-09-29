import os
import shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from read import clean_read

choice_param = 'Turb Detrend'
choice_gauge = '07263296'

results_folder = r'E:\hurricane\results'
data_folder = r'E:\hurricane\station_data\modified'

def get_effect(data, param, mean, stddev, start_index, lag=3, effect_type=1,
               dropthrough=(0,0), force_completion=None, max_effect=365):
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
        dropthrough: A tuple indicating the number of dropthroughs allowed and the number of days
                     the time series is allotted to drop through before being considered terminated
        force_completion: the number of days a returning trend can be reversed before it is forced to
                          return by calculating the best fit line for the last three returning days and
                          calculating the date of intersection. This allows an effect window to be
                          estimated even when additional storms/forcing effects follow the initial
                          peturbation. Default is None, which will never force a completion.
        max_effect: the maximum number of days an effect can continue before being terminated

    Returns:
        A list with two parts. The first is the index of the effect's end (or None, if there was
        no effect). The second is list, (days_above, days_below, days_between,
        termination_type, forcing_start, forcing_slope). termination_type can be "natural" or "forced".
        If not forced, forcing_start and forcing_slope will be None.
    """
    returner = [None, [0, 0, 0, 'natural', None, None]]

    def greater(a,b):
        return a>b
    def lesser(a,b):
        return a<b
    comp_dict = {1:greater,-1:lesser}
    def within(a,b):
        return b[1] > a > b[0]

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
        if comp_dict[effect_type](last_val,val):
            is_returning = True




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