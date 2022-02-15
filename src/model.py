# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 11:16:06 2021

@author: wroser
"""

import openseespy.opensees as ops
from math import pi
# import src.transformations as tr

global_z = 3

mat_dict = {}

def make_model(modelType='3D'):
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
    df = db.node
    node_names = db.get_node_list()
    for node in node_names:
        tag = db.get_node_tag(node)
        x = df.at[node, 'X']
        y = df.at[node, 'Y']
        z = df.at[node, 'Z']
        ops.node(tag, x, y, z)
    
def fix_nodes(db):
    df = db.fixity
    for node in df.index:
        tag = db.get_node_tag(node)
        dof_fixity = list( df.loc[node] == 'Fixed')
        dof_fixity = [int(i) for i in dof_fixity]
        ops.fix(tag, *dof_fixity)

def assign_node_mass(db):
    df = db.nodeMass
    for node in df.index:
        tag = db.get_node_tag(node)
        node_dof_mass = list(df.loc[node])
        ops.mass(tag, *node_dof_mass)
        
def make_elements(db):
    dfEle = db.ele
    dfProp = db.eleData
    dfTransf = db.transf
    global mat_dict
    
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
            transfTag = int( dfTransf.at[transf, 'Tag'] )
            ops.element('elasticBeamColumn', eleTag, iNode, jNode, Area, E_mod, G_mod, Jxx, Iy, Iz, transfTag)
            
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
            ops.rigidLink('beam', iNode, jNode)
        
        elif eleType == 'UFP':
            # eleTag = db.get_ele_tag(ele)
            # iNode = int( dfEle.at[ele, 'iNode'] )
            # jNode = int( dfEle.at[ele, 'jNode'] )
            # eleType = dfEle.at[ele, 'PropertyID']
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
            ops.element('corotTruss', eleTag, iNode, jNode, A, tag)
        
        elif eleType == 'placeholder':
            pass
        
        elif eleType == 'placeholder':
            pass
        
        else:
            print(eleType)
            raise ValueError('Element type "' + eleType + '" not included.')
            
def define_transformations(db):
    df = db.transf
    for i in df.index:
        trType = df.at[i, 'Type']
        tag = int(df.at[i, 'Tag'])
        xzVec = list(df.loc[i, ['Xvec', 'Yvec', 'Zvec']])
        ops.geomTransf(trType, tag, *xzVec)

def make_diaphragm_constraints(db):
    df = db.diaphragm
    for cNode in df.index:
        mNode = df.at[cNode, 'MasterNode']
        mTag = db.get_node_tag(mNode)
        cTag = db.get_node_tag(cNode)
        ops.rigidDiaphragm(3, mTag, cTag)

# def material_tag(material, dfProp):
#     global mat_dict
#     if material in mat_dict.keys():
#         tag = mat_dict[material]
#     elif mat_dict == {}:
#         tag = 1
#         tag = make_material
#     else:
#         tag = max(mat_dict.values())
#         mat_dict[material] = tag
#         tag = make_material(material, dfProp)
#         return tag
    
def make_material(material, dfProp):
    global mat_dict
    try:
        next_tag = max(mat_dict.values())
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
        
        Fy = fy*b*t**2/2/D
        k0 = 16/27/pi*E*b*(t/D)**3
        
        ops.uniaxialMaterial('Steel02', next_tag, Fy, k0, alpha)
        
        return next_tag
    
    else:
        raise ValueError('''Material constructor not in code.\n
                         Valid matierials must start with PT or UFP.''')
        return 'ERROR'