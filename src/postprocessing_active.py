# -*- coding: utf-8 -*-
"""
Function definitions to be called in the console or by other modules.
These fuctions act on an active OpenSees model, before wipe() is called.

Created on Mon Nov 15 11:24:08 2021
@author: wroser
"""

import openseespy.opensees as ops

# %% Nodes
def print_node_disps_and_rxns(db, nodes, get_tag=True):
    '''
    Print formatted table of nodal displacements and reactions.

    Parameters
    ----------
    nodes : list
        List of node tags (str). Set get_tag to False if passing integer tags.

    Returns
    -------
    None. All output is printed to console.

    '''
    # Node names (str) to OpenSees tags (int)
    if get_tag:
        nodes = [db.get_node_tag(node) for node in db.get_node_list()]
    
    # Main function. Loop through nodes and print to console.
    ops.reactions()
    for n in nodes:
        disps = ops.nodeDisp(n)
        print('{:>10}'.format(db.get_node_name(n)), '{:15.5f}{:15.5f}{:15.5e}{:15.0f}{:15.0f}{:15.0f}'.format(*disps))
        rxns = ops.nodeReaction(n)
        print('          ', '{:15.3f}{:15.3f}{:15.3f}{:15.2f}{:15.2f}{:15.2f}\n'.format(*rxns))

# %% Elements