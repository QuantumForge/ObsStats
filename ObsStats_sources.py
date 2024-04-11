#!/usr/bin/env python

import datetime as dt
#import getopt
import math
#import os
import re
import sys
#import string
#import time
from urllib.request import urlopen

## Import global variables into this namespace
from ObsStats_global import *

## Import functions into their own namespace
#import ObsStats_days
#import ObsStats_ephem#import ObsStats_runs
#import ObsStats_sources

## Create some simple aliases
#m_days = ObsStats_days
#m_ephem = ObsStats_ephem
#m_runs = ObsStats_runs
#m_sources = ObsStats_sources

def init_source_types():
    """
    Initialize the source_types dict.
    """
    source_types['AGN']=['AGN','Active Galaxy Nucleus']
    source_types['AMHer']=['Galactic','Catalysmic Variable']
    source_types['BLLac']=['AGN','BL Lac']
    source_types['Be*']=['Galactic','Be Star']
    #source_types['Blazar']=['AGN','Blazar']
    source_types['ClG']=['ExGalactic','Cluster of Galaxies']
    source_types['Crab']=['Crab','Crab']
    source_types['DMUkn']=['DM','DM Unknown']
    source_types['DwarfG']=['DM','Dwarf Galaxy']
    source_types['EB*Algol']=['NOSOURCE','Algol-type eclipsing binary ']
    source_types['EmG']=['ExGalactic','Emission-line Galaxy ']
    source_types['Flare*']=['NOSOURCE','Star']
    source_types['FR_II']=['ExGalactic','FR II Radio Galaxy']
    source_types['FSRQ']=['AGN','Radio Loud AGN']
    source_types['GRB']=['GRB','Gamma-ray Burst']
    source_types['Galaxy']=['ExGalactic','Galaxy']
    source_types['GalCen']=['DM','Galactic Center']
    source_types['GalUkn']=['Galactic','Galactic Unknown']
    source_types['GalYoung']=['Galactic','Galactic Young Stellar Objects']
    source_types['GinGroup']=['ExGalactic','Galaxy in Group of Galaxies ']
    source_types['GenExGal']=['ExGalactic','General']
    source_types['GlCl']=['ExGalactic','Globular Cluster']
    source_types['HMXB']=['Galactic','High Mass X-ray Binary']
    source_types['Hotspot']=['Unknown','Hotspots identified by others or in the SkySurvey']
    source_types['IG']=['ExGalactic','Interacting Galaxies']
    source_types['LINER']=['ExGalactic','LINER-type Active Galaxy Nucleus']
    source_types['LMXB']=['Galactic','Low Mass X-ray Binary']
    source_types['Mag']=['Galactic','Magnetar']
    #source_types['MolCld']=['Galactic','Molecular Cloud']
    source_types['Neb']=['Galactic','Nebula']
    source_types['NOSOURCE']=['NOSOURCE','Not a source']
    #source_types['nosource']=['NOSOURCE','Not a source']
    source_types['Nova']=['Galactic','Nova']
    source_types['OpCl']=['ExGalactic','Open Galactic Cluster']
    source_types['Planet']=['NOSOURCE','exoplanet']
    source_types['Pulsar']=['Galactic','Pulsar']
    source_types['QSO']=['AGN','QSO']
    #source_types['QSO_Candidate']=['AGN','QSO_Candidate']
    source_types['Radio']=['ExGalactic','Radio Source (unknown)']
    source_types['RadioG']=['ExGalactic','Radio Galaxy']
    source_types['SGR']=['Galactic','SGR']
    source_types['SNR']=['Galactic','SNR']
    source_types['Seyfert']=['AGN','Seyfert']
    source_types['Seyfert_1']=['AGN','Seyfert_1']
    source_types['Seyfert_2']=['AGN','Seyfert_2']
    source_types['Star']=['NOSOURCE','Star']
    source_types['SkySurvey']=['SkySurvey','SkySurvey']
    source_types['UID']=['Unknown','Unidentified Gamma Source']
    source_types['ULIRG']=['ExGalactic','ULIRG']
    source_types['Unknown']=['Unknown','Unknown']
    source_types['WR*']=['Galactic','Wolf-Rayet Star']

    return

def init_source_classes():
    """
    Initialize (extend) the source_classes list.
    """
    source_classes.extend(['AGN','Crab','DM','ExGalactic','Galactic','GRB','NOSOURCE',
        'SkySurvey','Unknown'])

    return

def fetch_sources_frm_dB():
    """
    Query the database for all the source data records.
    """

    try:
        import pymysql
    except ImportError:
        sys.exit('Failed to import pymysql in read_sources!\n')

    try:
        #db_connect=pymysql.connect(host="veritase.sao.arizona.edu",user="readonly",db="VERITAS")
        # Upgrading MacOS to 14.1.1 Sonoma, now need to specify the charset
        # WFH 20231125
        db_connect=pymysql.connect(host="romulus.ucsc.edu",user="readonly",db="VERITAS", charset="utf8")
        #db_connect=pymysql.connect(host="remus.ucsc.edu",user="readonly",db="VERITAS")
    except:
        sys.exit("Failed to connect to db in read_sources!\n")

    cursor=db_connect.cursor()

    query = 'SELECT source_id, description, ra, decl, epoch FROM tblObserving_Sources'
    cursor.execute (query)
    sources_IndB = cursor.fetchall()

    for source in sources_IndB:
        source_id = source[0]
        sources[source_id] = {'source_id':source_id, 'desc': source[1], \
            'ra': source[2], 'decl': source[3], 'epoch': source[4], \
            ## initialize some value(s) here which will be set elsewhere
            'source_type':''}

    cursor.close()
    db_connect.close()

    return

def init_source_type_in_sources():
    """
    Determine the source_type field for each source_id

    First, read in SourcesNTypes file and if possible initialize
    from that info.  If not, go the SIMBAD route ...

    ... parse source_id to determine whether its a bog standard source,
    if not, format the source_id and call SIMBAD.

    NB, source_id can be quite a messy beast,
        eg, 'GRB 2009-08-29 16:50:40 FERMI/GBM 273257442 FLT_POS'

    Verify that source_type is among the keys in the source_types dict;
    if not, print warning and add it.
    """

    ## Open and read the SourcesNTypes file into the destination array
    ## e.g., 1RXS J044127.8+150455,BLLac
    SNTFILE = open('SourcesNTypes.txt','r')
    lines = SNTFILE.readlines()
    SNTFILE.close()
    prflg = True
    for line in lines:
        if line[0] == '#':
            continue
        ## re.search returns a group.
        ## Groups()[1] is the 1st match, group()[2] is the second
        #stgs = re.search('^(.*)\W(.*)\n$',line)
        stgs = re.search('^(.*),(.*)\n$',line)
        source_id = stgs.groups()[0]
        type_id = stgs.groups()[1]
        #print "DEBUG: source_id %s type_id %s" % (source_id,type_id)
        if source_id in sources:
            sources[source_id]['source_type'] = type_id
        else:
            #if prflg: print ("\n") ; prflg = False
            ## If the source_id does not exist in sources then create it
            print (("\n** source_id %s of type_id %s not found in sources dB **\n") % (source_id, type_id))
            sources[source_id] = {'source_id':source_id, 'desc':'', \
                'ra':999.0, 'decl':999.0, 'epoch':999.0, \
                'source_type':type_id}

    #simbad = "http://simbad.u-strasbg.fr/simbad/sim-script?script=%20output%20script=off%20error=off%20console=off%0aformat%20object%20%22%25IDLIST(1)%7c%25OTYPE%22"
    simbad = "http://simbad.cfa.harvard.edu/simbad/sim-script?script=%20output%20script=off%20error=off%20console=off%0aformat%20object%20%22%25IDLIST(1)%7c%25OTYPE%22"

    prflg = True
    for source_id, source in sources.items():
        ## Test if we've set the source_type above
        ## ... if so then continue to next source
        if source['source_type'] != '':
            #print source_id,source
            continue
        ## ... or test whether its NOT a real source
        if isBSC.search(source_id) or \
            isCalEng.search(source_id) or \
            isDARK.search(source_id) or \
            isFAKE.search(source_id) or \
            isNOSOURCE.search(source_id) or \
            isREGULUS.search(source_id) or \
            isSTAR.search(source_id) or \
            isTEST.search(source_id) or \
            isTHETA1.search(source_id) or \
            isZENITH.search(source_id):
            source_type = 'NOSOURCE'
        ## ... or correct some naming deficiencies
        elif isANHER.search(source_id):
            source_type = 'AMHer'
        elif isCRAB.search(source_id):
            source_type = 'Crab'
        elif isGRBv1.search(source_id) or isGRBv2.search(source_id):
            source_type = 'GRB'
        elif isIC433.search(source_id):
            source_type = 'HMXB'
        elif isSURVEY.search(source_id) or isMilSURVEY.search(source_id) or isCygHS.search(source_id):
            source_type = 'SkySurvey'
        ## ... or interrogate the SIMBAD database to determine the source_type
        else:
            id = source_id
            id = re.sub('\+','%2B',id)
            id = re.sub('\-','%2D',id)
            id = re.sub(' ','%20',id)
            try:
                f = urlopen(("%s%s%s")%(simbad,'%0a',id))
                reply = f.read().decode('utf-8')
            except:
                #if prflg: print ("\n") ; prflg = False
                print (("\n** simbad call for source_id %s failed **\n") % (source_id))
                reply = ''
            if reply == '':
                source_type = 'Unknown'
            else:
                #if prflg: print ("\n") ; prflg = False
                # NB: the string value returned by SIMBAD is terminated with two <cr>s
                print (("\n** SIMBAD reports %s as source_id|source_type %s **") % \
                    (source_id, reply[0:-2]))
                    #print "DEBUG: SIMBAD return string: %s" % reply
                try:
                    source_type = reply[reply.index('|')+1:reply.index('~')-1]
                except ValueError:
                    source_type = 'Unknown'
                    print(("\n** source_id %s source_type lookup FAILS from simbad **\n") % (source_id))

                #source_type = reply[reply.index("b'|'")+1:reply.index("b'~'")-1]
                ## Catch returned blank but not empty 'reply'
                if source_type == '':
                    source_type = 'Unknown'
                    #if prflg: print ("\n") ; prflg = False
                    print (("\n** source_id %s returns blank from simbad **\n") % (source_id))
        source['source_type'] = source_type
        ## If source type not found then assign it to catchall
        if source_type not in source_types:
            #if prflg: print ("\n") ; prflg = False
            print (("\n** source_type %s of source_id %s not found in source_types **\n") % \
                (source_type, source_id))
            source_types[source_type] = ['Unknown','Unknown']
        if source_type == 'Unknown':
            print (("\n** source_id %s of unknown source_type **\n") % (source_id))
    return

def update_n_flag_sources():
    """
    Loop over sources and if the source_id is not among those in
    sources_in_runs remove it (ie, eliminate spurious sources).

    #If source_id is BSC or DARK, remove it.

    Add flag [A-Z,a-z,0-9] to remaining sources.  If the number of
    sources exceeds 62 flag = '?'
    """
    for source_id, source in list(sources.items()):
        #if source_id[0:3] == 'BSC' or source_id[0:4] == 'DARK':
            #del sources[source_id]
            #continue
        if source_id not in sources_in_runs:
            try:
                del sources[source_id]
            except:
                print (("\n** source_id %s not found in sources **\n") % (source_id))

    index = 1
    for source_id, source in list(sources.items()):
        if 1 <= index <= 26:
            ## A-Z
            source['flag'] = chr(index+64)
        elif 26 < index <= 52:
            ## a-z
            source['flag'] = chr(index+70)
        elif 52 < index < 62:
            ## 0-1
            source['flag'] = chr(index-5)
        else:
            source['flag'] = '?'
            #print ("\n** number of sources exceeds 62\n")
        index += 1

    return

def init_RA_stats():
    """
    Initialize the stats for each RA band"
       RA_stats = {RA: {n_sources:int, duration:datetime.timedelta, \
        awea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta,\
        Low_HV:datetime.timedelta,UV_Filt:datetime.timedelta}},
        bwea...}
    """
    for hr in range(24):
        RA_stats[hr] = {'n_sources':0,\
            'duration':dt.timedelta(0), \
            'awea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'bwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'cwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'dwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)} \
            }
    return
            
def init_source_stats():
    """
    Initialize the source_stats dict:
        source_stats = {source_id: {n_runs:int, duration:datetime.timedelta, \
        awea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
        bwea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
        etc}
   """
    for source_id, source in sources.items():
        if source['source_type'] == 'NOSOURCE':
            continue
        source_stats[source_id] = {'n_runs':0, \
            'duration':dt.timedelta(0), \
            'awea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'bwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'cwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'dwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            }

    return

def init_source_type_stats():
    """
    Initialize the source_type_stats dict:
        source_type_stats = {source_type: {n_sources(of type):int, n_runs:int, \
        awea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
        bwea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
        etc}

    Loop over the source_types dict
    """
    for type_id, source_type in source_types.items():
        source_type_stats[type_id] = {'source_type':source_type, \
            'n_sources':0, 'n_runs':0, \
            'duration':dt.timedelta(0), \
            'awea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'bwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'cwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'dwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            }

    return

def init_source_class_stats():
    """
    Initialize the source_class_stats dict:
        source_class_stats = {source_class: {n_sources(of type):int, n_runs:int, \
        awea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
        bwea:{y(moonlit):datetime.timedelta,n(moonlit):datetime.timedelta}},
        etc}

    Loop over the source_classes dict
    """
    for source_class in source_classes:
        source_class_stats[source_class] = {'source_class':source_class, \
            'n_sources':0, 'n_runs':0, \
            'duration':dt.timedelta(0), \
            'awea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'bwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'cwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            'dwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0),'Low_HV':dt.timedelta(0),'UV_Fil':dt.timedelta(0)}, \
            }

    #for type_id, source_type in source_types.items():
        #source_class = source_type[0]
        #if source_class not in source_class_stats:
            #source_class_stats[source_class] = { \
                #'n_sources':0, 'n_runs':0, \
                #'duration':dt.timedelta(0), \
                #'awea':{'Y':dt.timedelta(0),'N':dt.timedelta(0)}, \
                #'bwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0)}, \
                #'cwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0)}, \
                #'dwea':{'Y':dt.timedelta(0),'N':dt.timedelta(0)}, \
                #}

    return

def print_source(source):
    """
    Given one member of the "sources", print out the source information.

    Eg. m_sources.print_source(sources[source_id])
    """
    print ('\n')
    print (('source_id: %s  desc: %s') % (source['source_id'],source['desc']))
    print (('source_type: %s') % (source['source_type']))
    print (('ra: %s  decl: %s epoch: %s') % (source['ra'],source['decl'],source['epoch']))

    return

def print_sources():
    """
    Pass each source to print_source, but exclude BSC and DARK
    """
    for source_id, source in sources.items():
        if not (source_id[0:3] == 'BSC' or source_id[0:4] == 'DARK'):
            print_source(source)

    return

def process_sources():
    """
    Loop over the sources and gather stats
    """

    # The number of sources in each source_class
    for source_id, source in sources.items():
        source_type = source['source_type']
        source_class = source_types[source_type][0]
        source_class_stats[source_class]['n_sources'] += 1

    # The number of sources and the exposure in each RA band.
    for source_id, source in sources.items():
        source_type = source['source_type']
        if source_type == 'NOSOURCE':
            continue
        RA_hrs = source['ra']*24/(2.0*math.pi)
        RA_int = int(RA_hrs)
        #print(source_id,source_type,RA_hrs,RA_int)
        RA_stats[RA_int]['n_sources'] += 1
        RA_stats[RA_int]['duration'] += source_stats[source_id]['duration']
        RA_stats[RA_int]['awea']['Y'] +=  source_stats[source_id]['awea']['Y']
        RA_stats[RA_int]['awea']['N'] +=  source_stats[source_id]['awea']['N']
        RA_stats[RA_int]['awea']['Low_HV'] +=  source_stats[source_id]['awea']['Low_HV']
        RA_stats[RA_int]['awea']['UV_Fil'] +=  source_stats[source_id]['awea']['UV_Fil']
        RA_stats[RA_int]['bwea']['Y'] +=  source_stats[source_id]['bwea']['Y']
        RA_stats[RA_int]['bwea']['N'] +=  source_stats[source_id]['bwea']['N']
        RA_stats[RA_int]['bwea']['Low_HV'] +=  source_stats[source_id]['bwea']['Low_HV']
        RA_stats[RA_int]['bwea']['UV_Fil'] +=  source_stats[source_id]['bwea']['UV_Fil']
        RA_stats[RA_int]['cwea']['Y'] +=  source_stats[source_id]['cwea']['Y']
        RA_stats[RA_int]['cwea']['N'] +=  source_stats[source_id]['cwea']['N']
        RA_stats[RA_int]['cwea']['Low_HV'] +=  source_stats[source_id]['cwea']['Low_HV']
        RA_stats[RA_int]['cwea']['UV_Fil'] +=  source_stats[source_id]['cwea']['UV_Fil']
        RA_stats[RA_int]['dwea']['Y'] +=  source_stats[source_id]['dwea']['Y']
        RA_stats[RA_int]['dwea']['N'] +=  source_stats[source_id]['dwea']['N']
        RA_stats[RA_int]['dwea']['Low_HV'] +=  source_stats[source_id]['dwea']['Low_HV']
        RA_stats[RA_int]['dwea']['UV_Fil'] +=  source_stats[source_id]['dwea']['UV_Fil']

        #exposure = source_stats[source_id]['duration']
        #RA_sourceNumber_dist[RA_int] += 1
        #RA_exposure_dist[RA_int] += duration2hours(exposure)

    return
