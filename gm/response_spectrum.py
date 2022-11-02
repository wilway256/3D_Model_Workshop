# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 08:08:38 2022

@author: wfros
"""

import matplotlib.pyplot as plt
import numpy as np
import openseespy.opensees as ops

def max_response(Tn, accels, dt, g=386.4):
    ops.wipe()
    ops.model('basic', '-ndm', 1, '-ndf', 1)
    ops.node(1, 0.0)
    ops.node(2, 0.0)
    ops.fix(1, 1)
    ops.mass(2, 1.0)
    k = 4*np.pi**2/Tn
    ops.uniaxialMaterial('Elastic', 1, k)
    ops.element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 1)
    
    ops.timeSeries('Path', 1, '-dt', dt, '-values', *accels, '-factor', g) # define acceleration vector from file (dt=0.005 is associated with the input file gm)
    ops.pattern('UniformExcitation', 2, 1, '-accel', 1)	
    
    ops.constraints('Plain')    	 # how it handles boundary conditions
    ops.numberer('Plain')    # renumber dof's to minimize band-width (optimization), if you want to
    ops.system('BandGeneral') # how to store and solve the system of equations in the analysis
    ops.algorithm('Linear')	 # use Linear algorithm for linear analysis
    ops.integrator('Newmark', 0.5, 0.25)    # determine the next time step for an analysis
    ops.analysis('Transient')   # define type of analysis: time-dependent
    
    x = 0
    a = 0
    
    for i in range(len(accels)):
        ops.analyze(1, dt)
        x = max(x, abs(ops.nodeDisp(2)[0]))
        a = max(a, abs(ops.nodeAccel(2)[0]))
        
    return x, a

def response_spectrum(accels, dt):
    # Sample points
    Tns = np.linspace(0.01, 20.0)
    d = np.zeros(Tns.shape)
    a = np.zeros(Tns.shape)
    # Aggregate responses
    for i, Tn in enumerate(Tns):
        d[i], a[i] = max_response(Tn, accels, dt)
        
    fig, ax = plt.subplots()
    ax.plot(Tns, d)
    ax.plot(Tns, a)

if __name__ == "__main__":
    
    filename = '09 TallWoodEqs_225_4213_x.txt'
    with open(filename) as file:
        accels = file.readlines()
        for i, line in zip( range(len(accels)), accels):
            accels[i] = float(line)
    
    response_spectrum(accels, 0.8)
    # print(a,b)
    
    