# -*- coding: utf-8 -*-
"""
Created:  Tue Sep 27 12:25:02 2022
Author:   wroser
=============================================================================
Description:
    
"""

import matplotlib.pyplot as plt
import Model_10_Story.src.postprocessing as post


def base_moment(analysisID, case):#, pairs_of_columns):
    path = 'C:\\Users\\wroser\\Documents\\Code Workshop\\Model_10_Story/out/' + analysisID + '/' + case
    
    moment = post.Recorder(path + '/wall_base_forces.xml')
    disp = post.Recorder(path + '/base_rotation.xml')
    
    for Mdof, dispdof, sign in zip(['Mx_1', 'My_1'], ['D4', 'D5'], [[-1, 1], [1, -1]]):
        momentX = moment.df_dof(Mdof)
        dispRX = disp.df_dof(dispdof)
        sorted_disp_nodes = [x[0] for x in moment.nodes.values()]
        unsorted_disp_nodes = [x.split(' ')[0] for x in list(dispRX.columns)]
        fig, ax = plt.subplots()
        for i, node in enumerate(sorted_disp_nodes):
            j = unsorted_disp_nodes.index(node)
            # sorted_disp_df.iloc[:, i] = 
            ax.plot(dispRX.iloc[:, j]*sign[0], momentX.iloc[:, i]*sign[1], '-')
        ax.legend(['CLT N', 'CLT S', 'MPP W', 'MPP E'])
        ax.set_xlabel('Rotation (rad)')
        ax.set_ylabel('Moment (kip-in)')
        ax.set_title(case)
        ax.grid()
    
    return moment, disp

def wall_drift(analysisID, case):
    
    path = 'C:\\Users\\wroser\\Documents\\Code Workshop\\Model_10_Story/out/' + analysisID + '/' + case
    
    moment = post.Recorder(path + '/wall_base_forces.xml')
    disp = post.Recorder(path + '/wall_disp.xml')

if __name__ == '__main__':
    
    run = 'lateralXYD_800'
    
    base_moment(run, 'lateralX')
    base_moment(run, 'lateralY')
    
    