import os
import time

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from read import *
from compression import *

analyze = True

parent = r'E:\hurricane\station_data\Finished_Stations'
files = os.listdir(parent)

col = 'SS'
for i,file in enumerate(files):
    print(f'Checking {file}, file {i} of {len(files)}')
    working = os.path.join(parent, file)
    data = clean_read(working)
    sub = data[['Date', col]]

    if len(sub.dropna() != 0):
        break





if analyze:
    ind = 9800

    hist = int(7*8)
    wind = int(7*1)
    dev = typical_stddev(data[col], at_index=ind, history_length=hist, window_size=wind, step=2)

    width = 7*16
    segs = segment_window(data, col, dev, ind, width=width)

    #plt.plot(data.index[start:(end)], data[col][start:(end)], linewidth=3)
    for seg in segs:
        plt.plot(data.index[seg[0]:(seg[1])], data[col][seg[0]:(seg[1])])
    plt.axvline(ind, color='red', linewidth=1, linestyle='dashed')
    plt.axvline(ind+wind, color='orange', linewidth=1, linestyle='dashed')
    plt.axvline(ind-wind, color='orange', linewidth=1, linestyle='dashed')

else:
    plt.plot(data.index, data[col])
