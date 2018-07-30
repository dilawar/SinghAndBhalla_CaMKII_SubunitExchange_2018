"""compute_transitions.py: 

Compute up-down transitions in timeseries.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.signal  as _sig

def smooth( sig, N = 100 ):
    window = np.ones( N ) / float( N )
    return np.convolve(  sig, window, 'same' )

def digitize( sig, levels, thres = 4 ):
    for x in levels:
        sig[ (sig > (x-thres)) & (sig < (x+thres)) ] = x
    sig[ np.isnan( sig ) ] = 0
    return sig 

def compute_transitions( vec, levels, thres = 4 ):
    sig = digitize( vec, levels, thres )
    result = { }
    for x in levels:
        xIds = np.where( vec ==  x )[0]
        result[ 'kramer_%s' % x ] = len( xIds ) / 1.0 / len( vec )

    trans = np.diff( sig ) 

    result[ 'up_transitions' ] = np.where( trans > 0 )[0]
    result[ 'down_transitions' ] = np.where( trans < 0 )[0]

    return result, sig

    
def process( datafile ):
    data = pd.read_csv( datafile, sep = ' ', comment = '#' )
    data.dropna( how = 'any' )
    camkii = data.filter( regex = r'x0y\d.+' )
    tvec = data[ 'time' ]
    lowCaMKII = np.sum( camkii, axis = 1 )
    sig = smooth( lowCaMKII, 500 )
    res, newY = compute_transitions( sig, [0,8,16] )
    print( res )
    upT = tvec[ res[ 'up_transitions' ] ]
    downT = tvec[ res[ 'down_transitions' ] ]

    plt.subplot( 311 )
    plt.plot( tvec, lowCaMKII  )
    plt.plot( upT, sig.max() * np.ones( len( upT ) ) , '+' )
    plt.plot( downT, sig.min() * np.ones( len( downT ) ) , '+' )
    plt.subplot( 312 )
    #plt.plot( tvec, step_detection( yvec, 0, 8 ) )
    plt.plot( tvec, sig )
    plt.subplot( 313 )
    plt.plot( tvec, newY )
    plt.savefig( '%s_transitions.png' % datafile )

def main( ):
    datafile = sys.argv[1]
    process(datafile)

if __name__ == '__main__':
    main()
