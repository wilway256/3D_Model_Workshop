# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 10:13:37 2022

@author: wfros
"""

# %% Imports
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# %% Code
def newmark_beta(dt, accels, Tn, zeta=0.05, beta=1/4, gamma=0.5, g=386.4):
    m = 1.0
    k = 4*np.pi**2/Tn**2
    c = 2*zeta*np.sqrt(k*m)
    accels = accels*g
    
    t = np.linspace(0, dt*len(accels), len(accels))
    u = np.zeros((len(accels)), float)
    v = np.zeros((len(accels)), float)
    a = np.zeros((len(accels)), float)
    
    a[0] = accels[0]
    k_hat = k + gamma/beta/dt*c + m/beta/dt**2
    A = m/beta/dt+gamma*c/beta
    B = m/2/beta+c*dt*(gamma/2/beta-1)
    
    umax = 0
    amax = 0
    # print('1')
    for i in range(len(accels)-1):
        dp = m*(accels[i+1]-accels[i])
        dp_hat = dp + A*v[i] + B*a[i]
        du = dp_hat / k_hat
        dv = gamma*du/beta/dt-gamma*v[i]/beta+dt*a[i]*(1-gamma/2/beta)
        da = du/beta/dt**2 - v[i]/beta/dt - a[i]/2/beta
        
        u[i+1] = u[i] + du
        v[i+1] = v[i] + dv
        a[i+1] = a[i] + da
        
        umax = max(umax, u[i+1])
        amax = max(amax, a[i+1]+accels[i+1])
    
    # The following code snippet is for viewing the difference between absolute
    # acceleration, ground acceleration, and acceleration relative to the ground.
    # Very short period ground motions should have little acceleration relative
    # to the ground.
    plt.figure()
    plt.grid()
    plt.plot(t, a+accels)
    plt.plot(t, accels)
    plt.plot(t, a)
    plt.figure()
    plt.plot(t, u)
    # plt.xlim([20, 25])
    
    return umax, amax

if __name__ == "__main__":
    # import Model_10_Story
    # folder = Model_10_Story.__path__[0] + '//gm//'
    
    filename = '23 TallWoodEqs_MCE_4228_x.txt'
    # with open(folder + filename) as file:
    #     accels = file.readlines()
    #     for i, line in zip( range(len(accels)), accels):
    #         accels[i] = float(line)
    # accels = np.array(accels)
    
    # # Constant acceleration for testing.
    # accels = [1]*2000
    # accels = np.append(np.linspace(0,1,500), np.array(accels))*386.4
    
    # Constant acceleration for testing.
    accels = np.sin(np.linspace(0.0, 25, 5000)*np.pi*2/1.3)
    # accels = np.append(np.array(accels), np.zeros((1000)))*386.4
    
    # Periods. Select linear or log spaced values
    start = 0.01
    stop = 20.0
    N = 10
    base = 5 # no effect
    
    #Tns = np.linspace(start, stop, N)
    
    Tns = np.logspace(np.log(start)/np.log(base), np.log(stop)/np.log(base), N, base=base)
    
    
    u = np.zeros(Tns.shape)
    a = np.zeros(Tns.shape)
    
    for i, Tn in enumerate(Tns):
        u[i], a[i] = newmark_beta(0.005, accels, Tn)
    
    mpl.rcParams.update({"axes.grid" : True, "grid.color": "black"})
    fig, ax = plt.subplots(2, 1)
    ax[0].plot(Tns, u)
    ax[1].plot(Tns, a)
    
    ax[0].set_ylabel('S_d')
    ax[1].set_ylabel('S_a')
    ax[1].set_xlabel('Tn (sec.)')
    
    fig.suptitle(filename)