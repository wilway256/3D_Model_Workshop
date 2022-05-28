# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 16:25:13 2022

@author: wroser
"""

import numpy as np
import tkinter as tk
from tkinter import ttk
import os
import openseespy.opensees as ops
from src.loads import apply_nodal_loads
import gm.gm_reader as gm
import matplotlib.pyplot as plt

# Module-level variables
timeSeriesTag = 2
patternTag = 2

def analysis_loop(db, out_directory):
    df = db.loadCase.query('Run == "Y"')
    # print(df)
    for case in df.index:
        # Make output subfolders
        try:
            os.mkdir(out_directory + '/' + case)
        except FileExistsError:
            pass
        
        # Recorders
        
        
        # Gravity (or other constant load case)
        print('Applying Gravity')
        # gravity_load(db)
        # apply_nodal_loads(db, 'gravity')
        constant_analysis(db, 'gravity')
        
        # # Static
        # if df['Type'][case] == 'Static':
        #     print("static if")
        #     tag = list(db.loadCase.index).index(case) + 1 # ensures no tag repeat
        #     ops.timeSeries()
        #     ops.pattern()
        #     apply_nodal_loads(db, case)
        #     apply_nodal_loads(db)
        #     static_analysis(db)
        
        # # Pushover (displacement control)
        # elif df['Type'][case] == 'Disp':\
        #     print("disp ctrl if")
        
        # # Dynamic
        # elif df['Type'][case] == 'GM':
        #     print("dynamic if")
        #     tag = list(db.loadCase.index).index(case) + 1 # ensures no tag repeat
        #     pass

def constant_analysis(db, case):
    # Loads
    tag = list(db.loadCase.index).index(case) + 1
    ops.timeSeries('Constant', tag)
    ops.pattern('Plain', tag, tag)
    apply_nodal_loads(db, case)
    
    # Analysis
    ops.system("BandSPD")
    ops.numberer("Plain")
    ops.constraints("Transformation")
    ops.integrator("LoadControl", 1, 1)
    # Add later: pFlag = __ if option else 0
    ops.test('NormUnbalance', 1e-6, 200, 0)
    ops.algorithm("KrylovNewton")
    ops.analysis("Static")
    ops.analyze(1)
    ops.wipeAnalysis()
    ops.setTime(0.0)
    if case != 'gravity':
        ops.remove('timeSeries', tag)
        ops.remove('loadPattern', tag)

def static_analysis(db, case):
    # Number of steps
    loadFactor = db.loadCase.loc[case]['Incr']
    N = int(db.loadCase.loc[case]['Nsteps'])
    
    # Loads
    tag = list(db.loadCase.index).index(case) + 1 # ensures no tag repeat
    ops.timeSeries('Linear', tag)
    ops.pattern('Plain', tag, tag)
    apply_nodal_loads(db, case)
    
    # Analysis
    ops.system("BandSPD")
    ops.numberer("Plain")
    ops.constraints("Transformation")
    # Add later: pFlag = __ if option else 0
    ops.test('EnergyIncr', 1e-6, 100)
    ops.integrator("LoadControl", loadFactor)
    ops.algorithm("KrylovNewton")
    ops.analysis("Static")
    ops.analyze(N)
    ops.wipeAnalysis()
    # recursive_analyze_static()
    ops.remove('timeSeries', tag)
    ops.remove('loadPattern', tag)
    

def displacement_analysis(db, case):
    dofmap = {'X':1, 'Y':2, 'Z':3, 'MX':4, 'MY':5, 'MZ':6}
    # Number of steps
    loadFactor = db.loadCase.loc[case]['Incr']
    N = int(db.loadCase.loc[case]['Nsteps'])
    nodeTag = db.get_node_tag(db.loadCase.loc[case]['Reference'])
    dof = dofmap[db.loadCase.loc[case]['DOF']]
    print(nodeTag, dof)
    
    # Loads
    tag = list(db.loadCase.index).index(case) + 1 # ensures no tag repeat
    ops.timeSeries('Linear', tag)
    ops.pattern('Plain', tag, tag)
    apply_nodal_loads(db, case)
    
    # Analysis
    ops.system("BandSPD")
    ops.numberer("Plain")
    ops.constraints("Transformation")
    # Add later: pFlag = __ if option else 0
    ops.test('EnergyIncr', 1e-6, 100)
    ops.integrator("DisplacementControl", nodeTag, dof, loadFactor)
    ops.algorithm("KrylovNewton")
    ops.analysis("Static")
    ops.analyze(N)
    
    ops.wipeAnalysis()
    ops.remove('timeSeries', tag)
    ops.remove('loadPattern', tag)
    
#     pass

def dynamic_analysis(db, case, g=386.4):
    dofmap = {'X':1, 'Y':2, 'Z':3, 'MX':4, 'MY':5, 'MZ':6}
    dof = dofmap[db.loadCase.loc[case]['DOF']]
    
    tag = list(db.loadCase.index).index(case) + 1
    
    N = db.loadCase.loc[case]['Nsteps']
    dt_analysis = db.loadCase.loc[case]['Incr']
    
    filepath = db.loadCase.loc[case]['Reference']
    with open(filepath) as file:
        ispeer = gm.is_PEER(file)
    
    if ispeer:
        print('Reading PEER file...')
        values, dt = gm.PEER_to_list(filepath)
        ops.timeSeries('Path', tag, '-dt', dt, '-values', *values, '-factor', g)
        if N == 1:
            N = len(values)
    else:
        print('Reading txt file...')
        dt = db.loadCase.loc[case]['Incr']
        ops.timeSeries('Path', tag, '-dt', dt, '-filePath', filepath, '-factor', g)
        if N == 1:
            with open(filepath) as file:
                N = len(file.readlines())
    ops.pattern('UniformExcitation', tag, dof, '-accel', tag)
    
    # Analysis
    ops.system("BandSPD")
    ops.numberer("Plain")
    ops.constraints("Transformation")
    # Add later: pFlag = __ if option else 0
    # ops.test('NormUnbalance', 1e-6, 100, 2)
    ops.integrator('Newmark', 1/2, 1/4)
    # ops.integrator('CentralDifference')
    ops.algorithm("ModifiedNewton")
    ops.analysis("Transient")
    
    A = Convergence_Plot()
    
    
    # # ops.analyze(int(N), float(dt_analysis))
    for i in range(N):
        if (i+1)%100 == 0:
            print("Step: ", i+1)
        A.see_convergence(1, float(dt_analysis), 1e-6)
    #     ok = ops.analyze(1, float(dt_analysis))
    #     if ok == 0:
    #         A.add_step()
        
    #     # if (i+1)%10:
    #     #     print('{:8.3f}{:5d}{:10.2e}   {:d}'.format(dt_analysis*(i+1), ops.testIter(), ops.testNorm()[0], ok))
    #     else:
    #         ops.test('NormUnbalance', 1e-5, 100, 1)
    #         ok = ops.analyze(1, float(dt_analysis))
    #         if ok == 0:
    #             A.add_step()
            
    #         else:
    #             print('BAD')
    #             break
    #         A.add_step()
        # A.add_step()
    A.plot()
    # ops.wipeAnalysis()
    # ops.remove('timeSeries', tag)
    # ops.remove('loadPattern', tag)
    

# def recursive_analyze_static(n, dt, min_dt=1e-6):
#     for i in range(n):
#         ok = ops.analyze(1, dt)
#         if ok != 0 and dt >= min_dt:
#             dt = dt/2
#             recursive_analyze_static(2, dt)
            
# def recursive_analyze_EQ(n, dt, min_dt=1e-6):
#     for i in range(n):
#         ok = ops.analyze(1, dt)
#         if ok != 0 and dt >= min_dt:
#             dt = dt/2
#             recursive_analyze(1, dt)

def guaranteed_convergence(N, dt, maxFactor=100):
    ok = ops.analyze(1, float(dt_analysis))
    pass

def reset_gravity(db):
    tag = list(db.loadCase.index).index('gravity') + 1
    ops.remove('timeSeries', tag)
    ops.remove('loadPattern', tag)
    
def update_progress_label(step, dt):
    return 'Step: {:d}   Time: {:.3f}'.format(step, dt)

class Convergence_Plot():
    def __init__(self):
        self.Norms = []
    
    def add_step(self):
        norms = ops.testNorm()
        iters = ops.testIter()
        # print(iters, norms)
        for i in range(iters):
            self.Norms.append(norms[i])
    
    def plot(self):
        plt.figure()
        plt.semilogy(self.Norms, 'k-x')
        plt.grid()
        
    def see_convergence(self, N, dt, start_lim):
        ops.test('NormUnbalance', start_lim, 200)
        ok = ops.analyze(N, dt)
        if ok == 0:
            self.add_step()
        else:
            self.see_convergence(N, dt, start_lim*10)
        pass

def MCK():
    ops.wipeAnalysis()
        # Analysis
    ops.system("FullGeneral")
    ops.numberer("Plain")
    ops.constraints("Transformation")
    # ops.test('EnergyIncr', 1e-6, 100)
    ops.algorithm("Linear")
    # ops.analysis("Static")
    
    ops.analysis('Transient')
     
    # Mass
    ops.integrator('GimmeMCK',1.0,0.0,0.0)
    ops.analyze(1,0.0)
     
    # Number of equations in the model
    N = ops.systemSize() # Has to be done after analyze
     
    M = ops.printA('-ret') # Or use ops.printA('-file','M.out')
    M = np.array(M) # Convert the list to an array
    M.shape = (N,N) # Make the array an NxN matrix
     
    # Stiffness
    ops.integrator('GimmeMCK',0.0,0.0,1.0)
    ops.analyze(1,0.0)
    K = ops.printA('-ret')
    K = np.array(K)
    K.shape = (N,N)
     
    # Damping
    ops.integrator('GimmeMCK',0.0,1.0,0.0)
    ops.analyze(1,0.0)
    C = ops.printA('-ret')
    C = np.array(C)
    C.shape = (N,N)
    return M, C, K