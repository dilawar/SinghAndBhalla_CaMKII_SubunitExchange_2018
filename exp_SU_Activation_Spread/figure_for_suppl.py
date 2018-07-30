#!/usr/bin/env python
"""figure_for_suppl.py: 

This generates figure for supplementary.

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
import re

from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'

df_ = pd.DataFrame( )

def filter_files( files, dxy ):
    fs = []
    for f in files:
        ff = os.path.basename( f )
        m  = re.search( r'D-(\{.*?\})', ff )
        if m:
            d = eval(m.group(1).replace('--', ',').replace('++', ':'))
            if d['x'] == d['y'] == dxy:
                fs.append( (d,f) )
    return fs

def process( files, D, ax ):
    global df_
    files = filter_files( files, D )
    ys = []
    for i, (d, f) in enumerate(files):
        df = pd.read_csv( f, sep = ' ' )
        t = df['time'] 
        y = df['CaMKII*']
        ys.append( y )
        df_[ 'time' ] = t
        df_[ 'Dxy%g.%d' % (D,i) ] = y
        ax.plot( t/3600.0, y, alpha = 0.5 )

    ymean, ystd = np.mean( ys, axis=0), np.std(ys,axis=0)
    df_[ 'Dxy%gMean' % D ] = ymean
    df_[ 'Dxy%gSTD' % D ] = ystd
    #  ax.errorbar( t[::10], ymean[::10], ystd[::10], fmt='-o' )
    ax.plot( t/3600.0, ymean, lw=2 )
    ax.set_title( r'$D_{xy}=%g$' % D )
    ax.set_xlabel( 'Time (h)' )
    ax.set_ylabel( 'CaMKII' )

def main( ):
    dirname = sys.argv[1]
    files = glob.glob( './%s/*_processed.dat' % dirname )

    for i, D in enumerate([ 0e0, 1e-20, 1e-18, 1e-15, 1e-14, 1e-13 ]):
        ax = plt.subplot(2,3,i+1)
        process( files, D, ax )

    plt.suptitle( r'%s' % dirname.replace( r'_', r'\_') )
    plt.tight_layout( rect=(0,0,1.0,0.95) )
    plt.savefig( '%s.pdf' % dirname )
    df_.to_csv( '%s_summary.csv' % dirname, index = False )
    print( 'Wrote to {0}.pdf and {0}_summary.csv'.format(dirname))

if __name__ == '__main__':
    main()
