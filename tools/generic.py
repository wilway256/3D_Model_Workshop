# -*- coding: utf-8 -*-
"""
Created:  Thu Nov 10 08:00:28 2022
Author:   wroser
=============================================================================
Description:
    Code I will definitely reuse elsewhere. Not specific to project.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog as fd




def select_file(message='Select Files'):
    
    # Open fake root. Needed to supress fake tk window. See https://stackoverflow.com/questions/59018846/hide-tk-window-when-using-filedialog
    root = tk.Tk()
    root.attributes("-alpha", 0)
    
    # 
    # path = fd.askdirectory(title=message)
    path = fd.askopenfiles(title=message)
    
    # Close fake window
    root.destroy()
    
    return path

def animate_plot(x, y, N, skip=1, name='animation', path='', show=False):
    fig, ax = plt.subplots()

    line, = ax.plot(x, y)
    
    def animate(i):
        # ax.clear()
        i = i*skip
        start = max(0, i-N)
        line.set_xdata(x[start:i])
        line.set_ydata(y[start:i])
        return line
    
    ani = mpl.animation.FuncAnimation(fig, animate, frames=int(len(x)/skip)+N, interval=100, repeat=False)
    
    if show == True:
        savepath = path + '/' + name + '.mp4'
    elif path == '':
        savepath = name + '.mp4'
    else:
        savepath = path + '/' + name + '.mp4'
    
    ani.save(savepath, writer = 'ffmpeg', fps = 20)
    
    return ani
    

# t = np.linspace(0, 5)
# x = 4*np.cos(t)
# y = np.sin(t)
# animate_plot(x, y, 10)
