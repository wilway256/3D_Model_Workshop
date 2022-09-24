# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:00 2021

@author: wroser
"""

from timeit import default_timer
from time import strftime, gmtime
# from math import sqrt, pi
from src.model import Model
import openseespy.opensees as ops
# from src.excel_to_database import Database
from src.bookkeeping import make_output_directory, save_input_file
import src.analysis as analysis


ops.wipe()

# %% Create Output Directory
out_dir, out_folder = make_output_directory()

# %% Import Data
print('Starting Import')
start = default_timer()
model_filename = 'Model_Builder.xlsm'
model = Model(model_filename)
save_input_file(model_filename, out_folder)
model.out_dir = out_dir
ops.logFile(out_dir + 'log.txt', '-noEcho') # Must restart kernel if this is active.

# %% Define Structure
print('Defining Structure ' + strftime('%H:%M:%S', gmtime(default_timer() - start)))

model.define_nodes()

model.fix_nodes()

model.assign_node_mass()

model.make_diaphragm_constraints()

model.define_transformations()

model.make_elements(rigidLinkConstraint=False)

print('Model Built', default_timer() - start)

# %% PrintModel
# ops.printModel('-file', model_filename.split('.')[0] + '.txt')

# %% Eigenvalue Analysis
model.rayleigh_damping(0.05, (1, 9))

print('Eigen', default_timer() - start)
# %% Loop through Each Load Case
print('{:<50s}{:>50s}'.format("Analysis Loop",
                              strftime('%H:%M:%S', gmtime(default_timer() - start))))

loadCases = model.loadCase.query('Run == "Y"')

for case, function_name in zip(loadCases.index, loadCases.Command):
    print('\n== Starting New Load Case: ' + case + ' ==' + strftime('%H:%M:%S', gmtime(default_timer() - start)))
    ops.start() # Prints time to log file
    
    # Run analysis commands
    model.active_case = case
    analysis_script = getattr(analysis, function_name)
    args = str(loadCases.loc[case, 'Arguments']).split(', ')#; print(args)
    analysis_script(model, *args)
    ops.stop()
    
    
#-------------------------------------------------

#-------------------------------------------------




print('\n==  Out of Loop  == ' + strftime('%H:%M:%S', gmtime(default_timer() - start)))

ops.wipe()

# from src.postprocessing import *

