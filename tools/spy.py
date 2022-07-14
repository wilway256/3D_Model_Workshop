# -*- coding: utf-8 -*-
"""
Created:  Thu Jun  9 14:48:30 2022
Author:   wroser
=============================================================================
Description:

"""

# %% Imports
import numpy as np
import matplotlib.pyplot as plt
import openseespy.opensees as ops

# %% Code
def spy(system, numberer):
    
    ops.system(system)
    ops.numberer(numberer)
    ops.constraints("Transformation")
    ops.test('EnergyIncr', 1e-6, 100, 0)
    ops.integrator("LoadControl", 1)
    ops.algorithm("ModifiedNewton")
    ops.analysis("Static")
    ops.analyze(1)
    
    Neqn = ops.systemSize()
    print(Neqn)
    # Build spy matrix
    SpyMatrix = np.identity(Neqn)
    for e in ops.getEleTags():
       dofs = []
       # Build list of DOFs for this element
       for nd in ops.eleNodes(e):
          dofs += ops.nodeDOFs(nd)
    
          for idof in dofs:
             if idof < 0: # Constrained DOF
                continue
             for jdof in dofs:
                if jdof < 0: # Constrained DOF
                   continue
                SpyMatrix[idof,jdof] = 1.0
    
    # Determine bandwidth
    bw = 0
    for i in range(Neqn):
       bwi = 0
       # Find non-zero farthest from diagonal on this row
       for j in range(i,Neqn):
          kij = SpyMatrix[i,j]
          if kij != 0.0:
             bwi = j-i+1
       if bwi > bw:
          bw = bwi
    
    # Plot
    ttl = system + ', ' + numberer
    fig = plt.figure()
    plt.title(ttl)
    plt.spy(SpyMatrix,markersize=.05)
    plt.xlabel(f'Bandwidth={bw}')
    # plt.savefig('alt_' + system + '_' + numberer + '.png')
    # plt.close(fig)

if __name__ == '__main__':
    for i in ['FullGeneral']:#, 'BandGeneral', 'BandSPD', 'ProfileSPD', 'SuperLU', 'UmfPack', 'SparseSYM', ]:
        for j in ['Plain', 'RCM', 'AMD']:
            spy(i, j)
            ops.wipeAnalysis()
            ops.reset()