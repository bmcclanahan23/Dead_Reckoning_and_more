# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 18:14:14 2015

@author: Brian
"""
from matplotlib import pyplot as plt
from time import sleep

f = plt.figure(0)
plt.xlim([-1000,1000])
plt.ylim([-1000,1000])
f.show()
#positions = [[0],[0]]
#position = [0,0]
last_step = 0
cur_step = 0 

print
#Chris !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!111
#change this location to landmark dictionary 
#label_to_loc = {11:[0,0],12:[0,7],13:[0,12],14:[0,20],21:[-5,-2],22:[-5,7],23:[-5,13],24:[-5,20],31:[-10,-2],32:[-10,7],33:[-10,13],34:[-10,20]}
label_to_loc = {1:[0,0],2:[0,9],3:[0,20],4:[-10,20],5:[-7,10],6:[-10,-2]}
xs = []
ys = []

for key in label_to_loc: 
    xs.append(label_to_loc[key][0])
    ys.append(label_to_loc[key][1])
    
plt.plot(xs,ys,marker='o',ls='')
for pos in positions: 
#for head in headings: 
    '''
    item = item_all[u'all_data']
    if last_step != 0 and item[u'stepc'] > last_step: 
        steps_taken = item[u'stepc'] - last_step 
    elif  last_step == 0 and item[u'stepc'] > last_step:
        steps_taken = 1 
    else: 
        steps_taken = 0 
    
    mag = .8646*steps_taken 
    position = [position[0]+item[u'direction_0']*mag,position[1]+item[u'direction_1']*mag]
    positions[0].append(position[0])
    positions[1].append(position[1])    
    '''
    #ax = plt.axes()
    #ax.arrow(0, 0, head[0],head[1], head_width=0.05, head_length=0.1, fc='k', ec='k')
    plt.plot(pos[0],pos[1],marker='x')
    #plt.xlim([-12,2])
    #plt.ylim([-5,25])
    plt.xlim([-20,20])
    plt.ylim([-40,40])
    plt.draw()
    sleep(.01)