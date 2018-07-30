#!/usr/bin/env python
"""generate_figure.py: 

Figure from _data.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import re
import numpy as np
import pandas as pd
import glob
import ajgar
import pypgfplots
import pickle

import scipy.optimize as so
import scipy.misc as sm
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
try:
    mpl.style.use( 'ggplot' )
except Exception as e:
    pass
mpl.rcParams['axes.linewidth'] = 0.1
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
sys.path.append( '..' )

def transition( vec, i, midval, maxval ):
    res = [ ]
    j = 1
    while (midval + abs( vec[i-j] - midval )) < maxval:
        j += 1
    res.append( i - j )

    j = 1
    while (midval + abs( vec[i+j] - midval )) < maxval:
        j += 1
    res.append( i + j )

    return res


def transitions( vec, maxval ):
    print( '[INFO] Computing transition in CaMKII vector %d' % maxval )
    try:
        vec = vec.values
    except Exception as e:
        pass

    transT = [ ]
    x = np.where( vec == maxval / 2 )[0]
    xd = x[ np.where( np.diff( x ) >  1)[0] ]
    for v in xd[1:-1]:
        if len( transT ) > 0:
            prevT = transT[-1]
            if v < prevT[1]:
                continue
        try:
            t = transition( vec, v, maxval / 2, maxval )
            transT.append( t )
        except Exception as e:
            pass
    return transT

def sigmoid(x, x0, k, a):
    x = np.array( x )
    y = a / (1 + np.exp(-k*(x-x0)))
    return y

def gauss(x, A, mu, sigma):
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))

def poisson(x, A, lamb):
    return (A * lamb**x/sm.factorial(x)) * np.exp(-lamb)

def process( f ):
    print( '[INFO] Processing %s' % f )
    d = pd.read_csv( f, sep = ' ', comment = '#' )
    res = { }
    res[ 'MAXPP1' ] = int( re.search( r'PP(\d+)_', f ).group(1) )
    res[ 'MAXCAMKII' ] = maxCaM = int( re.search( r'CaM(\d+)_', f ).group(1) )
    res[ 'data' ] = d
    res[ 'suON' ] = '_suON' in f
    trans = transitions( d['CaMKII*'], maxCaM )
    res[ 'transitions' ] = trans
    return res

def main( ):
    if len( sys.argv ) < 2:
        print( 'USAGE: python %s FILES' % sys.argv[0] )
        quit( )

    pickleFile = '%s.pickle' % sys.argv[0]
    if not os.path.isfile( pickleFile ):
        # Sort files by number of PP1 in 
        files = sorted( 
                sys.argv[1:]
                , key = lambda x: int( re.search( r'PP(\d+)_', x).group(1)) 
                )

        toplot = [ ]
        [ toplot.append( process(f) ) for f in files ]
        with open( pickleFile, 'wb' ) as f:
            pickle.dump( toplot, f )
    else:
        print( '[WARN] Using cached pickle file %s' % pickleFile )
        with open( pickleFile, 'rb' ) as f:
            toplot = pickle.load( f )

    plt.figure( figsize=(12, 8) )
    plt.subplot( 211 )

    samples = [ toplot[35], toplot[20] ]
    for i, res in enumerate( samples ):
        suON, d = res[ 'suON' ], res[ 'data' ]
        x, y = d[ 'time' ], d['CaMKII*']
        y = y / y.max( )
        plt.plot( x, 1.5*i + y
                , label = 'With subunit-exchange' if suON else 'Without subunit-exchange'
                )
        plt.legend( framealpha = 0.1 )

    plt.yticks( [0.5, 2.0], [1, 2] )
    plt.title( 'Two sample trajectories: red (with subunit-exchange) and \
        blue (without subunit-exchange)'
        )

    suONY, suOFFY = [ ], [ ]
    suONYerr, suOFFYerr = [ ], [ ]
    suONX, suOFFX = [ ], [ ]
    suONH, suOFFH = [ ], [ ]
    suONRelax, suOFFRelax = [ ], [ ]
    for i, d in enumerate( toplot ):
        s = d['data']
        suON = d[ 'suON' ]
        camkii = d[ 'MAXCAMKII' ]
        actCaMKII = s[ 'CaMKII*']
        h, bs = np.histogram( actCaMKII, bins = camkii + 1, normed = True )
        pp1 = d[ 'MAXPP1' ]
        y = np.mean( actCaMKII / camkii )
        yerr = np.sum( h[2:-2] )
        if suON:
            suONY.append( y )
            suONYerr.append( yerr )
            suONX.append( pp1 / camkii)
            suONH.append( h )
            suONRelax.append( [ abs(x[1] - x[0]) for x  in d['transitions'] ] )
        else:
            suOFFY.append( y )
            suOFFYerr.append( yerr )
            suOFFX.append( pp1 / camkii )
            suOFFH.append( h )
            suOFFRelax.append( [ abs(x[1] - x[0]) for x  in d['transitions'] ] )

    df = pd.DataFrame( )
    df[ 'suON_pp1bycamkii' ] = suONX
    df[ 'suON_avgactivity' ] = suONY
    df[ 'suON_avgactivity_err' ] = suONYerr
    df[ 'suOFF_pp1bycamkii' ] = suOFFX
    df[ 'suOFF_avgactivity' ] = suOFFY
    df[ 'suOFF_avgactivity_err' ] = suOFFYerr

    y1 = [ sum(x[2:]) for x in suOFFH ]
    y2 = [ sum(x[2:]) for x in suONH ]
    assert len(y1) == len(y2), (y1, y2)
    df[ 'suON_intermediate_states' ] = y1
    df[ 'suOFF_intermediate_states' ] = y2

    y = [ np.mean( x ) for x in suOFFRelax ]
    yerr = [ np.std( x ) for x in suOFFRelax ]
    df[ 'suOFF_relaxation_time_mean' ] = y
    df[ 'suOFF_relaxation_time_std' ] = yerr

    y = [ np.mean( x ) for x in suONRelax ]
    yerr = [ np.std( x ) for x in suONRelax ]
    df[ 'suON_relaxation_time_mean' ] = y
    df[ 'suON_relaxation_time_std' ] = yerr

    # Add the distribution of states.
    for i in range( camkii + 1 ):
        df[ 'suON_hist_%d' % i ] = [ h[i] for h in suONH ]
        df[ 'suOFF_hist_%d' % i ] = [ h[i] for h in suOFFH ]

    outfile = 'summary_CaM%d.png' % camkii
    df.to_csv( '%s.csv' % outfile, index = False )
    print( '[INFO] Saved to %s and %s.csv' % (outfile, outfile) )

    # now plot
    plt.subplot( 223 )

    suOFFX, suOFFY = df[ 'suOFF_pp1bycamkii'], df[ 'suOFF_avgactivity']
    suOFFYerr = df[ 'suOFF_avgactivity_err' ]
    plt.plot( suOFFX, suOFFY, '*', color = 'blue', label='' )
    poptSUOFF, pcov = so.curve_fit( sigmoid, suOFFX, suOFFY, p0=[ 12, -0.7, 1 ] )
    plt.plot( suOFFX, sigmoid( suOFFX, *poptSUOFF ), color = 'blue' 
            , label = r'Without SU. $x_0=%.2f$, $k=%.2f$' % tuple( poptSUOFF[:2] )
            )

    suONX, suONY = df[ 'suON_pp1bycamkii'], df[ 'suON_avgactivity']
    suONYerr = df[ 'suON_avgactivity_err' ]
    plt.plot( suONX, suONY, 'o', color = 'red', label='' )
    poptSUON, pcov = so.curve_fit( sigmoid, suONX, suONY, p0=[ 12, -0.7, 1 ] )
    plt.plot( suOFFX, sigmoid( suONX, *poptSUON ), color = 'red' 
            , label = r'With SU. $x_0=%.2f$, $k=%.2f$' % tuple( poptSUON[:2] )
            )

    plt.text( 22, 0.5, r'$y=\frac{1}{1+ k \exp(x-x_0)}$', size = 14 )

    plt.plot( suONX, suONYerr.values, '-o', color = 'red'
            , label = 'With SU: Intermediate states' )
    plt.plot( suOFFX, suOFFYerr.values, '-*', color = 'blue'
            , label = 'Without SU: Intermediate States' )
    plt.legend( framealpha = 0.1, loc='upper right' )

    #plt.title( r'Errorbar represents fraction of time spent in intermediate states' )
    plt.xlabel( r'$x=\frac{PP1}{CaMKII}$' )
    plt.ylabel( r'State distribution (normalized)' )
    plt.title( r'Decay of Average CaMKII activity v/s PP1 \\ ' + \
            r' Distribution of intermediate states' 
            )

    plt.subplot( 224 )

    plt.errorbar( 
            suOFFX, df['suOFF_relaxation_time_mean']
            , yerr = df[ 'suOFF_relaxation_time_std']
            , color = 'blue' , label = 'Without SU'
            )
    plt.ylabel( r'Time (sec)' )
    plt.legend( )

    plt.errorbar( 
            suOFFX, df['suON_relaxation_time_mean']
            , yerr = df[ 'suON_relaxation_time_std']
            , color = 'blue' , label = 'Without SU'
            )

    plt.xlabel( r'$ \frac{PP1}{CaMKII}$' )
    plt.title( r'Relaxation time V/s $\frac{PP1}{CaMKII}$' )
    plt.legend( )

    plt.suptitle( 'Red line: with subunit-exchange, \
            Blue line: Without subunit exchange' )
    plt.tight_layout( pad = 3 )
    plt.savefig( outfile )


if __name__ == '__main__':
    main()
