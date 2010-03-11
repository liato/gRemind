#!/usr/bin/env python
try:
  from xml.etree import ElementTree # for Python 2.5 users
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import getopt
import sys
import string
import time
import calendar

try:
    from config import username, password
except ImportError:
    print """No config file found, please modify 'config.py.example' and rename
            it 'config.py'"""
    sys.exit(1)
    
from parsedatetime import parsedatetime as pdt    

gcal = gdata.calendar.service.CalendarService()
gcal.email = username
gcal.password = password
gcal.source = 'gRemind'
gcal.ProgrammaticLogin()
dateparser = pdt.Calendar()

title = raw_input('Remind me to: ')
title = title.decode(sys.stdout.encoding or 'utf-8', 'replace')
when = raw_input('In: ')
start_time = dateparser.parse(when, time.gmtime())[0]
end_time = time.gmtime(calendar.timegm(start_time)+60)
start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', start_time)
end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', end_time)

local_time = time.asctime(dateparser.parse(when)[0])

event = gdata.calendar.CalendarEventEntry()
event.title = atom.Title(text=title)
event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))
event = gcal.InsertEvent(event, '/calendar/feeds/default/private/full')

r = gdata.calendar.Reminder(minutes=0)
r.method = "sms"
event.when[0].reminder.append(r)

gcal.UpdateEvent(event.GetEditLink().href, event)

print "Google will remind you '%s' at %s" % (title, local_time)