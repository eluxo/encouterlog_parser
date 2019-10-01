class BasicHandler(object):
    '''
    Handler class that can be used as a parent class for observers on the
    EventSource. This class allows setting claims to function in order to
    dispatch different message types to their desired methods on the class.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        self.__claims = {}

    def handle(self, source, message):
        '''
        Checks, if a claim exists for the given message. If this is the case,
        it is forwarded to the specific funtion defined.

        @param source: The event source.
        @param message: The message being received.
        '''
        if message.typeId in self.__claims:
            self.__claims[message.typeId](source, message)

    def _setClaim(self, typeId, function):
        '''
        Registers a claim for a specific message typeId.

        @param typeId: The typeId to claim.
        @param function: The callback receiving the message.
        '''
        self.__claims[typeId] = function
