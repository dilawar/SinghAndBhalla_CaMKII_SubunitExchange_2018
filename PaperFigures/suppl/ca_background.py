"""ca_background.py: 
Calcium background simplification.
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

dt = 10e-3
tvec = np.arange(0, 20, dt )   # 10 ms precision
print( "[INFO ] Samples %d" % len(tvec) )
print( "[WARN ] DEPRECATED." )


def precise_ca( ):
    ca = np.ones( len(tvec) ) * 80e-9
    for t in np.arange(0, tvec.max(), 4.0): 
        a, b = int(t//dt), int((t+2)//dt)
        ca[a:b] = 80e-9
    return ca

def approx_ca( ):
    ca = np.random.uniform(80e-9, 160e-9, len(tvec))
    for t in np.arange(0, tvec.max(), 4.0): 
        a, b = int(t//dt), int((t+2)//dt)
        ca[a:b] = 80e-9
    return ca

def main():
    cavec1 = precise_ca()
    cavec2 = approx_ca()
    plt.subplot(221)
    plt.plot( tvec, cavec1 )
    plt.subplot(222)
    plt.plot( tvec, cavec2)

    plt.subplot(223)
    plt.hist(cavec1, range=(80e-9, 160e-9), bins=20)

    plt.subplot(224)
    plt.hist(cavec2, range=(80e-9, 160e-9), bins=20)
    plt.savefig( '%s.png' % __file__ )

if __name__ == '__main__':
    main()
