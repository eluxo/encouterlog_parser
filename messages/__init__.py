#!/usr/bin/env python2.7
# encoding: utf-8

class Message(object):
    '''
    Base class for all the messages in the log.
    
    This holds the different fields and subobjects shared by all messages.
    
    All messages have a timestamp and a type of the message. Some messages also
    contain a source and destination unit of the effect or ability.
    '''
    def __init__(self, row, srcUnitIndex = None, dstUnitIndex = None):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        @param srcUnitIndex: Optional. If the message may contain a source
            unit, this defines the index of the first value of it.
        @param dstUnitIndex: Optional. If the message may contain a destination
            unit, this defines the index of the first value of it.
        '''
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

    @staticmethod
    def getTypeFromRow(row):
        '''
        Reads the object type from the row.
        
        @param row: The row to read the type from.
        @return: Type value from the data row.
        '''
        return row[1]

class Position(object):
    '''
    Position class.
    
    This class holds the units position on the map.
    '''
    def __init__(self, row, i):
        self.position = [float(x) for x in row[i:i+3]]  # TODO: not completely sure about the third value

class UnitStats(object):
    '''
    Class holding all stat attributes of a single unit.
    
    This is a part of most of the messages in the log and allows keeping track
    of the current status of the unit.
    '''
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
        '''
        Parses a resource value.
        
        @param value: The resource value.
        @return: The parsed resource values.
        '''
        return [int(x) for x in value.split('/')]
    
class BeginCombat(Message):
    '''
    Marks the begin of a combat.
    '''
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(BeginCombat, self).__init__(row)

class EndCombat(Message):
    '''
    Marks the end of a combat.
    '''
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(EndCombat, self).__init__(row)

class TrialInit(Message):
    '''
    Initialization message for a trial. This is added when a trial is entered.
    '''

    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
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
    '''
    Start of the trial.
    
    This is added when the trial timers start.
    '''

    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(BeginTrial, self).__init__(row)
        # TODO: 2 -> 12. seems to be the same on TrialInit.
        self.serverTime = row[3]
        # 428363,BEGIN_TRIAL,12,1568915944828

class EndLog(Message):
    '''
    The END_LOG message marks the end of a single encouterlog. This allows to
    have multiple logs within a single file.
    '''

    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
        super(EndLog, self).__init__(row)

class BeginLog(Message):
    '''
    The BEGIN_LOG marker sets the beginning of an encouterlog. The entry always
    holds an absolute timestamp to allow referencing from the relative time
    values to an absolute server time.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
        super(BeginLog, self).__init__(row)
        self.serverTime = int(row[2])
        # TODO: 3 -> 15 ? (region code?)
        self.server = row[4]
        self.language = row[5]
        self.version = row[6]
        # 4,BEGIN_LOG,1569001784970,15,"EU Megaserver","de","eso.live.5.1"
        # 4,BEGIN_LOG,1569002720028,15,"EU Megaserver","de","eso.live.5.1"

class ZoneChanged(Message):
    '''
    Marks the change of a zone where the logging player is currently located.
    '''
    
    def __init__(self, row): 
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
        super(ZoneChanged, self).__init__(row)
        self.zoneId = int(row[2]) # is this really a zone id? think so.
        self.zoneName = row[3]
        self.zoneMode = row[4] # VETERAN, NORMAL, NONE

class MapChanged(Message):
    '''
    Communicates the map whenever the player enters a location on a different
    map.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
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
    '''
    Called whenever a new unit is added to the log.
    
    Units are players, monsters, NPCs or objects that are in the range of the
    player.
    
    All units that appear in the players range are always added to the log
    including the player and all the allies. So this allows keeping track of
    all the entities that exist during fights or interactions.
    
    Each unit that is removed from the scenery will cause a UNIT_REMOVED
    message. As far as I can tell, this is stable and every unit is always
    removed when it disappears from the players scenery.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
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
        return CLASS_ID[self.classId]
    
    def getRaceName(self):
        '''
        Getter for the name of the race.
        
        @return: Race name of the entity. Only useful on players.
        '''
        return RACE_ID[self.raceId]

    def isPlayer(self):
        '''
        Returns true, if unit is a player character.
        '''
        return self.unitType == "PLAYER"
        
class UnitRemoved(Message):
    '''
    Every unit that gets added to the log will be removed from the log at some
    point by a UNIT_REMOVED message.
    '''

    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
        super(UnitRemoved, self).__init__(row)
        self.unitId = int(row[2])

class AbilityInfo(Message):
    '''
    Abilities are defined using an AbilityInfo message. This message defines
    the name and the icon of the ability.
    
    Each ability is not bound to a unit until it is mentioned in a former
    message.
    
    Abilities can reappear but their abilityId is bound to a unit. A different
    unit having the same ability slotted might cause a new AbilityInfo of the
    same ability with a different abilityId value.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
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
    '''
    Marks the end of a cast event.
    
    The end of a cast event contains information about the outcome of the cast
    telling more about the time the cast actually took and if it has been
    completed or interrupted.
    '''

    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
        super(EndCast, self).__init__(row)
        self.interruptStatus = row[2] # -> INTERRUPT_STATUS
        self.abilityId = row[3]       # -> AbilityInfo.abilityId
        self.castId = row[4]          # -> BeginCast.castId

class EFFECT_CATEGORY:
    BUFF = "BUFF"
    DEBUFF = "DEBUFF"

class EFFECT_TYPE:
    BLEED = "BLEED"
    DISEASE = "DISEASE"
    MAGIC = "MAGIC"
    NONE = "NONE"
    POISON = "POISON"
    SNARE = "SNARE"

class EffectInfo(Message):
    '''
    Buffs and debuffs are called effects in the log.
    
    EFFECT_INFO messages mark the beginning of effects binding them to an
    ability using an ID.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
        super(EffectInfo, self).__init__(row)
        self.abilityId = int(row[2]) # -> AbilityInfo -> AbilityId
        self.effectCategory = row[3] # -> EFFECT_CATEGORY
        self.effectType = row[4]     # -> EFFECT_TYPE
        # TODO: 5
        # TODO: 6 (optional)
        #1580769,EFFECT_INFO,57477,BUFF,NONE,F
        #1582683,EFFECT_INFO,36598,BUFF,NONE,T
        #503821,EFFECT_INFO,26874,BUFF,NONE,T,26832

class BeginCast(Message):
    '''
    Marks the begin of a cast.
    
    A cast is the use of an active ability carried out by a unit.

    The cast may effect the unit itself or a different unit. If it only effects
    the casting unit, the messages dstUnit field will be None.
    
    The srcUnit field is always set to Unit data.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
        super(BeginCast, self).__init__(row, 6, 16)
        #0    1          2 3 4       5     6 7           8           9           10      11     12    13     14     15     16
        #1881,BEGIN_CAST,0,F,3168224,22262,1,40844/40844,18456/23025,24003/24003,449/500,0/1000,13233,0.2462,0.3413,0.3551,*
        #6047995,BEGIN_CAST,0,F,21621932,15435,119,32917/32917,10749/10749,15603/15603,500/500,0/1000,0,0.2921,0.4455,1.4435,0,0/0,0/0,0/0,0/0,0/0,0,0.0000,0.0000,0.0000
        # TODO: 2
        # TODO: 3
        self.castId = int(row[4])
        self.abilityId = int(row[5])

class EFFECT_CHANGE:
    GAINED = "GAINED"
    FADED = "FADED"
    UPDATED = "UPDATED"

class EffectChanged(Message):
    '''
    Effects might change over time.
    
    Everytime an effect gets updated, an EFFECT_CHANGED message is created.
    
    As BeginCast, this can have a srcUnit and dstUnit value.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
        super(EffectChanged, self).__init__(row, 6, 16)
        self.change = row[2] # -> EFFECT_CHANGE
        # 3 # self.unitId = int(row[3]) # TODO: the one casting or the one receiving? guess the first.
        #0    1              2      3 4       5   6 7           8           9           10      11     12    13     14     15     16
        #4215,EFFECT_CHANGED,GAINED,1,2759103,973,1,40844/40844,20505/23025,21717/24003,449/500,0/1000,26902,0.5177,0.8850,5.9674,*
        self.castId = row[4]    # -> BeginCast.castId
        self.abilityId = row[5] # -> AbilityInfo.abilityId

class HealthRegen(Message):
    '''
    HEALTH_REGEN messages mark events caused due to health reg values.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
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

class EVENT_RESOURCE:
    INVALID = "INVALID"
    MAGICKA = "MAGICKA"
    MOUNT_STAMINA = "MOUNT_STAMINA"
    STAMINA = "STAMINA"
    ULTIMATE = "ULTIMATE"

class CombatEvent(Message):
    '''
    COMBAT_EVENT messages identify each combat event.
    
    They hold information about damage cause, resources restored, ... basically
    every atomic information that essentially defines a fight.
    
    The COMBAT_EVENT always holds the details of the casting unit. It also
    identifies the target unit, if the event can be associated with one.
    
    Note: Splitting all of the events will be some serious work.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
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
    '''
    Each unit has a specific configuration when it is created. This
    configuration might change, as a unit also carries an attitude towards us
    and our group.
    
    If we (for example) attack a neutral unit, it might disliking us or even
    try to kill us. At that point, it switches from neutral to hostile.
    
    The UNIT_CHANGE messages are used to reflect this change.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
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
    '''
    Details about a player.
    
    This contains information about a players passive abilities, active
    abilities slottet and a complete definition of the players gear.
    
    There is a lot of stuff in here that still needs to be stripped
    apart and this is the location where gear IDs are used that are not
    a part of the log itself.
    '''
    
    def __init__(self, row):
        '''
        Constructor.
        
        @param row: The row of CSV data.
        '''
        super(TrialInit, self).__init__(row)
        super(PlayerInfo, self).__init__(row)
        row = self.__insert(row)
        self.unitId = row[2]         # -> UnitAdded.unitId
        self.passives = row[3]       # contains active effects (TODO: passives?)
        self.passivesMask = row[4]   # TODO: not completely sure, but this seems to be a mask for the effects
        self.currentGear = row[5]    # contains arrays of gear information. should have a class for this.
        self.bars = (row[6], row[7]) # ability bars -> AbilityInfo.abilityId
        # print "%4d [ %s ] [ %s ]" % (self.unitId, " ".join(["%6d" % x for x in self.bars[0]]), " ".join(["%6d" % x for x in self.bars[1]]))

    def __insert(self, entries):
        '''
        Makes trees out of horizontal lines.
        
        Might still need some fairydust, but believe me: Unicorns are happily
        living here.
        
        @param entries: The row of data to be parse.
        @return: Nice tree structure that allows easier access.
        '''
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
    '''
    Everthing should end with a factory.
    
    This one creates messages out of raw data.
    '''
    def __init__(self):
        pass
    
    def create(self, row):
        '''
        Creates a message based on the given row of CSV data.
        '''
        if len(row) < 2:
            return None
        rowType = Message.getTypeFromRow(row)
        return MESSAGE_TYPE_MAP[rowType][1](row)
