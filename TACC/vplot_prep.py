
# Computes anisotropy by averaging sigma_r/sigma_t in
# spherical shells where kinematics are available.  Uses SQL database where
# intmom is stored

from numpy import *
from pylab import *
from readcol import readcol
import os
import math as m
import sys
import glob
import sqlite3 as sql

#----------------
# PARAMETERS
nr = 20
nv = 5
nk = 5
deltachi = 7.04
#xfac = 2.8
#dist = 85
#----------------

# get individual galaxy properties
galname = sys.argv[ 1 ]
f_info = open( galname + '.info' )
dist = float( f_info.readline() )
xfac = float( f_info.readline() )
f_info.close()

# ^^ need to make .info files for each galaxy.  Store them in $galname/npsm/

# connect to SQL database
conn = sql.connect( 'result/' + galname + '.sql' )
cursor = conn.cursor()

# load positions of losvds
vbin_r = []
vbin_v = []
velbinfile = open( 'base/velbin.sav' )
for line in velbinfile:
    vbin_r.append( [ int( line.split()[ 4 ] ), int( line.split()[ 5 ] ) ] )
    vbin_v.append( [ int( line.split()[ 6 ] ), int( line.split()[ 7 ] ) ] )
velbinfile.close()

r = zeros( nr )
bin_rfile = open( 'base/bin_r.out' )
bin_rfile.readline()
bin_rfile.readline()
for i in range( 0, nr ):
    r[ i ] = float( ( bin_rfile.readline() ).split()[ 2 ] )
bin_rfile.close()

v = zeros( nv )
bin_vfile = open( 'base/bin_v.out' )
bin_vfile.readline()
bin_vfile.readline()
for i in range( 0, nv ):
    v[ i ] = float( ( bin_vfile.readline() ).split()[ 2 ] )
bin_vfile.close()

# read in data from best model

query = "select modnum, min( chi ) from results where chi != 0"
cursor.execute( query )
bestmod, bestchi = cursor.fetchone()

query = "select * from intmom where modnum = ?"
cursor.execute( query, [(bestmod)] )
res = cursor.fetchall()

i, j = ( 0, 0 )
vr = zeros( ( nr, nv ) )
vtheta = zeros( ( nr, nv ) )
vphi = zeros( ( nr, nv ) )
velphi = zeros( ( nr, nv ) )

for line in res:
    vr[ i, j ] = line[ 3 ]
    vtheta[ i, j ] = line[ 4 ]
    vphi[ i, j ] = line[ 6 ]
    velphi[ i, j ] = line[ 7 ]
    i += 1
    if i == nr:
        i = 0
        j += 1
vrvt_best = vr / sqrt( 0.5 * ( vtheta**2 + vphi**2 + velphi**2 ) )
p = zeros( 5 )


# get 1-sigma range
i, j = ( 0, 0 )
vr_L = zeros( ( nr, nv ) ) + 1e9
vtheta_L = zeros( ( nr, nv ) ) + 1e9
vphi_L = zeros( ( nr, nv ) ) + 1e9
velphi_L = zeros( ( nr, nv ) ) + 1e9
vr_H = zeros( ( nr, nv ) )  - 1e9
vtheta_H = zeros( ( nr, nv ) ) - 1e9
vphi_H = zeros( ( nr, nv ) ) - 1e9
velphi_H = zeros( ( nr, nv ) ) - 1e9


query = "select modnum from results where chi != 0 and chi * ? < ?"
cursor.execute( query, [(xfac), (xfac * bestchi + deltachi )] )
sigmalist = []
for i in cursor.fetchall():
    sigmalist.append( i[ 0 ] )

    
"""
---------DEPRECATED-------------

sigmalist = []
intmomlist = glob.glob( 'result/intmom.*' )
fres = open( 'result/res_scaled.tab' )
for line in fres:
    chi = float( line.split()[ nk + 3 ] )
    cmod = line.split()[ nk ]
    if( chi < bestchi + deltachi and 'result/intmom.mod' +
        cmod in intmomlist ):
        sigmalist.append( line.split()[ nk ] )
fres.close()
"""    

#sigmalist = glob.glob( 'mod/1sigma/*/intmom.out' )

query = "select v_r, v_theta, v_phi, v_rot from intmom where modnum = ?"
nmod = len( sigmalist )
imod = 0
E = zeros( ( nr, nv, nmod, 4 ) )
for mod in sigmalist:
    i, j = ( 0, 0 )
    cursor.execute( query, [(mod)] )
    res = cursor.fetchall()
    for line in res:
        E[ i, j, imod, 0 ] = line[ 0 ] # vr
        E[ i, j, imod, 1 ] = line[ 1 ] # vtheta
        E[ i, j, imod, 2 ] = line[ 2 ] # sigma_phi
        E[ i, j, imod, 3 ] = line[ 3 ] # v_phi
        i += 1
        if i == nr:
            i = 0
            j += 1
    imod += 1

vrvt_H = zeros( len( vbin_r ) )
vrvt_L = zeros( len( vbin_r ) )
vrvt = zeros( len( vbin_r ) )
rp = zeros( len( vbin_r ) )

ii = 0
for i in zip( vbin_r, vbin_v ):
    # get limits from velbinfile
    r1 = i[ 0 ][ 0 ] - 1
    r2 = i[ 0 ][ 1 ]
    #v1 = i[ 1 ][ 0 ] - 1 #<- these are being set constant.  Is that all I have
    #v2 = i[ 1 ][ 1 ]     #    to change for variable angle plots?
    v1 = 0
    v2 = 4

    # do it
    xx = []
    xvr = []
    xvphi = []
    xvthet = []
    for imod in range( 0, nmod ):
        x = array( mean( E[ r1:r2, v1:v2, imod, 0 ] ) / sqrt(
            0.5 * ( mean( E[ r1:r2, v1:v2, imod, 2 ] )**2 +
                    mean( E[ r1:r2, v1:v2, imod, 3 ] )**2 +
                    mean( E[ r1:r2, v1:v2, imod, 1 ] )**2 ) ) )
        xx.append( x )
        x = array( mean( E[ r1:r2, v1:v2, imod, 0 ] ) )
        xvr.append( x )
        x = array( mean( E[ r1:r2, v1:v2, imod, 1 ] ) )
        xvthet.append( x )
        x = array( mean( E[ r1:r2, v1:v2, imod, 2 ] ) )
        xvphi.append( x )
    vrvt_H[ ii ] = max( xx )
    vrvt_L[ ii ] = min( xx )
    vrvt[ ii ] = mean( vr[ r1:r2, v1:v2 ] ) / sqrt( 0.5 * (  mean(
        vphi[ r1:r2, v1:v2 ] )**2 + mean( velphi[ r1:r2, v1:v2 ] )**2 +
                                                           mean(
        vtheta[ r1:r2, v1:v2 ]**2 ) ) )
    rp[ ii ] = mean( r[ r1:r2 ] )
    ii += 1

clf()

rp *= dist * 1e3 / 206265.

w, h = figaspect( 1. )
figure( figsize = ( w, h ) )

#semilogx( rp, vrvt, 'k' )
semilogx( rp, [ mean( i ) for i in zip( vrvt_L, vrvt_H ) ], 'k' )
#semilogx( rp, vrvt_best[ r1:r2, v1:v2], 'k' )
fill_between( rp, vrvt_L, vrvt_H, color = '0.7' )
semilogx( rp, [ mean( i ) for i in zip( vrvt_L, vrvt_H ) ], 'k' )
#semilogx( rp, vrvt, 'k' )
ylim( [ 0.5, 2.0 ] )
#xlabel( '$r$ (arcsec)', fontsize = 14 )
ylabel( '$\\sigma_r / \\sigma_t$', fontsize = 14 )
xlim( [ min( rp ), max( rp ) ] )
#twiny()
#rpc = rp * 71e3 / 206265.
#xlim( [ min( rp ) * 71e3 / 206265., max(rp ) * 71e3 / 206265. ] )
#ylim( [ 0.5, 2.0 ] )
#semilogx( rpc, [ mean( i ) for i in zip( vrvt_L, vrvt_H ) ], color = 'None' )
xlabel( '$r$ (pc)', fontsize = 14 )
savefig( 'vplot.ps' )

f_out = open( galname + '.aniso', 'w' )
for i, j, k in zip( rp, vrvt_L, vrvt_H ):
    out = str( i ) + ' ' + str( j ) + ' ' + str( k ) + '\n'
    f_out.write( out )
f_out.close()

# in plot_vplot phase I'll need to compute the mean
