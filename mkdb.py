# Creates SQL database for storing model output in results directory.  Run
# mkdb.py before running any models or their output will be lost.  Edit base
# and galname accordingly 

from readcol import readcol
import numpy as np
import sqlite3 as sql
import sys
import os

def chomp( s ):
    return s[ :-1 ] if s.endswith( '\n' ) else s

base = '/work/01208/jardel/sextans/npsm/result/'
galname = 'sextans'

# create table if .sql doesn't exist, else update
if os.path.isfile( base + galname + '.sql' ):
    print 'WHAT ARE YOU DOING? THE DATABASE ALREADY EXISTS!!!'
    sys.exit()

conn = sql.connect( base + galname + '.sql' )
cursor = conn.cursor()

cursor.execute( """CREATE TABLE losvd (modnum integer, ilosvd integer, ivel integer, vel float, data float, data_hi float, data_low float, model float )""")
cursor.execute( """CREATE TABLE intmom (modnum integer, r float, theta float, v_r float, v_theta float, vrvt float, v_phi float, v_rot float, beta float )""")
cursor.execute( """CREATE TABLE iter (modnum integer, alpha float, ratio float, entropy float, entchi float )""")
cursor.execute( """CREATE TABLE gherm (modnum integer, iangle integer, r float, v float, sigma float, h3 float, h4 float )""" )
cursor.execute( """CREATE TABLE results (modnum integer not null, bh float not null, slope float, chi float, alpha float, norbit integer)""")
cursor.execute( """CREATE TABLE bin (modnum integer, rk float, rhok float )""" )


conn.commit()

sys.exit()


# playing around with pickling:

class Model:
    def __init__( self, modnum ):
        self.modnum = modnum
        self.read_files()

    def __str__( self ):
        return 'database entry for model ' + str( self.modnum )
 
    def read_files( self ):
        self.losvd = readcol( 'losvd.out', twod = True )
        self.intmom = readcol( 'intmom.out', twod = True, skipline = 1 )
        self.gherm = readcol( 'gherm.out', twod = True )
        self.iter = readcol( 'iter.out', twod = True )

        cresf = open( 'cres.mod' + str( self.modnum ) )
        cres = cresf.readline()
        cresf.close()

        self.bh = float( cres.split()[ 1 ] )
        self.slope = float( cres.split()[ 2 ] )
        self.chi = float( cres.split()[ 3 ] )
        self.alpha = float( cres.split()[ 4 ] )
        self.norbit = int( cres.split()[ 5 ] )

        return
        
    def write_db( self ):
        with open( base + galname + '.db', mode = 'a+b' ) as f:
            pickle.dump( losvd, f )
        return

mod = Model( modnum )

    
# this lets me append the object to the DB

# with open( FILEPATH , mode = 'a+b' ) as f:
#    pickle.dump( obj, f )

# in analysis routines, use a 'for item in f: pickle.load()'

sys.exit()

#f = open( 'losvd.mod' + smod )
#losvds = []
#for line in f:
#    losvds.append( chomp( line.expandtabs() ) )

#cursor.execute( """CREATE TABLE losvds (entry text)""" )

# ^^^ that's a stupid way to do this.

# store .intmom

# store .gherm

