#!/usr/bin/env python2.7
# encoding: utf-8

from messages import MESSAGE_TYPE as MessageType

class BasicRegistry(object):
    '''
    Base class for all registries providing a common interface for message
    distribution.
    '''
    
    def __init__(self):
        '''
        Constructor.
        '''
        self.__claims = {}
    
    def handle(self, message):
        '''
        Checks, if a claim exists for the given message. If this is the case,
        it is forwarded to the specific funtion defined.
        
        @param message: The message being received.
        '''
        if message.typeId in self.__claims:
            self.__claims[message.typeId](message)
    
    def _setClaim(self, typeId, function):
        '''
        Registers a claim for a specific message typeId.
        
        @param typeId: The typeId to claim.
        @param function: The callback receiving the message.
        '''
        self.__claims[typeId] = function

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
        self.__units = {}
    
    def __unitAdded(self, unitAdded):
        '''
        Adds the unit to the registry.
        
        @param unitAdded: The adding message.
        '''
        self.__units[unitAdded.unitId] = unitAdded
        print "adding unit %d %s %s" % (unitAdded.unitId, unitAdded.name, unitAdded.account)
    
    def __unitRemoved(self, unitRemoved):
        '''
        Removes the unit from the registry.
        
        @param unitRemoved: The removal message.
        '''
        unit = self.__units[unitRemoved.unitId]
        print "removing unit %d %s %s" % (unit.unitId, unit.name, unit.account)
        self.__units[unitRemoved.unitId] = None
        del self.__units[unitRemoved.unitId]

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
    
    def __abilityInfo(self, abilityInfo):
        '''
        Handles ABILITY_INFO messages and makes sure that the associated
        abilities are added to the database.
        '''
        self.__abilities[abilityInfo.abilityId] = abilityInfo
        print "adding ability %d %s" % (abilityInfo.abilityId, abilityInfo.name)

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
    
    def __effectInfo(self, effectInfo):
        '''
        Adds an effect to the registry.
        
        @param effectInfo: The effect to be added.
        '''
        self.__effects[effectInfo.effectId] = effectInfo
        print "adding effect %d %s" % (effectInfo.effectId, effectInfo.effectType)

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
    
    def handle(self, message):
        '''
        Forwards the received message to the different registries in order to
        let them handle the contained information.
        '''
        for registry in self.__registries:
            registry.handle(message)





        