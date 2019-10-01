#!/usr/bin/env python3
# encoding: utf-8

import csv
import messages
import utils
import time
import sys

import traceback as tr

from utils.handler import BasicHandler

from messages import MESSAGE_TYPE as MessageType

LOGFILE='/mnt/c/Users/nexus/Documents/Elder Scrolls Online/live/Logs/Encounter.log'

RED=    "\033[0;31m"
GREEN=  "\033[0;32m"
YELLOW= "\033[0;33m"
BLUE=   "\033[0;34m"
RESET=  "\033[0m"


class StatusDisplay(BasicHandler):
    def __init__(self):
        super(StatusDisplay, self).__init__()
        self.__oldCount = 0

    def loop(self, eventSource):
        '''
        Screen thread.

        This thread writes the status information to the screen.

        @param eventSource: The EventSource instance holding the database.
        '''
        self.eventSource = eventSource

        self.__clear()
        while True:
            self.__render()
            time.sleep(0.01)

    def __clear(self):
        '''
        Clears the screen and sets the cursor to 0,0.
        '''
        sys.stdout.write("\033[2J")
        sys.stdout.flush()

    def __origin(self):
        '''
        Moves the cursor back to 0,0.
        '''
        sys.stdout.write("\033[0;0H")

    def __render(self):
        '''
        Shows the curent status on the screen.
        '''
        now = int(time.time() * 1000)
        clock = self.eventSource.clock
        units = self.eventSource.database.units
        gameClock = clock.getGameClock()
        start = clock.getCombatStart()
        end = clock.getCombatEnd()
        self.__origin()

        allies = units.filter(lambda x: x.isPlayer())
        newCount = len(allies)
        if self.__oldCount != newCount:
            self.__clear()
        self.__oldCount = newCount

        for ally in allies:
            self.__printStats(ally)

        if start > end:
            print("Active combat: %s      " % (clock.getTimeString(gameClock - start)))
        else:
            print("Last combat:   %s      " % (clock.getTimeString(end - start)))
        print("Last update:   %s        " % (clock.getTimeString(now - clock.getLastUpdate())))
        sys.stdout.flush()

    def __create_bar(self, cur, max, color):
        '''
        Creates a bar to be displayed.

        @param cur: The current value.
        @param max: The maximum value.
        @param color: The color of the bar.
        @return: Two string. One containing the bar and a second one containing
           the values.
        '''
        if max == 0:
            max = 1
        if cur > max:
            cur = max

        count = int(cur * 15 / max)
        missing = 15 - count
        pct = int(cur * 100 / max)

        bar =   "%s[%s%s] %3i%% %s" % (color, "#" * count, " " * missing,  pct, RESET)
        value = "%s%-23s%s" % (color, "%d/%d" % (cur, max), RESET)
        return bar, value

    def __printStats(self, ally):
        hp = ["", ""]
        magicka = hp
        stamina = hp
        ulti = hp
        shield = hp
        name = ally.getName()[:35]
        info = ally.getInfoString()

        if ally.unitStats:
            unitStats = ally.unitStats
            hp =      self.__create_bar(unitStats.currentHp,   unitStats.maxHp,   RED)
            magicka = self.__create_bar(unitStats.currentMag,  unitStats.maxMag,  BLUE)
            stamina = self.__create_bar(unitStats.currentStam, unitStats.maxStam, GREEN)
            ulti =    self.__create_bar(unitStats.currentUlti, unitStats.maxUlti, YELLOW)
            shield =  self.__create_bar(unitStats.shield,      unitStats.maxHp,   RESET)

        print("%-35s %s %s %s %s %s" % (name, hp[0], magicka[0], stamina[0], ulti[0], shield[1]))
        print("%-35s %s %s %s %s %s" % (info,   hp[1], magicka[1], stamina[1], ulti[1], " " * len(shield[1])))
        print(" " * 80)



statusHandler = StatusDisplay()
loop = utils.EventSource.createFileReaderSource(LOGFILE) \
    .addHandler(statusHandler) \
    .enableDatabase() \
    .loop(background = True)

statusHandler.loop(loop)
loop.stop()
loop.thread.join()

