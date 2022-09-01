# EvData
This repository regroups different scripts to produce new event data samples, and process existing ones, for different file extensions and using different Python libraries.
All scripts are written in Python3 or in Bash. 

## Read event data

### read_event_data/loadData.py
The function ```load_data``` takes as input the path to an event file and opens it. It handles input files with extention ```npy```, ```npz```, ```hdf5``` and ```aedat``` (corresponding to aedat2, not aedat4). 

The events read in ```npz``` and ```aedat``` files are output as *xypt*. The events read in ```npy``` and ```hdf5``` files are as read.

The ```loaderdat``` function is adapted from [here](https://github.com/SensorsINI/processAEDAT/blob/master/jAER_utils/loadaerdat.py).

## Translate to different formats
Events can be saved under different formats, either as one combinason of *xypt* or under a totally different formalism. These scripts translate *xypt* data into formalism specifically adaptated to various SNN simulators. 

### translate_2_formats/events2spikes.py
The function ```ev2spikes``` takes as input an event sample and tranlastes it into spikes to be given as input to PyNN.

[PyNN](http://neuralensemble.org/PyNN/) is a Python simulator of Spiking Neural Networks (SNN). Ts SpikeSourceArray neurons take input as a list-of-list named, each sub-list corresponding to the timestamps of spikes emitted by the corresponding neuron. If the event data correspond to a (w,h) sensor, the list-of-list will be of length w*h. 

All events are considered the same, there is no difference between positive and negative events as is. For the polarity to be kept, one should split the event data into two positive and negative samples, then translate them separately and feed them *via* two input layers to the SNN. 
