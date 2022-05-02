# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:00 2021

@author: wroser
"""

# from src.excel_to_database import dfEle
import src.model as m
import openseespy.opensees as ops
from src.excel_to_database import initialize_database
from src.bookkeeping import make_output_directory, save_input_file
from src.analysis import constant_analysis
import os

ops.wipe()

# %% Create Output Directory
out_dir, out_folder = make_output_directory()

# %% Import Data
print('Starting Import')
model_filename = 'Model_Builder.xlsm'
db = initialize_database(model_filename)
save_input_file(model_filename, out_folder)
ops.logFile(out_dir + 'log.txt', '-noEcho') # Must restart kernel if this is active.

# %% Define Structure
print('Defining Structure')
m.make_model('3D')

m.define_nodes(db)

m.fix_nodes(db)

m.assign_node_mass(db)

m.make_diaphragm_constraints(db)

m.define_transformations(db)

m.make_elements(db)

# %% Manual Loads
# For debugging and quick testing

# ops.timeSeries('Linear', 999)
# ops.pattern('Plain', 999, 999)
# # nodeList = [2]
# # loadList = [8.0]
# # for node, load in zip(nodeList, loadList):
# #     ops.load(node, *[0.0, 0.0, load, 0.0, 0.0, 0.0])

# # ops.load(db.get_node_tag('F11_center'), *[-100.0, 0.0, 0.0, 0.0, 0.0, 10000.0])
# # ops.load(db.get_node_tag('F2 Corner4'), *[0.0, -1000.0, 0.0, 0.0, 0.0, 0.0])
# # ops.load(db.get_node_tag('F3 Center'), *[1000.0, 0.0, 0.0, 0.0, 0.0, 0.0])


# %% Load Cases
print("Analysis Loop")
loadCases = db.loadCase.query('Run == "Y"')

for case in loadCases.index:
    # Make output subfolders
    try:
        os.mkdir(out_dir + '/' + case)
    except FileExistsError:
        pass
    
    # Recorders
    
    
    # Gravity (or other constant load case)
    print('Applying Gravity')
    constant_analysis(db, 'gravity')
    
    # Static
    if loadCases['Type'][case] == 'Static':
        print("static if")
    
    # Pushover (displacement control)
    elif loadCases['Type'][case] == 'Disp':\
        print("disp ctrl if")
    
    # Dynamic
    elif loadCases['Type'][case] == 'GM':
        print("dynamic if")
        pass
    
    
print('Out of Loop')

# # ops.remove('recorders')
# # ops.wipe()

