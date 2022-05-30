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
    
    for element in root.iter():

        if element.tag == 'TimeOutput':
            column_names.append(element[0].text)

        elif element.tag == 'NodeOutput':
            tag = element.attrib['nodeTag']
            nodeName = db.get_node_name(int(tag))
            hierarchy[nodeName] = []
            for response in range(len(element)):
                column_names.append(nodeName + ' ' + element[response].text)
                hierarchy[nodeName].append(element[response].text)
                
        elif element.tag == 'ElementOutput':
            tag = element.attrib['eleTag']
            eleName = db.tag_to_name('ele', int(tag))
            hierarchy[eleName] = []
            for response in range(len(element)):
                column_names.append(eleName + ' ' + element[response].text)
                hierarchy[eleName].append(element[response].text)
    
    
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
    
    return df, hierarchy

# df.plot(0,8)

if __name__ == '__main__':
    outdir = 'out/temp/lateralX/'
    file = 'UFP_force.xml'
    filepath = outdir + file
    df, h = xml_to_df(filepath, remove_blanks=True)