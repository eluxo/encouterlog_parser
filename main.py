#!/usr/bin/env python2.7
# encoding: utf-8

import csv
import messages
import database
import utils
import traceback as tr

from messages import MESSAGE_TYPE as MessageType

#LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/encounterlog.backup.txt'
LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/Encounter.log'
#LOGFILE="samples/sample1.log"

class Handler:
    def __init__(self):
        self.startTime = None
        self.endTime = None
        self.unitRegistry = database.UnitRegistry()
        self.abilityRegistry = database.AbilityRegistry()

    def handle(self, source, message):
        self.unitRegistry.handle(message)
        self.abilityRegistry.handle(message)

        if message.typeId == MessageType.BEGIN_COMBAT:
            self.startTime = message.time
            
        elif message.typeId == MessageType.END_COMBAT:
            self.endTime = message.time
            self.calculateStats()
            
        elif message.typeId == MessageType.COMBAT_EVENT:
            self.combatEvent(message)
    
    def calculateStats(self):
        duration = self.endTime - self.startTime
        h = duration / (60 * 60 * 1000)
        m = (duration / (60 * 1000)) % 60
        s = (duration / 1000) % 60
        ms = duration % 1000
        print "total time in encounter: [%02d:%02d:%02d.%03d]" % (h, m, s, ms)
    
    def combatEvent(self, message):
        pass
        

handler = Handler()
utils.EventSource.createFileReaderSource(LOGFILE) \
    .setObserver(handler.handle) \
    .loop()

