# Insert a single model's results into the SQL database for that galaxy.  Keep
# a local copy for each galaxy in basedir and run from runall.s script as:
#             python update_db MODNUM
#
# If there are issues with the update, generate and send a warning email.


from readcol import readcol
import numpy as np
import sqlite3 as sql
import sys
import os
import smtplib
from email.mime.text import MIMEText as text

# python update_db MODNUM


def call_me_maybe( flgpath ):

    fromaddr = 'johnjardel@gmail.com'
    toaddrs  = 'jardel@astro.as.utexas.edu'
    m = text( 'The database file for the models you are running has not been created yet.\nSome output may have been lost' )
    m[ 'Subject' ] = 'DATABASE ERROR'
    m[ 'From' ] = 'LONESTAR'
    m[ 'To' ] = toaddrs


    # Credentials 
    username = 'johnjardel'
    pfil = open( '/home1/01208/jardel/pfile.in' )
    password = pfil.readline()

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, m.as_string())
    server.quit()

    # create flag file so I don't get 1000 emails
    f = open( flgpath, 'w' )
    f.write( 'CALL ME MAYBE' )
    f.close()

    return


base = '/work/01208/jardel/sextans/npsm/result/'
galname = 'sextans'
smod = sys.argv[ 1 ]
modnum = int( smod )

# assume DB has been made by mkdb.py before models have been run
if not os.path.isfile( base + galname + '.sql' ):
    print 'NO SQL DATABASE HAS BEEN CREATED.  RUN MKDB.PY FIRST'
    # send me an email telling me my models are not saving properly
    flgpath = base + galname + '.flg'
    if not os.path.isfile( flgpath ):
        call_me_maybe( flgpath )
    sys.exit()


# --- read losvd file
f = open( 'losvd.out' )
losvd = [] 
for line in f:
    item = []
    item.append( modnum )
    item.append( int( line.split()[ 0 ] ) )
    item.append( int( line.split()[ 1 ] ) )
    for x in line.split()[ 2: ]:
                item.append( float( x ) )
    losvd.append( tuple( item ) )
f.close()

# --- read intmom file
f = open( 'intmom.out' )
f.readline()
intmom = []
for line in f:
    item = []
    item.append( modnum )
    for x in line.split():
        item.append( float( x ) )
    intmom.append( tuple( item ) )
f.close()

# --- read gherm file
f = open( 'gherm.out' )
gherm = []
for line in f:
    item = []
    item.append( modnum )
    item.append( int( line.split()[ 0 ] ) )
    for x in line.split()[ 1: ]:
        item.append( float( x ) )
    gherm.append( tuple( item ) )
f.close()

# --- read cres file
f = open( 'cres.mod' + smod )
cres = f.readline()
res = []
res.append( modnum )
for x in cres.split()[ 1:5 ]:
    res.append( float( x ) )
res.append( int( cres.split()[ 5 ] ) )
f.close()

# --- read bin file
f = open( 'model' + smod + '.bin' )
bin = []
for line in f:
    item = []
    item.append( modnum )
    for x in line.split():
        item.append( float( x ) )
    bin.append( tuple( item ) )
f.close()


# --- do the updates
try:
    conn = sql.connect( base + galname + '.sql', timeout = 60 )
    cursor = conn.cursor()
    cursor.executemany( "INSERT INTO losvd VALUES (?,?,?,?,?,?,?,?)", losvd )
    cursor.executemany( "INSERT INTO intmom VALUES (?,?,?,?,?,?,?,?,?)",
                        intmom )
    cursor.executemany( "INSERT INTO gherm VALUES (?,?,?,?,?,?,?)", gherm )
    cursor.execute( "INSERT INTO results VALUES (?,?,?,?,?,?)", res )
    cursor.executemany( "INSERT INTO bin VALUES (?,?,?)", bin )
    conn.commit()
    conn.close()
except:
    print 'SQL ERROR FOR MODEL ' + smod
    f = open( 'database_fail.dat', 'wa' )
    f.write( smod + '\n' )
    f.close()
    conn.close()


