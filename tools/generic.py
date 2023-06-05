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
import pandas as pd
import logging


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

def mround(number, multiple):
    number = multiple * np.ceil(number / multiple)
    return number

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

class Overlap_Plot():
    
    def __init__(self, N_or_data, x=None, rownames=None, lbwh=[0.1, 0.1, 0.85, 0.8], overlap=0.0):
        if isinstance(N_or_data, int):
            self.count = N_or_data
            self.data = None
        elif isinstance(N_or_data, np.ndarray):
            self.data = self.set_data(N_or_data, rownames)
            self.count = self.data.shape[1]
        elif isinstance(N_or_data, pd.DataFrame):
            self.data = N_or_data
            self.count = self.data.shape[1]
        else:
            raise TypeError('Input must be integer (creates blank array) or a pandas dataframe or numpy array.')
            
        self.x = x
        self.fig, self.axes = plt.subplots(self.count, 1, figsize=(6.5, 9), sharex=True, sharey=True)
        self.resize(lbwh, overlap)
    
    def resize(self, lbwh, overlap=1.0):
        n = self.count
        left, bottom, width, height = lbwh
        hi = height * (1 + overlap) / (n + overlap)
        
        for i, ax in enumerate(self.axes):
            bi = bottom + height * max(0, (i) / (n + overlap))
            ax.set_position([left, bi, width, hi])
            ax.set_yticks((-0.5, 0, 0.5))
            if i != 0:
                ax.spines.bottom.set_visible(False)
                print(i, ax.get_xticks())
                # ax.set_xticks([])
            if i < n-1:
                ax.spines.top.set_visible(False)   
            # ax.set_yticks([0.0])
            ax.set_facecolor("None")
            ax.grid('major')
        
    def set_data(self, data, headers=None):
        if isinstance(data, pd.Dataframe):
            self.data = data
        elif isinstance(data, np.ndarray):
            self.data = pd.Dataframe(data)
        if isinstance(headers, list):
            self.data.columns = headers
    
    def draw(self, xlim=()):
        
        for i, col in enumerate(self.data):
            if self.x is None:
                self.axes[i].plot(self.data[col])
            else:
                self.axes[i].plot(self.x, self.data[col])
            self.axes[i].set_ylabel(col)
            
        self.axes[-1].tick_params(labelbottom=False)
        self.axes[0].tick_params(labelbottom=True)
        if len(xlim) == 2:
            self.axes[0].set_xlim(xlim)

class Offset_Plot():
    
    def __init__(self, data, x=None, rownames=None, offset=1.0, minordiv=None):
        self.offset = offset
        self.minordiv = minordiv
        if isinstance(data, np.ndarray):
            self.data = self.set_data(data, rownames)
            self.count = self.data.shape[1]
        elif isinstance(data, pd.DataFrame):
            self.data = data
            self.count = self.data.shape[1]
        else:
            raise TypeError('Input must be integer (creates blank array) or numpy array.')
            
        self.x = x
        self.fig, self.ax = plt.subplots(1, 1, figsize=(6.5, 9), sharex=True, constrained_layout=True)
        # self.resize(lbwh, overlap)
    
    # def resize(self, lbwh, overlap=1.0):
    #     n = self.count
    #     left, bottom, width, height = lbwh
    #     hi = height * (1 + overlap) / (n + overlap)
        
    #     for i, ax in enumerate(self.axes):
    #         bi = bottom + height * max(0, (i) / (n + overlap))
    #         ax.set_position([left, bi, width, hi])
    #         if i != 0:
    #             ax.spines.bottom.set_visible(False)
    #             print(i, ax.get_xticks())
    #             # ax.set_xticks([])
    #         if i < n-1:
    #             ax.spines.top.set_visible(False)   
    #         ax.set_yticks([0.0])
    #         ax.set_facecolor("None")
    #         ax.grid('major')
        
    def set_data(self, data, headers=None):
        if isinstance(data, pd.Dataframe):
            self.data = data
        elif isinstance(data, np.ndarray):
            self.data = pd.Dataframe(data)
        if isinstance(headers, list):
            self.data.columns = headers
    
    def draw(self, xlim=()):
        yticks = []
        for i, col in enumerate(self.data):
            yticks.append(i*self.offset)
            if self.x is None:
                self.ax.plot(self.data[col] + i*self.offset, color='b')
            else:
                self.ax.plot(self.x, self.data[col] + i*self.offset, color='b')
        self.ax.set_yticks(yticks)
        self.ax.set_yticklabels([str(col) for col in self.data.columns])
        
        self.ax.minorticks_on()
        # ax.tick_params(axis='x', which='minor')
        
        self.ax.grid(visible=True, which='major')
        minor_locator = mpl.ticker.AutoMinorLocator(self.minordiv)
        self.ax.yaxis.set_minor_locator(minor_locator)
        self.ax.grid(which='minor', linestyle=':')
        
        # self.axes[-1].tick_params(labelbottom=False)
        # self.axes[0].tick_params(labelbottom=True)
        if len(xlim) == 2:
            self.ax.set_xlim(xlim)
    
# Custom formatter for logging module
class MyFormatter(logging.Formatter):
    '''
    Allows each level of the logging module to have a different format.
    Source: https://stackoverflow.com/questions/14844970/modifying-logging-message-format-based-on-message-logging-level-in-python3
    '''
    err_fmt  = "ERROR: %(module)s: Line %(lineno)d: %(message)s"
    dbg_fmt  = "%(asctime)s %(message)s"

    def __init__(self):
        super().__init__(fmt="%(levelno)d: %(msg)s", datefmt=None, style='%')  
    
    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = MyFormatter.dbg_fmt

        elif record.levelno == logging.ERROR:
            self._style._fmt = MyFormatter.err_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result
    
# t = np.linspace(0, 5)
# x = 4*np.cos(t)
# y = np.sin(t)
# animate_plot(x, y, 10)
