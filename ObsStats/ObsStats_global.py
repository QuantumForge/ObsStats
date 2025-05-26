#!/usr/bin/env python

## ObsStats_global is a very non-pythonic way of making "global" values
## available to all the ObsStats modules.  My bad.

## system packages
import datetime as dt
#import getopt
import math
#import os
import re
import sys
import string
#import time

## From the xephem library
import ephem as eph

## Reserve some global values which will be initialized in the ObsStats_main
## Handles for the csv, txt and optional pickle files
CSVFILE = None
#PCKLFILE = None
RESFILE = None

# these globals need to be set on the command line or
# in the toml file ObsStats/data/ObsStats.ini
# which host to use for database connections
#
# format of ObsStats.ini:
# [database]
# host = "<hostname>"
# user = "<username>"
# db_name = "<db_name>"
# [simbad]
# host = "<hostname>"
#
db_host = None
db_user = None
db_name = None
# host used for simbad lookups
simbad_host = "simbad.u-strasbg.fr"

## An option to exclude all periods when the moon is up, however bright
dk_only = None
## Start and end of interval dates and a file_tag generated therefrom.
start_date = None
end_date = None
file_tag = None

## Two lists for distribution of sources in RA and distribution of
## observing time (exposure)
#RA_sourceNumber_dist =  [0]*24
#RA_exposure_dist =   [dt.timedelta(0)]*24
#RA_exposure_dist =   [0.]*24
RA_stats = {}

## DICT FOR SOURCES INFO (TO BE READ FROM dB)
## sources = {source_id: {desc:txt, ra:RA in rads, decl:Decl in rads,
##   epoch:epoch of coords, source_type:txt, flag:char},}
sources = {}

## DICT FOR SOURCE_STATS
## source_stats = {source_id: {n_runs:int, duration:datetime.timedelta, \
##   awea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
##   bwea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
##   etc}
source_stats = {}

## Some particular/peculiar source_ids
isBSC = re.compile('^BSC ',re.IGNORECASE)
isCalEng = re.compile('(biasCurve|chargeInjection|laser|other|pedestal|roadlaser|test|zenith)',re.IGNORECASE)
isDARK = re.compile('^DARK_',re.IGNORECASE)
isFAKE = re.compile('^Fake-',re.IGNORECASE)
isNOSOURCE = re.compile('NOSOURCE',re.IGNORECASE)
isSTAR = re.compile('^Star ',re.IGNORECASE)
isTEST = re.compile('TEST',re.IGNORECASE)
isZENITH = re.compile('ZENITH',re.IGNORECASE)

isANHER = re.compile('AN HER',re.IGNORECASE)
isCRAB = re.compile('^CRAB',re.IGNORECASE)
isCygHS = re.compile('Cygnus *HS',re.IGNORECASE)
isGRBv1 = re.compile(r'^GRB *\d\d\d\d\d\d',re.IGNORECASE)   #GRB123456
isGRBv2 = re.compile(r'^GRB *(\d\d|\d\d\d\d)-\d\d-\d\d',re.IGNORECASE) #GRB 1234-56-78 | GRB 12-34-56
isIC433 = re.compile('IC *433',re.IGNORECASE)
isMilSURVEY = re.compile(r'^MilSS *\d{2,3}',re.IGNORECASE)
isREGULUS = re.compile('^Regulus',re.IGNORECASE)
isSURVEY = re.compile(r'^SS *\d{2,3}',re.IGNORECASE)
isTHETA1 = re.compile('^Theta1',re.IGNORECASE)

## DICT FOR SOURCE_TYPES
# source_types = {source_type: {source_class, description},...}
source_types = {}
# source_types is initialized in ObsStats_sources, ie:
#source_types = {
    #'AGN':['AGN','Active Galaxy Nucleus'],
    #'AMHer':['Galactic','Catalysmic Variable'],
    #'BLLac':['AGN','BL Lac'],
    ##'Blazar':['AGN','Blazar'],
    #'ClG':['ExGalactic','Cluster of Galaxies'],
    #'Crab':['Crab','Crab'],
    #'DwarfG':['DM','Dwarf Galaxy'],
    #'EmG':['ExGalactic','Emission-line Galaxy '],
    #'FR_II':['AGN','FR II Radio Galaxy'],
    #'FSRQ':['AGN','Radio Loud AGN'],
    #'GRB':['GRB','Gamma-ray Burst'],
    #'Galaxy':['ExGalactic','Galaxy'],
    #'GinGroup':['ExGalactic','Galaxy in Group of Galaxies '],
    #'GlCl':['ExGalactic','Globular Cluster'],
    #'HMXB':['Galactic','High Mass X-ray Binary'],
    #'Hotspot':['Unknown','Hotspots identified by others or in the SkySurvey'],
    #'IG':['ExGalactic','Interacting Galaxies'],
    #'LINER':['ExGalactic','LINER-type Active Galaxy Nucleus'],
    #'LMXB':['Galactic','Low Mass X-ray Binary'],
    ##'MolCld':['Galactic','Molecular Cloud'],
    #'Neb':['Galactic','Nebula'],
    #'NOSOURCE':['NOSOURCE','Not a source'],
    #'OpCl':['ExGalactic','Open Galactic Cluster'],
    #'Pulsar':['Galactic','Pulsar'],
    #'QSO':['AGN','QSO'],
    ##'QSO_Candidate':['AGN','QSO_Candidate'],
    #'Radio':['ExGalactic','Radio Source (unknown)'],
    #'RadioG':['ExGalactic','Radio Galaxy'],
    #'SNR':['Galactic','SNR'],
    #'Seyfert':['AGN','Seyfert'],
    #'Seyfert_1':['AGN','Seyfert_1'],
    #'Seyfert_2':['AGN','Seyfert_2'],
    ##'Star':['NOSOURCE','Not a source'],
    #'SkySurvey':['SkySurvey','SkySurvey'],
    #'UID':['Unknown','Unidentified Gamma Source'],
    #'Unknown':['Unknown','Unknown'],
    #'WR*':['Galactic','Wolf-Rayet Star'],
    #}

## DICT FOR SOURCE_TYPE_STATS
# source_type_stats = {source_type: {n_sources(of type):int, n_runs:int, \
#    awea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
#    bwea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
#    etc}
source_type_stats = {}

## LIST FOR SOURCE_CLASSES
source_classes = []
# source_classes is initialized in ObsStats_sources, ie:
#source_classes = ['AGN','Crab','DM','ExGalactic','Galactic','GRB','NOSOURCE',
    #'SkySurvey','Unknown']

## DICT FOR SOURCE_CLASS_STATS
# source_class_stats = {source_class: {n_sources(of type):int, n_runs:int, \
#    awea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
#    bwea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
#    etc}
source_class_stats = {}

## DICT FOR "RUNS" INFO (TO BE READ FROM dB)
## runs = {run_id: {run_type:txt, observing_mode:enum txt run_status: enum txt,
##   db_start_time: datetime, db_end_time: datetime,
##   data_start_time: datetime, data_end_time: datetime, duration: time,
##   weather: enum txt, config_mask: int, pointing_mode: enum txt,
##   trigger_config: enum txt, trigger_multiplicity: int, trigger_coincidence: float,
##   offsetRA: rads, offsetDEC: rads, offset_distance: rads, offset_angle: rads,
##   source_id:txt,
##   moonlit:Y/N,
##   run_date:datetime.date}, ...}
##
## run_type == enum('observing', 'chargeInjection', 'laser', 'pedestal',
##   'biasCurve', 'roadlaser', 'test', 'other')
## observing_mode == enum('on', 'off', 'wobble', 'tracking', 'survey',
##   'zenith', 'drift', 'engineering', 'calibration', 'other')
## run_status == enum('prepared', 'defined', 'started', 'aborted', 'ended',
##   'manually_ended', 'test')
## weather == enum('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+',
##   'D', 'D-', 'F')
## pointing_mode == enum('parallel', 'convergent', 'tracking', 'zenith', \
##   parked', 'drift', 'N/A', 'other')
## trigger_config == enum('normal', 'external', 'muon', 'force_full', \
##   'roadlaser', 'low_gain_pedestal', 'T1T4required', 'T1T4suppressed', \
##   'low_energy_optimized', 'custom_test', 'other')
##
## moonlit is added in set_runs_moon_status()
## run_date is added in fetch_runs_frm_db and is the date associated
## with data_start_time
runs = {}

## A LIST FOR SOURCE_IDs WHICH ARE AMONG THE "RUNS"
sources_in_runs = []

## A LIST FOR RUN DURATIONS
run_duration_dist = [0]*32

## DICT FOR "DAYS"
## days = {date: {start_of_night:datetime, end_of_night:datetime,
##   length_of_night:datetime.timedelta,
##   length_of_data:datetime.timedelta,length_of_obs:datetime.timedelta,
##   data_dc:0.0,obs_dc:0.0,
##   phase_of_moon:percent, daysruns:[],
##   avgwea:0.0},...}
days = {}

### LISTS used in the "tic" routines (ie, they are not used)
#len_of_night_dist = [0]*720
#len_of_data_dist = [0]*720
#len_of_obs_dist = [0]*720
#duty_cycle_dist = [0]*100

## DICT FOR "OBSERVING MODE"
## e.g. observing_mode['wobble'] = {number of on runs:int, \
##   duration:datetime.timedelta}
observing_mode = {}
observing_mode['calibration'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['drift'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['engineering'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['off'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['on'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['other'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['survey'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['tracking'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['wobble'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['zenith'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['orbit'] = {'n_runs':0, 'duration':dt.timedelta(0)}
observing_mode['UNK'] = {'n_runs':0, 'duration':dt.timedelta(0)}

## DICT FOR "POINTING MODE"
pointing_mode = {}
pointing_mode['convergent'] = {'n_runs':0, 'duration':dt.timedelta(0)}
pointing_mode['drift'] = {'n_runs':0, 'duration':dt.timedelta(0)}
pointing_mode['N/A'] = {'n_runs':0, 'duration':dt.timedelta(0)}
pointing_mode['other'] = {'n_runs':0, 'duration':dt.timedelta(0)}
pointing_mode['parallel'] = {'n_runs':0, 'duration':dt.timedelta(0)}
pointing_mode['parked'] = {'n_runs':0, 'duration':dt.timedelta(0)}
pointing_mode['tracking'] = {'n_runs':0, 'duration':dt.timedelta(0)}
pointing_mode['zenith'] = {'n_runs':0, 'duration':dt.timedelta(0)}
pointing_mode['UNK'] = {'n_runs':0, 'duration':dt.timedelta(0)}

## DICT FOR "RUN STATUS"
run_status = {}
run_status['aborted'] = {'n_runs':0, 'duration':dt.timedelta(0)}
run_status['completed'] = {'n_runs':0, 'duration':dt.timedelta(0)}
run_status['defined'] = {'n_runs':0, 'duration':dt.timedelta(0)}
run_status['ended'] = {'n_runs':0, 'duration':dt.timedelta(0)}
run_status['manually_ended'] = {'n_runs':0, 'duration':dt.timedelta(0)}
run_status['prepared'] = {'n_runs':0, 'duration':dt.timedelta(0)}
run_status['started'] = {'n_runs':0, 'duration':dt.timedelta(0)}
run_status['test'] = {'n_runs':0, 'duration':dt.timedelta(0)}
run_status['UNK'] = {'n_runs':0, 'duration':dt.timedelta(0)}

## DICT FOR "RUN TYPE"
# There is no run_type 'zenith', this value is for use in timeline
#
# DARK_X_Y.Z have run_type 'observing' but are not observations.
# In m_runs.fetch_runs_frm_db their run_type is switched to 'dark', and
# their observing_mode to 'calibration'.
#
# BSC also have run_type 'observing' but are similarly no observations.
# In m_runs.fetch_runs_frm_db their run_type is switched to 'bsc', and
# their observing_mode to 'calibration'.
run_type = {}
run_type['biasCurve'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'@'}
run_type['bsc'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'*'}
run_type['chargeInjection'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'#'}
run_type['dark'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'_'}
run_type['flasher'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'$'}
run_type['highlow'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'$'}
run_type['laser'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'%'}
run_type['highlow'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'%'}
run_type['observing'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'O'}
run_type['obsFilter'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'OF'}
run_type['obsLowHV'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'OL'}
run_type['other'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'"'}
run_type['pedestal'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'&'}
run_type['roadlaser'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'+'}
run_type['test'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'='}
run_type['UNK'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'?'}
run_type['zenith'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'^'}
run_type['rasterScan'] = {'n_runs':0, 'duration':dt.timedelta(0),'flag':'^'}


## DICT FOR "TRIGGER CONFIGuration"
trigger_config = {}
trigger_config['custom_test'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['external'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['force_full'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['low_energy_optimized'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['low_gain_pedestal'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['muon'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['normal'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['other'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['roadlaser'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['T1T4required'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['T1T4suppressed'] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_config['UNK'] = {'n_runs':0, 'duration':dt.timedelta(0)}

## DICT FOR "WEATHER", weather = 'X' is treated as UNK
weather = {}
weather['A+'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['A'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['A-'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['B+'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['B'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['B-'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['C+'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['C'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['C-'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['D+'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['D'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['D-'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['F'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather['UNK'] = {'n_runs':0, 'duration':dt.timedelta(0)}
weather_keys = ['A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','UNK']

## LIST FOR "CONFIG_MASK"
## config_mask is an integer value from 0 to 15 which represents the
## bit mapped telescope trigger participation in each event.  Eg, 1101
## indicates that telescopes 1, 3 and 4, but not 2 were in the event.
##
## It would be more appropriate to call this tele_trig_participation!
##
## config_mask, decimal value, # teles triggered, telescope triggered
##   0000, 0,0, NONE
##   0001, 1,1, t1
##   0010, 2,1, t2
##   0100, 4,1, t3
##   1000, 8,1, t4
##
##   0011, 3,2, t1t2
##   0101, 5,2, t1t3
##   1001, 9,2, t1t4
##   0110, 6,2, t2t3
##   1010,10,2, t2t4
##   1100,12,2, t3t4
##
##   0111, 7,3, t1t2t3
##   1011,11,3, t1t2t4
##   1101,13,3, t1t3t4
##   1110,14,3, t2t3t4
##
##   1111,15,4, t1t2t3t4
#config_mask = [0]*16
config_mask = {}
config_mask[0] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[1] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[2] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[3] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[4] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[5] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[6] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[7] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[8] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[9] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[10] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[11] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[12] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[13] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[14] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask[15] = {'n_runs':0, 'duration':dt.timedelta(0)}
config_mask_map = ['NONE', 'T1', 'T2', 'T1T2', 'T3', 'T1T3', \
    'T2T3', 'T1T2T3', 'T4', 'T1T4', 'T2T4', 'T1T2T4', \
    'T3T4', 'T1T3T4', 'T2T3T4', 'T1T2T3T4']

## LIST FOR "TRIGGER_MULTIPLICITY"
trigger_multiplicity = [0]*5
trigger_multiplicity[0] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_multiplicity[1] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_multiplicity[2] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_multiplicity[3] = {'n_runs':0, 'duration':dt.timedelta(0)}
trigger_multiplicity[4] = {'n_runs':0, 'duration':dt.timedelta(0)}

## LIST FOR  AN ARRAY OF THE FULL MOONS FROM JAN 2000 TO DEC 2019
## The values are stored in "FullMoons.txt" as a datetime string and
## an MJD.
full_moons = []

# Create an instance of Observer and initialize it
#
# NB the data/time stored in Observer are UTC
flwo = eph.Observer()
flwo.long = eph.degrees('-110:57:08')
flwo.lat = eph.degrees('31:40:30')
flwo.elevation = 1269.5
flwo.pressure = 0.0
flwo.horizon = eph.degrees('00:00') # the default value

## dipAngle does not seem to do what it should, use flwo.horizon instead
#dipAngle = -0.314159 # == 18deg dip angle, only use with SUN!!

# the percentage of moon illumination beyond which it is assumed to be too bright
# to observe. This is done in the ephem library now...
#max_moon_phase = 66.6

def duration2minutes(delta_t):
    """
    Given a datetime.timedelta value calculate the equivalent
    in minutes, rounded to the nearest minute.

    The microseconds bit of delta_t is ignored.
    """
    days = delta_t.days
    seconds = delta_t.seconds
    # Round seconds to the nearest minute
    seconds += 30
    minutes = days*1440 + seconds/60
    return minutes

def duration2hours(delta_t):
    """
    Given a datetime.timedelta value calculate the equivalent
    in hours.
    """
    days = delta_t.days
    seconds = delta_t.seconds
    #microseconds = delta_t.microseconds
    hours = days*24. + seconds/3600. #+ microseconds/3600./1000000.
    return hours

def datetime2hours(yhdhms):
    """
    Given a datetime.datetime value calculate the equivalent
    in hours.
    """
    hours = yhdhms.hour
    minutes = yhdhms.minute
    seconds = yhdhms.second
    hours = hours + minutes/60. + seconds/3600.
    return hours

#def deltatime2hours(dsms):
    #"""
    #Given a datetime.timedelta value calculate the equivalent
    #in hours.
    #"""
    #hours = dsms.days*24. + dsms.seconds/3600.
    #minutes = yhdhms.minute
    #seconds = yhdhms.second
    #hours = hours + minutes/60. + seconds/3600.
    #return hours

def print_deltat(deltat, info=""):
    days = deltat.days
    seconds = deltat.seconds
    hours, remainder = divmod(seconds,3600.)
    minutes, seconds = divmod(remainder, 60.)
    #print(f"{info} {deltat} {hours:02}:{minutes:02}:{seconds:02}")
    if days == 0:
        #return ("%02d:%02d:%02d")%(hours,minutes,seconds)
        return (f"{int(hours):02}:{int(minutes):02d}:{int(seconds):02d}")
    else:
        return ("%0d:%02d:%02d")%(hours+days*24,minutes,seconds)

#def print_deltat_h(deltat):
    #days = deltat.days
    #seconds = deltat.seconds
    #hours = seconds/3600
    #seconds = deltat.seconds - 3600*hours
    #minutes = seconds/60
    #seconds = deltat.seconds - 3600*hours - 60* minutes
    #hours = hours + days*24. + minutes/60. + seconds/3600.
    #print ("%6.3f")%(hours),

