# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 11:24:08 2021

@author: wroser
"""

import pandas
# import sqlite3

def initialize_database(filename):
    
    dfNode = pandas.read_excel(filename, sheet_name='nodes',
                                  dtype={'Tag':int,
                                         'X':float,
                                         'Y':float,
                                         'Z':float})
    
    dfFix = pandas.read_excel(filename, sheet_name='nodeFix')
    dfFix = dfFix.iloc[:]=='Fixed'
    
    dfNodeMass = pandas.read_excel(filename, sheet_name='nodeMass',
                                   dtype={'X':float, 'RX':float,
                                          'Y':float, 'RY':float,
                                          'Z':float, 'RZ':float})
    
    dfEleList = pandas.read_excel(filename, sheet_name='elements', 
                                  dtype={'Element':str,
                                         'PropertyID':str,
                                         'Tag':int,
                                         'iNode':str,
                                         'jNode':str})
    
    dfEleType = pandas.read_excel(filename, sheet_name='eleProperties')
    dfEleType = dfEleType.astype(float, copy=False, errors='ignore')
    
    dfDiaphragm = pandas.read_excel(filename, sheet_name='diaphragms')
    
    dfTransf = pandas.read_excel(filename, sheet_name='eleTransf', 
                                  dtype={'Tag':int,
                                         'Xvec':float,
                                         'Yvec':float,
                                         'Zvec':float})
    
    # Set the first column of each worksheet as the index.
    for df in [dfNode, dfFix, dfEleList, dfEleType, dfDiaphragm, dfTransf]:
        df.set_index(df.columns[0], inplace=True)
    
    class Database:
        node = dfNode
        fixity = dfFix
        nodeMass = dfNodeMass
        ele = dfEleList
        eleData = dfEleType
        transf = dfTransf
        diaphragm = dfDiaphragm
        
        def get_node_list(self):
            index_list = list(self.node.index.values)
            return index_list
        
        def get_ele_list(self):
            index_list = list(self.ele.index.values)
            return index_list
        
        def get_node_tag(self, nodeUID):
            tag = int(self.node.at[nodeUID, 'Tag'])
            return tag
        
        def get_node_name(self, nodeTag):
            df = self.node
            name = df.loc[ df['Tag'] == nodeTag ].index[0]
            return name
        
        def get_ele_tag(self, eleUID):
            tag = int(self.ele.at[eleUID, 'Tag'])
            return tag
    
    database = Database()
    
    return database


if __name__ == '__main__':
    import os
    os.chdir(r'../')
    db = initialize_database(r'Model_Data.xlsm')