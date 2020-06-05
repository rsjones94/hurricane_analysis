"""
Junk code for exploring ideas
"""

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
x_dom = 120

n = 300
noise = 0.2
thresh = None


if thresh is None:
    thresh = noise*1

def func(x):
    y = -math.log10(x)*5 + 0.00001*x**3 - 0.000002*(x+80)**3 + 1*math.sin(0.1*x) + 0.1*x
    y += np.random.normal(0,noise)
    return y


####

exes = [round(random.random()*x_dom, 3) for i in range(0,n)]
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

starts = [i[0] for i in res]
ends = [i[1] for i in res]
e_norms = [i[2] for i in res]

ses = [list(i) for i in zip(starts,ends)]

plt.figure()
plt.plot(exes, whys)
for s in ses:
    plt.plot(exes[s[0]:s[1]], whys[s[0]:s[1]])

"""
f = 32
t = 100

plt.plot(exes[f:t], whys[f:t])
se = [f,t]
l = get_line(exes,whys,se)
#plot_line(l, se[0], se[1])
preds = get_lin_values(whys[f:t],l[0],l[1])
act = whys[f:t]
plt.plot(exes[f:t],preds)
"""

plt.xlim(0,x_dom)
plt.ylim(-15,15)
plt.show()
