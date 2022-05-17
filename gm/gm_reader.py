# -*- coding: utf-8 -*-
"""
Created:  Tue May 17 13:39:58 2022
Author:   wroser
=============================================================================
Description:
Reads ground motion input files

"""

# %% Imports
import numpy as np
import matplotlib.pyplot as plt

# %% Code
def is_PEER(file):
    firstline = file.readline()
    if 'PEER NGA' in firstline:
        return True
    else:
        return False

def PEER_to_txt(filePath):
    '''
    Converts PEER database GM file to txt file in place.
    New file will have same name and path as original.

    Parameters
    ----------
    filePath : string
        Full path to PEER AT2 file.

    Returns
    -------
    None.
    '''
    fileList = filePath.split('/')
    outfile = fileList[-1].split('.')[0] + '.txt'
    if len(fileList) == 1:
        outpath = ''
    else:
        outpath = '/'.join(fileList[0:-1]) + '/'
    
    with open(filePath, 'r') as peer:
        # Skip first three lines
        for i in [1, 2, 3]:
            peer.readline()
        
        # Get N and dt
        filedata = peer.readline().split()
        dt = float(filedata[3])
        N = int(filedata[1][:-1])
        print('dt = {:>10f}\nN  = {:>10d}'.format(dt, N))
        
        # Iterate through data points
        with open(outpath + outfile, 'w')as txt:
            while filedata != '':
                filedata = peer.readline()
                for data_point in filedata.split():
                    txt.write(data_point + '\n')
    # with open(outpath + outfile, 'w')as txt:
    #     pass
    print('End of file')
    
    

def PEER_to_list(filePath):
    '''
    Converts PEER file to OpenSees list.

    Parameters
    ----------
    filePath : string
        Full path to PEER AT2 file.

    Returns
    -------
    data : list of floats
        timeSeries('Path', tag, '-dt', dt, '-values', data, '-factor', g).
    dt : float
        timeSeries('Path', tag, '-dt', dt, '-values', data, '-factor', g).

    '''
    with open(filePath, 'r') as peer:
        # Skip first three lines
        for i in [1, 2, 3]:
            peer.readline()
        
        # Get dt
        filedata = peer.readline().split()
        dt = float(filedata[3])
        
        # Iterate through data points
        data = []
        while filedata != '':
            filedata = peer.readline()
            for data_point in filedata.split():
                data.append(data_point + '\n')
    return data, dt

def plot_gm(file, dt=None):
    '''
    Plots ground motion data.

    Parameters
    ----------
    file : file
        Must be list of values or PEER file.
    dt : float, optional
        Specify dt for a list of values. If not specified (default), the file 
        will be read as a PEER file.

    Returns
    -------
    None.

    '''
    if dt ==None:
        print("William hasn't added this feature yet.")
        pass
    else:
        data = [float(line) for line in file.readlines()]
        N = len(data)
        last = N*dt - dt
        t = np.linspace(0.0, last, N)
        
        plt.figure()
        plt.style.use('bmh')
        plt.plot(t, data, linewidth=1)
        plt.xlim((0, last))

if __name__ == '__main__':
    # files = ['input.txt', 'RSN825_CAPEMEND_CPM000.txt', 'RSN825_CAPEMEND_CPM090.txt']
    # for i in files:
    #     with open(i) as file:
    #         plot_gm(file, 0.05)
    
    # PEER_to_txt('RSN942_NORTHR_ALH090.AT2')
    
    l, a, b = PEER_to_list('RSN942_NORTHR_ALH090.AT2')
    