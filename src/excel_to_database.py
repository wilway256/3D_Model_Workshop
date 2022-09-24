# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 11:24:08 2021

@author: wroser
"""

import pandas
import openseespy.opensees as ops

# %% Class definition
class Database:
        
    def __init__(self, filename):
        # Nodes
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
        
        # Elements
        dfEleList = pandas.read_excel(filename, sheet_name='elements', 
                                      dtype={'UID':str,
                                             'PropertyID':str,
                                             'Tag':int,
                                             'iNode':str,
                                             'jNode':str,
                                             'Group':str})
        dfEleList.fillna(value={'Group':''}, inplace=True)
        
        dfEleType = pandas.read_excel(filename, sheet_name='eleProperties')
        dfEleType = dfEleType.astype(float, copy=False, errors='ignore')
        
        dfTransf = pandas.read_excel(filename, sheet_name='eleTransf',
                                      dtype={'Tag':int,
                                             'Xvec':float,
                                             'Yvec':float,
                                             'Zvec':float})
        # Multispring
        try:
            dfMultiSpring = pandas.read_excel(filename, sheet_name='multispring',
                                              dtype={'Area':float,
                                                      'K':float})
        # blank if does not exist
        except:
            dfMultiSpring = pandas.DataFrame()
        
        # Constraints
        dfDiaphragm = pandas.read_excel(filename, sheet_name='diaphragms')
        
        # Other
        dfLoadCase = pandas.read_excel(filename, sheet_name='loadCases', 
                                       dtype={'Steps':'Int64'})
    
        dfRecorders = pandas.read_excel(filename, sheet_name='recorders', usecols="A:G",
                                       dtype={'Node DOF':str, 'Case':str, 'Envelope':str})
        dfRecorders.dropna(how='all', inplace=True)
        dfRecorders.fillna(value={'Case':''}, inplace=True)
        
        
        # Set the first column of each worksheet as the index.
        for df in [dfNode, dfFix, dfNodeMass, dfEleList, dfEleType, dfDiaphragm, dfTransf, dfLoadCase, dfMultiSpring]:
            df.set_index(df.columns[0], inplace=True)
        
        # Make dataframes class properties
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
        self.multispring =  dfMultiSpring
        
        # Instance Variables (for recorders and output)
        self.out_dir = ''
        self.active_case = ''
   
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
    
    def tag_to_name(self, node_or_ele, tag):
        df = self.node_or_ele(node_or_ele)
        
        if type(tag) == int:
            tag = df.loc[ df['Tag'] == tag ].index[0]
            
        elif type(tag) == list:
            for i in range(len(tag)):
                tag[i] = df.loc[ df['Tag'] == tag[i] ].index[0]
        
        return tag
    
    def get_ele_tag(self, eleUID):
        tag = int(self.ele.at[eleUID, 'Tag'])
        return tag
    
    def get_tag(self, node_or_ele, UID):
        
        df = self.node_or_ele(node_or_ele)
        
        if type(UID) == str:
            UID = int(df.at[UID, 'Tag'])
            
        elif type(UID) == list:
            for i in range(len(UID)):
                UID[i] = int(df.at[UID[i], 'Tag'])
        
        return UID
    
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

    def get_subset(self, node_or_ele, name, tag=False):
        UID_list = []
        
        # Are we parsing nodes or elements?
        if node_or_ele == 'node':
            df = self.node
        elif node_or_ele == 'ele':
            df = self.ele
        else:
            raise ValueError("Acceptable arguments are 'node' or 'ele'.")
        
        for i in range(len(df.index)):
            if (name + ';') in df.iloc[i]['Group']:
                if tag:
                    raise ValueError('Feature not added yet.')
                    # node_list.append(self.get_tag(df.iloc[i].name))
                else:
                    UID_list.append(df.iloc[i].name)
        return UID_list
    
    def parse(self, node_or_ele, string):
        '''
        Returns list of node or element names.

        Parameters
        ----------
        node_or_ele : string
            Must be 'node' or 'ele'.
        string : string
            Values in command:argument format, separated by semicolons followed
            by spaces. All commands except NAME can be combined to return a list
            of only the elements/nodes that satisfy all criteria,
            Commands:
                NAME: Gets specific node or element.
                CONT: Node or element name contains argument.
                BEGIN: Name starts with argument.
                HASNT: Name does not contain argument string.
                GRP: List of nodes/elements with given group tag.
                NOT: List of nodes/elements without group tag.
        '''
        
        # Are we parsing nodes or elements?
        if node_or_ele == 'node':
            df = self.node
        elif node_or_ele == 'ele':
            df = self.ele
        else:
            raise ValueError("Acceptable arguments are 'node' or 'ele'.")
        
        args = string.split('; ')
        UID_list = []
        for arg in args:
            # Note: Using Python 3.8. match/case not available.
            cmd, value = arg.split(':')
            if cmd == 'NAME':
                subset = [value]
            elif cmd == 'GRP':
                subset = self.get_subset(node_or_ele, value)
            elif cmd == 'CONT':
                subset = []
                for name in df.index:
                    if value in name:
                        subset.append(name)
            elif cmd == 'HASNT':
                subset = []
                for name in df.index:
                    if value not in name:
                        subset.append(name)
            elif cmd == 'NOT':
                subset = list(set(self.get_subset('node', ''))\
                              .difference(self.get_subset('node', 'F2')))
            elif cmd == 'BEGIN':
                subset = []
                for name in df.index:
                    if name.startswith(value):
                        subset.append(name)
            else:
                raise ValueError('Invalid argument: ' + cmd)
            
            if UID_list != []:
                UID_list = list(set(UID_list).intersection(subset))
            else:
                UID_list = subset
        return UID_list
    
    def node_or_ele(self, node_or_ele):
        # Are we parsing nodes or elements?
        if node_or_ele == 'node':
            df = self.node
        elif node_or_ele == 'ele':
            df = self.ele
        else:
            raise ValueError("Acceptable arguments are 'node' or 'ele'.")
        
        return df


if __name__ == '__main__':
    import os
    os.chdir(r'../')
    db = Database(r'Model_Builder.xlsm')
    
    a = db.parse('ele', 'GRP:')