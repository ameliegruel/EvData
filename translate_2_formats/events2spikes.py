#!/bin/python3

"""
Function to transform events stored as a list of [x,y,t,p] to a SpikeSourceArray (PyNN)

Arguments:
- events (numpy array): events to be reduced
- coord_t (int): index of the timestamp coordinate 
Returns:
- spikes (2D list): events traduced as to be understood by Pynn as a SpikeSourceArray
- width (int): width of the sensor
- height (int): height of the sensor 

Author : Amélie Gruel - Université Côte d'Azur, CNRS/i3S, France - amelie.gruel@i3s.unice.fr
Date: 09/2021
"""

import numpy as np
from tqdm import tqdm
# import matplotlib.pyplot as plt

def ev2spikes(events,coord_t):
    if not 1<coord_t<4:
        raise ValueError("coord_t must equals 2 or 3")
    
    coord_t-=2
    width,height=int(np.max(events[::,0]))+1,int(np.max(events[::,1]))+1

    spikes=[[] for _ in range(width*height)]
    for x,y,*r in events:
        spikes[int(x)*height+int(y)].append(float(r[coord_t]))
    return spikes, width, height

# if __name__=="__main__":
#     a=np.load("Results/events_HR.npy")
#     r=ev2spikes2(a,2)
#     print(len(r))
#     print(sum(map(len,r)))
#     print(a.shape)
#     # # print(*map(lambda x:1 if x>0,r)) ## heatmap en fonction du nb d'events par pixel