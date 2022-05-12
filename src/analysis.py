# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 16:25:13 2022

@author: wroser
"""

import os
import openseespy.opensees as ops
from src.loads import apply_nodal_loads

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
    ops.test('NormUnbalance', 1e-6, 200, 1)
    ops.algorithm("KrylovNewton")
    ops.analysis("Static")
    ops.analyze(1)
    ops.wipeAnalysis()
    # ops.setTime(0.0)

# def static_analysis(db, case):
#     # Loads
#     tag = list(db.loadCase.index).index(case) + 1 # ensures no tag repeat
#     print(tag)
#     ops.timeSeries('Linear', tag)
#     ops.pattern('Plain', tag, tag)
#     apply_nodal_loads(db, case)
#     print('Loads COmplete')
#     # Analysis
#     ops.system("BandSPD")
#     ops.numberer("Plain")
#     ops.constraints("Transformation")
#     ops.test('EnergyIncr', 1e-6, 100)
#     ops.integrator("LoadControl", 0.1, 10)
#     ops.algorithm("KrylovNewton")
#     ops.analysis("Static")
#     recursive_analyze_static()

# def displacement_analysis(db, case):
    
#     pass

# def dynamic_analysis(db, case):
#     tag = list(db.loadCase.index).index(case) + 1
#     # ops.timeSeries(, tag)
#     # ops.pattern(, tag, tag)
#     pass

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

def reset_gravity(db):
    tag = list(db.loadCase.index).index('gravity') + 1
    ops.remove('timeSeries', tag)
    ops.remove('loadPattern', tag)