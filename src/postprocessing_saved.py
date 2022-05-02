# -*- coding: utf-8 -*-
"""
Function definitions to be called in the console or by other modules.
These functions refer only to recorders or other saved information.

Created on Mon Nov 15 11:24:08 2021
@author: wroser
"""

import os

def get_outdir():
    subfolders = [f.path for f in os.scandir('out') if f.is_dir()]
    return subfolders