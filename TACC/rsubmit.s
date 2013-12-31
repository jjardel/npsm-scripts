#!/bin/csh
#source /etc/profile
source ~/.cshrc
echo $WORK
echo " "
set x = `qstat | wc -l`
if ($x == 0) then
	cd $WORK/sculptor/npsm
	submit.s
endif
