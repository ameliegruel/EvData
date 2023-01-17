import argparse
import os
import numpy as np
import random
from datetime import datetime as d
import sys
sys.path.append('../read_event_data')
import loadData
from tqdm import tqdm

# initialise parser
parser = argparse.ArgumentParser(description='Generation random combinations of event samples')
parser.add_argument('-dataset', type=str, help='dataset to walk through (needs to end by events_np)', required=True)
parser.add_argument('-nb', type =int, help='number of combinations to create', default=100)
parser.add_argument('-S', action='store_true', help='keep only first second of data')
parser.add_argument('-duo', action='store_true', help='whether to create a duo (combination chosen per default)')
parser.add_argument('-trio', action='store_true', help='whether to create a trio')
parser.add_argument('-proba', action='store_true', help='whether to compute the probabilities (nb events, spatial and temporal densities)')
parser.add_argument('-shift', type=int, help='shift one sample compared to the other by a certain number of microseconds', default=-1)
args = parser.parse_args()

# select the files randomly
list_files = [
    os.path.join(repertory, f)
    for repertory,_,files in os.walk(args.dataset) 
    for f in files
]
random.shuffle(list_files)
print(len(list_files))

combination = 'duo'
n_lots = 2
if args.trio:
    combination = 'trio'
    n_lots = 3

n_samples = int( args.nb / n_lots )
samples = [[] for _ in range(n_lots)]
labels = [[None,None,None]]

n = 0
while n < n_samples:

    trio_labels = [None,None,None]
    
    while trio_labels in labels:
        trio_labels = []

        first_sample = list_files.pop()
        trio_labels.append(first_sample.split('/')[-2])
        second_sample = list_files.pop()
        trio_labels.append(second_sample.split('/')[-2])

        if args.trio:
            third_sample = list_files.pop()
            trio_labels.append(third_sample.split('/')[-2])
    
    labels.append(trio_labels)
    n += 1
    
    samples[0].append(first_sample)
    samples[1].append(second_sample)
    if args.trio:
        samples[2].append(third_sample)


assert len(samples[0]) == len(samples[1])

# create and store the new samples & compute probabilities
date_time = d.now().strftime("%Y%m%d-%H%M%S")
ff = 'combinations_'+combination+'_'+date_time

samples_references = 'file name;left sample;right sample;\n'

if args.trio:
    samples_references = 'file name;left sample;middle sample;right sample;\n'

if args.proba: 
    samples_info = 'sample name;nb events;temporal density;spatial density;\n'

shift = False
if args.shift > -1:
    shift = True
    samples_references = 'file name;left sample;right sample;shifted;shift;\n'
    ff = 'combinations_'+combination+'_shift'+str(args.shift)+'_'+date_time
    assert args.trio == False

final_folder = os.path.join(args.dataset, ff)
os.makedirs(final_folder)

for n in range(len(samples[0])):
    list_samples = []

    first = loadData.loadData(samples[0][n])
    first_label = samples[0][n].split('/')[-2]
    format = loadData.getFormat(first)
    first[:,format.index('t')] -= min(first[:,format.index('t')])

    second = loadData.loadData(samples[1][n])
    second_label = samples[1][n].split('/')[-2]
    second[:,format.index('t')] -= min(second[:,format.index('t')])

    sample_n_title = 'combination_'+combination+'_'+first_label+'_'+second_label+'.npy'
    sample_n_references = sample_n_title+';'+samples[0][n]+';'+samples[1][n]+';\n'
    
    if shift:
        shifted = random.choice(['left','right'])
        if shifted == 'left':
            first[:,format.index('t')] += args.shift
        else:
            second[:,format.index('t')] += args.shift
        sample_n_title = 'combination_'+combination+'_'+first_label+'_'+second_label+'_shifted_'+shifted+'_by_'+str(args.shift)+'.npy'
        sample_n_references = sample_n_title+';'+samples[0][n]+';'+samples[1][n]+';'+shifted+';'+str(args.shift)+';\n'

    list_samples.append((first.copy(),samples[0][n]))
    list_samples.append((second.copy(),samples[1][n]))
    second[:,format.index('x')] += max(first[:,format.index('x')])
    sample_n = np.vstack((first, second))

    if args.trio:
        third = loadData.loadData(samples[2][n])
        third_label = samples[2][n].split('/')[-2]
        third[:,format.index('t')] -= min(third[:,format.index('t')])
        list_samples.append((third.copy(),samples[2][n]))
        third[:,format.index('x')] += max(second[:,format.index('x')])
        
        sample_n = np.vstack((sample_n, third))
        sample_n_title = 'combination_'+combination+'_'+first_label+'_'+second_label+'_'+third_label+'.npy'
        sample_n_references = sample_n_title+';'+samples[0][n]+';'+samples[1][n]+';'+samples[2][n]+';\n'
    
    samples_references += sample_n_references
    np.save(
        os.path.join(final_folder, sample_n_title), 
        sample_n
    )

    if args.proba:
        time_window = 50e3
        for sample, sample_name in list_samples:
            X,Y,T = 128,128, max(sample[:,format.index('t')])
            start = 0
            done = set()
            nb = 0
            temporal_density = [[0 for _ in range(X)] for _ in range(Y)]
            spatial_density  = 0

            print('Proba sample', sample_name)
            for ev in tqdm(sample):
                x = ev[format.index('x')]
                y = ev[format.index('y')]
                t = ev[format.index('t')]
                
                # compute length
                nb += 1

                # compute spatial density
                if t >= (start + time_window):
                    nb_timewindows = int( (t - start) // time_window )
                    start += time_window * nb_timewindows
                    spatial_density += len(done) / ( X*Y )
                    done.clear()

                if (x,y) not in done:
                    done.add((x,y))
                
                # compute temporal density
                temporal_density[int(x)][int(y)] += 1
        
            spatial_density  /= int( T // time_window )
            temporal_density = np.sum(list(temporal_density / T)) / (X*Y)

            samples_info += sample_name+';'+str(nb)+';'+str(temporal_density)+';'+str(spatial_density)+';\n'
        print()

f_references = open(os.path.join(final_folder, 'references_'+date_time+'.csv'), 'a')
f_references.write(samples_references)
f_references.close()
print('New combinations correctly saved in',final_folder)

if args.proba : 
    f_proba = open(os.path.join(final_folder, 'probabilities_'+date_time+'.csv'), 'a')
    f_proba.write(samples_info)
    f_proba.close()