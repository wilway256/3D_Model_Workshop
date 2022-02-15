# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:44:00 2021

@author: wroser
"""

# from src.excel_to_database import dfEle
import src.model as m
import openseespy.opensees as ops
from src.excel_to_database import initialize_database

# %% Import Data
print('Starting Import')
model_filename = 'Model_Data_UFP.xlsm'
db = initialize_database(model_filename)

# %% Define Structure
print('Defining Structure')
ops.wipe()
m.make_model('3D')

m.define_nodes(db)

m.fix_nodes(db)

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

ops.load(db.get_node_tag('LWall1'), *[-100.0, 0.0, 0.0, 0.0, 0.0, 0.0])
# ops.load(db.get_node_tag('F2 Corner4'), *[0.0, -1000.0, 0.0, 0.0, 0.0, 0.0])
# ops.load(db.get_node_tag('F3 Center'), *[1000.0, 0.0, 0.0, 0.0, 0.0, 0.0])

# %% Recorders
#r.make_node_rocorders(db)
#r.make_ele_recorders(db)


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
a = ops.analyze(1)

# %% Postprocessing
nodes = ops.getNodeTags()
ops.reactions()
for n in nodes:
    disps = ops.nodeDisp(n)
    print('{:>10}'.format(db.get_node_name(n)), '{:15.5f}{:15.5f}{:15.5e}{:15.0f}{:15.0f}{:15.0f}'.format(*disps))
    rxns = ops.nodeReaction(n)
    print('          ', '{:15.3f}{:15.3f}{:15.3f}{:15.2f}{:15.2f}{:15.2f}\n'.format(*rxns))

eles = db.get_ele_list()
for e in eles:
    response = ops.eleResponse(db.get_ele_tag(e), 'force')
    print(f'{e:>10}', response)

# %% Visualization
import opsvis
# opsvis.plot_model(node_labels=0, element_labels=0, offset_nd_label=False, axis_off=1,
#                   az_el=(- 80.0, 30.0), fig_wi_he=(20.0, 20.0), fig_lbrt=(0.04, 0.04, 0.96, 0.96),
#                   lw=0.1, local_axes=False, nodes_only=False, fmt_model='ko-')
# opsvis.plot_defo(interpFlag=0)
opsvis.plot_defo( az_el=(-60.0, 30.0) )
