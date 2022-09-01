import numpy as np

def get(g1, g2, g3, shift,shape, nb=2):
    assert shape in ['square', 'line']

    g2 = g2.copy()
    g3 = g3.copy()

    g2[:,0] = g2[:,0] + 128
    if shape == 'line':
       g3[:,0] = g3[:,0] + 128*2
    elif shape == 'square':
       g3[:,1] = g3[:,1] + 128

    g1a = g1.copy()
    g2a = g2.copy()
    g3a = g3.copy()
    
    g1a = g1a[g1a[:,3] <= shift*2]
    g2a = g2a[g2a[:,3] <= shift*3]
    g3a = g3a[g3a[:,3] <= shift*3]
    
    g2a[:,3] += shift
    g3a[:,3] += 3*shift
    
    if nb == 2:
        g1b = g1.copy()
        g2b = g2.copy()
        g3b = g3.copy()

        g1b = g1b[g1b[:,3] > shift*2]
        g1b = g1b[g1b[:,3] <= shift*5]

        g2b = g2b[g2b[:,3] > shift*3]
        g2b = g2b[g2b[:,3] <= shift*6]

        g3b = g3b[g3b[:,3] > shift*3]
        g3b = g3b[g3b[:,3] <= shift*5]

        g1b[:,3] += shift*5
        g2b[:,3] += shift*7
        g3b[:,3] += shift*9

        g = np.vstack((g1a, g1b, g2a, g2b, g3a, g3b))
    
    else : 
        g = np.vstack((g1a,g2a,g3a))
    
    g = g[g[:,3].argsort()]

    return g


a=np.load('gestures/gesture_target4.npy')
b=np.load('gestures/gesture_target7.npy')
c=np.load('gestures/gesture_target10.npy')

for t in [10,20,30,40,50,60,70,80,90,100,150,200]:
    e = get(a,b,c,t*1e3, shape='line')
    np.save("gestures/trio_line_4_7_10_"+str(t)+"ms.npy",e)
    e = get(a,a,a,t*1e3, shape='line')
    np.save("gestures/trio_line_4_4_4_"+str(t)+"ms.npy",e)

