import npsm_common as npsm
import matplotlib.pyplot as plt

plt.clf()
fig = plt.figure()


gallist = [ 'All', 'Fornax', 'Carina', 'Sextans', 'Sculptor', 'Draco' ]
gallist.sort()

#plt.subplot( 2, 3, 1 ).axis( 'off' )

iplt = 1
for galname in gallist:
    plt.subplot( 2, 3, iplt )
    
    if iplt == 1 or iplt == 4:
        left = True
    else:
        left = False
    if iplt > 3:
        bottom = True
    else:
        bottom = False
    bottom = True
    
    gal = npsm.Galaxy( galname )
    if galname != 'Fornax':
        gal.plot_dmprof( left, bottom )
    else:
        gal.plot_dmprof2( left, bottom )
    
    
    # call special method for plot_fnx

    iplt += 1

plt.subplots_adjust( hspace = 0.2, wspace = 0. )
fig.text( 0.02, 0.5, '$\\rho_{DM} \, (M_{\odot} \, \mathrm{pc}^{-3})$',
          rotation = 'vertical', fontsize = '16' )
fig.text( 0.5, 0.02, '$r$ $\\mathrm{(pc)}$', fontsize = '16' )
plt.savefig( 'all_combined.ps' )
