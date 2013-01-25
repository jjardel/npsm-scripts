# plot_moments.py

# Plot Gauss-Hermite moments for every line in velbin.dat
# Has the option to select which angle/radius range you want to plot.
# Requires x and y coords in velbin.dat to actually be right.
#
# Requires plot.in to set preferred plot range.  Each line in plot.in is formatted as 
#
# rmin  rmax  theta_min  theta_max  matplotlib plotting symbol
#
# Required files:
#
# velbin.dat - list of LOSVDs and their positions
# *.herm files - output from pfitlove run on all LOSVDs.  Must have same names as LOSVDs in velbin.dat
# *.hermerr - output from pfitlove run using rncont_fiterr
# ghermd.out - data GH moments output from vlook
# gherm.out - model GH moments output from vlook



from numpy import *
from pylab import *
import math as m

f = open( 'velbin.dat' )
x = []
y = []
names = []
for line in f:
    names.append( line.split()[ 0 ] )
    x.append( float( line.split()[ 1 ] ) )
    y.append( float( line.split()[ 2 ] ) )
f.close()
nv = len( x )
theta = zeros( nv )
r = zeros( nv )
ii = 0
for i in zip( x, y ):
    theta[ ii ] = m.degrees( m.atan( i[ 1 ] / i[ 0 ] ) )
    r[ ii ] = m.sqrt( i[ 0 ]**2 + i[ 1 ]**2 )
    ii += 1

# read in pfitlove as data
data = zeros( ( nv, 4 ) )
ii = 0
for i in names:
    f = open( i[ :-2 ] + 'herm' )
    t = f.readline().split()
    data[ ii, : ] = t[ 1: ]
    f.close()
    ii += 1

# read in ghermd to compare how binning changes the moments
hdata = zeros( ( nv, 4 ) )
ii = 0
f = open( 'ghermd.out' )
for line in f:
    t = line.split()
    hdata[ ii, : ] = t[ 2: ]
    ii += 1
f.close()
    
# scale even moments in pfitlove to ghermd.out if necessary

#plot( data[ :, 1 ], hdata[ :, 1 ], 'go' )
#plot( [ 0, 15 ], [ 0, 15 ] )
#show()
#sys.exit()

model = zeros( ( nv, 4 ) )
f = open( 'gherm.out' )
ii = 0
for line in f:
    t = line.split()
    model[ ii, : ] = t[ 2: ]
    ii += 1
f.close()

errs = zeros( ( nv, 4, 2 ) )
ii = 0
for i in names:
    f = open( i[ :-2 ] + 'hermerr' )
    jj = 0
    for line in f:
        errs[ ii, jj, : ] = line.split()[ : ]
        jj += 1
    f.close()
    ii += 1

# get symmetric error bars
errb = zeros( ( nv, 4 ) )        
ii = 0
for i in errs:
    jj = 0
    for j in i:
        errb[ ii, jj ] = max( [ ( j[ 1 ] - j[ 0 ] ) / 2., 
                                ( j[ 1 ] - data[ ii, jj ] ) ] )
        jj += 1
    ii += 1

# calculate chi^2

diff = ( model - data )**2 
chi2 = 0
ii = 0
for line in errb:
    t = diff[ ii ] / line**2
    chi2 += t.sum()
    ii += 1
dof = nv * 4.
chi_red = chi2 / dof

print chi2, chi_red


#xfactor = chi_GH/chi_LOSVD = 12.3

# read in plotting range

f = open( 'plot.in' )
radrange = []
angrange = []
fmt = []
for line in f:
    radrange.append( [float( line.split()[ 0 ] ), float( line.split()[ 1 ] ) ] )
    angrange.append( [float( line.split()[ 2 ] ), float( line.split()[ 3 ] ) ] )
    fmt.append( line.split()[ 4 ] )
nplot = len( fmt )

clf()
w, h = figaspect( 1. )
fig = gcf()
#figure( figsize = ( w, h ) )
#sys.exit()
for iplt in range( 0, 4 ):
    subp = fig.add_subplot( 4, 1, iplt + 1 )
    for i in range( 0, nplot ):
        select = where( ( r >= radrange[ i ][ 0 ] ) & 
                        ( r < radrange[ i ][ 1 ] ) 
                        & ( theta >= angrange[ i ][ 0 ] ) &
                        ( theta < angrange[ i ][ 1 ] ) )
        rs = r[ select ]
        subp.semilogx( rs, data[ select, iplt ][ 0 ], fmt[ i ] )
        subp.semilogx( rs, model[ select, iplt ][ 0 ], 'k' )
        subp.errorbar( rs, data[ select, iplt ][ 0 ], 
                       yerr = errb[ select, iplt ][ 0 ],
                       fmt = None, ecolor = fmt[ i ][ :-1 ] )
        if iplt == 0:
            ylabel( '$V$ (km/s)' )
        elif iplt == 1:
            ylabel( '$\\sigma$ (km/s)' )
        elif iplt == 2:
            ylabel( '$h_3$' )
        else:
            ylabel( '$h_4$' )
            xlabel( 'R (arcsec)' )
            
        if iplt != 3:
            ax = gca()
            ax.set_xticklabels( [] )
            
subplots_adjust( hspace = 0. )
savefig( 'moments.ps' )
sys.exit()
