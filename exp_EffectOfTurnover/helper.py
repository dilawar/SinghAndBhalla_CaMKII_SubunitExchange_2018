"""camkii.py: 
Function to analyze CaMKII data.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import numpy as np
from collections import defaultdict

def fraction_of_time_spent_in_a_state( yvec, state, margin = 0 ):
    """Compute the residence time of given state 
    """
    n = len( yvec[ yvec == state ] )
    if margin > 0:
        for x in range( -margin, margin ):
            n += len( yvec[ yvec == x] )
    return float( n ) / len( yvec )

def smooth( sig, N = 100 ):
    window = np.ones( N ) / float( N )
    return np.convolve(  sig, window, 'same' )

def digitize( sig, levels, margins ):
    for x, t in zip(levels, margins):
        sig[ (sig > (x-t)) & (sig < (x+t)) ] = x
    sig.fillna(0)
    return sig 


def find_transitions( vec, levels, thres = 4 ):
    sig = digitize( vec, levels, [ thres ] * len( levels ) )
    result = defaultdict( list )
    for x in levels:
        xIds = np.where( vec ==  x )[0]
        result[ 'kramer_time' ].append( (x, len( xIds ) / 1.0 / len( vec )) )

    trans = np.diff( sig ) 
    result[ 'up_transitions' ] = np.where( trans > 0 )[0]
    result[ 'down_transitions' ] = np.where( trans < 0 )[0]
    return result

def compute_karmer_time( vec, levels, margins ):
    sig = digitize( vec, levels, margins )
    result = { }
    for x in levels:
        xIds = np.where( vec ==  x )[0]
        result[x] = len( xIds ) / 1.0 / len( vec )
    return result

def compute_transitions( vec, levels, margins ):
    states = range( len(levels) )
    res = [ ]
    x0 = vec[0]
    s0 = 0
    for i, (l,m) in enumerate( zip(levels, margins) ):
        if x0 > l - m and x0 <= l + m:
            s0 = i
            break

    s0, s1 = s0, s0
    i0, i1 = 0, 0
    for i, v in enumerate( vec[1:] ):
        if v > levels[s1] - margins[s1] and v <= levels[s1] + margins[s1]: 
            # its not possible to jump over a state so new state is the next
            # state.
            s0 = s1
            s1 = (s1 + 1) % len( states )
            res.append( ((levels[s0], levels[s1]), i+1) )
    return res

def test( ):
    import pylab
    import pandas as pd
    d = pd.read_csv( sys.argv[1], sep = ' ', comment  = '#' )
    t = d['time']
    camkii = smooth( d[ 'CaMKII*' ], N = 200 )
    res = compute_transitions( camkii, [0, 8], [1,1] )
    print( res )
    pylab.subplot( 211 )
    pylab.plot( t, camkii )
    pylab.subplot( 212 )
    pylab.savefig( 'test1.png' )

if __name__ == '__main__':
    test()
