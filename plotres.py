# Main statistical analysis routine for non-parametrically calculating the
# best-fitting density profile.  Requires res.tab file made from mkrestab.py
# which takes model.f output and converts to easily readable table.
# This version of plotres uses the biweight of the N lowest points within a
# sliding boxcar to fit a minimum to the 1-D marginalized chi^2 curves.
# Creates chi2.ps (Figure 6 of Jardel et al 2013).  Also outputs chi.out,
# the log-symmetric 1-sigma bounds for each point in the radial density profile


from readcol import readcol
from numpy import *
from pylab import *
import os
import sys
import math
from robust import biweightMean
from robust import std as rstd

#from gcvspl import *

# PARAMETERS
#===============
deltachi = 2.
chirange = 20.
dis = 135e3
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


# --- read contents of npoints.in to determine how to initialize the sliding
#        biweight.  npoints.in is formatted as:
#  radial_bin_no  N_rho_bins  window_width  N_points_in_biweight
chifile = open( 'chi.out', 'wa' )
npfile = open( 'npoints.in' )
ns = []
nbox = []
nbest = []
for line in npfile:
    ns.append( int( line.split()[ 1 ] ) )
    nbox.append( int( line.split()[ 2 ] ) )
    nbest.append( int( line.split()[ 3 ] ) )
npfile.close()
if( nk <=8 ):
    ncol = 2
    nrow = 4.

def xbin( x, xhat ):
    # bin up chi^2 space along the dimension of interest
    ii = 0
    for i in xhat:
        if( ii != 0 ):
            xlo = xhat[ ii - 1 ]
            xhi = i
        else:
            xlo = 0.
            xhi = i
        if( x >= xlo and x < xhi ):
            return ii
        ii += 1
clf()
ir = 1
xpos = [ .8, .75, .75, .75, .75, .75, .75 ]
# -- do statistics on rho bins and make exploratory plots
for i in range( 0, nk ):
    ifig = i + 1
    x = []
    y = []
    for item, chi in zip( alldens[ :, i ], allchi ):
        x.append( item )
        y.append( chi )
    xmin = .9 *  min( x ) 
    xmax = 1.1 * max( x )
    ymin = .99 * min( y )
    ymax = ymin + chirange
    subplot( 4, 2, i + 1 )
    semilogx( x, y, 'k.' )
    ylabel( '$\chi^2$' )
    xlabel( '$\\rho$' )
    ylim( [ymin, ymax ] )
    subplots_adjust( hspace = .5, wspace = 0.3 )
    xl = set( x )
    xl = sorted( xl )
    xa = array( x )
    ya = array( y )
    n = len( xl )
    ymarg = zeros( ns[ i ] ) + 1e9
    xmarg = zeros( ns[ i ] ) + 1e9
    npoints = ns[ i ]
    xhat = logspace(  math.log10( .9 * min( x ) ),
                     math.log10( 1.1 * max( x ) ) ,
                     num = npoints )
    ym = zeros( npoints ) -1.
    xm = zeros( npoints ) -1.
    ij = 0
    # compute the sliding biweight of each bin
    for ii in range( nbox[ i ], xhat.size ):
        inbin = where( ( xa >= xhat[ ii - nbox[ i ] ] ) & ( xa < xhat[ ii ] ) )
        if( len( inbin[ 0 ] ) > nbest[ i ] ):
            best = sorted( ya[ inbin[ 0 ] ] )[ :nbest[ i ] ]
            ym[ ii ] = biweightMean( array( best ) )
            xm[ ii ] = median( [ xhat[ ii - nbox[ i ] ], xhat[ ii ] ] )
    ym2 = interp( xhat, xm[ xm > 0 ], ym[ ym > 0 ] )
    xm2 = xhat
    ym2min = min( ym2 )
    pout = column_stack( ( xa, ya ) )
    savetxt( 'chi.' + str( i ), pout )
    sigmalist = where( ym2 < ( ym2min + 1  ) ) 
    siglo = min( xm2[ sigmalist ] )
    sighi = max( xm2[ sigmalist ] )
#    out = str( rk[ i ] ) + ' ' + str( siglo ) + ' ' + str( float( xhat[ where( ys == ysmin ) ] ) ) + ' ' + str( sighi ) + ' \n'
    print siglo, sighi
    out = str( rk[ i ] ) + ' ' + str( siglo ) + ' ' + str( 10**mean( [ math.log10( siglo ), math.log10( sighi ) ] ) ) + ' ' + str( sighi ) + ' \n'
    chifile.write( out )
    ax = gca()
    text( 0.05, 0.1, str( i + 1 ), transform = ax.transAxes )
    rr = rk[ i ] * dis / 206265. 
    textrad = '%4.1f' % rr + ' pc'
    text( xpos[ i ], .1, textrad, transform = ax.transAxes, fontsize = 10 )
    semilogx( xm2, ym2, 'r', linewidth = 2 )
savefig( 'chi2.ps' )
chifile.close()

clf()        
r, yl, yb, yh = readcol( 'chi.out', twod = False )
yy = zeros( nk )
# output log-symmetric 1-sigma bounds for each radial bin
for i in range( 0, nk ):
    yy[ i ] = 10**( ( math.log10( yh[ i ] )+ math.log10( yl[ i ] ) )/ 2. )

loglog( r, yy, 'k' )
fill_between( r, yl, yh, color = '.7' )
loglog( r, yy, 'k' )
loglog( r, yy, 'ko' )
xlabel( 'r (arcsec)' )
ylabel( '$\\rho \, (M_{\odot} \, \mathrm{pc}^{-3})$' )
#arrow( 27., 1.e-2, 0., 1e-3 )
#arrow( 893.8, 1e-2, 0., 1e-3 )


y1 = [ 1e1, 1e0 ]
x1 = [ 1e2, 1e3 ]
loglog( x1, y1, 'k' )

loglog( r, bestdens, 'r' )

savefig( 'dens2.ps' )
