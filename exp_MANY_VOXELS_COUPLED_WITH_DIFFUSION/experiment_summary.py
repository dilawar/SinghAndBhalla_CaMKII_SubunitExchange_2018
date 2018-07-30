#!/usr/bin/env python3

"""experiment_summary.py: 

    It shows the effect of diffusion on intermediate states distribution. 
    As we increase the diffusion coefficient of subunits 'x' and 'y', the
    intermediate states become scarser. And the cluster of N switches starts
    acting like one switch.

    Generates on PNG file and store data in csv file which can plotted by other
    programs later.
"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import glob
import ajgar                # pip install git+https://github.com/dilawar/ajgar
from collections import defaultdict

def main( ):
    print( '[INFO] Processing state distribution' )
    fs = glob.glob( './_data_archive/*_processed*' )
    files = [ ]
    for f in fs:
        diffVal = f.split( 'diff' )[1]
        nums = ajgar.find_all_floats( diffVal )
        files.append( (-nums[0], f) )

    if len( files ) == 0:
        print( '[WARN] No file found' )
        quit( )

    # Some data files had same seed so same values. Need to discard them.
    diffDict = defaultdict( set )
    offset = 2
    for d, f in sorted( files ):
        print( 'Processing %s' % f )
        data = pd.read_csv( f, sep = ' ', comment = '#' )
        camkii = data[ 'CaMKII*' ].values
        nBins = camkii.max( )
        freq, bins = np.histogram( camkii, bins = nBins, normed = True )
        diffDict[d].add( np.sum( freq[ offset:nBins-offset ] ) )

    xvec, yvec, errvec = [ ], [ ], [ ]
    for x in sorted( diffDict.keys( ) ):
        vals = list( diffDict[x] )
        xvec.append( x )
        yvec.append( np.mean( vals ) )
        errvec.append( np.std( vals ) )

    plt.xscale( 'log' )
    plt.errorbar( xvec, yvec, yerr = errvec )
    plt.xlabel( 'Diffusion coefficient of subunit' )
    plt.ylabel( 'Intermediate state distributions' )
    plt.legend( )
    outfile = 'decay_of_intermediate_states.png'
    plt.savefig( outfile )
    # Save image into a data-file as well.
    ajgar.arrays2csv( '%s.dat' % outfile
            , diff_const = xvec, intermediate_states_mean = yvec
            , intermediate_states_std = errvec
            )



if __name__ == '__main__':
    main( )
