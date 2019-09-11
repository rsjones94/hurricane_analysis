import random
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from compression import *

random.seed(2)
np.random.seed(2)

exes = [round(random.random()*100, 3) for i in range(0,200)]
exes.sort()


def func(x):
    y = .2*math.sin(.1*x) + 0.023*x + math.sin(.002*x)\
        - 0.0018*x**1.6 + 0.00000002*(x-100)**4\
        + .05*math.sin(.5*x)
    y += np.random.normal(0,.0001)
    return y


whys = [func(x) for x in exes]

lin_end = trawl(exes, whys, 114, 0.6, -1)

val_range = lin_end
m, b, r2 = get_line(exes, whys, val_range)

nex = [exes[i] for i in val_range]
ny = [func_linear(i, m, b) for i in nex]

plt.figure()
plt.plot(exes, whys)
plt.plot(nex, ny)
plt.show()
