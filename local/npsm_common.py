import matplotlib.pyplot as plt
import numpy as np

class Galaxy:
    def __init__( self, galname ):
        self.n_inner = 0
        self.n_outer = 0
        self.dis = 0
        self.xrange = [ 0, 0 ]
        self.yrange = [ 0, 0 ]
        self.kinrange = [ 0, 0 ]
        self.r = []
        self.dmlo = []
        self.dm = [] 
        self.dmhi = []
        self.r2 = []
        self.dmlo2 = []
        self.dm2 = []
        self.dmhi2 = []
        self.best_slope = 0
        self.best_slope_err = 0
        self.best_int = 0
        self.best_int_err = 0 
        self.galname = galname

        # --- read data
        self.readres( galname )

    def readres( self, galname ):
        """ Subroutine to read in .res file as formatted by dsphdm.py"""

        f = open( galname + '.res' )
        line = f.readline()
        self.n_inner = int( line.split()[ 0 ] )
        self.n_outer = int( line.split()[ 1 ] )
        line = f.readline()
        self.dis = float( line.split()[ 0 ] )
        line = f.readline()
        self.xrange = [ float( x ) for x in line.split()[ :2 ] ]
        line = f.readline()
        self.yrange = [ float( x ) for x in line.split()[ :2 ] ]
        line = f.readline()
        self.kinrange = [ float( x ) for x in line.split()[ :2 ] ]
        f.readline()
        for i in range( 0, self.n_inner + self.n_outer ): 
            line = f.readline()
            self.r.append( float( line.split()[ 0 ] ) )
            self.dmlo.append( float( line.split()[ 1 ] ) )
            self.dm.append( float( line.split()[ 2 ] ) )
            self.dmhi.append( float( line.split()[ 3 ] ) )
        line = f.readline()
        line = f.readline()
        while line != 'EOF\n':
            self.r2.append( float( line.split()[ 0 ] ) )
            self.dmlo2.append( float( line.split()[ 1 ] ) )
            self.dm2.append( float( line.split()[ 2 ] ) )
            self.dmhi2.append( float( line.split()[ 3 ] ) )
            line = f.readline()
        line = f.readline()
        self.best_slope = float( line.split()[ 0 ] )
        self.best_slope_err = float( line.split()[ 1 ] )
        line = f.readline()
        self.best_int = float( line.split()[ 0 ] )
        self.best_int_err = float( line.split()[ 1 ] )
        
        return

    def plot_dmprof( self, left = False, bottom = False ):
        """ make a single plot with the correct environment for a single
        galaxy\n 
        Returns an Axes object"""

        r = np.array( self.r ) * self.dis / 206265.
        r2 = np.array( self.r2 ) * self.dis / 206265.
        plt.loglog( self.r, self.dm, linewidth = None )
        plt.xlim( [ x * self.dis / 206265 for x in self.xrange ] ) 
        plt.ylim( self.yrange )

        dmlo2 = np.array( self.dmlo2 )
        dmhi2 = np.array( self.dmhi2 )
        
        bad = np.where( dmlo2 < 0 )
        nbad = len( bad[ 0 ] )
        
        
        plt.fill_between( r2, dmlo2, dmhi2, color = '0.7' )
        #if self.galname == 'Fornax':
        #    plt.fill_between( r2[ bad ], 1e-10 * np.ones( nbad ), 
        #                      dmhi2[ bad ], color = '1.' )
        inner = np.arange( 0, self.n_inner )
        outer = np.arange( self.n_inner, self.n_inner + self.n_outer )

        dm_err = np.array( self.dmhi ) - np.array( self.dm )
        dm = np.array( self.dm )

        plt.errorbar( r[ inner ], dm[ inner ], dm_err[ inner ], 
                      fmt = 'x', color = '0.3', ecolor = '0.3' )
        plt.errorbar( r[ outer ], dm[ outer ], dm_err[ outer ],
                      fmt = '.', color = '0.', ecolor = '0.' )
        
        
        # --- set kinrange indicators
        x1 = self.kinrange[ 0 ] * self.dis / 206265.
        x2 = self.kinrange[ 1 ] * self.dis / 206265.
        plt.loglog([ x1, x1 ],
                   [ plt.ylim()[ 0 ], 2. * plt.ylim()[ 0 ] ], 'k' )
        plt.loglog([ x2, x2 ],
                   [ plt.ylim()[ 0 ], 2. * plt.ylim()[ 0 ] ], 'k' )
  

        # --- draw NFW line
        x1 = np.log10( 5. * plt.xlim()[ 0 ] )
        x2 = np.log10( .5 * plt.xlim()[ 1 ] )
        y1 = np.log10( .2 * plt.ylim()[ 1 ] )
        y2 = -1. * ( x2 - x1 ) + y1
        plt.loglog( [ 10**x for x in [ x1, x2 ] ], 
                    [ 10**y for y in [ y1, y2 ] ], 'k--' )
                           

        ax = plt. gca()
        if not left:
            ax.set_yticklabels( [] )
        if not bottom:
            ax.set_xticklabels( [] )
            
        plt.text( 0.6, 0.9, self.galname, transform = ax.transAxes )

        return ax
