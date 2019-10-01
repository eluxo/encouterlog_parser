#!/usr/bin/env python3
# encoding: utf-8

import time

from messages import MESSAGE_TYPE as MessageType

from utils.handler import BasicHandler

class GameClock(BasicHandler):
    '''
    Helper class for all time based calculations around the combat activities.

    An instance of this is used by the EventSource to keep track of the current
    time configurations.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        super(GameClock, self).__init__()
        self.__referenceTime = 0  # holds the refecence clock
        self.__localReference = 0 # holds the local time at the time the referenceTime has been set
        self.__currentTime = 0    # holds the time last seen in the log
        self.__combatStart = 0
        self.__combatEnd = 0
        self.__lastUpdate = 0

        self._setClaim(MessageType.BEGIN_COMBAT, self.__beginCombat)
        self._setClaim(MessageType.END_COMBAT,   self.__endCombat)
        self._setClaim(MessageType.BEGIN_LOG,    self.__beginLog)
        self._setClaim(MessageType.UNKNOWN,      self.__message)

    def __beginCombat(self, source, message):
        '''
        Called when the combat has started.

        @param message: The BEGIN_COMBAT message.
        '''
        self.__combatStart = self.__getAbsTime(message)

    def __endCombat(self, source, message):
        '''
        Called when the combat has ended.

        @param message: This END_COMBAT message.
        '''
        self.__combatEnd = self.__getAbsTime(message)

    def __beginLog(self, source, message):
        '''
        Handles all BEGIN_LOG messages. Those messages contain a relative
        timestamp holding some difference between the actual timestamps and the
        server time and the server time. This is used to update the
        __referenceTime value.

        @param message: The BEGIN_LOG message.
        '''
        self.__referenceTime = message.serverTime - message.time
        self.__localReference = int(time.time() * 1000)

    def __message(self, source, message):
        '''
        Sets the current absolute time based on a relative timestamp extracted
        from the given message.

        The time is set based on the current reference time.

        @param message: The message used to set the time.
        '''
        self.__currentTime = self.__getAbsTime(message)
        self.__lastUpdate = int(time.time() * 1000)

    def __getAbsTime(self, message):
        '''
        Gets the absolute time out of a message object.

        @param message: The message containing a relative time.
        @return: Absolute time of the message.
        '''
        return message.time + self.__referenceTime

    def getGameClock(self):
        '''
        Returns the game clock based on the last time seen.

        @return: Current game clock.
        '''
        return self.__currentTime

    def getClockDrift(self):
        '''
        Returns the clock difference between the local system and the last game
        time seen.

        The value will be negative, if the game clock is ahead of the system
        clock.

        @return: Difference between the local system and the game clock.
        '''
        return int(time.time() * 1000) - self.getGameClock()

    def getCombatStart(self):
        '''
        Returns the time, when the last combat has started.

        @return: Time of the last combat start.
        '''
        return self.__combatStart

    def getCombatEnd(self):
        '''
        Returns the time, when the last combat has ended.

        @return: Time of the last combat end.
        '''
        return self.__combatEnd

    def getLastUpdate(self):
        '''
        Returns the time, when the last message has been received.

        @return: Time when the last message has been received.
        '''
        return self.__lastUpdate

    def getTimeString(self, timestamp):
        '''
        Returns a string representation of the given timestamp split into the
        different elements.

        @param timestamp: The timestamp to format.
        '''
        h = timestamp / (1000 * 60 * 60)
        m = (timestamp / (1000 * 60)) % 60
        s = (timestamp / 1000) % 60
        ms = timestamp % 1000
        return "%02d:%02d:%02d.%03d" % (h, m, s, ms)
