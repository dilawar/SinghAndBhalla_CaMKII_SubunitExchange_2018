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


def sort_files(files):
    res = []
    for f in files:
        ftemp = f.replace( '++', ':')
        ftemp = ftemp.replace( '--', ',')
        ff = '.'.join(ftemp.split('.')[:-2])
        if '+D-' not in ff:
            ff += '+D-{}'
        try:
            fs = [tuple(x.split('-', 1)) for x in ff.split('+')]
            fs = [(x, myeval(y)) for (x, y) in fs]
            m = dict(fs)
            res.append((m, f))
        except Exception as e:
            print( "[WARN ] Failed to parse %s"  % f )
            
    res = sorted(res, key=lambda x: (x[0]['N'], x[0]['D']['x'], x[0]['D']['PP1']))
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
            , density=True
            , orientation='horizontal'
            )
    #  ax.set_xlim([0, 0.4])
    #  ax.locator_params(nbins=2, axis='x')

def is_bistable( hist, bins ):
    # assumes that binsize is 1.
    #  print( hist, hist[1:-1] )
    if hist[-1] < 0.05:
        return 0
    if hist[0] < 0.05:
        return 0

    if sum(hist[-2:]) > hist[-3] and hist[0] > hist[1]:
        return 1

    return 0

def process(files):
    try:
        m0, f0 = files[0]
    except Exception as e:
        print( "[WARN ] Ignoring %s. Error %s" % (files[0], e) )
        return 
        
    dfs, row = [], []
    row = []
    N, D, MeanCaM, StdCaM=[], [], [], []

    plt.figure(figsize=(12, 1.2*len(files)))
    grid = (len(files),9)
    for i, (m, f) in enumerate(files):
        if not os.path.exists(f):
            print( "[WARN ] File %s does not exists" % f)
            continue
            
        df = pd.read_csv(f, sep=' ')

        try:
            N.append(m['N'])
            D.append(math.log(m['D']['x'],10))
            MeanCaM.append(np.mean(df['CaMKII*']))
            StdCaM.append(np.std(df['CaMKII*']))
            if m0['N'] != m['N']:
                m0 = m
                dfs.append(row)
                row = [ ]
            row.append((m, df))
        except ValueError as e:
            pass

        ax1 = plt.subplot2grid(grid, (i,0), colspan=7)
        ax2 = plt.subplot2grid(grid, (i,7), colspan=1) 
        title = str(m)
        print('[INFO] %s' % title)
        plot_hist(m, df, ax2)
        ax1.plot( df['time'], df['CaMKII*'] )
        ax1.set_title(title, fontsize=6)

    # generate outdirectory given the group. 
    resfile = groupName( [x[1] for x in files] )
    outfile = '%s.png' % resfile
    plt.tight_layout(h_pad=0.01,w_pad=0.01)
    plt.savefig(outfile)
    plt.close()
    print("[INFO] Saved to %s" % outfile)

    #  dfs.append(row)

    plt.figure()
    groups = itertools.groupby( row, key = lambda x: x[0]['D']['x'] )
    img = []
    X, Y, Z,S, ZZ = [], [], [], [],[]

    final = pd.DataFrame()
    for gname, glist in groups:
        glist = list(glist)
        print( '-> Plotting for %s' % gname )
        print( '-> Total cols %d' % len(glist) )
        for m, traj in glist:
            if 0.0 in m['D'].values():
                continue

            vec = traj['CaMKII*']
            h, b = np.histogram( vec[100:]
                    , bins=m['CaM'], range=(0,m['CaM'])
                    , density=True)
            X.append( mylog(m['D']['PP1']) )
            Y.append( mylog(m['D']['x']) )
            Z.append( vec.mean() )
            S.append( vec.std() )
            ZZ.append( 10 * is_bistable(h, b) )

    final['Dpp1'] = X
    final['Dxy'] = Y
    final['Mean CaMKII'] = Z
    final['Std CaMKII'] = S
    final['is_bistable'] = ZZ
    outfile = '%s.csv' % dict_to_string(m)
    final.to_csv(  outfile, index = False )
    print( '[INFO] Saved to %s' % outfile )

    ax = plt.subplot(111)
    x, y = np.mgrid[max(X):min(X):10j,max(Y):min(Y):10j]
    z = griddata( (X,Y), Z, (x, y), method='linear')
    im = ax.contourf(x, y, z, 10 )
    plt.colorbar(im, ax=ax)
    ax.set_xlabel( r'$\log(D_{PP1})$' )
    ax.set_ylabel( r'$\log(D_{xy})$' )
    ax.set_title( 'Average activity. Black dot=bistable' )

    im = ax.scatter(X, Y, s=ZZ, color='black' )
    plt.savefig('test.png' )

    # Now create an image
    #img = []
    #for row in dfs:
    #    r = [np.mean(df['CaMKII*']) for m, df in row]
    #    img.append(r)

    #minCol = min( [ len(x) for x in img ] )
    #img = [x[:minCol] for x in img ]
    #print( img )

    #ax = plt.subplot2grid(grid, (5,0), rowspan=2, colspan=3)
    #im = ax.imshow( img, aspect='auto', interpolation='bicubic', cmap='seismic' )
    #plt.colorbar(im, ax = ax )

    #ax = plt.subplot2grid(grid, (5,4), rowspan=2, colspan=3)
    #assert len(D) == len(N)
    #assert len(N) == len(MeanCaM)

    #try:
    #    # Notice the odd complex number in np.mgrid.
    #    xi,yi = np.mgrid[min(D):max(D):19j,min(N):max(N):10j]
    #    zi = griddata( (D, N), MeanCaM, (xi, yi), method='linear' )
    #    im = ax.contour(xi, yi, zi, 20, cmap='seismic')
    #    im = ax.contourf(xi, yi, zi, 20, cmap='seismic')
    #    ax.set_title('contour', fontsize=6)
    #    ax.locator_params(nbins = 4, axis='x')
    #    ax.set_xlabel(r'log(D)', fontsize=6)
    #    ax.set_ylabel(r'\#Voxel (N)', fontsize=6)
    #    plt.colorbar(im, ax=ax)
    #except Exception as e:
    #    pass

    #res = pd.DataFrame()
    #res['N'] = N
    #res['D'] = D
    #res['Mean CaMKII'] = MeanCaM
    #res['Std CaMKII'] = StdCaM
    #res.to_csv( 'summary.csv', index = False )


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
