# -*- coding: utf-8 -*-
"""
Created:  Thu May 12, 2022
Author:   wroser
=============================================================================
Description:

"""

import os
import tkinter as tk
from tkinter import ttk
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from postprocessing import xml_to_df

class App(tk.Tk):
    def __init__(self):
        super().__init__() # Initializes Tk() window
        self.title('Embedded Graph')
        self.minsize(600, 400)
        self.df = pd.DataFrame()
        self.lFrame = ttk.Frame(self)
        self.rFrame = ttk.Frame(self)
        self.lFrame.pack(side=tk.LEFT, expand=True, fill='both', padx=10, pady=10)
        self.rFrame.pack(side=tk.RIGHT, padx=10, pady=10)
        
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
        ttk.Button(self.selectFrame, text="Pick File", command=self.pick_file).pack(side=tk.BOTTOM)
        # ttk.Button(self.lFrame, text="File", command=get_file).pack(side=tk.BOTTOM)
        ttk.Button(self.lFrame, text="Plot", command=self.update_plot).pack()
        self.listbox = tk.Listbox(self.selectFrame, selectmode='multiple', width=30, height=30)
        for name in self.df.columns:
            self.listbox.insert('end', name)
        self.listbox.pack()
        
        # Treeview
        # self.tree = ttk.Treeview(self.selectFrame)
        # self.tree.pack()
        
    
    def update_plot(self):
        columns = [self.df.columns[i] for i in self.listbox.curselection()]
        self.ax.clear()
        for i in columns:
            self.ax.plot(self.df['time'], self.df[i],
                         linewidth=0.5)
            self.ax.grid()
            self.canvas.draw()
    #     print(self.listbox.curselection(), results)
    #     return results
        # print(self.tree.selection())
    
    def pick_file(self):
        filepath = tk.filedialog.askopenfilename(initialdir='./out', filetypes=[('XML Recorder', '*.xml')])
        self.df, self.hierarchy = xml_to_df(filepath)
        print(filepath)
        # tree = ET.parse(filepath)
        # root = tree.getroot()
        
        # # Parse data labels
        # column_names = []
        
        
        # for element in root.iter():
        #     # print(element.tag)
        #     if element.tag == 'TimeOutput':
        #         column_names.append(element[0].text)
        #     elif element.tag == 'NodeOutput':
        #         nodeTag = element.attrib['nodeTag']
        #         for response in range(len(element)):
        #             column_names.append('Node_' + nodeTag + ' ' + element[response].text)
        
        # # Parse numerical data from recorder, return numpy array
        # data = root.find('Data').text
        # data = data.strip().split('\n')
        # for i in range(len(data)):
        #     data[i] = data[i].split()
        #     for j in range(len(data[i])):
        #         data[i][j] = float(data[i][j])
        # data = np.asarray(data)
        
        # Assign to class dataframe
        # self.df = pd.DataFrame(data, columns=column_names)
        self.listbox.delete(0, tk.END)
        for name in self.df.columns:
            self.listbox.insert('end', name)
       
        # for name, i in zip(self.hierarchy, range(len(self.hierarchy))):
        #     self.tree.insert('', i, name, text=name)
        #     for response in self.hierarchy[name]:
        #         self.tree.insert(name, 'end', name + ' ' + response, text=response)

if __name__ == '__main__':
    app = App()
    app.mainloop()