#!/usr/bin/env python3
# encoding: utf-8

from utils.handler import BasicHandler as BasicRegistry
from messages import MESSAGE_TYPE as MessageType

class EffectRegistry(BasicRegistry):
    '''
    Database storing all effects.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        super(EffectRegistry, self).__init__()
        self._setClaim(MessageType.EFFECT_INFO, self.__effectInfo)
        self.__effects = {}

    def __effectInfo(self, source, effectInfo):
        '''
        Adds an effect to the registry.

        @param source: The event source causing the message.
        @param effectInfo: The effect to be added.
        '''
        self.__effects[effectInfo.abilityId] = effectInfo
