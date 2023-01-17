# -*- coding: utf-8 -*-
"""
Created:  Tue Sep 27 12:25:02 2022
Author:   wroser
=============================================================================
Description:
    
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
from Model_10_Story import __path__
import Model_10_Story.src.postprocessing as post
import numpy as np
import pandas as pd
from generic import mround, Offset_Plot, Overlap_Plot

# For ease, set default path.
_default_out_dir = __path__[0] + '/out'


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

def wall_max_drift(analysisID, case, out_dir=_default_out_dir):
    '''
    Creates plot of drifts for the walls in their in-plane directions. One plot
    for each primary direction (X and Y). (Out-of_plane plots were considered
    but did not convey much ue to rigid diaphragm constraint.) Plots are saved
    in the same directory as the source file.
    '''
    
    path = _default_out_dir + '/' + analysisID + '/' + case
    filename = 'wall_disp'
    disp_recorder = post.NodeDispRecorder(path + '\\' + filename +'.xml')
    
    # Iterables
    walls = [[['F', 'ACLT'], ['F', 'CCLT']],
             [['F', 'MPP1'], ['F', 'MPP4']]]
    dofs = 'XY'
    styles = ['v:', '^:']
    titles = ['East-West', 'North-South']
    legends = [['North CLT', 'South CLT'], ['West MPP', 'East MPP']]
    
    # Plot drift
    # Drift is only plotted in the primary direction of each wall because the
    # out-of-plane drifts of each wall tends to be the average of the in-plane
    # walls.
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 5))
    
    for i, (nodes, dof) in enumerate(zip(walls, dofs)):
        
        for node, style in zip(nodes, styles):
            
            drift_profile = disp_recorder.max_drifts(node, dof)
            drifts = [value*100 for value in drift_profile.values()]
            floors = list(drift_profile.keys())
            ax[i].plot(drifts, floors, style, linewidth=2.0)
        
    # Formatting
        ax[i].grid(True)
        ax[i].set_title(titles[i])
        ax[i].legend(legends[i])
        upper = ax[i].get_xlim()[1]
        upper = mround(upper, 0.5)
        upper = ax[i].set_xlim([0.0, upper])
        ax[i].set_ylim([1.5, 11.5])
        ax[i].set_yticks(floors)
        
    ax[0].set_ylabel('Floor')
    fig.suptitle(disp_recorder.loadcase)
    fig.supxlabel('Drift (%)')
    fig.savefig(disp_recorder.dir + '\\wall_drift_profile.png')
    


def wall_drift_history(analysisID, case, split_node, dof, out_dir=_default_out_dir, title=None, name=None):
    '''
    Creates plot of drifts for the walls in their in-plane directions. One plot
    for each primary direction (X and Y). (Out-of_plane plots were considered
    but did not convey much ue to rigid diaphragm constraint.) Plots are saved
    in the same directory as the source file.
    '''
    
    path = _default_out_dir + '/' + analysisID + '/' + case
    filename = 'wall_disp'
    disp_recorder = post.NodeDispRecorder(path + '\\' + filename +'.xml')
    
    a=disp_recorder.df
    drifts = disp_recorder.drift(split_node, dof)
    drifts = {key:value*100 for (key,value) in drifts.items()}
    
    drifts = pd.DataFrame(drifts)
    # fig = Overlap_Plot(drifts, x=disp_recorder.df['time'], overlap=0.5)
    fig = Offset_Plot(drifts, x=disp_recorder.df['time'], offset=1.5, minordiv=6)
    fig.draw(xlim=(0, 30))
    
    

    # Labels. Include axis scale.
    minor_scale = fig.offset / fig.minordiv
    scale_message = "(Vertical gridlines spaced at {:.1f}%.)".format(minor_scale)
    # props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    # fig.ax.text(0.0, 0.0, scale_message, transform=fig.ax.transAxes, fontsize=10,
    #         horizontalalignment='right', bbox=props)
    fig.ax.set_xlabel('Time (sec)')
    fig.ax.set_ylabel(scale_message)
    fig.fig.supylabel('Drift at Floor')
    
    # Title
    if title is None:
        title = split_node[1]
    fig.ax.set_title(title)
    
    # Filename
    if name is None:
        name = split_node[1]
    name = 'drift_profile_' + name
    
    fig.fig.savefig(disp_recorder.dir + '\\' + name + '.png')

def drift_four_walls(analysisID, case, out_dir=_default_out_dir):
    nodes = [['F', 'ACLT'], ['F', 'CCLT'], ['F', 'MPP1'], ['F', 'MPP4']]
    dofs = 'XXYY'
    walls = ['North', 'South', 'West', 'East']
    for split_node, dof, wall_name in zip(nodes, dofs, walls):
        title = wall_name + ' Wall Drift History (' + dof + ')'
        wall_drift_history(analysisID, case, split_node, dof, title=title, name=wall_name)

def drift_history():
    pass


if __name__ == '__main__':
    
    # %% Input for all analysis types
    analysisID = '16 Victoria'#'6 EQ xy'
    case = ['02_ChiChi_43', '08_Tohoku_225', '15_Tokachi_475', '16_Victoria_975', '25_Ferndale_MCE'][-2]
    
    # # Drift history
    # split_node = ['F', 'ACLT']
    # dof = 'X'
    # wall_drift_history(analysisID, case, split_node, dof)
    
    # Drift history, four walls
    drift_four_walls(analysisID, case)
    
    
    
    # # Drift Profile
    # wall_drift(analysisID, case)
    
    
    
    
    
    
    # %% Fourier
    # from scipy.fft import fft, fftfreq
    # analysisID = '16 Victoria yx reverse'
    # case = '16_Victoria_975'
    # path = 'C:\\Users\\wroser\\Documents\\Code Workshop\\Model_10_Story/out/' + analysisID + '/' + case
    
    # disp = post.Recorder(path + '/center_disp.xml')
    # dispx = np.array(disp.df['F5_center D1'])
    # dispy = np.array(disp.df['F5_center D2'])
    
    # dispx = np.append(dispx[:], np.zeros((1))) # Zero padding can increase curve smoothness
    # dispy = np.append(dispy[:], np.zeros((1)))
    
    # dt = disp.df['time'][1]
    # sample_rate = 1/dt
    
    # plt.figure()
    # PSDx = fft(dispx)[:len(dispx)//2]
    # PSDx = np.abs(PSDx)/len(dispx)
    # freqx = fftfreq(len(dispx), dt)[:len(dispx)//2]
    # plt.plot(freqx, PSDx)
    
    # PSDy = fft(dispy)[:len(dispy)//2]
    # PSDy = np.abs(PSDy)/len(dispy)
    # freqy = fftfreq(len(dispy), dt)[:len(dispy)//2]
    # plt.plot(freqy, PSDy)
    
    
    # plt.xlim([0, 4])
    # plt.xlabel('Frequency (Hz)')
    # plt.grid(True)
    
    
    # %% Wall Drift
    # run = '16 Victoria'
    
    # base_moment(run, 'lateralX')
    # base_moment(run, 'lateralY')
    
    # %% UFP
    # analysisID = 'hystY_nogravity'
    # case = 'hystY'
    # path = 'C:\\Users\\wroser\\Documents\\Code Workshop\\Model_10_Story/out/' + analysisID + '/' + case
    # ufp = post.Recorder(path + '/UFP_FD.xml')
    
    
    
    
    # D_L = ufp['UFP_F11_W_L e1']
    # F_L = ufp['UFP_F11_W_L P1']
    # D_R = ufp['UFP_F11_W_R e1']
    # F_R = ufp['UFP_F11_W_R P1']
    
    
    # wall = post.Recorder(path + '/wall_disp.xml')
    # top_y = wall["TopMPP1 D2"]
    
    
    # # N = 10000
    # skip=5
    # fig, ax = plt.subplots(2, 1)
    
    # ax[0].set_xlabel('Displacement (in.)')
    # ax[0].set_ylabel('Force (kip)')
    # ax[1].set_xticks([])
    # ax[1].set_ylabel('Top of Wall Disp. (in.)')
    # plt.tight_layout()
    
    # base1, = ax[0].plot(D_L, F_L, color='gainsboro')
    # base2, = ax[0].plot(D_R, F_R, color='gainsboro')
    # line1, = ax[0].plot(D_L, F_L, color='blue', linewidth=0.5)
    # line2, = ax[0].plot(D_R, F_R, color='red', linewidth=0.5, linestyle='dashdot')
    # point1, = ax[0].plot(D_L, F_L, 'o', color='blue')
    # point2, = ax[0].plot(D_R, F_R, 'o', color='red')
    
    # base3, = ax[1].plot(top_y, color='gainsboro')
    # point3, = ax[1].plot(top_y[0], 'o')
    
    # def animate(i):
    #     # ax.clear()
    #     i = i*skip
    #     # start = max(0, i-N)
    #     line1.set_xdata(D_L[0:i])
    #     line1.set_ydata(F_L[0:i])
    #     line2.set_xdata(D_R[0:i])
    #     line2.set_ydata(F_R[0:i])
    #     point1.set_xdata(D_L[i])
    #     point1.set_ydata(F_L[i])
    #     point2.set_xdata(D_R[i])
    #     point2.set_ydata(F_R[i])
    #     point3.set_xdata(i+1)
    #     point3.set_ydata(top_y[i])
    #     return line1, line2, point1, point2, point3
    
    # ani = mpl.animation.FuncAnimation(fig, animate, frames=int(len(D_L)/skip)+10, interval=20, repeat=False)
    # ani.save('ufp.mp4', writer = 'ffmpeg', fps = 20)
    
    