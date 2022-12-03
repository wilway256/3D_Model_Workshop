# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 16:25:13 2022

@author: wroser
"""

# %% Imports
import numpy as np
# import tkinter as tk
# from tkinter import ttk
# import os
import openseespy.opensees as ops
from src.loads import apply_nodal_loads
import gm.gm_reader as gm
import matplotlib.pyplot as plt
# import opsvis
# from tools.spy import spy
from time import strftime


# %% Code
'''
def constant_analysis(db, case):
    print('Constant')
    # Loads
    tag = list(db.loadCase.index).index(case) + 1
    ops.timeSeries('Constant', tag)
    ops.pattern('Plain', tag, tag)
    apply_nodal_loads(db, case)
    
    # Analysis
    ops.system("BandSPD")
    ops.numberer("RCM")
    ops.constraints("Transformation")
    ops.integrator("LoadControl", 1, 1)
    # Add later: pFlag = __ if option else 0
    ops.test('NormUnbalance', 1e-6, 200, 0)
    ops.algorithm("ModifiedNewton")
    ops.analysis("Static")
    ops.analyze(1)
    
    # opsvis.plot_defo(interpFlag=0)
    
    ops.wipeAnalysis()
    ops.setTime(0.0)
    if case != 'gravity':
        ops.remove('timeSeries', tag)
        ops.remove('loadPattern', tag)

def static_analysis(db, case):
    print('Static')
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
    ops.numberer("RCM")
    ops.constraints("Transformation")
    # Add later: pFlag = __ if option else 0
    ops.test('EnergyIncr', 1e-6, 100, 0)
    ops.integrator("LoadControl", loadFactor)
    ops.algorithm("ModifiedNewton")
    ops.analysis("Static")
    ops.analyze(N)
    
    # opsvis.plot_defo(interpFlag=0)
    
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
    ops.numberer("RCM")
    ops.constraints("Transformation")
    # Add later: pFlag = __ if option else 0
    ops.test('EnergyIncr', 1e-6, 100)
    ops.integrator("DisplacementControl", nodeTag, dof, loadFactor)
    ops.algorithm("ModifiedNewton")
    ops.analysis("Static")
    ops.analyze(N)
    
    # opsvis.plot_defo(interpFlag=0)
    
    # ops.wipeAnalysis()
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
'''
def sumForces():
    totalApp = np.zeros((6))
    totalRxn = np.zeros((6))
    Mapp = [0.0, 0.0, 0.0]
    Mrxn = [0.0, 0.0, 0.0]
    ops.reactions('-dynamic')
    
    for tag in ops.getNodeTags():
        totalApp += np.array(ops.nodeUnbalance(tag))
        totalRxn += np.array(ops.nodeReaction(tag))
        x, y, z = ops.nodeCoord(tag)
        
        Mapp[0] = y * ops.nodeUnbalance(tag)[2] - z * ops.nodeUnbalance(tag)[1]
        Mrxn[0] = y *  ops.nodeReaction(tag)[2] - z *  ops.nodeReaction(tag)[1]
        
        Mapp[1] = -x * ops.nodeUnbalance(tag)[2] + z * ops.nodeUnbalance(tag)[0]
        Mrxn[1] = -x *  ops.nodeReaction(tag)[2] + z *  ops.nodeReaction(tag)[0]
        
        Mapp[2] = x * ops.nodeUnbalance(tag)[1] - y * ops.nodeUnbalance(tag)[0]
        Mrxn[2] = x *  ops.nodeReaction(tag)[1] - y *  ops.nodeReaction(tag)[0]
        
        totalApp += np.array([0.0, 0.0, 0.0, *Mapp])
        totalRxn += np.array([0.0, 0.0, 0.0, *Mrxn])
    
    for title, array in zip(['Applied: ', 'Reaction:'], [totalApp, totalRxn]):
        print('{:10}{:10.2f}{:10.2f}{:10.2f}{:10.2f}{:10.2f}{:10.2f}'.format(title, *array))
    print('')

# %% Scripts

def gravity(model, record=True):
    print('Gravity analysis...')
    # Loads
    ops.timeSeries('Constant', 1)
    ops.pattern('Plain', 1, 1)
    model.apply_nodal_loads('gravity')
    
    # Analysis
    ops.system("UmfPack")
    ops.numberer("AMD")
    ops.constraints("Transformation")
    # ops.constraints("Lagrange", 1e6, 1e6)
    ops.integrator("LoadControl", 1, 1)
    ops.test('EnergyIncr', 1e-20, 200, 1)
    ops.algorithm("KrylovNewton")
    ops.analysis("Static")
    ops.analyze(1)
    
    # Cleanup
    sumForces()
    # opsvis.plot_defo(interpFlag=0)
    ops.setTime(0.0)
    ops.wipeAnalysis()
    if record:
        model.apply_recorders(model.active_case)
        ops.record()
        ops.remove('recorders')
        ops.remove('timeSeries', 1)
        ops.remove('loadPattern', 1)

def ramp_loadcontrol(model, N, dt, *cases):
    
    N = int(N)
    dt = float(dt)
    
    fig, ax = plt.subplots()
    x = np.zeros(N)
    y = np.zeros(N)
    ax.set_title(model.active_case)
    fig.suptitle('Top of Bldg. Displacement')
    ax.set_xlabel('x (in.)')
    ax.set_ylabel('y (in.)')
    
    gravity(model, record=False)
    
    print('Load control analysis...')
    # Loads
    ops.timeSeries('Linear', 2)
    ops.pattern('Plain', 2, 2)
    for case in cases:
        model.apply_nodal_loads(case)
    
    # Recorders
    model.apply_recorders(model.active_case)
    ops.record()
    
    # Analysis Options
    ops.system("UmfPack")
    ops.numberer("Plain")
    ops.constraints("Transformation")
    # ops.constraints("Lagrange", 1e20, 1e20)
    ops.integrator("LoadControl", dt, 1)
    ops.test('EnergyIncr', 1e-10, 200, 1)
    ops.algorithm("KrylovNewton")
    ops.analysis("Static")
    
    # Analysis Loop
    for i in range(N):
        if (i+1)%50 == 0:
            print("Step: ", i+1)
        ok = ops.analyze(1)
        if ok != 0: # If does not converge
            print(ops.testNorm()[-10:-1])
        #     ops.algorithm("ModifiedNewton")
        #     ops.test('EnergyIncr', 1e-2, 500, 1)
        x[i], y[i] = ops.nodeDisp(model.get_node_tag('F11_center'))[:2]
        # sumForces()
    
    ax.plot(x, y)
    ax.grid()
    # Cleanup
    ops.remove('recorders')
    ops.remove('timeSeries', 1)
    ops.remove('loadPattern', 1)
    ops.remove('timeSeries', 2)
    ops.remove('loadPattern', 2)
    ops.wipeAnalysis()
    ops.reset()

# def hysteresis_force(model, forces, *cases):
    
#     forces = [float(x) for x in forces.split(';')]
    
    
    
#     gravity(model, record=False)
    
#     print('Load control analysis...')
#     # Loads
#     ops.timeSeries('Linear', 2)
#     ops.pattern('Plain', 2, 2)
#     for case in cases:
#         model.apply_nodal_loads(case)
    
#     # Recorders
#     model.apply_recorders(model.active_case)
#     ops.record()
    
#     # Analysis Options
#     ops.system("UmfPack")
#     ops.numberer("Plain")
#     ops.constraints("Transformation")
#     # ops.constraints("Lagrange", 1e6, 1e6)
#     dt = forces[0]/50
#     ops.integrator("LoadControl", dt, 1)
#     ops.test('EnergyIncr', 1e-8, 200, 1)
#     ops.algorithm("KrylovNewton")
#     ops.analysis("Static")
    
#     # Analysis Loop
#     for force in forces:
#         dt = force/50
#         ops.integrator("LoadControl", dt, 1)
#         ok = ops.analyze(50)
        
#         print(force, ops.nodeDisp(model.get_node_tag('F11_center')))
#         sumForces()
        
#         ops.integrator("LoadControl", -dt, 1)
#         ok = ops.analyze(100)
        
#         print(-force, ops.nodeDisp(model.get_node_tag('F11_center')))
#         sumForces()
        
#         ops.integrator("LoadControl", dt, 1)
#         ok = ops.analyze(50)
    
#     # Cleanup
#     ops.remove('timeSeries', 1)
#     ops.remove('loadPattern', 1)
#     ops.remove('timeSeries', 2)
#     ops.remove('loadPattern', 2)
#     ops.wipeAnalysis()
#     ops.reset()


def ramp_dispcontrol(model, node, dof, N, dt, *cases):
    print(node, dof, N, dt)
    tag = model.get_node_tag(node)
    dofs = {'X':1, 'Y':2, 'Z':3}
    dof = dofs[dof]
    
    gravity(model, record=False)
    
    print('Disp control analysis...')
    # Loads
    ops.timeSeries('Constant', 2)
    ops.pattern('Plain', 2, 2)
    for case in cases:
        model.apply_nodal_loads(case)
    
    # Recorders
    model.apply_recorders(model.active_case)
    ops.record()
    
    # Analysis Options
    ops.system("UmfPack")
    ops.numberer("Plain")
    # ops.constraints("Lagrange", 1e6, 1e6)
    ops.constraints("Transformation")
    # print(type(dt), dt, float(dt))
    ops.integrator("DisplacementControl", tag, dof, float(dt))
    ops.test('NormDispIncr', 1e-6, 100, 1)
    ops.algorithm("KrylovNewton")
    ops.analysis("Static")
    testNorm = 1e-4
    # Analysis Loop
    for i in range(int(N)):
        print('Step:', i+1)
        ok = ops.analyze(1)
        print(ok)
        if ok != 0:
        
            ops.test('NormDispIncr', 1e-5, 10, 1)
        
            ok = ops.analyze(1)
            print(ok)
            if ok !=0:
                ops.algorithm("NewtonLineSearch")
                ops.test('NormDispIncr', 1e-4, 10, 1)
                ok = ops.analyze(1)
                # ops.test('NormDispIncr', 1e-5, 10, 1)
                # ops.algorithm("KrylovNewton")
                print(ok)
                if ok != 0:
                    testNorm = testNorm * 2
                    ops.test('NormDispIncr', testNorm, 10, 1)
                    ok = ops.analyze(1)
                    print(ok)
                    if ok != 0:
                        print(ops.testNorm())
                        break
    
    # Cleanup
    ops.remove('timeSeries', 1)
    ops.remove('loadPattern', 1)
    ops.remove('timeSeries', 2)
    ops.remove('loadPattern', 2)
    ops.wipeAnalysis()
    ops.reset()
    
    
def hysteresis(model, node, dof, disps, *cases):
    
    steps = 20
    
    tag = model.get_node_tag(node)
    disps = [float(x) for x in disps.split(';')]
    dofs = {'X':1, 'Y':2, 'Z':3}
    dof = dofs[dof]
    
    gravity(model, record=False)
    
    print('Disp control analysis...')
    
    # Load Pattern
    ops.timeSeries('Linear', 2)
    ops.pattern('Plain', 2, 2)
    for case in cases:
        model.apply_nodal_loads(case)
    
    # Recorders
    model.apply_recorders(model.active_case)
    ops.record()
    
    # Analysis Options
    ops.system("UmfPack")
    ops.numberer("Plain")
    ops.constraints("Transformation")
    # ops.constraints("Lagrange", 1e6, 1e6)
    dt = disps[0]/50
    print('dt = {}'.format(dt))
    ops.integrator("DisplacementControl", tag, dof, dt)
    ops.test('NormDispIncr', 1e-6, 100, 1 ) # Will be overwritten later
    # ops.algorithm("NewtonLineSearch")
    ops.algorithm("NewtonLineSearch")
    ops.analysis("Static")
    
    
    
    # Analysis Loop
    for disp in disps:
        
        
        testNorm = 1e-6
        dt = 0.1
        steps = int(disp/dt)
        
        print('\nStarting +/-{} in. over 4x{} steps...'.format(disp, steps))
        
        ops.integrator("DisplacementControl", tag, dof, dt)
        _analyze_iterative_tolerance('NormDispIncr',  N=steps, testNorm=testNorm, testIter=25, pFlag=1)
        
        print('Max. displacement at', node, '\n  Intended:', disp, dof, '\n  Actual:', ops.nodeDisp(model.get_node_tag(node)))
        sumForces()
        
        ops.integrator("DisplacementControl", tag, dof, -dt)
        _analyze_iterative_tolerance('NormDispIncr',  N=2*steps, testNorm=testNorm, testIter=25, pFlag=1)
        
        print(-disp, ops.nodeDisp(model.get_node_tag(node)))
        sumForces()
        
        ops.integrator("DisplacementControl", tag, dof, dt)
        _analyze_iterative_tolerance('NormDispIncr',  N=steps, testNorm=testNorm, testIter=25, pFlag=1)
    
    # Cleanup
    ops.remove('timeSeries', 1)
    ops.remove('loadPattern', 1)
    ops.remove('timeSeries', 2)
    ops.remove('loadPattern', 2)
    ops.wipeAnalysis()
    ops.reset()
    
def initial_stiffness(model, dof, *cases):
    
    import numpy as np
    import matplotlib.pyplot as plt
    from src.analysis import sumForces
    from src.analysis import gravity
    node = 'F11_center'
    # dof = 'X'
    Ns = [10]#, 40, 40, 40, 40, 40]
    dts = [0.25]#, -0.25, 0.25, -0.25, 0.5, -0.5]
    tag = model.get_node_tag(node)
    dofs = {'X':1, 'Y':2, 'Z':3}
    dof = dofs[dof]
    # cases = ['ASCE_X']
    
    phi = np.zeros((sum(Ns)))
    M = phi.copy()
    
    gravity(model, record=False)
    
    print('Disp control analysis...')
    # Loads
    ops.timeSeries('Constant', 2)
    ops.pattern('Plain', 2, 2)
    for case in cases:
        model.apply_nodal_loads(case)
        model.active_case = case
    
    # Recorders
    model.apply_recorders('disctrl')
    ops.record()
    
    # Analysis Options
    ops.system("UmfPack")
    ops.numberer("Plain")
    # ops.constraints("Lagrange", 1e6, 1e6)
    ops.constraints("Transformation")
    # print(type(dt), dt, float(dt))
    
    
    # ops.integrator("MinUnbalDispNorm", 1.0)
    # ops.integrator("ArcLength", 1.0, 10.0)
    ops.integrator("DisplacementControl", tag, dof, float(dts[0]))
    ops.test('NormDispIncr', 1e-6, 100, 1)
    ops.algorithm("KrylovNewton")
    ops.analysis("Static")
    
    
    # Analysis Loop
    step = 0
    for dt, N in zip(dts, Ns):
        ops.integrator("DisplacementControl", tag, dof, float(dt))
        for i in range(int(N)):
            print('Step:', i+1)
            ok = ops.analyze(1)
            print(ok)
            if ok != 0:
                
                ops.test('NormDispIncr', 1e-5, 10, 1)
                
                ok = ops.analyze(1)
                print(ok)
                if ok !=0:
                    ops.algorithm("NewtonLineSearch")
                    ops.test('NormDispIncr', 1e-4, 10, 1)
                    ok = ops.analyze(1)
                    ops.test('NormDispIncr', 1e-5, 10, 1)
                    ops.algorithm("KrylovNewton")
                    print(ok)
                    if ok != 0:
                        break
            
            if dof == 1:
                nodetag = 5
                idof = 4
                eletag = 33
            elif dof == 2:
                nodetag = 6
                idof = 3
                eletag = 35
            
            phi[step] = ops.nodeDisp(nodetag)[idof]
            M[step] = ops.eleResponse(eletag, 'force')[idof]
            # print(ops.nodeDisp(model.get_node_tag('F11_center')))
            # print(ops.nodeDisp(5)[4], '\n')
            step+=1
        
    # plt.figure()
    # plt.plot(phi, M, '.-')
    # plt.title('with UFP')
            # ops.algorithm("KrylovNewton")
            
            
    for i in range(len(M)-1):
        K = (M[i+1] - M[i]) / (phi[i+1] - phi[i])
        print('K_rot = {}'.format(K))
    
    # Cleanup
    ops.remove('timeSeries', 1)
    ops.remove('loadPattern', 1)
    ops.remove('timeSeries', 2)
    ops.remove('loadPattern', 2)
    ops.wipeAnalysis()
    ops.reset()

def eq3DOF(model, filename, dt, N):
    
    gravity(model, record=False)
    
    print('Earthquake analysis' + filename + '...')
    
    # Ground motion
    dt = float(dt)
    N = int(N)
    
    dof = 'XYZ'
    suffix = 'xyz'
    dofs = {'X':1, 'Y':2, 'Z':3}
    
    
    for i in range(3):
        path = 'gm\\' + filename + '_' + suffix[i] + '.txt'
        print(path, dt, i+2)
        ops.timeSeries('Path', i + 2, '-dt', dt, '-filePath', path, '-factor', 32.2*12)
        ops.pattern('UniformExcitation', i + 2, dofs[dof[i]], '-accel', i + 2)
    
    
    
    
    # Recorders
    model.apply_recorders(model.active_case)
    ops.record()
    
    # Analysis Options
    ops.system("UmfPack")
    ops.numberer("Plain")
    ops.constraints("Transformation")
    ops.test('NormDispIncr', 1e-10, 100, 2)
    ops.algorithm("KrylovNewton")
    ops.integrator('Newmark', 0.5, 0.25)
    ops.analysis("Transient")
    
    # Analysis Loop
    for i in range(int(N)):
        if (i+1)%1000 == 0:
            print("Step: ", i+1, strftime('%H:%M:%S'))
        ok = ops.analyze(1, dt)
        
        if ok != 0:
            ok = ops.analyze(10, dt/10)
            if ok !=0:
                
            #     if ok != 0:
                    print(ops.testNorm())
                    break
    
    # Cleanup
    for i in range(1, 5):
        ops.remove('timeSeries', i)
        ops.remove('loadPattern', i)
    ops.remove('recorders')
    ops.wipeAnalysis()
    ops.reset()

def _analyze_iterative_tolerance(test,  N=1, testNorm=1e-6, testIter=100, pFlag=0):
    
    ops.test(test, testNorm, testIter, pFlag)
    for i in range(N):
        ok = ops.analyze(1)
        
        if ok != 0:
            print('Test failed: Norm = {}'.format(ops.testNorm()[-1]))
            print("Trying Krylov".format(i+1, 2*testNorm))
            ops.algorithm("KrylovNewton")
            ok = ops.analyze(1)
            
            if ok != 0:
                print('Test failed: Norm = {}'.format(ops.testNorm()[-1]))
                print("Tolerance increased - Step: {} New Tolerance: {}".format(i+1, 2*testNorm))
                ok = _analyze_iterative_tolerance(test,  N, testNorm*2, testIter, pFlag)
    
    return ok