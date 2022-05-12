# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 11:24:08 2021

@author: wroser
"""

import pandas
# import sqlite3
# %% Dataframes
def initialize_database(filename):
    # %%% Nodes
    dfNode = pandas.read_excel(filename, sheet_name='nodes',
                                  dtype={'Tag':int,
                                         'X':float,
                                         'Y':float,
                                         'Z':float,
                                         'Group':str})
    
    dfFix = pandas.read_excel(filename, sheet_name='nodeFix')
    dfFix.iloc[:, 1:] = dfFix.iloc[:, 1:]=='Fixed'
    
    dfNodeMass = pandas.read_excel(filename, sheet_name='nodeMass',
                                   dtype={'X':float, 'RX':float,
                                          'Y':float, 'RY':float,
                                          'Z':float, 'RZ':float})
    
    dfNodeLoad = pandas.read_excel(filename, sheet_name='nodeLoads',
                                   dtype={'Node':str,
                                          'Load':float,
                                          'Direction':str,
                                          'Pattern':str})
    
    # %%% Elements
    dfEleList = pandas.read_excel(filename, sheet_name='elements', 
                                  dtype={'Element':str,
                                         'PropertyID':str,
                                         'Tag':int,
                                         'iNode':str,
                                         'jNode':str,
                                         'Group':str})
    
    dfEleType = pandas.read_excel(filename, sheet_name='eleProperties')
    dfEleType = dfEleType.astype(float, copy=False, errors='ignore')
    
    dfTransf = pandas.read_excel(filename, sheet_name='eleTransf',
                                  dtype={'Tag':int,
                                         'Xvec':float,
                                         'Yvec':float,
                                         'Zvec':float})
    
    # %%% Constraints
    dfDiaphragm = pandas.read_excel(filename, sheet_name='diaphragms')
    
    # %%% Other
    dfLoadCase = pandas.read_excel(filename, sheet_name='loadCases', 
                                   dtype={'Steps':'Int64'})

    dfRecorders = pandas.read_excel(filename, sheet_name='recorders', usecols="A:G",
                                   dtype={'Node DOF':str, 'Case':str, 'Envelope':str})
    dfRecorders.dropna(how='all', inplace=True)
    dfRecorders.fillna(value={'Case':''}, inplace=True)
    
    
    # %% Set the first column of each worksheet as the index.
    for df in [dfNode, dfFix, dfNodeMass, dfEleList, dfEleType, dfDiaphragm, dfTransf, dfLoadCase]:
        df.set_index(df.columns[0], inplace=True)
    
    database = Database(dfNode, dfFix, dfNodeMass, dfNodeLoad, dfEleList, dfEleType, dfTransf, dfDiaphragm, dfLoadCase, dfRecorders)
    
    return database

# %% Class definition
class Database:
    
    def __init__(self, dfNode, dfFix, dfNodeMass, dfNodeLoad, dfEleList, dfEleType, dfTransf, dfDiaphragm, dfLoadCase, dfRecorders):
        self.node = dfNode
        self.fixity = dfFix
        self.nodeMass = dfNodeMass
        self.nodeLoad = dfNodeLoad
        self.ele = dfEleList
        self.eleData = dfEleType
        self.transf = dfTransf
        self.diaphragm = dfDiaphragm
        self.loadCase = dfLoadCase
        self.recorders = dfRecorders
    
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
    
    def get_node_subset(self, name, tag=False):
        node_list = []
        for i in range(len(self.node.index)):
            if (name + ';') in self.node.iloc[i]['Group']:
                if tag:
                    node_list.append(self.get_node_tag(self.node.iloc[i].name))
                else:
                    node_list.append(self.node.iloc[i].name)
        return node_list
    
    def get_ele_subset(self, name, tag=False):
        node_list = []
        for i in range(len(self.ele.index)):
            if (name + ';') in self.node.iloc[i]['Group']:
                if tag:
                    node_list.append(self.get_node_tag(self.node.iloc[i].name))
                else:
                    node_list.append(self.node.iloc[i].name)
        return node_list


if __name__ == '__main__':
    import os
    os.chdir(r'../')
    db = initialize_database(r'Model_Builder.xlsm')