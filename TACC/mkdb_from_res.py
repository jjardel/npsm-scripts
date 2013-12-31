# Converts the old method of storing model output (independent files) to the
# new method of using an SQL database.  Set base and galname accordingly and
# run from the results directory.

from readcol import readcol
import numpy as np
import sqlite3 as sql
import sys
import os
import glob

def f_float( x ):
    try:
        f = float( x )
    except ValueError:
        f = 0.
    return f
    
        

base = '/work/01208/jardel/sextans/npsm/result/'
galname = 'sextans'


# create table if .sql doesn't exist, else update
if os.path.isfile( base + galname + '.sql' ):
    print 'WHAT ARE YOU DOING? THE DATABASE ALREADY EXISTS!!!'
    #sys.exit()

conn = sql.connect( base + galname + '.sql' )
cursor = conn.cursor()

cursor.execute( """CREATE TABLE losvd (modnum integer, ilosvd integer, ivel integer, vel float, data float, data_hi float, data_low float, model float )""")
cursor.execute( """CREATE TABLE intmom (modnum integer, r float, theta float, v_r float, v_theta float, vrvt float, v_phi float, v_rot float, beta float )""")
cursor.execute( """CREATE TABLE iter (modnum integer, alpha float, ratio float, entropy float, entchi float )""")
cursor.execute( """CREATE TABLE gherm (modnum integer, iangle integer, r float, v float, sigma float, h3 float, h4 float )""" )
cursor.execute( """CREATE TABLE results (modnum integer, bh float, slope float, chi float, alpha float, norbit integer)""")
cursor.execute( """CREATE TABLE bin (modnum integer, rk float, rhok float )""" )
conn.commit()


# construct results table
for model in glob.iglob( 'cres.*' ):
    smod = model.strip( 'cres.mod' )
    modnum = int( smod )
    f = open( model )
    cres = f.readline()
    res = []
    res.append( modnum )
    for x in cres.split()[ 1:5 ]:
        res.append( f_float( x ) )
    res.append( int( cres.split()[ 5 ] ) )
    f.close()
    cursor.execute( "INSERT INTO results VALUES (?,?,?,?,?,?)", res )
conn.commit()


# construct losvd table
losvd = []
for model in glob.iglob( 'losvd.*' ):
    smod = model.strip( 'losvd.mod' )
    modnum = int( smod )
    f = open( model )
    for line in f:
        item = []
        item.append( modnum )
        item.append( int( line.split()[ 0 ] ) )
        item.append( int( line.split()[ 1 ] ) )
        for x in line.split()[ 2: ]:
            item.append( f_float( x ) )
        losvd.append( tuple( item ) )
    f.close()
cursor.executemany( "INSERT INTO losvd VALUES (?,?,?,?,?,?,?,?)", losvd )
conn.commit()

# construct intmom table
intmom = []
for model in glob.iglob( 'intmom.*' ):
    smod = model.strip( 'intmom.mod' )
    modnum = int( smod )
    f = open( model )
    f.readline()
    for line in f:
        item = []
        item.append( modnum )
        for x in line.split():
            item.append( f_float( x ) )
        intmom.append( tuple( item ) )
    f.close()
cursor.executemany( "INSERT INTO intmom VALUES (?,?,?,?,?,?,?,?,?)", intmom )
conn.commit()

# construct gherm table
gherm = []
for model in glob.iglob( 'gherm.*' ):
    smod = model.strip( 'gherm.mod' )
    modnum = int( smod )
    f = open( model )
    for line in f:
        item = []
        item.append( modnum )
        item.append( line.split()[ 0 ] )
        for x in line.split()[ 1: ]:
            item.append( f_float( x ) )
        gherm.append( tuple( item ) )
    f.close()
cursor.executemany( "INSERT INTO gherm VALUES (?,?,?,?,?,?,?)", gherm )
conn.commit()

# construct bin table
bin = []
for model in glob.iglob( '../modlists/model*.bin' ):
    t1 = model.strip( '../modlists/model' )
    t2 = t1.strip( '.bin' )
    modnum = int( t2 )
    f = open( model )
    for line in f:
        item = []
        item.append( modnum )
        item.append( f_float( line.split()[ 0 ] ) )
        item.append( f_float( line.split()[ 1 ] ) )
        bin.append( tuple( item ) )
    f.close()
cursor.executemany( "INSERT INTO bin VALUES (?,?,?)", bin )
conn.commit()
conn.close()
