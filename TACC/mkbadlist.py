#  Program to add info from cres into a table named res.tab stored in ./result

from readcol import readcol
from numpy import *
import sys

basedir = '/work/01208/jardel/super_scaled/'

slopefil = open( 'slope.dat' )
slope = float( slopefil.read() )
slopefil.close()

modnum = int( sys.argv[ 1 ] )
filein = 'model' + ( str( modnum ) ).rjust( 5, '0' ) + '.bin'
rk, rhok = readcol( filein, twod = False )
nk = rk.size
out = []
for i in list( rhok ):
    out.append( i )
out.append( slope )
out.append( modnum )
out2 = []
k = 0
for i in out:
    if( k != nk + 1 ):
        out2.append( '%1.4e' % i + ' ')
    elif( k == nk + 1 ):
        out2.append( '%05i' % i + ' ' )
    k += 1
out2[ nk +1 ] += '\n'
fout = open( basedir + 'result/bad.list', 'a' )
fout.writelines( out2 )
fout.close()
