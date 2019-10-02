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

from database.unit import UnitRegistry
from database.ability import AbilityRegistry
from database.effect import EffectRegistry
from database.location import LocationData

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
        self.location = LocationData()
        self.__registries = [ self.units, self.abilities, self.effects, self.location ]

    def handle(self, source, message):
        '''
        Forwards the received message to the different registries in order to
        let them handle the contained information.

        @param source: The source causing the message.
        @param message: The message to be handled.
        '''
        for registry in self.__registries:
            registry.handle(source, message)

