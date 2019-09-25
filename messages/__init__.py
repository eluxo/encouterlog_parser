#!/usr/bin/env python2.7
# encoding: utf-8

class Message(object):
    def __init__(self, row, srcUnitIndex = None, dstUnitIndex = None):
        self.time = int(row[0])
        self.type = Message.getTypeFromRow(row)
        self.row = row

        if srcUnitIndex:
            self.srcUnit = UnitStats(row, srcUnitIndex)
        else:
            self.srcUnit = None
        
        if dstUnitIndex:
            self.dstUnit = UnitStats(row, dstUnitIndex)
        else:
            self.dstUnit = None

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
        self.currentU2, self.maxU2 =     self.parseResource(row[i + 5]) # UNKNOWN
        self.shield = int(row[i + 6])
        self.position = Position(row, i + 7)

    def parseResource(self, value):
        return [int(x) for x in value.split('/')]
    
class BeginCombat(Message):   # COMPLETE
    def __init__(self, row):
        super(BeginCombat, self).__init__(row)

class EndCombat(Message):    # COMPLETE
    def __init__(self, row):
        super(EndCombat, self).__init__(row)

class TrialInit(Message):
    def __init__(self, row):
        super(TrialInit, self).__init__(row)
        # 5,TRIAL_INIT,12,F,F,0,0,F,0

class BeginTrial(Message):
    def __init__(self, row):
        super(BeginTrial, self).__init__(row)
        # 2
        self.serverTime = row[3]
        # 428363,BEGIN_TRIAL,12,1568915944828

class EndLog(Message):       # COMPLETE
    def __init__(self, row):
        super(EndLog, self).__init__(row)

class BeginLog(Message):
    def __init__(self, row):
        super(BeginLog, self).__init__(row)
        self.serverTime = int(row[2])
        # 3 -> 15 ? (region code?)
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
        
class UnitAdded(Message):
    def __init__(self, row):
        super(UnitAdded, self).__init__(row)
        self.unitId = int(row[2])
        self.unitType = row[3]
        # 4
        # 5
        # 6
        # 7
        # 8
        # 9
        self.unitName = row[10]
        self.unitAccount = row[11]
        # 12
        self.unitLevel = row[13]
        self.unitCP = row[14]
        # 15
        self.unitAttitude = row[16]
        self.inParty = True if row[9] == "T" else False # verify?
        #1574407,UNIT_ADDED,34,MONSTER,F,0,74123,F,0,0,"Wache des Hauses","",0,50,160,0,NEUTRAL,F
        #1574407,UNIT_ADDED,35,PLAYER,F,10,0,F,6,8,"","",0,46,0,0,PLAYER_ALLY,F
        #4,UNIT_ADDED,1,PLAYER,T,4,0,F,6,6,"","",0,50,927,0,PLAYER_ALLY,F
        #4,UNIT_ADDED,1,PLAYER,T,5,0,F,6,6,"","",0,50,927,0,PLAYER_ALLY,T
        #4,UNIT_ADDED,4,PLAYER,F,6,0,F,4,6,"","",0,50,1217,0,PLAYER_ALLY,T
        #4,UNIT_ADDED,21,PLAYER,F,7,0,F,3,8,"","",0,50,125,0,PLAYER_ALLY,T
        #5,UNIT_ADDED,19,PLAYER,F,8,0,F,3,9,"","",0,50,27,0,PLAYER_ALLY,T

class UnitRemoved(Message):  # COMPLETE
    def __init__(self, row):
        super(UnitRemoved, self).__init__(row)
        self.unitId = int(row[2])

class AbilityInfo(Message):
    def __init__(self, row):
        super(AbilityInfo, self).__init__(row)
        self.abilityId = int(row[2])
        self.abilityName = row[3]
        self.abilityIcon = row[4]
        # 5
        # 6
        #5,ABILITY_INFO,63150,"Rache","/esoui/art/icons/ability_mage_065.dds",T,T
        #5,ABILITY_INFO,61555,"Magieerosion","/esoui/art/icons/ability_weapon_016.dds",F,T
    
class EndCast(Message):
    def __init__(self, row):
        super(EndCast, self).__init__(row)
        #5665,END_CAST,COMPLETED,2827434,22182
        self.castStatus = row[2] # COMPLETED, PLAYER_CANCELLED, INTERRUPTED
        self.abilityId = row[4]
        # 5
        #6284,END_CAST,COMPLETED,3717871,28541

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

class CombatEvent(Message):
    def __init__(self, row):
        super(CombatEvent, self).__init__(row, 9, 19)
        self.eventType = row[2]          # see at the end of the file
        self.effectCategory = row[3]     # COLD,DISEASE,FIRE,GENERIC,MAGIC,NONE,OBLIVION,PHYSICAL,POISON,SHOCK
        self.effectedResource = row[4]   # INVALID,MAGICKA,STAMINA,ULTIMATE,MOUNT_STAMINA
        self.effectAmount = int(row[5])  # amount of change on target
        
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
        self.unitId = row[2]       # ->UnitAdded.unitId
        self.passives = row[3]     # contains active effects (passives?)
        self.passivesMask = row[4] # not completely sure, but this seems to be a mask for the effects
        self.currentGear = row[5]  # contains arrays of gear information
        self.frontAbilities = row[6]
        self.backAbilities = row[7]
        self.row = row
        print "%4d [ %s ] [ %s ]" % (self.unitId, " ".join(["%6d" % x for x in self.frontAbilities]), " ".join(["%6d" % x for x in self.backAbilities]))

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
            
            try:
                value = int(value)
            except:
                pass
            stack[-1].append(value)
            for i in range(upstack):
                sublist = stack.pop(-1)
                stack[-1].append(sublist)
        return stack[0]
                                   
TYPE_MAP = {
    'PLAYER_INFO': PlayerInfo,
    'COMBAT_EVENT': CombatEvent,
    'END_LOG': EndLog,
    'BEGIN_LOG': BeginLog,
    'UNIT_REMOVED': UnitRemoved,
    'BEGIN_COMBAT': BeginCombat,
    'TRIAL_INIT': TrialInit,
    'END_COMBAT': EndCombat,
    'BEGIN_CAST': BeginCast,
    'END_CAST': EndCast,
    'MAP_CHANGED': MapChanged,
    'EFFECT_CHANGED': EffectChanged,
    'BEGIN_TRIAL': BeginTrial,
    'UNIT_ADDED': UnitAdded,
    'ABILITY_INFO': AbilityInfo,
    'UNIT_CHANGED': UnitChanged,
    'HEALTH_REGEN': HealthRegen,
    'EFFECT_INFO': EffectInfo,
    'ZONE_CHANGED': ZoneChanged,
}

class MessageFactory(object):
    def __init__(self):
        pass
    
    def create(self, row):
        rowType = Message.getTypeFromRow(row)
        return TYPE_MAP[rowType](row)


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
