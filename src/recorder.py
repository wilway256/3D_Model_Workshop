# -*- coding: utf-8 -*-
"""
Created:  Mon May  9 15:35:25 2022
Author:   wroser
=============================================================================
Description:

"""

# %% Imports
from  openseespy.opensees import recorder
import numpy as np

# %% Code
def apply_recorders(db, case, outdir=''):
    df = db.recorders
    for i in df.index:
        if df.at[i, 'Case'] == case or df.at[i, 'Case'] == '':
            respType = df.at[i, 'RespType']
            fileName = outdir + df.at[i, 'FileName'] + '.xml'
            if df.at[i, 'Type'] == 'node':
                nodeTags = db.get_node_subset(df.at[i, 'Group'], tag=True)
                try:
                    dofs = df.at[i, 'Node DOF'].split(',')
                    for j in range(len(dofs)):
                        dofs[j] = int(dofs[j])
                except AttributeError:
                    dofs = [1, 2, 3, 4, 5, 6]
                arg1 = 'Node' if df.at[i, 'Envelope'] != 'Y' else 'EnvelopeNode'
                
                # print('rec', fileName, nodeTags, dofs)
                recorder(arg1, '-xml', fileName, '-time', '-node', *nodeTags, '-dof', *dofs, respType)
            elif df.at[i, 'Type'].startswith('ele'):
                if df.at[i, 'Envelope'] == 'Y':
                    pass
                else:
                    pass
            else:
                print('Error: Recorder defined in Excel but not recorder.py.')
        else:
            # Do nothing. This load case does not include these recorders.
            pass

