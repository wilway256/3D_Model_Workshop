# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:00 2021

@author: wroser
"""

# %% User input
# To do: make these command line arguments
model_filename = 'Model_Builder.xlsm'
print_model = False
zeta_i = 0.02
zeta_j = None
iMode = 1
jMode = 9

# %% Imports
# Python Standard Libraries
from timeit import default_timer # accurate way to measure time elapsed in seconds
from time import localtime, strftime # for logging date and time when program is run
from datetime import timedelta # for logging amount of time program takes to run
import logging # saves runtime information to file
from os import getlogin # for logging username
from sys import stdout # for logging
# Other External Libraries
import openseespy.opensees as ops
# Imports from this project
from src.model import Model
from src.bookkeeping import make_output_directory, save_input_file
import src.analysis as analysis


# %% Initialization
# Make sure no OpenSees model is loaded.
ops.wipe()

# Create Output Directory
out_dir, out_folder = make_output_directory()

# Log Files
save_variables = {'Metadata':{}, 'Eigen':{}, 'Time':{}, 'Analysis':{}}
logfile = out_dir + 'log.txt'
logging.basicConfig(filename=logfile, format='%(message)s', level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(stdout)) # Prints to file and to console. Source: https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
start = default_timer()
def log(string):
    global start
    # print(default_timer(), start)
    logging.info(str(timedelta(seconds=default_timer() - start)) + ' - ' + string + '\n')

log('Program Start\n    ' + strftime('(%a) %Y-%b-%d %H:%M', localtime()) + '\n    by ' + getlogin())
save_variables['Metadata']['Username'] = getlogin()
save_variables['Metadata']['Date'] = strftime('%Y-%b-%d', localtime())
save_variables['Metadata']['Time'] = strftime('%H:%M', localtime())


# %% Import Data from Excel
log('Starting Import')

model = Model(model_filename)
save_input_file(model_filename, out_folder)
save_variables['Metadata']['Model Filename'] = model_filename
save_variables['Metadata']['Model Path'] = out_folder + model_filename
model.out_dir = out_dir
ops.logFile(out_dir + 'opensees_log.txt', '-noEcho') # Must restart kernel when activating/deactivating this option.


# %% Create OpenSees Model
log('Defining Structure')

model.define_nodes()
model.fix_nodes()
model.assign_node_mass()
model.make_diaphragm_constraints()
model.define_transformations()
model.make_elements(rigidLinkConstraint=False)

log('Model Built')
save_variables['Time']['Load Model'] = default_timer() - start


# %% PrintModel
# (for debugging)
if print_model:
    ops.printModel('-file', model_filename.split('.')[0] + '.txt')


# %% Eigenvalue Analysis
log('Starting Eigenvalue Analysis')
if zeta_j == None:
    zeta = zeta_i
else:
    zeta = (zeta_i, zeta_j)
save_variables['Eigen'] = model.rayleigh_damping(zeta, (iMode, jMode))
save_variables['Time']['Eigen Analysis'] = default_timer() - save_variables['Time']['Load Model']


# %% Loop through Each Load Case
log('Starting Analysis Loop')

# Loop through selected load cases in Excel file
loadCases = model.loadCase.query('Run == "Y"')

for case, function_name in zip(loadCases.index, loadCases.Command):
    log('Starting New Load Case: ' + case)
    ops.start() # Prints time to OpenSees log file
    
    # Run analysis commands
    model.active_case = case
    analysis_script = getattr(analysis, function_name)
    args = str(loadCases.loc[case, 'Arguments']).split(', '); print(args)
    save_variables['Analysis'][case] = analysis_script(model, *args)
    ops.stop()

log('Out of Loop\n')
save_variables['Time']['Runtime'] = default_timer() - start


# %% Postprocessing
# Rename integer tags with node and element names
log('Starting Postprocessing')
from src.postprocessing import output_preprocessing
output_preprocessing(model.out_dir)
save_variables['Time']['Postprocessing'] = default_timer() - save_variables['Time']['Runtime']

# Save Data
import json
with open(out_dir + "data.json", 'w') as file:
    json.dump(save_variables, file, indent=4)

log('End of Script')


# %% Cleanup
ops.wipe()
logging.shutdown() # required to safely exit the program
logger.handlers.clear() # needed to avoid bugs if running program twice from same console

