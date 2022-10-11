# -*- coding: utf-8 -*-
"""
Created:  Fri Sep 23 14:41:19 2022
Author:   wroser
=============================================================================
Description:
    Overhaul of xml_to_graph.py.
"""

# import os
import tkinter as tk
from tkinter import ttk
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# import xml.etree.ElementTree as ET
# import numpy as np
import pandas as pd
from src.postprocessing import xml_to_df
from functools import partial

# Class definition for tkinter window
class App(tk.Tk):
    def __init__(self):
        
        # Iterables
        self.data = {}
        self.hierarchy = {}
        self.listbox = {}
        self.varFrame = {}
        
        # Data
        
        self.data['X'] = pd.DataFrame()
        self.data['Y'] = pd.DataFrame()
        
        
        
        # Basic Window Layout
        super().__init__() # Initializes Tk() window
        self.title('Embedded Graph')
        self.minsize(600, 400)
        
        self.frame_left = ttk.Frame(self)
        self.frame_left.pack(side=tk.LEFT, expand=True, fill='both')
        self.frame_ui = ttk.Notebook(self.frame_left)
        self.frame_plot = ttk.Frame(self)
        self.frame_ui.pack(side=tk.TOP, expand=True, fill='both', padx=10, pady=10, anchor=tk.N)
        self.frame_plot.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.variables = ttk.Frame(self.frame_ui)
        # self.ui_lower = ttk.Frame(self.frame_left).pack()
        self.plot_options = ttk.Frame(self.frame_ui)
        self.frame_ui.add(self.variables, text=('Variables'))
        self.frame_ui.add(self.plot_options, text=('Plot Options'))
        
        # Matplotlib figure
        self.fig = mpl.figure.Figure(figsize=(10, 8), dpi=100)
        mpl.pyplot.style.use('seaborn-whitegrid')
        self.ax = self.fig.add_subplot(1, 1, 1)
        # self.ax.grid()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_plot)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_plot)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM)
        
        # Make two frames for selecting two variables to graph
        
        
        
        # X-axis selection
        for var in ['X', 'Y']:
            self.varFrame[var] = ttk.Frame(self.variables)
            self.varFrame[var].pack(side=tk.LEFT)
            # self.frame_ui.add(self.varFrame[var], text=(var+'-axis')) # Adds tab to ttk notebook
            
            # Listbox for selecting data
            selectFrame = ttk.LabelFrame(self.varFrame[var], text=var, padding=10)
            selectFrame.pack(side=tk.TOP, expand=True, fill='both')
            
            self.listbox[var] = tk.Listbox(selectFrame, selectmode='multiple', width=30, height=30, exportselection=0)
            for name in self.data[var].columns:
                self.listbox[var].insert('end', name)
            self.listbox[var].pack()
                    
            
            # Buttons
            ttk.Button(selectFrame, text="Pick File", command=partial(self.pick_file, var)).pack(side=tk.BOTTOM)
        
        
        
        ttk.Button(self.frame_left, text="Plot", command=self.update_plot).pack(side=tk.BOTTOM, expand=True)
        
        # Figure control window
        fields = ['Title', 'X Label', 'Y Label', 'X Limit <', 'X Limit >', 'Y Limit v', 'Y Limit ^']
        self.entries = {}
        for field in fields:
            row = ttk.Frame(self.plot_options)
            label = ttk.Label(row, width=25, text=field+': ', anchor='w')
            entry = ttk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.entries[field] = entry
        # self.xlim_lower = tk.StringVar()
        # self.xlim_lower = ttk.Entry(self.plot_options)
    
    def update_plot(self):
        # Wipe current plot
        self.ax.clear()
        
        # Get data
        colsX = [self.data['X'].columns[i] for i in self.listbox['X'].curselection()]
        colsX = ['time'] if colsX == [] else colsX
        colsY = [self.data['Y'].columns[i] for i in self.listbox['Y'].curselection()]
        
        if len(colsX) != len(colsY) and len(colsX) != 1:
            print('Must select the same number of variables or only one x-variable.')
            return
        
        # One independent variable
        if len(colsX) == 1:
            for headerY in colsY:
                self.ax.plot(self.data['X'][colsX[0]],
                             self.data['Y'][headerY],
                              linewidth=0.5)
                # self.ax.grid()
                # self.canvas.draw()
        
            
            
            
            
        # Multiple independent variables
        else:
        
            for headerX, headerY in zip(colsX, colsY):
                self.ax.plot(self.data['X'][headerX],
                             self.data['Y'][headerY],
                              linewidth=0.5)
                # self.ax.grid()
                # self.canvas.draw()
        
        # Plot options
        self.ax.set_title(self.entries['Title'].get())
        self.ax.set_xlabel(self.entries['X Label'].get())
        self.ax.set_ylabel(self.entries['Y Label'].get())
        try:
            self.ax.set_xlim(left=float(self.entries['X Limit <'].get()),
                              right=float(self.entries['X Limit >'].get()))
        except:
            pass
        try:
            self.ax.set_ylim(bottom=float(self.entries['Y Limit v'].get()),
                              top=float(self.entries['Y Limit ^'].get()))
        except:
            pass
        # self.ax.grid()
        self.canvas.draw()
    
    def pick_file(self, var):
        filepath = tk.filedialog.askopenfilename(initialdir='./out', filetypes=[('XML Recorder', '*.xml')])
        self.data[var], self.hierarchy[var], _ = xml_to_df(filepath)
        print(var, filepath)
        self.listbox[var].delete(0, tk.END)
        for name in self.data[var].columns:
            self.listbox[var].insert('end', name)

if __name__ == '__main__':
    app = App()
    app.mainloop()