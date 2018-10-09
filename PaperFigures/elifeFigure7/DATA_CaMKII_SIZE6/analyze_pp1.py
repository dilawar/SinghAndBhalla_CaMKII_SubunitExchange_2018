#!/usr/bin/env python

import sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import scipy.stats as stats
import scipy.signal as sig
import matplotlib.pyplot as plt
mpl.style.use( 'bmh' )
mpl.rcParams['axes.linewidth'] = 0.2
mpl.rcParams['lines.linewidth'] = 1.0
mpl.rcParams['text.latex.preamble'] = [ r'\usepackage{siunitx}' ]
mpl.rcParams['text.usetex'] = False

def smooth( vec, N = 180 ):
    window = np.ones( N ) / N
    return np.convolve(vec, window, 'same')

def process( files ):
    basefile = files[0]
    base = pd.read_csv( basefile, sep = ' ' )
    baseCaM = base['CaMKII*']
    toplot = [ ]
    for i, f in enumerate(files):
        data = pd.read_csv( f, sep = ' ' )
        t = data['time']
        cam = data[ 'CaMKII*']
        pp1 = data['PP1']
        corr = sig.correlate(smooth(cam.data), smooth(baseCaM.data))
        if np.log10( corr.mean() ) < 4:
            print('x', end='')
            continue
        toplot.append( (f, t, cam, pp1) )

    plt.figure( figsize=(12, len(toplot)) )
    for i, (f, t, cam, pp) in enumerate(toplot):
        ax1 = plt.subplot(len(toplot), 2, 2*i+1)
        ax1.plot(t, cam, alpha=0.5 )
        ax2 = plt.subplot(len(toplot), 2, 2*i+2)
        ax2.plot(t, pp, alpha=0.5, label=f )
        ax2.legend( fontsize=6 )

    plt.tight_layout()
    plt.savefig( '%s.png' % sys.argv[0] )


def main():
    files = sys.argv[1:]
    print( "[INFO ] Analyzing files %s" % files )
    process( files )


if __name__ == '__main__':
    main()
