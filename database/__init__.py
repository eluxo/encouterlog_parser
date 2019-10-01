#!/usr/bin/env python3
# encoding: utf-8

from database.unit import UnitRegistry
from database.ability import AbilityRegistry
from database.effect import EffectRegistry

class LogDatabase:
    '''
    Common object for all database elements. This receives and distributes the
    different log messages to all subtables.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        self.units = UnitRegistry()
        self.abilities = AbilityRegistry()
        self.effects = EffectRegistry()
        self.__registries = [ self.units, self.abilities, self.effects ]

    def handle(self, source, message):
        '''
        Forwards the received message to the different registries in order to
        let them handle the contained information.

        @param source: The source causing the message.
        @param message: The message to be handled.
        '''
        for registry in self.__registries:
            registry.handle(source, message)

