#!/usr/bin/env python

import datetime as dt
#import getopt
import os
import re
import sys
#import string
#import time

## Import global variables into this namespace
from ObsStats_global import *

# Import functions into their own namespace
#import ObsStats_days
import ObsStats_ephem
#import ObsStats_runs
#import ObsStats_sources

# Create some simple aliases
#m_days = ObsStats_days
m_ephem = ObsStats_ephem
#m_runs = ObsStats_runs
#m_sources = ObsStats_sources

def fetch_runs_frm_db():
    """
    From start_date to the end_date query the database for all the run data records.
    runs index is run_id (ie, run number).
    """
    try:
        #import pymysql
        import pymysql
    except ImportError:
        #sys.exit('Failed to import pymysql in read_runs!\n')
        sys.exit('Failed to import pymysql in read_runs!\n')

    try:
        #db_connect=pymysql.connect(host="db.vts",user="readonly",db="VERITAS")
        # Upgrading MacOS to 14.1.1 Sonoma, now need to specify the charset
        # WFH 20231125
        db_connect=pymysql.connect(host="romulus.ucsc.edu",user="readonly",db="VERITAS", charset="utf8")
        #db_connect=pymysql.connect(host="remus.ucsc.edu",user="readonly",db="VERITAS")
        #db_connect=pymysql.connect(host="veritase.sao.arizona.edu",user="readonly",db="VERITAS")
    except:
        sys.exit("Failed to connect to db in read_runs!\n")

    cursor=db_connect.cursor()

    query = 'SELECT run_id, run_type, observing_mode, run_status, ' \
        'db_start_time, db_end_time, ' \
        'data_start_time, data_end_time, duration, ' \
        'weather, config_mask, pointing_mode, ' \
        'trigger_config, trigger_multiplicity, trigger_coincidence, ' \
        'offsetRA, offsetDEC, offset_distance, offset_angle, ' \
        'source_id ' \
        'FROM tblRun_Info WHERE ' \
        'data_start_time > ' + \
        "'" + start_date.strftime('%Y-%m-%d %H:%M') + "'" + \
        ' AND ' + \
        'data_end_time <= ' + \
        "'" + end_date.strftime('%Y-%m-%d %H:%M') + "'"

    cursor.execute(query)
    runs_IndB = cursor.fetchall()

    for run in runs_IndB:
        (run_id,run_type,observing_mode,run_status,
            db_start_time,db_end_time,data_start_time,data_end_time,duration,
            weather,config_mask,pointing_mode,
            trigger_config,trigger_multiplicity,trigger_coincidence,
            offsetRA,offsetDEC,offset_distance,offset_angle,
            source_id) = run
        runs[run_id] = {'run_id':run_id,'run_type':run_type,\
            'observing_mode':observing_mode,\
            'run_status':run_status,\
            'db_start_time':db_start_time,\
            'db_end_time':db_end_time,\
            'data_start_time':data_start_time,\
            'data_end_time':data_end_time,\
            'duration':duration,\
            'weather':weather,\
            'config_mask':config_mask,\
            'pointing_mode':pointing_mode,
            'trigger_config':trigger_config,\
            'trigger_multiplicity':trigger_multiplicity,\
            'trigger_coincidence':trigger_coincidence,\
            'offsetRA':offsetRA,\
            'offsetDEC':offsetDEC,\
            'offset_distance':offset_distance,\
            'offset_angle':offset_angle,\
            'source_id':source_id, \
            ## Initialize some value(s) here which will be set elsewhere
            'data_duration':dt.timedelta(0), \
            'moonlit':'Y/N', \
            }
        ## In the dB "DARK" runs are given run_type 'observing', though they are
        ## not actually source observations.
        ## Hence, change their run_type to 'dark' and their observing_mode to 'calibration'.
        if isDARK.search(runs[run_id]['source_id']):
            runs[run_id]['run_type'] = 'dark'
            runs[run_id]['observing_mode'] = 'calibration'
        ## ... similarly for BSC "sources"
        if isBSC.search(runs[run_id]['source_id']):
            runs[run_id]['run_type'] = 'bsc'
            runs[run_id]['observing_mode'] = 'calibration'
        ## Determine the actual duration of data taking
        data_duration = runs[run_id]['data_end_time'] \
            - runs[run_id]['data_start_time']
        runs[run_id]['data_duration'] = data_duration
        ## Round data_start_time to nearest local midnight (UTC=7h)
        run_date = data_start_time. \
            replace(hour=7,minute=0,second=0,microsecond=0).date()
        runs[run_id]['run_date'] = run_date

    cursor.close()
    db_connect.close()

    ## Create a temporary list containing all source_ids,  includes duplicates
    templist = [runs[key]['source_id'] for key in runs.keys()]
    ## ... then turn it in to a set in which all entries are unique
    templist = set(templist)
    ## ... then back in to a list
    templist = list(templist)
    ## ... before "copying" it to sources_in_runs
    sources_in_runs.extend(templist)

    return

def print_run(run):
    """
    Given one member of "runs", print out the run's information.

    Eg. m_runs.print_run(runs[run_id])
    """
    print (('run_id: %d run_date: %s') % (run['run_id'],run['run_date']))
    source_type = sources[run['source_id']]['source_type']
    print (('source_id: %s  source_type: %s') % (run['source_id'],source_type))
    print (('run_type: %s     observing_mode: %s     run_status: %s') % (run['run_type'], \
         run['observing_mode'],run['run_status']))
    print (('db_start_time:   %s     db_end_time:   %s') % (run['db_start_time'], \
        run['db_end_time']))
    print (('data_start_time: %s     data_end_time: %s') % (run['data_start_time'], \
        run['data_end_time']))
    print (('duration: %s     data_duration: %s    weather: %s') % (run['duration'], \
        run['data_duration'], run['weather']))
    print (('config_mask: %s     pointing_mode: %s') % (run['config_mask'], run['pointing_mode']))
    print (('trigger_config: %s     trigger_multiplicity: %s     trigger_coincidence: %s') % \
        (run['trigger_config'], run['trigger_multiplicity'], run['trigger_coincidence']))
    print (('offsetRA: %.4f     offsetDEC: %.4f     offset_distance: %.4f     offset_angle: %.4f') % \
        (run['offsetRA'], run['offsetDEC'], run['offset_distance'], run['offset_distance']))
    print (('moonlit: %s') % (run['moonlit']))
    print (('start_az: %.2f     start_alt: %.2f     end_az: %.2f     end_alt: %.2f') % \
        (run['start_az'],run['start_alt'],run['end_az'],run['end_alt']))

    return

def print_runs():
    """
    Pass each run (incl all its values) to print_run
    """
    for key in sorted(runs.keys()):
        print_run(runs[key])
    #for run_id, run in runs.items():
        #print_run(run)

    return

def init_run_astro_status():
    """
    Loop over the runs determining whether the moon was up or down
    during the run based on its data_start_time and data_end_time.

    Find the run's source ra and decl and determine the az and alt at
    the start and end of data.
    """
    ## For each run ...
    for run_id, run in runs.items():
        isMoonUp = m_ephem.isMoonUp(run['data_start_time'],run['data_end_time'])
        run['moonlit'] = isMoonUp
        #print "Moon up or not: %s" % (isMoonUp)
        source_id = run['source_id']
        ## If the source is not a source then there is no meaninful RA and decl
        # WFH
        if source_id == 'nosource':
            run['source_id'] = 'NOSOURCE'
            source_id = 'NOSOURCE'
        if source_id == 'NOSOURCE':
            run['start_az'] = 0.0
            run['start_alt'] = 0.0
            run['end_az'] = 0.0
            run['end_alt'] = 0.0
            continue
        ## Sources ra and decl are in radians
        ## ... convert to ephem colon notation, ie, hh:mm:ss.s
        #print source_id
        source_ra_hrs = eph.hours(sources[source_id]['ra'])
        source_decl_deg = eph.degrees(sources[source_id]['decl'])
        source_epoch = sources[source_id]['epoch']
        ## Initialize the ephem source
        source_str = "%s,f,%s,%s,'',%s" % \
            (source_id,source_ra_hrs,source_decl_deg,source_epoch)
        source = eph.readdb(source_str)
        ## Compute the source's az and alt positions at start
        flwo.date = run['data_start_time']
        source.compute(flwo)
        ## ... add zero to force to float
        start_az = math.degrees(source.az + 0.0)
        start_alt = math.degrees(source.alt + 0.0)
        ## ... ditto for the end of run
        flwo.date = run['data_end_time']
        source.compute(flwo)
        end_az = math.degrees(source.az + 0.0)
        end_alt = math.degrees(source.alt + 0.0)
        run['start_az'] = start_az
        run['start_alt'] = start_alt
        run['end_az'] = end_az
        run['end_alt'] = end_alt

    return

def process_runs():
    """
    Loop over the runs accumulating the various stats.

    Eg.:
        config_mask = {}
        observing_mode = {}
        pointing_mode = {}
        run_status = {}
        run_type = {}
        trigger_config = {}
        trigger_multiplicity = []
        weather = {}
    """
    ## For each run ...
    print (f"Number of runs: {len(runs)}")
    for run_id, run in runs.items():
        ## Extract the time related values ...
        data_start = run['data_start_time']
        data_end = run['data_end_time']
        run_date = run['run_date']
        start_of_night = days[run_date]['start_of_night']
        end_of_night = days[run_date]['end_of_night']
        ## If only want dark-time results
        ## ... and the run ends before start_of_night or starts after end_of_night
        if dk_only == True and \
            (data_end < start_of_night or data_start > end_of_night):
            ## ... then skip this run
            continue

        ## Create some shorthand values ...
        cma = run['config_mask']
        moo = run['moonlit']
        omo = run['observing_mode']
        pmo = run['pointing_mode']
        rst = run['run_status']
        rty = run['run_type']
        #print run['source_id'], sources[run['source_id']]['source_type'], source_types[sources[run['source_id']]['source_type']][0]
        scl = source_types[sources[run['source_id']]['source_type']][0]
        sid = run['source_id']
        sty = sources[sid]['source_type']
        tco = run['trigger_config']
        tmu = run['trigger_multiplicity']
        wea = run['weather']
        #print rty, sid, source_types[sources[run['source_id']]['source_type']][0]

        ## Determine the first to last event duration
        data_duration = run['data_duration']
        ## Then accumulate stats ...
        ## ... for this first set do so regardless of run_type
        ## ... pointing_mode
        pointing_mode[pmo]['n_runs'] += 1
        pointing_mode[pmo]['duration'] += data_duration
        ## ... run_type
        run_type[rty]['n_runs'] += 1
        run_type[rty]['duration'] += data_duration
        ## ... trigger_config
        trigger_config[tco]['n_runs'] += 1
        trigger_config[tco]['duration'] += data_duration

        ## For the following only for the observing runs (std, reduced HV, UV filters)...
        if (rty == 'observing' or rty == 'obsFilter' or rty == 'obsLowHV') and sty != 'NOSOURCE':
            ## ... config_mask
            config_mask[cma]['n_runs'] += 1
            config_mask[cma]['duration'] += data_duration
            ## ... observing mode
            observing_mode[omo]['n_runs'] += 1
            observing_mode[omo]['duration'] += data_duration
            ## ... run_duration_dist (round duration to nearest minute)
            index = int((data_duration.seconds+30)/60)
            if index > 31: index = 31
            run_duration_dist[index] += 1
            ## ... run_status
            run_status[rst]['n_runs'] += 1
            run_status[rst]['duration'] += data_duration
            ## ... trigger_multiplicity
            if type(tmu) is not int:
                trigger_multiplicity[0]['n_runs'] += 1
                trigger_multiplicity[0]['duration'] += data_duration
            else:
                trigger_multiplicity[tmu]['n_runs'] += 1
                trigger_multiplicity[tmu]['duration'] += data_duration
            ## ... weather
            weather[wea]['n_runs'] += 1
            weather[wea]['duration'] += data_duration

            ## ... and source, source_type and source_class
            if wea == 'A+' or wea == 'A' or wea == 'A-':
                wea = 'awea'
            elif wea == 'B+' or wea == 'B' or wea == 'B-':
                wea = 'bwea'
            elif wea == 'C+' or wea == 'C' or wea == 'C-':
                wea = 'cwea'
            elif wea == 'D+' or wea == 'D' or wea == 'D-':
                wea = 'dwea'
            else:
                wea = 'dwea'
            ## ... sources
            source_stats[sid]['n_runs'] += 1
            source_stats[sid]['duration'] += data_duration
            if rty == 'obsLowHV':
                source_stats[sid][wea]['Low_HV'] += data_duration
            elif rty == 'obsFilter':
                source_stats[sid][wea]['UV_Fil'] += data_duration
            else:
                source_stats[sid][wea][run['moonlit']] += data_duration
            ## ... source_types
            source_type_stats[sty]['n_runs'] += 1
            source_type_stats[sty]['duration'] += data_duration
            if rty == 'obsLowHV':
                source_type_stats[sty][wea]['Low_HV'] += data_duration
            elif rty == 'obsFilter':
                source_type_stats[sty][wea]['UV_Fil'] += data_duration
            else:
                source_type_stats[sty][wea][run['moonlit']] += data_duration
            ## ... source_classes
            source_class_stats[scl]['n_runs'] += 1
            source_class_stats[scl]['duration'] += data_duration
            if rty == 'obsLowHV':
                source_class_stats[scl][wea]['Low_HV'] += data_duration
            elif rty == 'obsFilter':
                source_class_stats[scl][wea]['UV_Fil'] += data_duration
            else:
                source_class_stats[scl][wea][moo] += data_duration

    return
