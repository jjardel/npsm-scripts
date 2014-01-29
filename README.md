npsm-scripts
============

various bookkeeping procedures and analysis routines for Non-Parametric Schwarzschild Modeling (NPSM)

For use with the NPSM code described in Jardel et al (2013 ApJ 763 91).
This repo is divided into 3 sections:

1.  TACC - routines to be run on the Texas Advanced Computing Center (Lonestar).
           These include routines to manage job submission, parameter space
	   sampling, chi^2 analysis, and interface with PSQL database storing 
	   results
2.  local - routines to be run on your local machine.  These are mostly designed
    	    to perform analysis on results obtained on TACC and stored in the 
	    database (Corral)
3.  R - routines for interactive visualizations.
            
DESCRIPTIONS:

1.  TACC
--------------------------------------------------------------------------------

plotres.py - Main analysis routine to determine dark matter densities and 
             corresponding uncertainties.  Computes them from sliding biweight
             of k-lowest chi^2 points per bin for marginalized chi^2 curves.
	     Makes Figure 6 in Jardel et al. (2013 ApJ 763, 91)

plotres_multi-param.py - Secondary analysis routine to determine dark matter
		         densities and their uncertainties.  Computes the 
			 joint 1-sigma confidence band (in contrast to the
			 point-wise band determined by plotres.py).  Also does
			 a better job at interpolating between radial bins.
			 Makes gray band from Figure 1 in Jardel & Gebhardt
			 (ApJL 775L, 30 ).

rungrid.py - Sets up a multi-dimensional grid of parameter combinations to run,
	     a brute force method.  Usually start off modeling with rungrid, then
	     do something more sophisticated like smartgrid.py.  Contains Launcher
	     class for submitting jobs to Lonestar.

smartgrid.py - Uses iterative refinement technique described in Jardel et al. 
	       (2013 ApJ 763, 91) to sample parameter space.  Finds areas of 
	       low chi^2 and takes fractional steps in each direction.  Can be 
	       automated to run with crontab using rsubmit.s and submit.s.

submit.s - Script to run smartgrid.py

rsubmit.s - Driver script to call submit.s.  Place a call to rsubmit.s inside 
	    of a crontab.

update_db.py - Inserts results from a model into the PostgreSQL database on 
	       Corral.  Place a local copy in base/.

runall.s - Main driver script to run NPSM.

Add mplot, mk_mplot4p.py, and run_master_mplot.csh


2.  local
--------------------------------------------------------------------------------

dsphdm2.py - Computes the dark matter density profile by subtracting the
	     stellar profile from the total density profile (determined from
	     plotres and plotres_multi on TACC).  Relies on SSP models from
	     Maraston et al. (2005) in SSP.tab.  Writes out *.res files for 
	     reading with npsm_common.py.  Also fits a power law with Monte
	     Carlo methods (deprecated, use calc_est.py instead).

npsm_common.py - Holds Galaxy class. A Galaxy instance consists of a set of 
	         matplotlib axes with the full dark matter density profile 
		 ready for plotting in a combined plot with plotall.py.  
		 First run dsphdm2.py to calculate the densities.

plotall.py - Constructs a multi-panel plot for a number of galaxies at the
	     same time.  Creates plots like Figure 1 in Jardel & Gebhardt 2013
	     (ApJL 775L, 30 ),

plotall_single_panel.py - Puts all the Galaxy instances on a single panel 
			  like Figure 2 of Jardel & Gebhardt 
			  (2013 ApJL, 775L, 30 ).  Calls plot_dmprof_all()
			  method of Galaxy.

plot_monents_univ.py - Makes plots of Gauss-Hermite moments (V, sigma, h3, h4) for
		       any dSph.  Makes something like Figure 4 of Jardel et al.
		       (2013, 763, 91).  

get_res_all.s - Script to grab all the analysis data (chiXXX.out) from Lonestar,
	        then run dsphdm2.py on each dSph.  Puts .res files in right 
		location for a run with plotall.py.

cmdplot.py - Gets stellar population parameters by fitting isochrones to 
	     color-magnitude diagrams.  Returns [Fe/H] and t_age.

chiPlotter.py - Plays around with results interactively.  Lets the user specify a
	        delta chi^2 threshold and see how the profile changes.  Can also
   		show where (spatially) most of the contribution to total chi^2 
		comes from.  Writes to file readable by the Shiny app in R/.

3.  R
--------------------------------------------------------------------------------

ui.R
server.R 

Routines to run Shiny App to explore output of chiPlotter.py.  See http://rstudio.github.io/shiny/tutorial/ for details on how to use Shiny.

