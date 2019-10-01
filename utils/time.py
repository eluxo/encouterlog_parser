#!/usr/bin/env python3
# encoding: utf-8

import time

from messages import MESSAGE_TYPE as MessageType

class GameClock:
    '''
    Helper class for all time based calculations around the combat activities.
    
    An instance of this is used by the EventSource to keep track of the current
    time configurations.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        self.__referenceTime = 0  # holds the refecence clock
        self.__localReference = 0 # holds the local time at the time the referenceTime has been set
        self.__currentTime = 0    # holds the time last seen in the log
    
    def handle(self, source, message):
        '''
        Handles all messages that are received from the log and keeps their
        timestamps.
        
        @param source: The event source.
        @param message: The message being received.
        '''
        if message.type == MessageType.BEGIN_LOG:
            self.__beginLog(message)
        self.__message(message)
    
    def __beginLog(self, message):
        '''
        Handles all BEGIN_LOG messages. Those messages contain a relative
        timestamp holding some difference between the actual timestamps and the
        server time and the server time. This is used to update the
        __referenceTime value.
        
        @param message: The BEGIN_LOG message.
        '''
        self.__referenceTime = message.serverTime - message.time
        self.__localReference = int(time.time() * 1000)
    
    def __message(self, message):
        '''
        Sets the current absolute time based on a relative timestamp extracted
        from the given message.
        
        The time is set based on the current reference time.
        
        @param message: The message used to set the time.
        '''
        self.__currentTime = message.time + self.__referenceTime
    
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

    def getTimeString(self, time):
        '''
        Returns a string representation of the given timestamp split into the
        different elements.
        '''
        latency = meter.getLatency()
        h = latency / (1000 * 60 * 60)
        m = (latency / (1000 * 60)) % 60
        s = (latency / 1000) % 60
        ms = latency % 1000
        return "%02d:%02d:%02d.%03d" % (h, m, s, ms)
