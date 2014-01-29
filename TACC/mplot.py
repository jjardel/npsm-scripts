from numpy import *
from pylab import *
from readcol import readcol
import os
import math as m
import sys
import glob

# python mplot.py 'galname'

#----------------
# PARAMETERS
nr = 20 * 4
nv = 5 * 4
#----------------

# get rmax and dis from galaxy.params
f = open( 'base/galaxy.params' )
f.readline()
line = f.readline().split()
dis = float( line[ 1 ] ) * 1e6
line = f.readline().split()
rmax = float( line[ 1 ] )


r = zeros( nr )
bin_rfile = open( 'base/bindemo_r.out' )
bin_rfile.readline()
bin_rfile.readline()
bin_rfile.readline()
bin_rfile.readline()
bin_rfile.readline()

for i in range( 0, nr ):
    r[ i ] = float( ( bin_rfile.readline() ).split()[ 3 ] ) * rmax * dis / 206265.
bin_rfile.close()

# read in data from best/
trash, mr_best = readcol( 'mod/best/mr.dat', twod = False )
trash, rc, vc_best = readcol( 'mod/best/vcirc.out', twod = False )
rc = rc * rmax * dis / 206265.
nrc = len( rc )

# get 1-sigma range
mr_low = zeros( nr ) + 1e10
mr_hi = zeros( nr ) - 1e10
vc_low = zeros( nrc ) + 1e10
vc_hi = zeros( nrc ) - 1e10


m_sigmalist = glob.glob( 'mod/mplot/*/mr.dat' )
vc_sigmalist = glob.glob( 'mod/mplot/*/vcirc.out' )

for cmod in m_sigmalist:
    i = 0
    f = open( cmod )
    for line in f:
        x = float( line.split()[ 1 ] )
        mr_hi[ i ] = max( [ x, mr_hi[ i ] ] )
        mr_low[ i ] = min( [ x, mr_low[ i ] ] )
        i += 1
    f.close()

for cmod in vc_sigmalist:
    i = 0
    f = open( cmod )
    for line in f:
        x = float( line.split()[ 2 ] )
        vc_low[ i ] = min( [ x, vc_low[ i ] ] )
        vc_hi[ i ] = max( [ x, vc_hi[ i ] ] )
        i += 1
    f.close()

# figure out which galaxy mplot is currently being called on
galname = sys.argv[ 1 ]

# have my r_half, m_est, m_est_low, m_est_hi in a file called 'm_half.est'
f_est = open( galname + '.est' )
r_half = float( f_est.readline() )
m_half_low_est = float( f_est.readline() )
m_half_est = float( f_est.readline() )
m_half_hi = float( f_est.readline() )
f_est.close()


# calculate my mass at r_half from the models
m_half = interp( r_half, r, mr_best )
m_half_low = interp( r_half, r, mr_low )
m_half_hi = interp( r_half, r, mr_hi )

# save this to a new file GALNAME.mhalf
print m_half / 1e7, ( m_half - m_half_low) / 1e7, ( m_half_hi - m_half )/ 1e7
f_half = open( galname + '.half', 'w' )
out = str( r_half ) + '\n'
out += str( m_half_low ) + '\n'
out += str( m_half ) + '\n'
out += str( m_half_hi ) + '\n'
f_half.write( out )
f_half.close()


# output galname.mass & galname.vc
f_out = galname + '.mass'
out = column_stack( ( r, mr_low, mr_best, mr_hi ) )
savetxt( f_out, out, fmt = '%-5.5f %-5.5e %-5.5e %-5.5e' )

f_out = galname + '.vc'
out = column_stack( ( rc, vc_low, vc_best, vc_hi ) )
savetxt( f_out, out, fmt = '%-5.5f %-5.5e %-5.5e %-5.5e' )

sys.exit()

# END OF NEW MPLOT.PY
#--------------------------------------------------------------------------


#m_est = 2.11e7
#vc_est = sqrt( 4.3e-3 * m_est / 205.2. )

m_est = 1.9e7
vc_est = sqrt( 4.3e-3 * m_est / 205.2 )

clf()
loglog( r, mr_best, 'k' )
fill_between( r, mr_low, mr_hi, color = '0.7' )
xlabel( '$r$ pc' )
ylabel( '$M(r)$ $(M_{\odot})$' )
xlim( [ 5, 700 ] )
errorbar( [ 205.2 ], [ m_est ], yerr = .5e7, fmt = None, ecolor = 'k' )
loglog( [ 205.2 ], [ m_est ], 'go' )
x1 = [ 27. / 206265. * 71e3, 27. / 206265. * 71e3 ]
x2 = [ 893.8 / 206265 * 71e3, 893.8 / 206265 * 71e3 ]
y1 = ylim()
y2 = ylim()
#loglog( x1, y1, 'k' )
#loglog( x2, y2, 'k' )
arrow( 9.2, 1e3, 0., 1e3 )
arrow( 500., 1e3, 0., 1e3 )

savefig( 'mr.ps' )


clf()
rc = rc / 1e3
plot( rc, vc_best, 'k' )
fill_between( rc, vc_low, vc_hi, color = '0.7' )
xlim( .008, .7 )
xlabel( '$r$ kpc' )
ylabel( '$V_c$ $\mathrm{km}$ $\mathrm{ s}^{-1}$' )
errorbar( [.2052 ], [vc_est], yerr = 2.6, fmt = None, ecolor = 'k' )
plot( [ .2052 ], [vc_est ], 'go' )
ylim( [ 0, 50 ] )

arrow( .500, 0.2, 0., 2. )



#rq, vcq = readcol( 'vcirc/vcirc.aq', twod = False )
#plot( rq, vcq )

savefig( 'vc.ps' )

sys.exit()

clf()
rc *= 1e3

vcm = rc * vc_best**2 / 4.3e-3
vcmL = rc * vc_low**2 / 4.3e-3
vcmH = rc * vc_hi**2 / 4.3e-3

loglog( rc, vcm )
fill_between( rc, vcmL, vcmH, color = '0.7' )
xlim( [ 5, 700 ] )
ylim( [ 1e3, 1e9 ] )

savefig( 'mr2.ps' )

