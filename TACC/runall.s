#! /bin/csh

set libn = mod$1
set scr = $libn
set workdir = /tmp/$libn
set base = /work/01208/jardel/super_scaled/base
set res = /work/01208/jardel/super_scaled/result


cd /tmp

rm -rf $libn
mkdir $libn
cd $libn
cp -r $base/* .
cp $base/../modlists/model${1}.bin .
	
#model of the stars
./gden_NP.x << eof
super.gden
10.
90
.67
$3
$1
$2
eof

./library.x
./plot.libsos.x
mv pgplot.ps libsos.ps
./sos2vor.x
chmod +x varea.script
./varea.script
./vor2vphase.x
cp phase.vor phase.out
cp velbin.sav velbin.dat
./seecor.x

head -1 velbin.sav > velbin.dat
./model.x << eof
0
1.
0
1
1.e-10
1
eof
./seecor2.x
cp velbin.sav velbin.dat
./model.x << eof
0
1.0
0
1
1.e-7
1
1.e-6
1
1.e-5
1
3.e-5
1
1.e-4
1
666
eof
cp ml.out ml.stars
cp iteration.out iteration.stars

rm -f res.$libn
cat norbit ml.stars > res.$libn
cat iteration.stars > iter.$libn
rawk_NP res.$libn

#cp cres.$libn $res
#cp res.$libn $res
#cp iter.$libn $res

./vlook.x << eof
vlook.ps/cps
eof

#cp intmom.out $res/intmom.$libn
#cp losvd.out $res/losvd.$libn
#cp gherm.out $res/gherm.$libn
	
if( -e badmodel ) then
	python mkbadlist.py $1
else
	python mkrestab.py $1
	python update_db.py $1
endif

cd $res
rm -r $workdir
