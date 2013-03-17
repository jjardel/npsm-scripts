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

        # read data
        self.readres( galname )

    def readres( self, galname ):
        """ Subroutine to read in .res file """

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

    
