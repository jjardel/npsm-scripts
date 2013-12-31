import matplotlib.pyplot as plt
import numpy as np
from readcol import readcol
import sys
import math as m
import scipy

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
        #sys0.exit
        
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

    def plot_dmprof2( self, left = False, bottom = False ):
        """ make a single plot with the correct environment for a single
        galaxy\n 
        Returns an Axes object"""

        r = np.array( self.r ) * self.dis / 206265.
        r2 = np.array( self.r2 ) * self.dis / 206265.
        plt.loglog( self.r, self.dm, linewidth = None )
        plt.xlim( [ x * self.dis / 206265 for x in self.xrange ] ) 
        plt.ylim( self.yrange )

        rhol2 = np.array( self.dmlo2 )
        rhoh2 = np.array( self.dmhi2 )
        
        rs, stars, stars_err = readcol( 'stars.out', twod = False )

        dmhi2 = rhoh2 - stars
        dmlo2 = rhol2 - stars

        #badlist = np.where( rhol2 < ( stars + stars_err ) )[ 0] 
        badlist = np.where( dmlo2 - ( stars + stars_err ) < 0 )[ 0 ]
        badstart = badlist[ 0 ]
        badend = badlist[ -1 ]


        stars5 = np.interp( r, rs, stars )
        stars5_err = np.interp( r, rs, stars_err )
        
        dm = np.array( self.dm ) - stars5
        rho_err_temp = np.array( self.dmhi ) - np.array( self.dm )
        dm_err = ( rho_err_temp**2 + stars5_err**2 )**( 0.5 )
                


        #sys0.exit()

        # what I think is DM is actually rho since dsphdm_fnx spits out rho

        
        plt.fill_between( r2[ :badstart ], dmlo2[ :badstart], 
                          dmhi2[ :badstart ], color = '0.7' )
        plt.fill_between( r2[ badend + 1: ], dmlo2[ badend + 1: ], 
                          dmhi2[ badend + 1: ], color = '0.7' )


        plt.fill_between( rs, stars - stars_err, stars + stars_err, 
                          color = 'r' )



        inner = np.arange( 0, self.n_inner )
        outer = np.arange( self.n_inner, self.n_inner + self.n_outer )

        # **** HEADS UP ***
        # I'm hard-coding outer to skip the one negative point in Fnx
        outer = np.arange( 3, 5 )
        # ***           ***

        rho_err = np.array( self.dmhi ) - np.array( self.dm )
        rho = np.array( self.dm )

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



    def plot_dmprof_all( self, left = False, bottom = False,
                         icolor = 0):
        """ Plot all scaled DM profiles on the same axes"""
        
        inner = np.arange( 0, self.n_inner )
        outer = np.arange( self.n_inner, self.n_inner + self.n_outer )

        color = [ 'r', 'b', 'g', 'k', 'y' ]
        
        r = np.array( self.r ) * self.dis / 206265.
        dm = np.array( self.dm )
        dm_100 = np.interp( m.log10( 100. ), np.log10( r ), np.log10( dm ) )
        dm_100 = 10**dm_100

        dm_err_abs = np.array( self.dmhi ) - np.array( self.dm )
        dm_err = .434 * dm_err_abs / dm

        fiducial = lambda x: 2 - x
        fiducial = np.vectorize( fiducial )
        fiducial_dens = fiducial( np.linspace( -2., 2. ) )
        fiducial_100 = np.interp( np.log10( 100. ), np.linspace( -2., 2. ),
                                  fiducial_dens )

        # trying to find normalization by minimizing chi^2 wrt r^-1 powerlaw
        
        y = np.log10( dm )
        x = np.log10( r )
        
        fitfunc = lambda p, x: p[ 0 ] -1. * x
        errfunc = lambda p, x, y, err: ( y - fitfunc( p, x ) ) / err 

        pinit = [ 1.0 ]
        out = scipy.optimize.leastsq( errfunc, pinit, args = ( y, x, dm_err ),
                                      full_output = 1 )
        p = out[ 0 ]
        
        y_100 = p[ 0 ] -1. * np.log10( 100 )

        yscale = y_100 - fiducial_100
        r = np.log10( r/ 100. )
        dm = np.log10( dm )
        dm -= yscale

        """
        dm *= yscale

        #dm_err *= yscale

        r /= 100.
        

        """
        plt.errorbar( r, dm, yerr = dm_err, ecolor = 'k', fmt = None )
        plt.plot( r, dm, color[ icolor ] + 'o' )
        #plt.plot( r, dm, color = color[ icolor ] )
        #plt.loglog( [ 100. ], rho_100, color[ icolor ] + 'o' )
        plt.xlim( [ -2, 2 ] )
        plt.ylim( [ -2, 2 ] )


        """
        # --- draw NFW line
        x1 = np.log10( 5. * plt.xlim()[ 0 ] )
        x2 = np.log10( .5 * plt.xlim()[ 1 ] )
        y1 = np.log10( .2 * plt.ylim()[ 1 ] )
        y2 = -1. * ( x2 - x1 ) + y1
        plt.loglog( [ 10**x for x in [ x1, x2 ] ], 
                    [ 10**y for y in [ y1, y2 ] ], 'k--' )
        """
        #plt.plot( [ -2., 2.], [2., -2.], 'k--' )

        yp = [ 0.9, 0.85, 0.8, 0.75, 0.7 ]

        ax = plt.gca()
        plt.text( 0.8, yp[ icolor ], self.galname, transform = ax.transAxes,
                  color = color[ icolor ])

        # don't forget to move temp to common_prof.out once all the dSphs 
        # are run

        f = open( 'temp.out', 'a' )
        for i, j, k in zip( r[ outer ], dm[ outer ], dm_err[ outer ] ):
            out = str( i ) + ' ' + str( j ) + ' ' + str( k ) + '\n'
            f.write( out )
        f.close()
        
        # HARD CODED TO BEST SLOPE/INTERCEPT FIT BY PLOT_COMMON_PROF.PY

        m_slope = -1.2
        b = 0.084

        m_slope_outer = -0.9
        b_outer = -.1
        
        def y_best_fit( x, m_slope, b ):
            return m_slope * x + b
        
        y = np.vectorize( y_best_fit )
        y_plot = y( np.linspace( -1.5, 1.5 ), m_slope, b )
        y_plot_outer = y( np.linspace( -1.5, 1.5 ), m_slope_outer, b_outer )
        plt.plot( np.linspace( -1.5, 1.5 ), y_plot, 'k--' )
        plt.plot( np.linspace( -1.5, 1.5 ), y_plot_outer,
                  'k', linestyle = 'dashdot' )

        plt.plot( [ -1.5, 1.5 ], [ 1.5, -1.5 ], 'r--' )
        plt.text( -1.88, 1.5, '$\\rho \\propto r^{-1}$' )
        plt.text( -1.88, 1.8, '$\\rho \\propto r^{-1.2}$' )
        plt.text( -1.88, 1.2, '$\\rho \\propto r^{-0.9}$' )
        
        return ax
