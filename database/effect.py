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
