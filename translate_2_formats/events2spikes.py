#!/bin/python3

"""
Function to transform events stored as a list of [x,y,t,p] to a SpikeSourceArray (PyNN)

Arguments:
- events (numpy array): events to be reduced
Returns:
- spikes (2D list): events traduced as to be understood by Pynn as a SpikeSourceArray
- width (int): width of the sensor
- height (int): height of the sensor 

Author : Amélie Gruel - Université Côte d'Azur, CNRS/i3S, France - amelie.gruel@i3s.unice.fr
Date: 09/2021
"""

import numpy as np
import sys
sys.path.append('/home/amelie/Scripts/EvData/read_event_data')
from loadData import getFormat

def ev2spikes(events, width=None, height=None):
    format_ev = getFormat(events)
    coord_t = format_ev.index('t')

    if not 1<coord_t<4:
        raise ValueError("coord_t must equals 2 or 3")
    
    coord_t-=2
    if width == None or height == None: 
        w,h=int(np.max(events[::,0]))+1,int(np.max(events[::,1]))+1
        if width == None:
            width = w
        if height == None:
            height = h

    spikes=[[] for _ in range(width*height)]
    for x,y,*r in events:
        spikes[int(x)*height+int(y)].append(float(r[coord_t]))
    return spikes, width, height