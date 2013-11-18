import numpy as np
import psycopg2 as sql
import matplotlib.pyplot as plt
import cPickle as pickle
import csv

class ChiPlotter:
    def __init__( self, galname, scalingFile, deltaChiBase = None ):
        self.galname = galname
        self.scaling = self.get_scaling( scalingFile )

        self.dbPath = 'dbname=gebhardt_modelresults user=jardel host=db.corral.tacc.utexas.edu'

        self.queryDB()
        self.get_binLocations()
        self.calcChi()

    def get_scaling( self, scalingFile ):
        # get scaling factor for chi^2 in the galaxy under study
        
        fp = open( scalingFile )
        for line in fp:
            if line.split()[ 0 ] == self.galname:
                return float( line.split()[ 1 ] )

        #  if galname not found, complain
        raise ValueError( 'Galaxy name not found in scaling file' )
        

    def get_chiLim( self, conn, cursor, deltaChiBase = 5.84 ):
        # get chi^2 threshold below which models are in 1-sigma band.
        # uses default chi^2 threshold for 5 degrees of freedom.

        deltaChi = deltaChiBase / self.scaling # have to scale it 

        # =======================================================================
        # PSQL QUERY TO GET MINIMUM CHI^2
        query = """SELECT modnum, chi FROM results WHERE
        chi = ( select min( chi ) FROM results WHERE
        chi != 0 AND galname = ( %s ) )"""
        # =======================================================================
        
        cursor.execute( query, [ self.galname ] )
        bestMod, bestChi = cursor.fetchone()

        return bestChi + deltaChi
        

    def queryDB( self, nVelBins = 15, deltaChiBase = None, nBins = 5 ):
        # get results from PostgreSQL DB.  nVelBins set to default number of
        # velocity bins in LOSVDs
        
        conn = sql.connect( self.dbPath )
        cursor = conn.cursor()
        chiLim = self.get_chiLim( conn, cursor ) # chi^2 threshold

        # get LOSVDs for models below threshold

        # =======================================================================
        # PSQL QUERY TO GRAB ALL THE LOSVDS
        query = """SELECT t.data, t.data_hi, t.data_low, t.model FROM
        %(name)s_losvd AS t JOIN %(name)s_results ON
        t.modnum = %(name)s_results.modnum AND %(name)s_results.chi != 0 AND
        %(name)s_results.chi < """ % {"name":self.galname}
        query += "(%s);"
        # =======================================================================
        
        cursor.execute( query, ( chiLim, ) )
        losvds = np.array( cursor.fetchall() )

        # find number of 1-sigma models

        # =======================================================================
        # PSQL QUERY TO COUNT THE NUMBER OF MODELS
        query = """SELECT COUNT( DISTINCT t.modnum  ) FROM %(name)s_losvd AS t JOIN
        %(name)s_results ON t.modnum = %(name)s_results.modnum AND
        %(name)s_results.chi != 0 AND
        %(name)s_results.chi < """ % {"name":self.galname}
        query += "(%s);"
        # =======================================================================

        cursor.execute( query, ( chiLim, ) )
        nModels = int( cursor.fetchone()[ 0 ] ) # returns long int for some reason
        nLosvds = losvds.shape[ 0 ] / nModels / nVelBins 

        newLosvds = np.reshape( losvds,
                                ( nModels, nLosvds, nVelBins, losvds.shape[ 1 ] ) )

        # grab parameters (density profiles) from best models
        
        # =======================================================================
        # PSQL QUERY TO SELECT BEST DENSITY PROFILES
        query = """SELECT t.modnum, t.rk, t.rhok, %(name)s_results.chi FROM
        %(name)s_bin AS t JOIN %(name)s_results ON
        t.modnum = %(name)s_results.modnum AND %(name)s_results.chi != 0 AND
        %(name)s_results.chi < """ % {"name":self.galname}
        query += "(%s);"
        # =======================================================================

        cursor.execute( query, ( chiLim, ) )
        densTable = np.array( cursor.fetchall() )
        
        cursor.close()
        conn.close()

        # save outputs
        header = [ 'model', 'rk', 'rhok', 'chi' ]
        self.saveAsCSV( 'densityTable.csv', densTable, header )
        self.losvds = newLosvds

    def calcChi( self ):
        # calculate chi^2 in losvd locations
        
        losvds = self.losvds

        # need to calculate error bars
        errb1 = ( losvds[ :, :, :, 2 ] - losvds[ :, :, :, 1 ] ) / 2.
        errb2 = losvds[ :, :, :, 1 ] - losvds[ :, :, :, 0 ]

        # error bars asymmetric, choose biggest
        errb = np.max(
            np.column_stack( ( errb1.flatten(), errb2.flatten() ) ),
            axis = 1
            )
        
        errb = np.reshape( errb, losvds.shape[ :3 ] )

        # do the chi^2 calculation
        chi2 = np.sum( (
            losvds[ :, :, :, 0 ] - losvds[ :, :, :, 3 ] )**2 /
            errb**2, axis = 2
            )

        # save outputs
        self.chi2 = chi2
        #header = [ '{:5.2f}'.format( bin ) for bin in self.binLocations ]
        header = [ 'bin' + str( i + 1 ) for i in range( chi2.shape[ 1 ] ) ]
        self.saveAsCSV( 'losvds.csv', chi2, header )
        return

    def get_binLocations( self ):

        filename = self.galname + '_velbin.dat'
        fp = open( filename )
        binLocations = []        

        for line in fp:
            x = float( line.split()[ 1 ] )
            y = float( line.split()[ 2 ] )
            r = np.sqrt( x * x + y * y )
            binLocations.append( r )

        fp.close()
        self.binLocations = np.array( binLocations )
        self.saveAsCSV( 'binLocations.csv', ( binLocations, ) )
        return

    def jitter( self, xCoords ):
        # jitter points to make final plot look more like an image
        # -- DON'T USE THIS, CAUSES PROBLEMS WHEN USED WITH LOG SCALE

        binLocations = self.binLocations
        intervals1 = list( binLocations )
        intervals2 = list( binLocations[ 1: ] )
        intervals2.append( binLocations[ -1 ] + binLocations[ -2 ] )

        intervals = zip( intervals1, intervals2 )
        for bottom, top in intervals:
            nSamples = xCoords[ xCoords == bottom ].shape
            xCoords[ xCoords == bottom ] = np.random.uniform( bottom, top,
                                                              size = nSamples )
        return xCoords            
        

    def plot( self ):
        # make heatmap of contributions to chi^2 as a function of radius for
        # all models within 1-sigma

        plt.clf()
        chi2 = self.chi2
        binLocations = self.binLocations

        # convert chi^2 from z = f( x, y ) into list of points
        yCoords = chi2.flatten()
        xCoords = np.array(
            [ binLocations[ i ] for j in range( chi2.shape[ 0 ] )
            for i in range( chi2.shape[ 1 ] ) ]            
            )

        
        #xCoordsRand = self.jitter( xCoords ) -- NO!
        xCoords = np.log10( xCoords )

        # get 2D histogram of points
        xarr = np.linspace( np.min( xCoords ), np.max( xCoords ), num = 50 )
        yarr = np.linspace( 0, 5, num = 100 )
        H, x, y = np.histogram2d( xCoords, yCoords, bins = [ 30, 30 ] )
        extent = [ np.min( x ), np.max( x ), 0., 5. ]
        plt.imshow( H.T, extent = extent, aspect = 'auto', origin = 'lower',
                    interpolation = 'gaussian', cmap = 'hot' )
        plt.xlabel( 'log R' )
        plt.ylabel( '$\\chi^2$ $\\mathrm{per}$ $\\mathrm{LOSVD}$',
                    fontsize = 16 )
        
        ax = plt.gca()

        self.axesForPlot = ax
        return ax

    def plotHistogram( self, axis = None ):
        # show a given radial bin's 1D histogram.  Sometimes more insightful

        if axis is None:
            raise ValueError( 'must specify an axis' )
        
        chi2 = self.chi2
        hist = plt.hist( chi2[ :, axis ] )

        plt.xlabel( '$\\chi^2$ $\\mathrm{per}$ $\\mathrm{LOSVD}$' )
        plt.ylabel( 'Number of Models' )
        
        ax = plt.gca()

        self.histogram = ax
        return ax
        

    def save( self ):
        # save the whole object for testing purposes
        
        filename = self.galname + '.pkl'
        fp = open( filename, 'wb')
        pickle.dump( self, fp )
        
        fp.close()

    def saveAsCSV( self, filename, obj, header = None ):
        # write out to a csv file so I can do fancy things with R

        fp = open( filename, 'w' )
        writer = csv.writer( fp )

        if header is not None:
            writer.writerow( header )
            
        for row in obj:
            writer.writerow( row )

        fp.close()

        

def main( **kwargs ):
    galaxyList = kwargs[ 'galaxyList' ]
    galaxyList.sort()

    plt.clf()
    fig = plt.figure()
    plt.subplot( 2, 3, 1 ).axis( 'off' )

    igal = 2
    for gal in galaxyList:
        galaxy = ChiPlot( gal, kwargs[ 'scalingFile' ] )
        plot = galaxy.plot()
        plt.subplot( 2, 3, igal )
        print gal + ' done'
        galaxy.save()
        igal += 1

    plt.savefig( 'chi2plot.png' )
    return 0

if __name__ == '__main__':
    kwargs = { 'galaxyList':
             [ 'draco', 'carina', 'fornax', 'sculptor', 'sextans' ],
             'scalingFile': 'scaling.dat' }
    main( **kwargs )
    
