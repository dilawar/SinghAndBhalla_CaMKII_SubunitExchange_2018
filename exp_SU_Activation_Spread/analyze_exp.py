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
#  mpl.style.use('ggplot')
plt.rc('font', size=8)

#  import matplotlib.mlab
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import itertools
import glob
import math

meanCaMKII_, stdCaMKII_           = [], []
times_                            = []
Dxy_, meanRiseTime_, stdRiseTime_ = [], [], []
meanRateRise_, stdRateRise_       = [], []
meanStartTime_, stdStartTime_     = [], []
df_                               = pd.DataFrame()
maxN_                             = 18

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

def linear_fit(x, y, maxN=18):
    try:
        return linear_fit_helper(x, y, maxN)
    except Exception as e:
        return math.nan

def linear_fit_helper(x, y, thres=2, maxN=18):
    # Compute the time it takes to reach 20% to 80% of max.
    ymin, ymax = 2, 16
    if y.max() < 5:
        return math.nan

    if y.max() < ymax:
        #  print( '[INFO] Computing rate to compute time' )
        tvec = x.copy()
        yvec = y.copy()
        #  yvec[ yvec <= 1 ] = 0
        yvec[ yvec >= ymin ] = 0
        #  print( yvec, y )
        i, j = np.nonzero(yvec)[0][0], np.idxmax(yvec)
        m, c = np.polyfit(tvec[i:j], yvec[i:j], 1)
        return ymax/m 

    t0 = 0
    for tt, yy in zip(x, y):
        if yy >= ymax:
            return tt - t0

    return math.nan

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
    # Compure time to reach from 10% to 90% and also the time to reach 10%.
    startT, endT = 0, 0
    midVal, curT, curVal = ymax // 2, 0, 0
    minVal, maxVal = math.ceil(0.1*ymax), math.floor(0.9*ymax)

    for t, y in zip(tvec,yvec):
        if startT == 0:
            if y >= minVal:
                startT = t
        if y >= midVal:
            curT, curVal = t, y
        if y >= maxVal:
            endT = t
            break

    # Means that till the end of trajectory we can't reach 10% value.
    if startT == 0:
        startT = tvec.max()

    if endT == 0:
        if curT > 0:
            # estimate the time to reach maxVal to 90%.
            return startT, (curT-startT)/(curVal-minVal)*(0.8*ymax)
        # else we can't estimate.
        return startT, math.nan
    assert endT > startT, (endT, startT)
    return startT, (endT - startT)

def get_data_and_plot( files, plot = True ):
    row = []
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

    print( tvec.shape, meanTrace.shape, stdTrace.shape, gname)
    df_['time'] = tvec
    df_[ 'mean_camkii_%s' % gname] = meanTrace
    df_[ 'std_camkii_%s' % gname] = stdTrace

    meanCaMKII_.append( meanTrace )
    stdCaMKII_.append( stdTrace )
    tvec = tvec/3600.0
    times_.append(tvec)

    fax.plot(tvec, meanTrace, lw=2, label = r'$D_x=%g$' %gname)
    fax.legend( fontsize=4 )

    # fit plots.
    ts = [linear_fit(tvec, y) for y in yvecs]
    t0 = linear_fit(tvec, meanTrace)
    #  m1 = np.mean(ts, axis=0)
    m1std = np.std(ts, axis=0)
    meanRateRise_.append(t0)
    stdRateRise_.append(m1std)
    for yvec in yvecs:
        ax.plot( tvec, yvec, lw=1, alpha = 0.7 )

    ax.plot(tvec, meanTrace, lw = 2, color='black' )

    #ax.fill_between( tvec, meanTrace - stdTrace, meanTrace + stdTrace,
    #        alpha=0.3 )
    #  ax.axvline( t0 )
    ax.set_ylim( [0, maxN_ ] )
    ax.set_xlabel( 'Time (h)' )
    #  ax.legend()
    ax.set_title( r'$D_x=D_y=%g$' % gname, fontsize = 8 )

    # summary data
    Dxy_.append( float(gname) )
    riseTimesWithStartTimes = [compute_rise_time(tvec, x) for x in yvecs]
    startTimes, riseTimes = zip( *riseTimesWithStartTimes )

    meanRiseTime_.append(np.nanmean(riseTimes, axis=0))
    stdRiseTime_.append(np.nanstd(riseTimes, axis=0))

    meanStartTime_.append(np.nanmean(startTimes, axis=0))
    stdStartTime_.append(np.nanstd(startTimes, axis=0))


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
        plot_for_df(tvec, yvecs, ax, fax, gname)
            
    fax.set_xlim(0, 3.5)
    fax.set_title( 'Combined' )

    print( 'Dxy', Dxy_ )
    print( '<RT>', meanRiseTime_ )
    print( '<ST>', meanStartTime_ )

    # The final plot which shows both rate of activation and start time.
    x, y, yerr = Dxy_, meanRiseTime_, stdRiseTime_
    ax = plt.subplot( nRows, 2, 2*nRows )
    ax.set_xlim( [1e-21, 1e-11] )
    ax.errorbar(x[1:], y[1:], yerr[1:], fmt='-o', color = 'red', label = 'RT' )
    ax.set_xscale( 'log' )
    ax.set_xlabel( r'$D_x=D_y$ $m^2/s$' )
    ax.set_ylabel( r'Rise Time (hour)' )
    ax.legend()

    x1, y1, yerr1 = Dxy_, meanStartTime_, stdStartTime_
    ax1 = ax.twinx()
    ax1.errorbar(x1[1:], y1[1:], yerr1[1:], fmt='-x', color = 'blue', label = 'ST' )
    ax1.set_xscale( 'log' )
    ax1.set_xlabel( r'$D_x=D_y$ $m^2/s$' )
    ax1.set_ylabel( r'Start Time (hour)' )
    ax1.legend()
    ax1.set_title( 'Activation Rate' ) 

    plt.suptitle( 'Rise time of CaMKII activity (n=%d for each plot)' % len(groups[0][1]))
    plt.tight_layout( rect=(0,0,1,0.95) )
    plt.savefig('summary.png' )
    plt.close()

    # write final data.
    riseDF = pd.DataFrame()
    riseDF['Dxy'] = x
    riseDF['Mean RiseTime'] = y
    riseDF['Std RiseTime'] = yerr
    riseDF['Mean StartTime'] = y1
    riseDF['Std StartTime'] = yerr1
    riseDF.to_csv( 'summary_risetime.csv', index = False )
    df_.to_csv( 'mean_std_risetime_starttime.csv', index = False )
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
