#!/usr/bin/env python3
# encoding: utf-8

from utils.handler import BasicHandler as BasicRegistry
from messages import MESSAGE_TYPE as MessageType

class AbilityRegistry(BasicRegistry):
    '''
    Database holding all abilities including their IDs.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        super(AbilityRegistry, self).__init__()
        self._setClaim(MessageType.ABILITY_INFO, self.__abilityInfo)
        self.__abilities = {}

    def __abilityInfo(self, source, abilityInfo):
        '''
        Handles ABILITY_INFO messages and makes sure that the associated
        abilities are added to the database.

        @param source: The event source causing the message.
        @param abilityInfo: The ability info object.
        '''
        self.__abilities[abilityInfo.abilityId] = abilityInfo
