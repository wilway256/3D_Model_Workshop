# -*- coding: utf-8 -*-
"""
Active postprocessing script.
This file is for the user to run batches of postprocessing functions. No other
file should call this one. This will be used for generating quick output
after calling main.py.

Created on Mon Nov 15 11:24:08 2021
@author: wroser
"""

import numpy as np
import openseespy.opensees as ops
import matplotlib.pyplot as plt
import matplotlib
# import opsvis
# import src.postprocessing_active as pp1
# import src.postprocessing_saved as pp2

# %% Postprocessing
# nodes = ops.getNodeTags()
# pp1.print_node_disps_and_rxns(db, nodes, get_tag=False)

# eles = db.get_ele_list()
# for e in eles:
#     response = ops.eleResponse(db.get_ele_tag(e), 'force')
#     print(f'{e:>10}', response)

# # %% Visualization
# 
# opsvis.plot_model(node_labels=0, element_labels=0, offset_nd_label=False, axis_off=1,
#                   az_el=(- 80.0, 30.0), fig_wi_he=(20.0, 20.0), fig_lbrt=(0.04, 0.04, 0.96, 0.96),
#                   lw=0.1, local_axes=False, nodes_only=False, fmt_model='ko-')
# opsvis.plot_defo(interpFlag=0)
# opsvis.plot_defo( az_el=(-60.0, 30.0) )

# opsvis.plot_mode_shape(1, interpFlag=0)

# %% Visualization

def plot_nodes(factor=100.0):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    coords = np.zeros([len(ops.getNodeTags()), 3])
    for i, tag in enumerate(ops.getNodeTags()):
        coords[i,:] = coords[i,:] + np.asarray(ops.nodeCoord(tag))
        coords[i,:] = coords[i,:] + np.asarray(ops.nodeDisp(tag)[0:3]) * factor
    
    ax.scatter(coords[:,0], coords[:,1], coords[:,2], marker='+')
    return fig, ax

def plot_node_response(df, info):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    # x = []; y = []; z = []
    # for node in info.keys():
    #     x.append()
    ax.scatter(info['X'].to_numpy(), info['Y'].to_numpy(), info['Z'].to_numpy(), marker='+')
    # ax.scatter([1, 1], [3,2], [12,2], marker='+')

def disp_to_coords(df, info, factor = 50.0):
    for col in list(df):
        for node in info.index:
            if col.startswith(node):
                if col.endswith('D1'): # if X
                    index = 'X'
                elif col.endswith('D2'): # if Y
                    index = 'Y'
                elif col.endswith('D3'): # if Z
                    index = 'Z'
                for i in range(len(df)):
                    df.iloc[i][col] = df.iloc[i][col] * factor + info.loc[node][index]
    
    return df

# %% XML Parser
import os
import xml.etree.ElementTree as ET

import pandas as pd
from src.excel_to_database import initialize_database
from tkinter.filedialog import askopenfilename

def xml_to_df(filepath, remove_blanks=False):
    # outdir = 'out/triangle/'
    # file = 'node_t.xml'
    # filepath = outdir + file
    # model_filename = askopenfilename()
    # db = initialize_database(model_filename)
    
    # Get database from Excel
    a = filepath.split('/')
    i = filepath.find(a[-2]+'/'+a[-1])
    db_path = filepath[:i]
    
    for file in os.listdir(db_path):
        if file[:-1].endswith('.xls'):
            print(db_path + file)
            db = initialize_database(db_path + file)
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    column_names = []
    hierarchy = {}
    info = {}
    node_or_ele = ''
    
    for element in root.iter():

        if element.tag == 'TimeOutput':
            column_names.append(element[0].text)

        elif element.tag == 'NodeOutput':
            node_or_ele = 'node'
            tag = element.attrib['nodeTag']
            nodeName = db.get_node_name(int(tag))
            hierarchy[nodeName] = []
            for response in range(len(element)):
                column_names.append(nodeName + ' ' + element[response].text)
                hierarchy[nodeName].append(element[response].text)
            
            info[nodeName] = [element.attrib['coord1'], element.attrib['coord2'], element.attrib['coord3']]
                
        elif element.tag == 'ElementOutput':
            node_or_ele = 'ele'
            tag = element.attrib['eleTag']
            eleName = db.tag_to_name('ele', int(tag))
            hierarchy[eleName] = []
            for response in range(len(element)):
                column_names.append(eleName + ' ' + element[response].text)
                hierarchy[eleName].append(element[response].text)
    
    if node_or_ele == 'node':
        info = pd.DataFrame.from_dict(info, orient='index', columns=['X', 'Y', 'Z'], dtype=float)
    
    data = root.find('Data').text
    data = data.strip().split('\n')
    for i in range(len(data)):
        data[i] = data[i].split()
        for j in range(len(data[i])):
            data[i][j] = float(data[i][j])
    data = np.asarray(data)
    
    df = pd.DataFrame(data, columns=column_names)
    
    if remove_blanks:
        for column in list(df):
            if (df[column] == 0).all():
                df.drop(columns=column, inplace=True)
    
    return df, hierarchy, info

def xml_to_csv(folder, name):
    df, _, _ = xml_to_df(folder + '/' + name + '.xml')
    df.to_csv(folder + '/' + name + '.csv', index=None)

class Response:
    pass

def animate_df(df):
    frames = len(df) - 1
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    title = ax.set_title('Test')
    
    def update_graph(i):
        # graph._offsets3d = (df.iloc[i]['F11_center D1'], df.iloc[i]['F11_center D2'], df.iloc[i]['F11_center D3'])
        
        x = [df.iloc[i]['F11_center D1']]
        y = [df.iloc[i]['F11_center D2']]
        z = [df.iloc[i]['F11_center D3']]
        ax.set_xlim(0.0, 400.0)
        g = ax.scatter(x, y, z, marker='o')
        return g
        # graph.set_data(x, y)
        # graph.set_3d_properties(z)
        # title.set_text('time={}\nx={} y={} z={}\n{}{}{}'.format(i, x, y, z, type(x), type(y), type(z)))
        # return title, graph,
    
    
    # graph, = ax.scatter([df.iloc[0]['F11_center D1']], [df.iloc[0]['F11_center D2']], [df.iloc[0]['F11_center D3']], marker='o')
    ax.set_xlim(0.0, 400.0)
    # ax.set_xlabel('X')
    # ax.set_ylim3d([-5.0, 5.0])
    # ax.set_ylabel('Y')
    # ax.set_zlim3d([-5.0, 5.0])
    ani = matplotlib.animation.FuncAnimation(fig, update_graph, frames, interval=2000, blit=True)
    writergif = matplotlib.animation.PillowWriter(fps=1) 
    ani.save('xxx.gif', writer=writergif)

# def update_graph():
#     pass

if __name__ == '__main__':
    outdir = 'out/temp/dispX/'
    file = 'center_disp.xml'
    filepath = outdir + file
    df, h, info = xml_to_df(filepath, remove_blanks=False)
    
    df2 = disp_to_coords(df, info)
    # animate_df(df2)
    frames = len(df) - 1
    xs = df2['F11_center D1']
    ys = df2['F11_center D2']
    # zs = df2.loc['F11_center D3']
    
    def update(t):
        ax.cla()
    
        x = xs[t]
        y = ys[t]
        z = 0
    
        ax.scatter(x, y, z, s=9, marker = 'o')
    
        ax.set_xlim(0, 400)
        ax.set_ylim(0, -400)
        ax.set_zlim(-5, 5)
    
    
    fig = plt.figure(dpi=100)
    ax = fig.add_subplot(projection='3d')
    
    ani = matplotlib.animation.FuncAnimation(fig = fig, func = update, frames = frames, interval = 200)
    
    plt.show()