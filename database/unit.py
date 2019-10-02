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
from messages import CLASS_ID as ClassId
from messages import RACE_ID as RaceId
from messages import UNIT_TYPE as UnitType

class UnitData(object):
    '''
    Data describing a single unit.
    '''

    def __init__(self, unitAdded = None):
        '''
        Constructor.

        @param unitAdded: Initial set of information about the unit is normally
            provided by a UNIT_ADDED message. This can be used in the
            constructor to set the initial data. If this is empty (None), an
            empty UnitData instance will be created with no further
            information.
        '''
        if not unitAdded:
            return

        self.unitStats = None
        self.playerInfo = None
        clone = [ "unitId", "unitType", "playerId", "monsterType", "classId",
                  "raceId", "name", "account", "uuid", "level", "cp",
                  "parentId", "attitude", "inParty" ]
        for attr in clone:
            setattr(self, attr, getattr(unitAdded, attr, None))

    def setStats(self, unitStats):
        '''
        Updates the current stats of the unit.

        @param unitStats: The stats to be set on the unit.
        '''
        self.unitStats = unitStats

    def setPlayerInfo(self, playerInfo):
        '''
        Updates the player information on the unit.

        @param playerInfo: The player information to be set.
        '''
        self.playerInfo = playerInfo

    def hasStats(self):
        '''
        Checks, if status information is already available on the unit.

        As this is not set when UNIT_ADDED is received, initial unit
        configurations are always without stats.

        @return: True, when stats are available for the unit.
        '''
        return not self.stats == None

    def getName(self):
        '''
        Constructs a name for the unit based on different values of the unit.

        If there is no naming information available, it will create those
        infamous Anonymus <number> entries that should match with the
        encounterlog website.

        @return: Name for the unit.
        '''
        name = ""
        if len(self.name) > 0:
            name += self.name

        if len(self.account) > 0:
            name += " [%s]" % self.account

        if len(name) == 0:
            name = "Anonymous %d" % self.unitId

        return name

    def getClassName(self):
        '''
        Getter for the name of the class.

        @return: Class name of the entity. Only useful on players.
        '''
        return ClassId[self.classId]

    def getRaceName(self):
        '''
        Getter for the name of the race.

        @return: Race name of the entity. Only useful on players.
        '''
        return RaceId[self.raceId]

    def getInfoString(self):
        '''
        Getter for the char information string.

        @return: Char information string.
        '''
        if not self.isPlayer():
            return ""
        return "%02d[%4d] %s %s" % (self.level, self.cp, self.getClassName(), self.getRaceName())

    def isPlayer(self):
        '''
        Returns true, if unit is a player character.
        '''
        return self.unitType == UnitType.PLAYER

class UnitRegistry(BasicRegistry):
    '''
    Registry for all encountered units.

    Units are added whenever a UNIT_ADDED message is received. After the unit
    has been added, it will be updated as long as it is knonw.

    As soon as the unit reveives a UNIT_REMOVED event, it is removed from the
    registry.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        super(UnitRegistry, self).__init__()
        self._setClaim(MessageType.UNIT_ADDED, self.__unitAdded)
        self._setClaim(MessageType.UNIT_REMOVED, self.__unitRemoved)
        self._setClaim(MessageType.PLAYER_INFO, self.__playerInfo)
        for entry in [MessageType.BEGIN_CAST,
                      MessageType.EFFECT_CHANGED,
                      MessageType.COMBAT_EVENT]:
            self._setClaim(entry, self.__unitMessage)
        self.__units = {}

    def __unitAdded(self, source, unitAdded):
        '''
        Adds the unit to the registry.

        @param source: The event source causing the message.
        @param unitAdded: The adding message.
        '''
        self.__units[unitAdded.unitId] = UnitData(unitAdded)

    def __unitRemoved(self, source, unitRemoved):
        '''
        Removes the unit from the registry.

        @param source: The event source causing the message.
        @param unitRemoved: The removal message.
        '''
        unit = self.__units[unitRemoved.unitId]
        self.__units[unitRemoved.unitId] = None
        del self.__units[unitRemoved.unitId]

    def __playerInfo(self, source, playerInfo):
        '''
        Receives additional player information data containing skills and
        other data about the player.

        The data will be attached to the unit.
        @param source: The event source causing the message.
        @param unitAdded: The adding message.
        '''
        if not playerInfo.unitId in self.__units:
            return
        self.__units[playerInfo.unitId].setPlayerInfo(playerInfo)

    def __unitMessage(self, source, message):
        '''
        Gets called on every message that has unit stats attached. This method
        updates the associated units.

        @param source: The event source causing the message.
        @param message: The message that has unit stats attached.
        '''
        self.__updateUnitStats(message.srcUnit)
        self.__updateUnitStats(message.dstUnit)

    def __updateUnitStats(self, unitStats):
        '''
        Updates the stats on a single unit.

        @param unitStats: The stats to be used for updating the associated
            unit.
        '''
        if not unitStats or not unitStats.unitId:
            return

        if not unitStats.unitId in self.__units:
            return

        self.__units[unitStats.unitId].setStats(unitStats)

    def get(self, unitId):
        '''
        Returns the unit for the given ID, if any with this ID exists.

        @param unitId: ID of the unit to request.
        @return: Unit with the given ID.
        '''
        if not unitId in self.__units:
            return None
        return self.__units[unitId]

    def list(self):
        '''
        Returns a list of all known units.

        @return: List of all units.
        '''
        return self.__units.values()

    def filter(self, filter):
        '''
        Returns the list of all known units based on a filter.

        @return: Filtered list of units.
        '''
        rc = []
        for unit in self.__units.values():
            if filter(unit):
                rc.append(unit)
        return rc

