# -*- coding: utf-8 -*-
"""
Created:  Tue Sep 27 12:25:02 2022
Author:   wroser
=============================================================================
Description:
    
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import Model_10_Story.src.postprocessing as post
import numpy as np
import pandas as pd


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
    
    # %% Drift
    analysisID = '6 EQ xy'
    case = ['02_ChiChi_43', '08_Tohoku_225', '15_Tokachi_475', '25_Ferndale_MCE'][2]
    path = 'C:\\Users\\wroser\\Documents\\Code Workshop\\Model_10_Story/out/' + analysisID + '/' + case
    
    
    filename = 'center_disp'
    node = ['F', '_center']
    dof = 'X'
    
    disp_recorder = post.Recorder(path + '/' + filename +'.xml')
    direction = {'X': ' D1', 'Y':' D2'}
    time = disp_recorder.df['time']
    
    # plt.figure()
    profile = {}
    
    for floor in range(2, 12):
        nodeUIDi = node[0] + str(floor) + node[1]
        dispi = np.array(disp_recorder.df[nodeUIDi + direction[dof]])
        zi = disp_recorder.info.loc[nodeUIDi, 'Z']
        
        try:
            nodeUIDj = node[0] + str(floor-1) + node[1]
            dispj = np.array(disp_recorder.df[nodeUIDj + direction[dof]])
            zj = disp_recorder.info.loc[nodeUIDj, 'Z']
        except:
            dispj = np.zeros(dispi.shape)
            zj = 0
        
        drift = (dispi - dispj) / (zi - zj)
        # plt.plot(time, drift)
        
        profile[floor] = max(abs(drift))
    
    fig, ax = plt.subplots(figsize=(4, 8))
    # ax.grid(True)
    bar_index = np.arange(len(profile))
    bar_values = [value*100 for value in profile.values()]
    # bar_strval = ['{:.2f}'.format(value) for value in bar_values]
    bar_floors = list(profile.keys())
    ax.barh(bar_index, bar_values, tick_label=bar_floors)
    for i, drift in enumerate(bar_values):
        ax.text(min(bar_values)/2, i, '{:.2f}%'.format(drift), ha='center', va='center', color='white')
    
    ax.set_xlabel('Drift (%)')
    ax.set_ylabel('Floor')
    ax.set_title(case)
    
    
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
    
    