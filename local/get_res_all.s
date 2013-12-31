#!/bin/csh

# run from alldsphs/plotall directory

# block to scp chi.out and chi_multi.out files here

set TACC = lonestar.tacc.utexas.edu:

scp $TACC/work/01208/jardel/draco/npsm/result/chi_draco.out .
scp $TACC/work/01208/jardel/draco/npsm/result/chi_draco_multi.out .
scp $TACC/work/01208/jardel/carina/npsm/result/chi_carina.out .
scp $TACC/work/01208/jardel/carina/npsm/result/chi_carina_multi.out .
scp $TACC/work/01208/jardel/fornax/npsm/result/chi_fornax.out .
scp $TACC/work/01208/jardel/fornax/npsm/result/chi_fornax_multi.out .
scp $TACC/work/01208/jardel/sculptor/npsm/result/chi_sculptor.out .
scp $TACC/work/01208/jardel/sculptor/npsm/result/chi_sculptor_multi.out .
scp $TACC/work/01208/jardel/sextans/npsm/result/chi_sextans.out .
scp $TACC/work/01208/jardel/sextans/npsm/result/chi_sextans_multi.out .
	

# copy appropriate input files for dsphdm2

set BASE = /home/jardel/research
set DRACO = $BASE/draco/cmd/new/aasplot
set CARINA = $BASE/carina/cmd
set FORNAX = $BASE/fornax/cmd
set SCULPTOR = $BASE/sculptor/cmd
set SEXTANS = $BASE/sex/cmd

cp $DRACO/dsphdm2.py .
cp $DRACO/light.dat .
cp chi_draco.out chi.out
python dsphdm2.py

cp $CARINA/dsphdm2.py .
cp $CARINA/light.dat .
cp chi_carina.out chi.out
python dsphdm2.py

cp $FORNAX/dsphdm_fnx.py .
cp $FORNAX/light.dat .
cp chi_fornax.out chi.out
python dsphdm_fnx.py

cp $SCULPTOR/dsphdm2.py .
cp $SCULPTOR/light.dat .
cp chi_sculptor.out chi.out
python dsphdm2.py

cp $SEXTANS/dsphdm2.py .
cp $SEXTANS/light.dat .
cp chi_sextans.out chi.out
python dsphdm2.py

