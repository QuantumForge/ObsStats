#!/usr/bin/env python

# quick and dirty hack to get full moon dates and times (UTC) in the format
# required for the ObsStats FullMoons.txt file
# William.Hanlon@cfa.harvard.edu, 20231017

import datetime
import ephem


date = datetime.datetime(year=2024, month=1, day=1, hour=12)
full_moon_dates = []

# pyephem uses UTC dates and times
for i in range(0, 24):
    full_moon_date = ephem.next_full_moon(date)
    if i > 0:
        if ephem.julian_date(full_moon_date) - \
                ephem.julian_date(full_moon_dates[-1]) > 1:
            full_moon_dates.append(full_moon_date)
    else:
        full_moon_dates.append(full_moon_date)
    # advance by 15 days to catch blue moons
    date = date + datetime.timedelta(days=15)

for d in full_moon_dates:
    print('{0}    {1:.3f}'.format(d.datetime().strftime('%Y-%b-%d %R'),
          ephem.julian_date(d)))
