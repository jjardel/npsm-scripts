#  play around with Draco CMD from Segall et al. (2007).  goal is to get
#  luminosity-weighted M/L for different spatial bins.
#  get M from MS for best-fitting isochrone.

# CMD of central 6' from CFHT data in g' and r' (AB)

from numpy import *
from pylab import *
from readcol import readcol
import coords as c
import math as m

def linint( x, xp, yp ):
    n = len( xp )
    for i in arange( 0, n - 2 ):
#        print x, xp[ i ], xp[ i + 1 ]
        if( x <= xp[ i ] and x > xp[ i + 1 ] ):
            y = yp[ i ] + ( yp[ i + 1 ] - yp[ i ] ) * ( x - xp[ i ] ) / ( 
                xp[ i + 1 ] - xp[ i ] )
            return y
        

def load_isochrone( t, Z, band ):
    isofile = open( 'combined.dat' )
    l = 0
    lend = 0
    foundit = False
    for line in isofile:
        if( 'Z =' in line ):
            if( abs( Z / float( line.split()[ 4 ] ) - 1. ) < .01 and
                abs( t / float( line.split()[ 7 ] ) - 1. ) < .01 ):
                 lstart = l + 2
                 foundit = True
        if( 'Isochrone' in line and foundit == True and ( l - lstart ) 
            > 0 ):
            foundit = False
            lend = l
        l += 1
    if( lend == 0 ):
        lend = l
    isofile.seek( 0 )
    lines = isofile.readlines()
    head = lines[ lstart ]
    head = head.split()
    print lstart, lend
    try:
        i1 = head.index( band[ 0 ] ) - 1
        i2 = head.index( band[ 1 ] ) - 1
    except:
        print 'Band not found'
        return
    mag1 = []
    mag2 = []
    print i1, i2
    outf = open( 'iso.best', 'w' )
    for line in lines[ lstart + 1:lend ]:
        mag1.append( float( line.split()[ i1 ] ) )
        mag2.append( float( line.split()[ i2 ] ) )
        outf.write( line.split()[ 1 ] + '\t' + line.split()[ i1 ] + '\t' +
                    line.split()[ i2 ] + '\n' )
    mag1 = array( mag1 )
    mag2 = array( mag2 )
    outf.close()
    return mag1, mag2

def getmass( L, color, dist ):
    isofile = open( 'iso.best' )
    mass = []
    m1 = []
    m2 = []
    for line in isofile:
        mass.append( float( line.split()[ 0 ] ) )
        m1.append( float( line.split()[ 1 ] ) )
        m2.append( float( line.split()[ 2 ] ) )

# check if L, color place this star in the area of the cmd that satisfies
# constraints

    m1 = array( m1 )
    m2 = array( m2 )
    m1 = m1 + dist
    m2 = m2 + dist
    if( L < 25 and L >= 23. ):
        clim = .3
    elif( L < 23 and L >= 21. ):
        clim = .1
    else:
        clim = -1

# if not within clim restrictions at m1, return None
# else get mass

# interpolate to m1, m2, mass
    iclose = argsort( abs( L - m1 ) )
    isocolor = m1 - m2

    if( L < 23 ):
        clim = -1

    if( abs( isocolor[ iclose[ 0 ] ] - color ) > clim ):
        smass = None
    else:

#        smass = mass[ iclose[ 0 ] ]
        smass = linint( L, m1, mass )
#        lum = 10**( ( 5.11 - L + dist ) / 2.5 )
#        smass = lum**(.25 ) 
# if on HB, all stars have same mass
#    if( L < 21 and L > 19.6 and color > -0.5 and color < 0.5 ):
#        smass = .8424
#    print isocolor[ iclose[ 0 ] ], color, clim, smass, L
    return smass
    



rah, ram, ras, decd, decm, decs, gmag, egmag, t1, imag, eimag, t2  = readcol( 
    'megacam.tab', twod = False )
nstars = len( rah )
coords = []
for i in range( 0, nstars ):
    stringra = str( rah[ i ] ) + ':' + str( ram[ i ] ) + ':' + str( ras[ i ] ) 
    stringdec = str(decd[ i ] ) + ':' + str( decm[ i ] ) + ':' + str( decs[ i ] ) 
    stringcoords = stringra + ' ' + stringdec
    co = c.Position( stringcoords )
    coords.append( co.dd() )
coords = array( coords )
center = zeros( 2 )
center[ 0 ] = 260.055
center[ 1 ] = 57.915

# check conversions on a few of these
theta = m.radians( 88. + 90. )
rdiff = ( coords[ :, 0 ] - center[ 0 ] ) * 3600. * m.cos( m.radians( center[ 1 ] ) )
ddiff = ( coords[ :, 1 ] - center[ 1 ] ) * 3600.
x = rdiff * m.cos( theta ) - ddiff * m.sin( theta )
y = rdiff * m.sin( theta ) + ddiff * m.cos( theta )
r = ( x * x + y * y )**0.5

i = 0
l = []
for item in r:
    if( item < 60. * 6. ):
        l.append( i )
    i += 1

# 12.5e9 , .0007
iso1, iso2 = load_isochrone( 12.5e9, .0007,(  "g'", "i'" ) )

iso1 = iso1 + 19.4
iso2 = iso2 + 19.4
isocolor = iso1 - iso2
color = gmag[ l ] - imag[ l ]
mag = gmag[ l ]
w, h = figaspect( 1. )
figure( figsize = ( w, h ) )


plot( color, mag, 'k.' )
plot( isocolor, iso1, 'r' )
ylim( [ 25, 18 ] )
xlabel( "g' - i'" )
ylabel( "g'" )
xlim( [ -1, 2 ] )
#show() 
text( -0.8, 19, 't = 12.5 Gyr' )#'$t=12.5 \\times 10^9 Gyr$' )
text( -0.8, 19.5, '[Fe/H] = -1.4' )
savefig( 'cmd.ps' )
# if on HB, just use single value for L, M in isochrone at L of HB

# constraint:
# must be within .5 mags in g-i from MS, .2 mags from RGB, or in square box
# defining BS.

ii = 0
massf = open( 'mass.out', 'w' )
for i in mag:
    mass = getmass( i, color[ ii ], 19.4 )
    if( mass != None ):
        out = str( i ) + '\t' + str( mass ) + '\n'
        massf.write( out )
    ii += 1
massf.close()
print mag[ 0 ], getmass( mag[ 0 ], color[ 0 ], 19.4 )
