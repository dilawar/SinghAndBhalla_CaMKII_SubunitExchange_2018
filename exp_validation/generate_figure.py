"""generate_figure.py: 

Generate figure for this experiment.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
try:
    mpl.style.use( 'ggplot' )
except Exception as e:
    pass
mpl.rcParams['axes.linewidth'] = 0.1
# plt.rc('text', usetex=True)
plt.rc('font', family='serif')

import numpy as np

sys.path.append( '..' )
import helper 
import glob
import pandas as pd
import re
import operator
import itertools

args_ = None

# See https://stackoverflow.com/questions/45476509/group-list-of-tuples-efficiently
def groupby( a ):
    b = [(k, [x for _, x in g]) for k, g 
            in itertools.groupby(a, operator.itemgetter(0))]
    return b

def find_files( x, nv, d = '_data' ):
    g1Expr = 'camk%d\_.+voxel%d.+suON.+\_processed\.dat$' % (x,nv)
    g2Expr = 'camk%d\_.+voxel%d.+suOFF.+\_processed\.dat$' % (x,nv)
    withSu, withoutSu = [ ], [ ]
    for d, sd, fs in os.walk( '_data' ):
        for f in fs:
            if re.match( r'%s' % g1Expr, f ):
                withSu.append( os.path.join( d, f ) )
            if re.match( r'%s' % g2Expr, f ):
                withoutSu.append( os.path.join( d, f ) )
    return sorted( withSu ), sorted( withoutSu )


def plot_errorbar( xs, ys, ax, label = ' ' ):
    y = zip( xs, ys )
    gy = groupby( y )
    if len( gy ) < 1:
        print( 'Empty data. Ignoring ...' )
        return [], [], []
    x1, y1 = zip( *gy )
    ys = [ np.mean(x) for x in y1 ]
    yerr = [ np.std(x) for x in y1 ]
    ax.errorbar( x1, ys, yerr=yerr, label = label )
    ax.legend( )
    return x1, ys, yerr

def analyze( files ):
    global args_
    if len( files ) < 1:
        print( '[WARN] No datafile found' )
        return [], [], []

    results = [ ]
    for f in files:
        print( '- Doing %s' % f )
        pp1X = re.search( r'pp(\d+)\_', f )
        pp1 = int( pp1X.group( 1 ) )
        d = pd.read_csv( f, sep = ' ', comment = '#' )
        t = d[ 'time' ]
        yvec = d[ 'CaMKII*' ]
        trans = helper.compute_transitions( yvec, [0,args_.camkii], [1,1] )
        kt = helper.compute_karmer_time( yvec, [0,args_.camkii], [1,1] )
        nTrans = len( trans )
        results.append( ( pp1, nTrans, kt[args_.camkii] ) )

    results = sorted( results )
    pp1Vec = map( lambda x: x[0], results )
    tON = map(lambda x: x[-1], results)
    trans = map(lambda x: x[-2], results)
    return pp1Vec, tON, trans

def main( args ):
    global args_
    args_ = args
    nv = args.voxels
    x = args.camkii
    withSUFs, withoutSUFs = find_files( x, nv )

    r1 = analyze( withSUFs )
    r2 = analyze( withoutSUFs )

    ax1 = plt.subplot( 211 )
    tonSU = plot_errorbar( r1[0], r1[1], ax1, label = 'With SU' )
    tonWSU = plot_errorbar( r2[0], r2[1], ax1, label = 'Without SU' )
    # Write these analysis to csv file so it can be plotted by python later.
    withSu = pd.DataFrame( )
    withoutSu = pd.DataFrame( )
    for df, d in zip( [withSu, withoutSu], [tonSU, tonWSU] ):
        df[ 'tON_PP1' ] = d[0]
        df[ 'tON' ] = d[1]
        df[ 'tONErr' ] = d[2] 

    ax1.set_title( 'Time spent in ON state' )

    ax2 = plt.subplot( 212, sharex = ax1 )
    tranSU = plot_errorbar( r1[0], r1[2], ax2, label = 'With SU' )
    tranWSU = plot_errorbar( r2[0], r2[2], ax2, label = 'Without SU' )
    ax2.set_title( 'Number of transitions' )
    ax2.legend( )

    plt.tight_layout( pad = 3 )
    plt.savefig( '%s.png' % sys.argv[0] )
    print( '[INFO] Saved data to %s.png' % sys.argv[0] )

    # Write these analysis to csv file so it can be plotted by python later.
    for df, d in zip( [withSu, withoutSu], [tranSU, tranWSU] ):
        df[ 'trans_PP1' ] = d[0]
        df[ 'trans' ] = d[1]
        df[ 'transErr' ] = d[2] 

    if args.outfile is None:
        args.outfile = 'camkii%d_voxel%d' % (args.camkii, args.voxels)

    outfiles = [ args.outfile + x for x in [ '_su.dat', '_wsu.dat' ] ]
    for df, f in zip( [ withSu, withoutSu ], outfiles ):
        df.to_csv( f, sep = ' ', index = False )
        print( '[INFO] Wrote data to %s' % f )


if __name__ == '__main__':
    import argparse
    # Argument parser.
    description = '''Genearte figure'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--camkii', '-c'
        , required = False
        , default = 8
        , type = int
        , help = 'System size (#CaMKII rings)'
        )
    parser.add_argument('--voxels', '-v'
        , required = False
        , default = 1
        , type = int
        , help = 'Number of voxels. (default 1)'
        )
    parser.add_argument('--outfile', '-o'
        , required = False
        , help = 'Data file name. Suffix _su and _wsu will be added.'
        )
    class Args: pass 
    args = Args()
    parser.parse_args(namespace=args)
    main( args )
