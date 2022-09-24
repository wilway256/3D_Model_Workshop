# -*- coding: utf-8 -*-
"""
Created:  Tue Sept 20 2022
Author:   wroser
=============================================================================
Description:
    Derived from rigid_wall.py.
    For checking reasonableness of rocking wall moment-rotation response
"""

# %% Imports
from math import sqrt
import matplotlib.pyplot as plt
import numpy as np


# %% Wall Parameters
# MPP
B = 105.125 # in, wall width
t = 9.1875 # in, wall thickness
W = 57.13 # kip, wall weight
E = 2004 # ksi

d = [45.4375, 45.4375, 59.6875, 59.6875] # in, distances from edge to PT
T_PT = 50 # kip, initial
K_PT = 44.3*2 # kip/in, PT stiffness

# CLT
# B = 117.125 # in, wall width
# t = 12.375 # in, wall thickness
# W = 87.8 # kip, wall weight
# E = 1134.8 # ksi

# d = [51.4375, 51.4375, 65.6875, 65.6875] # in, distances from edge to PT
# T_PT = 12.76*2 # kip, initial
# K_PT = 44.3*2 # kip/in, PT stiffness


# Both walls
H = 1374 # in, wall height
g = 32.2*12 # in/sec/sec, acceleration due to gravity


# Derived units
R = sqrt(B**2 + H**2)/2 # in, length of position vector from center of mass to point of rocking
I0 = W/g*(B**2+H**2)/12 # mass moment of inertia for wall
alpha = np.arctan(B/H) # rad, maximum rotation before overturning


# %% Function Definitions

def rigid_block(theta, W, R, alpha):
    '''
    Gives moment (M) as a function of base rotation (theta).
    '''
    if theta <= -alpha or theta >= alpha:
        M = 0
    else:
        M = W*R*np.sin(alpha-abs(theta))
        if theta < 0:
            M = -M
    return M

def rigid_block_PT(theta, W, R, alpha, d, T_PT, K_PT):
    '''
    Gives moment (M) as a function of base rotation (theta).
    '''
    PT_force = 0
    for i in range(len(d)):
        PT_force += abs(theta) * d[i]**2 * K_PT
    M = W*R*np.sin(alpha-abs(theta)) \
        + T_PT*R*np.sin(alpha) \
        + PT_force
    if theta < 0:
        M = -M
    return M

# %% Code
if __name__ == '__main__':
    
    theta = np.linspace(-0.04, 0.04, 200)
    M1 = np.zeros((len(theta)))
    M2 = np.zeros((len(theta)))
    
    for i in range(len(theta)):
        M1[i] = rigid_block(theta[i], W, R, alpha)
        M2[i] = rigid_block_PT(theta[i], W, R, alpha, d, T_PT, K_PT)
    
    print(W*R*np.sin(alpha))
    
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    # ax.plot(theta, M1, '-', theta, M2, '-')
    ax.plot(theta, M2, '-')
    ax.set_xlabel('Base Rotation (rad.)')
    ax.set_ylabel('Base Moment (kip-in)')
    ax.grid()
    
    # Stiffness check
    K = 4*E*I0/H
    init_stiff_rot = np.array([-0.04, 0.04])
    init_stiff_mom = init_stiff_rot*K
    ax.plot(init_stiff_rot, init_stiff_mom, ':')
    