#!/usr/bin/env python2.7
# encoding: utf-8

import csv
import messages
import traceback as tr

#LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/encounterlog.backup.txt'
#LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/Encounter.log'
LOGFILE="samples/sample1.log"
fp = open(LOGFILE, "rb")
reader = csv.reader(fp)

factory = messages.MessageFactory()

loglines = []
types = {}
i = 0
for row in reader:
    try:
        i += 1
        message = factory.create(row)
        loglines.append(message)
        types[message.type] = 0
    except:
        print i, row
        tr.print_exc()
        break

for type in types.keys():
    print "\t'%s': Message," % (type)


