# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 18:17:14 2022

@author: wroser
"""

import os
import matplotlib.pyplot as plt
import pandas

# This code makes the plot interactive.
from IPython import get_ipython
ipython = get_ipython()
ipython.magic("matplotlib qt")

# Plot all nodes on sheet "nodes"
df = pandas.read_excel(r'C:\Users\wroser\Documents\Code Workshop\3D Model 2\Model_Builder.xlsm', sheet_name='nodes', usecols='C:E')

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.scatter(df['X'], df['Y'], df['Z'])