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

class LocationData(BasicRegistry):
    '''
    Keeps track of location and map information.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        super(LocationData, self).__init__()
        self._setClaim(MessageType.BEGIN_LOG, self.__beginLog)
        self._setClaim(MessageType.MAP_CHANGED, self.__mapChanged)
        self._setClaim(MessageType.ZONE_CHANGED, self.__zoneChanged)
        self.zoneId = None
        self.zoneName = None
        self.zoneMode = None
        self.mapId = None
        self.mapName = None
        self.mapFile = None
        self.server = None
        self.language = None
        self.version = None

    def __beginLog(self, source, beginLog):
        '''
        Called for BEGIN_LOG messages.

        @param source: The EventSource triggering the event.
        @param beginLog: The message.
        '''
        self.server = beginLog.server
        self.language = beginLog.language
        self.version = beginLog.version

    def __mapChanged(self, source, mapChanged):
        '''
        Called when the map was changed.

        @param source: The EventSource triggering the event.
        @param mapChanged: The message.
        '''
        self.mapId = mapChanged.mapId
        self.mapName = mapChanged.mapName
        self.mapFile = mapChanged.mapFile

    def __zoneChanged(self, source, zoneChanged):
        '''
        Called when the zone was changed.

        @param source: The EventSource triggering the event.
        @param zoneChanged: The message.
        '''
        self.zoneId = zoneChanged.zoneId
        self.zoneName = zoneChanged.zoneName
        self.zoneMode = zoneChanged.zoneMode

