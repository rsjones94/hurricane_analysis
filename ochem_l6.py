import os
import shutil

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from scipy.interpolate import make_interp_spline, BSpline


def plot_entry(d, k, col):
    """

    Args:
        d: dict
        k: key

    Returns:
        nothing

    """

    exes = np.array([0,0.5,1])
    whys = np.array([d[k][0], np.max(d[k])+abs(np.diff(d[k])[0])*0.2, d[k][1]])

    xnew = np.linspace(exes.min(), exes.max(), 500)  # 300 represents number of points to make between T.min and T.max
    spl = make_interp_spline(exes, whys, k=3, bc_type='clamped')  # BSpline object
    power_smooth = spl(xnew)

    lab = k + f'\ndeltaH = {int(round(np.diff(d[k])[0],0))} kJ/mol'
    plt.plot(xnew, power_smooth, color=col, label=lab)


colors = ['black', 'royalblue', 'indianred', 'olivedrab']

p1_heats = {'Formaldehyde:Formaldehyde+': (-142.598,695.762),
            'Acetone:Acetone+': (-223.079, 540.583),
            'Benzophenone:Benzophenone+': (72.518,767.641)
            }


fontP = FontProperties()
fontP.set_size('small')

fig, ax = plt.subplots(1, figsize=(6,7))
for i,k in enumerate(p1_heats):
    plot_entry(p1_heats, k, col=colors[i])
    plt.title('Reaction Energy Diagram, Part 1')
    plt.ylabel('Heat of Formation (kJ/mol)')
    plt.xlabel('Reaction Coordinate')
ax.set_xticklabels([])
plt.tick_params(bottom=False)
fig.legend(prop=fontP, loc=7)
plt.tight_layout()
plt.grid(axis='y')
fig.show()
