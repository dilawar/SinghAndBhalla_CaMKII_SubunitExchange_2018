#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""analyze_exp.py:

"""

__author__ = "Dilawar Singh"
__copyright__ = "Copyright 2017-, Dilawar Singh"
__version__ = "1.0.0"
__maintainer__ = "Dilawar Singh"
__email__ = "dilawars@ncbs.res.in"
__status__ = "Development"

import sys
import os
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.margins(x=0.1, y=0.1)
mpl.style.use('ggplot')
plt.rc('font', size=8)

import matplotlib
#  import matplotlib.mlab
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import itertools
import glob
import math
from collections import defaultdict, OrderedDict

meanCaMKII, stdCaMKII = [], []
times = []
Dxy, meanRiseTime, stdRiseTime = [], [], []
meanRateRise, stdRateRise = [], []
df = pd.DataFrame()

def myeval(x):
    try:
        return eval(x)
    except Exception as e:
        return x

def mylog(val, base=10):
    if val == 0.0:
        return -20
    return math.log(val, base)

def groupName( names ):
    import hashlib
    txt = ''.join( list(names) )
    return hashlib.md5(txt.encode('utf-8')).hexdigest()

def dict_to_string( d ):
    m= []
    for k, v in d.items():
        if isinstance(v, dict):
            s = dict_to_string(v)
        else:
            s = str(v)
        m.append( '%s:%s' % (k,s) )
    return '+'.join(m)

def linear_fit(x, y, thres=2, maxN=18):
    tvec = x.copy()
    yvec = y.copy()
    ymean = int(np.mean( y ))
    #  yvec[ yvec <= max(2, ymean - 10) ] = 0
    #  yvec[ yvec >= 15 ] = 0
    yvec[ yvec > ymean ] = 0
    #  print( yvec, y )
    i, j = np.nonzero(yvec)[0][0], np.argmax(yvec)
    return np.polyfit(tvec[i:j], yvec[i:j], 1)

def exp_fit(x, y, maxn):
    import scipy.optimize as sco

    def decay(x, k):
        return maxn * (1-np.exp(-k*x))

    y[ y <= 1 ] = 0
    i = np.nonzero(y)[0][0]
    p0, c0 = sco.curve_fit(decay, x[i:], y[i:])
    return p0[0], maxn


def sort_files(files):
    res = []
    for f in files:
        ftemp = f.replace( '++', ':')
        ftemp = ftemp.replace( '--', ',')
        ff = '.'.join(ftemp.split('.')[:-2])
        if '+D-' not in ff:
            ff += '+D-{}'
        fs = [tuple(x.split('-', 1)) for x in ff.split('+')]
        fs = [(x, myeval(y)) for (x, y) in fs]
        m = dict(fs)
        res.append((m, f))
    res = sorted(res, key=lambda x:(x[0]['N'], x[0]['D']['x'], x[0]['D']['PP1']))
    return res

def get_data(camkii, su, files):
    dfs = []
    for kv, df in files:
        if int(kv['camkii']) == camkii and kv['su'] == su:
            dfs.append((kv, df))
    return dfs

def plot_hist(m, df, ax):
    camkii = df['CaMKII*']
    ax.hist(camkii, color='blue'
            , bins=range(0,int(camkii.max())+2)
            #  , density=True
            , normed = True
            , orientation='horizontal'
            )

def is_bistable( hist, bins ):
    # assumes that binsize is 1.
    #  print( hist, hist[1:-1] )
    if hist[0] > 5e-3 and hist[1] < hist[0]:
        return 1
    return 0

def compute_rise_time( tvec, yvec, ymax = 18 ):
    startT, endT = 0, 0
    for t, y in zip(tvec,yvec):
        if startT == 0:
            if y >= 0.1 * ymax:
                startT = t
        if y >= 0.9 * ymax:
            endT = t
            break

    if endT == 0:
        return math.nan
    assert endT > startT, (endT, startT)
    
    return (endT - startT)

def get_data_and_plot( files, plot = True ):
    dfs, row = [], []
    N, D, MeanCaM, StdCaM=[], [], [], []
    plt.figure(figsize=(12, 1.2*len(files)))
    grid = (len(files),9)
    m0, f0 = files[0]
    for i, (m, f) in enumerate(files):
        if not os.path.exists(f):
            print( "[WARN ] File %s does not exists" % f)
            continue
            
        df = pd.read_csv(f, sep=' ')

        N.append(m['N'])
        D.append(m['D']['x'])
        MeanCaM.append(np.mean(df['CaMKII*']))
        StdCaM.append(np.std(df['CaMKII*']))
        row.append((m, df))
        if not plot:
            continue

        ax1 = plt.subplot2grid(grid, (i,0), colspan=7)
        ax2 = plt.subplot2grid(grid, (i,7), colspan=1) 
        title = str(m)
        print('[INFO] %s' % title)
        plot_hist(m, df, ax2)
        ax1.plot( df['time'], df['CaMKII*'] )
        ax1.set_title(title, fontsize=6)

    if plot:
        # generate outdirectory given the group. 
        resfile = groupName( [x[1] for x in files] )
        outfile = '%s.png' % resfile
        plt.tight_layout(h_pad=0.01,w_pad=0.01)
        plt.savefig(outfile)
        plt.close()
        print("[INFO] Saved to %s" % outfile)

    return row

def plot_for_df( tvec, yvecs, ax, fax, gname ):
    meanTrace = np.mean(yvecs, axis=0)
    stdTrace = np.std(yvecs, axis=0)
    df[ '%s_mean_camkii' % gname] = meanTrace
    df[ '%s_std_camkii' % gname] = stdTrace
    meanCaMKII.append( meanTrace )
    stdCaMKII.append( stdTrace )
    tvec = tvec/3600.0
    times.append(tvec)
    fax.plot(tvec, meanTrace, lw=2, label = r'$D_x=%g$' %gname)
    fax.legend( fontsize=4 )
    ax.plot(tvec, meanTrace)

    # fit plots.
    try:
        m, c = linear_fit(tvec, meanTrace)
        #  rates = [linear_fit(tvec, y) for y in yvecs]
        rates = [ exp_fit(tvec, y, max(10, np.mean(y))) for y in yvecs ]
        m1, c1 = np.mean(rates, axis=0)
        m1std, c1std = np.std(rates, axis=0)
        #  ax.plot(tvec, m1*tvec+c1)
        maxn = max(10, np.mean( meanTrace[:-100] ))
        k, maxN = exp_fit(tvec, meanTrace, maxn)
        ax.plot( tvec, maxN*(1-np.exp(-k*tvec)))
        meanRateRise.append(m1)
        stdRateRise.append(m1std)
    except Exception as e:
        print( "[WARN ] Failed to compute fit with error %s" % e)
        return 0, 0

    ax.fill_between( tvec, meanTrace - stdTrace, meanTrace + stdTrace,
            alpha=0.3 )
    ax.set_ylim( [0, 18 ] )
    ax.set_xlabel( 'Time (h)' )
    #  ax.legend()
    ax.set_title( r'$D_x=D_y=%g$' % gname, fontsize = 8 )

    # summary data
    Dxy.append( float(gname) )
    riseTimes = [compute_rise_time(tvec, x) for x in yvecs]
    meanRiseTime.append( np.nanmean(riseTimes, axis=0))
    stdRiseTime.append( np.nanstd(riseTimes, axis=0))


def process(files):
    row = get_data_and_plot( files, plot = False )
    groups = itertools.groupby( row, key = lambda x: x[0]['D']['x'] )
    groups = [ (x, list(y)) for x, y in groups ]

    plt.figure( figsize=(6, 1.1*len(groups)) )
    nRows = math.ceil(len(groups)/2.0) + 1
    fax = plt.subplot( nRows, 2, 1 )
    for i, (gname, glist) in enumerate(groups):
        yvecs = [ x['CaMKII*'] for m, x in glist ]
        ax = plt.subplot(nRows, 2, i+2)
        tvec = glist[0][1]['time']
        try:
            plot_for_df(tvec, yvecs, ax, fax, gname)
        except Exception as e:
            print( "[WARN ] Failed to plot with error %s." % e )
            continue

    fax.set_xlim(0, 3.5)
    fax.set_title( 'Combined' )

    # The final plot.
    #  plt.figure()
    x, y, yerr = np.array(Dxy), np.array(meanRateRise), np.array(stdRateRise)
    ax = plt.subplot( nRows, 2, 2*nRows )
    ax.semilogx(x, y)
    ax.set_xlabel( r'$D_x=D_y$ $m^2/s$' )
    ax.set_ylabel( r'\# per hour' )
    ax.set_title( 'Activation Rate' ) 
    ax.fill_between( x, y-yerr, y+yerr, alpha = 0.3 )

    plt.suptitle( 'Rise time of CaMKII activity (n=%d for each plot)' % len(groups[0][1]))
    plt.tight_layout( rect=(0,0,1,0.95) )
    plt.savefig('summary.png' )
    plt.close()

    # write final data.
    riseDF = pd.DataFrame()
    riseDF['Dxy'] = Dxy
    riseDF['Mean RiseTime'] = meanRiseTime
    riseDF['Std RiseTime'] = stdRiseTime
    riseDF.to_csv( 'summary_risetime.csv', index = False )
    df.to_csv( 'mean_std_rise_time.csv', index = False )
    print( "[INFO ] Wrote data tp summary_risetime.csv and mean_std_rise_time.csv." )


def main( files ):
    groups = sort_files(files)
    process(groups)

if __name__ == '__main__':
    pat = '*_processed.dat'
    files = [ ]
    if len(sys.argv) == 2:
        pat = sys.argv[1]
    elif len(sys.argv) > 2:
        files = sys.argv[1:]
    else:
        print( "[INFO ] Using pat %s" % pat )
        files = glob.glob(pat)
    main( files )
