# -*- coding: utf-8 -*-
"""
Created:  Thu Jun  9 15:27:22 2022
Author:   wroser
=============================================================================
Description:
WARNING: May take a long time to run.
"""

# %% Imports
from timeit import default_timer
import numpy as np
import matplotlib.pyplot as plt
import openseespy.opensees as ops

# %% Code
output = []

for i in ['FullGeneral', 'BandGeneral', 'BandSPD', 'ProfileSPD', 'SuperLU', 'UmfPack', 'SparseSYM' ]:
    for j in ['Plain', 'RCM', 'AMD']:
        for k in ['NormUnbalance', 'NormDispIncr', 'EnergyIncr', 'RelativeNormUnbalance', 'RelativeNormDispIncr', 'RelativeTotalNormDispIncr', 'RelativeEnergyIncr']:
            for l in ['Linear', 'Newton', 'ModifiedNewton', 'KrylovNewton', 'SecantNewton', 'RaphsonNewton', 'PeriodicNewton']:
        
                ops.timeSeries('Constant', 1)
                ops.pattern('Plain', 1, 1)
                ops.load(226, *[1,1,1,1,1,1]) # 226 is top center
                
                start = default_timer()
                ops.system(i)
                ops.numberer(j)
                ops.constraints("Transformation")
                ops.test(k, 1e-6, 100, 2)
                ops.integrator("LoadControl", 1)
                ops.algorithm(l)
                ops.analysis("Static")
                ok = ops.analyze(1)
                
                time = default_timer() - start
                # print(i,j,time,ok)
                output.append([i,j,k,l,time,ok,ops.testIter(),ops.testNorm()])
                
                ops.remove('timeSeries', 1)
                ops.remove('loadPattern', 1)
                ops.wipeAnalysis()
                ops.reset()