#!/usr/bin/env python

import datetime as dt
#import getopt
#import math
#import os
#import re
#import sys
#import string
#import time

## Import global variables into this namespace
from ObsStats.ObsStats_global import *

## Import functions into their own namespace
#import ObsStats_days
from ObsStats import ObsStats_ephem
#import ObsStats_runs
from ObsStats import ObsStats_sources

## Create some simple aliases
#m_days = ObsStats_days
m_ephem = ObsStats_ephem
#m_runs = ObsStats_runs
m_sources = ObsStats_sources

#def init_days(min_dark_time=dt.timedelta(minutes=10),max_moon_phase=99.9):
#def init_days(min_dark_time=dt.timedelta(minutes=45),max_moon_phase=99.9):
def init_days(min_dark_time=dt.timedelta(minutes=120),max_moon_phase=66.6):
    """
    From start_date to the end_date fill the 'days' dictionary
    with values: start_of_night, end_of_night, length_of_night and the moon's phase.

    An empty list 'daysruns' is also created.  This list will contain all runs taken on
    the night in question..
    """
    ## Day, though measured in UTC, starts out at local midnight on the start_date ...
    day = start_date.replace(hour=7,minute=0,second=0,microsecond=0)
    while day < end_date:
        ## ObsStats_ephem returns time values as datetime objects
        (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon_phase) = \
            m_ephem.findStartStopLofNAndPh(day,min_dark_time,max_moon_phase)
        ## Extract the date portion
        start_of_night_date = start_of_night.date()
        end_of_night_date = end_of_night.date()
        ## Perform a sanity check:
        ## ... start and end of night should be on the same UTC datetime ...
        if start_of_night_date != end_of_night_date:
            print ("\n** An error occured: start_of_night_date != end_of_night_date\n")
            exit()
        ## ... and the length of night should be less than 12 hours
        if length_of_night > dt.timedelta(hours=12):
            print ("\n** An error occured: length_of_night is greater than 12 hours\n")
            exit()
        #days[start_of_night_date] = {
        days[day.date()] = {
            #'date':day.date(),
            'start_of_night':start_of_night,
            'end_of_night':end_of_night,
            'length_of_night':length_of_night,
            'length_of_dark':length_of_dark,
            'length_of_moon':length_of_moon,
            'length_of_data':dt.timedelta(),
            'length_of_obs':dt.timedelta(),
            'data_dc':0.0,'obs_dc':0.0,
            'moon_phase':moon_phase,
            'daysruns':[],'avgwea':0.0
            #'timeline':[['-']*720,['-']*720]
            }
        day = day + dt.timedelta(days=1)

    return

def init_daysruns():
    """
    For each run insert its run_id into the 'runs' list of the appropriate
    dict 'days' value

    Need to properly assign runs to each _local_ night's observing period.
    Runs after noon local (ie, runs whose time is after seventeenhours UTC) are
    associated with that local day's night. PF: I DON'T THINK THIS IS TRUE.

    Eg.
      UTC day 5 Dec 1955 at 18:00 the local time in AZ is 1pm.  A run at that
      time would be associated with all the runs
    """
    seventeenhours = dt.time(hour=17,minute=0,second=0,microsecond=0)
    for run_id, run in runs.items():
        ## First, fetch run's UTC start time and date
        run_date = run['data_start_time'].date()
        run_time = run['data_start_time'].time()
        ## ... if its start time is later than 17 hours UTC (ie, after 12 noon local)
        ## ... it ought to appear in the next day's daysruns list
        #if run_time > seventeenhours:
            ## ... so increment run_date by 1 day
            #    run_date = run_date + dt.timedelta(days=1)
        days[run_date]['daysruns'].append(run_id)

    return

#def UTC2tick(utc_event_time):
    #"""
    #time will typically be a run's start or stop time (of type datetime.datetime)

    #Calculate the UTC time at 18hours local on that date (ie, 0100 hrs UTC), then find
    #the difference between that time and evtime in minutes.
    #"""
    #eighteenhourslocal_utc = \
        #utc_event_time.replace(hour=1,minute=0,second=0,microsecond=0)
    #delta_t = utc_event_time - eighteenhourslocal_utc
    #tick = delta_t.days*1440.+delta_t.seconds/60.+delta_t.microseconds/(60.*1000000.)
    #return int(tick+0.5)

def print_day(day):
    print("")
    #print("date: %s") % (day['date'])
    start_of_night = day['start_of_night'].strftime('%Y-%m-%d %H:%M:%S')
    end_of_night = day['end_of_night'].strftime('%Y-%m-%d %H:%M:%S')
    print("start_of_night: %s  end_of_night: %s") % \
        (start_of_night, end_of_night),
    length_of_night_hrs = duration2hours(day['length_of_night'])
    length_of_data_hrs = duration2hours(day['length_of_data'])
    length_of_obs_hrs = duration2hours(day['length_of_obs'])
    print("lon: %4.2f  lod: %4.2f  loo: %4.2f") % \
        (length_of_night_hrs,length_of_data_hrs,length_of_obs_hrs)
    print ("Length of dark: %s Length of Moon: %s" % \
        (day['length_of_dark'],day['length_of_moon']))
    print("moon_phase: %4.2f  avgwea: %4.2f") % \
        (day['moon_phase'],day['avgwea'])
    print("daysruns: %s") % (day['daysruns'])

    return

def print_days():
    for key in sorted(days.keys()):
        print_day(days[key])

    return

def print_timelines(day):
    """
    timeline0 and timeline1 are 720 character strings which represent 1 minute intervals
    from 1800 hrs local to 0600 hours local.

    Print the two out as 9 lines of 80 characters each.
    """
    timeline0 = ''.join(day['timeline'][0])
    timeline1 = ''.join(day['timeline'][1])

    print ("start_of_night: %s   end_of_night: %s") % \
        (day['start_of_night'],day['end_of_night'])
    print ("dayruns: %s") % (day['daysruns'])
    for line in range(0,9):
        fstchar = 0 + line*80
        lstchar = 79 + line*80
        print (timeline0[fstchar:lstchar])
        print (timeline1[fstchar:lstchar])
        print ("")

    return

def process_days():
    """
    Loop over the SORTED days accumulating total duration of runs for
    each day, and total for period.

    days = {date: {start_of_night:datetime, end_of_night:datetime,
      length_of_night:datetime.timedelta,
      phase_of_moon:percent, runs[]},}
    """
    tot_len_of_night = dt.timedelta(0)
    tot_len_of_dark = dt.timedelta(0)
    tot_len_of_moon = dt.timedelta(0)
    tot_len_of_data = dt.timedelta(0)
    tot_len_of_obs = dt.timedelta(0)
    #print(days)
    for date, day in days.items():
        ## For this day fetch the start_ and end_of_night, and its length
        start_of_night = days[date]['start_of_night']
        end_of_night = days[date]['end_of_night']
        length_of_night = days[date]['length_of_night']
        length_of_dark = days[date]['length_of_dark']
        length_of_moon = days[date]['length_of_moon']
        ## If the length_of_night is less than 60 minutes, skip it
        if length_of_night < dt.timedelta(minutes=60):
            continue
        length_of_data = dt.timedelta(0)
        length_of_obs = dt.timedelta(0)
        wea_scld_length_of_obs = 0.
        ## Accumulate the total length of night's runs
        daysruns = days[date]['daysruns']
        ## ... initialize some values prior to looping through the night's runs
        ## <RUN INTERVAL PLOTS
        start_of_run = dt.datetime(2000,1,1)
        end_of_run = dt.datetime(2000,1,1)
        length_of_run = dt.timedelta(0)
        run_type = ''
        source_id = ''
        default_mask = 0
        all_tels_working = False
        for run_id in daysruns:
            #if runs[run_id]['run_type'] == 'observing':
            #    if (all_tels_working == False) and (runs[run_id]['config_mask'] == 15 \
            #                                        and (runs[run_id]['data_duration'].total_seconds() >600.0)):
            #        default_mask = 15
            #        all_tels_working = True
            #    elif (all_tels_working == False) and (runs[run_id]['config_mask'] != 15 \
            #                                          and (runs[run_id]['data_duration'].total_seconds() >600.0)):
            #        default_mask = runs[run_id]['config_mask']
            last_start_of_run = start_of_run
            last_end_of_run = end_of_run
            last_length_of_run = length_of_run
            last_run_type = run_type
            last_source_id = source_id
            ## Fetch the start and end of the run ...
            start_of_run = runs[run_id]['data_start_time']
            end_of_run = runs[run_id]['data_end_time']
            length_of_run = runs[run_id]['data_duration']
            run_type = runs[run_id]['run_type']
            source_id = runs[run_id]['source_id']
            weather = runs[run_id]['weather']
            if weather not in weather_keys:
                continue
            weatherval = 1. - weather_keys.index(weather)/13.
            delt = start_of_run - last_end_of_run
            if last_source_id == source_id and \
                (run_type == 'observing' or run_type == 'obsFilter' or run_type == 'obsLowHV'):
                deltsec = delt.seconds+delt.microseconds/1000000.+0.5
                #print ('%s,%s,%s,%s,%s') % (source_id, last_end_of_run, start_of_run, end_of_run, int(deltsec))
            else:
                last_source_id = source_id
            last_end_of_run = end_of_run

            ## All remaining runs are during observing period
            ## ... accumulate length of data (includes ALL logged data) for _this_ night
            length_of_data += length_of_run
            ## ... for run_type == observing accumulate the total time for _this_ night
            if run_type == 'observing' or run_type == 'obsFilter' or run_type == 'obsLowHV':
                length_of_obs += length_of_run
                wea_scld_length_of_obs += length_of_run.days*86400.*weatherval \
                    + length_of_run.seconds*weatherval
            ### Accumulate some stats concerning the run to run interval
            ### distribution of gaps in data taking and length of time for slewing
            ##if last_end_of_run != datetime.datetime.combine(day,datetime.time(0,0)):
                ##dt_run_to_run_all = start_of_run - last_end_of_run
                ##if source_id == last_source_id:
                    ##dt_run_to_run_same = start_of_run - last_end_of_run
            ##last_end_of_run = end_of_run
            ##last_source_id = source_id
            ##last_run_type_flag = run_type_flag
        ## Finished processing runs for this night so initialize days length of data and observing
        #print date,default_mask
        days[date]['length_of_data'] = length_of_data
        days[date]['length_of_obs'] = length_of_obs
        ## Calculate duty cycles ...
        tnght = length_of_night.days*86400.+length_of_night.seconds #+length_of_night.microseconds*1000000.
        tdata = length_of_data.days*86400.+length_of_data.seconds #+length_of_data.microseconds*1000000.
        tobs = length_of_obs.days*86400.+length_of_obs.seconds #+length_of_obs.microseconds*1000000.
        twsobs = wea_scld_length_of_obs
        data_dc = 0.
        obs_dc = 0.
        avgwea = 99.
        if tnght > 0.:
            data_dc = tdata/tnght
            obs_dc = tobs/tnght
            if tobs > 0.:
                avgwea = twsobs/tobs
        ## ... and initialize days duty cycle values
        days[date]['data_dc'] = data_dc
        days[date]['obs_dc'] = obs_dc
        days[date]['avgwea'] = avgwea
        ## Accumulate totals for this period
        tot_len_of_night += length_of_night
        tot_len_of_dark += length_of_dark
        tot_len_of_moon += length_of_moon
        tot_len_of_data += length_of_data
        tot_len_of_obs += length_of_obs
    tnght = tot_len_of_night.days*86400.+tot_len_of_night.seconds #+tot_len_of_night.microseconds*1000000.
    tdata = tot_len_of_data.days*86400.+tot_len_of_data.seconds #+tot_len_of_data.microseconds*1000000.
    tobs = tot_len_of_obs.days*86400.+tot_len_of_obs.seconds #+tot_len_of_obs.microseconds*1000000.
    if tnght > 0.:
        data_dc = tdata/tnght
        obs_dc = tobs/tnght
        print (('Total length of night: %s (dark: %s, moon: %s)\n') % (print_deltat(tot_len_of_night),print_deltat(tot_len_of_dark),print_deltat(tot_len_of_moon)))
        print (("Total length of data: %s and data duty cycle: %5.3f\n") % \
                   (print_deltat(tot_len_of_data),tdata/tnght))
        print (("Total length of observing: %s and observing duty cycle: %5.3f") % \
                   (print_deltat(tot_len_of_obs),tobs/tnght))
        print("")
        #print ("total length of night: %s") % (tot_len_of_night)
        #print ("total length of data: %s  duty cycle: %2f") % (tot_len_of_data,data_dc)
        #print ("total length of obs: %s  duty cycle: %2f") % (tot_len_of_obs,obs_dc)
        #print (f"total length of night: {tot_len_of_night}")
        print (f"total length of data: {tot_len_of_data}  duty cycle: {tdata/tnght:5.3f}")
        print (f"total length of obs: {tot_len_of_obs}  duty cycle: {tobs/tnght:5.3f}")
    else:
        print ("** total length of night is zero")

    return
