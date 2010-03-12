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
from optparse import OptionParser

try:
    from config import username, password
except ImportError:
    sys.stderr.write("""No config file found, please modify 'config.py.example' and rename
            it 'config.py'""")
    sys.exit(1)
    
from parsedatetime import parsedatetime as pdt

VERBOSE = False
RETRY_WAIT = 10

def print_help():
    print 'Usage: python %s <title> in <time>' % sys.argv[0]
    print 'Example: python %s eat pizza in 2h 30m' % sys.argv[0]
    sys.exit()
    
def prnt(s, verbose=False, target=sys.stdout):
    if not verbose:
        print >> target, s
    elif verbose and VERBOSE:
        print >> target, s

parser = OptionParser()
parser.usage = "%prog [[options] | <reminder> in <time>]\nExample: %prog eat pizza in 2h 30m"
parser.add_option("-i", "--interactive", dest="interactive",
                  action="store_true", help="Run gRemind in interactive mode")
parser.add_option("-v", "--verbose", dest="verbose",
                  action="store_true", help="More info about what's going on")

options, args = parser.parse_args()

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit()

if options.verbose:
    VERBOSE = True

if options.interactive:
    title = raw_input('Remind me to: ')
    when = raw_input('In: ')
else:
    args = ' '.join(args)
    if ' in ' in args:
        i = args.rfind(' in ')
        title = args[:i]
        when = args[i+4:]
    else:
        print_help()
        
title = title.decode(sys.stdout.encoding or 'utf-8', 'replace')

gcal = gdata.calendar.service.CalendarService()
gcal.email = username
gcal.password = password
gcal.source = 'gRemind'
prnt('Logging in as %s' % username, True)
try:
    gcal.ProgrammaticLogin()
except gdata.service.BadAuthentication, e:
    prnt(e, target=sys.stderr)
    sys.exit(1)

dateparser = pdt.Calendar()

start_time = dateparser.parse(when, time.gmtime())[0]
end_time = time.gmtime(calendar.timegm(start_time)+60)
start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', start_time)
end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', end_time)

local_time = time.asctime(dateparser.parse(when)[0])

event = gdata.calendar.CalendarEventEntry()
event.title = atom.Title(text=title)
event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))
r = gdata.calendar.Reminder(minutes=0)
r.method = "sms"
event.when[0].reminder.append(r)

prnt('Creating reminder event.', True)
try:
    event = gcal.InsertEvent(event, '/calendar/feeds/default/private/full')
except gdata.service.RequestError:
    prnt('Failed to create a reminder, retrying in %d seconds...' % RETRY_WAIT, True, sys.stderr)
    time.sleep(RETRY_WAIT)
    try:
        prnt('Attempting to set a reminder again...', True)
        event = gcal.InsertEvent(event, '/calendar/feeds/default/private/full')
    except gdata.service.RequestError:
        prnt('Unable to create a new reminder, please try again in a couple of seconds.', target=sys.stderr)
        sys.exit(1)
    else:
        prnt('Reminder created successfully.', True)


print "Google will remind you '%s' at %s" % (title, local_time)