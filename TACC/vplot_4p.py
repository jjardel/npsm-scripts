from readcol import readcol
import matplotlib.pyplot as plt
import numpy as np

plt.clf()
gallist = [ 'carina', 'fornax', 'sculptor', 'sextans' ]
fig = plt.figure()
iplt = 1
for gal in gallist:
    plt.subplot( 2, 2, iplt )
    r, vrvt_low, vrvt_hi = readcol( gal + '.aniso', twod = False )
    vrvt_mean = [ np.mean( i ) for i in zip( vrvt_low, vrvt_hi ) ]
    plt.semilogx( r, vrvt_mean, linewidth = None )
    plt.fill_between( r, vrvt_low, vrvt_hi, color = '0.7' )
    plt.semilogx( r, vrvt_mean, 'k' )
    plt.ylim( [ 0, 2 ] )
    plt.autoscale( axis = 'x', tight = True )
    ax = plt.gca()
    plt.text( 0.1, 0.9, gal[ 0 ].upper() + gal[ 1: ],
              transform = ax.transAxes )
    
    
    iplt += 1
fig.text( 0.02, 0.5, '$\\sigma_r/\sigma_t$',
          rotation = 'vertical', fontsize = '16' )
fig.text( 0.5, 0.02, '$r \, (\mathrm{pc})$', fontsize = '16' )

plt.savefig( 'aniso.ps' )
