#!/usr/bin/env python

import pandas as pd
import sys
import re
import os
from collections import OrderedDict
import ajgar    # https://github.com/dilawar/ajgar

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

mpl.rcParams['axes.linewidth'] = 0.1
plt.rc('text', usetex=False)
plt.rc('font', family='serif')

def raw_traces( data ):
    f, axarr = plt.subplots( len(data), sharex = True, figsize=(12,18) )
    result = [ ]
    for i, x in enumerate( data.keys( ) ):
        fs = ajgar.find_all_floats( x )
        ax = axarr[i]
        yvec = data[ x ][ 'CaMKII*' ].values
        tvec = data[ x ][ 'time' ].values / 86400
        ax.plot( tvec, yvec, lw = .5 )
        ax.set_title( x, fontsize = 8 )
        divider = make_axes_locatable( ax )
        cax = divider.append_axes("right", size="10%", pad=0.05, sharey = ax )
        n, bins, ps = cax.hist( yvec, bins = 7, normed = True, orientation = 'horizontal' )
        result.append( ( fs[-1], fs[-2], n ) )
        cax.set_xlim( [ 0, 1.] )
        cax.set_yticks( [ ] )
    
    axarr[-1].set_xlabel( 'Time (day)' )
    outfile = 'analysis_trace.png' 
    plt.savefig( outfile )
    print( '[INFO] Saved to %s' % outfile )
    plt.close( )

    plt.figure( )
    res = [ ]
    for kb, kf, hist in result:
        res.append( ( kf / (kf + kb ), hist[0] + hist[1] ) )
    plt.xlabel( 'Fraction of x removed' )
    plt.ylabel( 'Time spent in OFF state' )
    xvec, yvec = zip( *sorted( res ) )

    # Write result to a summary file.
    with open( 'summary.dat', 'w' ) as f:
        f.write( 'fraction_of_x_removed time_spent_in_off_state\n' )
        for x, y in sorted( res ):
            f.write( '%g %g\n' % (x, y) )

    plt.plot( xvec, yvec, '-o' )
    plt.ylim( [0, 1.0 ] )
    plt.savefig( 'summary.png' )
    print( '[INFO] Saved to summary.png file' )

def sort_files( files ):
    result = [ ]
    for x in files:
        fs = ajgar.find_all_floats( x )
        kb, kf = fs[-1], fs[-2]
        result.append( ( kf / (kf + kb), x ) )
    result.sort( )
    return [ x[1] for x in result ]

def analyze( data ):
    raw_traces( data )

def main( ):
    files = [ ]
    for d, df,fs in os.walk( '.' ):
        for f in fs:
            if '_processed' in f:
                files.append( os.path.join( d, f ) )

    files = sort_files( files )
    data = OrderedDict( )
    for f in files:
        data[ f ] = pd.read_csv( f, sep = ' ' )
    analyze( data )


if __name__ == '__main__':
    main()
