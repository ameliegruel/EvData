from subprocess import Popen, PIPE
from shlex import split
import argparse
import esim_py
import os
import numpy as np
import re
from skimage import io
from datetime import datetime as dt

### set up parser
parser = argparse.ArgumentParser(description="Get timestamps for an image dataset given as input")
parser.add_argument("dataset", metavar="D", type=str, help="Input dataset")
parser.add_argument("--contrast_threshold", "-ct", help="Define the contrast threshold used to compute the events", metavar="CT", type=float, default=0.25)
parser.add_argument("--frame_per_second", "-fps", help="Define the time interval between frames", metavar="F", type=int, default=30)
parser.add_argument("--output", "-o", help="Name of output file, where events will be saved", metavar="O", type=str, default=None)
parser.add_argument("--figure", "-f", help="Visualize the events", action='store_true', default=False)
args = parser.parse_args()

### fonctions

def getTS(
    dataset_repertory, 
    output_file="timestamps.txt",
    fps = 30 #fps
    ):
    
    frame_interval = 1e6 / fps  # if timestamps in microseconds

    # get number of files in input dataset
    p1 = Popen(split("ls "+dataset_repertory), stdout=PIPE)
    p2 = Popen(split("wc -l"), stdin=p1.stdout, stdout=PIPE)
    out, _ = p2.communicate()
    nb_files = int(out.strip().decode('ascii'))

    # create file 
    ts_file = open(output_file, "w")
    ts = 0
    while ts < nb_files-2:
        ts_file.write(str(float(ts*frame_interval))[::-1].zfill(9)[::-1]+"\n")
        ts += 1
    ts_file.write(str(float(ts*frame_interval))[::-1].zfill(9)[::-1])
    ts_file.close() 

# function provided by Gehrig et al (CVPR 2019) to visualise the events
def viz_events(events, resolution):
    pos_events = events[events[:,-1]==1]
    neg_events = events[events[:,-1]==-1]

    image_pos = np.zeros(resolution[0]*resolution[1], dtype="uint8")
    image_neg = np.zeros(resolution[0]*resolution[1], dtype="uint8")

    np.add.at(image_pos, (pos_events[:,0]+pos_events[:,1]*resolution[1]).astype("int32"), pos_events[:,-1]**2)
    np.add.at(image_neg, (neg_events[:,0]+neg_events[:,1]*resolution[1]).astype("int32"), neg_events[:,-1]**2)

    image_rgb = np.stack(
        [
            image_pos.reshape(resolution), 
            image_neg.reshape(resolution), 
            np.zeros(resolution, dtype="uint8") 
        ], -1
    ) * 50

    return image_rgb

def plot_figure(events, H,W):
    import matplotlib.pyplot as plt

    # get optimal parameters
    number_events_per_plot = int(1e6)
        
    plt.imshow(viz_events(events[:number_events_per_plot], [H, W]))
    plt.savefig("contrast_train.png")

def produceEvents(
    dataset,
    args
):
    # get data
    image_folder = os.path.join(os.path.dirname(__file__), dataset)
    getTS(dataset, fps=args.frame_per_second)
    timestamps_file = os.path.join(os.path.dirname(__file__), "timestamps.txt")

    # define parameters
    contrast_threshold_positive = contrast_threshold_negative = args.contrast_threshold
    refractory_period = 1e-4
    log_eps = 1e-3
    use_log = True
    H, W, _ = io.imread( 
        os.path.join( dataset, os.listdir(dataset)[0] )
    ).shape  # height and wideness of images (high resolution)

    event_simulator = esim_py.EventSimulator(contrast_threshold_positive, contrast_threshold_negative, refractory_period, log_eps, use_log)
    events = event_simulator.generateFromFolder(image_folder, timestamps_file)

    # save events
    if args.output == None:
        output_file = re.sub('/$','',dataset.replace('frames','events'))+'.npy'
    else :
        output_file = args.output[0]
    np.save(output_file, events)
    print("Events produced from "+dataset+" saved as "+output_file)

    # display figure
    if args.figure:
        plot_figure(events, H, W)

    # clean up
    os.remove(timestamps_file)


### MAIN
for (rep, _, _) in os.walk(args.dataset):
    if 'frames' in rep or 'Fr' in rep:
        print(">",rep)
        start = dt.now()
        produceEvents(rep, args)
        print(f'Time {rep}: {(dt.now() - start).total_seconds()} \n')
