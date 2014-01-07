from readcol import readcol
import numpy as np
import sys
import math as m
import os
from itertools import product

class Results:
    def __init__( self, **kwargs ):
        pass

    def getResults( self, **kwargs ):
        nk = kwargs[ 'nk' ]
        filename = kwargs[ 'resFilePath' ]
        
        dens = []
        slope = []
        bh = []
        
        fp = open( filename )
        for line in fp:
            dens.append( [ float( x ) for x in line.split()[ :nk ] ] )
            slope.append( float( line.split()[ nk + 2 ] ) )
            bh.append( float( line.split()[ nk + 1 ] ) )

        fp.close()

        self.dens = np.array( dens )
        self.slope = np.array( slope )
        self.bh = np.array( bh )
        self.res = np.column_stack( ( np.array( dens ), np.array( slope ),
                                      np.array( bh ) ) )
        
        
class Models( Results ):

    def __init__( self, allModels, **kwargs ):
        self.allModels = allModels
        self.getResults( **kwargs )

    def checkForDups( self, **kwargs ):

        goodModels = []
        for model in self.allModels:
            if not self.inResults( model, **kwargs ):
                goodModels.append( model )

        return goodModels
    
    def inResults( self, model, **kwargs ):
        # can't use np.close because of old shitty numpy on TACC

        results = self.res
        for resModel in results:
            if self.isclose( model, resModel, **kwargs ):
                return True

        return False

    def isclose( self, testMod, resMod, **kwargs ):
        # check if model to be run is close to a model in res.tab
        
        tol = kwargs[ 'tol' ]
        flag = True

        for a, b in zip( testMod, resMod ):
            if abs( float( a ) / b - 1 ) > tol:
                return False


        return flag



class Grid:
    def __init__( self, **kwargs ):
        self.readParamFiles( **kwargs )
        self.getCombinations( **kwargs )
        if kwargs[ 'monotonic' ]:
            self.onlyMonotonic( **kwargs )


    def readParamFiles( self, **kwargs ):
        self.readGridFile( **kwargs )
        self.readSlopeFile( **kwargs )
        if kwargs[ 'includeBHs']:
            self.readBHFile( **kwargs )

    def readGridFile( self, **kwargs ):

        # gridFile is organized as:
        # binNumber rhoStart rhoEnd nSteps

        gridFile = kwargs[ 'gridFilePath' ]
        nbins = kwargs[ 'nk' ]
        

        fp = open( gridFile )
        rho = []
        for line in fp:
            row = []
            for item in line.split()[ 1:3 ]:
                row += [ float( item ) ]
            row += [ int( line.split()[ 3 ] ) ]
            rho.append( row )

        fp.close()
        self.rhodata = rho

    def readSlopeFile( self, **kwargs ):
         # slope file is one line organized as:
         # slopeStart slopeEnd nSlopes

        slopeFile = kwargs[ 'slopeFilePath' ]

        with open( slopeFile ) as fp:
            line = fp.readline().split()

        slope = []
        slope += [ float( item ) for item in line[ 0:2 ] ]
        slope += [ int( line[ 2 ] ) ]

        self.slopedata = slope

    def readBHFile( self, **kwargs ):
        # BH file is one line organized as :
        # BHstart BHend, nBHs

        bhFile = kwargs[ 'bhFilePath' ]

        with open( bhFile ) as fp:
            line = fp.readline().split()

        bh = []
        bh += [ float( item ) for item in line[ 0:2 ] ]
        bh += int( line[ 2 ] )

        self.bhdata = bh

    def getCombinations( self, **kwargs ):

        arg = []

        # build list with each bin's values to sample
        for k in self.rhodata:
            x = np.logspace( np.log10( k[ 0 ] ), np.log10( k[ 1 ] ),
                                                           num = k[ 2 ] )
            arg.append( x.tolist() )

        # add slopes
        slopes = self.slopedata
        x = np.linspace( slopes[ 0 ], slopes[ 1 ], num = slopes[ 2 ] )
        arg.append( x.tolist() )

        #add BHs
        if kwargs[ 'includeBHs' ]:
            bhs = slopes.bhdata
            x = np.logpace( np.log10( bhs[ 0 ] ), np.log10( bhs[ 1 ] ),
                            num = bhs[ 2 ] )
            arg.append( x.tolist() )

        gModels = product( *arg ) # this is a generator
        models = []
        for i in gModels:
            models.append( i )

        self.models = models

    def onlyMonotonic( self, **kwargs ):

        # if we only monotonically decreasing profiles, scrub the ones
        # out of order
        
        nk = kwargs[ 'nk' ]
        newmodels = []
        for i in self.models:
            if list( i[ :nk ] ) == sorted( i[ :nk ], reverse = True ):
                newmodels.append( list( i ) )

        self.models = newmodels

class Launcher:

    def __init__( self, modelsToRun, **kwargs ):
        self.models = modelsToRun
        self.initializeScripts( **kwargs )

        self.loopOverModels( nBatchMax = 96, **kwargs )

    def initializeScripts( self, **kwargs ):
        sgeFile = open( kwargs[ 'sgeFilePath' ] )
        sgeTemplate = sgeFile.readlines()
        self.sgeTemplate = sgeTemplate

        smodlist = os.listdir( kwargs[ 'modlistsDir' ] )
        modlist = []
        for mod in smodlist:
            if 'model' in mod and '.bin' in mod:
                t1 = mod.replace( 'model', '' )
                t2 = t1.replace( '.bin', '' )
                modlist.append( int( t2 ) )

        if not modlist:
            self.iStart = 1
        else:
            self.iStart = max( modlist ) + 1

        print 'starting with model' + ( str( self.iStart ) ).rjust( 5, '0' ) + '.bin'

        # get radii for bins from param2np output
        paramFile = open( kwargs[ 'paramFilePath' ] )
        radius = []
        for line in paramFile:
            radius.append( float( line.split()[ 0 ] ) )

        self.radius = radius

        if len( radius ) != kwargs[ 'nk' ]:
            raise InputError( "your param2np output doesn't have the same number of elements as 'nk' in kwargs" )



    def loopOverModels( self, nBatchMax = None, **kwargs ):
        models = self.models
        modlistsDir = kwargs[ 'modlistsDir' ]
        nk = kwargs[ 'nk' ]

        i = self.iStart
        kount = 1
        nBatch = 0

        # need to write to slope.list and bh.list too
        slopeFilePath = modlistsDir + '/slope.list'
        bhFilePath = modlistsDir + '/bh.list'

        slopeFile = open( slopeFilePath, 'a' )
        bhFile = open( bhFilePath, 'a' )


        for model in models:
            if kount % nBatchMax == 1:

                # sloppy way to close the first batch file
                try:
                    batchFile.close()
                except:
                    pass
                
                nBatch += 1
                batchFile, submitFile = self.openBatchFiles( nBatch,
                                                             nBatchMax = nBatchMax
                                                             )
                
                os.chmod( batchFile.name, 0754 )
                self.mkSubmitFile( nBatchMax, batchFile.name, submitFile )
                submitFile.close()

            # write out modlist file
            sModel = str( i ).rjust( 5, '0' )
            
            modFile = modlistsDir + '/model' + sModel
            out = np.column_stack( ( self.radius, model[ :nk ] ) )
            np.savetxt( modFile, out, fmt = '%-5.5f %-5.5e' )

            # write to slope file
            sSlope = str( model[ nk ] )
            slopeFile.write( sModel + ' ' + sSlope + '\n')

            # if using BH
            if kwargs[ 'includeBHs' ]:
                sBH = ':e5.5'.format( model[ nk + 1 ] )
            else:
                sBH = '0'

            bhFile.write( sModel + ' ' + sBH + '\n')
            out = 'runall.s %(model)s %(slope)s %(bh)s \n' % { 'model': sModel,
                                                               'slope': sSlope,
                                                               'bh': sBH
                                                               }

            batchFile.write( out ) # write the line in runbatchXX.s
            i += 1
            kount += 1
            
        batchFile.close()
        slopeFile.close()
        bhFile.close()

        # need to fix the last SGE file
        dummy, submitFile = self.openBatchFiles( nBatch, justSGE = True )
        numProcs = ( kount - 1 )% nbatchmax
        numProcs = int( m.ceil( numProcs / 12. ) * 12. )
        batchName = submitFile.name[ :-3 ] + 's'
        self.mkSubmitFile( numProcs, batchName, submitFile )
        submitFile.close()

        
    def openBatchFiles( self, nBatch, nBatchMax = None, justSGE = False ):

        base = 'runbatch' + str( nBatch ).rjust( 2, '0' )
        
        if not justSGE:
            fBatch = open( base + '.s', 'w' )
        else:
            fBatch = None

        fSubmit = open( base + '.sge', 'w' )
        
        return fBatch, fSubmit # each is file object designated for writing
        
    def mkSubmitFile( self, maxProcs, batchName, fSubmit ):
        template = self.sgeTemplate
        template[ 16 ] = template[ 16 ][ :13 ] + str( maxProcs ) + '\n'
        template[ 37 ] = template[ 37 ][ :22 ] + batchName + '\n'

        for line in template:
            fSubmit.write( line )
    

    
def main( **kwargs ):

    grid = Grid( **kwargs )
    models = Models( grid.models, **kwargs )
    toRun = models.checkForDups( **kwargs )

    launcher = Launcher( toRun, **kwargs )

    
        
        
        
if __name__ == '__main__':

    kwargs = { 'nk': 5,
               'includeBHs': False,
               'resFilePath': 'result/res.tab',
               'gridFilePath': 'grid.in',
               'slopeFilePath': 'slope.in',
               'sgeFilePath': 'runbatch.sge',
               'paramFilePath': 'param/mod.param.bin',
               'modlistsDir': './modlists',
               'monotonic': True,
               'tol':  5e-2
               }

    main( **kwargs )
    
