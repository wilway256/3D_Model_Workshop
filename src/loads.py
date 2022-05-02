# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 17:24:45 2022

@author: wroser
"""

import openseespy.opensees as ops

def apply_nodal_loads(db, pattern):
    loadList = db.nodeLoad
    dirmap = {'X':0, 'Y':1, 'Z':2, 'MX':3, 'MY':4, 'MZ':5}
    
    for index, row in loadList.iterrows():
        if loadList['Pattern'][index] == pattern:
            tag = db.get_node_tag(loadList['Node'][index])
            loadValue = loadList['Load'][index]
            load = [0.0]*6 # 6 degrees of freedom
            dirTag = dirmap[ loadList['Direction'][index] ]
            load[dirTag] = loadValue
            ops.load(tag, *load)

