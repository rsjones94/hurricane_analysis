import random
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from compression import *

random.seed(2)

exes = [round(random.random()*100, 3) for i in range(0,200)]
exes.sort()


def func(x):
    y = .2*math.sin(.1*x) + 0.023*x + math.sin(.002*x)\
        - 0.0018*x**1.6 + 0.00000002*(x-100)**4\
        + .05*math.sin(.5*x)
    y += np.random.normal(0,.04)
    return y


whys = [func(x) for x in exes]

plt.figure()
plt.plot(exes, whys)
plt.show()
