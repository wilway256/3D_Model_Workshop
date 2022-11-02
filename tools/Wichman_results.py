# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 11:11:24 2022

@author: wfros
"""

from scipy.io import loadmat
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import seaborn as sns


        
class Data:
    
    sepCLT = 216
    sepMPP = 384
    
    intensities = ['43-year', '225-year', '475-year', '975-year', 'N/A', 'N/A', 'MCER']
    walls = ['CLT North', 'MPP West', 'MPP East', 'CLT South']
    
    info = {'43-year': {'SKW': [11, 2, 6, 5, 3],
                            'Name': ['Ferndale', 'Chi-Chi', 'Tohoku aftershock', 'Northridge', 'San Simeon'],
                            'dt': [0.005, 0.004, 0.01, 0.01, 0.005]},
            '225-year': {'SKW': [10, 11, 6, 3, 7],
                         'Name': ['Ferndale', 'Ferndale', 'Tohoku', 'Niigata', 'Tokachi'],
                         'dt': [0.005, 0.005, 0.01, 0.01, 0.01]},
            '475-year': {'SKW': [3, 2, 11, 4, 7],
                         'Name': ['Chi-Chi', 'Chi-Chi', 'Ferndale', 'Niigata', 'Tokachi'],
                         'dt': [0.005, 0.005, 0.005, 0.01, 0.01]},
            '975-year': {'SKW': [2, 4, 5, 6],
                         'Name': ['Victoria', 'Northridge', 'Tohoku', 'Tokachi'],
                         'dt': [0.01, 0.01, 0.01, 0.01]},
            'MCER': {'SKW': [7, 3, 5, 11, 8],
                     'Name': ['Tohoku', 'Niigata', 'Loma Prieta', 'Ferndale', 'Tokachi'],
                     'dt': [0.01, 0.005, 0.005, 0.005, 0.01]},}
    
    
    data = loadmat(r'D:\Users\wfros\Documents\Will\College\Box Sync\William Roser PhD Research\Writing\SPONSE\wallDisp_Reno.mat') # returns dict with metadata
    data = data['data'][0] # separates data from metadata
    
    
    def __init__(self, filename, **kwargs):
        
        self.choose_EQ(**kwargs)
        
    def choose_EQ(self, intensity='', SKW=-1):
        
        if intensity == '':
            for i, key in enumerate(self.intensities):
                print(str(i) + ' - ' + key)
            self.iintensity = int(input('Please select an intensity level: '))
            self.intensity = self.intensities[self.iintensity]
        else:
            self.intensity = intensity
            self.iintensity = self.intensities.index(self.intensity)
        
        if SKW < 0:
            for i in range(len(self.info[self.intensity]['SKW'])):
                print(str(i) + ' - ' + str(self.info[self.intensity]['SKW'][i]) + ' ' + self.info[self.intensity]['Name'][i])
            iInfo = int(input('Please select an earthquake: '))
            self.SKW = self.info[self.intensity]['SKW'][iInfo]
        else:
            self.SKW = SKW
            iInfo = self.info[self.intensity]['SKW'].index(self.SKW)
            
        self.name = self.info[self.intensity]['Name'][iInfo]
        self.dt = self.info[self.intensity]['dt'][iInfo]
        
        self.N = len(self.data[self.iintensity]['wall_disp_x'][self.SKW-1][0][0][0])
        self.time = np.linspace(0, self.N*self.dt, self.N)

        
    def get_xy(self, wall='', floor=-1):
        
        if wall == '':
            for i, wallname in enumerate(self.walls):
                print(str(i) + ' - ' + wallname)
            iwall = int(input('Please select a wall: '))
            self.wall = self.walls[iwall]
        else:
            iwall = self.walls.index(wall)
            self.wall = wall
        
        if floor < 1:
            floor = int(input('\nPlease select a floor [1 to 11]: '))
        
        self.floor = str(floor)
        x_data = self.data[self.iintensity]['wall_disp_x'][self.SKW-1][0][iwall][floor-1]
        y_data = self.data[self.iintensity]['wall_disp_y'][self.SKW-1][0][iwall][floor-1]
        
        return (x_data, y_data)
    
    def avg_xyr(self, floor, plot=False):
        
        sepCLT = 216
        sepMPP = 384
        
        xN, yN = self.get_xy('CLT North', floor)
        xS, yS = self.get_xy('CLT South', floor)
        xNS = (xN + xS)/2
        yNS = (yN + yS)/2
        rotCLT = np.arctan2(xS-xN, sepCLT + yN - yS)
        
        xW, yW = self.get_xy('MPP West', floor)
        xE, yE = self.get_xy('MPP East', floor)
        xEW = (xE + xW)/2
        yEW = (yE + yW)/2
        rotMPP = np.arctan2(yE-yW, sepMPP + xE - xW)
        
        xavg = (xNS + xEW)/2
        yavg = (yNS + yEW)/2
        rotAvg = (rotCLT + rotMPP)/2 # Sanity check: These two values should be the same if diaphragm is rigid.
        
        if plot:
            fig, ax = plt.subplots(3, 1)
            ax[0].plot(self.time, xavg)
            ax[1].plot(self.time, yavg)
            ax[2].plot(self.time, rotAvg)
            ax[0].set_title('{} {} Floor {:d}'.format(self.intensity, self.name, floor))
            
        return xavg, yavg, rotAvg
    
    def xy_point(self, coord, x, y, r):
        
        dx = x + coord[0]*np.cos(r) - coord[1]*np.sin(r)
        dy = y + coord[0]*np.sin(r) + coord[1]*np.cos(r)
        
        return dx, dy
    
    # def max_drift(self, coord)

# %% Process Data
if __name__ == '__main__':
    pass
    
    import pandas as pd
    # from matplotlib.lines import Line2D
    
    sns.axes_style('whitegrid')
    mpl.rcParams.update({"axes.grid" : False, "grid.color": 'gray'})
    
    cols = ['Intensity',
            'SKW',
            'Name',
            'Subassembly',
            'Floor',
            'xmax_x',
            'xmax_y',
            'xmax_abs',
            'ymax_x',
            'ymax_y',
            'ymax_abs',
            'absmax_x',
            'absmax_y',
            'absmax_abs']
    out = pd.DataFrame(columns=cols)
    
    SKWs = {'43-year': [11, 2, 6, 5, 3],
            '225-year': [10, 11, 6, 3, 7],
            '475-year': [3, 2, 11, 4, 7],
            '975-year': [2, 4, 5, 6],
            'MCER': [7, 3, 5, 11, 8]}
    
    intensity = ['43-year', '225-year', '475-year', '975-year', 'MCER'][4]
    wall = ['CLT North', 'MPP West', 'MPP East', 'CLT South'][0]
    SKW = 3
    floor = 1
    
    data = Data('wallDisp_Reno.mat', intensity=intensity, SKW=SKW)
    x, y = data.get_xy(wall, floor)
    fig, ax = plt.subplots()
    
    ax.plot(data.time, x, '-', data.time, y, '-')
    ax.set_title(data.name + data.intensity + data.wall + data.floor)
    ax.grid()
    #         for isub in range(len(wallcoord)):
                
    #             if subs[isub] == 'Sub. 4 (Curtain Wall)': #separates CFS 2 data
    #                 ufloors = [2,3]
    #                 lfloors = [1,2]
    #             else:
    #                 ufloors = [2,3,4]
    #                 lfloors = [1,2,3]
                
    #             for upper, lower in zip(ufloors, lfloors):
                    
    #                 # Plot every time history. WARNING!
    #                 # data.avg_xyr(upper, plot=True)
                    
    #                 # Get movement of two floors
    #                 x4, y4, r4 = data.avg_xyr(upper)
    #                 x3, y3, r3 = data.avg_xyr(lower)
                    
    #                 # Factor in effect of rotation for x and y at building corner
    #                 dx4, dy4 = data.xy_point(wallcoord[isub], x4, y4, r4)
    #                 dx3, dy3 = data.xy_point(wallcoord[isub], x3, y3, r3)
                    
    #                 # Difference between floors
    #                 xdrift = abs(dx4 - dx3)/heights[lower-1]*100
    #                 ydrift = abs(dy4 - dy3)/heights[lower-1]*100
    #                 absdrift = np.sqrt(xdrift**2 + ydrift**2)
                    
    #                 # Find extreme values
    #                 ixmax = abs(xdrift).argmax()
    #                 iymax = abs(ydrift).argmax()
    #                 iabsmax = abs(absdrift).argmax()
                    
    #                 xmax = [xdrift[ixmax][0], ydrift[ixmax][0], absdrift[ixmax][0]]
    #                 ymax = [xdrift[iymax][0], ydrift[iymax][0], absdrift[iymax][0]]
    #                 absmax = [xdrift[iabsmax][0], ydrift[iabsmax][0], absdrift[iabsmax][0]]
                    
    #                 out.loc[len(out.index)] = [intensity, SKW, 
    #                                           data.name, 
    #                                           subs[isub], lower, 
    #                                           *xmax, *ymax, *absmax]
    
    # out['Subassembly'] = out['Subassembly'].astype('category')
    # out['Intensity'] = out['Intensity'].astype('category')
    
    
    # # %% Display Data
    
    # marker = ['x', 'o', '+', '1']
    # sub = ['Sub. 1 (Platform)', 'Sub. 2 (Bypass)', 'Sub. 3 (Spandrel)', 'Sub. 4 (Curtain Wall)']
    # colors = ['blue','green','red','black']
    # axes = ['x', 'y']
    # direction = ['East-West', 'North-South']
    # lw = [1.0, 0.0, 1.0, 1.0]
    # drift_limit = {'x':{'Sub. 1 (Platform)':[2.54, 2.40, 0.59],
    #                     'Sub. 2 (Bypass)':[2.3, 2.3, 2.3],
    #                     'Sub. 3 (Spandrel)':[0.78, 2.40, 1.14],
    #                     'Sub. 4 (Curtain Wall)':[2.50, 3.05, -1]},
    #                'y':{'Sub. 1 (Platform)':[2.50, 3.00, 0.59],
    #                     'Sub. 2 (Bypass)':[2.3, 2.3, 2.3],
    #                     'Sub. 3 (Spandrel)':[0.78, 3, 1.14],
    #                     'Sub. 4 (Curtain Wall)':[2.50, 3.42, -1]}}
    # # 
    # # plt.grid(visible=False)
    
    # for axis in range(len(axes)):
    #     for floor in [1, 2, 3]:
    #         plt.figure()
    #         for i in range(len(sub)):
    #             tempdata = out[out['Floor']==floor]
    #             tempdata = tempdata[tempdata['Subassembly']==sub[i]]
                
    #             y = axes[axis] + 'max_' + axes[axis]
                
    #             plot = sns.stripplot(x='Intensity', y=y, data=tempdata, 
    #                           hue='Subassembly', marker=marker[i], 
    #                           dodge=True, linewidth=lw[i], palette=sns.xkcd_palette(colors),
    #                           order=intensities, jitter=False)
    #             plot.set_position([0.1, 0.1, 0.85, 0.82])
                
    #             plt.axis('tight')
    #             plt.xlabel(None)
    #             plt.ylabel('Interstory Drift (%)')
    #             plt.ylim([0, 2.5])
    #             # print(axes[axis],floor,i)
                
    #             # Drift Limits
    #             y_limit = drift_limit[axes[axis]][sub[i]][floor-1]
    #             if y_limit < 2.5:
    #                 if y_limit > 0.75:
    #                     x_limit = -0.4
    #                     if floor == 2 and i == 2:
    #                         x_limit = 0.1
    #                 else:
    #                     x_limit = 3.8
                    
    #                 plt.axhline(y=y_limit,
    #                             color=colors[i], linestyle='--', linewidth=0.5)
                    
                    
                    
    #                 plt.text(x_limit, y_limit-0.01, sub[i].split(' (')[0], color=colors[i],
    #                          fontsize='small', va='top')
                
    #             # Change MCER to MCE_R
    #             labels = [item.get_text() for item in plot.get_xticklabels()]
    #             labels[4] = '$MCE_{R}$'
    #             plot.set_xticklabels(labels)
            
    #         # Plot title (removed for space in Word document)
    #         title = '{} Drift - Story {:d}'.format(direction[axis], floor)
    #         plt.title(title)
            
    #         # Fix markers (stripplot shows only colors by default)
    #         markers = {'Sub. 1 (Platform)':'x', 'Sub. 2 (Bypass)':'o', 'Sub. 3 (Spandrel)':'+', 'Sub. 4 (Curtain Wall)':'1'}
    #         handles, labels = plot.get_legend_handles_labels()
    #         handles = [Line2D([], [], color=c, linestyle='', 
    #                           marker=markers[l]) for h, l, c in zip(handles, labels, colors)]
            
            
    #         if floor == 3:
    #             if axis == 1: # Legend appears in wrong spot on this one. Manual correction.
    #                 plot.legend(handles[:3], labels[:3], loc=(0.015, 0.65))
    #             else:
    #                 plot.legend(handles[:3], labels[:3])
    #         else:
    #             plot.legend(handles[:4], labels[:4])
    #         plt.savefig(title + '.png')
    
    
    
    
    
    
    
   