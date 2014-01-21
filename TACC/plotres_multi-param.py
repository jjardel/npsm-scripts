# computes profile by just taking models that lie in multi-dimensional
#    chi^2 cut.  Also does a better job interpolating between rho bins.

from readcol import readcol
from numpy import *
from pylab import *
import os
import sys
import math
from robust import biweightMean
from robust import std as rstd


def interp_1sigma_models( y_actual, x_actual, x ):
    # y_actual is NGOOD x NK array containing density profiles within the
    # delta chi^2 cut.
    #
    # x_actual is array containing positions of knots
    #
    # return y_upper( x ), y_lower( x ), the 1-sigma envelope at each
    # intepolated point from rg


    i = 0
    yup = zeros( len( x ) )
    ylo = zeros( len( x ) )

    for xi in x:
        yl = 1e10
        yh = -1e10
        for iprofile in y_actual:
            y = interp( log10( xi ), log10( x_actual ), log10( iprofile ) )
            y = 10**y
            yl = min( yl, y  )
            yh = max( yh, y )
        yup[ i ] = yh
        ylo[ i ] = yl
        i += 1
    return ylo, yup
        
    
    

# PARAMETERS
#===============
deltachi = 5.84
chirange = 20.
dis = 71e3
#===============

paramf = open( '../param/mod.param.bin' )
rk = []
for line in paramf:
    rk.append( float( line.split()[0] ) )
paramf.close()
nk = len( rk )

# --- open res.tab file and index results
resf = open( 'res.tab', 'r' )
resin = resf.readlines()
resf.close()

nmod = len( resin )
alldens = zeros( ( nmod, nk ) )
allchi = zeros( nmod )
slope = zeros( nmod )
allmod = zeros( nmod )

ii = 0
for line in resin:
    allchi[ ii ] = float( line.split()[ nk + 3 ] )
    slope[ ii ] = float( line.split()[ nk + 2 ] )
    alldens[ ii, : ] = [ float( j ) for j in line.split()[ :nk ] ]
    allmod[ ii ] = int( line.split()[ nk ] )
    ii += 1
chimin = min( allchi )
imin = where( allchi == chimin )[ 0 ]
bestdens = alldens[ imin, : ][ 0 ]
incut = where( allchi <= chimin + deltachi )[ 0 ]

# --- create grid and do interpolation
rg = logspace( math.log10( rk[ 0 ] ), math.log10( rk[ nk - 1 ] ), num = 100 )
ylo, yup = interp_1sigma_models( alldens[ incut ], rk, rg )

clf()

loglog( rk, bestdens, 'k' )
fill_between( rg, ylo, yup, color = '0.7' )
loglog( rk, bestdens, 'k' )
loglog( rk, bestdens, 'ko' )

# ---write out chi.out, plotres_boxcar will have to write chi_1D.out
#     combine results in dsphdm

out = column_stack( ( rg, ylo, yup ) )
savetxt( 'chi_multi.out', out, fmt = '%6.2f %6.4e %6.4e' )


savefig( 'dens.ps' )

    

