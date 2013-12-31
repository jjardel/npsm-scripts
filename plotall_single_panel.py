import npsm_common as npsm
import matplotlib.pyplot as plt

plt.clf()
fig = plt.figure()


gallist = [ 'Fornax', 'Carina', 'Sextans', 'Sculptor', 'Draco' ]
gallist.sort()

iplt = 2
for galname in gallist:
    
    if iplt == 2 or iplt == 4:
        left = True
    else:
        left = False
    if iplt > 3:
        bottom = True
    else:
        bottom = False
    bottom = True
    
    gal = npsm.Galaxy( galname )
    gal.plot_dmprof_all( left, bottom, icolor = iplt - 2 )
    
    iplt += 1

#fig.text( 0.02, 0.5, '$\\rho_{DM} \, (M_{\odot} \, \mathrm{pc}^{-3})$',
#          rotation = 'vertical', fontsize = '16' )
#fig.text( 0.5, 0.02, '$r$ $\\mathrm{(pc)}$', fontsize = '16' )
plt.xlabel( '$ \\log \, r / 100$ $\\mathrm{pc}$', fontsize = '16' )
plt.ylabel( '$\\log \, \\rho_{DM} \,$' '$ \\mathrm{(arbitrary} \,$' 
            '$\mathrm{units)}$', fontsize = '16' )
plt.savefig( 'all_in_one.ps' )
