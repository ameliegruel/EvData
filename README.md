# EvData
This repository regroups different scripts to produce new event data samples, and process existing ones, for different file extensions and using different Python libraries.
All scripts are written in Python3 or in Bash. 

## Read event data
The function ```load_data``` (in read_event_data/loadData.py) takes as input the path to an event file and opens it. It handles input files with extention ```npy```, ```npz```, ```hdf5``` and ```aedat``` (corresponding to aedat2, not aedat4). 

The events read in ```npz``` and ```aedat``` files are output as *xypt*. The events read in ```npy``` and ```hdf5``` files are as read.

The ```loaderdat``` function is adapted from [here](https://github.com/SensorsINI/processAEDAT/blob/master/jAER_utils/loadaerdat.py).
