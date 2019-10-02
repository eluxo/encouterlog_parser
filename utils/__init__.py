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

from time import sleep
import csv
import threading

import database

import traceback as tr

from messages import MessageFactory

from utils.gameclock import GameClock

class TailSource:
    '''
    A tail source can be used with a CSV source in order to read from a file
    that gets extended while being parsed.

    This can be used for live reading of logs. The reader blocks while there
    are no updates found in the file.
    '''
    def __init__(self, filename):
        '''
        Constructor.

        @param filename: Path to the file being read.
        '''
        self.__fp = open(filename, "rb")
        self.__stop = False
        self.__sleep = 0.01

    def __iter__(self):
        '''
        Getter for the iterator instance.

        @return: Always references itself.
        '''
        return self

    def next(self):
        '''
        Reads the next line from the opened file.

        If there is not enough data in the file, this call bkocks until a fill
        line of data has been appended to the file.
        '''
        pos = self.__fp.tell()
        while not self.__stop:
            rc = self.__fp.readline()
            if rc.endswith("\n"):
                return rc

            if len(rc) != 0:
                self.__fp.seek(pos)

            sleep(self.__sleep)

class EventSource(object):
    '''
    The event source handles reading the logfile from the given source and
    converts the retrieved data into message objects that are delivered to the
    observing objects of this class.
    '''

    def __init__(self, reader):
        '''
        Constructor.

        @param reader: A CSV reader or some equal source of data.
        '''
        self.__reader = reader
        self.__factory = MessageFactory()
        self.__count = 0
        self.__observers = []
        self.__enableDatabase = False
        self.__running = False
        self.thread = None
        self.database = database.LogDatabase()
        self.clock = GameClock()

    def loop(self, background = False):
        '''
        The main loop of the event source. This remains blocking until the
        reader runs out of data.

        If the reader is one that does wait for more data on EOF, this will
        block forever.

        If a blocking call is not applicable, the loop can also be put into
        a background thread. All callbacks will then be handled from within
        the background thread.

        Having a background thread collecting and parsing the data makes
        sense when live data is captured.

        @param background: If set true, a background thread will be created.
        '''
        if self.__running:
            raise Exception("can only bestarted once")

        self.__running = True
        if background:
            thread = threading.Thread(target = self.loop)
            self.__running = False
            thread.start()
            self.thread = thread
            return self

        useDatabase = self.__enableDatabase
        for row in self.__reader:
            try:
                #time.sleep(0.01)
                if not self.__running:
                    return self

                self.__count += 1
                if len(self.__observers) == 0:
                    continue

                message = self.__factory.create(row)
                if not message:
                    continue

                # Note the order:
                #   1.) clock update
                #   2.) database update
                #   3.) call observers
                self.clock.handle(self, message)
                if useDatabase:
                    self.database.handle(self, message)

                for observer in self.__observers:
                    observer(self, message)
            except:
                print(row)
                tr.print_exc()
        return self

    def stop(self):   # TODO: make it work properly
        '''
        Stops the event loop.

        This will only stop, if there is new data on the input file for now.
        '''
        self.__running = False  # TODO: using a different variable will make it safe

    def addHandler(self, handler):
        '''
        This is only a wrapper around the addObserver method to allow adding
        BasicHandler instances without having to care about the base classes
        interface.

        @param handler: Instance of the handler to be added.
        '''
        return self.addObserver(handler.handle)

    def addObserver(self, callback):
        '''
        Adds an observer method that gets called by the EventSource
        everytime a new line of data bas been received.

        The callback will receive two parameters:

        1. the instance of the EventSource
        2. the message object that has been received

        @param callback: The observer to be added.
        '''
        self.__observers.append(callback)
        return self

    def remHandler(self, handler):
        '''
        This is only a wrapper around the remObserver method to allow adding
        BasicHandler instances without having to care about the base classes
        interface.

        @param handler: Instance of the handler to be added.
        '''
        return self.remObserver(handler.handle)

    def remObserver(self, callback):
        '''
        Removes an observer from ther list of observers.

        @param callback: The observer to be removed.
        '''
        self.__observers.remove(callback)

    def enableDatabase(self):
        '''
        Enables using the internal database object. This needs to be called
        before the handling loop is started as otherwise important messages are
        skipped and the integrity of the database can not be assured.
        '''
        self.__enableDatabase = True
        return self

    def getLines(self):
        '''
        Returns the number of the line read last.

        @return: Number of the last line read.
        '''
        return self.__count

    @staticmethod
    def createFileReaderSource(filename):
        '''
        Creates an EventSource based on a file that is read until EOF is
        found.
        '''
        return EventSource(csv.reader(open(filename, "r")))

    @staticmethod
    def createFileStreamSource(filename):
        '''
        Creates an EventSource based on a file that is streamed. The reader
        will block on EOF until new content is received.
        '''
        return EventSource(csv.reader(TailSource(filename)))

