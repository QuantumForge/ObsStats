#!/usr/bin/env python
# encoding: utf-8

###### !/usr/bin/python

import datetime as dt
#import getopt
import matplotlib as mpl
## Select the graphics format
#matplotlib.use('SVG')
#matplotlib.use('PDF')
mpl.use('Agg')
mpl.rcParams['legend.fancybox'] = True
import matplotlib.pyplot as plt
import numpy as np

#import os
import re
#import sys
#import string
#import time

## Import global variables into this namespace
from ObsStats.ObsStats_global import *

## Select the graphics format file extension
#fext = '.svg'
#fext = '.pdf'
fext = '.png'

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

def print_stats_fmtA(titles,stats):
    """
    Print stats of the form:

Observing Mode
Mode                    num runs:         total duration (d h:m:s)/(h):
  NONE                         0                 0:00:00 / 0.000
  T1                           0                 0:00:00 / 0.000
  T2                           0                 0:00:00 / 0.000
    """
    title = titles[0]
    colmn_title = titles[1]
    RESFILE.write(('%s') % (title))
    RESFILE.write(('%-25s %s         %s') % (colmn_title,'num runs:','total duration (d h:m:s)/(h):'))

    if isinstance(stats,dict):
        index = sorted(stats.keys(),key=str.lower)
    elif isinstance(stats,list):
        index = range(len(stats))
    else:
        print (("\n** %s neither a dict or a list \n") % (title))
        print (stats)
        return

    n_runs = 0
    duration = 0
    for i in index:
        RESFILE.write(('  %-21s   %6d                 %s / %.3f\n') % \
            (i,stats[i]['n_runs'], \
            stats[i]['duration'], \
            duration2hours(stats[i]['duration'])))
        n_runs += stats[i]['n_runs']
        duration += duration2hours(stats[i]['duration'])
    RESFILE.write(('  Total                   %6d                       %.3f\n') % \
        (n_runs, duration))

    CSVFILE.write(('%s\n') % (title))
    CSVFILE.write(('%s,%s,%s') % (colmn_title,'num runs:','total duration (d h:m:s)/(h):\n'))
    for i in index:
        CSVFILE.write(('%s,%d,%.3f\n') % \
            (i,stats[i]['n_runs'], \
            duration2hours(stats[i]['duration'])))
    CSVFILE.write('\n')
    CSVFILE.flush()

    return


def print_stats_fmtB(titles,stats):
    """
    Print stats of the form:

Observing Mode
Mode                    num runs:            total duration (h)       frac(%):
  NONE                         0                 0.000                   0.0
  T1                           0                 0.000                   1.1
  T2                           0                 0.000                  99.9
    """
    title = titles[0]
    colmn_title = titles[1]
    RESFILE.write(('%s\n') % (title))
    RESFILE.write(('%-25s %s     %s     %s\n') % \
        (colmn_title,'num runs:','total duration (h):','frac (%):'))

    if isinstance(stats,dict):
        index = sorted(stats.keys(),key=str.lower)
    elif isinstance(stats,list):
        index = range(len(stats))
    else:
        print (("\n** %s neither a dict or a list \n") % (title))
        print (stats)
        return

    n_runs = 0
    total_duration = 0
    for i in index:
        n_runs += stats[i]['n_runs']
        duration_hrs = duration2hours(stats[i]['duration'])
        total_duration += duration_hrs

    if total_duration > 0:
        if isinstance(index[0],int):
            for i in index:
                duration_hrs = duration2hours(stats[i]['duration'])
                RESFILE.write(('  %-21s   %6d            %8.3f          %8.1f\n') % \
                    (i,stats[i]['n_runs'],duration_hrs,100.*duration_hrs/total_duration))
        else:
            for i in index:
                duration_hrs = duration2hours(stats[i]['duration'])
                RESFILE.write(('  %-21s   %6d            %8.3f          %8.1f\n') % \
                    (i[0:20],stats[i]['n_runs'],duration_hrs,100.*duration_hrs/total_duration))
        RESFILE.write(('  Total                   %6d            %8.3f\n') % \
            (n_runs, total_duration))
    else:
        RESFILE.write('  Total duration was zero.\n')


    CSVFILE.write(('%s\n') % (title))
    CSVFILE.write(('%s,%s,%s') % (colmn_title,'num runs:','total duration (h):\n'))
    for i in index:
        duration_hrs = duration2hours(stats[i]['duration'])
        CSVFILE.write(('%s,%d,%.3f\n') % \
            (i,stats[i]['n_runs'],duration_hrs))
    CSVFILE.write('\n')
    CSVFILE.flush()

    return


def print_stats_fmtC(titles,stats):
    """
    Print stats of the form:

Source Types
Type:                          total duration (Moon/Dark/Low_HV/UV_Fil):
                               A                 B                   C                  D
  AGN                   0.0/0.0/0.0/0.0    0.0/0.0/0.0/0.0    0.0/0.0/0.0/0.0    0.0/0.0/0.0/0.0
  AMHer                 0.0/0.0/0.0/0.0    0.0/0.0/0.0/0.0    0.0/0.0/0.0/0.0    0.0/0.0/0.0/0.0
  BLLac                 1.0/24.8/0.0/0.0   0.0/3.2/0.0/0.0    0.0/6.3/0.0/0.0    0.0/0.0/0.0/0.0
  ClG                   0.0/0.0/0.0/0.0    0.0/0.0/0.0/0.0    0.0/0.0/0.0/0.0    0.0/0.0/0.0/0.0
    """

    darkSky_total = {'awea':0, 'bwea':0, 'cwea':0, 'dwea':0, 'allwea':0}
    moonLit_total = {'awea':0, 'bwea':0, 'cwea':0, 'dwea':0, 'allwea':0}
    Low_HV_total =  {'awea':0, 'bwea':0, 'cwea':0, 'dwea':0, 'allwea':0}
    UV_Fil_total =  {'awea':0, 'bwea':0, 'cwea':0, 'dwea':0, 'allwea':0}

    title = titles[0]
    colmn_title = titles[1]
    RESFILE.write(('%s\n') % (title))
    RESFILE.write(('%-28s        %s\n') % (colmn_title,'total duration [Moon,Dark,Low_HV,UV_Fil]:'))
    RESFILE.write("                                      A                         B                         C                         D\n")
    for key in sorted(stats.keys(),key=str.lower):
        #if source_stats[key]['n_runs'] > 0 and sources[key]['source_type'] != 'NOSOURCE':
        RESFILE.write(('"%-20s" [%4.1f,%5.1f,%5.1f,%5.1f ]  [%4.1f,%5.1f,%5.1f,%5.1f ]  [%4.1f,%5.1f,%5.1f,%5.1f ]  [%4.1f,%5.1f,%5.1f,%5.1f ]\n') % \
            (key[0:20], \
            duration2hours(stats[key]['awea']['Y']), \
            duration2hours(stats[key]['awea']['N']), \
            duration2hours(stats[key]['awea']['Low_HV']), \
            duration2hours(stats[key]['awea']['UV_Fil']), \
            duration2hours(stats[key]['bwea']['Y']), \
            duration2hours(stats[key]['bwea']['N']), \
            duration2hours(stats[key]['bwea']['Low_HV']), \
            duration2hours(stats[key]['bwea']['UV_Fil']), \
            duration2hours(stats[key]['cwea']['Y']), \
            duration2hours(stats[key]['cwea']['N']), \
            duration2hours(stats[key]['cwea']['Low_HV']), \
            duration2hours(stats[key]['cwea']['UV_Fil']), \
            duration2hours(stats[key]['dwea']['Y']), \
            duration2hours(stats[key]['dwea']['N']), \
            duration2hours(stats[key]['dwea']['Low_HV']), \
            duration2hours(stats[key]['dwea']['UV_Fil']) \
            ))
        darkSky_total['awea'] +=  duration2hours(stats[key]['awea']['N'])
        darkSky_total['bwea'] +=  duration2hours(stats[key]['bwea']['N'])
        darkSky_total['cwea'] +=  duration2hours(stats[key]['cwea']['N'])
        darkSky_total['dwea'] +=  duration2hours(stats[key]['dwea']['N'])
        darkSky_total['allwea'] += duration2hours(stats[key]['awea']['N']) \
            + duration2hours(stats[key]['bwea']['N']) \
            + duration2hours(stats[key]['cwea']['N']) \
            + duration2hours(stats[key]['dwea']['N'])

        moonLit_total['awea'] +=  duration2hours(stats[key]['awea']['Y'])
        moonLit_total['bwea'] +=  duration2hours(stats[key]['bwea']['Y'])
        moonLit_total['cwea'] +=  duration2hours(stats[key]['cwea']['Y'])
        moonLit_total['dwea'] +=  duration2hours(stats[key]['dwea']['Y'])
        moonLit_total['allwea'] += duration2hours(stats[key]['awea']['Y']) \
            + duration2hours(stats[key]['bwea']['Y']) \
            + duration2hours(stats[key]['cwea']['Y']) \
            + duration2hours(stats[key]['dwea']['Y'])

        Low_HV_total['awea'] +=  duration2hours(stats[key]['awea']['Low_HV'])
        Low_HV_total['bwea'] +=  duration2hours(stats[key]['bwea']['Low_HV'])
        Low_HV_total['cwea'] +=  duration2hours(stats[key]['cwea']['Low_HV'])
        Low_HV_total['dwea'] +=  duration2hours(stats[key]['dwea']['Low_HV'])
        Low_HV_total['allwea'] += duration2hours(stats[key]['awea']['Low_HV']) \
            + duration2hours(stats[key]['bwea']['Low_HV']) \
            + duration2hours(stats[key]['cwea']['Low_HV']) \
            + duration2hours(stats[key]['dwea']['Low_HV'])

        UV_Fil_total['awea'] +=  duration2hours(stats[key]['awea']['UV_Fil'])
        UV_Fil_total['bwea'] +=  duration2hours(stats[key]['bwea']['UV_Fil'])
        UV_Fil_total['cwea'] +=  duration2hours(stats[key]['cwea']['UV_Fil'])
        UV_Fil_total['dwea'] +=  duration2hours(stats[key]['dwea']['UV_Fil'])
        UV_Fil_total['allwea'] += duration2hours(stats[key]['awea']['UV_Fil']) \
            + duration2hours(stats[key]['bwea']['UV_Fil']) \
            + duration2hours(stats[key]['cwea']['UV_Fil']) \
            + duration2hours(stats[key]['dwea']['UV_Fil'])


    RESFILE.write(('  Total:                  [%4.1f,%5.1f,%5.1f,%5.1f]  [%4.1f,%5.1f,%5.1f,%5.1f]  [%4.1f,%5.1f,%5.1f,%5.1f]  [%4.1f,%5.1f,%5.1f,%5.1f]\n') % \
        (
        moonLit_total['awea'], darkSky_total['awea'], Low_HV_total['awea'], UV_Fil_total['awea'], \
        moonLit_total['bwea'], darkSky_total['bwea'], Low_HV_total['bwea'], UV_Fil_total['bwea'], \
        moonLit_total['cwea'], darkSky_total['cwea'], Low_HV_total['cwea'], UV_Fil_total['cwea'], \
        moonLit_total['dwea'], darkSky_total['dwea'], Low_HV_total['dwea'], UV_Fil_total['dwea']
        ))
    RESFILE.write(('  Total All Wea. [Moon,Dark,Low_HV,UV_Fil]:  [%5.1f,%5.1f,%5.1f,%5.1f]\n') % \
        (moonLit_total['allwea'], darkSky_total['allwea'], Low_HV_total['allwea'], UV_Fil_total['allwea']))

    CSVFILE.write(('%s\n') % (title))
    CSVFILE.write(('%s,%s') % (colmn_title,'total duration [Moon,Dark,Low_HV,UV_Fil]:\n'))
    for key in sorted(stats.keys(),key=str.lower):
        CSVFILE.write(('%s,%4.1f,%5.1f,%5.1f,%5.1f,%4.1f,%5.1f,%5.1f,%5.1f,%4.1f,%5.1f,%5.1f,%5.1f,%4.1f,%5.1f%5.1f,%5.1f\n') % \
            (key, \
            duration2hours(stats[key]['awea']['Y']), \
            duration2hours(stats[key]['awea']['N']), \
            duration2hours(stats[key]['awea']['Low_HV']), \
            duration2hours(stats[key]['awea']['UV_Fil']), \
            duration2hours(stats[key]['bwea']['Y']), \
            duration2hours(stats[key]['bwea']['N']), \
            duration2hours(stats[key]['bwea']['Low_HV']), \
            duration2hours(stats[key]['bwea']['UV_Fil']), \
            duration2hours(stats[key]['cwea']['Y']), \
            duration2hours(stats[key]['cwea']['N']), \
            duration2hours(stats[key]['cwea']['Low_HV']), \
            duration2hours(stats[key]['cwea']['UV_Fil']), \
            duration2hours(stats[key]['dwea']['Y']), \
            duration2hours(stats[key]['dwea']['N']), \
            duration2hours(stats[key]['dwea']['Low_HV']), \
            duration2hours(stats[key]['dwea']['UV_Fil']) \
            ))
    CSVFILE.write(('%s,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f\n') % \
        ('Total', \
        moonLit_total['awea'], darkSky_total['awea'], Low_HV_total['awea'], UV_Fil_total['awea'], \
        moonLit_total['bwea'], darkSky_total['bwea'], Low_HV_total['bwea'], UV_Fil_total['bwea'], \
        moonLit_total['cwea'], darkSky_total['cwea'], Low_HV_total['cwea'], UV_Fil_total['cwea'], \
        moonLit_total['dwea'], darkSky_total['dwea'], Low_HV_total['dwea'], UV_Fil_total['dwea'] \
        ))

    CSVFILE.write('\n')
    CSVFILE.flush()

    return

def plot_stats_oneBar(fig,sp,titles,stats,stats_keys=None):
    """
    Plot a simple bar chart.

    NB left edge == 0, right=edge is "nbins" ... but see
    below.
    """
    title = titles[0]
    ylabel = titles[1]
    if stats_keys == None:
        xticklabels = sorted(stats.keys(),key=str.lower)
    else:
        xticklabels = stats_keys
    yvals = []
    for key in xticklabels:
        yvals.append(duration2hours(stats[key]['duration']))
    nbins = len(xticklabels)
    step = 1.0
    width = step/2.
    xvals = np.arange(width,nbins+0.5,step)

    ax = fig.add_subplot(sp)
    ## Now plot values
    ax.bar(xvals+width/2.,yvals,width,color='0.45')
    ## To make plots look good, need to increase xlim by 1
    ax.set_xlim(0.,nbins+1)
    ## ... "dress" those with titles, ticks and tick labels
    ax.set_title(title)
    ax.set_xticks(xvals+width)
    ax.set_xticklabels(xticklabels,rotation=90)
    ax.set_ylabel(ylabel)

    plt.figtext(0.15, 0.85, file_tag, size='x-small', ha='left', va='center')

    return

def plot_oneBar(fig,sp,textvals,xvals,yvals):
    """
    Plot a simple bar chart.

    NB left edge == 0, right=edge is "nbins"
    """
    title = textvals[0]
    xticklabels = textvals[1]
    ylabel = textvals[2]
    nbins = len(yvals)
    step = 1.0
    width = step/2.
    ## If values passed then convert to a pylab array
    ## ... else create an array
    if len(xvals) != 0:
        xvals = np.array(xvals)
    else:
        xvals = np.arange(width,nbins+0.5,step)
    ax = fig.add_subplot(sp)
    ## Now plot values
    ax.bar(xvals+width/2.,yvals,width,color='0.45')
    ## To make plots look good need to increase xlim by a bit
    #ax.set_xlim(0.,nbins+1)
    ax.set_xlim(0.,nbins+0.5)
    ## ... "dress" those with titles, ticks and tick labels
    ax.set_title(title)
    ax.set_xticks(xvals+width)
    ax.set_xticklabels(xticklabels,rotation=90)
    ax.set_ylabel(ylabel)

    plt.figtext(0.15, 0.85, file_tag, size='x-small', ha='left', va='center')

    return

def plot_stats_twoBar(fig,sp,titles,stats,stats_keys=None):
    """
    Plot a pair of "interleaved" stats bar charts.
    """
    ## Extract the titles/labels ...
    title = titles[0]
    y1label = titles[1]
    y2label = titles[2]
    if stats_keys == None:
        xticklabels = sorted(stats.keys(),key=str.lower)
    else:
        xticklabels = sorted(stats_keys,key=str.lower)
    ## ... and the data values
    y1vals = []
    y2vals = []
    for key in xticklabels:
        y1vals.append(stats[key]['n_runs'])
        y2vals.append(duration2hours((stats[key]['duration'])))
    nbins = len(xticklabels)
    step = 1.0
    width = step/2.
    xvals = np.arange(width,nbins+0.5,step)

    ax1 = fig.add_subplot(sp)
    ## Now plot 1st set of data values
    ax1.bar(xvals+width/2,y1vals,width/2,color='0.45')
    ## ... create second axes
    ax2 = ax1.twinx()
    ## ... plot 2nd sed
    ax2.bar(xvals+width,y2vals,width/2,color='0.65')
    ## ... "dress" those with titles, ticks and tick labels
    ## ... but turn off xtick labels
    ax2.set_xticklabels('',visible=False)
    ax2.set_ylabel(y2label)
    ax2.yaxis.tick_right()

    ## To make plots look good need to increase xlim by 1
    ax1.set_xlim(0.,nbins+1)
    ## ... now "dress" with titles, ticks and tick labels
    ## ... from first plot
    ax1.set_title(title)
    ax1.set_xticks(xvals+width)
    ax1.set_xticklabels(xticklabels,rotation=90)
    ax1.set_ylabel(y1label)

    plt.figtext(0.15, 0.85, file_tag, size='x-small', ha='left', va='center')

    return

def plot_twoBar(fig,sp,textvals,xvals,y1vals,y2vals):
    """
    Plot a pair of "interleaved" bar charts.
    """
    title = textvals[0]
    xticklabels = textvals[1]
    y1label = textvals[2]
    y2label = textvals[3]
    nbins = len(y1vals)
    step = 1.0
    width = step/2.
    ## If values passed then convert to a pylab array
    ## ... else create an array
    if len(xvals) != 0:
        xvals = np.array(xvals)
    else:
        xvals = np.arange(width,nbins+0.5,step)
    ax1 = fig.add_subplot(sp)
    ## Now plot 1st set of data values
    ax1.bar(xvals+width/2,y1vals,width/2,color='0.45')
    ## ... create second axes
    ax2 = ax1.twinx()
    ## ... plot 2nd sed
    ax2.bar(xvals+width,y2vals,width/2,color='0.65')
    ## ... "dress" those with titles, ticks and tick labels
    ## ... but turn off xtick labels
    ax2.set_xticklabels('',visible=False)
    ax2.set_ylabel(y2label)
    ax2.yaxis.tick_right()

    ## To make plots look good need to increase xlim by 1
    #ax1.set_xlim(0.,nbins+1)
    ax1.set_xlim(0.,nbins+0.5)
    ## ... now "dress" with titles, ticks and tick labels
    ## ... from first plot
    ax1.set_title(title)
    ax1.set_xticks(xvals+width)
    ax1.set_xticklabels(xticklabels,rotation=90)
    ax1.set_ylabel(y1label)

    plt.figtext(0.15, 0.85, file_tag, size='x-small', ha='left', va='center')

    return

def plot_stats_stackedWeatherBar(fig,sp,titles,tmp_stats):
    """
    Plot the duration under different weather conditinons
    for a (variable) set of sources, source_types or source_classes
    """

    title = titles[0]
    ylabel = titles[1]
    xticklabels = []
    yAvals = []
    yBvals = []
    yCvals = []
    yDvals = []
    keys = sorted(tmp_stats.keys(),key=str.lower)

    for key in keys:
    #for key in sorted(tmp_stats.keys(),key=str.lower):
        xticklabels.append(key)
        yAvals.append(tmp_stats[key][0])
        yBvals.append(tmp_stats[key][1])
        yCvals.append(tmp_stats[key][2])
        yDvals.append(tmp_stats[key][3])

    nkeys = len(keys)
    yAvals = np.array(yAvals)
    yBvals = np.array(yBvals)
    yCvals = np.array(yCvals)
    yDvals = np.array(yDvals)
    nbins = len(tmp_stats)
    step = 1.0
    width = step/2.
    xvals = np.arange(width,nbins+0.5,step)

    ax = fig.add_subplot(sp)
    pA = ax.bar(xvals+width/2.,yAvals,width,color='0.2')
    pB = ax.bar(xvals+width/2.,yBvals,width, \
        bottom=yAvals,color='0.4')
    pC = ax.bar(xvals+width/2.,yCvals,width, \
        bottom=yAvals+yBvals,color='0.6')
    pD = ax.bar(xvals+width/2.,yDvals,width, \
        bottom=yAvals+yBvals+yCvals,color='0.8')

    ## To make plots look good need to increase xlim by 1
    ax.set_xlim(0.,nbins+1)
    ax.set_title(title)
    ax.set_xticks(xvals+width)
    if nkeys > 33:
        ax.set_xticklabels(xticklabels,size='xx-small',rotation=90)
    else:
        ax.set_xticklabels(xticklabels,rotation=90)
    ax.set_ylabel(ylabel)
    ax.legend((pA[0],pB[0],pC[0],pD[0]), ('A','B','C','D'), \
        shadow=True)

    plt.figtext(0.15, 0.85, file_tag, size='x-small', ha='left', va='center')

    return

def plot_stats_Pie(fig,sp,titles,stats,stats_keys=None,min_frac=0):
    """
    Plot a simple pie chart.

    If a stats value falls below min_frac then lump its contribution in to
    'Other'.
    """
    title = titles[0]
    if stats_keys == None:
        slicelabels = sorted(stats.keys(),key=str.lower)
    else:
        slicelabels = stats_keys
    ## Define the parameters for call to plt.pie
    colors = []
    explode = []
    fracs = []
    labels = []

    ## Now find total of stats value
    total_duration =  0
    for key, stat in stats.items():
        total_duration += stat[4]
    min_duration = total_duration*min_frac
    other_duration = 0
    ## ... then loop over stats again, testing the values again min,
    ## ... if they exceed min then append to fracs, labels, etc, if not,
    ## ... collect in "other"
    for key, stat in stats.items():
        duration = stat[4]
        if duration < min_duration:
            other_duration += duration
        else:
            colors.append('0.80')
            explode.append(0.05)
            if total_duration > 0:
                fracs.append(float(duration)/total_duration)
            else:
                fracs.append(0.0)
            labels.append(key)

    if other_duration > 0:
            colors.append('0.80')
            explode.append(0.05)
            fracs.append(float(other_duration)/total_duration)
            labels.append('Other')

    #plt.pie(fracs, colors=colors, explode=explode, labels=labels, autopct='%1.1f%%')
# modified this line with normalize = True after receiving this error:
# MatplotlibDeprecationWarning: normalize=None does not normalize if the sum is
# less than 1 but this behavior is deprecated since 3.3 until two minor
# releases later. After the deprecation period the default value will be
# normalize=True. To prevent normalization pass normalize=False
# 
# I'm not sure what behavior is desired
# WFH 24 March 2021
    plt.pie(fracs, colors=colors, explode=explode, labels=labels,
        autopct='%1.1f%%', normalize=True)
    plt.title(title+'\n'+file_tag)
#    plt.figtext(0.39, 0.9, file_tag, size='x-small', ha='left', va='center')

    return

##
## ... begin stat specific functions
##

def print_config_mask_dist():
    """
    NB: Config_mask requires a dedicated print statement since we order the print out
    in a non-sorted fashion.

    config_mask_map = ['NONE', 'T1', 'T2', 'T1T2', 'T3', 'T1T3', \
    'T2T3', 'T1T2T3', 'T4', 'T1T4', 'T2T4', 'T1T2T4', \
    'T3T4', 'T1T3T4', 'T2T3T4', 'T1T2T3T4']
    """
    RESFILE.write("Configuration Mask (obs only)\n")
    RESFILE.write('Config_mask               num runs:     total duration (h):     frac (%):\n')

    n_runs = 0
    total_duration = 0
    for i in range(0,16):
        duration_hrs = duration2hours(config_mask[i]['duration'])
        n_runs += config_mask[i]['n_runs']
        total_duration += duration_hrs

    if total_duration > 0:
        for i in range(0,16):
            duration_hrs = duration2hours(config_mask[i]['duration'])
            RESFILE.write(('  %-12s            %6d            %8.3f          %8.1f\n') % \
                (config_mask_map[i],config_mask[i]['n_runs'],duration_hrs,100.*duration_hrs/total_duration))
        RESFILE.write(('  Total                   %6d            %8.3f\n') % \
            (n_runs, total_duration))
        RESFILE.write('\n')
        RESFILE.write('\n')
    else:
        RESFILE.write('  Total duration was zero.\n')

    CSVFILE.write('Configuration_Mask (obs only)\n')
    CSVFILE.write('Config_mask,num runs,duration(h)\n')
    for i in range(0,16):
        duration_hrs = duration2hours(config_mask[i]['duration'])
        CSVFILE.write(('%s,%d,%.3f\n') % \
            (config_mask_map[i],config_mask[i]['n_runs'],duration_hrs))
    CSVFILE.write('\n')
    CSVFILE.flush()

    return

def print_observing_mode_dist():
    """
    Print:
        observing_mode[mode] = {number of on runs:int,
        duration:datetime.timedelta}
    """
    print_stats_fmtB(['Observing Mode','Mode'], observing_mode)
    RESFILE.write('\n')
    RESFILE.write('\n')

    fig = plt.figure()
    fig.subplots_adjust(right=0.85)
    fig.subplots_adjust(bottom=0.25)
    sp = 111
    plot_stats_twoBar(fig,sp, \
        ['Observing Mode','N Runs','Duration (h)'], \
        observing_mode)
    fig.savefig(f'{output_dir}/ObservingMode_{file_tag}{fext}')

    return fig

def print_RA_dist():
    """
    Print and plot the distribution of the number of sources and total exposure
    as a function of RA.
    """
    RESFILE.write('RA distribution (obs only)\n')
    RESFILE.write('RA (hours)  num sources:  total duration [Moon,Dark,Low_HV,UV_Fil]:\n')
    RESFILE.write("                                          A                         B                         C                         D\n")

    #xticklabels = ['00','01','02','03','04','05','06','07','08','09',
    #    '10','11','12','13','14','15','16','17','18','19',
    #    '20','21','22','23','24',]
    xticklabels = ['00','01','02','03','04','05','06','07','08','09',
        '10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23']

    RA_sourceNumber_dist = [0]*24
    RA_exposure_dist = [0.0]*24
    total_exposure = 0

    for hr in range(24):
        total_exposure += duration2hours(RA_stats[hr]['duration'])
        RA_sourceNumber_dist[hr] = RA_stats[hr]['n_sources']
        RA_exposure_dist[hr] = duration2hours(RA_stats[hr]['duration'])
        RESFILE.write(('  %-11s %3d         %4.1f [%4.1f,%5.1f,%5.1f,%5.1f]  [%4.1f,%5.1f,%5.1f,%5.1f]  [%4.1f.%5.1f,%5.1f,%5.1f]  [%4.1f,%5.1f,%5.1f,%5.1f]\n') % \
                (xticklabels[hr],RA_stats[hr]['n_sources'],duration2hours(RA_stats[hr]['duration']),\
                 duration2hours(RA_stats[hr]['awea']['Y']), \
                 duration2hours(RA_stats[hr]['awea']['N']), \
                 duration2hours(RA_stats[hr]['awea']['Low_HV']), \
                 duration2hours(RA_stats[hr]['awea']['UV_Fil']), \
                 duration2hours(RA_stats[hr]['bwea']['Y']), \
                 duration2hours(RA_stats[hr]['bwea']['N']), \
                 duration2hours(RA_stats[hr]['bwea']['Low_HV']), \
                 duration2hours(RA_stats[hr]['bwea']['UV_Fil']), \
                 duration2hours(RA_stats[hr]['cwea']['Y']), \
                 duration2hours(RA_stats[hr]['cwea']['N']), \
                 duration2hours(RA_stats[hr]['cwea']['Low_HV']), \
                 duration2hours(RA_stats[hr]['cwea']['UV_Fil']), \
                 duration2hours(RA_stats[hr]['dwea']['Y']), \
                 duration2hours(RA_stats[hr]['dwea']['N']), \
                 duration2hours(RA_stats[hr]['dwea']['Low_HV']), \
                 duration2hours(RA_stats[hr]['dwea']['UV_Fil']) \
                 ))
    RESFILE.write(('  Total exposure:  %8.3f\n') % (total_exposure))
    RESFILE.write('\n')
    RESFILE.write('\n')

    CSVFILE.write('RA distribution (obs only),num sources,duration(h)\n')
    for hr in range(24):
        CSVFILE.write(('%s,%d,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,\n') %\
                      (xticklabels[hr],RA_stats[hr]['n_sources'],duration2hours(RA_stats[hr]['duration']),\
                       duration2hours(RA_stats[hr]['awea']['Y']), \
                       duration2hours(RA_stats[hr]['awea']['N']), \
                       duration2hours(RA_stats[hr]['awea']['Low_HV']), \
                       duration2hours(RA_stats[hr]['awea']['UV_Fil']), \
                       duration2hours(RA_stats[hr]['bwea']['Y']), \
                       duration2hours(RA_stats[hr]['bwea']['N']), \
                       duration2hours(RA_stats[hr]['bwea']['Low_HV']), \
                       duration2hours(RA_stats[hr]['bwea']['UV_Fil']), \
                       duration2hours(RA_stats[hr]['cwea']['Y']), \
                       duration2hours(RA_stats[hr]['cwea']['N']), \
                       duration2hours(RA_stats[hr]['cwea']['Low_HV']), \
                       duration2hours(RA_stats[hr]['cwea']['UV_Fil']), \
                       duration2hours(RA_stats[hr]['dwea']['Y']), \
                       duration2hours(RA_stats[hr]['dwea']['N']), \
                       duration2hours(RA_stats[hr]['dwea']['Low_HV']), \
                       duration2hours(RA_stats[hr]['dwea']['UV_Fil']) \
                       ))
    CSVFILE.write('\n')
    CSVFILE.flush()

    textvals = ['',[],'','']
    textvals[0] = 'RA Distributions'
    textvals[1] = xticklabels
    textvals[2] = 'N Sources'
    textvals[3] = 'Exposure (h)'

    fig = plt.figure()
    #fig.subplots_adjust(wspace=0.75)
    #fig.subplots_adjust(hspace=0.5)
    fig.subplots_adjust(right=0.9)
    fig.subplots_adjust(bottom=0.25)
    sp = 111
    plot_twoBar(fig,sp,textvals,range(24),RA_sourceNumber_dist,RA_exposure_dist)
    #plot_stats_oneBar(fig,sp, \
        #('Weather (obs only)','Duration (h)'), \
        #weather,stats_keys=weather_keys)
    fig.savefig(f'{output_dir}/RA_dists_{file_tag}{ext}')

    return fig

def print_run_duration_dist():
    RESFILE.write('Run Durations (obs only)\n')
    RESFILE.write('mins:                     num runs:\n')
    for min in range(32):
        RESFILE.write(('%4d                       %5d\n') % \
            (min,run_duration_dist[min]))
    RESFILE.write('\n')
    RESFILE.write('\n')

    CSVFILE.write('Run Duration (obs only),mins,num runs\n')
    for min in range(32):
        CSVFILE.write(('%d,%d\n') % (min,run_duration_dist[min]))
    CSVFILE.write('\n')
    CSVFILE.flush()

    fig = plt.figure()
    fig.subplots_adjust(right=0.85)
    fig.subplots_adjust(bottom=0.25)
    sp = 111
    textvals = ['',[],'']
    textvals[0] = 'Run Duration (obs only)'
    for min in range(32):
        textvals[1].append(str(min))
    textvals[2] = 'N Runs'
    plot_oneBar(fig,sp,textvals,range(32),run_duration_dist)
    fig.savefig(f'{output_dir}/RunDurations_{file_tag}{fext}')

    return fig

def print_run_status_dist():
    print_stats_fmtB(['Run Status (obs only)','Status'], run_status)
    RESFILE.write('\n')
    RESFILE.write('\n')

    return

def print_run_type_dist():
    print_stats_fmtB(['Run Type','Type'], run_type)
    RESFILE.write('\n')
    RESFILE.write('\n')

    fig = plt.figure()
    fig.subplots_adjust(right=0.85)
    fig.subplots_adjust(bottom=0.25)
    sp = 111
    plot_stats_twoBar(fig,sp, \
        ['Run Type','N Runs','Duration (h)'], \
        run_type)
    fig.savefig(f'{output_dir}/RunType_{file_tag}{fext}')

    return fig

def print_source_stats_dist():
    if len(source_stats) <= 1:
        print ("\n**No Sources observed**\n")
        return

    print_stats_fmtB(['Sources','Name'], source_stats)
    RESFILE.write('\n')

    print_stats_fmtC(['Sources','Name'], source_stats)
    RESFILE.write('\n')

    RESFILE.write("Sources\n")
    RESFILE.write("Name:                       Type:         Class:\n")
    for key in sorted(source_stats.keys(),key=str.lower):
        #if source_stats[key]['n_runs'] > 0 and sources[key]['source_type'] != 'NOSOURCE':
        source_type = sources[key]['source_type']
        source_class = source_types[source_type][0]
        source_class_desc = source_types[source_type][1][0:20]
        source_class = source_class+'-'+source_class_desc
        RESFILE.write(('  %-20s      %-8s      %-s\n') % \
            (key[0:20], source_type, source_class))
    RESFILE.write('\n')
    RESFILE.write('\n')

    ## Create some temporary variables ...
    ## ... SkySource and NOSOURCE are used to sum up all of the respective sources
    ## ... of those types.  See below where they may be deleted if none found.
    tmp_stats = {}
    tmp_stats['NOSOURCE'] = [0,0,0,0]
    ifNoNOSOURCE = True
    tmp_stats['SkySurvey'] = [0,0,0,0]
    ifNoSkySurvey = True
    for source_id, stat in source_stats.items():
        if sources[source_id]['source_type'] == 'NOSOURCE':
            #isBSC.search(source_id) or \
            #isCalEng.search(source_id) or \
            #isdarkSky.search(source_id) or \
            #isFAKE.search(source_id) or \
            #isNOSOURCE.search(source_id) or \
            #isSTAR.search(source_id) or \
            #isTEST.search(source_id) or \
            #isZENITH.search(source_id):
            awea = stat['awea']['Y'] + stat['awea']['N']
            bwea = stat['bwea']['Y'] + stat['bwea']['N']
            cwea = stat['cwea']['Y'] + stat['cwea']['N']
            dwea = stat['dwea']['Y'] + stat['dwea']['N']
            tmp_stats['NOSOURCE'][0] += duration2hours(awea)
            tmp_stats['NOSOURCE'][1] += duration2hours(bwea)
            tmp_stats['NOSOURCE'][2] += duration2hours(cwea)
            tmp_stats['NOSOURCE'][3] += duration2hours(dwea)
            ifNoNOSOURCE = False
        elif isSURVEY.search(source_id) or \
            isMilSURVEY.search(source_id) or \
            isCygHS.search(source_id):
            awea = stat['awea']['Y'] + stat['awea']['N']
            bwea = stat['bwea']['Y'] + stat['bwea']['N']
            cwea = stat['cwea']['Y'] + stat['cwea']['N']
            dwea = stat['dwea']['Y'] + stat['dwea']['N']
            tmp_stats['SkySurvey'][0] += duration2hours(awea)
            tmp_stats['SkySurvey'][1] += duration2hours(bwea)
            tmp_stats['SkySurvey'][2] += duration2hours(cwea)
            tmp_stats['SkySurvey'][3] += duration2hours(dwea)
            ifNoSkySurvey = False
        else:
            awea = stat['awea']['Y'] + stat['awea']['N']
            bwea = stat['bwea']['Y'] + stat['bwea']['N']
            cwea = stat['cwea']['Y'] + stat['cwea']['N']
            dwea = stat['dwea']['Y'] + stat['dwea']['N']
            tmp_stats[source_id] = [
                duration2hours(awea),
                duration2hours(bwea),
                duration2hours(cwea),
                duration2hours(dwea),
                ]
    if ifNoSkySurvey: del tmp_stats['SkySurvey']
    if ifNoNOSOURCE: del tmp_stats['NOSOURCE']

    if len(tmp_stats) <= 30:
        fig = plt.figure()
        #fig.subplots_adjust(wspace=0.75)
        #fig.subplots_adjust(hspace=0.5)
        fig.subplots_adjust(right=0.9)
        fig.subplots_adjust(bottom=0.25)
        sp = 111
        plot_stats_stackedWeatherBar(fig,sp, \
            ('Sources','Duration (h)'), \
            tmp_stats)
        fig.savefig(f'{output_dir}/SourceStats_{file_tag}{fext}')

        return fig

    else:
        ## I could do a if < len(tmp_stats)/2 then do first else do second half ...
        ## ... might not be too hard
        auppkeys = []
        zdwnkeys = []
        auppstat = {}
        zdwnstat = {}
        index = sorted(tmp_stats.keys(),key=str.lower)
        for cnt in range(len(tmp_stats)):
            ## first half of sources
            if cnt < len(tmp_stats)/2:
                auppkeys.append(index[cnt])
            else:
                zdwnkeys.append(index[cnt])
        for key in auppkeys:
            auppstat[key] = tmp_stats[key]
        for key in zdwnkeys:
            zdwnstat[key] = tmp_stats[key]
        figaupp = plt.figure()
        #fig.subplots_adjust(wspace=0.75)
        #fig.subplots_adjust(hspace=0.5)
        figaupp.subplots_adjust(right=0.9)
        figaupp.subplots_adjust(bottom=0.25)
        spaupp = 111
        plot_stats_stackedWeatherBar(figaupp,spaupp, \
            ('Sources_A-UP','Duration (h)'), \
            auppstat)
        figaupp.savefig(f'{output_dir}/SourceStats_A-UP_{file_tag}{fext}')
        figzdwn = plt.figure()
        #fig.subplots_adjust(wspace=0.75)
        #fig.subplots_adjust(hspace=0.5)
        figzdwn.subplots_adjust(right=0.9)
        figzdwn.subplots_adjust(bottom=0.25)
        spzdwn = 111
        plot_stats_stackedWeatherBar(figzdwn,spzdwn, \
            ('Sources_Z-DWN','Duration (h)'), \
            zdwnstat)
        figzdwn.savefig(f'{output_dir}/SourceStats_Z-DWN_{file_tag}{fext}')

        #a2lkeys = []
        #m2zkeys = []
        #for key in tmp_stats.keys():
            #if key.upper()[0] < 'M':
                #a2lkeys.append(key)
            #else:
                #m2zkeys.append(key)
        ##a2mkeys = [key for key in source_stats.keys() if key.upper() < 'L']
        ##n2zkeys = [key for key in source_stats.keys() if key.upper() > 'N']
        #a2lstat = {}
        #m2zstat = {}
        #for key in a2lkeys:
        ##if source_stats[key]['n_runs'] > 0:
            #a2lstat[key] = tmp_stats[key]
        #for key in m2zkeys:
        ##if source_stats[key]['n_runs'] > 0:
            #m2zstat[key] = tmp_stats[key]
        #figa2l = plt.figure()
        ##fig.subplots_adjust(wspace=0.75)
        ##fig.subplots_adjust(hspace=0.5)
        #figa2l.subplots_adjust(right=0.9)
        #figa2l.subplots_adjust(bottom=0.25)
        #spa2l = '111'
        #plot_stats_stackedWeatherBar(figa2l,spa2l, \
            #('Sources_A-L','Duration (h)'), \
            #a2lstat)
        #figa2l.savefig(f'{output_dir}/SourceStats_A-L_{file_tag}{fext}')
        #figm2z = plt.figure()
        ##fig.subplots_adjust(wspace=0.75)
        ##fig.subplots_adjust(hspace=0.5)
        #figm2z.subplots_adjust(right=0.9)
        #figm2z.subplots_adjust(bottom=0.25)
        #spm2z = '111'
        #plot_stats_stackedWeatherBar(figm2z,spm2z, \
            #('Sources_M-Z','Duration (h)'), \
            #m2zstat)
        #figm2z.savefig(f'{output_dir}/SourceStats_M-Z_{file_tag}{fext}')

    #return (figa2l, figm2z)
    return (figaupp, figzdwn)

def print_source_class_stats_dist():
    if len(source_stats) <= 1:
        print ("\n**No Sources observed**\n")
        return

    print_stats_fmtB(['Source Class','Class'],source_class_stats)
    RESFILE.write('\n')

    print_stats_fmtC(['Source Class','Class'],source_class_stats)
    RESFILE.write('\n')
    RESFILE.write('\n')

    tmp_stats = {}
    for source_id, stat in source_class_stats.items():
        awea = stat['awea']['Y'] + stat['awea']['N']
        bwea = stat['bwea']['Y'] + stat['bwea']['N']
        cwea = stat['cwea']['Y'] + stat['cwea']['N']
        dwea = stat['dwea']['Y'] + stat['dwea']['N']
        duration = duration2hours(awea+bwea+cwea+dwea)
        tmp_stats[source_id] = [
            duration2hours(awea),
            duration2hours(bwea),
            duration2hours(cwea),
            duration2hours(dwea),
            duration
            ]

    fig1 = plt.figure()
    #fig.subplots_adjust(wspace=0.75)
    #fig.subplots_adjust(hspace=0.5)
    fig1.subplots_adjust(right=0.9)
    fig1.subplots_adjust(bottom=0.25)
    sp = 111
    plot_stats_stackedWeatherBar(fig1,sp, \
        ('Source Classes','Duration (h)'), \
        tmp_stats)
    fig1.savefig(f'{output_dir}/SourceClassStats_{file_tag}{fext}')

    fig2 = plt.figure(figsize=(6,6))
    titles = ['Source Classes']
    plot_stats_Pie(fig2,sp,titles,tmp_stats,stats_keys=None,min_frac=0.02)
    fig2.savefig(f'{output_dir}/SourceClassStatsPie_{file_tag}{fext}')

    return (fig1, fig2)

def print_source_type_stats_dist():
    if len(source_stats) <= 1:
        print ("\n**No Sources observed**\n")
        return

    print_stats_fmtB(['Source Types','Type'], source_type_stats)
    RESFILE.write('\n')

    print_stats_fmtC(['Source Types','Type'], source_type_stats)
    RESFILE.write('\n')
    RESFILE.write('\n')

    tmp_stats = {}
    for source_id, stat in source_type_stats.items():
        awea = stat['awea']['Y'] + stat['awea']['N']
        bwea = stat['bwea']['Y'] + stat['bwea']['N']
        cwea = stat['cwea']['Y'] + stat['cwea']['N']
        dwea = stat['dwea']['Y'] + stat['dwea']['N']
        duration = duration2hours(awea+bwea+cwea+dwea)
        tmp_stats[source_id] = [
            duration2hours(awea),
            duration2hours(bwea),
            duration2hours(cwea),
            duration2hours(dwea),
            duration
            ]

    fig1 = plt.figure()
    #fig.subplots_adjust(wspace=0.75)
    #fig.subplots_adjust(hspace=0.5)
    fig1.subplots_adjust(right=0.9)
    fig1.subplots_adjust(bottom=0.25)
    sp = 111
    plot_stats_stackedWeatherBar(fig1,sp, \
        ('Source Types','Duration (h)'), \
        tmp_stats)
    fig1.savefig(f'{output_dir}/SourceTypeStats_{file_tag}{fext}')

    fig2 = plt.figure(figsize=(6,6))
    titles = ['Source Types']
    plot_stats_Pie(fig2,sp,titles,tmp_stats,stats_keys=None,min_frac=0.02)
    fig2.savefig(f'{output_dir}/SourceTypeStatsPie_{file_tag}{fext}')

    return (fig1, fig2)

def print_trigger_config_dist():
    print_stats_fmtB(['Trigger Configuration','Configuration'], trigger_config)
    RESFILE.write('\n')
    RESFILE.write('\n')

    return

def print_trigger_multiplicity_dist():
    print_stats_fmtB(['Trigger Multiplicity (obs only)','Multiplicity'], trigger_multiplicity)
    RESFILE.write('\n')
    RESFILE.write('\n')

    return

def print_weather_dist():
    """
    NB: Weather requires a dedicated print statement since we order the print out
    in a non-sorted fashion.
    """
    RESFILE.write('Weather (obs only)\n')
    RESFILE.write('Weather                   num runs:     total duration (h):     frac (%):\n')

    n_runs = 0
    total_duration = 0
    for key in weather_keys:
        n_runs += weather[key]['n_runs']
        duration_hrs = duration2hours(weather[key]['duration'])
        total_duration += duration_hrs

    if total_duration > 0:
        for key in weather_keys:
            duration_hrs = duration2hours(weather[key]['duration'])
            RESFILE.write(('  %-21s   %6d            %8.3f          %8.1f\n') % \
                (key,weather[key]['n_runs'],duration_hrs,100.*duration_hrs/total_duration))
        RESFILE.write(('  Total                   %6d            %8.3f\n') % \
            (n_runs, total_duration))
        RESFILE.write('\n')
        RESFILE.write('\n')
    else:
        RESFILE.write('  Total duration was zero.\n')

    CSVFILE.write('Weather (obs only),num runs,duration (h)\n')
    for key in weather_keys:
        duration_hrs = duration2hours(weather[key]['duration'])
        CSVFILE.write(('%s,%d,%.3f\n') % \
            (key,weather[key]['n_runs'],duration_hrs))
    CSVFILE.write('\n')
    CSVFILE.flush()

    fig = plt.figure()
    #fig.subplots_adjust(wspace=0.75)
    #fig.subplots_adjust(hspace=0.5)
    fig.subplots_adjust(right=0.9)
    fig.subplots_adjust(bottom=0.25)
    sp = 111
    plot_stats_oneBar(fig,sp, \
        ('Weather (obs only)','Duration (h)'), \
        weather,stats_keys=weather_keys)
    fig.savefig(f'{output_dir}/Weather_{file_tag}{fext}')

    return fig

def print_days_dist():
    """
    Generate three seperate plots, data duty cycle, observing duty cycle and
    data vs observing duty cycle.
    """
    min_len = dt.timedelta(hours=2.0)
    ddcs_bad = []
    odcs_bad = []
    ddcs_good = []
    odcs_good = []
    for date, day in days.items():
        lon = days[date]['length_of_night']
        ddc = days[date]['data_dc']
        odc = days[date]['obs_dc']
        avgwea = days[date]['avgwea']
        if ddc == 99. or odc == 99.:
            continue
        if lon < min_len or avgwea < 0.69:
            ddcs_bad.append(ddc)
            odcs_bad.append(odc)
            continue
        ddcs_good.append(ddc)
        odcs_good.append(odc)

    ddcs_all = []; ddcs_all.extend(ddcs_bad) ; ddcs_all.extend(ddcs_good)
    odcs_all = []; odcs_all.extend(odcs_bad) ; odcs_all.extend(odcs_good)
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    if len(ddcs_all) > 1:
        ax1.hist(ddcs_all, bins=50, facecolor='0.45')
    ax1.set_xlim(0.0,1.0)
    #ax.bar(xvals+0.025,ddc_hist,0.025)
    ax1.set_title("Data Duty Cycle")
    fig1.savefig(f'{output_dir}/DataDutyCycle_{file_tag}{fext}')

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    if len(odcs_all) > 1:
        ax2.hist(odcs_all, bins=50, facecolor='0.45')
    ax2.set_xlim(0.0,1.0)
    #ax.bar(xvals+0.025,ddc_hist,0.025)
    ax2.set_title("Observing Duty Cycle")
    fig2.savefig(f'{output_dir}/ObservingDutyCycle_{file_tag}{fext}')

    fig3 = plt.figure()
    ax3 = fig3.add_subplot(111)
    ax3.plot(ddcs_good, odcs_good, 'o', color='green')
    ax3.plot([0.05,0.95],[0.05,0.95],color='black',linestyle='dashed')
    plt2 = ax3.plot(ddcs_bad, odcs_bad, '+', color='red')
    ax3.set_xlim(0.0,1.0)
    ax3.set_ylim(0.0,1.0)
    ax3.set_title("Data vs Observing Duty Cycle")
    ax3.legend(('good','bad'))
    fig3.savefig(f'{output_dir}/DataVsObservingDutyCycle_{file_tag}{fext}')

    return (fig1, fig2, fig3)


def close_stats():
    #fig1.savefig(f'{output_dir}/Stats-1.pdf')
    #fig2.savefig(f'{output_dir}/Stats-2.pdf')
    #fig3.savefig(f'{output_dir}/Stats-3.pdf')
    #fig4.savefig(f'{output_dir}/Stats-4.pdf')

    return
