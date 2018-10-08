#!/usr/bin/env python
import sys
import pandas as pd 
import numpy as np

N_ = 30
everyN_ = 10

def smooth( vec ):
    global N_
    return np.convolve( vec, np.ones(N_)/N_, 'same' )

def main():
    global N_
    data = pd.read_csv( sys.argv[1], sep = ' ' )
    data['time'] /= 3600.0 
    if len(sys.argv) > 2:
        N_ = int( sys.argv[2] )
    data['mean'] = smooth( data['CaMKII*'] )
    data = data[N_:-N_:everyN_]
    print( data.to_csv( index = False, header=False, sep = ' ', columns=['time', 'mean']) )

if __name__ == '__main__':
    main()
