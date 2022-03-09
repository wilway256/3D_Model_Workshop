# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 17:24:45 2022

@author: wroser
"""

def assign_nodel_loads(db):
    loadList = db.nodeLoad
    dirmap = {'X':1, 'Y':2, 'Z':3, 'MX':4, 'MY':5, 'MZ':6}
    