import argparse
from slayerSNN import spikeFileIO as s
import os
import numpy as np

# initialise parser
parser = argparse.ArgumentParser(description='Generation of slayer input')
parser.add_argument('-dataset', type=str, help='dataset to walk through (needs to end by events_np)', required=True)
parser.add_argument('-divider', nargs='+', help='list of divider dataset to be transformed in dataset', required=True)
parser.add_argument('-method', nargs='+', help='list of methods to be transformed in dataset', default=[])
parser.add_argument('-output', type=str, help='repertory where to store the information', required=True)
parser.add_argument('-S', action='store_true', help='keep only first second of data')
parser.add_argument('-nb', type=int, help='keep only N first events of data', default=-1)
parser.add_argument('-nb_train', type=int, help='number of samples to keep in train',default=-1)
parser.add_argument('-nb_test', type=int, help='number of samples to keep in test', default=-1)
args = parser.parse_args()

if args.dataset[-1] != '/':
    args.dataset += '/'
if args.output[-1] != '/':
    args.output += '/'

# functions test
def isData(repertory):
    datasets = args.divider
    # datasets = ['new_div10', 'new_div4', 'new_div25']
    for d in datasets:
        if len(args.method) != 0:
            for m in args.method:
                if d in repertory and m in repertory:
                    return True
        if d in repertory and len(args.method) == 0:
            return True
    return False


# create train.txt and test.txt
def initialiseTxtFiles(rep):
    # os.makedirs(rep)
    train_file = 'train.txt'
    test_file  = 'test.txt'
    
    for f in [train_file, test_file]:
        rep_f = os.path.join(rep, f)
        if not os.path.isfile( rep_f ):
            ftxt = open(rep_f, 'w')
            ftxt.write('sample\tlabel\n')
            ftxt.close()

def addFileToTxt(global_rep, rep, f_name, label):
    if 'train' in global_rep: #f_name:
        path_txt = os.path.join(rep, 'train.txt')
    elif 'test' in global_rep: # f_name:
        path_txt = os.path.join(rep, 'test.txt')

    ftxt = open(path_txt, 'a')
    ftxt.write(f_name+"\t"+label+"\n")
    ftxt.close() 

# walk the files
for (input_rep, _, files) in os.walk(args.dataset):
    repertory = input_rep.replace(args.dataset,"").split("/")
    if ('events_np' in repertory or  'events_np_0.2' in repertory) and isData(repertory):
        output_rep = os.path.join( args.output, repertory[0], repertory[1] )

        if 'events_np' in repertory[-1]:
            print(output_rep)
            nb_sample = 0
            os.makedirs(output_rep, exist_ok=True)
            # initialiseTxtFiles(output_rep)
        
        if 'train' in repertory and args.nb_train > -1:
            files = np.random.choice(files, size=args.nb_train,replace=False)
        elif 'test' in repertory and args.nb_test > -1 :
            files = np.random.choice(files, size=args.nb_test,replace=False)
        
        # try:
        for f in files:
            if f.endswith('npz'): # and not os.path.exists(os.path.join( output_rep, str(nb_sample)+'.bs2' )):
                # print(str(nb_sample)+'.bs2' )
                
                try:
                    # create event
                    F = np.load( os.path.join( input_rep, f ) )
                    x = F['x']
                    y = F['y']
                    p = F['p']
                    t = F['t']
                
                    # keep data according to arguments
                    if args.S and len(t) > 0:
                        t_1s = t[0] + 1e+6
                        x = x[t <= t_1s]
                        y = y[t <= t_1s]
                        p = p[t <= t_1s]
                        t = t[t <= t_1s]

                    elif args.nb > -1:
                        x = x[:args.nb]
                        y = y[:args.nb]
                        p = p[:args.nb]
                        t = t[:args.nb]

                    ev = s.event(
                        xEvent = x,
                        yEvent = y,
                        pEvent = p,
                        tEvent = t
                    )

                    # create corresponding output directory
                    # f_name = '_'.join(repertory).split('events_np_')[-1] + '_' + f[:-3] + 'bs2'
                    s.encode2Dspikes(
                        os.path.join( output_rep, str(nb_sample)+'.bs2' ),
                        ev   
                    )

                    # save info in txt files
                    label = repertory[-1]
                    addFileToTxt(repertory, output_rep, str(nb_sample), label)
                    nb_sample += 1
        
                except (ValueError, IndexError):
                    pass

print('Translation of '+args.dataset+' into bs2 files stored in '+args.output)