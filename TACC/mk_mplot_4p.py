import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from readcol import readcol

# plotting ranges
xrange = [ [ 5e0, 1e3 ], [ 10, 3e3 ], [ 5e0, 1e3 ], [ 2e1, 1e3 ] ]
mrange = [ [ 1e2, 1e8 ], [ 1e4, 1e9 ], [ 1e2, 1e9 ], [ 1e4, 1e8 ] ]
vrange = [ [ 0, 30 ], [ 0, 40 ], [ 0, 30 ], [ 0, 20 ] ]

fig = plt.figure()
gallist = [ 'carina', 'fornax', 'sculptor', 'sextans' ]
f_compare = open( 'est_comparison.out', 'w' )

vc_est = {}
G = 4.3e-3
iplt = 1
for gal in gallist:
    plt.subplot( 2, 2, iplt )
    rm, mlow, m, mhi = readcol( gal + '.mass', twod = False )

    # read in M_1/2 estimates
    est_file = open( gal + '.est' )
    r_half = float( est_file.readline() )
    m_est_low = float( est_file.readline() )
    m_est = float( est_file.readline() )
    m_est_hi = float( est_file.readline() )
    est_file.close()
    
    # read in M_1/2 from models
    half_file = open( gal + '.half' )
    half_file.readline()
    m_half_low = float( half_file.readline() )
    m_half = float( half_file.readline() )
    m_half_hi = float( half_file.readline() )
    half_file.close()

    # get errorbars for M_1/2
    m_est_err = np.zeros( ( 2, 1 ) )
    m_est_err[ 0 ] = m_est - m_est_low
    m_est_err[ 1 ] = m_est_hi - m_est 
    m_half_err = [ m_half - m_half_low, m_half_hi - m_half ]

    vc_est[ gal ] = [ np.sqrt( G * m_est / r_half ),
                      np.sqrt( G / r_half / m_est ) / 2. * m_est_err ,
                      r_half ]
    
    # vc_err has to take into account the partials
    plt.loglog( rm, m, linewidth = None )
    plt.fill_between( rm, mlow, mhi, color = '0.7' )
    plt.loglog( rm, m, 'k' )
    plt.errorbar( r_half, m_est, yerr = m_est_err.T, fmt = None, ecolor = 'k' )
    plt.loglog( r_half, m_est, 'k.' )

    # write out comparison for table
    # galaxy, m_est, -err, +err, m_half, -err, +err
    
    out = gal + ' '
    out += str( m_est ) + ' ' + str( m_est_err[ 0 ][ 0 ] ) + ' '
    out += str( m_est_err[ 1 ][ 0 ] ) + ' ' + str( m_half ) + ' '
    out += str( m_half_err[ 0 ] ) + ' ' + str( m_half_err[ 1 ] ) + '\n'
    f_compare.write( out )

    # adjusting the plots
    ax = plt.gca()
    plt.xlim( xrange[ iplt - 1 ] )
    plt.ylim( mrange[ iplt - 1 ] )

    plt.text( 0.1, 0.9, gal[ 0 ].upper() + gal[ 1: ],
              transform = ax.transAxes )
    
    iplt += 1

# more tinkering
fig.text( 0.02, 0.7, '$\mathrm{Enclosed} \, \mathrm{Mass} \, (M_{\odot})$',
          rotation = 'vertical', fontsize = '16' )
fig.text( 0.5, 0.02, '$r \, (\mathrm{pc})$', fontsize = '16' )
plt.savefig( 'mplot_4p.ps' )

# now the Vc figure
plt.clf()
iplt = 1
color = [ 'r', 'b', 'g', 'k' ]
yp = [ 0.3, .22, .14, .06 ]
for gal in gallist:
    rvc, vclow, vc, vchi = readcol( gal + '.vc', twod = False )
    rvcp = rvc / 1000.
    plt.fill_between( rvcp[ rvc < xrange[ iplt - 1 ] [ 1 ] ],
                      vclow[ rvc < xrange[ iplt - 1 ] [ 1 ] ],
                      vchi[ rvc < xrange[ iplt - 1 ] [ 1 ] ],
                      color = color[ iplt - 1 ] )
    plt.plot( vc_est[ gal ][ 2 ] / 1000., vc_est[ gal ][ 0 ],
              color[ iplt - 1 ] + 'o' )
    plt.errorbar( vc_est[ gal ][ 2 ] / 1000., vc_est[ gal ][ 0 ],
                  yerr = vc_est[ gal ][ 1 ][ 0 ],
                  fmt = None, ecolor = 'k' )
    ax = plt.gca()
    plt.text( 0.8, yp[ iplt - 1 ], gal[ 0 ].upper() + gal[ 1: ],
              transform = ax.transAxes, color = color[ iplt - 1 ],
              fontsize = '16' )

    iplt += 1
    

plt.ylim( [ 0, 40 ] )
plt.ylabel( '$V_c \, (\mathrm{km} \, \mathrm{s}^{-1})$', fontsize = '16' )
plt.xlabel( '$r \, (\mathrm{kpc})$', fontsize = '16' )
plt.savefig( 'vcplot.ps' )




# if I want to do a 4-panel thing later
"""
plt.clf()
fig2 = plt.figure()
iplt = 1

for gal in gallist:
    plt.subplot( 2, 2, iplt )
    rvc, vclow, vc, vchi = readcol( gal + '.vc', twod = False )
    rvc /= 1000.
    plt.plot( rvc, vc, linewidth = None )
    plt.fill_between( rvc, vclow, vchi, color = '0.7' )
    plt.plot( rvc, vc, 'k' )
    #plt.ylim( [ 1, 50 ] )
    plt.xlim( ( xrange[ iplt - 1 ][ 0 ] / 1e3  ), xrange[ iplt - 1 ][ 1 ] / 1e3 )
    plt.ylim( vrange[ iplt - 1 ]
    iplt += 1

plt.savefig( 'vcplot_4p.ps' )
"""
