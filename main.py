#!/usr/bin/env python2.7
# encoding: utf-8

import csv
import messages
import database
import utils
import traceback as tr

from messages import MESSAGE_TYPE as MessageType

#LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/encounterlog.backup.txt'
#LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/Encounter.log'
LOGFILE="samples/sample1.log"

class Handler:
    def __init__(self):
        self.startTime = None
        self.endTime = None
        self.database = database.LogDatabase()
        self.damageSums = {}

    def handle(self, source, message):
        self.database.handle(message)

        if message.typeId == MessageType.BEGIN_COMBAT:
            self.startTime = message.time
            
        elif message.typeId == MessageType.END_COMBAT:
            self.endTime = message.time
            self.calculateStats()
            self.damageSums = {}
            
        elif message.typeId == MessageType.COMBAT_EVENT:
            self.__combatEvent(message)
    
    def calculateStats(self):
        duration = self.endTime - self.startTime
        h = duration / (60 * 60 * 1000)
        m = (duration / (60 * 1000)) % 60
        s = (duration / 1000) % 60
        ms = duration % 1000
        for src, entries in self.damageSums.iteritems():
            for dst, value in entries.iteritems():
                print "%35s -> %35s %10d %10.2f" % (src, dst, value, value * 1000 / float(duration))
        print "total time in encounter: [%02d:%02d:%02d.%03d]" % (h, m, s, ms)
    
    def __combatEvent(self, message):
        src = message.srcUnit
        dst = message.dstUnit
        if dst == None or src == None:
            return
        
        srcUnit = self.database.units.get(src.unitId)
        dstUnit = self.database.units.get(dst.unitId)
        srcId = srcUnit.getName()
        dstId = dstUnit.getName()
        if srcId not in self.damageSums:
            self.damageSums[srcId] = {}
        
        if dstId not in self.damageSums[srcId]:
            self.damageSums[srcId][dstId] = 0
        
        self.damageSums[srcId][dstId] += message.damage

handler = Handler()
utils.EventSource.createFileReaderSource(LOGFILE) \
    .setObserver(handler.handle) \
    .loop()

