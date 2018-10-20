#!/usr/bin/env python
"""plot_data.py: 
"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.optimize as sco
import scipy.spatial as scs

maxF_ = 100
tauMean8um_ = 0


def exp_fit( t, tau ):
    return maxF_ * (1-np.exp(-t/tau))

def fit_with_exp(t, y):
    popt, pcorr = sco.curve_fit( exp_fit, t, y, p0=[50] )
    return popt[0]

def to_glob( cm, rg, rl ):
    if type(cm) == float:
        cm = '%s' % cm
    rg, rl = '%.6f'%rg, '%.6f'%rl
    rg = rg[:-1] + '*'
    rl = rl[:-1] + '*'
    return '../UsingChemReacs/CM%s_rg%s_rl%s.csv' % (cm, rg, rl)

def plot_contour(C, ax = None):
    # templ 
    if ax is None:
        ax = plt.subplot(325)
    for c in C.collections:
        p = c.get_paths()[0]
        v = p.vertices
        ax.loglog( v[:,0], v[:,1] )

def plot_phase_plot_rlrg_tau( df, ax, tau, err=0.2):
    ax.set_xscale( 'log' )
    ax.set_yscale( 'log' )
    vmin = df['tau'].min()
    vmax = df['tau'].max()
    X, Y, Z = df['rgain'], df['rlose'], df['tau']
    im = ax.tricontourf(X, Y, Z, 10
            , vmin=vmin, vmax=vmax, alpha = 0.5
            )
    plt.colorbar( im, ax = ax )
    C = ax.tricontourf(X, Y, Z, 10
            , vmin=vmin, vmax=vmax, alpha = 0.5
            )

    plot_contour( C )

    d = df[ df['tau'] < (1+err)*tau ]
    d = d[ d['tau'] > (1-err)*tau ]
    X, Y, Z = d['rgain'], d['rlose'], d['tau']
    print( Z.min(), Z.max(), Z.mean() )
    ax.scatter( X, Y, c=Z
            , marker='o'
            , vmin=vmin, vmax=vmax
            )
    ax.set_xlabel( 'rate gain' )
    ax.set_ylabel( 'rate lose' )
    ax.set_title( r'$\tau$, Point ($%.2f \pm$%.1f%%)' % (tau,err*100) )

    # return the dataframe with good values.
    return d

def plot_experimental_data():
    plot_fig2c()
    plot_fig3c()

def plot_fig3c():
    global tauMean8um_
    df = pd.read_csv('./figure_3c.csv')
    plt.subplot(321)
    y1 = df['half-life1'].values
    y2 = df['half-life2'].values

    plt.plot( df['time'].values, y1, 'bo' )
    plt.plot( df['time'].values, y2, 'bo' )
    
    x = df['time'].values
    y = 0.5*y1 + 0.5*y2
    popt, pcorr = sco.curve_fit(exp_fit, x, y, p0=[60])
    plt.plot( df['time'], exp_fit(df['time'], *popt), 'red'
            , label = r'$%d(1-e^{-t/%.2f})$' % (maxF_, popt[0])
            )
    #  plt.legend( bbox_to_anchor = (1,1), loc = 2, fontsize=8 )
    plt.legend( fontsize=8 )
    plt.ylim( 0, 100 )
    plt.xlabel( 'Time (min)' )
    plt.ylabel( '% Co-localization' )
    plt.title( 'Figure 3C' )
    tauMean8um_ = popt[0]

    # Now filter trajectories which are close to this range for this
    # concentration range.
    ax = plt.subplot(322)
    df = pd.read_csv('../UsingChemReacs/summary_CM8e-3.csv')
    validRange = plot_phase_plot_rlrg_tau( df, ax, tauMean8um_ )
    assert len(validRange) >0

    fs8u, fs1u = [], []
    for i, row in validRange.iterrows():
        rg, rl = row['rgain'], row['rlose']
        fs8u.append((to_glob('8e-3', rg, rl),rg,rl))
        fs1u.append((to_glob('1e-3', rg, rl),rg,rl))

    errors = []
    for (f1,rg,rl), (f8,rg,rl) in zip(fs1u, fs8u):
        try:
            f1 = glob.glob(f1)[0]
            f8 = glob.glob(f8)[0]
            d1 = pd.read_csv( f1 )
            d8 = pd.read_csv( f8 )
        except Exception as e:
            print( "[WARN ] Failed %s" % e )
            continue

        # fit with tau
        err = compute_error(d1)
        #  print( 'Error %s' % err )
        errors.append( (err, d1, d8, rg, rl) )

    best = sorted(errors)[1]
    err, d1, d8, rg, rl = best
    t1, y1 = d1['time'], d1['colocalization_perc']
    t8, y8 = d8['time'], d8['colocalization_perc']
    ax = plt.subplot(324)
    ax.plot(t8, y8, label = 'Exp')
    ax.plot(t1, y1, lw = 0.5, label = 'Exp' )
    ax.legend()
    ax.set_title( 'rate gain=%g, rate lose=%g' % (rg, rl) )

def compute_error( df1u ):
    df2c1u = fig2c_data( ['Time', 'mean_1_37'] )
    df2c8u = fig2c_data( ['Time', 'mean_8_37'] )
    tau1umSim = fit_with_exp( df1u['time'], df1u['colocalization_perc'] )
    tau1umExp = fit_with_exp( df2c1u['Time'], df2c1u['mean_1_37'] )
    return abs(tau1umExp - tau1umSim)/tau1umExp

def fig2c_data( colnames ):
    df = pd.read_csv( './figure_2.csv' )
    if colnames:
        df = df[ colnames ].dropna()
    return df

def plot_fig2c():
    colors_ = [ 'red', 'blue' ]
    df = fig2c_data([])
    plt.subplot(323)
    for i, c in enumerate(['8_37', '1_37']):
        col = 'mean_%s' % c
        colErr = 'std_%s' % c
        d = df[ ['Time', col, colErr] ].dropna()
        t, y, yerr = d['Time'], d[col], d[colErr]
        print( "[INFO ] Plotting %s" % c )
        plt.errorbar( t, y, yerr, fmt='o', label=c, color=colors_[i])

        # fit
        popt, pcorr = sco.curve_fit(exp_fit, t, y, p0=(50,) )
        plt.plot( t, exp_fit(t, *popt), color=colors_[i]
                    , label = '$1-e^{-t/%.2f}$'%popt)
        print( "[INFO ] Popt %s" % popt )

        #  plt.legend(loc = 'upper left', bbox_to_anchor=(1,1) )
        plt.legend( fontsize=6 )
    plt.title( "Figure 2" )

    plt.subplot(324)
    for i, c in enumerate(['8_37', '1_37']):
        col = 'mean_%s' % c
        colErr = 'std_%s' % c
        d = df[ ['Time', col, colErr] ].dropna()
        t, y, yerr = d['Time'], d[col], d[colErr]
        print( "[INFO ] Plotting %s" % c )
        plt.errorbar( t, y, yerr, label=c, color=colors_[i])


    try:
        plt.title( "Sim Vs Exp" )
        rg, rl = '1.00*', '0.0018*'
        f1 = glob.glob('../UsingChemReacs/CM1e-3_rg%s_rl%s.csv'%(rg,rl))[0]
        f2 = glob.glob('../UsingChemReacs/CM8e-3_rg%s_rl%s.csv'%(rg,rl))[0]
        for f in [f1, f2]:
            d = pd.read_csv(f)
            plt.plot( d['time'], d['colocalization_perc'] )
    except Exception as e:
        print( "[INFO ] Failed with error: %s" % e )

def fit_simulation_data( ):
    simFiles = glob.glob( '../UsingChemReacs/summary_*.csv' )
    ax = plt.subplot(325)
    allPts = []
    for i, (ca, tau) in enumerate(zip(['1e-3', '8e-3'], [60, 20])):
        f = '../UsingChemReacs/summary_CM%s.csv' % ca 
        df = pd.read_csv( f )
        scale = 2
        df = df[ df['tau'] < scale*tau ] 
        df = df[ df['tau'] > tau/scale ] 
        X, Y, Z = df['rgain'], df['rlose'], df['tau']
        #  im = ax.tricontourf(X, Y, Z, alpha = 0.5)
        pts = np.vstack((X,Y)).T
        allPts.append( pts )
        ax.scatter(X, Y, marker='o', alpha=0.1)
        #  h = scs.ConvexHull( pts )
        #  for i, smplx in enumerate(h.simplices):
            #  print( "[INFO ] Simplex %d" % i )
            #  ax.plot( pts[smplx, 0], pts[smplx, 1] )
        #  ax.plot( pts[h.vertices,0], pts[h.vertices,1], '--' )
        ax.set_xlabel( 'rate gain' )
        ax.set_ylabel( 'rate lose' )
        ax.set_xscale( 'log' )
        ax.set_yscale( 'log' )

def plot_with_our_values_of_rl_rg():
    ax = plt.subplot(324)
    f1 = '../UsingChemReacs/CM1e-3_rg0.8886238162743403_rl0.8858667904100823.csv'
    f2 = '../UsingChemReacs/CM8e-3_rg0.8886238162743403_rl0.8858667904100823.csv'
    d1 = pd.read_csv(f1)
    d2 = pd.read_csv(f2)
    ax.plot( d1['time'], d1['colocalization_perc'], label = 'This Paper' )
    ax.plot( d2['time'], d2['colocalization_perc'], label = 'This paper' )
    ax.legend()

        
def main():
    plt.figure( figsize=(8,8) )
    plot_with_our_values_of_rl_rg()
    plot_experimental_data()
    plt.tight_layout()
    plt.savefig( 'stratton_elife_2016.png' )

if __name__ == '__main__':
    main()
