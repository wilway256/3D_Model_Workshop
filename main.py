# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:00 2021

@author: wroser
"""

# from src.excel_to_database import dfEle
from timeit import default_timer
from time import strftime, gmtime
# from math import sqrt, pi
from src.model import Model
import openseespy.opensees as ops
from src.excel_to_database import Database
from src.bookkeeping import make_output_directory, save_input_file
import src.analysis as analysis
from src.recorder import apply_recorders
import os

ops.wipe()

# %% Create Output Directory
out_dir, out_folder = make_output_directory()

# %% Import Data
print('Starting Import')
start = default_timer()
model_filename = 'Model_Builder UFP and PT.xlsm'
db = Database(model_filename)
save_input_file(model_filename, out_folder)
# ops.logFile(out_dir + 'log.txt', '-noEcho') # Must restart kernel if this is active.

# %% Define Structure
print('Defining Structure ' + strftime('%H:%M:%S', gmtime(default_timer() - start)))
model = Model(db)

model.define_nodes()

model.fix_nodes()

model.assign_node_mass()

model.make_diaphragm_constraints()

model.define_transformations()

model.make_elements(rigidLinkConstraint=True)
print('Model Built', default_timer() - start)
# %% PrintModel
# ops.printModel('-file', model_filename.split('.')[0] + '.txt')

# %% Eigenvalue Analysis
model.rayleigh_damping(0.05, (1, 9))

print('Eigen', default_timer() - start)
# %% Loop through Each Load Case
print('{:<50s}{:>50s}'.format("Analysis Loop",
                              strftime('%H:%M:%S', gmtime(default_timer() - start))))
loadCases = db.loadCase.query('Run == "Y"')

for case in loadCases.index:
    print('\n== Starting New Load Case: ' + case + ' ==' + strftime('%H:%M:%S', gmtime(default_timer() - start)))
    
    # Make output subfolders
    try:
        os.mkdir(out_dir + '/' + case)
    except FileExistsError:
        pass
    
    ops.reset()
    ops.wipeAnalysis()
    
    # Gravity (or other constant load case)
    analysis.constant_analysis(db, 'gravity')
    
    # Recorders
    apply_recorders(db, case, out_dir + '/' + case + '/')
    ops.record()
    print('d')
    # Constant
    if loadCases['Type'][case] == 'Const':
        print('const if')
        analysis.constant_analysis(db, case)
        print('Constant', default_timer() - start)
        
    # Static
    if loadCases['Type'][case] == 'Static':
        print("static if")
        analysis.static_analysis(db, case)
        print('Static', default_timer() - start)
    
    # Pushover (displacement control)
    elif loadCases['Type'][case] == 'Disp':
        analysis.displacement_analysis(db, case)
        print("disp ctrl if")
        print('Disp', default_timer() - start)
    
    # Dynamic
    elif loadCases['Type'][case] == 'EQ':
        print("dynamic if")
        analysis.dynamic_analysis(db, case)
        print('Quake', default_timer() - start)
    
    analysis.reset_gravity(db)
    ops.remove('recorders')
    ops.reset()
    
print('\n==  Out of Loop  == ' + strftime('%H:%M:%S', gmtime(default_timer() - start)))

# M, C, K = analysis.MCK()
# ops.wipe()

