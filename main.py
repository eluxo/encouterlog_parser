#!/usr/bin/env python2.7
# encoding: utf-8

import csv
import messages
import utils
import traceback as tr

#LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/encounterlog.backup.txt'
LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/Encounter.log'
#LOGFILE="samples/sample1.log"

def handler(source, message):
    print "%4i %s" % (source.getLines(), message.type)

utils.EventSource.createFileReaderSource(LOGFILE) \
    .setObserver(handler) \
    .loop()

