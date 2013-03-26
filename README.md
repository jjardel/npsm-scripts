npsm-scripts
============

various bookkeeping procedures and analysis routines for Non-Parametric Schwarzschild Modeling (NPSM)

For use with the NPSM code described in Jardel et al (2013 ApJ 763 91)


PROGRAM DESCRIPTIONS:

mkdb.py, update_db.py, mkdb_from_res.py - create/manage SQL database containing model output.

npsm_common.py - contains methods for Galaxy objects
  
    METHODS:
	1. readres( galname ) - reads .res file output by dsphdm2. 
	2. plot_dmprof() - creates a plot of a single galaxy's DM profile.  Can be strung together with plotall.py to produce multi-panel plots.

cmdplot.py - Fits Isochrones of varying age & metallicity to a color-magnitude
diagram.  

dsphdm.py - takes output from plotres.py and subtracts the stellar density to obtain the dark matter profile.  Calculates uncertainties with Monte Carlo methods.

dsphdm2.py - Same as dsphdm.py but produces .res file for later plotting

plotall.py - Produces publication quality 5-panel plot of the 5 dSphs I've modeled.

plot_moments.py - Plot Gauss-Hermite moments of the input LOSVDs.  Calculates
chi^2 with respect to GH moments for scaling purposes.

smartgrid.py - Iterative sampling scheme described in Jardel et al (2013).  Determines models within delta chi^2 = CHILIM of the minimum and perturbs their parameters by a fractional STEP.  Usage is invoked through a crontab as rsubmit.s >& cron.log

    REQUIRED ANCILLARY SCRIPTS
    - submit.s 
    - rsubmit.s

plotres.py - Statistical analysis routine to determine best-fitting density profile