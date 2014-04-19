#  Program to add info from cres into a table named res.tab stored in ./result

from readcol import readcol
from numpy import *
import sys

basedir = '/work/01208/jardel/super_scaled/'

modnum = int( sys.argv[ 1 ] )
filein = 'model' + ( str( modnum ) ).rjust( 5, '0' ) + '.bin'
rk, rhok = readcol( filein, twod = False )
nk = rk.size
cresf = open( 'cres.mod' + ( str( modnum ) ).rjust( 5, '0' ), 'r' )
cres = cresf.readline()
cresf.close()

rhok = list( rhok ) 
creslist = cres.split()
list2 = [ float( i ) for i in creslist ]
out =  rhok + list2

k = 0
out2 = []
for i in out:
    if( k <= nk - 1 ):
        out2.append( '%1.4e' % i + ' ')
    elif( k == nk or k == nk + 5 ):
        out2.append( '%05i' % i + ' ' )
# check that integer formatting is actually being used        
    else:
        out2.append( '%5.5f' % i + ' ' )
    k += 1
    
out2[ nk + 5 ] += '\n'
fout = open( basedir + 'result/res.tab', 'a' )
fout.writelines( out2 )
fout.close()
