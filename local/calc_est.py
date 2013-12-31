import numpy as np
import os
from readcol import readcol
import scipy

# general routine to calculate mass estimates from profiles in surf/sb.mag 
# and dispersion in kin/sigma.out

# put these together to get sigma_LOS

pwd = os.getcwd()
gallist = [ 'carina', 'fornax', 'sculptor', 'sex' ]

d = {}
d[ 'carina' ] = [ 104e3, 246.69, 325.20 ] # [ distance, Re, re ]
d[ 'fornax' ] = [ 135e3, 689, 900 ]
d[ 'sculptor' ] = [ 85e3, 319.17, 539.91 ]
d[ 'sextans' ] = [ 85e3, 697.58, 926.30 ]

for gal in gallist:
    if gal in pwd:
        #galname = gal.upper()[ 0 ] + gal[ 1: ]
        galname = gal
        if galname == 'sex':
            galname = 'sextans' 

r_surf, surf = readcol( 'surf/sb.mag', twod = False )
dist = d[ galname ][ 0 ]
r_surf *= dist / 206265.
zp = 26.402
surf_solar = 10**( ( zp - surf ) / 2.5 )
r_kin, sigma, sigma_err = readcol( 'kin/sigma.out', twod = False )
sigma_low_int = np.interp( r_surf, r_kin, sigma - sigma_err )
sigma_hi_int = np.interp( r_surf, r_kin, sigma + sigma_err )
sigma_int = np.interp( r_surf, r_kin, sigma )

integrand_hi = sigma_hi_int**2 * surf_solar
integrand_low = sigma_low_int**2 * surf_solar
integrand = sigma_int**2 * surf_solar

sigma_los_hi = scipy.integrate.trapz( 
    integrand_hi, x = r_surf ) / scipy.integrate.trapz(
    surf_solar, x = r_surf )

sigma_los_low = scipy.integrate.trapz( 
    integrand_low, x = r_surf ) / scipy.integrate.trapz(
    surf_solar, x = r_surf )

sigma_los = scipy.integrate.trapz( 
    integrand, x = r_surf ) / scipy.integrate.trapz(
    surf_solar, x = r_surf )

M = 930. * sigma_los * d[ galname ][ 1 ]
M_low = 930. * sigma_los_low * d[ galname ][ 1 ]
M_hi = 930.  * sigma_los_hi * d[ galname ] [ 1 ]

f = open( '/home/jardel/research/alldSphs/calc_est/' + galname + '.est' , 'w' )
out = str( d[ galname ][ 2 ] ) + '\n'
out += str( M_low ) + '\n'
out += str( M ) + '\n'
out += str( M_hi ) + '\n'
f.write( out )
f.close()

# re, M_low, M, M_hi

"""
out += str( d[ galname ][ 1 ] ) + '\n'
out += str( np.sqrt( sigma_los_low ) ) + '\n'
"""





