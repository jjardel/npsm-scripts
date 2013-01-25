from readcol import readcol
from numpy import *
from pylab import *
import os
import sys
import math as m
from datetime import datetime
import smtplib

def call_me_maybe():

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
    
    return None

def repcheck( x, slope, reslist, nk=5, imono = 0, eps = 1e-1):
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
    for line in reslist:
        test = []
        for item in line[ 0:nk ]:
            test.append( float( item ) )
        test.append( line[ nk + 2 ] )
        flag = True
        for a, b in zip(test, x):
            if( abs( float( a ) / b - 1 ) > eps):
                flag = False
        if flag:
            return flag   
            
    return flag
# ---------

def unique_rows(a):
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))

# read step.in in main routine

def findmods( parin, slopein, chi2, step, min, chilim ):
    # findmods figures out which new models to run, sets up the .sge files
    # and submits jobs to the queue.  

    nmod = len( parin[ : ] )
    npar = len( parin[ 0 ] )
    dopars = where( step != 0 )[ 0 ]


    goodchi =  where( chi2 <= chilim )[ 0 ]
    goodmod = unique_rows( parin[ goodchi ] )
    ngood = len( goodmod[ : ] )
    print ngood, 'points within chilim'
    

    # take a fractional increase of STEP above and below each point within
    # CHILIM
    todo = []
    slopeout = []
    for i in range( 0, ngood ):
        for s in slopein:
            for k in range( -1, 2, 2 ):
                x = goodmod[ i, : ].copy()
                for j in dopars:
                    delta = ones( npar )
                    delta[ j ] = abs( k - step[ j ] )
                    todo.append( goodmod[ i, : ] * delta )
                    slopeout.append( s )

    return todo, slopeout


# PARAMETERS
#===============
deltachi = 3.0
#stepsize = 0.1
nbatchmax = 96
maxflag = 2000
#===============

paramf = open( 'param/mod.param.bin' )
rk = []
for line in paramf:
    rk.append( float( line.split()[0] ) )
paramf.close()
nk = len( rk )

# --- open res.tab file and index results
resf = open( 'result/res.tab', 'r' )
resin = resf.readlines()
resf.close()
resdict = {}
for line in resin:
    chi = float( line.split()[nk+3] )
    rho = []
    for i in line.split():
        rho.append( float( i ) )
    resdict[ chi ] = rho

chimin = min( resdict.keys() )
print 'min chi^2 = ', chimin

chikey = nk + 3
bhkey = nk + 1
modkey = nk
bestmod = int( resdict[ chimin ][ nk ] )
bestdens = resdict[ chimin ][ :nk ]
chilist = array( resdict.keys() )
biglist = array( resdict.values() )
denslist = biglist[ :, :nk ]
slopelist = biglist[ :, nk + 2 ]
trash, pstep = readcol( 'step.in', twod = False )    


todo, slopeout = findmods( denslist, [2, 3, 4 ], chilist,
                           pstep, .05, chimin + deltachi )

#something like step /= 2

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

kount = 1
imod = istart
ii = 0
nbatch = 0
sgefile = open( 'runbatch.sge', 'r' )
sgetempl = sgefile.readlines()
sgefile.close()

# --- process run files

for i in zip( todo, slopeout ):
    if( not repcheck( list( i[ 0 ] ), i[ 1 ], biglist, nk = nk, imono = 1 ) ):
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
                         + '\t' + str( i[ 1 ] ) + '\n' )
         modfil = 'modlists/model' + ( str( imod ).rjust( 5, '0' ) ) + '.bin'
         slopefil = open( 'modlists/slope.list', 'a' )
         pout = column_stack( ( array( rk ), array( i[ 0 ] ) ) )
         pout2 = str( imod ).rjust( 5, '0' ) + '\t' + str( i[ 1 ] ) + '\n'
         slopefil.write( pout2 )
         slopefil.close()
         savetxt( modfil, pout, fmt = '%-5.5f %-5.5e' )
         kount += 1
         imod += 1

print 'there are ' + str( kount - 1 ) + ' new models'
batchfil.close()
slopefil.close()

if( kount <= 1 ):
    sys.exit()    

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

try:
    logfil = open( 'modlists/logfile', 'r' )
    nb = len( logfil.readlines() ) + 1
    logfil.close()
    firsttime = False
except:
    nb = 1
    firsttime = True
sout = str( nb ) + '\t ' + str( datetime.now() ) + '\t' + ( str( istart ) ).rjust( 5, '0' ) +  ' - ' + ( str( imod - 1 ) ).rjust( 5, '0' ) + '\n'
logfil = open( 'modlists/logfile', 'a' )
if( firsttime ):
    logfil.write( 'batch number \t \t date \t  \t modnum range \t stepsize \n' )
logfil.write( sout )
logfil.close()

if( kount > maxflag ):
    t = call_me_maybe()
    
