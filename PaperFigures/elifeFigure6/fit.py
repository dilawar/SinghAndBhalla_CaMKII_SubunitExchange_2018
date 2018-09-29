#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""fit.py: 

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
import scipy.optimize as sco
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.style.use( 'bmh' )
mpl.rcParams['axes.linewidth'] = 0.2
mpl.rcParams['lines.linewidth'] = 1.0
mpl.rcParams['text.latex.preamble'] = [ r'\usepackage{siunitx}' ]
mpl.rcParams['text.usetex'] = True


def split( tvec, vec, N = 7 ):
    # Split where tvec is multiple of 500
    splitAt = []
    for i, t in enumerate(tvec):
        if t % 500 == 0:
            splitAt.append( i )

    # Drop the last one
    splitAt.pop()

    ys = np.split( vec, splitAt )
    minL = min( [len(x) for x in ys] )
    # Ignore first 2 points from all trajectories since this is the time for
    # which input is applied.
    return [ y[2:minL] for y in ys ]

def split_and_normalize( tvec, vec, N = 7 ):
    ys = split( tvec, vec, N )
    ys = [ y / y.max() if y.max() > 1 else y for y in ys ]
    return ys

def single_exp( t, tau, A ):
    return A * np.exp( - t / tau )

def find_midpoint( ys ):
    maxY = ys.max()
    for i, y in enumerate( ys ):
        if y < maxY / 2:
            return i
    return -1

def find_tau( ys ):
    maxY = ys.max()
    for i, y in enumerate( ys ):
        if y < maxY * 0.63:
            return i
    return -1

def estimate_nonzero_part( ys ):
    for i, y in enumerate(ys):
        if y <= 0.01:
            return i
    return len(ys)

def main():
    seOFF = pd.read_csv('./CaM100_PP90000_voxels20_suOFF.dat_processed.dat', sep = ' ')
    seON = pd.read_csv('./CaM100_PP90000_voxels20_suON.dat_processed.dat', sep = ' ')

    gridSize = (3, 2)
    plt.figure( figsize=(6,6) )
    ax1 = plt.subplot2grid( gridSize, (0,0), colspan = 2 )
    ax2 = plt.subplot2grid( gridSize, (1,0), colspan = 1 )
    ax3 = plt.subplot2grid( gridSize, (1,1), colspan = 1 )
    ax4 = plt.subplot2grid( gridSize, (2,0), colspan = 1 )
    ax5 = plt.subplot2grid( gridSize, (2,1), colspan = 1 )
    
    seONCaMKII = seON['CaMKII*'].values
    seOFFCaMKII = seOFF['CaMKII*'].values
    seOFFt = seOFF['time'].values
    seONt = seON['time'].values

    # On this axis we plot the raw data.
    ax1.plot( seONt, seONCaMKII, label = '+SE' )
    ax1.plot( seOFFt, seOFFCaMKII, label = '-SE' )
    ax1.legend()
    ax1.set_xlabel( 'Time' )
    ax1.set_ylabel( 'Activity' )

    # Now split the trajectories at every 500 sec and take average.
    # Drop the first input.
    #seONCaMKIISlices = split_and_normalize( seONt, seONCaMKII )
    #seOFFCaMKIISlices = split_and_normalize( seOFFt, seOFFCaMKII )
    seONCaMKIISlices = split( seONt, seONCaMKII )
    seOFFCaMKIISlices = split( seOFFt, seOFFCaMKII )
    
    dt = 5
    avgY, stdY, ts = [], [], []
    for label, ys in zip( ['+SE', '-SE'], [seONCaMKIISlices, seOFFCaMKIISlices]):
        yerr = np.std(ys, axis=0)
        y = np.mean(ys, axis=0)
        avgY.append( y )
        stdY.append( yerr )
        t = np.arange(0, dt*(len(y)), dt)
        ts.append(t)
        try:
            ax2.errorbar(t, y, yerr=yerr, label=label)
        except Exception as e:
            print( label, len(t), len(y), len(yerr) )
            print( e )
        #  ax2.set_xlim(0, 500)
        ax2.legend()

    ax2.set_title( 'Split at every 500 sec' )

    # Fit curves.
    ## With SE
    t, y, yerr, ax = ts[0], avgY[0], stdY[0], ax4
    tau0 = t[find_tau(y)]
    print( f"[INFO ] init t0={tau0}" )
    N = estimate_nonzero_part(y)
    assert N > 1, N
    popt, pcov = sco.curve_fit(
            lambda t, x: single_exp(t, x, y.max())
            , t[:N], y[:N]
            , p0 = [tau0]
            , sigma=yerr[:N]+1e-20
            , absolute_sigma=True
            #  , method = 'trf'
            )
    ax.plot( t, single_exp(t, *popt, y.max()), label = label)
    ax.fill_between(t, y+yerr, y-yerr, alpha=0.3)
    ax.plot(t, y, lw=2, label = r'$e^{-t/%.3f}$' % popt)
    ax.legend()
    print( popt )

    ## Without SE
    t, y, yerr, ax = ts[1], avgY[1], stdY[1], ax5
    tau0 = t[find_tau(y)]
    print( f"[INFO ] init t0={tau0}" )
    N = estimate_nonzero_part(y)
    assert N > 1, N
    popt, pcov = sco.curve_fit( 
            lambda t, x: single_exp(t, x, y.max())
            , t[:N], y[:N]
            , p0 = [tau0]
            #  , sigma=yerr[:N]
            #  , absolute_sigma=True
            #  , method = 'trf'
            )
    ax.plot( t, single_exp(t, *popt, y.max()), label = label)
    #  ax.errorbar( t, y, yerr=yerr, alpha=0.5)
    ax.fill_between(t, y+yerr, y-yerr, alpha=0.3)
    ax.plot(t, y, lw=2, label = r'$e^{-t/%.3f}$' % popt)
    ax.legend()

    # Add fitted curves.
    plt.suptitle( 'Figure 6- eLife' )
    plt.tight_layout( rect = (0,0,1,0.95) )
    plt.savefig( '%s.pdf' % __file__ )


if __name__ == '__main__':
    main()

