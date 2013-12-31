#!/bin/csh

#set PYTHONPATH=/opt/apps/python/epd/7.2.2/modules/lib/python:/opt/apps/python/epd/7.2.2/lib:/home1/01208/jardel/python:/home1/01208/jardel/python/lib/python/:/home1/01208/jardel/python/lib/python2.7/site-packages/
#export PYTHONPATH 

unalias ls
rm -f Para*
rm -f runbatch??.*
python smartgrid.py

ls runbatch??.sge | awk '{print "qsub",$1}' > qsub.s
chmod +x qsub.s
qsub.s

set x=`cat runbatch??.s | wc -l`
echo `date` $x >> submit.log
alias ls='ls -F --color'

