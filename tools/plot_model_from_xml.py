# -*- coding: utf-8 -*-
"""
Created:  Thu Sep  8 14:40:16 2022
Author:   wroser
=============================================================================
Description:
    
"""

import tkinter as tk
from tkinter.filedialog import askopenfilename

# filename = askopenfilename(initialdir='../out')

def get_path():
    root = tk.Tk()
    root.withdraw()
    path = askopenfilename(initialdir='../out')
    # root.destroy()
    return(path)

filename = get_path()
