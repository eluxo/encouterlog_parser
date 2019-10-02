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
