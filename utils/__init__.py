import time

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

