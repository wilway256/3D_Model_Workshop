# -*- coding: utf-8 -*-
"""
Created:  Mon Oct  3 13:03:39 2022
Author:   wroser
=============================================================================
Description:
    
"""

import numpy as np
import matplotlib.pyplot as plt

from Model_10_Story.src.excel_to_database import Database
from Model_10_Story.src.postprocessing import Recorder



db = Database(r'C:\Users\wroser\Documents\Code Workshop\Model_10_Story\out\eigen\Model_Builder.xlsm')

for mode in '123456789':

    mode1 = Recorder(r'C:\Users\wroser\Documents\Code Workshop\Model_10_Story\out\eigen\eigen\eigen0' + mode + '.xml', db=db)
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Mode ' + mode)
    
    sfac = 200
    # print(mode1.path)
    for ele in db.parse('ele', 'GRP:wall'):
        
        node1 = db.ele.loc[ele, 'iNode']
        node2 = db.ele.loc[ele, 'jNode']
        
        test = node1 + ' E'+mode+'1' in mode1.df.columns and node2 + ' E'+mode+'1' in mode1.df.columns or\
            node1 + ' E'+mode+'2' in mode1.df.columns and node2 + ' E'+mode+'2' in mode1.df.columns or\
            node1 + ' E'+mode+'3' in mode1.df.columns and node2 + ' E'+mode+'3' in mode1.df.columns
        
        # print(test, node1, node2)
        if test:
            # print('hello')
            # break
            coord = np.zeros([2, 3])
            coord[0, :] = db.node_coord(node1)
            coord[1, :] = db.node_coord(node2)
            
            coord[0, 0] += mode1.df.loc[0, node1 + ' E'+mode+'1'] * sfac
            coord[0, 1] += mode1.df.loc[0, node1 + ' E'+mode+'2'] * sfac
            coord[0, 2] += mode1.df.loc[0, node1 + ' E'+mode+'3'] * sfac
            coord[1, 0] += mode1.df.loc[0, node2 + ' E'+mode+'1'] * sfac
            coord[1, 1] += mode1.df.loc[0, node2 + ' E'+mode+'2'] * sfac
            coord[1, 2] += mode1.df.loc[0, node2 + ' E'+mode+'3'] * sfac
            
            ax.plot(coord[:, 0], coord[:, 1], coord[:, 2], color='blue')
        
    
    ax.set_box_aspect(aspect = (1,1,3))

# coords = np.zeros([len(ops.getNodeTags()), 3])
# for i, tag in enumerate(ops.getNodeTags()):
#     coords[i,:] = coords[i,:] + np.asarray(ops.nodeCoord(tag))
#     coords[i,:] = coords[i,:] + np.asarray(ops.nodeDisp(tag)[0:3]) * factor

# ax.scatter(coords[:,0], coords[:,1], coords[:,2], marker='+')