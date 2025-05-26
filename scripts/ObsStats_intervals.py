#!/usr/bin/env python
## Generate an observing stats report for the day, the dark run and the season.

import datetime as dt
#import os
#import re
import sys
import string
import subprocess
import time

## today at 14h UTC is the end datetime for all three intervals
todayDate = dt.date.today()
today = dt.datetime(todayDate.year, todayDate.month, todayDate.day, hour=14)

## Now determine the start dates for the three intervals:
## startOfToday, the startOfMonth and the startOfSeason

## startOfToday ...
## ... is today - 24 hours
startOfToday = today-dt.timedelta(hours=24)

## startOfMonth is the start of the dark run ...
## ... loop over a file containing the date of the full Moon until we find a date less than
## ....one synodic month prior to today's date
## ....29days, 12hours, 44minutes, 2.9 seconds is the synodic period of the moon, which measures
## ....its phase.
## The file format is:  'Date UTC_Time    Julian_Date'  eg, '2000-Jan-21 04:42    2451564.696'
fullMoonFH = open('FullMoons.txt','r')
synodicMonth = dt.timedelta(days=29, hours=12, minutes=44, seconds=2.9)
while True:
    ## read a line
    fullMoonLine = fullMoonFH.readline()
    ## extract the Date and UTC_Time from the first 16 characters
    fullMoonDate = dt.datetime.strptime(fullMoonLine[0:16],'%Y-%b-%d %H:%M')
    if (today - fullMoonDate) < synodicMonth:
        startOfMonth = fullMoonDate
        break
fullMoonFH.close()

## startOfSeason ...
## ... the season is assumed to start on September 1st at 14h UTC.  If the current month is >=9 then we
## ... are in the first "half" of the season so the year is the current year, else its last year.
if todayDate.month >= 9:
    startOfSeason = dt.datetime(todayDate.year, month=9, day=1, hour=14)
else:
    startOfSeason = dt.datetime(todayDate.year-1, month=9, day=1, hour=14)

## Now assemble some "command" strings of the form:
## ./ObsStats_main.py --start '2008-May-20' --end '2008-Jun-18' > 'Results/ObsStats_2008may20-2008jun18.txt'

delCommand = "rm Results/*thisDay.* >& /dev/null; rm Results/*thisMonth.* >& /dev/null; rm Results/*thisSeason.* >& /dev/null"
todayCommand = "./ObsStats_main.py --tag thisDay --start '"+str(startOfToday)[0:16]+"' --end '"+str(today)[0:16]+"' > Results/ObsStats_Msgs.txt"
monthCommand = "./ObsStats_main.py --tag thisMonth --start '"+str(startOfMonth)[0:16]+"' --end '"+str(today)[0:16]+"' > Results/ObsStats_Msgs.txt"
seasonCommand = "./ObsStats_main.py --tag thisSeason --start '"+str(startOfSeason)[0:16]+"' --end '"+str(today)[0:16]+"' >> Results/ObsStats_Msgs.txt"

#delCommand = "rm Results/*thisSeason.*"
#seasonCommand = "./ObsStats_main.py --tag thisSeason --start '"+str(startOfSeason)[0:16]+"' --end '2017-Jul-06' >> Results/ObsStats_Msgs.txt"

print(delCommand)
retcode = subprocess.call(delCommand,shell=True)
print(todayCommand)
retcode = subprocess.call(todayCommand,shell=True)
print(monthCommand)
retcode = subprocess.call(monthCommand,shell=True)
print(seasonCommand)
retcode = subprocess.call(seasonCommand,shell=True)
