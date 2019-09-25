#!/usr/bin/env python2.7
# encoding: utf-8

import csv
import messages
import players
import utils
import traceback as tr
import sys
import time


#LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/encounterlog.backup.txt'
#LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/Encounter.log'
LOGFILE='samples/sample1.log'
#fp = open(LOGFILE, "rb")
class CsvSource:
    def __init__(self, filename):
        self.__fp = open(filename, "rb")
    
    def __iter__(self):
        return self
    
    def next(self):
        pos = self.__fp.tell()
        while True:
            self.__printLatency()
            rc = self.__fp.readline()
            if rc.endswith("\n"):
                return rc
            
            if len(rc) != 0:
                self.__fp.seek(pos)
            time.sleep(0.01)
        
    def __printLatency(self):
            latency = meter.getLatency()
            h = latency / (1000 * 60 * 60)
            m = (latency / (1000 * 60)) % 60
            s = (latency / 1000) % 60
            ms = latency % 1000
            sys.stdout.write("Latency: %-12d [%02d:%02d:%02d.%03d]        \r" % (latency, h, m, s, ms))
            

csvSource = CsvSource(LOGFILE)
reader = csv.reader(csvSource)

factory = messages.MessageFactory()
allies = players.AllyList()
meter = utils.LatencyMeter()

RED=    "\033[0;31m"
GREEN=  "\033[0;32m"
YELLOW= "\033[0;33m"
BLUE=   "\033[0;34m"
RESET=  "\033[0m"

def render(cur, max, color):
    if max == 0:
        max = 1
    if cur > max:
        cur = max
    
    count = cur * 15 / max
    missing = 15 - count
    pct = cur * 100 / max
    
    
    bar =   "%s[%s%s] %3i%% %s" % (color, "#" * count, " " * missing,  pct, RESET) 
    value = "%s%-23s%s" % (color, "%d/%d" % (cur, max), RESET)
    return bar, value

sys.stdout.write("\033[2J")
sys.stdout.flush()
while True:
    rowCount = [0, 0]
    nallies = 0
    for row in reader:
        try:
            message = factory.create(row)
            allies.handle(message)
            meter.handle(message)
            sys.stdout.write("\033[0;0H")
            print nallies, len(allies.allies)
            if nallies > len(allies.allies):
                sys.stdout.write("\033[2J")            
            nallies = len(allies.allies)
            for id, ally in allies.allies.iteritems():
                hp = ["", ""]
                magicka = hp
                stamina = hp
                ulti = hp
                shield = hp
                if ally.unitStats:
                    unitStats = ally.unitStats
                    hp = render(unitStats.currentHp, unitStats.maxHp, RED)
                    magicka = render(unitStats.currentMag, unitStats.maxMag, BLUE)
                    stamina = render(unitStats.currentStam, unitStats.maxStam, GREEN)
                    ulti = render(unitStats.currentUlti, unitStats.maxUlti, YELLOW)
                    shield = render(unitStats.shield, unitStats.maxHp, RESET)
                print "%-20s %s %s %s %s %s" % (ally.account, hp[0], magicka[0], stamina[0], ulti[0], shield[0])
                print "%-20s %s %s %s %s %s" % ("",           hp[1], magicka[1], stamina[1], ulti[1], shield[1])
        except:
            print row
            tr.print_exc()
            break
