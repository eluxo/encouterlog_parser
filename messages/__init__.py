#!/usr/bin/env python2.7
# encoding: utf-8

class Message(object):
    def __init__(self, row, srcUnitIndex = None, dstUnitIndex = None):
        self.time = int(row[0])
        self.type = Message.getTypeFromRow(row)
        self.typeId = MESSAGE_TYPE_MAP[self.type][0]
        self.row = row

        self.srcUnit = None
        if srcUnitIndex:
            srcUnit = UnitStats(row, srcUnitIndex)
            if srcUnit.unitId:
                self.srcUnit = srcUnit
        
        self.dstUnit = None
        if dstUnitIndex:
            dstUnit = UnitStats(row, dstUnitIndex)
            if dstUnit.unitId:
                self.dstUnit = dstUnit

    def parseResource(self, value):
        return [int(x) for x in value.split('/')]

    @staticmethod
    def getTypeFromRow(row):
        return row[1]

class Position(object):
    def __init__(self, row, i):
        self.position = [float(x) for x in row[i:i+3]]

class UnitStats(object):
    def __init__(self, row, i):
        self.unitId = row[i]
        if self.unitId == '*':
            self.unitId = None
            return

        self.unitId = int(self.unitId)
        self.currentHp,   self.maxHp =   self.parseResource(row[i + 1])
        self.currentMag,  self.maxMag =  self.parseResource(row[i + 2])
        self.currentStam, self.maxStam = self.parseResource(row[i + 3])
        self.currentUlti, self.maxUlti = self.parseResource(row[i + 4])
        self.currentU2, self.maxU2 =     self.parseResource(row[i + 5]) # TODO: x/1000 value. unknown.
        self.shield = int(row[i + 6])
        self.position = Position(row, i + 7)

    def parseResource(self, value):
        return [int(x) for x in value.split('/')]
    
class BeginCombat(Message):
    def __init__(self, row):
        super(BeginCombat, self).__init__(row)

class EndCombat(Message):
    def __init__(self, row):
        super(EndCombat, self).__init__(row)

class TrialInit(Message):
    def __init__(self, row):
        super(TrialInit, self).__init__(row)
        # TODO: 2 -> 12 number of players required?
        # TODO: 3 T/F
        # TODO: 4 T/F
        # TODO: 5
        # TODO: 6
        # TODO: 7 T/F
        # TODO: 8
        # 5,TRIAL_INIT,12,F,F,0,0,F,0 (???)

class BeginTrial(Message):
    def __init__(self, row):
        super(BeginTrial, self).__init__(row)
        # TODO: 2 -> 12. seems to be the same on TrialInit.
        self.serverTime = row[3]
        # 428363,BEGIN_TRIAL,12,1568915944828

class EndLog(Message):       # COMPLETE
    def __init__(self, row):
        super(EndLog, self).__init__(row)

class BeginLog(Message):
    def __init__(self, row):
        super(BeginLog, self).__init__(row)
        self.serverTime = int(row[2])
        # TODO: 3 -> 15 ? (region code?)
        self.server = row[4]
        self.language = row[5]
        self.version = row[6]
        # 4,BEGIN_LOG,1569001784970,15,"EU Megaserver","de","eso.live.5.1"
        # 4,BEGIN_LOG,1569002720028,15,"EU Megaserver","de","eso.live.5.1"

class ZoneChanged(Message):  # COMPLETE
    def __init__(self, row): 
        super(ZoneChanged, self).__init__(row)
        self.zoneId = int(row[2]) # is this really a zone id? think so.
        self.zoneName = row[3]
        self.zoneMode = row[4] # VETERAN, NORMAL, NONE

class MapChanged(Message):   # COMPLETE
    def __init__(self, row):
        super(MapChanged, self).__init__(row)
        self.mapId = row[2]
        self.mapName = row[3]
        self.mapFile = row[4]

CLASS_ID = [
  None,
  "DK",
  "SC",
  "NB",
  "WD",
  "NC",
  "TP",
]

RACE_ID = [
  None,
  "Breton",
  "Redguard",
  "Orc",
  "Dark Elf",
  "Nord",
  "Argonian",
  "High Elf",
  "Wood Elf",
  "Khajit",
  "Imperial",
]

class UNIT_ATTITUDE:
    FRIENDLY = "FRIENDLY"
    HOSTILE = "HOSTILE"
    NEUTRAL = "NEUTRAL"
    NPC_ALLY="NPC_ALLY"
    PLAYER_ALLY="PLAYER_ALLY"

class UNIT_TYPE:
    PLAYER = "PLAYER"
    MONSTER = "MONSTER"
    OBJECT = "OBJECT"

class UnitAdded(Message):
    def __init__(self, row):
        super(UnitAdded, self).__init__(row)
        self.unitId = int(row[2])
        self.unitType = row[3]                                # -> UNIT_TYPE
        # TODO: 4? T/F
        self.playerId = int(row[5])                       # 5 -> TODO: only set for PLAYERS and counted upwards, unique by session?
        self.monsterType = int(row[6])                    # 6 -> TODO: only set for MONSTER
        # TODO: 7? T/F
        self.classId = int(row[8])                        # -> CLASS_ID array
        self.raceId = int(row[9])                         # -> RACE_ID array
        self.name = row[10]
        self.account = row[11]
        self.uuid = int(row[12])
        self.level = row[13]                              # 1-50
        self.cp = row[14]                                 # does not cap with 810
        self.parentId = int(row[14])                      # unit owning this unit
        self.attitude = row[16]                           # -> UNIT_ATTITUDE
        self.inParty = True if row[9] == "T" else False   # TODO: verify!
    
    def getName(self):
        '''
        Constructs a name for the unit based on different values of the unit.
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
        '''
        return CLASS_ID[self.classId]
    
    def getRaceName(self):
        '''
        Getter for the name of the race.
        '''
        return RACE_ID[self.raceId]
        
class UnitRemoved(Message):
    def __init__(self, row):
        super(UnitRemoved, self).__init__(row)
        self.unitId = int(row[2])

class AbilityInfo(Message):
    def __init__(self, row):
        super(AbilityInfo, self).__init__(row)
        self.abilityId = int(row[2])
        self.name = row[3]
        self.icon = row[4]
        # TODO: 5? T/F
        # TODO: 6? T/F

class INTERRUPT_STATUS:
    COMPLETED = "COMPLETED"
    PLAYER_CANCELLED = "PLAYER_CANCELLED"
    INTERRUPTED = "INTERRUPTED"

class EndCast(Message):
    def __init__(self, row):
        super(EndCast, self).__init__(row)
        self.interruptStatus = row[2] # -> INTERRUPT_STATUS
        self.abilityId = row[3]       # -> AbilityInfo.abilityId
        self.castId = row[4]          # -> BeginCast.castId

class EffectInfo(Message):
    def __init__(self, row):
        super(EffectInfo, self).__init__(row)
        self.abilityId = int(row[2]) # -> AbilityInfo -> AbilityId
        self.effectCategory = row[3] # BUFF, DEBUFF
        self.effectType = row[4]     # BLEED, DISEASE, MAGIC, NONE, POISON, SNARE
        # 5
        #1580769,EFFECT_INFO,57477,BUFF,NONE,F
        #1582683,EFFECT_INFO,36598,BUFF,NONE,T
        #503821,EFFECT_INFO,26874,BUFF,NONE,T,26832

class BeginCast(Message):
    def __init__(self, row):
        super(BeginCast, self).__init__(row, 6, 16)
        #0    1          2 3 4       5     6 7           8           9           10      11     12    13     14     15     16
        #1881,BEGIN_CAST,0,F,3168224,22262,1,40844/40844,18456/23025,24003/24003,449/500,0/1000,13233,0.2462,0.3413,0.3551,*
        #6047995,BEGIN_CAST,0,F,21621932,15435,119,32917/32917,10749/10749,15603/15603,500/500,0/1000,0,0.2921,0.4455,1.4435,0,0/0,0/0,0/0,0/0,0/0,0,0.0000,0.0000,0.0000
        # 2
        # 3
        self.castId = int(row[4])
        self.abilityId = int(row[5])

class EffectChanged(Message):
    def __init__(self, row):
        super(EffectChanged, self).__init__(row, 6, 16)
        self.changeType = row[2] # GAINED, FADED, UPDATED
        # 3 # self.unitId = int(row[3]) # the one casting or the one receiving? guess the first.
        #0    1              2      3 4       5   6 7           8           9           10      11     12    13     14     15     16
        #4215,EFFECT_CHANGED,GAINED,1,2759103,973,1,40844/40844,20505/23025,21717/24003,449/500,0/1000,26902,0.5177,0.8850,5.9674,*
        # same as in BeginCast
        self.castId = row[4]    # -> BeginCast.castId
        self.abilityId = row[5] # -> AbilityInfo.abilityId

class HealthRegen(Message):
    def __init__(self, row):
        super(HealthRegen, self).__init__(row)
        # 2 (amount?)
        self.sourceUnit = UnitStats(row, 3)

class EVENT_TYPE:
    ABILITY_ON_COOLDOWN = "ABILITY_ON_COOLDOWN"
    BAD_TARGET = "BAD_TARGET"
    BLOCKED_DAMAGE = "BLOCKED_DAMAGE"
    BUSY = "BUSY"
    CANNOT_USE = "CANNOT_USE"
    CANT_SEE_TARGET = "CANT_SEE_TARGET"
    CASTER_DEAD = "CASTER_DEAD"
    CRITICAL_DAMAGE = "CRITICAL_DAMAGE"
    CRITICAL_HEAL = "CRITICAL_HEAL"
    DAMAGE = "DAMAGE"
    DAMAGE_SHIELDED = "DAMAGE_SHIELDED"
    DIED = "DIED"
    DIED_XP = "DIED_XP"
    DODGED = "DODGED"
    DOT_TICK = "DOT_TICK"
    DOT_TICK_CRITICAL = "DOT_TICK_CRITICAL"
    FAILED = "FAILED"
    FAILED_REQUIREMENTS = "FAILED_REQUIREMENTS"
    FALL_DAMAGE = "FALL_DAMAGE"
    HEAL = "HEAL"
    HEAL_ABSORBED = "HEAL_ABSORBED"
    HOT_TICK = "HOT_TICK"
    HOT_TICK_CRITICAL = "HOT_TICK_CRITICAL"
    IMMUNE = "IMMUNE"
    INSUFFICIENT_RESOURCE = "INSUFFICIENT_RESOURCE"
    INTERRUPT = "INTERRUPT"
    IN_AIR = "IN_AIR"
    KILLING_BLOW = "KILLING_BLOW"
    KNOCKBACK = "KNOCKBACK"
    LINKED_CAST = "LINKED_CAST"
    MISSING_EMPTY_SOUL_GEM = "MISSING_EMPTY_SOUL_GEM"
    OFFBALANCE = "OFFBALANCE"
    POWER_DRAIN = "POWER_DRAIN"
    POWER_ENERGIZE = "POWER_ENERGIZE"
    QUEUED = "QUEUED"
    REFLECTED = "REFLECTED"
    REINCARNATING = "REINCARNATING"
    SNARED = "SNARED"
    SOUL_GEM_RESURRECTION_ACCEPTED = "SOUL_GEM_RESURRECTION_ACCEPTED"
    SPRINTING = "SPRINTING"
    STAGGERED = "STAGGERED"
    STUNNED = "STUNNED"
    TARGET_DEAD = "TARGET_DEAD"
    TARGET_NOT_IN_VIEW = "TARGET_NOT_IN_VIEW"
    TARGET_OUT_OF_RANGE = "TARGET_OUT_OF_RANGE"
    TARGET_TOO_CLOSE = "TARGET_TOO_CLOSE"

class EVENT_ELEMENT:
    COLD = "COLD"
    DISEASE = "DISEASE"
    FIRE = "FIRE"
    GENERIC = "GENERIC"
    INVALID = "INVALID"
    MAGIC = "MAGIC"
    NONE = "NONE"
    OBLIVION = "OBLIVION"
    PHYSICAL = "PHYSICAL"
    POISON = "POISON"
    SHOCK = "SHOCK"

class EventResource:
    INVALID = "INVALID"
    MAGICKA = "MAGICKA"
    MOUNT_STAMINA = "MOUNT_STAMINA"
    STAMINA = "STAMINA"
    ULTIMATE = "ULTIMATE"

class CombatEvent(Message):
    def __init__(self, row):
        super(CombatEvent, self).__init__(row, 9, 19)
        self.eventType = row[2]          # -> EVENT_TYPE
        self.element = row[3]            # -> EVENT_ELEMENT
        self.resource = row[4]           # -> EVENT_RESOURCE INVALID,MAGICKA,STAMINA,ULTIMATE,MOUNT_STAMINA
        self.damage = int(row[5])        # amount of damage?
        self.heal = int(row[6])          # amount of heal?
        
        self.castId = int(row[7])
        self.abilityId = int(row[8]) #4103177,38250,
        
        #4447,COMBAT_EVENT,POWER_DRAIN,GENERIC,STAMINA,479,0,4100939,15356,4,18748/18748,34198/34198,11552/12031,255/500,0/1000,0,0.6274,0.4590,1.6218,*
        #4781,COMBAT_EVENT,HEAL,GENERIC,MAGICKA,0,1828,4100988,88988,4,18748/18748,34198/34198,11552/12031,255/500,0/1000,0,0.6253,0.4599,1.9407,*
        # time type         eventType            res     dmg  ? castId  abId  pId   hp         mag          stam   ??       ??       ....              target    targetHp        .....             targetPos                             
        #5248,COMBAT_EVENT,CRITICAL_DAMAGE,FIRE,MAGICKA,5212,0,7957275,16165,1,11017/11017,31922/31922,9867/9867,66/500,0/1000,0,0.5085,0.4377,4.7704,268435457,3002289/3007501,0/0,0/0,0/0,0/0,0,0.5167,0.4375,-1.3146

class UnitChanged(Message):
    def __init__(self, row):
        super(UnitChanged, self).__init__(row)
        self.unitId = row[2] # unsure
        # 2
        # 3
        self.unitName = row[4]
        self.unitAccount = row[5]
        # 4
        self.unitLevel = row[5]
        self.unitCP = row[6]
        # 7
        self.unitAttitude = row[8]
        self.inParty = True if row[9] == "T" else False # verify?
        
        #484573,UNIT_CHANGED,245,0,0,"Skelett-Schütze","",0,50,160,0,HOSTILE,F
        #522730,UNIT_CHANGED,643,0,0,"Skelett-Schütze","",0,50,160,0,HOSTILE,F
        #551112,UNIT_CHANGED,927,0,0,"Frostbrunnen","",0,50,160,0,HOSTILE,F
        #554326,UNIT_CHANGED,924,0,0,"Nachstellender Sprengknochen","",0,50,160,0,HOSTILE,F

class PlayerInfo(Message):
    def __init__(self, row):
        super(PlayerInfo, self).__init__(row)
        row = self.__insert(row)
        self.unitId = row[2]         # -> UnitAdded.unitId
        self.passives = row[3]       # contains active effects (TODO: passives?)
        self.passivesMask = row[4]   # TODO: not completely sure, but this seems to be a mask for the effects
        self.currentGear = row[5]    # contains arrays of gear information. should have a class for this.
        self.bars = (row[6], row[7]) # ability bars -> AbilityInfo.abilityId
        # print "%4d [ %s ] [ %s ]" % (self.unitId, " ".join(["%6d" % x for x in self.bars[0]]), " ".join(["%6d" % x for x in self.bars[1]]))

    def __insert(self, entries):
        stack = [[],]
        while len(entries) > 0:
            value = entries.pop(0)
            while value.startswith("["):
                stack.append([])
                value = value[1:]
            
            upstack = 0
            while value.endswith("]"):
                upstack += 1
                value = value[:-1]
            
            if len(value) > 0:
                try:
                    value = int(value)
                except:
                    pass
                stack[-1].append(value)

            for i in range(upstack):
                sublist = stack.pop(-1)
                stack[-1].append(sublist)
        return stack[0]

class MESSAGE_TYPE:
    PLAYER_INFO =     0
    COMBAT_EVENT =    1
    END_LOG =         2
    BEGIN_LOG =       3
    UNIT_REMOVED =    4
    BEGIN_COMBAT =    5
    TRIAL_INIT =      6
    END_COMBAT =      7
    BEGIN_CAST =      8
    END_CAST =        9  
    MAP_CHANGED =    10
    EFFECT_CHANGED = 11
    BEGIN_TRIAL =    12
    UNIT_ADDED =     13
    ABILITY_INFO =   14
    UNIT_CHANGED =   15
    HEALTH_REGEN =   16
    EFFECT_INFO =    17
    ZONE_CHANGED =   18
                                   
MESSAGE_TYPE_MAP = {
    'PLAYER_INFO':    (MESSAGE_TYPE.PLAYER_INFO,    PlayerInfo),
    'COMBAT_EVENT':   (MESSAGE_TYPE.COMBAT_EVENT,   CombatEvent),
    'END_LOG':        (MESSAGE_TYPE.END_LOG,        EndLog),
    'BEGIN_LOG':      (MESSAGE_TYPE.BEGIN_LOG,      BeginLog),
    'UNIT_REMOVED':   (MESSAGE_TYPE.UNIT_REMOVED,   UnitRemoved),
    'BEGIN_COMBAT':   (MESSAGE_TYPE.BEGIN_COMBAT,   BeginCombat),
    'TRIAL_INIT':     (MESSAGE_TYPE.TRIAL_INIT,     TrialInit),
    'END_COMBAT':     (MESSAGE_TYPE.END_COMBAT,     EndCombat),
    'BEGIN_CAST':     (MESSAGE_TYPE.BEGIN_CAST,     BeginCast),
    'END_CAST':       (MESSAGE_TYPE.END_CAST,       EndCast),
    'MAP_CHANGED':    (MESSAGE_TYPE.MAP_CHANGED,    MapChanged),
    'EFFECT_CHANGED': (MESSAGE_TYPE.EFFECT_CHANGED, EffectChanged),
    'BEGIN_TRIAL':    (MESSAGE_TYPE.BEGIN_TRIAL,    BeginTrial),
    'UNIT_ADDED':     (MESSAGE_TYPE.UNIT_ADDED,     UnitAdded),
    'ABILITY_INFO':   (MESSAGE_TYPE.ABILITY_INFO,   AbilityInfo),
    'UNIT_CHANGED':   (MESSAGE_TYPE.UNIT_CHANGED,   UnitChanged),
    'HEALTH_REGEN':   (MESSAGE_TYPE.HEALTH_REGEN,   HealthRegen),
    'EFFECT_INFO':    (MESSAGE_TYPE.EFFECT_INFO,    EffectInfo),
    'ZONE_CHANGED':   (MESSAGE_TYPE.ZONE_CHANGED,   ZoneChanged),
}

class MessageFactory(object):
    def __init__(self):
        pass
    
    def create(self, row):
        if len(row) < 2:
            return None
        rowType = Message.getTypeFromRow(row)
        return MESSAGE_TYPE_MAP[rowType][1](row)


'''
Combat Events:
ABILITY_ON_COOLDOWN
BAD_TARGET
BLOCKED_DAMAGE
BUSY
CANNOT_USE
CANT_SEE_TARGET
CASTER_DEAD
CRITICAL_DAMAGE
CRITICAL_HEAL
DAMAGE
DAMAGE_SHIELDED
DIED
DIED_XP
DODGED
DOT_TICK
DOT_TICK_CRITICAL
FAILED
FAILED_REQUIREMENTS
FALL_DAMAGE
HEAL
HEAL_ABSORBED
HOT_TICK
HOT_TICK_CRITICAL
IMMUNE
INSUFFICIENT_RESOURCE
INTERRUPT
IN_AIR
KILLING_BLOW
KNOCKBACK
LINKED_CAST
MISSING_EMPTY_SOUL_GEM
OFFBALANCE
POWER_DRAIN
POWER_ENERGIZE
QUEUED
REFLECTED
REINCARNATING
SNARED
SOUL_GEM_RESURRECTION_ACCEPTED
SPRINTING
STAGGERED
STUNNED
TARGET_DEAD
TARGET_NOT_IN_VIEW
TARGET_OUT_OF_RANGE
TARGET_TOO_CLOSE
'''

# time type         eventType            res     dmg  ? castId  abId  pId   hp         mag          stam   ??       ??       ....              target    targetHp        .....             targetPos                             
# 5248,COMBAT_EVENT,CRITICAL_DAMAGE,FIRE,MAGICKA,5212,0,7957275,16165,1,11017/11017,31922/31922,9867/9867,66/500,0/1000,0,0.5085,0.4377,4.7704,268435457,3002289/3007501,0/0,0/0,0/0,0/0,0,0.5167,0.4375,-1.3146
