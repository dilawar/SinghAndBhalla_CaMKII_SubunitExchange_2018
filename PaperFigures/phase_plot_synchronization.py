#!/usr/bin/env python

"""phase_plot_synchronization.py: 

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
import csv
import scipy.interpolate as sci
import scipy.optimize as sco

def f(x, k, x0, A, B ):
    v = A + B / ( 1 + np.exp( k * (x-x0) ) )
    return v

def interpolate( x, y ):
    f = sci.interp1d( x, y, 'cubic', fill_value = 'extrapolate' )
    img = [ ]
    Ds = np.logspace( 1e-16, 1e-12, 12 )
    ks = np.linspace( 10e-9, 100e-9, 10 )
    for k in ks:
        row = [ ]
        for D in Ds:
            kfkb = D / k / k
            v = f(kfkb)
            assert v < 1.0, v
            assert v > 0.0, v
            row.append( v )
        print( row )
        img.append( row )

    plt.imshow( img, interpolation = 'none', aspect = 'auto')
    plt.colorbar( )
    outfile = '%s.png' % sys.argv[0]
    plt.savefig( outfile )
    print( '[INFO] Done saving to %s' % outfile )

def fit_function( x, y, yerr ):
    plt.semilogx( x, y, '-o', label = 'original' )

    popt, pcov = sco.curve_fit( f, x, y, sigma = yerr )
    plt.semilogx( x, f(x, *popt ), '-*', label = 'fit' )

    plt.xlabel( r'$k_fk_b=\frac{D}{k^2}$. For $k=30\times 10^{-9}$nm' )
    plt.ylabel( 'Intermediate state distribution' )
    plt.legend( )

    outfile = '%s.png' % sys.argv[0]
    plt.savefig( outfile )
    print( '[INFO] Done saving to %s' % outfile )
    return popt


def main( ):
    data = np.loadtxt( './decay_of_intermediate_states.dat', delimiter = ','
            , skiprows = 1 
            )
    x = data[:,1]
    y = data[:,2]
    yerr = data[:,0]
    x = x / (30e-9 ** 2)

    ## Interpolation.
    #interpolate( x, y )
    #print( 'Done interpolation' )

    # Now we need to do 
    popt = fit_function( x, y, yerr )

    img = [ ]
    with open( 'data_sync_phase_plot.csv', 'w' ) as dataF:
        dataF.write( 'D,k,intermediate_state\n' )
        Ds = np.logspace( -16, -12, 10 )
        ks = np.linspace( 1e-9, 100e-9, 10 )
        for D in Ds:
            row = [ ]
            for k in ks:
                kfkb = D / k / k
                #print( D, k, kfkb )
                v = f(kfkb, *popt)
                dataF.write( '%g,%g,%f\n' % (D, k, v ) )
                assert v < 1.0, v
                assert v > 0.0, v
                row.append( v )
            img.append( row )

    print( 'Done writing data to file for plotting by TeX' )

    plt.figure()
    plt.imshow( img, interpolation = 'none', aspect = 'auto' )
    plt.colorbar( )
    plt.savefig( 'phase_plot.png' )
    print( 'Done plotting phase-plot' )


if __name__ == '__main__':
    main()

