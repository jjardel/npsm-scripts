# Insert a single model's results into the SQL database for that galaxy.  Keep
# a local copy for each galaxy in basedir and run from runall.s script as:
#             python update_db MODNUM
#

# USING POSTGRESQL DB NOW


from readcol import readcol
import numpy as np
import psycopg2 as sql
import sys
import os

# python update_db MODNUM

def f_float( x ):
    try:
        f = float( x )
    except ValueError:
        f = 0.
    return f


base = '/work/01208/jardel/test/core/result/'
galname = 'coreTest'
smod = sys.argv[ 1 ]
modnum = int( smod )

# --- read losvd file
f = open( 'losvd.out' )
losvd = [] 
for line in f:
    item = []
    item.append( galname )
    item.append( modnum )
    item.append( int( line.split()[ 0 ] ) )
    item.append( int( line.split()[ 1 ] ) )
    for x in line.split()[ 2: ]:
                item.append( f_float( x ) )
    losvd.append( tuple( item ) )
f.close()

# --- read intmom file
f = open( 'intmom.out' )
f.readline()
intmom = []
for line in f:
    item = []
    item.append( galname )
    item.append( modnum )
    for x in line.split():
        item.append( f_float( x ) )
    intmom.append( tuple( item ) )
f.close()

# --- read gherm file
f = open( 'gherm.out' )
gherm = []
for line in f:
    item = []
    item.append( galname )
    item.append( modnum )
    item.append( int( line.split()[ 0 ] ) )
    for x in line.split()[ 1: ]:
        item.append( f_float( x ) )
    gherm.append( tuple( item ) )
f.close()

# --- read cres file
f = open( 'cres.mod' + smod )
cres = f.readline()
res = []
res.append( galname )
res.append( modnum )
for x in cres.split()[ 1:5 ]:
    res.append( f_float( x ) )
res.append( int( cres.split()[ 5 ] ) )
f.close()

# --- read iter file
f = open( 'iter.mod' + smod )
iter = []
for line in f:
    item = []
    item.append( galname )
    item.append( modnum )
    for x in line.split():
        item.append( f_float( x ) )
    iter.append( tuple( item ) )
f.close()

# --- read bin file
f = open( 'model' + smod + '.bin' )
bin = []
for line in f:
    item = []
    item.append( galname )
    item.append( modnum )
    for x in line.split():
        item.append( f_float( x ) )
    bin.append( tuple( item ) )
f.close()


# --- do the updates
try:
    conn = sql.connect( 'dbname=gebhardt_modelresults user=jardel host=db.corral.tacc.utexas.edu' )
    cursor = conn.cursor()
    cursor.executemany( """INSERT INTO losvd( galname, modnum, ilosvd, ivel, vel, data, data_hi, data_low, model ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);""", losvd )
    cursor.executemany( """INSERT INTO intmom( galname, modnum, r, theta, v_r, v_theta, vrvt, v_phi, v_rot, beta ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""", intmom )
    cursor.executemany( """INSERT INTO gherm( galname, modnum, iangle, r, v, sigma, h3, h4 ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);""", gherm )
    cursor.execute( """INSERT INTO results( galname, modnum, bh, slope, chi, alpha, norbit ) VALUES (%s,%s,%s,%s,%s,%s,%s);""", res )
    cursor.executemany( """INSERT INTO bin( galname, modnum, rk, rhok ) VALUES (%s,%s,%s,%s);""", bin )
    cursor.executemany( """INSERT INTO iter( galname, modnum, alpha, ratio, entropy, entchi ) VALUES (%s,%s,%s,%s,%s,%s);""", iter )
    conn.commit()
    cursor.close()
    conn.close()

except:
    print 'SQL ERROR FOR MODEL ' + smod
    f = open( base + 'database_fail.dat', 'a+' )
    f.write( smod + '\n' )
    f.close()
    cursor.close()
    conn.close()


