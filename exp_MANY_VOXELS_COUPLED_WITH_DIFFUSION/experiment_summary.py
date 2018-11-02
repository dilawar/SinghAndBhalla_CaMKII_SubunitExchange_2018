#!/usr/bin/env python
    
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
import scipy.stats as _stats
import helper
import math

def _smooth(y, N):
    win = np.ones(N)/N
    return np.convolve(y, win, 'same' )

def kl_div( P, Q ):
    # distance from Q to P. Q is reference.
    d = 0
    for p, q in zip(P, Q):
        if p == 0:
            continue
        if q == 0:
            continue
        d += p * math.log(p/q)
    return d

def _filename_to_dict( f ):
    f = os.path.basename(f).split( '.' )[0]
    keys, vals = zip(*[ x.split('-', 1) for x in f.split( '+' )])
    vals = [ float(x) for x in vals ]
    return dict(zip(keys, vals))

def _histogram( y):
    h, b = np.histogram(y, density = True, range=(0,6) )
    return h

def _trajectory_stats( y ):
    residenceTime  = helper.compute_residence_time(y, [0,6], [1,1])
    residenceTime['transitions'] = 1 - sum(residenceTime.values())
    return residenceTime

def is_bistable( y ):
    rd = _trajectory_stats(y)
    ratio = rd[6] / (rd[0]+rd[6])
    if rd[0] > 1e-2 and rd[6] > 1e-2:
        if rd['transitions'] < rd[0] + rd[6]:
            return True, ratio
    return False, ratio

def compare( ref, others):
    #  refH = _histogram_camkii(ref)
    yref = ref['CaMKII*'].values
    aref, bref = is_bistable(yref)
    fig = plt.figure(figsize=(15,15))
    grid = 8, 7
    N = int(len(others) ** 0.5) 
    #  hGrid = ImageGrid(fig, 211, nrows_ncols=(N, N), axes_pad=0.1)
    boxes = [ ]
    X, Y, Z1, Z2, ksD, ksP, KL = [], [], [], [], [], [], []
    for i, (f, df) in enumerate(others):
        #  print( "[INFO ] Plotting %s" % f)
        d = _filename_to_dict(f)
        y = df['CaMKII*']

        _D, _p = _stats.ks_2samp(y, yref)
        print( d, _D, _p )
        print( y.min(), y.mean(), y.max(), yref.min(), yref.mean(), yref.max() )
        ksD.append(_D)
        ksP.append(_p)

        X.append( d['Dpp'] )
        Y.append( d['Dsub'] )
        a, b = is_bistable(y)
        x = 1 if a else 0
        Z1.append( abs(b - bref)/bref )
        Z2.append(10*x)
        h, href = _histogram(y), _histogram(yref)
        _kl = kl_div(h, href)
        KL.append( _kl )

        plt.subplot(*grid, i+1)
        plt.hist(y, range=(0,6), bins=7, cumulative=1, histtype='step')
        plt.hist(yref, range=(0,6), bins=7, cumulative=1, histtype='step')
        plt.title( str(d) + '\n' + 'KS = %g, KL div=%g' % (_p,_kl), fontsize=8 )

    plt.subplot(*grid, len(others)+1)
    plt.hist(yref, range=(0,6), bins=7 )
    plt.title( 'Well-mixed' )
    plt.tight_layout()
    plt.savefig( 'hists.png' )
    plt.close()

    plt.figure()
    ax = plt.subplot(221)
    ax.set_xscale( 'log' )
    ax.set_yscale( 'log' )
    plt.tricontourf(X, Y, Z1)
    plt.colorbar()
    plt.xlabel( r'$D_{pp1}$' )
    plt.ylabel( r'$D_{sub}$' )
    plt.scatter(X, Y, s=Z2 )

    ax = plt.subplot(222)
    ax.set_xscale( 'log' )
    ax.set_yscale( 'log' )
    plt.tricontourf(X, Y, KL )
    plt.colorbar()
    plt.title( 'KL divergence' )
    plt.xlabel( r'$D_{pp1}$' )
    plt.ylabel( r'$D_{sub}$' )
    plt.tight_layout()

    ax = plt.subplot(223)
    ax.set_xscale( 'log' )
    ax.set_yscale( 'log' )
    plt.tricontourf(X, Y, ksP )
    plt.colorbar()
    plt.title( 'KS Test (p value)' )
    plt.xlabel( r'$D_{pp1}$' )
    plt.ylabel( r'$D_{sub}$' )

    plt.tight_layout()
    plt.savefig( 'summary.png' )

    # final csv.
    df = pd.DataFrame()
    df['Dpp'] = X
    df['Dsub'] = Y
    df['KL_divergence'] = KL
    df['ks_p'] = ksP
    df['is_bistable'] = Z2
    df['mean_activity'] = Z1
    df.to_csv( 'summary_camkii6.csv', index = False )


def main():
    ref = pd.read_csv( './ref.dat_processed.dat', sep=' ' )
    data = []
    files = glob.glob( './Dsub-*_processed.dat' )
    files = sorted( files, key=lambda x: list(_filename_to_dict(x).values()))
    for f in files:
        d = _filename_to_dict(f)
        data.append( (f, pd.read_csv(f, sep=' ')) )
    compare(ref, data)

if __name__ == '__main__':
    main()
