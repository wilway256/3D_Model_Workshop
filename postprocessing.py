# -*- coding: utf-8 -*-
"""
Active postprocessing script.
This file is for the user to run batches of postprocessing functions. No other
file should call this one. This will be used for generating quick output
after calling main.py.

Created on Mon Nov 15 11:24:08 2021
@author: wroser
"""

# import openseespy.opensees as ops
# import opsvis
# import src.postprocessing_active as pp1
# import src.postprocessing_saved as pp2

# %% Postprocessing
# nodes = ops.getNodeTags()
# pp1.print_node_disps_and_rxns(db, nodes, get_tag=False)

# eles = db.get_ele_list()
# for e in eles:
#     response = ops.eleResponse(db.get_ele_tag(e), 'force')
#     print(f'{e:>10}', response)

# # %% Visualization
# 
# opsvis.plot_model(node_labels=0, element_labels=0, offset_nd_label=False, axis_off=1,
#                   az_el=(- 80.0, 30.0), fig_wi_he=(20.0, 20.0), fig_lbrt=(0.04, 0.04, 0.96, 0.96),
#                   lw=0.1, local_axes=False, nodes_only=False, fmt_model='ko-')
# opsvis.plot_defo(interpFlag=0)
# opsvis.plot_defo( az_el=(-60.0, 30.0) )

# opsvis.plot_mode_shape(1, interpFlag=0)

# %% XML Parser
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd


outdir = 'out/triangle/'
file = 'node_t.xml'
filepath = outdir + file
tree = ET.parse(filepath)
root = tree.getroot()

column_names = []

for element in root.iter():
    # print(element.tag)
    if element.tag == 'TimeOutput':
        column_names.append(element[0].text)
        print('    ', element[0].text)
    elif element.tag == 'NodeOutput':
        nodeTag = element.attrib['nodeTag']
        for response in range(len(element)):
            column_names.append('Node_' + nodeTag + ' ' + element[response].text)
            print('    ', 'Node', nodeTag, element[response].text)


data = root.find('Data').text
data = data.strip().split('\n')
for i in range(len(data)):
    data[i] = data[i].split()
    for j in range(len(data[i])):
        data[i][j] = float(data[i][j])
data = np.asarray(data)

df = pd.DataFrame(data, columns=column_names)

