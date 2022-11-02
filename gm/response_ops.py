# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 17:37:07 2022

@author: wfros
"""

# %% Imports
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import openseespy.opensees as ops

# %% Code
def max_response(dt, accels, Tn, zeta=0.05, beta=1/4, gamma=0.5, g=386.4):
    m = 1.0
    k = 4*np.pi**2/Tn**2
    c = 2*zeta*np.sqrt(k*m)
    
    ops.wipe()
    ops.model('basic', '-ndm', 1, '-ndf', 1)
    
    ops.node(1, 0)
    ops.fix(1, 1)
    ops.uniaxialMaterial('Elastic', 1, k, c)
    
    ops.node(2, 0)
    ops.mass(2, m)
    ops.element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 1)
    
    # Ground motion
    ops.timeSeries('Path', 1, '-dt', dt, '-values', *accels, '-factor', g, '-prependZero')
    ops.pattern('UniformExcitation', 1, 1, '-accel', 1)
    
    # Analysis Options
    ops.system("BandSPD")
    ops.numberer("Plain")
    ops.constraints("Transformation")
    ops.test('NormDispIncr', 1e-10, 100)
    ops.algorithm("Newton")
    ops.integrator('Newmark', 0.5, 0.25)
    ops.analysis("Transient")
    
    N = len(accels)
    t = np.arange(0, dt*N, dt)
    # nodeDisp = np.zeros(t.shape)
    # nodeAccel = np.zeros(t.shape)
    
    umax = 0.0
    amax = 0.0
    
    for i in range(N):
        ops.analyze(1, dt)
        # print('Floor', floor, ops.nodeDisp(i+1))
        # nodeDisp[i] = ops.nodeDisp(2)[0]
        # nodeAccel[i] = ops.nodeAccel(2)[0]
        umax = max(umax, abs(ops.nodeDisp(2)[0]))
        amax = max(amax, abs(ops.nodeAccel(2)[0]+accels[i]*g))
    
    # # The following code snippet is for viewing the difference between absolute
    # # acceleration, ground acceleration, and acceleration relative to the ground.
    # # Very short period ground motions should have little acceleration relative
    # # to the ground.
    # fig, ax = plt.subplots(2, 1)
    # plt.grid(visible=True)
    # ax[0].plot(t, nodeDisp)
    # ax[1].plot(t, nodeAccel)
    # ax[1].plot(t[0:len(accels)], accels*g)
    # ax[1].plot(t[0:len(accels)], accels*g+nodeAccel)
    
    return umax, amax

if __name__ == "__main__":
    import Model_10_Story
    folder = Model_10_Story.__path__[0] + '//gm//'
    
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
    
    for eq in data:
        for xyz in 'xyz'[0:eq[2]]:
            dt = eq[1]
            
            filename = eq[0] + '_' + xyz + '.txt'
            with open(folder + filename) as file:
                accels = file.readlines()
                for i, line in zip( range(len(accels)), accels):
                    accels[i] = float(line)
            accels = np.array(accels)
            
            # # Constant acceleration for testing.
            # accels = [1]*2000
            # accels = np.append(np.linspace(0,1,500), np.array(accels))*386.4
            
            # # Harmonic acceleration for testing.
            # accels = np.sin(np.linspace(0.0, 50, 10000)*np.pi*2/1.0)
            # # accels = np.append(np.array(accels), np.zeros((1000)))*386.4
            
            # Periods. Select linear or log spaced values
            start = 0.01
            stop = 3.0
            N = 250
            base = 5 # no effect
            
            #Tns = np.linspace(start, stop, N)
            
            Tns = np.logspace(np.log(start)/np.log(base), np.log(stop)/np.log(base), N, base=base)
            
            
            u = np.zeros(Tns.shape)
            a = np.zeros(Tns.shape)
            
            for i, Tn in enumerate(Tns):
                u[i], a[i] = max_response(dt, accels, Tn)
            
            # mpl.rcParams.update({"axes.grid" : True})
            
            fig, ax = plt.subplots(2, 1, figsize=(16, 9))
            plt.grid(visible=True, which='major')
            # plt.minorticks_on()
            ax[0].plot(Tns, u)
            ax[1].plot(Tns, a/32.2/12)
            
            ax[0].set_ylabel('$S_{d}$ (in.)')
            ax[1].set_ylabel('$S_{a}$ (g)')
            ax[1].set_xlabel('Tn (sec.)')
            
            ax[0].set_xlim([0, stop])
            ax[1].set_xlim([0, stop])
            ax[0].set_ylim([0, ax[0].get_ylim()[1]])
            ax[1].set_ylim([0, ax[1].get_ylim()[1]])
            
            ml = mpl.ticker.MultipleLocator(0.10)
        
            ax[0].xaxis.set_minor_locator(ml)
            
            ax[0].xaxis.grid(which="minor", color='#999999', linestyle=':', linewidth=0.7)
            ax[1].xaxis.set_minor_locator(ml)
            ax[1].xaxis.grid(which="minor", color='#999999', linestyle=':', linewidth=0.7)
            
            figname = eq[3] + ' ' + xyz.upper()
            fig.suptitle(figname)
            
            fig.savefig(filename[0:2] + 'S ' + figname + '.png')
            plt.close()