import numpy as np
import hdf5 as h

def loadaerdat(datafile, debug=1, camera='DVS128'):
    """
    Adapted from https://github.com/SensorsINI/processAEDAT/blob/master/jAER_utils/loadaerdat.py
    load AER data file and parse these properties of AE events:
    - timestamps (in us), 
    - x,y-position [0..127]
    - polarity (0/1)
    @param datafile - path to the file to read
    @param debug - 0 = silent, 1 (default) = print summary, >=2 = print all debug
    @param camera='DVS128' or 'DAVIS240'
    @return (ts, xpos, ypos, pol) 4-tuple of lists containing data of all events;
    """
    # constants
    EVT_DVS = 0  # DVS event type
    aeLen = 8  # 1 AE event takes 8 bytes
    readMode = '>II'  # struct.unpack(), 2x ulong, 4B+4B
    td = 0.000001  # timestep is 1us   
    if(camera == 'DVS128'):
        xmask = 0x00fe
        xshift = 1
        ymask = 0x7f00
        yshift = 8
        pmask = 0x1
        pshift = 0
    elif(camera == 'DAVIS240'):  # values take from scripts/matlab/getDVS*.m
        xmask = 0x003ff000
        xshift = 12
        ymask = 0x7fc00000
        yshift = 22
        pmask = 0x800
        pshift = 11
        eventtypeshift = 31
    else:
        raise ValueError("Unsupported camera: %s" % (camera))

    aerdatafh = open(datafile, 'rb')
    k = 0  # line number
    p = 0  # pointer, position on bytes
    statinfo = os.stat(datafile)
    length = statinfo.st_size 
    if debug > 0:
        print ("file size", length)
    
    # header
    lt = aerdatafh.readline()
    while lt and lt[0] == "#":
        p += len(lt)
        k += 1
        lt = aerdatafh.readline() 
        if debug >= 2:
            print (str(lt))
        continue
    
    # variables to parse
    timestamps = []
    xaddr = []
    yaddr = []
    pol = []
    
    # read data-part of file
    aerdatafh.seek(p)
    s = aerdatafh.read(aeLen)
    p += aeLen
    
    while p < length:
        addr, ts = struct.unpack(readMode, s)
        # parse event type
        if(camera == 'DAVIS240'):
            eventtype = (addr >> eventtypeshift)
        else:  # DVS128
            eventtype = EVT_DVS
        
        # parse event's data
        if(eventtype == EVT_DVS):  # this is a DVS event
            x_addr = (addr & xmask) >> xshift
            y_addr = (addr & ymask) >> yshift
            a_pol = (addr & pmask) >> pshift


            if debug >= 3: 
                print("ts->", ts)  # ok
                print("x-> ", x_addr)
                print("y-> ", y_addr)
                print("pol->", a_pol)

            timestamps.append(ts)
            xaddr.append(x_addr)
            yaddr.append(y_addr)
            pol.append(a_pol)
                  
        aerdatafh.seek(p)
        s = aerdatafh.read(aeLen)
        p += aeLen        

    if debug > 0:
        try:
            print ("read %i (~ %.2fM) AE events, duration= %.2fs" % (len(timestamps), len(timestamps) / float(10 ** 6), (timestamps[-1] - timestamps[0]) * td))
            n = 5
            print ("showing first %i:" % (n))
            print ("timestamps: %s \nX-addr: %s\nY-addr: %s\npolarity: %s" % (timestamps[0:n], xaddr[0:n], yaddr[0:n], pol[0:n]))
        except:
            print ("failed to print statistics")

    events = np.concatenate((
        [[e] for e in xaddr],
        [[e] for e in yaddr],
        [[e] for e in pol],
        [[e] for e in timestamps]
    ), axis=1).astype('float64')

    return events

def loadData(file_name):
    if file_name.endswith('npy'): 
        ev = np.load(file_name)
        
    elif file_name.endswith('npz'):
        ev = np.load(file_name)
        ev = np.concatenate((
            ev["x"].reshape(-1,1),
            ev["y"].reshape(-1,1),
            ev["p"].reshape(-1,1),
            ev["t"].reshape(-1,1)
        ), axis=1).astype('float64')
    
    elif file_name.endswith('hdf5'):
        ev = h.File(file_name,'r')
        assert 'event' in ev.keys()
        ev = np.array(ev['event'])
    
    elif file_name.endswith('aedat'):
        ev = loadaerdat(file_name)

    return ev

def getFormat(ev):
    string_coord = [None]*4
    set_coord = [2,3]
    
    if max(ev[:,2]) in [0,1]:
        coord_p = 2
        set_coord.remove(2)
    elif max(ev[:,3]) in [0,1]:
        coord_p = 3
        set_coord.remove(3)
    string_coord[coord_p] = 'p'

    if max(ev[:,0]) > 1e6:
        coord_ts = 0
        coord_x = 1
        coord_y = set_coord[0]
    else:
        coord_ts = set_coord[0]
        coord_x = 0
        coord_y = 1
    
    string_coord[coord_x] = 'x'
    string_coord[coord_y] = 'y'
    string_coord[coord_ts] = 't'
    
    return ''.join(string_coord)