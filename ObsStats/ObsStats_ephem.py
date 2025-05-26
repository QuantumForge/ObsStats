#!/usr/bin/env python

## The xephem library, ephem, is available at http://rhodesmill.org/pyephem/
## installation is relatively straight forward if you are at all familiar with
## the python environment.

import datetime as dt
#import getopt
#import os
#import re
#import sys
#import string
#import time

import importlib.resources
from . import data

# From the xephem library
from ephem import *

## Import global variables into this namespace
#from ObsStats_global import flwo, full_moons, max_moon_phase
from ObsStats.ObsStats_global import flwo, full_moons

## Import functions into their own namespace
#import ObsStats_days
#import ObsStats_ephem
#import ObsStats_runs
#import ObsStats_sources

## Create some simple aliases
#m_days = ObsStats_days
#m_ephem = ObsStats_ephem
#m_runs = ObsStats_runs
#m_sources = ObsStats_sources

moon = Moon()
sun = Sun()

def findStartStopLofNAndPh(tm,min_dark_time=dt.timedelta(minutes=45),max_moon_phase=66.6):
    """
    Given a date return the start of night, end of night, length of night,
    lenght of moon time, lenght of dark time, and the moon's phase.
    NB the ephem.Date objects are converted to datetime objects
    before being returned!

    The date (tm) is UTC.  Midnight local is ~7hr UTC.

    Start of night is defined as when the sun dips X degrees below the horizon OR
    when the moon sets, but only if the latter is bright (see max moon phase).
    End of night is defined as when the sun rises to within X degrees of the horizon OR
    when the moon rises, but only if the latter is bright (see max moon phase).
    """
    ## Save the existing flwo values for date-time and horizon
    flwo_date = flwo.date
    flwo_horizon = flwo.horizon

    ## On the day in question calculate times for astronomical twilight for sun set and
    ## rise, defined as the time the sun passes -15deg below the horizon
    ## NB: there is a "dipAngle" value but this does not seem to work, also, the conventional
    ## value for the angle below which the sun is "set" is -18deg, but our observing calendar
    ## uses 15 degrees.
    ## NB: For the 2012-2013 season (and presumably beyond, we have to set the horizon to
    ## -16.5 degrees for sun set and -15.0 for sunrise. This is required for the more
    ## sensitive PMTs we installed during the upgrade.
    flwo.date = Date(tm)
    flwo.horizon = degrees('-16:30')

    sun.compute(flwo)
    try:
        prv_sun_set = flwo.previous_setting(sun)
    except AlwaysUpError:
        print ('Circumpolar error! The Sun never sets on this day.')
    except NeverUpError:
        print ('Circumpolar error! The Sun never rises on this day.')

    flwo.horizon = degrees('-15:00')
    sun.compute(flwo)
    try:
        nxt_sun_rise = flwo.next_rising(sun)
    except AlwaysUpError:
        print ('Circumpolar error! The Sun never sets on this day.')
    except NeverUpError:
        print ('Circumpolar error! The Sun never rises on this day.')

    ## Now calculate the _next_ moon rise and set values after the sun set for the moon
    ## horizon = 0degs
    flwo.date = prv_sun_set
    flwo.horizon = degrees('-0:34')
    moon.compute(flwo)
    try:
        nxt_moon_set = flwo.next_setting(moon)
    except AlwaysUpError:
        print ("Circumpolar error! The Moon never sets on this day."
        "Can't calculate next set time.")
    except NeverUpError:
        print ("Circumpolar error! The Moon never rises on this day."
        "Can't calculate next set time.")
    try:
        nxt_moon_rise = flwo.next_rising(moon)
    except AlwaysUpError:
        print ("Circumpolar error! The Moon never sets on this day."
        "Can't calculate next rise time.")
    except NeverUpError:
        print ("Circumpolar error! The Moon never rises on this day."
        "Can't calculate next rise time.")

    ## Restore the original flwo date and horizon
    flwo.date = flwo_date
    flwo.horizon = flwo_horizon

    length_of_night = dt.timedelta(0)
    length_of_dark  = dt.timedelta(0)
    length_of_moon  = dt.timedelta(0)
    
    ## sun set < moon rise < sun rise < moon set
    ## The moon is down at start of night AND rises during the night
    if prv_sun_set < nxt_moon_rise < nxt_sun_rise < nxt_moon_set:
        ## Check that the requirement on dark time is satisfied. If not,
        ## return 0 duration for night, dark, and moon time.
        if (nxt_moon_rise.datetime() - prv_sun_set.datetime() < min_dark_time):
            start_of_night = prv_sun_set.datetime()
            end_of_night = nxt_sun_rise.datetime()
            return (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon.phase)
        if moon.phase < max_moon_phase:
            start_of_night = prv_sun_set.datetime()
            end_of_night = nxt_sun_rise.datetime()
            length_of_night = end_of_night-start_of_night
            length_of_dark = nxt_moon_rise.datetime() - prv_sun_set.datetime()
            length_of_moon = nxt_sun_rise.datetime() - nxt_moon_rise.datetime()
            return (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon.phase)
        else:
            start_of_night = prv_sun_set.datetime()
            end_of_night = nxt_moon_rise.datetime()
            length_of_night = end_of_night-start_of_night
            length_of_dark = length_of_night
            return (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon.phase)
        #print "Test: ",length_of_night
        
    ## sun set < moon set < sun rise < moon rise
    ## The moon sets during the night
    if prv_sun_set < nxt_moon_set < nxt_sun_rise < nxt_moon_rise:
        ## Start by checking that we meet the requirement on minimum
        ## duration of dark time.
        if (nxt_sun_rise.datetime() - nxt_moon_set.datetime() < min_dark_time):
            start_of_night = prv_sun_set.datetime()
            end_of_night = nxt_sun_rise.datetime()
            return (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon.phase)
        if moon.phase < max_moon_phase:
            start_of_night = prv_sun_set.datetime()
            end_of_night = nxt_sun_rise.datetime()
            length_of_night = end_of_night-start_of_night
            length_of_dark = nxt_sun_rise.datetime() - nxt_moon_set.datetime()
            length_of_moon = nxt_moon_set.datetime() - prv_sun_set.datetime()
            return (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon.phase)
        else:
            start_of_night = nxt_moon_set.datetime()
            end_of_night = nxt_sun_rise.datetime()
            length_of_night = end_of_night-start_of_night
            length_of_dark = length_of_night
            return (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon.phase)

    ## sun set < sun rise < moon rise < moon set
    ## The moon is down and does not rise during the night
    if prv_sun_set < nxt_sun_rise < nxt_moon_rise < nxt_moon_set:
        start_of_night = prv_sun_set.datetime()
        end_of_night = nxt_sun_rise.datetime()
        length_of_night = end_of_night-start_of_night
        length_of_dark = length_of_night
        return (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon.phase)

    ## sun set < sun rise < moon set < moon rise
    ## xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ## The moon is up all night
    ## We shouldn't be observing in this case since there is no dark time.
    if prv_sun_set < nxt_sun_rise < nxt_moon_set < nxt_moon_rise:
        start_of_night = prv_sun_set.datetime()
        end_of_night = nxt_sun_rise.datetime()
        return (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon.phase)
        #if moon.phase < max_moon_phase:
        #    start_of_night = prv_sun_set.datetime()
        #    end_of_night = nxt_sun_rise.datetime()
        #    length_of_night = end_of_night-start_of_night
        #    length_of_moon = length_of_night
        #    return (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon.phase)
        #else:
        #    start_of_night = prv_sun_set.datetime()
        #    end_of_night = prv_sun_set.datetime()
        #    return (start_of_night, end_of_night, length_of_night, length_of_dark, length_of_moon, moon.phase)

    if 1:
        print ("\n** An error occured: findStartStopAndLoN failed\n")
        exit()

    return

def isMoonUp(run_start_tm, run_end_tm):
    """
    Given a the time at which a run starts and end determine whether there
    moon is up at any point in between.

    The date (tm) is UTC.  Midnight local is ~7hr UTC.
    """
    ## Save the existing flwo values for date-time and horizon
    flwo_date = flwo.date

    flwo.date = run_start_tm
    moon.compute(flwo)
    if moon.alt >= 0.0:
        flwo.date = flwo_date
        return 'Y'

    flwo.date = run_end_tm
    moon.compute(flwo)
    if moon.alt >= 0.0:
        flwo.date = flwo_date
        return 'Y'

    flwo.date = flwo_date
    #print moon.alt,run_end_tm
    return 'N'

def fetchFullMoons():
    """
    Open the FullMoons text file and read in each line, parse the line
    e.g., '2000-Jan-21 04:42'    2451564.696
    throwing away the julian date, convert the time string to a datetime object.
    """
    inp_file = importlib.resources.files(data).joinpath('FullMoons.txt')
    FMFILE = open(inp_file,'r')
    ## Read the entire file into the destination array
    lines = FMFILE.readlines()
    ## Skip the first line which contains header info
    for line in lines[1:]:
        full_moons.append(dt.datetime.strptime(line[0:19],"'%Y-%b-%d %H:%M'"))
    FMFILE.close()

    return
