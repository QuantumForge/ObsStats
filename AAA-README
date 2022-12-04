This code was created basically to generate some observing stats for
the quarterly reports (good riddance) to our paymasters, the JOG.

A few "external" python modules are required:

numpy http://numpy.scipy.org/
matplotlib http://matplotlib.sourceforge.net/
pyephem http://rhodesmill.org/pyephem/

otherwise its all pretty much standard stuff found in any distribution.

Once it is running the only "maintenance" required is to update the
SourcesNTypes.txt file.  If a new source is inserted in the database then
an entry should be placed in the SourcesNTypes file to identify what type
of source it is (eg, pulsar, AGN).  If the source can't be found in the
SourcesNTypes file then an attempt is made to determine the source type by
accessing SIMBAD.  The results however are not all that reliable.

AAA-README: this file

FullMoons.txt: contains the date and time of the full moon (including JD)
  from Jan 2000 to Dec 2019.

ObsStats.php: php script to generate the Observing Stats page at
  http://veritas.sao.arizona.edu/private/ObsStats/Results/ObsStats.php

ObsStats_Msgs.png: part of the ObsStats web page

ObsStats_Summary.png: ditto

ObsStats_days.py: for the period of interest (month, season, last night
  or user defined) this module initializes a python dictionary (array)
  with the start of night, end of night, length of night, runs in that
  night, etc..

ObsStats_ephem.py: a module with two principal routines, one to determine
  the beginning and end of each night, and the phase of the moon, and one
  just to determine whether the moon is up at a particular point in time.

ObsStats_global.py: an ugly hack ... globals are bad, nasty things

ObsStats_intervals.py: this module generates three intervals, "last night",
  this month (since the last full moon), and this season (defined starting
  on September 1).  It then makes three calls to ObsStats_main with these
  interval values.

ObsStats_main.py: validates the command-line arguments and then calls all
  the other routines

ObsStats_pckl.py: this routine will "pickle" the observing stats in a
  compressed form, retaining data structures, etc.  Unused.

ObsStats_runs.py: makes a call to the dB and fetches the information out
  of tblRun_Info for each run in the interval, loops over the runs and
  establishes whether the moon was up during any point in the run, and the
  azimuth and elevation of the source at the start and end of each run.
  The main function processes each run to accumulate stats such as what
  source was observed (and how long), the pointing mode, etc..

ObsStats_sources.py: fetches the sources from the dB.  Since the database
  entry does not classify sources as to Type (eg, pulsar, SNR) or source
  Class (ie, where it fits in with respect to the old key science projects),
  this information is extracted in part from SourcesNTypes.  Given a source
  Type the Class is determined from a lookup table.  If the source is not
  in the SourcesNTypes file a call is made to SIMBAD.  The results are not
  particularly reliable.  Two "source type" error messages may emerge from
  this process:

  ** SIMBAD reports BLOTZ as source_id|source_type BLOTZ|Pulsar ~ **

  where the source has (presumably) been correctly identified as a
  pulsar (or whatever), and something like

  ** source_id 2FGL J0221.2+2516 of unknown source_type **

  where the source wasn't in the SourcesNTypes file and couldn't be found
  by SIMBAD.  In this case its just type and classed as UNKNOWN and
  UNKNOWN

  When you see such messages it is best to update the SourcesNTypes files
  manually.

ObsStats_stats.py: this module generates all the plots, text and csv
  output files.

SourcesNTypes.txt: the oft mentioned SourcesNTypes file.  This is the
  file which needs updating as sources are added to the dB (which is
  surprisingly frequently).

cronjob: its a cronjob (which runs every morning about 7am) and calls
  ObsStats_intervals to generate the plots, etc for the ObsStats webpage.




- k
