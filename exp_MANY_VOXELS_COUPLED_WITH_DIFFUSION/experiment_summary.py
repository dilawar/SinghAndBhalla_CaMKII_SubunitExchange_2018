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
import helper
import glob
from collections import defaultdict

def is_bistable( hist, bins ):
    # assumes that binsize is 1.
    #  print( hist, hist[1:-1] )
    if hist[0] > 5e-3 and hist[1] < hist[0]:
        return 1
    return 0

def find_diff_vals( f ):
    f  = os.path.basename(f)
    f = f.split('.')[0]
    fs = f.split( '+' )
    keys, vals = zip(*[ x.split('-', 1) for x in fs ])
    vals = map(float, vals)
    return dict(zip(keys, vals))

def main( ):
    print( '[INFO] Processing state distribution' )
    fs = glob.glob( './Dsub*_processed.dat' )
    files = [ ]
    for f in fs:
        d = find_diff_vals( f )
        files.append( (d, f) )

    if len( files ) == 0:
        print( '[WARN] No file found' )
        quit( )

    # Some data files had same seed so same values. Need to discard them.
    diffDict = {}
    offset = 2
    for d, f in sorted( files, key=lambda x: x[0]['Dpp']):
        print( 'Processing %s' % f )
        data = pd.read_csv( f, sep = ' ', comment = '#' )
        camkii = data[ 'CaMKII*' ].values
        nBins = camkii.max( )
        avg = camkii.mean()
        freq, bins = np.histogram( camkii, bins = nBins, density = True )
        t = is_bistable(freq, bins)
        diffDict[(d['Dpp'],d['Dsub'])] = (np.sum(freq[offset:nBins-offset]),avg,t)

    X, Y, Z, M, B = [], [], [], [], []
    for Dpp, Dsub in sorted( diffDict.keys( ) ):
        val, avg, isBis = diffDict[(Dpp,Dsub)]
        print(val, isBis)
        X.append( Dpp )
        Y.append( Dsub )
        Z.append( val )
        M.append( avg )
        B.append( isBis )

    plt.xscale( 'log' )
    plt.yscale( 'log' )
    plt.tricontourf(X, Y, M )
    plt.colorbar()
    plt.scatter( X, Y, s=[x*10 for x in B], marker='o', color='black')
    plt.xlabel( r'$D_{PP1}$' )
    plt.ylabel( r'$D_{sub}$' )
    df = pd.DataFrame()
    df['Dpp1'] = X
    df['Dsub'] = Y
    df['Avg CaMKII'] = M
    df['intermediate_state'] = Z
    df['is_bistable'] = B
    df.to_csv( 'result.csv', index = False )
    plt.savefig( 'test.png' )

if __name__ == '__main__':
    main( )
