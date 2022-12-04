#!/usr/bin/env python

#import datetime as dt
#import getopt
import os
import pickle
import re
import sys
#import string

## Import global variables into this namespace
from ObsStats_global import *

## Import functions into their own namespace
#import ObsStats_days
#import ObsStats_ephem
#import ObsStats_runs
#import ObsStats_sources
#import ObsStats_stats

## Create some simple aliases
#m_days = ObsStats_days
#m_ephem = ObsStats_ephem
#m_runs = ObsStats_runs
#m_sources = ObsStats_sources
#m_stats = ObsStats_stats

def load_stats(fnm='stats.pckl'):
    """
    Read in (load) the pickled stats data from file 'fnm'
    """
    PCKLFILEIN = open(fnm,'rb')
    stats = pickle.load(PCKLFILEIN)
    PCKLFILEIN.close()

    sources.update(stats[0])
    source_stats.update(stats[1])
    source_type_stats.update(stats[2])
    source_class_stats.update(stats[3])
    runs.update(stats[4])
    sources_in_runs.extend(stats[5])
    run_duration_dist.extend(stats[6])
    days.update(stats[7])
    observing_mode.update(stats[8])
    pointing_mode.update(stats[9])
    run_status.update(stats[10])
    run_type.update(stats[11])
    trigger_config.update(stats[12])
    weather.update(stats[13])
    config_mask.update(stats[14])
    trigger_multiplicity.extend(stats[15])

    return

def dump_stats(fnm='stats.pckl'):
    """
    Write out (dump) the pickled stats data from file 'fnm'
    """
    PCKLFILEOUT = open(fnm,'wb')
    stats = (
        sources,
        source_stats,
        source_type_stats,
        source_class_stats,
        runs,
        sources_in_runs,
        run_duration_dist,
        days,
        observing_mode,
        pointing_mode,
        run_status,
        run_type,
        trigger_config,
        weather,
        config_mask,
        trigger_multiplicity,
        )
    pickle.dump(stats,PCKLFILEOUT)
    PCKLFILEOUT.close()

    return
