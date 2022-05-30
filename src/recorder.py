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
            
            # -------  NODES   -------
            if df.at[i, 'Type'] == 'node':
                tags = db.parse('node', df.at[i, 'Arguments'])
                tags = db.get_tag('node', tags)
                try:
                    dofs = df.at[i, 'Node DOF'].split(',')
                    for j in range(len(dofs)):
                        dofs[j] = int(dofs[j])
                except AttributeError:
                    dofs = [1, 2, 3, 4, 5, 6]
                arg1 = 'Node' if df.at[i, 'Envelope'] != 'Y' else 'EnvelopeNode'
                
                # print('rec', fileName, nodeTags, dofs)
                recorder(arg1, '-xml', fileName, '-time', '-node', *tags, '-dof', *dofs, respType)
                
            # ------- ELEMENTS -------
            elif df.at[i, 'Type'].startswith('ele'):
                tags = db.parse('ele', df.at[i, 'Arguments'])
                tags = db.get_tag('ele', tags)
                
                arg1 = 'Element' if df.at[i, 'Envelope'] != 'Y' else 'EnvelopeElement'
                
                # print('rec', fileName, nodeTags, dofs)
                recorder(arg1, '-xml', fileName, '-time', '-ele', *tags, respType)
                
            else:
                print('Error: Recorder defined in Excel but not recorder.py.')
        else:
            # Do nothing. This load case does not include these recorders.
            pass
