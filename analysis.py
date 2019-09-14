import os
import time

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from read import *
from compression import *


parent = r'E:\hurricane\station_data\Finished_Stations'
files = os.listdir(parent)

col = 'Turb'
working = os.path.join(parent, files[50])

data = clean_read(working)
sub = data[['Date', col]]
nodata_indices = sub[col].index[sub[col].apply(np.isnan)]

"""
##
plt.figure()
plt.plot([i for i in sub.index], sub[col])

sub.plot(x='Date', y=col)

plt.show()
"""

'''

ind = (10400,10700)
subsub = sub.loc[ind[0]:ind[1]]
exes = [i for i in range(ind[0],ind[1])]
whys = sub[col][ind[0]:ind[1]]

plt.plot(exes, whys)
dev = window_stddev(whys, 14, step=1)
print(f'Dev: {dev}')

subsub_nonan = subsub.dropna()
exes_nonan = subsub_nonan.index
whys_nonan = subsub_nonan[col]

res = linear_recurse(exes_nonan, whys_nonan, threshold=dev)

starts = [i[0] for i in res]
ends = [i[1] for i in res]
e_norms = [i[2] for i in res]

ses = [list(i) for i in zip(starts,ends)]

for s in ses:
    plt.plot(exes_nonan[s[0]:s[1]], whys_nonan[s[0]:s[1]])

"""
for i in range(1,15):
    print(f'Dev for step {i}: {window_stddev(whys, 28, step=i)}')

for i in range(2,28):
    print(f'Dev for window {i}: {window_stddev(whys, i, step=1)}')
"""
'''

ind = 10485
width = 56*8
history = int(width/2)

start = ind-int(width/2)
end = ind+int(width/2)

dev = typical_stddev(data[col], at_index=ind, history_length=history, window_size=14, step=3)
segs = segment_window(data, col, dev, ind, width=width)

#plt.plot(data.index[start:(end+1)], data[col][start:(end+1)], linewidth=3)
for seg in segs:
    plt.plot(data.index[seg[0]:(seg[1]+1)], data[col][seg[0]:(seg[1]+1)])
plt.axvline(ind, color='red', linewidth=1, linestyle='dashed')