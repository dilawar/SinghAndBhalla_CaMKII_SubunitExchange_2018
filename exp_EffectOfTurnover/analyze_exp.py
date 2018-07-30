#!/usr/bin/env python3

"""analyze_exp.py:

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
import pandas as pd
import helper
import re
import glob

import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.style.use( 'ggplot' )

df = pd.DataFrame( )

def extract_params( f ):
    pat = re.compile( r'CaM(?P<camkii>\d+)_turnover(?P<turnover>.+?)_su(?P<SE>ON|OFF)' )
    m = pat.search( f )
    return m.groupdict()

def analyze_helper( N, suON, suOFF ):

    plt.figure( figsize=(6, 5) )
    ax1 = plt.subplot( 211 )
    ax2 = plt.subplot( 212, sharex = ax1 )

    suONRes, suOFFRes = [ ],  [ ]
    for d, attrib in suON:
        camkii = d[ 'CaMKII*' ]
        trans = helper.find_transitions( camkii, [0, N] )
        suONRes.append( (attrib, trans) )

    for d, attrib in suOFF:
        camkii = d[ 'CaMKII*' ]
        trans = helper.find_transitions( camkii, [0, N] )
        suOFFRes.append( (attrib, trans) )

    for su, (ax1, ax2), data in zip( ['OFF','ON'], [(ax1, ax2),(ax1,ax2)], [suOFFRes, suONRes] ):
        xvec, y1, y2 = [], [], []
        for x, y in data:
            xvec.append( 1 / (float(x[ 'turnover' ])) )
            y1.append( len( y['up_transitions'] ) )
            y2.append( y['kramer_time'][1][1] )

        df[ 'x_%s' % su ] =  xvec
        df[ 'transitions_%s' % su ] =  y1
        df[ 'KramerON_%s' % su ] =  y2

        ax1.semilogx( xvec, y1, '-o', label = 'SE=%s' % su)
        ax1.legend( )
        ax2.semilogx( xvec, y2, '-o', label = 'SE=%s' % su)
        ax2.legend( )

    ax1.set_ylabel( 'Number of transitions' )
    ax1.set_xlabel( 'Turnover rate (per hour)' )
    ax2.set_ylabel( 'Fraction of time spent in ON state' )
    ax2.set_xlabel( 'Turnover rate (per hour)' )
    plt.tight_layout( )
    pngfile = 'camkii%d_result.png' % N 
    plt.savefig( pngfile )
    print( '[INFO] Image saved to %s' % pngfile )
    df.to_csv( 'camkii%d_data_effect_of_turnover.csv' % N, index = False )
    print( '[INFO] Data saved to camkii%d_data_turnover.csv' % N)


def analyze( camkii, files ):
    res = {} 
    suON, suOFF = [ ], [ ]
    for f in files:
        attrib = extract_params( f )
        d = pd.read_csv( f, sep = ' ' )
        if attrib[ 'SE' ] == 'ON':
            suON.append( (d, attrib) )
        else:
            suOFF.append( (d, attrib) )
    analyze_helper( camkii, suON, suOFF )

def sort_file( files ):
    fs = [ ]
    for f in files:
        tr = re.search( 'CaM(\d+).+?turnover(\d+)', f )
        fs.append( (float(tr.group(1)), float(tr.group(2)), f) )
    fs = sorted( fs )
    return [ x[-1] for x in fs ]

def main( ):
    for camkii in [ 6, 8, 12, 16 ]:
        files = glob.glob( '*CaM%d*processed.dat' % camkii )
        analyze( camkii, sort_file(files) )
    print( 'All done' )

if __name__ == '__main__':
    main()

