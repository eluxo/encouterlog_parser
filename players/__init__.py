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

class AllyList(object):
    def __init__(self):
        self.allies = {}

    def handle(self, message):
        if message.type == "UNIT_ADDED":
            self.__unitAdded(message)
            return

        if message.type == "UNIT_REMOVED":
            self.__unitRemoved(message)
            return

        if message.srcUnit:
            self.__unitUpdate(message.srcUnit)

        if message.dstUnit:
            self.__unitUpdate(message.dstUnit)

    def __unitAdded(self, unitAdded):
        if unitAdded.unitType != "PLAYER":
            return

        if unitAdded.unitAttitude != "PLAYER_ALLY":
            return

        ally = Ally(unitAdded)
        self.allies[ally.unitId] = ally

    def __unitRemoved(self, unitRemoved):
        if unitRemoved.unitId in self.allies:
            self.allies[unitRemoved.unitId] = None
            del self.allies[unitRemoved.unitId]

    def __unitUpdate(self, unitStats):
        if not unitStats or not unitStats.unitId:
            return

        if not unitStats.unitId in self.allies:
            return

        self.allies[unitStats.unitId].update(unitStats)


class Ally(object):
    def __init__(self, unit):
        self.unitId = unit.unitId
        self.name = unit.unitName
        self.account = unit.unitAccount
        self.level = unit.unitLevel
        self.cp = unit.unitCP
        self.unitStats = None

    def update(self, unitStats):
        self.unitStats = unitStats



