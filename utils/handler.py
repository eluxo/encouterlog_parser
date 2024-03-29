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

from messages import MESSAGE_TYPE as MessageType

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

        if MessageType.UNKNOWN in self.__claims:
            self.__claims[MessageType.UNKNOWN](source, message)

    def _setClaim(self, typeId, function):
        '''
        Registers a claim for a specific message typeId.

        @param typeId: The typeId to claim.
        @param function: The callback receiving the message.
        '''
        self.__claims[typeId] = function
