#!/bin/csh

# Invoke as run_master_mplot.csh X X X where X is y or n 
# indicating which blocks of the script to run.


# SETUP ENVIORNMENTAL VARIABLES

set CARINA = /work/01208/jardel/carina/npsm/
set DRACO = /work/01208/jardel/draco/npsm/
set FORNAX = /work/01208/jardel/fornax/npsm/
set SCULPTOR = /work/01208/jardel/sculptor/npsm/
set SEXTANS = /work/01208/jardel/sextans/npsm/

set WORKDIR = /work/01208/jardel/alldsphs/
set BASE = /work/01208/jardel/
set SCRIPTSDIR = /home1/01208/jardel/npsm/scripts/alldsphs/

#set GALLIST = 'carina fornax sculptor sextans'
set GALLIST = 'draco' #for testing

unalias ls

# call the individual run_mplot.s scripts for each galaxy.  
# requires a custom runallmplot.s in each galaxy's directory

if ($1 == "y" ) then
    cd $WORKDIR
    foreach galaxy ($GALLIST)
	cd $BASE${galaxy}/npsm/
	python ${SCRIPTSDIR}runmplot.py
	ls runmplot??.sge | awk '{print "qsub", $1}' > qsub.s
	chmod +x qsub.s
	qsub.s
    end
endif

# call a new version of mplot.py to output $galaxy.mass and $galaxy.vc
# have to move stuff to best/ if it hasn't been done yet.

if ($2 == "y" ) then
    cd $WORKDIR
    foreach galaxy ($GALLIST)
	cd $BASE${galaxy}/npsm/
	if( ! -d mod/best ) then
	    mkdir mod/best
	    set BESTMOD = `sort -gr -k9 result/res.tab | tail -1 | awk '{print $6}'`
	    cp mod/mplot/${BESTMOD}/* mod/best
	endif
	python /home1/01208/jardel/npsm/scripts/alldsphs/mplot.py $galaxy
	cp ${galaxy}.mass $WORKDIR
	cp ${galaxy}.vc $WORKDIR
	cp ${galaxy}.est $WORKDIR
	cp ${galaxy}.half $WORKDIR
    end
endif
	

# make 4 panel plot with similar to what goes on in npsm_common but on lonestar

if ($3 == "y" ) then
    cd $WORKDIR
    python mk_mplot_4p.py
endif
