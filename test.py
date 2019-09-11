import random
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from compression import *

random.seed(2)
np.random.seed(2)


"""
#150, 0.01, 0.8
def func(x):
    y = .2*math.sin(.1*x) + 0.023*x + math.sin(.002*x)\
        - 0.0018*x**1.6 + 0.00000002*(x-100)**4\
        + .05*math.sin(.5*x)\
        + .4*math.cos(0.03*x+2)
    y += np.random.normal(0,noise)
    return y
"""

n = 100
noise = 0.1
thresh = 0.7

def func(x):
    y = .2*math.sin(.1*x) + 0.023*x + math.sin(.002*x)\
        - 0.0018*x**1.6 + 0.00000002*(x-100)**4\
        + .05*math.sin(.5*x)\
        + .4*math.cos(0.03*x+2)
    y += np.random.normal(0,noise)
    return y

####

exes = [round(random.random()*100, 3) for i in range(0,n)]
exes.sort()


whys = [func(x) for x in exes]

"""
lin_end = trawl(exes, whys, 114, 0.6, -1)

val_range = lin_end
m, b, r2 = get_line(exes, whys, val_range)

nex = [exes[i] for i in val_range]
ny = [func_linear(i, m, b) for i in nex]
"""

res = linear_recurse(exes, whys, thresh, None)
print(f'Result: {res}')

starts = [i[0] for i in res]
ends = [i[1] for i in res]
r2s = [i[2] for i in res]

ses = [list(i) for i in zip(starts,ends)]

plt.figure()
plt.plot(exes, whys)
for s in ses:
    plt.plot(exes[s[0]:s[1]], whys[s[0]:s[1]])

plt.plot(exes[32:100], whys[32:100])
se = [32,100]
l = get_line(exes,whys,se)
plot_line(l, se[0], se[1])

plt.show()
