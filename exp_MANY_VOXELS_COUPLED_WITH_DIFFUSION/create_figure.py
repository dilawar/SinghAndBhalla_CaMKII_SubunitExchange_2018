#!/usr/bin/env python3

"""create_figure.py: 

    This script create figrue for paper. 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import OrderedDict, defaultdict
import glob
import ajgar # pip3 install git+https://github.com/dilawar/ajgar

data_ = defaultdict( list )

def create_figure( ):
    global data_
    datafiles = glob.glob( './_data_archive/*processed*.dat' )
    for f in sorted( datafiles ):
        fracs = ajgar.find_floats( f )
        dConst = - fracs[ 5 ]
        print( '[INFO] Loading file %s' % f )
        d = pd.read_csv( f, sep = ' ', comment = '#' )
        data_[ dConst ].append( d )

    print( data_.keys( ) )
    diffConst = [ 0, 1e-15, 1e-13 ]
    for i, d in enumerate( diffConst ):
        print( 'Diffusion const %g' % d )
        data = data_[ d ]
        data = sum( data ) / len( data )
        camkii =  data[ 'CaMKII*' ] 
        plt.subplot( len( diffConst ), 1, i+1 )
        plt.plot( camkii, label = d )
        plt.legend( )

    plt.savefig( '%s.png' % sys.argv[0] )
    plt.close( )
    

def main( ):
    create_figure( )

if __name__ == '__main__':
    main()
