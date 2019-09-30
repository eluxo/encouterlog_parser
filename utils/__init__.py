import time
import csv

import traceback as tr

from messages import MessageFactory

class LatencyMeter(object):
    def __init__(self):
        self.start = -1
        self.diff = 0
        self.current = 0

    def handle(self, message):
        if message.type == "BEGIN_LOG":
            self.__beginLog(message)
            return

        self.__message(message)

    def __beginLog(self, beginLog):
        self.start = beginLog.serverTime
        self.diff = beginLog.time
        self.__message(beginLog)

    def __message(self, message):
        self.current = self.start + self.diff + message.time

    def getLatency(self):
        now = int(time.time() * 1000)
        return now - self.current

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

            time.sleep(self.__sleep)

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
        self.__callback = None

    def loop(self):
        '''
        The main loop of the event source. This remains blocking until the
        reader runs out of data.

        If the reader is one that does wait for more data on EOF, this will
        block forever.
        '''
        for row in self.__reader:
            try:
                self.__count += 1
                if not self.__callback:
                    continue

                message = self.__factory.create(row)
                if not message:
                    continue

                self.__callback(self, message)
            except:
                print row
                tr.print_exc()

    def setObserver(self, callback):
        '''
        Sets the observer method that gets called by the EventSource
        everytime a new line of data bas been received.

        The callback will receive two parameters:

        1. the instance of the EventSource
        2. the message object that has been received

        @param callback: The callback to be used.
        '''
        self.__callback = callback
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
        return EventSource(csv.reader(open(filename, "rb")))

    @staticmethod
    def createFileStreamSource(filename):
        '''
        Creates an EventSource based on a file that is streamed. The reader
        will block on EOF until new content is received.
        '''
        return EventSource(csv.reader(TailSource(filename)))
