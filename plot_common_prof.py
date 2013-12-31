from numpy import *
from pylab import *
from scipy import stats
from scipy import random
from scipy import optimize
import math as m
from readcol import readcol


def fitfunc( x, a, b ):
    func = a * x + b
    return func


xi, yi, yerr = readcol( 'common_prof.out', twod = False )


# --- add simulated noise to points in the profile and collect statistics


p0 = [ 1., 1. ]

pfit, cov = optimize.curve_fit( fitfunc, xi, yi, p0 = p0, sigma=yerr )

y = []
resid = []
ii = 0
for i in xi:
    y.append( pfit[ 0 ] * i + pfit[ 1 ] )
    resid.append( yi[ ii ] - y[ ii ] )
    ii += 1

nboot = 1000
boot_slope = []
boot_int = []
boot_err = []

yfit = zeros( ( len( xi ), nboot ) )
ymin = zeros( len( xi ) ) + 1e10
ymax = zeros( len( xi ) ) - 1e10

chi2 = zeros( nboot ) 
random.seed( 1 )
xsam = zeros( len( xi ) )
ysam = zeros( len( xi ) )

for iboot in range( 0, nboot):
    yboot = zeros( len( xi ) )
    for i in range( 0, len( xi ) ):
        ysam[ i ] = random.normal( yi[ i ], yerr[ i ] )
        xsam[ i ] = xi[ i ]
#        yboot[ i ] = y[ i ] + resid[ random.randint( 0, len( xi ) ) ]
#    slope, intercept, r_value, p_value, std_err = stats.linregress( xi, yboot )
    pfit, cov = optimize.curve_fit( fitfunc, xsam, ysam, p0 = p0 )#, 
#                                    sigma = yerr )
    slope = pfit[ 0 ]
    intercept = pfit[ 1 ]
    boot_slope.append( slope )
    boot_int.append( intercept )
#    boot_err.append( std_err )
    yfit[ :, iboot ] = slope *  xi + intercept
    j = 0
    for ii in xi:
        chi2[ iboot ] += ( y[ j ] - ( slope * xi[ j ] + 
                                      intercept ) )**2 / yerr[ j ]**2
        j += 1

slope_med = median( boot_slope )
slope_std = std( boot_slope )
int_med = median( boot_int )
int_std = std( boot_int )

boot_slope = sorted( boot_slope )
boot_int = sorted( boot_int )

i16 = int( round( float( nboot ) * .16 ) )
i16 = max( [ 1, i16 ] )
i84 = int( round( float( nboot ) * .84 ) )
i84 = min( [ nboot, i84 ] )

print boot_slope[ i16 ], boot_slope[ i84 ]
best_slope =  mean( [ boot_slope[ i16 ], boot_slope[ i84 ] ] )
print best_slope, best_slope - boot_slope[ i16 ]
print boot_int[ i16 ], boot_int[ i84 ]
best_int =  mean( [ boot_int[ i16 ], boot_int[ i84 ] ] )


# create histogram of slopes and intercepts
clf()
w, h = figaspect( 1. )
figure( figsize = ( w, h ) )
subplot( 2, 2, 1 )
h_slope = hist( boot_slope, color = '0.7', bins = 15 )
plot( [ boot_slope[ i16 ], boot_slope[ i16 ] ], [ 0, ylim()[ 1 ] ],
      'r' )
plot( [ boot_slope[ i84 ], boot_slope[ i84 ] ], [ 0, ylim()[ 1 ] ],
      'r' )
xlabel( '$\\alpha$' )
ylabel( 'N' )
xlim( [-1.5, -1.] )
subplot( 2, 2, 3 )
h_int = hist( boot_int, color = '0.7', bins = 15 )
plot( [ boot_int[ i16 ], boot_int[ i16 ] ], [ 0, ylim()[ 1 ] ],
      'r' )
plot( [ boot_int[ i84 ], boot_int[ i84 ] ], [ 0, ylim()[ 1 ] ],
      'r' )
xlabel( '$\\beta$' )
ylabel( 'N' )
xlim( [ 0., .5 ] )
savefig( 'hist.ps' )

clf()
