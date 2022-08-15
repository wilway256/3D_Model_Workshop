# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 11:16:06 2021

@author: wroser
"""

# %% Imports
import numpy as np
from numpy.linalg import solve
import openseespy.opensees as ops
from math import pi


# %% Module Level Variables
mat_dict = {}
integrations = {} # to be filled with {N: ((x,y), area)}

# %% Definitions
def make_model(modelType='3D'):
    '''
    Wrapper for OpenSees model builder command.
    '''
    ops.wipe()
    # print('No model type specified. Using 3D, 6 DOF model by default.')
    if modelType == '3D':
        ops.model('Basic', '-ndm', 3, '-ndf', 6)
    elif modelType == '2D':
        ops.model('Basic', '-ndm', 2, '-ndf', 3)
    elif modelType == '1D':
        ops.model('Basic', '-ndm', 1, '-ndf', 1)
    elif modelType == 'Truss':
        ops.model('Basic', '-ndm', 2, '-ndf', 2)
    else:
        raise ValueError("Must use '1D', '2D', '3D', or 'Truss'")

def define_nodes(db):
    '''
    Loop through nodes in database and create them in OpenSees.
    '''
    df = db.node
    node_names = db.get_node_list()
    for node in node_names:
        tag = db.get_node_tag(node)
        x = df.at[node, 'X']
        y = df.at[node, 'Y']
        z = df.at[node, 'Z']
        ops.node(tag, x, y, z)
        # Debugging: Add nonzero mass to every DOF:
        # ops.mass(tag, *[0.01, 0.01, 0.01, 0.01, 0.01, 0.01])
    
def fix_nodes(db):
    '''
    Loop through list of node names. Fix DOFs based on True/False table.
    '''
    df = db.fixity
    for node in df.index:
        tag = db.get_node_tag(node)
        dof_fixity = list( df.loc[node] )
        dof_fixity = [int(i) for i in dof_fixity]
        ops.fix(tag, *dof_fixity)

def assign_node_mass(db):
    '''
    Loop through list of node names. Add mass at all nodal DOFs at once.
    '''
    df = db.nodeMass
    for node in df.index:
        tag = db.get_node_tag(node)
        node_dof_mass = list(df.loc[node])
        ops.mass(tag, *node_dof_mass)
        
def make_elements(db, rigidLinkConstraint=True):
    print('Ele Loop')
    dfEle = db.ele
    dfProp = db.eleData
    dfTransf = db.transf
    dfMS = db.multispring
    global mat_dict
    release = {'I':1, 'J':2, 'IJ':3}
    
    for ele in dfEle.index:
        # print(ele)
        eleTag = db.get_ele_tag(ele)
        iNode = db.get_node_tag( dfEle.at[ele, 'iNode'] )
        jNode = db.get_node_tag( dfEle.at[ele, 'jNode'] )
        eleType = dfEle.at[ele, 'Type']
        eleInfo = dfEle.at[ele, 'PropertyID']
        # print(eleType) # for debugging
        
        if eleType == 'elasticBeamCol':
            Area = dfProp.at[eleInfo, 'A']
            E_mod = dfProp.at[eleInfo, 'E']
            G_mod = dfProp.at[eleInfo, 'G']
            Jxx = dfProp.at[eleInfo, 'J']
            Iy = dfProp.at[eleInfo, 'Iy']
            Iz = dfProp.at[eleInfo, 'Iz']
            transf = dfEle.at[ele, 'Transformation']
            releasey = dfProp.at[eleInfo, 'releasey']
            if releasey not in ['I', 'J', 'IJ']:
                releasey = 0
            else:
                releasey = release[releasey]
            releasez = dfProp.at[eleInfo, 'releasez']
            if releasez not in ['I', 'J', 'IJ']:
                releasez = 0
            else:
                releasez = release[releasez]
            transfTag = int( dfTransf.at[transf, 'Tag'] )
            ops.element('elasticBeamColumn', eleTag, iNode, jNode, Area, E_mod, G_mod, Jxx, Iy, Iz, transfTag,
                        '-releasey', releasey, '-releasez', releasez)
            
        elif eleType == 'Timoshenko':
            Area = dfProp.at[eleInfo, 'A']
            Av = 5/6*Area
            E_mod = dfProp.at[eleInfo, 'E']
            G_mod = dfProp.at[eleInfo, 'G']
            Jxx = dfProp.at[eleInfo, 'J']
            Iy = dfProp.at[eleInfo, 'Iy']
            Iz = dfProp.at[eleInfo, 'Iz']
            transf = dfEle.at[ele, 'Transformation']
            transfTag = int( dfTransf.at[transf, 'Tag'] )
            ops.element('ElasticTimoshenkoBeam', eleTag, iNode, jNode,
                        E_mod, G_mod, Area, Jxx, Iy, Iz, Av, Av, transfTag)
            
        elif eleType == 'rigidLink':
            if rigidLinkConstraint:
                ops.rigidLink('beam', iNode, jNode)
            else:
                eleInfo = 'rigidLink'
                Area = dfProp.at[eleInfo, 'A']
                E_mod = dfProp.at[eleInfo, 'E']
                G_mod = dfProp.at[eleInfo, 'G']
                Jxx = dfProp.at[eleInfo, 'J']
                Iy = dfProp.at[eleInfo, 'Iy']
                Iz = dfProp.at[eleInfo, 'Iz']
                transf = 'Std Beam'
                transfTag = int( dfTransf.at[transf, 'Tag'] )
                ops.element('elasticBeamColumn', eleTag, iNode, jNode, Area, E_mod, G_mod, Jxx, Iy, Iz, transfTag)
            
        
        elif eleType == 'UFP':
            material = eleInfo
            
            if material in mat_dict.keys():
                tag = mat_dict[material]
            else:
                tag = make_material(eleInfo, dfProp)

            ops.element('zeroLength', eleTag, iNode, jNode,
                        '-mat', tag, '-dir', 3) # 3 = z-direction
        
        elif eleType == 'PT':
            material = eleInfo
            
            # Skip if material already generated. Initialize material otherwise.
            if material in mat_dict.keys():
                tag = mat_dict[material]
            else:
                tag = make_material(eleInfo, dfProp)
            
            A = dfProp.at[eleInfo, 'A']
            # print('Truss tag: ', tag)
            ops.element('corotTruss', eleTag, iNode, jNode, A, tag)
        
        elif eleType == 'multiSpring':
            # Get properties
            E = dfProp.at[eleInfo, 'E']
            alpha = dfProp.at[eleInfo, 'alpha']
            fy = dfProp.at[eleInfo, 'fy']
            Leff = dfProp.at[eleInfo, 'Leff']
            
            A = dfMS.at[ele, 'Area']
            K = dfMS.at[ele, 'K']
            
            Fy = fy * A
            
            material = ele # Each spring will have a unique material.
            
            # Create material.
            if material in mat_dict.keys():
                tag = mat_dict[material]
            else:
                tag = make_material(eleInfo, dfProp, K=K, Fy=Fy, alpha=alpha)
            
            # Create element.
            ops.element('zeroLength', eleTag, iNode, jNode, '-mat', tag, '-dir', 3)
            pass
        
        elif eleType == 'placeholder':
            pass
        
        else:
            print(eleType)
            raise ValueError('Element type "' + eleType + '" not included.')
    
            
def define_transformations(db):
    '''
    Loops through list of transformations and defines them in OpenSees.
    Relationship between tag and name is managed by database object.
    '''
    df = db.transf
    for i in df.index:
        trType = df.at[i, 'Type']
        tag = int(df.at[i, 'Tag'])
        xzVec = list(df.loc[i, ['Xvec', 'Yvec', 'Zvec']])
        ops.geomTransf(trType, tag, *xzVec)

def make_diaphragm_constraints(db):
    '''
    Loops through list of node names. Adds nodes to diaphragm one at a time.
    '''
    df = db.diaphragm
    for cNode in df.index:
        mNode = df.at[cNode, 'RetainedNode']
        mTag = db.get_node_tag(mNode)
        cTag = db.get_node_tag(cNode)
        ops.rigidDiaphragm(3, mTag, cTag)
    
def make_material(material, dfProp, **kwargs):
    global mat_dict; print(mat_dict)
    try:
        next_tag = max(mat_dict.values()) + 1
    except:
        next_tag = 1
    
    if material[:2] == 'PT':
        
        E = dfProp.at[material, 'E']
        fy = dfProp.at[material, 'fy']
        alpha = dfProp.at[material, 'alpha']
        e0 = dfProp.at[material, 'init_strain']
        eu = dfProp.at[material, 'fail_strain']
        
        mat_dict[material + '_EPPGap'] = next_tag
        mat_dict[material + '_Init'] = next_tag + 1
        mat_dict[material] = next_tag + 2
        
        ops.uniaxialMaterial('ElasticPPGap', next_tag, E, fy, 0.0, alpha)
        ops.uniaxialMaterial('InitStrainMaterial', next_tag+1, next_tag, e0)
        # ops.uniaxialMaterial('InitStressMaterial', next_tag+1, next_tag, e0*E)
        ops.uniaxialMaterial('MinMax', next_tag+2, next_tag+1, '-max', eu)
        
        return next_tag + 2
    
    elif material[:3] == 'UFP':
        
        b = dfProp.at[material, 'b']
        t = dfProp.at[material, 't']
        D = dfProp.at[material, 'D']
        E = dfProp.at[material, 'E']
        fy = dfProp.at[material, 'fy']
        alpha = dfProp.at[material, 'alpha']
        
        mat_dict[material] = next_tag
        
        Fy = fy*b*t**2/3/D
        k0 = 16/27/pi*E*b*(t/D)**3
        print(Fy, type(Fy), k0, type(k0))
        ops.uniaxialMaterial('Steel02', next_tag, Fy, k0, alpha)
        
        return next_tag
    
    elif material[:2] == 'ms':
        print('Pre:', mat_dict)
        K = kwargs['K']
        Fy = kwargs['Fy']
        alpha = kwargs['alpha']
        
        mat_dict[material] = next_tag
        
        print(K, type(K), Fy, type(Fy), alpha, type(alpha))
        ops.matTag = ops.uniaxialMaterial('ElasticPPGap', next_tag, K, Fy, 0.0, alpha, 'damage')
        
        return next_tag
    
    else:
        raise ValueError('Material "' + material + '"constructor not in code.\n' +
                         'Valid matierials must start with PT or UFP.')
        return 'ERROR'
    
    print(next_tag, mat_dict)

def rayleigh_damping(zeta, modes, highmode=False, printme=True):
    '''
    Add rayleigh damping to OpenSees model.

    Parameters
    ----------
    zeta : float or tuple of floats
        Damping factor, decimal. Two factors if different.
    modes : tuple of integers
        Apply rayleigh damping factor at these two modes.
    highmode : integer
        Override for eigen(highmode). Use the higher of modes by default.
    printme : TYPE, optional
        Option to print table to console.

    Returns
    -------
    None.

    '''
    if highmode:
        w2 = ops.eigen(highmode)
    else:
        w2 = ops.eigen(modes[1])
    
    w = np.sqrt(w2)
    f = w/2/np.pi
    T = 1/f
    if type(zeta) is float:
        zeta = (zeta, zeta)
    elif type(zeta) is tuple:
        pass
    else:
        raise TypeError('Zeta must be float or tuple.')
    
    # Calculate rayleigh damping factors
    A = np.asarray([[1/w[modes[0]-1], w[modes[0]-1]], [1/w[modes[1]-1], w[modes[1]-1]]])
    B = 2 * np.asarray([zeta[0], zeta[1]])
    a = solve(A, B)
    
    # Apply damping to model
    ops.rayleigh(a[0], 0, 0, a[1])
    
    # Print to console
    print('\n')
    print('{:^60}'.format('Modal Information'))
    print('{:-^60}'.format(''))
    print('{:>5}{:>13}{:>12}{:>10}{:>10}{:>10}'.format('Mode', 'w2', 'w', 'f', 'T', 'Damp.'))
    print('{:>5}{:>13}{:>12}{:>10}{:>10}{:>10}'.format('', '[rad²/sec²]', '[rad/sec]', '[Hz]', '[sec]', 'Ratio'))
    print('{:-^60}'.format(''))
    for i in range(len(w2)):
        h = a[0]/2/w[i] + a[1]*w[i]/2
        print('{:5d}{:13.4g}{:12.2f}{:10.2f}{:10.2g}{:10.2%}'.format(i+1, w2[i], w[i], f[i], T[i], h))
    print('\n')
