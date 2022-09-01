# EvData
This repository regroups different scripts to produce new event data samples, and process existing ones, for different file extensions and using different Python libraries.
All scripts are written in Python3 or in Bash. 

## Read event data

### read_event_data/loadData.py

#### Load data
The function ```load_data``` takes as input the path to an event file and opens it. It handles input files with extention ```npy```, ```npz```, ```hdf5``` and ```aedat``` (corresponding to aedat2, not aedat4). 

The events read in ```npz``` and ```aedat``` files are output as *xypt*. The events read in ```npy``` and ```hdf5``` files are as read.

The ```loaderdat``` function is adapted from [here](https://github.com/SensorsINI/processAEDAT/blob/master/jAER_utils/loadaerdat.py).

#### Get events' format
The function ```getFormat``` takes an event sample and outputs the corresponding format as a string of "x" (x coordinates),"y" (y coordinates),"p" (polarity),"t" (timestamps). The index of each information can be obtained using ```index()```. 

## Translate to different formats
Events can be saved under different formats, either as one combinason of *xypt* or under a totally different formalism. These scripts translate *xypt* data into formalism specifically adaptated to various SNN simulators. 

### translate_2_formats/events2spikes.py
The function ```ev2spikes``` takes as input an event sample and tranlastes it into spikes to be given as input to PyNN.

[PyNN](http://neuralensemble.org/PyNN/) is a Python simulator of Spiking Neural Networks (SNN). SpikeSourceArray neurons take input as a list-of-list, each sub-list corresponding to the timestamps of spikes emitted by the corresponding neuron. If the event data correspond to a (w,h) sensor, the list-of-list will be of length w*h. 

All events are considered the same, there is no difference between positive and negative events as is. For the polarity to be kept, one should split the event data into two positive and negative samples, then translate them separately and feed them *via* two input layers to the SNN.

### translate_2_formats/getSlayerData.py
This script translates events saved as *xypt* in npy/npz files into bs2 files to be given as input to a SLAYER network. 

[SLAYER](https://github.com/bamsumit/slayerPytorch) is a Python framework based on PyTorch and designed to simulate "backpropagation based SNN learning" on GPU. A specific "SLAYER Loihi" module has been implemented to run SNN models initially developed on SLAYER, on Intel's Loihi neuromorphic chips.  According to the authors, when the input is a spiking dataset "the spike data from the DVS is directly fed into the classifier".

SLAYER require a certain input architecture, which is obtained using this script. The ```slayerSNN``` is required, as the class ```event``` and function ```encode2Dspikes``` from the module```spikeFileIO``` [here](https://github.com/bamsumit/slayerPytorch/blob/master/src/spikeFileIO.py) are used.

The script's input arguments are: 
- ```dataset``` (str, required): path to the dataset to walk through (as is, this dataset needs to end by "events_np" since this script was initially used to translate [PLIF](https://www.frontiersin.org/articles/10.3389/fncom.2021.658764/full) input data into SLAYER input data
- ```divider``` (str, required): list of divider datasets to be transformed in dataset (i.e., what the input path must contain in order to translate the corresponding events)
- ```output``` (str, required): repertory where to store the information
- ```method``` (str, optional): list of methods to be transformed into dataset
- ```S``` (True if present, optional): wether to keep only first second of data
- ```nb``` (int, optional): number of events to keep in the first ones present in the sample
- ```nb_train``` (int, optional): number of samples to keep in train
- ```nb_test``` (int, optional): number of samples to keep in test
