# -*- coding: utf-8 -*-
"""
Created:  Tue Sep 27 12:25:02 2022
Author:   wroser
=============================================================================
Description:
    
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import json
from collections import defaultdict
import numpy as np
import pandas as pd

from Model_10_Story import __path__
import Model_10_Story.src.postprocessing as post
from Model_10_Story.src.excel_to_database import Database
from generic import mround, Offset_Plot, Overlap_Plot

# For ease, set default path.
_default_out_dir = __path__[0] + '/out'

# Global Variables and Styles
tree = lambda: defaultdict(tree) # Allows recursive dictionary of arbitrary depth.

linestyles = {0:{'color':'blue'},
              1:{'color':'darkorange'},
              2:{'color':'forestgreen'},
              3:{'color':'red'},
              'overlap':{'linestyle':'--'}}

markerstyles = {0:{'color':'darkblue', 'linestyle':'None', 'marker':4, 'zorder':1.9},
                1:{'color':'darkgoldenrod', 'linestyle':'None', 'marker':4, 'zorder':1.9},
                2:{'color':'darkgreen', 'linestyle':'None', 'marker':4, 'zorder':1.9},
                3:{'color':'firebrick', 'linestyle':'None', 'marker':4, 'zorder':1.9},
                'L':{'color':'darkblue', 'linestyle':'None', 'marker':5, 'zorder':1.9},
                'R':{'color':'darkgoldenrod', 'linestyle':'None', 'marker':4, 'zorder':1.8},
                'X':{'color':'black', 'linestyle':'None', 'marker':'x'}}

labelstyles = {'L':{'ha':'right', 'va':'center_baseline', 'fontsize':'small', 'textcoords':'offset points', 'xytext':(-8, 0)},
               'R':{'ha':'left', 'va':'center_baseline', 'fontsize':'small', 'textcoords':'offset points', 'xytext':(8, 0)},
               'rightarrow':{'ha':'right', 'va':'center', 'fontsize':'small', 'zorder':1.9, 'arrowprops':dict(facecolor='silver', edgecolor='silver', width=0.1, headwidth=4, headlength=4, shrink=0.02)},
               'high':{'ha':'center', 'va':'top', 'fontsize':'small', 'textcoords':'offset points', 'xytext':(0, -4)},
               'low':{'ha':'center', 'va':'bottom', 'fontsize':'small', 'textcoords':'offset points', 'xytext':(0, 4)}}

level_elevations = [14, 170, 302, 434, 566, 698, 830, 962, 1094, 1226, 1358]
level_names = ['Base', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Roof']

def base_moment(analysisID, case):#, pairs_of_columns):
    # Load Recorders
    path = _default_out_dir + '/' + analysisID + '/' + case
    moment = post.Recorder(path + '/wall_base_forces.xml')
    disp = post.Recorder(path + '/base_rotation.xml')
    
    legend = ['CLT N', 'CLT S', 'MPP W', 'MPP E']
    maxima = tree()
    
    for Mdof, dispdof, sign, title in zip(['Mx_1', 'My_1'], ['D4', 'D5'], [[-1, 1], [1, -1]], ['North-South', 'East-West']):
        momentX = moment.df_dof(Mdof)
        dispRX = disp.df_dof(dispdof)
        # print(momentX)
        # print(dispRX)
        sorted_disp_nodes = [x[0] for x in moment.nodes.values()]
        # print(sorted_disp_nodes)
        unsorted_disp_nodes = [x.split(' ')[0] for x in list(dispRX.columns)]
        # print(unsorted_disp_nodes)
        fig, ax = plt.subplots(1, 1, figsize=(6, 4), sharex=True, constrained_layout=True)
        for i, node in enumerate(sorted_disp_nodes):
            j = unsorted_disp_nodes.index(node)
            line, = ax.plot(dispRX.iloc[:, j]*sign[0], momentX.iloc[:, i]*sign[1], **{**linestyles[i], **{'linewidth':0.5}})
            
            
        ax.legend(legend)
        ax.set_xlabel('Rotation (rad)')
        ax.set_ylabel('Moment (kip-in)')
        ax.set_title(title)
        ax.minorticks_on()
        ax.grid(True, which='minor', color='#EEEEEE')
        
        # Record maxima
        for i, line in enumerate(ax.get_lines()):
            
            x = max(line.get_xdata(), key=abs)
            y = max(line.get_ydata(), key=abs)
            
            maxima['Rotation'][title][legend[i]] = x
            maxima['Moment'][title][legend[i]] = y
        
        fig.savefig(moment.dir + '\\base_moment_' + title + '.png')
    
    return {'Base MR':maxima}

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
    maxima = {}
    
    # Plot drift
    # Drift is only plotted in the primary direction of each wall because the
    # out-of-plane drifts of each wall tends to be the average of the in-plane
    # walls.
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 5))
    
    for i, (nodes, dof) in enumerate(zip(walls, dofs)):
        
        for j, (node, style) in enumerate(zip(nodes, styles)):
            
            drift_profile = disp_recorder.max_drifts(node, dof)
            maxima[legends[i][j]] = drift_profile
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
    # fig.suptitle(disp_recorder.loadcase)
    fig.supxlabel('Max. Drift (%)')
    fig.savefig(disp_recorder.dir + '\\wall_drift_profile.png')
    print(maxima)
    return {'Max Drift':maxima}

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
    
    drifts = disp_recorder.drift(split_node, dof)
    drifts = {key:value*100 for (key,value) in drifts.items()}
    drifts = pd.DataFrame(drifts)
    
    # Choose scale
    scale_options = {0.1: 5, 0.2: 5, 0.25: 5, 0.3: 3, 0.4: 4, 0.5:5, 0.6: 6,
                     0.75: 3, 0.8: 2, 1.0: 5, 1.2: 6, 1.25: 5, 1.5: 6, 1.75: 5,
                     2.0: 4, 2.25: 5, 2.5: 5, 2.75: 5, 3.0: 6, 3.2: 4, 3.5: 5,
                     3.6: 6, 3.75: 5, 4.0: 4, 4.5: 5, 5.0: 5}
    try:
        offset = max([i for i in scale_options if 2*max(drifts.max()) >= i])
    except:
        offset = min([i for i in scale_options if 2*max(drifts.max()) < i])
    
    fig = Offset_Plot(drifts, x=disp_recorder.df['time'], offset=offset, minordiv=scale_options[offset])
    fig.draw(xlim=(0, disp_recorder.df['time'].iloc[-1]))
    
    

    # Labels. Include axis scale.
    minor_scale = fig.offset / fig.minordiv
    print(fig.offset, fig.minordiv)
    scale_message = "(Vertical gridlines spaced at {:.2f}%.)".format(minor_scale)
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
    
    # Mark maxima
    for line in fig.ax.get_lines():
        x = line.get_xdata()
        y = line.get_ydata()
        y_true = y - round(y[0], 2)
        xy = (x[np.argmax(abs(y_true))], y[np.argmax(abs(y_true))])
        y_max = y_true[np.argmax(abs(y_true))]
        fig.ax.plot(*xy, **markerstyles['X'])
        # va = 'bottom' if y_max < 0 else 'top'
        # style = {**labelstyles['rightarrow'], 'va':va}
        fig.ax.annotate('{:.2f}%'.format(y_max), xy, xytext=(x[-1] - 1, xy[1]),  **labelstyles['rightarrow'])
    
    fig.fig.savefig(disp_recorder.dir + '\\' + name + '.png')
    
    # No return. Maxima recorded by another graph.

def drift_four_walls(analysisID, case, out_dir=_default_out_dir):
    nodes = [['F', 'ACLT'], ['F', 'CCLT'], ['F', 'MPP1'], ['F', 'MPP4']]
    dofs = 'XXYY'
    walls = ['North', 'South', 'West', 'East']
    for split_node, dof, wall_name in zip(nodes, dofs, walls):
        title = wall_name + ' Wall Drift History (' + dof + ')'
        wall_drift_history(analysisID, case, split_node, dof, title=title, name=wall_name)

def base_shear(analysisID, case, out_dir=_default_out_dir):
    path = _default_out_dir + '/' + analysisID + '/' + case
    base_reaction = post.Recorder(path + '/reactions.xml')
    df = base_reaction.df
    time = df['time']
    
    maxima = {'X':{}, 'Y':{}}
    
    # --- Base Shear for Each Wall ---
    fig_each, ax_each = plt.subplots(4, 1, figsize=(6.5, 8), sharex=True, constrained_layout=True)
    titles = ['CLT North', 'CLT South', 'MPP West', 'MPP East']
    nodes = ['F1ACLT', 'F1CCLT', 'F1MPP1', 'F1MPP4']
    for i, (title, node) in enumerate(zip(titles, nodes)):
        for j, (suffix, xory) in enumerate(zip([' R1', ' R2'], 'XY')):
            line, = ax_each[i].plot(time, df[node + suffix], label=xory, **linestyles[j])
            # Record maxima
            y = line.get_ydata()
            x, y = (time[np.argmax(abs(y))], y[np.argmax(abs(y))])
            maxima[xory][titles[i]] = y
            if j == int(i/2) % 2: # major direction only
                ax_each[i].plot(x, y, **markerstyles[j])
                ax_each[i].annotate('{:.1f}'.format(y), (x, y), **labelstyles['R'])
        ax_each[i].minorticks_on()
        ax_each[i].grid(True, which='major', axis='both')
        ax_each[i].grid(True, which='minor', axis='x')
        ax_each[i].set_xlim([0, time.iloc[-1]])
        ax_each[i].set_ylabel(title)
        # Legend on first plot only
        if i == 0:
            blue_line = mpl.lines.Line2D([], [], color='blue', label='X')
            orange_line = mpl.lines.Line2D([], [], color='orange', label='Y')
            ax_each[i].legend(handles=[blue_line, orange_line])
    ax_each[i].set_xlabel('Time (sec.)')
    fig_each.supylabel('Base Shear (kip.)')
    
    fig_each.savefig(base_reaction.dir + '\\base_shear_walls.png')
    
    # --- Net Base Shear ---
    fig_total, ax_total = plt.subplots(2, 1, figsize=(6.5, 5), sharex=True, constrained_layout=True)
    # Note: A quick test showed 98% of base shear is acounted for only including the walls. 92% is carried by the walls in the primary directions.
    dfx = df.filter(regex=' R1')
    dfy = df.filter(regex=' R2')
    
    for i, (direction, label) in enumerate(zip('XY', [' R1', ' R2'])):
        df_tot = df.filter(regex=label)
        df_tot = df_tot.sum(axis=1) # Sum of each row.
        line, = ax_total[i].plot(time, df_tot, linewidth=1.0)
        ax_total[i].minorticks_on()
        ax_total[i].grid(True, which='major', axis='both')
        ax_total[i].grid(True, which='minor', axis='x')
        ax_total[i].set_xlim([0, time.iloc[-1]])
        ax_total[i].set_ylabel(direction)
        # Record maxima
        y = line.get_ydata()
        x, y = (time[np.argmax(abs(y))], y[np.argmax(abs(y))])
        maxima[direction]['Total'] = y
        ax_total[i].plot(x, y, **markerstyles[0])
        ax_total[i].annotate('{:.1f}'.format(y), (x, y), **labelstyles['R'])
        
    ax_total[-1].set_xlabel('Time (sec.)')
    fig_total.supylabel('Total Base Shear (kip.)')
    fig_total.savefig(base_reaction.dir + '\\base_shear_total.png')
    
    return {'Base Shear':maxima}

def toe_uplift(analysisID, case, out_dir=_default_out_dir):
    path = _default_out_dir + '/' + analysisID + '/' + case
    baseFD = post.NodeDispRecorder(path + '\\base_spring_FD.xml')
    df = baseFD.df
    time = df['time']
    
    # Displacements end with e1
    # Node name numbering system is x by y.
    # TO DO: Retrieve min/max of rocking wall from Excel file for if N !=21.
    
    # North-South
    figNS, axNS = plt.subplots(2, 1, figsize=(6.5, 4), sharex=True, constrained_layout=True)
    axNS[0].plot(time, df['Base_MPP1_2_21 e1'], label='West', **linestyles[0])
    axNS[0].plot(time, df['Base_MPP4_2_21 e1'], label='East', **linestyles[1], **linestyles['overlap'])
    axNS[1].plot(time, df['Base_MPP1_2_1 e1'], label='West', **linestyles[0])
    axNS[1].plot(time, df['Base_MPP4_2_1 e1'], label='East', **linestyles[1], **linestyles['overlap'])
    axNS[0].legend(handles=axNS[0].get_lines())
    figNS.supylabel('Toe Uplift (in.)')
    axNS[0].set_ylabel('North')
    axNS[1].set_ylabel('South')
    axNS[1].set_xlabel('Time (sec.)')
    figNS.suptitle('MPP Walls Toe Uplift')
    axNS[0].set_xlim([0, time.iloc[-1]])
    axNS[1].set_xlim([0, time.iloc[-1]])
    
    
    # East-West
    figEW, axEW = plt.subplots(2, 1, figsize=(6.5, 4), sharex=True, constrained_layout=True)
    axEW[0].plot(time, df['Base_ACLT_1_2 e1'], label='North', **linestyles[0])
    axEW[0].plot(time, df['Base_CCLT_1_2 e1'], label='South', **linestyles[1], **linestyles['overlap'])
    axEW[1].plot(time, df['Base_ACLT_21_2 e1'], label='North', **linestyles[0])
    axEW[1].plot(time, df['Base_CCLT_21_2 e1'], label='South', **linestyles[1], **linestyles['overlap'])
    axEW[0].legend(handles=axNS[1].get_lines())
    figEW.supylabel('Toe Uplift (in.)')
    axEW[0].set_ylabel('West')
    axEW[1].set_ylabel('East')
    axEW[1].set_xlabel('Time (sec.)')
    figEW.suptitle('CLT Walls Toe Uplift')
    axEW[0].set_xlim([0, time.iloc[-1]])
    axEW[1].set_xlim([0, time.iloc[-1]])
    
    
    # Plot Maxima and save to dict
    maxima = tree()
    for fig in [figNS, figEW]:
        for ax in fig.axes:
            for i, line in enumerate(ax.get_lines()):
                y = line.get_ydata()
                xy = (time[np.argmax(abs(y))], y[np.argmax(abs(y))])
                maxima[fig._suptitle.get_text().split(' ')[0]][ax.get_ylabel()][line.get_label()] = xy[1]
                ax.plot(*xy, **markerstyles['LR'[i]])
                ax.annotate('{:.2f}'.format(xy[1]), xy, **labelstyles['LR'[i]])
    
    # Save Figures
    figNS.savefig(baseFD.dir + '\\toe_uplift_MPP.png')
    figEW.savefig(baseFD.dir + '\\toe_uplift_CLT.png')
    
    return {'Toe Uplift':maxima}
    
def PT_three_charts(analysisID, case, out_dir=_default_out_dir):
    path = _default_out_dir + '/' + analysisID + '/' + case
    PT_axial = post.NodeDispRecorder(path + '\\PT_force.xml')
    PT_XYZ = post.NodeDispRecorder(path + '\\PT_globalforces.xml')
    # PT_stretch = post.NodeDispRecorder(path + '\\PT_defo.xml')
    
    time = PT_axial.df['time']
    # Observation: X and Y forces are much more stable than axial/Z forces.
    # X and Y forces tend to be almost the same for all 4 on a wall.
    
    # PT X and Y totals for each wall
    df = PT_XYZ.df
    fig, ax = plt.subplots(4, 1, figsize=(6.5, 8), sharex=True, constrained_layout=True)
    titles = ['CLT North', 'CLT South', 'MPP West', 'MPP East']
    walls = ['ACLT', 'CCLT', 'MPP1', 'MPP4']
    for i, wall in enumerate(walls):
        df_wall = df.filter(regex=wall)
        lines = [None, None]
        for j, (xory, xory2) in enumerate(zip('XY', [' P2_1', ' P2_2'])):
            df_sum = df_wall.filter(regex=xory2)
            df_sum = df_sum.sum(axis=1) # Sum of each row.
            lines[j], = ax[i].plot(time, df_sum, label=xory)
            
            # Plot Maxima and save to dict
            y = df_sum
            xy = (time[np.argmax(abs(y))], y[np.argmax(abs(y))])
            ax[i].plot(*xy, **markerstyles['LR'[j]])
            ax[i].annotate('{:.2f}'.format(xy[1]), xy, **labelstyles['LR'[j]])
            
        ax[i].set_ylabel(titles[i])
        ax[i].minorticks_on()
        ax[i].grid(True, which='minor', axis='x')
    ax[0].legend(frameon=True, framealpha=1.0)
    ax[-1].set_xlabel('Time (sec.)')
    ax[-1].set_xlim([0, time.iloc[-1]])
    fig.supylabel('Net PT Force at Top of Each Wall (kip.)')
    fig.savefig(PT_XYZ.dir + '\\PT_each_wall.png')
    
    # PT X and Y total for building
    fig, ax = plt.subplots(1, 1, figsize=(6.5, 4), constrained_layout=True)
    for i, (xory, xory2) in enumerate(zip('XY', [' P2_1', ' P2_2'])):
        df_sum = df.filter(regex=xory2)
        df_sum = df_sum.sum(axis=1)
        line, = ax.plot(time, df_sum, label=xory)
        
        # Plot Maxima and save to dict
        y = df_sum
        xy = (time[np.argmax(abs(y))], y[np.argmax(abs(y))])
        ax.plot(*xy, **markerstyles['LR'[i]])
        ax.annotate('{:.2f}'.format(xy[1]), xy, **labelstyles['LR'[i]])
                    
    ax.set_xlim([0, time.iloc[-1]])
    ax.legend(frameon=True, framealpha=1.0)
    ax.set_xlabel('Time (sec.)')
    ax.set_xlim([0, time.iloc[-1]])
    ax.set_ylabel('Net PT Forces at Top of Building (kip.)')
    fig.savefig(PT_XYZ.dir + '\\PT_total.png')
    
    # PT axial force
    df = PT_axial.df
    maxima = tree()
    titles = ['CLT North', 'CLT South', 'MPP West', 'MPP East']
    walls = ['ACLT', 'CCLT', 'MPP1', 'MPP4']
    for i, wall in enumerate(walls):
        fig, ax = plt.subplots(1, 1, figsize=(6.5, 4), constrained_layout=True)
        for j, PTi in enumerate(['SW', 'NW', 'SE', 'NE']): # Corresponds to site's labels: 1, 2, 3, 4
            y = df[wall + '_PT_' + PTi + ' N']
            ax.plot(time, y, label=PTi, **{**linestyles[j], 'linewidth':0.5})
            
            # Plot Maxima and save to dict
            xy = (time[np.argmax(abs(y))], y[np.argmax(abs(y))])
            marker = 5 if j % 2 == 0 else 4
            ax.plot(*xy, **{**markerstyles[j], 'marker':marker})
            ax.annotate('{:.2f}'.format(xy[1]), xy, **labelstyles['LR'[j%2]])
            maxima[wall][PTi] = xy[1]
            
            
        ax.legend(frameon=True, framealpha=1.0)
        
        
        ax.set_title(titles[i])
        ax.minorticks_on()
        ax.grid(True, which='minor', axis='x')
        ax.set_xlabel('Time (sec.)')
        ax.set_xlim([0, time.iloc[-1]])
        ax.set_ylabel('Axial Force (kip.)')
        fig.savefig(PT_axial.dir + '\\PT_axial_' + titles[i] + '.png')
    
    return {'PT Axial':maxima}

def wall_force_profile(analysisID, case, wall, response, file, out_dir=_default_out_dir):
    path = _default_out_dir + '/' + analysisID + '/' + case
    wall_forces = post.Recorder(path + '\\' + file)
    df = wall_forces.df
    time = df['time']
    
    # Get names of elements
    ele_names = list(wall_forces.nodes.keys())
    
    data = []
    for ele in ele_names:
        if wall in ele:
            # Get max response
            F1 = wall_forces.get_response(ele, response + '_1').abs().max()[0]
            F2 = wall_forces.get_response(ele, response + '_2').abs().max()[0]
            # Get node information
            inode, jnode = wall_forces.nodes[ele]
            _, _, z1 = wall_forces.coord.loc[inode]
            _, _, z2 = wall_forces.coord.loc[jnode]
            
            data.append([z1, z2, F1, F2])
        else:
            continue
    
    data = pd.DataFrame(data)
    data = data.sort_values(0, ignore_index=True)
    data = list(np.array(data))
    z = []
    F = []
    for row in data:
        z.extend(row[0:2])
        F.extend(row[2:])
    return z, F

def wall_moment_profile(analysisID, case, out_dir=_default_out_dir):
    responses = ['My', 'My', 'Mx', 'Mx']
    fig, ax, maxima = _plot_wall_profile(analysisID, case, responses, out_dir=out_dir)
    
    fig.supxlabel('Max. Moment (kip-in.)')
    ax[0].ticklabel_format(axis='x', style='sci', scilimits=(3,3))
    ax[1].ticklabel_format(axis='x', style='sci', scilimits=(3,3))
    
    fig.savefig(_default_out_dir + '/' + analysisID + '/' + case + '\\profile_moment.png')
    
    return {'Wall Moment':maxima}

def wall_shear_profile(analysisID, case, out_dir=_default_out_dir):
    responses = ['Px', 'Px', 'Py', 'Py']
    fig, ax, maxima = _plot_wall_profile(analysisID, case, responses, out_dir=out_dir)
    
    fig.supxlabel('Max. Shear (kip)')
    
    fig.savefig(_default_out_dir + '/' + analysisID + '/' + case + '\\profile_shear.png')
    
    return {'Wall Shear':maxima}

def _plot_wall_profile(analysisID, case, responses, out_dir=_default_out_dir):
    wallinfo = pd.DataFrame([
        ['WallN', 'WallS', 'WallW', 'WallE'],
        responses,
        ['wallN_forces.xml', 'wallS_forces.xml', 'wallW_forces.xml', 'wallE_forces.xml'],
        ['CLT North', 'CLT South', 'MPP West', 'MPP East']
        ],
        index=['UID', 'response', 'file', 'label'])
    
    maxima = {}
    
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 4), constrained_layout=True, sharey=True)
    
    for i in wallinfo:
        z, F = wall_force_profile(analysisID, case, wallinfo[i]['UID'], wallinfo[i]['response'], wallinfo[i]['file'], out_dir=out_dir)
        
        ax[i//2].plot(F, z, label=wallinfo[i]['label'], **linestyles[i])
        # print(ax[i//2].get_xlim())
        # ax[i//2].set_xlim([0, ax[i//2].get_xlim()[1]])
        # ax[i//2].set_xlim(left=0, right=None)
        
        imax = np.argmax(F)
        maxima[wallinfo[i]['label']] = {}
        maxima[wallinfo[i]['label']]['Base'] = F[0]
        maxima[wallinfo[i]['label']]['Max'] = {'Value': F[imax],
                                               'Elevation': z[imax]}
    
    # lines_labels = [axis.get_legend_handles_labels() for axis in ax]
    # lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    fig.legend()#lines, labels)
    
    
    ax[0].set_yticks(level_elevations, labels=level_names)
    ax[0].set_ylim([z[0], z[-1]])
    ax[0].set_xlim(left=0, right=None)
    ax[1].set_xlim(left=0, right=None)
    
    fig.supylabel('Level')
    return fig, ax, maxima

def base_strains(analysisID, case, out_dir=_default_out_dir):
    walls = ['ACLT', 'CCLT', 'MPP1', 'MPP4']
    direction = ['X', 'X', 'Y', 'Y']
    regex = ['ACLT\w*_2 e1', 'CCLT\w*_2 e1', 'MPP1_2\w* e1', 'MPP4_2\w* e1']
    labels = ['CLT North', 'CLT South', 'MPP West', 'MPP East']
    eleProperty = ['ms CLT', 'ms CLT', 'ms MPP', 'ms MPP']
    
    path = _default_out_dir + '/' + analysisID + '/' + case
    baseFD = post.Recorder(path + '\\base_spring_FD.xml')
    db = Database(baseFD.sourcefile)
    
    fig, ax = plt.subplots(1, 1, figsize=(6.5, 3), constrained_layout=True)
    dfmin = baseFD.df.min()
    
    savevar = {}
    
    for i, wall in enumerate(walls):
        savevar[labels[i]] = {}
        comp_strains = dfmin.filter(regex=regex[i]) / db.eleData.loc[eleProperty[i]]['Leff']
        savevar[labels[i]]['Max. Strain'] = min(comp_strains)
        x = []
        
        for ele in comp_strains.index:
            x.append(baseFD.coord.loc[baseFD.nodes[ele[:-3]][0]][direction[i]])
        x = np.array(x)
        x = x - np.average(x)
        
        ax.plot(x, comp_strains, ('-' + '-'*(i%2)), label=labels[i], **linestyles[i])
    ax.legend(loc='lower center')
    ax.set_xlim([-60, 60])
    ax.set_ylim([ax.get_ylim()[0], 0])
    ax.set_xlabel('Distance to Centerline (in.)')
    ax.set_ylabel('Strain (in./in.)')
    
    # Strains of Interest
    yield_strain = db.eleData.loc['ms CLT']['fy'] / db.eleData.loc['ms CLT']['E']
    savevar['CLT Yield'] = yield_strain
    ax.axhline(y=yield_strain, linestyle='--', **linestyles[0])
    ax.annotate('CLT Yield: {:.2e}'.format(yield_strain), (0, yield_strain), **labelstyles['high'])
    yield_strain = db.eleData.loc['ms MPP']['fy'] / db.eleData.loc['ms MPP']['E']
    savevar['MPP Yield'] = yield_strain
    ax.axhline(y=yield_strain, linestyle='--', **linestyles[3])
    ax.annotate('MPP Yield: {:.2e}'.format(yield_strain), (0, yield_strain), **labelstyles['low'])
    
    fig.savefig(baseFD.dir + '\\base_strain.png')
    
    return {'Strain': savevar}

def same_each_floor_XY(analysisID, case, in_file, out_filename, response, ylabel, floors=(2, 11), out_dir=_default_out_dir):
    '''
    

    Parameters
    ----------
    analysisID : TYPE
        DESCRIPTION.
    case : TYPE
        DESCRIPTION.
    in_file : TYPE
        DESCRIPTION.
    out_filename : TYPE
        DESCRIPTION.
    response : TYPE
        DESCRIPTION.
    ylabel : TYPE
        DESCRIPTION.
    floors : TYPE, optional
        DESCRIPTION. The default is (2, 11).
    out_dir : TYPE, optional
        DESCRIPTION. The default is _default_out_dir.

    Returns
    -------
    None.

    '''
    
    path = out_dir + '/' + analysisID + '/' + case
    recorder = post.NodeDispRecorder(path + '\\' + in_file + '.xml')
    df = recorder.df
    time = df['time']
    
    for floor in range(floors[0], floors[1]+1):
        fig, ax = plt.subplots(1, 1, figsize=(6.5, 4), constrained_layout=True)
        
        
        if isinstance(response[0], str) and len(response) == 2: # Plot single function
            ax.plot(time, df[response[0] + str(floor) + response[1]])
            
        elif isinstance(response[0], list) and len(response) == 2: # Plot x and y together
            for item, xory in zip(response, 'XY'):
                ax.plot(time, df[item[0] + str(floor) + item[1]], label=xory)
            ax.legend(frameon=True, framealpha=1.0)
                
        else:
            print(response)
            raise TypeError('"response" must be list of two strings or list of two lists of two strings.')
        
        if floor == 11:
            ax.set_ylabel('Roof ' + ylabel)
        else:
            ax.set_ylabel('Floor ' + str(floor) + ' ' + ylabel)
            
        ax.set_xlim([0, time.iloc[-1]])
        ax.set_xlabel('Time (sec.)')
        
        fig.savefig(recorder.dir + '\\' + out_filename + str(floor) + '.png')
        plt.close() # Will run faster if using backend that does not display plots.
    
def two_page_split(analysisID, case, in_file, out_filename, responses, ylabel, out_dir=_default_out_dir, sharey=True, n_digits=2, scale=1.0):
    
    path = out_dir + '/' + analysisID + '/' + case
    recorder = post.NodeDispRecorder(path + '\\' + in_file + '.xml')
    df = recorder.df
    time = df['time']
    maxima = tree()
    
    # One figure per page
    for floorrange, updown in zip([[7, 11], [2, 6]], ['upper', 'lower']):
        fig, ax = plt.subplots(5, 2, figsize=(6.5, 8), constrained_layout=True, sharex=True, sharey=sharey)
        
        for row, floor in enumerate(range(floorrange[1], floorrange[0]-1, -1)):
            
            for col, (item, xory) in enumerate(zip(responses, 'XY')):
                y = df[item[0] + str(floor) + item[1]] / scale
                ax[row][col].plot(time, y, **{**linestyles[col*3], 'linewidth':0.5})
                x, y = (time[np.argmax(abs(y))], y[np.argmax(abs(y))])
                maxima[out_filename][xory][floor] = y
                ax[row][col].plot(x, y, **markerstyles[col*3])
                ax[row][col].annotate(('{:.' + str(n_digits) + 'f}').format(y), (x, y), **labelstyles['R'])
                
                if row == 0:
                    ax[0][col].set_title(xory)
            if floor == 11:
                ax[row][0].set_ylabel('Roof')
            else:
                ax[row][0].set_ylabel('Floor ' + str(floor))
                
        ax[-1][0].set_xlim([0, time.iloc[-1]])
        fig.supxlabel('Time (sec.)')
        fig.supylabel(ylabel)
            
        fig.savefig(recorder.dir + '\\' + out_filename + updown + '.png')
    
    return maxima

def two_page_same(analysisID, case, in_file, out_filename, response, ylabel, out_dir=_default_out_dir, sharey=False, n_digits=2, scale=1.0):
    
    path = out_dir + '/' + analysisID + '/' + case
    recorder = post.NodeDispRecorder(path + '\\' + in_file + '.xml')
    df = recorder.df
    time = df['time']
    maxima = tree()
    
    # One figure per page
    for floorrange, updown in zip([[7, 11], [2, 6]], ['upper', 'lower']):
        fig, ax = plt.subplots(5, 1, figsize=(6.5, 8), constrained_layout=True, sharex=True, sharey=sharey)
        
        for row, floor in enumerate(range(floorrange[1], floorrange[0]-1, -1)):
            
            if isinstance(response[0], str) and len(response) == 2: # Plot single response
                y = df[response[0] + str(floor) + response[1]] / scale
                ax.plot(time, y, **linestyles[0])
                
            elif isinstance(response[0], list) and len(response) == 2: # Plot x and y together
                lines = []
                for i, (item, xory) in enumerate(zip(response, 'XY')):
                    y = df[item[0] + str(floor) + item[1]] / scale
                    line, = ax[row].plot(time, y, **{**linestyles[i*3], 'linewidth':0.5}, label=xory)
                    lines.append(line)
                    x, y = (time[np.argmax(abs(y))], y[np.argmax(abs(y))])
                    maxima[out_filename][xory][floor] = y
                    ax[row].plot(x, y, **markerstyles[i*3])
                    ax[row].annotate(('{:.' + str(n_digits) + 'f}').format(y), (x, y), **labelstyles['R'])
                
                    if row == 0:
                        ax[0].set_title(xory)
                        ax[0].legend(handles=lines)
            if floor == 11:
                ax[row].set_ylabel('Roof')
            else:
                ax[row].set_ylabel('Floor ' + str(floor))
                
        ax[-1].set_xlim([0, time.iloc[-1]])
        fig.supxlabel('Time (sec.)')
        fig.supylabel(ylabel)
            
        fig.savefig(recorder.dir + '\\' + out_filename + updown + '.png')
    
    return maxima

def two_page_sharey(analysisID, case, in_file, out_filename, responses, ylabel, out_dir=_default_out_dir, sharey=True, n_digits=2, scale=1.0):
    
    path = out_dir + '/' + analysisID + '/' + case
    recorder = post.NodeDispRecorder(path + '\\' + in_file + '.xml')
    df = recorder.df
    time = df['time']
    maxima = tree()
    
    # One figure per page
    fig = [plt.figure(), plt.figure()]
    ax = []
    
    for page, (floorrange, updown) in enumerate(zip([[7, 11], [2, 6]], ['upper', 'lower'])):
        
        fig, ax = plt.subplots(5, 2, figsize=(6.5, 8), constrained_layout=True, sharex=True)
        
        for row, floor in enumerate(range(floorrange[1], floorrange[0]-1, -1)):
            
            for col, (item, xory) in enumerate(zip(responses, 'XY')):
                y = df[item[0] + str(floor) + item[1]] / scale
                ax[row][col].plot(time, y, **{**linestyles[col*3], 'linewidth':0.5})
                x, y = (time[np.argmax(abs(y))], y[np.argmax(abs(y))])
                maxima[out_filename][xory][floor] = y
                ax[row][col].plot(x, y, **markerstyles[col*3])
                ax[row][col].annotate(('{:.' + str(n_digits) + 'f}').format(y), (x, y), **labelstyles['R'])
                
                if row == 0:
                    ax[0][col].set_title(xory)
                
                if row == 0 and col == 0 and page == 0:
                    ax1 = ax[0][0]
                else:
                    ax[row][col].sharey(ax1)
            if floor == 11:
                ax[row][0].set_ylabel('Roof')
            else:
                ax[row][0].set_ylabel('Floor ' + str(floor))
                
        ax[-1][0].set_xlim([0, time.iloc[-1]])
        fig.supxlabel('Time (sec.)')
        fig.supylabel(ylabel)
            
        fig.savefig(recorder.dir + '\\' + out_filename + updown + '.png')
    
    return maxima

def two_page_split_differential(analysisID, case, in_file, out_filename, responses, ylabel, out_dir=_default_out_dir, sharey=True,
                                baseresponse=None, basefile=''):
    
    path = out_dir + '/' + analysisID + '/' + case
    recorder = post.NodeDispRecorder(path + '\\' + in_file + '.xml')
    df = recorder.df
    if baseresponse is not None:
        baserecorder = post.NodeDispRecorder(path + '\\' + basefile + '.xml')
    time = df['time']
    maxima = tree()
    
    # One figure per page
    for floorrange, updown in zip([[7, 11], [2, 6]], ['upper', 'lower']):
        fig, ax = plt.subplots(5, 2, figsize=(6.5, 8), constrained_layout=True, sharex=True, sharey=sharey)
        
        for row, floor in enumerate(range(floorrange[1], floorrange[0]-1, -1)):
            
            for col, (item, xory) in enumerate(zip(responses, 'XY')):
                y = df[item[0] + str(floor) + item[1]]
                ax[row][col].plot(time, y, **{**linestyles[col*3], 'linewidth':0.5})
                x, y = (time[np.argmax(abs(y))], y[np.argmax(abs(y))])
                maxima[out_filename][xory][floor] = y
                ax[row][col].plot(x, y, **markerstyles[col*3])
                ax[row][col].annotate('{:.0f}'.format(y), (x, y), **labelstyles['R'])
                
                if row == 0:
                    ax[0][col].set_title(xory)
            if floor == 11:
                ax[row][0].set_ylabel('Roof')
            else:
                ax[row][0].set_ylabel('Floor ' + str(floor))
                
        ax[-1][0].set_xlim([0, time.iloc[-1]])
        fig.supxlabel('Time (sec.)')
        fig.supylabel(ylabel)
            
        fig.savefig(recorder.dir + '\\' + out_filename + updown + '.png')
    
    return maxima

def add_to_json(func, analysisID, case, *args, **kwargs):
    
    path = _default_out_dir + '/' + analysisID + '/' + case + '/outdata.json'
    
    try:
        with open(path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    
    value = func(analysisID, case, *args, **kwargs)
    
    data = {**data, **value} # merges dictionaries
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)
    
    return value

def gm_plots(analysisID, case):
    from Model_10_Story.gm.response_ops import response_spectrum
    
    rundata = _default_out_dir + '/' + analysisID + '/data.json'
    try:
        with open(rundata, 'r') as file:
            rundata = json.load(file)
            # print(rundata)
    except FileNotFoundError:
        raise FileNotFoundError('JSON file not yet created.')
    
    eq_info = rundata['Analysis'][case]
    
    fig_accel, ax_accel = plt.subplots(len(eq_info['GM Files']), 1, figsize=(6.5, 4), sharex=True, constrained_layout=True)
    data = {'PGA':{}}
    for i, (eq_path, xyz) in enumerate(zip(eq_info['GM Files'], eq_info['directions'])):
        eq_path = __path__[0] + '/' + eq_path
        
        with open(eq_path) as file:
            accels = file.readlines()
            for j, line in zip( range(len(accels)), accels):
                accels[j] = float(line)
        
        # PGA
        accels = np.array(accels)
        time = np.linspace(0, eq_info['Duration'], len(accels))
        t_PGA, PGA = (time[np.argmax(abs(accels))], accels[np.argmax(abs(accels))])
        data['PGA'][xyz] = PGA
        print('PGA {:.2e} g {:}'.format(PGA, xyz))
        
        # Acceleration History
        ax_accel[i].plot(time, accels, **linestyles[i])
        ax_accel[i].set_ylabel(xyz)
        if abs(PGA) > 0.0: # OpenSees crashes while calculating spectrum if ground motion is all zeros
            ax_accel[i].plot(t_PGA, PGA, **markerstyles[i])
            ax_accel[i].annotate('{:.2e} g'.format(PGA), (t_PGA, PGA), **labelstyles['R'])
            
            # Spectrum
            fig, ax = response_spectrum(eq_info['dt'], accels, figsize=(6.5, 4))
            ax[0].set_title(xyz)
            fig.savefig(_default_out_dir + '/' + analysisID + '/' + case + '/gm_spectrum_' + xyz + '.png')
    
    ax_accel[0].set_xlim(0, eq_info['Duration'])
    fig_accel.supylabel('Acceleration (g)')
    ax_accel[-1].set_xlabel('Time (sec.)')
    fig_accel.savefig(_default_out_dir + '/' + analysisID + '/' + case + '/gm_acceleration.png')
    
    return data

def all_graphs(analysisID, case):
    
    # Drift history, four walls v
    drift_four_walls(analysisID, case)
    plt.close('all')
    
    # # Drift Profile v j
    a = add_to_json(wall_max_drift, analysisID, case)
    plt.close('all')
    
    # # Base Moment v j
    a = add_to_json(base_moment, analysisID, case)
    plt.close('all')
    
    # # Base Shear v j
    a = add_to_json(base_shear, analysisID, case)
    plt.close('all')
    
    # Uplift of the rocking toe v j
    a = add_to_json(toe_uplift, analysisID, case)
    plt.close('all')
    
    # # PT Forces v j
    a = add_to_json(PT_three_charts, analysisID, case)
    plt.close('all')
    
    # Same each story, XY v
    # Displacement
    a = add_to_json(two_page_split, analysisID, case, 
                    'center_disp',
                    'disp_',
                    [['F', '_center D1'], ['F', '_center D2']],
                    'Displacement (in.)',
                    sharey='row')
    plt.close('all')
    
    # Acceleration
    a = add_to_json(two_page_sharey, analysisID, case,
                    'center_accel',
                    'accel_',
                        [['F', '_center A1'], ['F', '_center A2']],
                        'Acceleration (g)',
                        sharey=True,
                        scale=386.4)
    plt.close('all')
    
    
    # Differential rotation
    
    
    # EQ
    a = add_to_json(gm_plots, analysisID, case)
    plt.close('all')
    
    # Max Wall Shear and Moment
    a = add_to_json(wall_moment_profile, analysisID, case)
    a = add_to_json(wall_shear_profile, analysisID, case)
    plt.close('all')
    
    # Base Strains
    a = add_to_json(base_strains, analysisID, case)
    plt.close('all')
    
    # print(dict(a))





if __name__ == '__main__':
    
    # %% Change Default plotting styles
    mpl.rcParams['lines.linewidth'] = 1.0 # Thin lines
    mpl.rcParams.update({"axes.grid" : True}) # always show grid
    
    # %% Output to Graphs
    # Input for all analysis types
    analysisID = 'MCE_Collection_2'#'Report_Test'#'16 Victoria'#'6 EQ xy'
    case = {2: '02_ChiChi_43',
            8: '08_Tohoku_225',
            15: '15_Tokachi_475',
            16: '16_Victoria_975',
            22: '22_Tohoku_MCE',
            23: '23_Niigata_MCE',
            24: '24_LomaPrieta_MCE',
            25: '25_Ferndale_MCE',
            26: '26_Tokachi_MCE',
            27: '27_Northridge_MCE',
            28: '28_SuperstitionHills_MCE'}[28]
    
    # # # Drift history - for individual walls
    # split_node = ['F', 'ACLT']
    # dof = 'X'
    # wall_drift_history(analysisID, case, split_node, dof)
    
    # -----------------------------------------------------
    
    # Drift history, four walls v
    # drift_four_walls(analysisID, case)
    
    
    # # Drift Profile v
    # wall_max_drift(analysisID, case)
    
    
    # Base Moment v
    # base_moment(analysisID, case)
    # a = add_to_json(base_moment, analysisID, case)
    
    # # Base Shear v j
    # base_shear(analysisID, case)
    # a = add_to_json(base_shear, analysisID, case)
    
    # # Uplift of the rocking toe v j
    # toe_uplift(analysisID, case)
    # a = add_to_json(toe_uplift, analysisID, case)
    
    # # PT Forces v
    # PT_three_charts(analysisID, case)
    
    
    # # Same each story, XY v
    # # Displacement
    # same_each_floor_XY(analysisID, case, 'center_disp', 'disp_',
    #                     [['F', '_center D1'], ['F', '_center D2']],
    #                     'Displacement (in.)')
    # # Rotation
    # same_each_floor_XY(analysisID, case, 'center_disp', 'rotation_',
    #                     ['F', '_center D6'], 'Rotation (rad.)')
    # # Acceleration
    # same_each_floor_XY(analysisID, case, 'center_accel', 'accel_',
    #                     [['F', '_center A1'], ['F', '_center A2']],
    #                     'Acceleration (in/sec²)')
    
    # gm_plots(analysisID, case)
    
    # Force Profile
    # data = wall_force_profile(analysisID, case, 'WallE', 'Mx')
    # wall_moment_profile(analysisID, case)
    # wall_shear_profile(analysisID, case)
    
    # Base of Wall Plot
    # base_strains(analysisID, case)
    
    # %% Main Script - All Graphs
    # -----------------------------------------------------
    all_graphs(analysisID, case)
    # from Model_10_Story.tools.write_EQ_summary import write_report
    # write_report(analysisID, case)

    
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
    
    