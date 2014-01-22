# smartgrid.py

# Program for determining an optimal set of models to run in order to better
# sample parameter space.  The models within CHILIM are selected, and their
# parameters are fractionally increased/decreased by STEP in each dimension.
# All the relevant batch files and scripts for LONESTAR are created.
#
# Requires some set of models to be previously run, with their results stored
# in res.tab.  Probably best to start exploration of parameter space with a
# brute force method like rungrid.py.

# Edit kwargs in main to set parameters


from readcol import readcol
import numpy as np
import sys
import math as m
import os
from itertools import product
import rungrid
import smtplib

class SmartGrid( rungrid.Models ):

    def __init__( self, **kwargs ):
        self.getResults( **kwargs )

        self.readSlopeFile( **kwargs )
        if kwargs[ 'includeBHs' ]:
            self.readBHFile( **kwargs )
        
        self.findMods( **kwargs )

    def readStepFile( self, path ):
        fp = open( path )
        step = []
        for line in fp:
            step.append( float( line.split()[ 1 ] ) )

        self.stepdata = np.array( step )

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

        bhFile = kwargs[ 'bhFilePath' ]
        with open( bhFile ) as fp:
            line = fp.readline().split()

        bh = []
        bh += [ float( item ) for item in line[ 0:2 ] ]
        bh += int( line[ 2 ] )

        self.bhdata = bh            

    def unique_rows(self, a):
        unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
        return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))

    
    def call_me_maybe( self ):

        fromaddr = 'johnjardel@gmail.com'
        toaddrs  = 'jardel@astro.as.utexas.edu'
        msg = '''
        From: LONESTAR
        Subject: Error in smartgrid_auto

        There are more models than you probably want to run so I stopped the script.'''


        # Credentials (if needed)
        username = 'johnjardel'
        pfil = open( '/home1/01208/jardel/pfile.in' )
        password = pfil.readline()

        # The actual mail send
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username,password)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()

        os.system( 'crontab -r' )
        failfile = open( 'fail.warn', 'w' )
        failfile.write( 'FAIL: EXCESSIVE MODELS' )
        failfile.close()

        raise LaunchError( 'Too many models' )
    
            
    def findMods( self, **kwargs ):

        stepPath = kwargs[ 'stepFilePath' ]
        self.readStepFile( stepPath )

        deltaChi = kwargs[ 'deltaChi' ]
        nk = kwargs[ 'nk' ]

        allModels = self.res
        chi = self.chi
        step = self.stepdata
        slopein = self.slopedata
        if kwargs[ 'includeBHs' ]:
            bhs = self.bhdata
        else:
            bhs = [ 0. ]

        minChi = np.min( chi[ chi != 0 ] )

        print 'minimum chi^2 is ', minChi
        
        goodList = np.where( chi < minChi + deltaChi )[ 0 ]
        goodModels = allModels[ goodList, :nk ]
        nGood = len( goodList )
        print nGood, ' models within chiLim'

        dopars = np.where( step != 0 )[ 0 ]
        npar = step.shape[ 0 ]

        
        # take a fractional increase of STEP above and below each point within
        # CHILIM
        todo = []
        for i in range( 0, nGood ):
            for s in slopein:
                for b in bhs:
                    for k in range( -1, 2, 2 ):
                        x = goodModels[ i, : ].copy()
                        for j in dopars:
                            delta = np.ones( npar )
                            delta[ j ] = abs( k - step[ j ] )
                            mod = goodModels[ i, : ] * delta
                            todo.append( mod.tolist() + [ s, b ] )

        # a ridiculous way to remove duplicates from res.tab
        todo = self.unique_rows( np.array( todo ) ).tolist()
        self.allModels = todo

        if len( todo ) > kwargs[ 'maxModels' ]:
            self.call_me_maybe()
        

def main( **kwargs ):

    models = SmartGrid( **kwargs )
    toRun = models.checkForDups( **kwargs )
    launcher = rungrid.Launcher( toRun, **kwargs )

    
        
        
        
if __name__ == '__main__':

    # EDIT PARAMETERS HERE

    kwargs = { 'nk': 5, # number of radial bins in the profile
               'deltaChi': 2.0, # delta chi^2 threshold above chiMin
               'maxModels': 2000, # abort if number of models is greater
               'includeBHs': False, # use BHs?
               'resFilePath': 'result/res.tab', # path to res.tab
               'stepFilePath': 'step.in', # path to file
                                          # determinig density grid
               'slopeFilePath': 'slope.in', # path to file determining slopes
               'bhGridFilePath': 'bh.in', # path to file determining BH values
               'sgeFilePath': 'runbatch.sge', # path to template
                                              # submission file
               'paramFilePath': 'param/mod.param.bin', # path to previous
                                                       # output of param2np
               'modlistsDir': './modlists', # path to modlists directory
               'monotonic': True, # only monotonically decreasing profiles?
               'tol':  5e-2 # relative tolerance for considering
                            # two profiles equal
               }

    main( **kwargs )
    
