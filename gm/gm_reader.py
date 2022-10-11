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
import os

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
    if is_PEER(file):
        pass
    else:
        if dt ==None:
            dt = float(input("Please enter dt: "))
        
        try:
            data = [float(line) for line in file.readlines()]
            data = np.asarray(data)
            N = len(data)
        except:
            pass
        #     file.seek(0, 0)
        #     data = [line.split() for line in file.readlines()]
        #     data = np.asfarray(data).T
        #     N = data.shape[1]
        
        last = N*dt - dt
        t = np.linspace(0.0, last, N)
        
        plt.figure()
        plt.style.use('bmh')
        plt.plot(t, data, linewidth=1)
        plt.xlim((0, last))
        
def pick_and_plot(folder='.'):
    gm_files = os.listdir(folder)
    temp= []
    i = 1
    print('\nPlease choose a file:\n')
    for filename in gm_files:
        if filename.endswith('.txt'):# or filename.endswith('.AT2'):
            temp.append(filename)
            print('{:3d}   {}'.format(i, filename))
            i += 1
    gm_files = temp
    
    choice = int(input())-1
    print('You selected:', temp[choice])
    with open(folder + '/' + gm_files[choice]) as file:
        plot_gm(file)

def sixdof_to_txt(folder, convert_all=False):
    
    gm_files = os.listdir(folder)
    
    
    
    temp= []
    i = 1
    print('\nPlease choose a file:\n')
    for filename in gm_files:
        if filename.endswith('.txt'):# or filename.endswith('.AT2'):
            temp.append(filename)
            print('{:3d}   {}'.format(i, filename))
            i += 1
    gm_files = temp
    
    if not convert_all:
        choice = int(input())-1
        print('You selected:', temp[choice])
        gm_files = [gm_files[choice]]
    
    for gm_file in gm_files:
        filepath = folder + '/' + gm_file
        with open(filepath) as file:
            data = [line.split() for line in file.readlines()]
        data = np.asfarray(data)
        
        for i in range(3): # x, y, and z
            path = filepath[:-9]
            out = path + '_' + 'xyz'[i] + '.txt'
            np.savetxt(out, data[:, i])

def get_file_names():
    for file in os.listdir():
        if '.txt' in file:
            print('gm/' + file)
            
def plot_gm3(filename, dt, Ndof, name):
    '''
    Plots ground motion data.

    Parameters
    ----------
    file : txt file
        Must be list of values or PEER file.
    dt : float, optional
        Specify dt for a list of values. If not specified (default), the file 
        will be read as a PEER file.

    Returns
    -------
    None.

    '''
    import matplotlib
    matplotlib.use('Agg')
    
    fig, ax = plt.subplots(Ndof, 1, sharex=True, figsize=(16,9))
    plt.style.use('bmh')
    
    if Ndof == 1:
        ax = [ax]
    
    for i, suffix in enumerate('xyz'[0:Ndof]):
        filenamei = filename + '_' + suffix + '.txt'
        with open(filenamei) as file:
    
            data = [float(line) for line in file.readlines()]
            data = np.asarray(data)
            N = len(data)
            
            last = N*dt - dt
            t = np.linspace(0.0, last, N)
            
            
            ax[i].plot(t, data, linewidth=1)
            ax[i].set_xlim((0, last))
    ax[Ndof-1].set_xlabel('Time (sec.)')
    # fig.text(0.04, 0.5, 'Acceleration (g)', va='center', ha='center', rotation='vertical')
    if Ndof == 3:
        ax[1].set_ylabel('Acceleration (g)')
    else:
        ax[0].set_ylabel('Acceleration (g)')
    
    
    
    fig.suptitle(name.split('-year')[0])
    plt.tight_layout()
    
    
    fig.savefig(filename.split(' TallWoodEqs')[0] + filename.split(' TallWoodEqs')[1])
    # return ax2
    
if __name__ == '__main__':
    # Test plot_gm
    # files = ['input.txt', 'RSN825_CAPEMEND_CPM000.txt', 'RSN825_CAPEMEND_CPM090.txt', 'RSN942_NORTHR_ALH090.txt']
    # for i in files:
    #     with open(i) as file:
    #         plot_gm(file, 0.05)
    
    # PEER_to_txt('RSN942_NORTHR_ALH090.AT2')
    
    # l, a, b = PEER_to_list('RSN942_NORTHR_ALH090.AT2')
    
    # %% Test pick_and_plot (leave on by default)
    # pick_and_plot()
    
    # %% Split 6dof files
    # sixdof_to_txt('./Final_ Phase 1 Ground Motions sent to UCSD', convert_all=True)
    
    # %% Plot 3 DOF GM
    data = [['01 TallWoodEqs_43_subRSN2000890', 0.005, 3, 'Ferndale 43-year'],
            ['02 TallWoodEqs_43_3320', 0.004, 3, 'Chi-Chi 43-year'],
            ['03 TallWoodEqs_43_CHB0121103111526', 0.01, 3, 'Tohoku Aftershock 43-year'],
            ['04 TallWoodEqs_43_975', 0.01, 3, 'Northridge 43-year'],
            ['05 TallWoodEqs_43_4031', 0.005, 3, 'San Simeon 43-year'],
            ['06 TallWoodEqs_225_subRSN2000890', 0.005, 3, 'Ferndale 225-year'],
            ['07 TallWoodEqs_225_subRSN2000905', 0.005, 3, 'Ferndale 225-year'],
            ['08 TallWoodEqs_225_CHBH041103111446', 0.01, 3, 'Tohoku 225-year'],
            ['09 TallWoodEqs_225_4213', 0.01, 3, 'Niigata 225-year'],
            ['10 TallWoodEqs_225_HKD1310309260450', 0.01, 3, 'Tokachi 225-year'],
            ['11 TallWoodEqs_475_3471', 0.005, 3, 'Chi-Chi 475-year'],
            ['12 TallWoodEqs_475_2951', 0.005, 3, 'Chi-Chi 475-year'],
            ['13 TallWoodEqs_475_subRSN2000905', 0.005, 3, 'Ferndale 475-year'],
            ['14 TallWoodEqs_475_4213', 0.01, 3, 'Niigata 475-year'],
            ['15 TallWoodEqs_475_HKD1310309260450', 0.01, 3, 'Tokachi 475-year'],
            ['16 TallWoodEqs_975_268', 0.01, 3, 'Victoria 975-year'],
            ['19 TallWoodEqs_975_964', 0.01, 3, 'Northridge 975-year'],
            ['20 TallWoodEqs_975_CHBH041103111446', 0.01, 1, 'Tohoku 975-year'],
            ['21 TallWoodEqs_975_HKD1270309260450', 0.01, 1, 'Tokachi-year'],
            ['22 TallWoodEqs_MCE_CHBH041103111446', 0.01, 1, 'Tohoku MCE'],
            ['23 TallWoodEqs_MCE_4228', 0.005, 3, 'Niigata MCE'],
            ['24 TallWoodEqs_MCE_761', 0.005, 3, 'Loma Prieta MCE'],
            ['25 TallWoodEqs_MCE_subRSN2000890', 0.005, 3, 'Ferndale MCE'],
            ['26 TallWoodEqs_MCE_HKD1270309260450', 0.01, 1, 'Tokachi MCE'],
            ['27 TallWoodEqs_MCE_Northridge', 0.01, 3, 'Northridge MCE'],
            ['28 TallWoodEqs_MCE_SuperstitionHills', 0.01, 2, 'Superstition Hills MCE']]
    
    for item in data:
        ax = plot_gm3(*item)
    