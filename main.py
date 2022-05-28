# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:00 2021

@author: wroser
"""

# from src.excel_to_database import dfEle
from math import sqrt, pi
import src.model as m
import openseespy.opensees as ops
from src.excel_to_database import initialize_database
from src.bookkeeping import make_output_directory, save_input_file
import src.analysis as analysis
from src.recorder import apply_recorders
import os

ops.wipe()

# %% Create Output Directory
out_dir, out_folder = make_output_directory()

# %% Import Data
print('Starting Import')
model_filename = 'Model_Builder.xlsm'
db = initialize_database(model_filename)
save_input_file(model_filename, out_folder)
# ops.logFile(out_dir + 'log.txt', '-noEcho') # Must restart kernel if this is active.

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

# %% Eigenvalue Analysis
m.modal_damping(0.05, (1, 9))
# eig = ops.eigen(5)
# Tn = [2*pi/sqrt(w2) for w2 in eig]
# print(Tn)

# # %% Damping
# damp_ratio = 0.05

# ops.rayleigh(0, 0, 0, 2*damp_ratio*Tn[0])



# %% Loop through Each Load Case
print("Analysis Loop")
loadCases = db.loadCase.query('Run == "Y"')

for case in loadCases.index:
    print('\n== Starting New Load Case: ' + case + ' ==')
    
    # Make output subfolders
    try:
        os.mkdir(out_dir + '/' + case)
    except FileExistsError:
        pass
    
    # Gravity (or other constant load case)
    analysis.constant_analysis(db, 'gravity')
    
    # Recorders
    apply_recorders(db, case, out_dir + '/' + case + '/')
    ops.record()
   
    # Constant
    if loadCases['Type'][case] == 'Const':
        analysis.constant_analysis(db, case)
        print('const if')
        
    # Static
    if loadCases['Type'][case] == 'Static':
        analysis.static_analysis(db, case)
        print("static if")
    
    # Pushover (displacement control)
    elif loadCases['Type'][case] == 'Disp':
        analysis.displacement_analysis(db, case)
        print("disp ctrl if")
    
    # Dynamic
    elif loadCases['Type'][case] == 'EQ':
        print("dynamic if")
        analysis.dynamic_analysis(db, case)
    
    analysis.reset_gravity(db)
    ops.remove('recorders')
    ops.reset()
    
print('\nOut of Loop')

# M, C, K = analysis.MCK()
# ops.wipe()

