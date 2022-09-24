# -*- coding: utf-8 -*-
"""
Created:  Thu May 12, 2022
Author:   wroser
=============================================================================
Description:

"""

import os
import csv
import tkinter as tk
from tkinter import ttk
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
# from postprocessing import xml_to_df
import matplotlib.pyplot as plt


class App(tk.Tk):
    def __init__(self):
        super().__init__() # Initializes Tk() window
        self.title('Embedded Graph')
        self.minsize(600, 400)
        self.lFrame = ttk.Frame(self)
        self.rFrame = ttk.Frame(self)
        self.bFrame = ttk.Frame(self)
        self.bFrame.pack(side=tk.BOTTOM, padx=10, pady=10, fill='x', expand=True)
        self.lFrame.pack(side=tk.LEFT, expand=True, fill='both', padx=10, pady=10)
        self.rFrame.pack(side=tk.RIGHT, padx=10, pady=10)
        # self.bFrame.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        # Matplotlib figure
        self.fig = mpl.figure.Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.rFrame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.rFrame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM)
        
        # X-axis selection
        self.selectFrame = ttk.LabelFrame(self.lFrame, text='text', padding=10)
        self.selectFrame.pack(side=tk.TOP, expand=True, fill='both')
        # ttk.Label(self.selectFrame, text="Hello World!").pack()
        
        # ttk.Button(self.lFrame, text="File", command=get_file).pack(side=tk.BOTTOM)
        ttk.Button(self.lFrame, text="Plot", command=self.update_plot).pack()
        self.listbox = tk.Listbox(self.selectFrame, selectmode='multiple', width=30, height=30)
        # for name in self.df.columns:
        #     self.listbox.insert('end', name)
        self.listbox.pack()
        
        # File Selection
        ttk.Button(self.bFrame, text="Pick File", command=self.pick_file).pack(side=tk.LEFT)
        self.filepath = tk.StringVar()
        self.fileentry = ttk.Entry(self.bFrame, textvariable=self.filepath, width=100)
        self.fileentry.pack(side=tk.RIGHT, fill='x', expand=True)
        
        # Variables
        self.data = np.asarray([])
        self.time = np.asarray([])
        
    
    def update_plot(self):
        self.data = np.asarray([])
        with open(self.filepath) as file:
            reader = csv.reader(file, delimiter=' ')
            tempdata = list(reader)
            self.data = np.asfarray(tempdata).T
            # self.data = np.zeros((len(col), len(tempdata)))
            self.time = np.linspace(0, 0.01*len(tempdata), len(tempdata))
            # print(self.data[0])
            for i in range(self.data.shape[0]):
                self.ax.plot(self.time, self.data[i])
            self.ax.grid()
            self.canvas.draw()
            
        self.ax.clear()
        for i in range(self.data.shape[0]):
            self.ax.plot(self.time, self.data[i],
                         linewidth=0.5)
            self.ax.grid()
            self.canvas.draw()
    
    def pick_file(self):
        self.filepath = tk.filedialog.askopenfilename(initialdir='../gm')#, filetypes=[('XML Recorder', '*.xml')])
        self.fileentry.delete(0, tk.END)
        self.fileentry.insert(0, self.filepath)
        
        

if __name__ == '__main__':
    app = App()
    app.mainloop()