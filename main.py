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
model_filename = 'Model_no gravity framing.xlsm'
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
model.rayleigh_damping(0.02, (1, 9))

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
    args = str(loadCases.loc[case, 'Arguments']).split(', '); print(args)
    analysis_script(model, *args)
    ops.stop()
    
    
#-------------------------------------------------
# Loads
# ops.timeSeries('Constant', 1)
# ops.pattern('Plain', 1, 1)
# model.apply_nodal_loads('gravity')

# # Analysis
# ops.system("UmfPack")
# ops.numberer("AMD")
# ops.constraints("Transformation")
# ops.integrator("LoadControl", 1, 1)
# ops.test('EnergyIncr', 1e-20, 200, 1)
# ops.algorithm("KrylovNewton")
# ops.analysis("Static")
# ops.analyze(1)

# # Cleanup
# ops.setTime(0.0)


# # Ground motion
# dt = 0.01
# path = r'gm\28 TallWoodEqs_MCE_SuperstitionHills_x.txt'
# dof = 'X'
# N = 200

# dofs = {'X':1, 'Y':2, 'Z':3}
# dof = dofs[dof]

# ops.timeSeries('Path', 2, '-dt', dt, '-filePath', path, '-factor', 32.2*12)
# ops.pattern('UniformExcitation', 2, dof, '-accel', 2)


# # dt = 0.01
# path = r'gm\28 TallWoodEqs_MCE_SuperstitionHills_y.txt'
# dof = 'Y'
# # N = 2300

# dofs = {'X':1, 'Y':2, 'Z':3}
# dof = dofs[dof]

# ops.timeSeries('Path', 3, '-dt', dt, '-filePath', path, '-factor', 32.2*12)
# ops.pattern('UniformExcitation', 3, dof, '-accel', 3)


# # dt = 0.01
# path = r'gm\28 TallWoodEqs_MCE_SuperstitionHills_z.txt'
# dof = 'Z'
# # N = 5000

# dofs = {'X':1, 'Y':2, 'Z':3}
# dof = dofs[dof]

# ops.timeSeries('Path', 4, '-dt', dt, '-filePath', path, '-factor', 32.2*12)
# ops.pattern('UniformExcitation', 4, dof, '-accel', 4)



# # Recorders
# model.apply_recorders('EQ1')
# ops.record()

# # Analysis Options
# ops.wipeAnalysis()

# ops.system("UmfPack")
# ops.numberer("AMD")
# ops.constraints("Transformation")

# ops.test('NormDispIncr', 1e-10, 100, 2)
# ops.algorithm("KrylovNewton")
# ops.integrator('Newmark', 0.5, 0.25)
# ops.analysis("Transient")

# # Analysis Loop
# for i in range(int(N)):
#     if (i+1)%100 == 0:
#         print("Step: ", i+1)
#     ok = ops.analyze(1, dt)
    
#     if ok != 0:
    
#         # ops.test('NormDispIncr', 1e-5, 10, 1)
    
#         # ok = ops.analyze(1)
#         # print(ok)
#         # if ok !=0:
#         #     ops.algorithm("NewtonLineSearch")
#         #     ops.test('NormDispIncr', 1e-4, 10, 1)
#         #     ok = ops.analyze(1)
#         #     ops.test('NormDispIncr', 1e-5, 10, 1)
#         #     ops.algorithm("KrylovNewton")
#         #     print(ok)
#         #     if ok != 0:
#                 print(ops.testNorm())
#                 break

# # Cleanup
# ops.remove('timeSeries', 1)
# ops.remove('loadPattern', 1)
# ops.remove('timeSeries', 2)
# ops.remove('loadPattern', 2)
# ops.wipeAnalysis()
# ops.reset()

#-------------------------------------------------




print('\n==  Out of Loop  == ' + strftime('%H:%M:%S', gmtime(default_timer() - start)))

ops.wipe()

print('\n==  Starting Postprocessing  == ' + strftime('%H:%M:%S', gmtime(default_timer() - start)))
from src.postprocessing import output_preprocessing

output_preprocessing(model.out_dir)
print('\n==  End of Script  == ' + strftime('%H:%M:%S', gmtime(default_timer() - start)))
