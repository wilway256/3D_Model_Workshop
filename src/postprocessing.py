# -*- coding: utf-8 -*-
"""
Active postprocessing script.
This file is for the user to run batches of postprocessing functions. No other
file should call this one. This will be used for generating quick output
after calling main.py.

Created on Mon Nov 15 11:24:08 2021
@author: wroser
"""

import re
import numpy as np
import openseespy.opensees as ops
import matplotlib.pyplot as plt
import matplotlib
import Model_10_Story
from Model_10_Story.src.excel_to_database import Database
import pandas as pd
from pandas import DataFrame
import numpy as np
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

def global_forces():
    total = np.zeros((6))
    ops.reactions()
    for tag in ops.getNodeTags():
        nodeRxn = np.array(ops.nodeUnbalance(tag))
        total += nodeRxn
    return total

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

def plot_base_spring(model, name):
    if 'CLT' in name:
        xory = 0
    elif 'MPP' in name:
        xory = 1
    else:
        raise ValueError
    tags = model.get_tag('node', model.parse('node', 'GRP:base; HASNT:fixed; CONT:' + name))
    tags = tags + [model.get_tag('node', 'F1' + name)]
    x = np.zeros((len(tags)))
    z = np.zeros((len(tags)))
    for i, tag in enumerate(tags):
        x[i] = ops.nodeCoord(tag)[xory]
        z[i] = ops.nodeDisp(tag)[2]
    
    fig, ax = plt.subplots()
    ax.plot(x, z, '.')
        

# %% XML Parser
import os
import xml.etree.ElementTree as ET

import pandas as pd
# from excel_to_database import Database
# from tkinter.filedialog import askopenfilename

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
            db = Database(db_path + file)
    
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
            nodeName = tag#db.get_node_name(int(tag))
            hierarchy[nodeName] = []
            for response in range(len(element)):
                column_names.append(nodeName + ' ' + element[response].text)
                hierarchy[nodeName].append(element[response].text)
            
            info[nodeName] = [element.attrib['coord1'], element.attrib['coord2'], element.attrib['coord3']]
                
        elif element.tag == 'ElementOutput':
            node_or_ele = 'ele'
            tag = element.attrib['eleTag']
            eleName = tag#db.tag_to_name('ele', int(tag))
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

# %% Output Objects and Definitions
class Response:
    pass

def plot_disp(filepath, sfac=1.0):
    df, headers, info = xml_to_df(filepath)
    # print(df)
    nodedf = info.transpose()#, columns=headers.keys(), index=['x', 'y', 'z', 'dx', 'dy', 'dz'])
    
    plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(nodedf.loc['X'], nodedf.loc['Y'], nodedf.loc['Z'], marker='.', c='green')
    
    for node in nodedf.columns:
        filtered_columns = [col for col in df if col.startswith(node)]
        for dof, direction in zip([1, 2, 3], ['X', 'Y', 'Z']):
            col_index = [col for col in filtered_columns if col.endswith(str(dof))][0]
            nodedf.at[direction, node] += sfac * df.at[0, col_index]
    
    # plt.figure()
    # ax = plt.axes(projection='3d')
    ax.scatter(nodedf.loc['X'], nodedf.loc['Y'], nodedf.loc['Z'], marker='.')
    
    ax.set_xlabel('X (in.)')
    ax.set_ylabel('Y (in.)')
    ax.set_zlabel('Z (in.)')
    
    return df, nodedf

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

def choose_folder():
    cwd = os.getcwd()
    if 'out' in os.listdir(cwd):
        pass
    else:
        raise ValueError

# class Output(Database):
    
#     def __init__(self, filename):
#         super().__init__(filename)

  

def folder_select(path):
    i = 1
    print('Please select a folder...')
    for folder in next(os.walk(path))[1]:
        if '.' not in folder:
            print('{:>2d} - {:}'.format(i, folder))
            i += 1
    i = int(input())
    return path + '/' + folder

class Output:
    def __init__(self, output_folder=None, cases=None):
        # Select output folder if not specified
        
        if output_folder == None:
            output_folder = Model_10_Story.__path__[0] + '/out'
            # i = 1
            # print('Please select a folder...')
            # for folder in os.listdir(output_folder):
            #     if '.' not in folder:
            #         print('{:>2d} - {:}'.format(i, folder))
            # i = int(input())
            self.path = folder_select(output_folder)
        else:
            self.path = Model_10_Story.__path__[0] + '/out/' + output_folder
        
        # Loop through analyses
        print(self.path)
        self.cases = {}
        for folder in next(os.walk(self.path))[1]:
            self.cases[folder] = Case(self.path + '/' + folder)
            

class Case():
    def __init__(self, path):
        pass

class Recorder():
    '''
    
    '''
    
    def __init__(self, path, db=None, remove_blanks=False):
        self.path = path
        self.dir = '\\'.join(re.split(r'\\|/', self.path)[:-1])
        self.nodes = {}
        self.df, self.hierarchy, self.info = self.xml_to_df(path, db=db, remove_blanks=remove_blanks)
        self.tags = list(self.hierarchy.keys())
        self.loadcase = re.split(r'\\|/', self.path)[-2] # Assumes folder has analysis title
        
        # Can't subclass DataFrame
        self.columns = self.df.columns
        self.loc = self.df.loc
        
    def __getitem__(self, index):
        return self.df[index]
    
    def xml_to_df(self, filepath, db=None, remove_blanks=False):
        '''
        Returns:
            df: pandas dataframe of results
            hierarchy: links individual responses to their node/element
            coords: nodal coordinates
        '''
        
        # Get database for node and element names. Use tags if not available
        use_names = False
        
        # Parse XML using xml.etree.ElementTree
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        column_names = []
        hierarchy = {}
        coord = {}
        node_or_ele = ''
        
        for element in root.iter():
    
            if element.tag == 'TimeOutput':
                column_names.append(element[0].text)
    
            elif element.tag == 'NodeOutput':
                node_or_ele = 'node'
                tag = element.attrib['nodeTag']
                nodeName = db.get_node_name(int(tag)) if use_names else tag
                hierarchy[nodeName] = []
                for response in range(len(element)):
                    column_names.append(nodeName + ' ' + element[response].text)
                    hierarchy[nodeName].append(element[response].text)
                
                coord[nodeName] = [element.attrib['coord1'], element.attrib['coord2'], element.attrib['coord3']]
                
                    
            elif element.tag == 'ElementOutput':
                node_or_ele = 'ele'
                tag = element.attrib['eleTag']
                eleName = db.tag_to_name('ele', int(tag)) if use_names else tag
                hierarchy[eleName] = []
                for response in range(len(element)):
                    column_names.append(eleName + ' ' + element[response].text)
                    hierarchy[eleName].append(element[response].text)
                
                self.nodes[eleName] = [element.attrib['node1'], element.attrib['node2']]
        
        coord = pd.DataFrame.from_dict(coord, orient='index', columns=['X', 'Y', 'Z'], dtype=float)
        # Get data table
        # Explanation: OpenSees outputs all traditional recorder outputs within
        #              a single tag, "Data".
        data = root.find('Data').text
        # Split into lines. Split each line into data points. Convert to array of floats.
        data = data.strip().split('\n')
        for i in range(len(data)):
            data[i] = data[i].split() # 
            for j in range(len(data[i])):
                data[i][j] = float(data[i][j])
        data = np.asarray(data)
        
        # Convert array to pandas Dataframe. Column names are from parsing the xml.
        df = pd.DataFrame(data, columns=column_names)
        
        # Optional: Remove columns where all records are zero.
        if remove_blanks:
            for column in list(df):
                if (df[column] == 0).all():
                    df.drop(columns=column, inplace=True)
        
        return df, hierarchy, coord
    
    def get_dofs(self, uid):
        newcols = list(self.loc[:, self.columns.str.startswith(str(uid) + ' ')].columns)
        for i in range(len(newcols)):
            newcols[i] = newcols[i].replace(str(uid) + ' ', '')
        return newcols
    
    def plot_responses(self, uid):
        pass
    
    def plot_dof(self, dofs):
        if type(dofs) is str:
            dofs = [dofs]
        
        # fig, ax = plt.subplots()
        # ax.grid()
        
        for dof in dofs:
            newcols = self.columns.str.endswith(dof)
            newcols[0] = True # Adds time
            newdf = self.loc[:, newcols]
            ax = newdf.plot(x='time')
        return ax
    
    def df_dof(self, dofs):
        if type(dofs) is str:
            dofs = [dofs]
        
        for dof in dofs:
            newdf = self.loc[:, self.columns.str.endswith(dof)]
            
        return newdf
    
    def get_response(self, uid, dof):
        cols_uid = list(self.loc[:, self.columns.str.startswith(str(uid) + ' ')].columns)#; print(cols_uid)
        cols_dof = list(self.loc[:, self.columns.str.endswith(str(dof))].columns)#; print(cols_dof)
        cols = list(set(cols_uid) & set(cols_dof))#; print(cols)
        newdf = self.loc[:, cols]
        return newdf

class NodeDispRecorder(Recorder):
    
    def drift(self, node, dof):
        
        direction = {'X': ' D1', 'Y':' D2'}
        time = self.df['time']
        profile = {} # dictionary of floors and max drifts
        
        for floor in range(2, 12):
            # Upper floor displacement history and height
            nodeUIDi = node[0] + str(floor) + node[1]
            dispi = np.array(self.df[nodeUIDi + direction[dof]])
            zi = self.info.loc[nodeUIDi, 'Z']
            
            # Lower floor displacement history and height
            try:
                nodeUIDj = node[0] + str(floor-1) + node[1]
                dispj = np.array(self.df[nodeUIDj + direction[dof]])
                zj = self.info.loc[nodeUIDj, 'Z']
            except:
                dispj = np.zeros(dispi.shape)
                zj = 0
            
            # Calculate drift and save to dict
            drift = (dispi - dispj) / (zi - zj)
            profile[floor] = drift
        
        return profile
    
    def max_drifts(self, node, dof):
        
        drift_profile = self.drift(node, dof)
        for floor in drift_profile.keys():
            drift_profile[floor] = max(abs(drift_profile[floor]))
        
        return drift_profile
    
    def drift_plot(self, node, dof):
        
        drift_profile = self.max_drifts(node, dof)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(4, 8))
        # ax.grid(True)
        bar_index = np.arange(len(drift_profile))
        bar_values = [value*100 for value in drift_profile.values()]
        bar_floors = list(drift_profile.keys())
        ax.barh(bar_index, bar_values, tick_label=bar_floors)
        for i, drift in enumerate(bar_values):
            ax.text(min(bar_values)/2, i, '{:.2f}%'.format(drift), ha='center', va='center', color='white')
        
        ax.set_xlabel('Drift (%)')
        ax.set_ylabel('Floor')
        ax.set_title(self.loadcase)
        
        return fig

def tags_to_names(path):
    '''
    Converts integer tags to names in a text file.

    Parameters
    ----------
    path : str
        DESCRIPTION.

    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    -------
    db : TYPE
        DESCRIPTION.

    '''
    # Open database object
    path = path.replace('\\', '/')
    out_folder, analysisID = path.split('out/')
    out_folder += 'out/'
    analysisID = analysisID.split('/')[0]
    try:
        db = Database(out_folder + analysisID + '/Model_Builder.xlsm')
    except:
        print(out_folder + analysisID + '/Model_Builder.xlsm not found.')
        print(os.listdir(out_folder + analysisID))
        filename = input('Enter name of Excel file: ')
        db = Database(out_folder + analysisID + '/' + filename)
    
    # Convert xml to names
    with open(path, errors='ignore') as file:
        filedata = file.read()
    
    # Find and replace: nodeTag="__" eletag="__" node1="_" node2="_"
    
    for regex, case in zip(['nodeTag="\d+"', 'eleTag="\d+"', 'node1="\d+"', 'node2="\d+"'], ['node', 'ele', 'node', 'node']):
        # Find all instances that need to be replaced
        target_strs = re.findall(regex, filedata)
        # For each instance, get tag then replace with name from Excel file
        for target in target_strs:
            replace = int(re.findall('\d+', target)[0])
            try:
                if case == 'node':
                    name = db.get_node_name(replace)
                elif case == 'ele':
                    name = db.get_ele_name(replace)
                else:
                    raise ValueError
            except:
                print(replace, case)
            before, after = regex.split('\d+')
            replace = before + name + after
            filedata = re.sub(target, replace, filedata)
            target = re.findall(regex, filedata)
    
    # # Uncomment to not overwrite original file
    # path = re.sub('\.xml', '_alt.xml', path)
        
    # Overwrite original file
    with open(path, 'w') as file:
        file.write(filedata)
    return db

def output_preprocessing(outfolder):
    '''
    Walks through outfolder and changes integer tags to names in all xml recorders.
    '''
    for subdir, dirs, files in os.walk(outfolder): # dirs should be individual load cases
        for subfolder in dirs:
            for subdir, dirs, files in os.walk(outfolder + '/' + subfolder): # get files in folder
                for file in files:
                    if file.endswith('.xml'): # can corrupt other files
                        print('Reading:', subfolder, file)
                        tags_to_names(subdir + '/' + file)

if __name__ == '__main__':
    pass
    
    # %% Script - change tags to names in xml file
    # db = output_preprocessing('C:\\Users\\wroser\\Documents\\Code Workshop\\Model_10_Story/out/deleteme')
    
    # %% Script
    # # results = Output('temp')
    # node = Recorder('C:\\Users\\wroser\\Documents\\Code Workshop\\Model_10_Story/out/SuperstitionMCE XYZ/EQ1/wall_disp.xml')
    # eleX = Recorder('C:\\Users\\wroser\\Documents\\Code Workshop\\Model_10_Story/out/temp/lateralX/wall_base_forces.xml')
    # eleY = Recorder('C:\\Users\\wroser\\Documents\\Code Workshop\\Model_10_Story/out/temp/lateralY/wall_base_forces.xml')
    # rxn = Recorder('C:\\Users\\wroser\\Documents\\Code Workshop\\Model_10_Story/out/temp/lateralX/reactions.xml')
    
    # eleX.plot_dof('Mx_1')
    # eleY.plot_dof('My_1')
    
    # %% Script
    # outdir = '../out/temp/'
    # file = 'eigen/eigen04.xml'
    # filepath = outdir + file
    
    # df1, df2 = plot_disp(filepath, sfac=100)
    
    
    
    
    
    
    
    # %% Script
    # df, h, info = xml_to_df(filepath, remove_blanks=False)
    
    # df2 = disp_to_coords(df, info)
    # # animate_df(df2)
    # frames = len(df) - 1
    # xs = df2['F11_center D1']
    # ys = df2['F11_center D2']
    # # zs = df2.loc['F11_center D3']
    
    # def update(t):
    #     ax.cla()
    
    #     x = xs[t]
    #     y = ys[t]
    #     z = 0
    
    #     ax.scatter(x, y, z, s=9, marker = 'o')
    
    #     ax.set_xlim(0, 400)
    #     ax.set_ylim(0, -400)
    #     ax.set_zlim(-5, 5)
    
    
    # fig = plt.figure(dpi=100)
    # ax = fig.add_subplot(projection='3d')
    
    # ani = matplotlib.animation.FuncAnimation(fig = fig, func = update, frames = frames, interval = 200)
    
    # plt.show()