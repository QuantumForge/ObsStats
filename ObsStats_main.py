#!/usr/bin/env python
# encoding: utf-8


### !/usr/bin/python

import datetime as dt
from optparse import OptionParser
import os
import re
import sys
#import string

# Import global variables into this namespace
import ObsStats_global
m_global = ObsStats_global

# Parse the command-line options
usage = "usage: %prog [-s starting date -e ending date][-t file tag][--dark-only]"
parser = OptionParser(usage)
parser.add_option("-d", "--dark-only", action="store_true", dest="dk_only", default=False, help="exclude non-observing periods")
parser.add_option("-e", "--end", dest="end_date", help="the end date")
parser.add_option("-s", "--start", dest="start_date", help="the start date")
parser.add_option("-t", "--tag", dest="tag", help="an optional file tag")
(options, args) = parser.parse_args()

m_global.dk_only = options.dk_only

## If start_date OR end_date not specified issue warning then exit
if options.start_date == None or options.end_date == None :
    print ("\n** The start and end dates must be specified\n")
    sys.exit()
else:
    ## ... else the start_date AND end_date are specified.
    start_date =  options.start_date
    end_date = options.end_date

## If start_date time not specified set to default value
if not re.search('\d\d:\d\d$',start_date):
    start_date = start_date+' 14:00'
## ... ditto for the end_date time.
if not re.search('\d\d:\d\d$',end_date):
    end_date = end_date+' 14:00'

## Now verify that dates are of a legitimate form, eg 2011-Jan-01 14:00 or 2011-01-01 14:00 ...
## ... and generate the start and end datetime values
## ... both of the form 2011-Jan-01 14:00
if (re.search('^\d\d\d\d-[a-z,A-Z]{3}-\d\d \d\d:\d\d$',start_date) \
    and re.search('^\d\d\d\d-[a-z,A-Z]{3}-\d\d \d\d:\d\d$',end_date)):
    m_global.start_date = dt.datetime.strptime(start_date,"%Y-%b-%d %H:%M")
    m_global.end_date = dt.datetime.strptime(end_date,"%Y-%b-%d %H:%M")
## ... or both of the form 2011-01-01 14:00
elif  (re.search('^\d\d\d\d-\d\d-\d\d \d\d:\d\d$',start_date) \
    and re.search('^\d\d\d\d-\d\d-\d\d \d\d:\d\d$',end_date)):
    m_global.start_date = dt.datetime.strptime(start_date,"%Y-%m-%d %H:%M")
    m_global.end_date = dt.datetime.strptime(end_date,"%Y-%m-%d %H:%M")
## ... or both of mixed form
elif (re.search('^\d\d\d\d-[a-z,A-Z]{3}-\d\d \d\d:\d\d$',start_date) \
    and re.search('^\d\d\d\d-\d\d-\d\d \d\d:\d\d$',end_date)):
    m_global.start_date = dt.datetime.strptime(start_date,"%Y-%b-%d %H:%M")
    m_global.end_date = dt.datetime.strptime(end_date,"%Y-%m-%d %H:%M")
elif  (re.search('^\d\d\d\d-\d\d-\d\d \d\d:\d\d$',start_date) \
    and re.search('^\d\d\d\d-[a-z,A-Z]{3}-\d\d \d\d:\d\d$',end_date)):
    m_global.start_date = dt.datetime.strptime(start_date,"%Y-%m-%d %H:%M")
    m_global.end_date = dt.datetime.strptime(end_date,"%Y-%b-%d %H:%M")
else:
    print (("\n** start/end dates: %s / %s not properly specified\n") % (start_date,end_date))
    sys.exit()

## Write (to stdout) some general info:
print (("Start date: %s, end date: %s\n") % (start_date,end_date))

## Generate a simple tag for use in file names
if options.tag == None:
    m_global.file_tag = m_global.start_date.strftime('%Y%b%d')+'-'+m_global.end_date.strftime('%Y%b%d')
else:
    m_global.file_tag = options.tag

## Open the csv, txt and optionally pickle results files
m_global.CSVFILE = open('Results/ObsStats_'+m_global.file_tag+'.csv',"w")
#m_global.PCKLFILE = open('ObsStatsPckl_'+m_global.file_tag+'.pckl',"w")
m_global.RESFILE = open('Results/ObsStats_'+m_global.file_tag+'.txt',"w")

## Import functions into their own namespace
import ObsStats_days
#import ObsStats_ephem
#import ObsStats_pckl
import ObsStats_runs
import ObsStats_sources
import ObsStats_stats

## Create some simple aliases
m_days = ObsStats_days
#m_ephem = ObsStats_ephem
#m_pckl = ObsStats_pckl
m_runs = ObsStats_runs
m_sources = ObsStats_sources
m_stats = ObsStats_stats

def main():
    m_global.RESFILE.write(("start date: %s  end date: %s\n")%(m_global.start_date,m_global.end_date))
    m_global.RESFILE.write('\n')

    m_global.CSVFILE.write(("start date: %s\nend date: %s\n\n")%(m_global.start_date,m_global.end_date))
    m_global.CSVFILE.flush()

    ## Read in the run info from the dB from start_time to end_time
    ## determine the actual run data duration, and generate sources_in_runs list
    ## start_time and end_time are provided on the command line or by default
    ## in ObsStats_global.
    m_runs.fetch_runs_frm_db()
    if len(m_global.runs) == 0:
        print (("\n** No runs in interval %s to %s \n") % (m_global.start_date,m_global.end_date))
        #return
    else:
        print (("Number of runs in interval: %d \n") % (len(m_global.runs)))


    ## Initialize the source_types dict the and source_classes list
    ##    source_types = {source_type: {source_class, description},...}
    ## and is read in from SourcesNTypes_vX.txt
    ##    source_classes = ['AGN','Crab','DM','ExGalactic', ...]
    ## "source_classes" are already defined for all "source_types"
    m_sources.init_source_types()
    m_sources.init_source_classes()
    m_sources.init_RA_stats()
    
    ## Read in the sources from the dB
    m_sources.fetch_sources_frm_dB()

    ## Loop over the sources dict, determine the "source_type"
    ## and set that value in the sources dict
    ## First try to using SourcesNTypes_vX.  If that doesn't work take a shot
    ## at Simbad.
    m_sources.init_source_type_in_sources()

    ## Filter out (delete) sources from the sources dict which are not present
    ## in any of the runs (ie, period) under consideration.
    ## Also, add a source flag [A-Z,a-z]
    m_sources.update_n_flag_sources()
    print (("Number of sources observed in interval: %d \n") % (len(m_global.sources)))

    ## Initialize a separate _source, _type and _class dicts
    m_sources.init_source_stats()
    m_sources.init_source_type_stats()
    m_sources.init_source_class_stats()

    ## Loop over the runs: determine whether the moon was up or not, and the az and elev
    ## at the run's start and end
    m_runs.init_run_astro_status()
    #return

    ## Initialize the days dict from start_date to end_date. Only days
    ## that pass the cuts on dark time duration (default is a minimum
    ## of 45 mimutes) and moon phase (we don't cut by default) are
    ## considered.
    ##
    ## days is of the form:
    ##    days[start_of_night_date] = {
    ##       'date':day.date(),
    ##       'start_of_night':start_of_night,
    ##       'end_of_night':end_of_night,
    ##       'length_of_night':length_of_night,
    ##       'moon_phase':moon_phase,
    ##       'runs':list()}
    #min_dark_time = dt.timedelta(minutes=45)
    #max_moon_phase = 99.9
    min_dark_time = dt.timedelta(minutes=120)
    max_moon_phase = 66.6
    m_days.init_days(min_dark_time,max_moon_phase)

    m_days.init_daysruns()

    ## This is the routine where the various stats (eg, weather, run mode), are
    ## accumulated.
    m_runs.process_runs()
    #m_runs.print_runs()

    ## Process the runs, generating length_of_data, length_of_observing, and related
    ## duty cycles.
    m_days.process_days()

    ## Process the sources, generating distribution of number of sources in each
    ## source class, and the distribution of sources and exposure in RA
    m_sources.process_sources()

    ## The stats are then printed/plotted by calls to the appropriate routine.
    (cmfig) = m_stats.print_config_mask_dist()
    (omfig) = m_stats.print_observing_mode_dist()
    (rafig) = m_stats.print_RA_dist()
    (rdfig) = m_stats.print_run_duration_dist()
    (rsfig) = m_stats.print_run_status_dist()
    (rtfig) = m_stats.print_run_type_dist()
    (ssfig) = m_stats.print_source_stats_dist()
    (scfig) = m_stats.print_source_class_stats_dist()
    (stfig) = m_stats.print_source_type_stats_dist()
    (tcfig) = m_stats.print_trigger_config_dist()
    (tmfig) = m_stats.print_trigger_multiplicity_dist()
    (wefig) = m_stats.print_weather_dist()
    ## Plot day related values, particularly the duty cycles.
    (dyfig) = m_stats.print_days_dist()

    m_stats.close_stats()

    #m_runs.print_runs()
    #m_days.print_days()
    #m_pckl.dump_stats()

    #for k,v in m_global.days.items():
    #    print(k, v)
    #return

if __name__ == "__main__":
    main()
