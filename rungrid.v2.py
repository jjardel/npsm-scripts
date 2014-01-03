from product import product as product2
from readcol import readcol
import numpy as np
import sys
import math as m
import os
from datetime import datetime
from itertools import product

# ---------------
# PARAMETER BLOCK
nbatchmax = 96
nsteps = 5
#----------------

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

    def mkSGEfile( self, **kwargs ):
        pass

    def mkrunallFile( self, **kwargs ):
        pass

    def updateLog( self, **kwargs ):
        pass
    

    
def main( **kwargs ):

    grid = Grid( **kwargs )
    models = Models( grid.models, **kwargs )
    toRun = models.checkForDups( **kwargs )

    import pdb; pdb.set_trace()
    
        
        
        
if __name__ == '__main__':

    kwargs = { 'nk': 5,
               'includeBHs': False,
               'resFilePath': 'result/res.tab',
               'gridFilePath': 'grid.in',
               'slopeFilePath': 'slope.in',
               'monotonic': True,
               'tol':  5e-2
               }

    main( **kwargs )
    

# in __main__ do
#
# 1.  gridtorun = grid()
# 2.  newmodels = grid.someMethodToGetNewModels()
# 3.  mksgeFile and other scripts
# 



sys.exit()

def mksgeFile():
    pass


def repcheck( x, slope, nk=7, imono = 0, eps = 5e-2):
# check if duplicate in density profile + outer slope
# returns True if density profile is a duplicate
# Argument imono=1 requires the profile to be monotonic

    if( imono ==1 ):
        if( x != sorted( x, reverse = True ) ):
            return True
    
    try:
        resfil = open('result/res.tab')
    except:
        return False

    x.append( slope )
    res = resfil.readlines()
    retval = False
    for line in res:
        test = []
        for item in line.split()[ 0:nk ]:
            test.append( float( item ) )
        test.append( float( line.split()[ nk + 2 ] ) )
        flag = True
        for a, b in zip(test, x):
            if( abs( float( a ) / b - 1 ) > eps):
                flag = False
        if flag:
            return flag   
            
    return flag
# ---------

# -- read in grid file

gridfile = open( 'grid.in' )
temp = gridfile.readlines()
nbins = len( temp )
gridfile.seek( 0 )
bin = zeros( nbins )
rhostart = zeros( nbins )
rhoend = zeros( nbins )
i = 0
for line in gridfile:
    bin[ i ] = int( line.split()[ 0 ] )
    rhostart[ i ] = float( line.split()[ 1 ] )
    rhoend[ i ] = float( line.split()[ 2 ] )
    i += 1

slope = []
slopefile = open( 'slope.in' )
for line in slopefile:
    slope.append( float( line ) )



# get latest modlist

smodlist = os.listdir( './modlists' )
modlist = []
for x in smodlist:
    if 'model' in x and '.bin' in x:
        t1 = x.replace( 'model', '' )
        t2 = t1.replace( '.bin', '' )
        modlist.append( int( t2 ) )

if( len( modlist ) > 0 ):
    istart = max( modlist ) + 1
else:
    istart = 1
print 'starting with model' + ( str( istart ) ).rjust( 5, '0' ) + '.bin'


    
#-------------------------------------------------
# INTERPRET BEST MODEL FROM TABLE IN RESULT (PRODUCED BY NEW
# RUNALL.S)

newstart = 0
try:
    resf = open( 'result/res.tab', 'r' )
except:
    print 'no res.tab file found, starting a new one...'
    newstart = 1

    if( istart != 1 ):
        print 'ERROR: no res.tab file found, but modlists dir not empty'
        sys.exit( 0 )

bestf = open( 'param/mod.param.bin' )
rk = []
rho = []
for line in bestf:
    rk.append( float( line.split()[0] ) )
    if( newstart ):
        rho.append( float( line.split()[ 1 ] ) )
bestf.close()
nk = len( rk )

#INITIALIZE DICTIONARY WHERE NK RHO ELEMENTS ARE STORED ACCORDING TO
# MODEL NUMBER
if( not newstart ):
    resin = resf.readlines()
    resdict = {}
    for line in resin:
        chi = float( line.split()[nk+3] )
        rho = []
        for i in line.split()[ :nk ]:
            rho.append( float( i ) )
        resdict[ chi ] = rho

# this is where I left off.  get 2D array with res, slope I can pass to
# repcheck later.


# check to see modlist is as long as restab, otherwise issue warning
    k = len( resdict.keys() )
    if( istart - 1 != k  ):
        print 'WARNING!! ', k, ' entries in res.tab but ', istart - 1, 'entries in modlists'

#-------------------------------------------------
    chimin = min( resdict.keys() )
    rhok = array( resdict[ chimin ][ :nk ] )
else:
    rhok = array( rho )
kount = 1
imod = istart
ii = 0
rhovar = zeros( ( nbins, nsteps ) )
for i in bin:
    rhovar[ ii, : ] = logspace( m.log10( rhostart[ ii ] ),
                       m.log10( rhoend[ ii ] ), num = nsteps )
    ii += 1

kount = 1
nbatch = 0
imod = istart
sgefile = open( 'runbatch.sge', 'r' )
sgetempl = sgefile.readlines()
sgefile.close()


for kk in slope:
    for i in product2( tuple( arange( 0, nsteps ) ), repeat = nbins ):
        jj = 0
        rhok2 = rhok.copy()
        for j in i:
            ibin = bin[ jj ]
            rhok2[ ibin ] = rhovar[ jj, j ]
            jj += 1
        if( not repcheck( list( rhok2 ), kk, nk = nk, imono = 1 ) ):
            if( kount % nbatchmax == 1 ):
                nbatch += 1
                bfilnam = 'runbatch' + ( str( nbatch ) ).rjust( 2, '0' ) + '.s'
                batchfil = open( bfilnam, 'w' )
                os.chmod( bfilnam, 0754 )
                sgefile = open( bfilnam[ :-1 ] + 'sge', 'w' )
                sgewrite = sgetempl
                sgewrite[ 16 ] = sgetempl[ 16 ][ :13 ] + str( nbatchmax ) + '\n'
                sgewrite[ 37 ] = sgetempl[ 37 ][ :22 ] + bfilnam + '\n'
                for line in sgewrite:
                    sgefile.write( line )
                sgefile.close()
            batchfil.write( 'runall.s \t' + ( str( imod ).rjust( 5, '0' ) )
                     + '\t' + str( kk ) + '\n' )
            modfil = 'modlists/model' + ( str( imod ).rjust( 5, '0' ) ) + '.bin'
            slopefil = open( 'modlists/slope.list', 'a' )
            pout = column_stack( ( array( rk ), rhok2 ) )
            pout2 = str( imod ).rjust( 5, '0' ) + '\t' + str( kk ) + '\n'
            slopefil.write( pout2 )
            slopefil.close()
            savetxt( modfil, pout, fmt = '%-5.5f %-5.5e' )
            kount += 1
            imod += 1

print 'there are ' + str( kount ) + ' new models'


# --- fix numprocs on last sge file
sgefile = open( bfilnam[ :-1 ] + 'sge', 'r' )
sgewrite = sgefile.readlines()
sgefile.close()
numprocs = ( kount - 1 )% nbatchmax
numprocs = int( m.ceil( numprocs / 12. ) * 12. )
sgeout = sgewrite
sgeout[ 16 ] = sgewrite[ 16 ][ :13 ] + str( numprocs ) + '\n'
sgefile = open( bfilnam[ :-1 ] + 'sge', 'w' )
for line in sgeout:
    sgefile.write( line )
sgefile.close()


