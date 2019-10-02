#!/usr/bin/env python3
# encoding: utf-8

import time

from messages import MESSAGE_TYPE as MessageType
from messages import EVENT_TYPE as EventType
from messages import EVENT_ELEMENT as EventElement
from messages import EVENT_RESOURCE as EventResource

from utils.handler import BasicHandler

class Combat:
    '''
    Class representing a single combat including the DPS counts.
    '''

    def __init__(self, combatStart = 0):
        '''
        Constructor.

        @param combatStart: Start time for the combat.
        '''
        self.combatStart = combatStart
        self.combatEnd = 0
        self.timestamp = 0

class DamageTracker(BasicHandler):
    '''
    Class tracking damage events and suming up the damage caused based on the
    source and the target in a fight.
    '''

    DAMAGE_EVENTS = [
        EventType.CRITICAL_DAMAGE,
        EventType.DAMAGE,
        EventType.DAMAGE_SHIELDED,
        EventType.DOT_TICK,
        EventType.DOT_TICK_CRITICAL,
    ]

    HEAL_EVENTS = [
        EventType.CRITICAL_HEAL,
        EventType.HEAL,
        EventType.HOT_TICK,
        EventType.HOT_TICK_CRITICAL,
    ]

    def __init__(self):
        '''
        Constructor.
        '''
        super(DamageTracker, self).__init__()
        self._setClaim(MessageType.COMBAT_EVENT, self.__combatEvent)
        self._setClaim(MessageType.BEGIN_COMBAT, self.__beginCombat)
        self._setClaim(MessageType.END_COMBAT, self.__endCombat)
        self.__combats = []

    def __combatEvent(self, source, combatEvent):
        '''
        Method receiving all the combat event messages.

        @param source: The event source.
        @param combatEvent: The combat event.
        '''
        if len(self.__combats) == 0:
            return

        if self.__combats[-1].combatEnd != 0:
            return

        clock = source.clock
        self.__combats[-1].timestamp = clock.getGameClock()

        if combatEvent.eventType in [ EventType.POWER_DRAIN, EventType.POWER_ENERGIZE ]:
            return

        if not combatEvent.eventType in self.DAMAGE_EVENTS:
            if combatEvent.damage != 0:
                print("event: %s" % ",".join(combatEvent.row))

    def __beginCombat(self, source, beginCombat):
        '''
        Called on the start of a combat.

        @param source: The event source.
        @param beginCombat: Begin message for the combat.
        '''
        clock = source.clock
        combat = Combat(clock.getCombatStart())
        self.__combats.append(combat)

    def __endCombat(self, source, endCombat):
        '''
        Called on the end of a combat.

        @param source: The event source.
        @param endCombat: End message for the combat.
        '''
        clock = source.clock
        self.__combats[-1].combatEnd = clock.getCombatEnd()

    def __resolveChildUnit(self, database, unit):
        '''
        Recursively resolves the parent resource for a child unit.

        Units may have pets. The pets damage is always associated with the pet.

        As we want to associate the damage of a pat with its parent, we define
        a method to resolve the pets parent.

        As it it plausible that a monster may spawn adds that spawn own pets,
        we try to recursively resolve the parent, until the monster does not
        have a parent anymore.

        @param database: The database storing all the units.
        @param unit: The unit to resolve.
        '''
        rc = unit
        while rc.parentId != 0:
            rc = database.units.get(rc.parentId)
        return rc

