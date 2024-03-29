#!/usr/bin/env python3
# encoding: utf-8
#
# Eluxo's Encouterlog Parser
# Copyright (C) 2019  eluxo
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import csv
import messages
import utils
import traceback as tr
from utils.handler import BasicHandler
from utils.damagetracker import DamageTracker

from messages import MESSAGE_TYPE as MessageType

#LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/encounterlog.backup.txt'
#LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/Encounter.log'
LOGFILE="samples/sample1.log"

class Handler(BasicHandler):
    def __init__(self):
        super(Handler, self).__init__()
        self._setClaim(MessageType.BEGIN_COMBAT, self.__beginCombat)
        self._setClaim(MessageType.END_COMBAT, self.__endCombat)
        self._setClaim(MessageType.COMBAT_EVENT, self.__combatEvent)
        self.startTime = None
        self.endTime = None
        self.damageSums = {}

    def calculateStats(self):
        duration = self.endTime - self.startTime
        h = duration / (60 * 60 * 1000)
        m = (duration / (60 * 1000)) % 60
        s = (duration / 1000) % 60
        ms = duration % 1000
        for src, entries in self.damageSums.items():
            for dst, value in entries.items():
                print("%35s -> %35s %10d %10.2f" % (src, dst, value, value * 1000 / float(duration)))
        print("total time in encounter: [%02d:%02d:%02d.%03d]" % (h, m, s, ms))

    def __beginCombat(self, source, message):
        self.startTime = message.time

    def __endCombat(self, source, message):
        self.endTime = message.time
        self.calculateStats()
        self.damageSums = {}

    def __combatEvent(self, source, message):
        src = message.srcUnit
        dst = message.dstUnit
        if dst == None or src == None:
            return

        srcUnit = source.database.units.get(src.unitId)
        #if not srcUnit.isPlayer():
        #    return

        dstUnit = source.database.units.get(dst.unitId)
        #if dstUnit.isPlayer():
        #    return

        srcId = srcUnit.getName()
        dstId = dstUnit.getName()
        if srcId not in self.damageSums:
            self.damageSums[srcId] = {}

        if dstId not in self.damageSums[srcId]:
            self.damageSums[srcId][dstId] = 0

        self.damageSums[srcId][dstId] += message.damage

handler = Handler()
tracker = DamageTracker()
loop = utils.EventSource.createFileReaderSource(LOGFILE) \
    .addHandler(tracker) \
    .addHandler(handler) \
    .enableDatabase() \
    .loop(background = True)
loop.thread.join()
