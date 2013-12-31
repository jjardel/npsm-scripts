import npsm_common as npsm
import matplotlib.pyplot as plt

plt.clf()

gal = npsm.Galaxy( 'Sextans' )

fig = plt.figure()
subp = gal.plot_dmprof( bottom = True, left = True )

#fig = plt.figure()
#fig.add_subplot( 2, 1, 1 )
#subp = gal.plot_dmprof()
#fig.add_subplot( 2, 1, 2 )
#subp = gal.plot_dmprof()


plt.savefig( 'test.ps' )
