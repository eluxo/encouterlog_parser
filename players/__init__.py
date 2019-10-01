#!/usr/bin/env python3
# encoding: utf-8

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



