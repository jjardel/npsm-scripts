# dsphdm.py 

# Analysis routine to subtract stellar density from best-fitting total density
# found by plotres.py.  Calculates uncertainties by adding noise from a gaussian
# distribution with (mean = best fitting density, std dev = 1-sigma range in 
# denstiy) at each point in the profile.

# Used to create Figure 8 in 2013 ApJ 763 91.  

# Required input:
# chi.out - created by plotres.py.  Contains +/- 1-sigma range in density for 
#     each point
# light.dat - radial profile of luminosity density along the major axis of the
#     galaxy
# ssp.tab - Table of Maraston et al (2005) SSP models.  Contains mass-to-light
#     ratios in various filters (band), as a function of stellar age (t_in)
#     and metallicity (Z_in).

# simulated noise from outer points in profile

from readcol import readcol
from numpy import *
from pylab import *
from scipy import interpolate
from scipy import stats
from scipy import random
from scipy import optimize
import math as m

def fitfunc( x, a, b ):
    func = a * x + b
    return func

def SSP_load( Z_in, t_in, band ):
    tabf = open( 'ssp.tab' )
    tests = ' ' + band + ' '
    Z = []
    t = []
    ml = []
    for line in tabf:
        noread = False
        if( tests in line ):
            try: 
                col = line.split().index( band )
            except:
                print 'band not found'
                return
        try:
            Z.append( float( line.split()[ 0 ] ) )
        except:
            noread = True
        if( not noread ):
            ml.append( float( line.split()[ col ] ) )
            t.append( float( line.split()[ 1 ] ) )
    n = len( ml )
    j = 0
    xml = []
    x1 = zeros( n / 4 )
    x2 = zeros( n / 4 )
    y = zeros( n / 4 )
    for i in range( 0, n ):
        x1[ j ] = Z[ i ]
        x2[ j ] = t[ i ]
        y[ j ] = ml[ i ] 
        j+= 1
        if( j == n / 4 ):
            j = 0
            func = interpolate.LinearNDInterpolator( ( x1, x2 ), y )
            xml.append( func( Z_in, t_in ) )
    lo = min( xml )
    hi = max( xml )
    return lo, hi


# INDIVIDUAL GALAXY PARAMETERS
kinstart = 47.8
kinend = 3523.
galname = 'Sculptor'
dis = 85e3
xlim0 = 8.
xlim1 = 4000.
ylim0 = 1e-2
ylim1 = 1e2
Zrange = [ -1.67 - 0.25, -1.67 + 0.25 ]
trange = [ 5, 7.5, 10., 12.5 ]


# use photo metallicities from 2011 A&A 531, A152 with spread in age of trange

mlrange = [ 1e9, -1e9 ]

for i in Zrange:
    for j in trange:
        lo, hi = SSP_load( i, j, 'V' )
        mlrange[ 0 ] = min( [ lo, mlrange[ 0 ] ] )
        mlrange[ 1 ] = max( [ hi, mlrange[ 1 ] ] )

ml = mean( mlrange )
ml_err = max( [ ( mlrange[ 1 ] - mlrange[ 0 ] ) / 2., mlrange[ 1 ] - ml ] )

rl, light = readcol( 'light.dat', twod = False )
r, rhol, rhoread, rhoh = readcol( 'chi.out', twod = False )

rho_err = zeros( r.size )
rho = zeros( r.size )
ii = 0
for i in zip( rhol, rhoh ):
    rho[ ii ] = mean( [ i[ 0 ], i[ 1 ] ] )
    rho_err[ ii ] = max( [ ( i[ 1 ] - i[ 0 ] ) / 2., i[ 1 ] - rho[ ii ] ] )
    ii += 1


stars = interp( r, rl, light * ml )
stars_err = stars * ml_err

dm = rho - stars
dm_err = sqrt( stars_err**2 + rho_err**2 )

# correction to keep DM positive when it's close to the stellar density
badlist = where( ( dm - dm_err ) < 0 )
# ......
# ......

"""
clf()
loglog( r, dm, 'k' )
fill_between( r, dm - dm_err, dm + dm_err, color = '0.7' )
savefig( 'dsphdm.ps' )
"""

inner = where( r < kinstart )
outer = where( r > kinstart )
n_inner = len( r[ inner ] )

yi = log10( dm[ outer ] )
xi = log10( r[ outer ] )
yerr = .434 * dm_err[ outer ] / dm[ outer ]

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
xlim( [-2., 0.] )
subplot( 2, 2, 3 )
h_int = hist( boot_int, color = '0.7', bins = 15 )
plot( [ boot_int[ i16 ], boot_int[ i16 ] ], [ 0, ylim()[ 1 ] ],
      'r' )
plot( [ boot_int[ i84 ], boot_int[ i84 ] ], [ 0, ylim()[ 1 ] ],
      'r' )
xlabel( '$\\beta$' )
ylabel( 'N' )
xlim( [ 0., 5. ] )
savefig( 'hist.ps' )

clf()


# plot resulting density profile with uncertainties
loglog( r[ outer ], dm[ outer ], 'k' )
fill_between( r[ outer ], dm[ outer ] - dm_err[ outer ], 
              dm[ outer ] + dm_err[ outer ], color = '0.7' )
loglog( r[ outer ], dm[ outer ], 'k' )
loglog( r[ outer ], dm[ outer ], 'ko' )

errorbar( r[ inner ], dm[ inner ], yerr = dm_err[ inner ], fmt = 'x', 
          color = '0.5', ecolor = '0.5' )

ylim( [ ylim0, ylim1 ] )
xlim( [ xlim0, xlim1 ] )
xlabel( '$r$ (arcsec)' )#, fontsize = '16' )
ylabel( '$\\rho_{DM} \, (M_{\odot} \, \mathrm{pc}^{-3})$', fontsize = '16' )
arrow( kinstart, ylim()[ 0 ], 0., 0.1 * ylim()[ 0 ] )
arrow( kinend, ylim()[ 0 ], 0., 0.1 * ylim()[ 0 ] )

# --- draw NFW line
y1 = [ 1e1, 1e0 ]
x1 = [ 1e2, 1e3 ]
loglog( x1, y1, 'k--' )


xp = xlim()[ 1 ] * .4
yp = ylim()[ 1 ] * .6
annotate( galname, [ xp, yp ] )

# --- put pc axis on top
rpc = r * dis / 206265.
twiny()
loglog( r, dm, linestyle = 'None' )
ax2 = gca()
xlim( [ 8 * dis / 206265., 2000. * dis / 206265. ] )
xlabel( '$r$ (pc)' )
ylim( [ ylim0, ylim1 ] )

savefig( galname + '.ps' )
