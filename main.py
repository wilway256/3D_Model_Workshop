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
print('Applying Loads')
# m.apply_loads()
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
# nodeList = [2]
# loadList = [8.0]
# for node, load in zip(nodeList, loadList):
#     ops.load(node, *[0.0, 0.0, load, 0.0, 0.0, 0.0])

# ops.load(db.get_node_tag('F11_center'), *[-100.0, 0.0, 0.0, 0.0, 0.0, 10000.0])
# ops.load(db.get_node_tag('F2 Corner4'), *[0.0, -1000.0, 0.0, 0.0, 0.0, 0.0])
# ops.load(db.get_node_tag('F3 Center'), *[1000.0, 0.0, 0.0, 0.0, 0.0, 0.0])

# %% Loads
# load.gravity
# load.



# %% Analysis
print('Analysis Options')
# m.set_analysis_options()
ops.system("BandSPD")
ops.numberer("RCM")
ops.constraints("Transformation")
ops.test('EnergyIncr', 1e-6, 100, 1)
ops.integrator("LoadControl", 0.1, 10)
ops.algorithm("KrylovNewton")
ops.analysis("Static")

# m.run_analysis()
# a = ops.analyze(1)

# %% Recorders
# #r.make_node_rocorders(db)
# #r.make_ele_recorders(db)
ops.recorder('Node', '-xml', out_dir + 'eigen.xml', '-node', 24, 22, '-dof', 1, 2, 6, 'eigen 0')
ops.eigen(2)
ops.record()

ops.remove('recorders')
# ops.wipe()
