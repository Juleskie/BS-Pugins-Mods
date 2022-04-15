import bs
import random
import weakref
import bsSpaz
import bsUtils
import BuddyBunny
import SnoBallz
import bsMainMenu
import bsUI
import sys

defaultPowerupInterval = 8000
coopPowerupDropRate = 3000

class PowerupMessage(object):
    """
    category: Message Classes

    Tell something to get a powerup.
    This message is normally recieved by touching
    a bs.Powerup box.
    
    Attributes:
    
       powerupType
          The type of powerup to be granted (a string). See bs.Powerup.powerupType for available type values.

       sourceNode
          The node the powerup game from, or an empty bs.Node ref otherwise.
          If a powerup is accepted, a bs.PowerupAcceptMessage should be sent
          back to the sourceNode to inform it of the fact. This will generally
          cause the powerup box to make a sound and disappear or whatnot.
    """
    def __init__(self,powerupType,sourceNode=bs.Node(None)):
        """
        Instantiate with given values.
        See bs.Powerup.powerupType for available type values.
        """
        self.powerupType = powerupType
        self.sourceNode = sourceNode

class PowerupAcceptMessage(object):
    """
    category: Message Classes

    Inform a bs.Powerup that it was accepted.
    This is generally sent in response to a bs.PowerupMessage
    to inform the box (or whoever granted it) that it can go away.
    """
    pass

class _TouchedMessage(object):
    pass

class PowerupFactory(object):
    """
    category: Game Flow Classes
    
    Wraps up media and other resources used by bs.Powerups.
    A single instance of this is shared between all powerups
    and can be retrieved via bs.Powerup.getFactory().

    Attributes:

       model
          The bs.Model of the powerup box.

       modelSimple
          A simpler bs.Model of the powerup box, for use in shadows, etc.

       texBox
          Triple-bomb powerup bs.Texture.

       texPunch
          Punch powerup bs.Texture.

       texIceBombs
          Ice bomb powerup bs.Texture.

       texStickyBombs
          Sticky bomb powerup bs.Texture.

       texShield
          Shield powerup bs.Texture.

       texImpactBombs
          Impact-bomb powerup bs.Texture.

       texHealth
          Health powerup bs.Texture.

       texLandMines
          Land-mine powerup bs.Texture.

       texCurse
          Curse powerup bs.Texture.

       healthPowerupSound
          bs.Sound played when a health powerup is accepted.

       powerupSound
          bs.Sound played when a powerup is accepted.

       powerdownSound
          bs.Sound that can be used when powerups wear off.

       powerupMaterial
          bs.Material applied to powerup boxes.

       powerupAcceptMaterial
          Powerups will send a bs.PowerupMessage to anything they touch
          that has this bs.Material applied.
    """

    def __init__(self):
        """
        Instantiate a PowerupFactory.
        You shouldn't need to do this; call bs.Powerup.getFactory() to get a shared instance.
        """

        self._lastPowerupType = None

        if bs.getConfig().get('Powerup Shape') == 'Powerup Shape: Smoothed Square':
           self.model = bs.getModel("powerupSimple")
           self.rscale = 0.45
        else:
           self.model = bs.getModel("powerup")
           self.rscale = 0.65
        self.modelSimple = bs.getModel("powerupSimple")
        
        self.texNull = bs.getTexture("white")

        self.texBomb = bs.getTexture("powerupBomb")
        self.texPunch = bs.getTexture("powerupPunch")
        self.texIceBombs = bs.getTexture("powerupIceBombs")
        self.texStickyBombs = bs.getTexture("powerupStickyBombs")
        self.texGlueBombs = bs.getTexture("powerupGlueBombs")
        self.texShield = bs.getTexture("powerupShield")
        self.texImpactBombs = bs.getTexture("powerupImpactBombs")
        self.texHealth = bs.getTexture("powerupHealth")
        self.texLandMines = bs.getTexture("powerupLandMines")
        self.texRangerBombs = bs.getTexture("powerupRangerBombs")
        self.texCombatBombs = bs.getTexture("powerupCombatBombs")
        self.texFireBombs = bs.getTexture("powerupFireBombs")
        self.texDynamitePack = bs.getTexture("powerupDynamitePack")
        self.texGrenades = bs.getTexture("powerupGrenade")
        self.texHealBombs = bs.getTexture("powerupHealBombs")
        self.texKnockerBombs = bs.getTexture("powerupKnockerBombs")
        self.texCurse = bs.getTexture("powerupCurse")
        self.texOverdrive = bs.getTexture("powerupOverdrive")
        self.texHijump = bs.getTexture("powerupHijump")
        self.texSpeed = bs.getTexture("powerupSpeed")
        self.texBlast = bs.getTexture("powerupBlast")
        self.texMagnet = bs.getTexture("powerupMagnet")
        self.texCake = bs.getTexture("powerupCake")
        self.texTesla = bs.getTexture("powerupTesla")
        #New Powerups
        self.texEgg = bs.getTexture("neoSpazIcon")
        self.texInstantBomb = bs.getTexture("achievementTeamPlayer")
        self.texFireworkBombs = bs.getTexture("achievementOnslaught")
        self.texClusterBomb = bs.getTexture("achievementWall")
        self.texSno = bs.getTexture("achievementCrossHair") #Bunny is most uniform plain white color.
        self.texInfatuateBombs = bs.getTexture("bombHealingColor")
        self.texDigitalBombs = bs.getTexture("ouyaOButton")
        self.texSnowball = bs.getTexture("shrapnelSnow")
        self.texPalette = bs.getTexture("logo")
        self.texGloo = bs.getTexture("shrapnelGlue")
        self.texBot = bs.getTexture("discordIcon")
        self.texRadiusBombs = bs.getTexture("gameCenterIcon")
        self.texScatterBombs = bs.getTexture("shrapnelMine")
        self.texHunterBombs = bs.getTexture("achievementFootballShutout")
        self.texPills = bs.getTexture("achievementStayinAlive")
        self.texBloomingBombs = bs.getTexture("spaceBGColor") 

        self.healthPowerupSound = bs.getSound("healthPowerup")
        self.overdrivePowerupSound = bs.getSound("overdrivePowerup")
        self.powerupSound = bs.getSound("powerup01")
        self.powerdownSound = bs.getSound("powerdown01")
        self.dropSound = bs.getSound("boxDrop")
        self.boxShakeSound = bs.getSound("powerupShake")

        # material for powerups
        self.powerupMaterial = bs.Material()

        # material for anyone wanting to accept powerups
        self.powerupAcceptMaterial = bs.Material()

        # pass a powerup-touched message to applicable stuff
        self.powerupMaterial.addActions(
            conditions=(("theyHaveMaterial",self.powerupAcceptMaterial)),
            actions=(("modifyPartCollision","collide",True),
                     ("modifyPartCollision","physical",False),
                     ("message","ourNode","atConnect",_TouchedMessage())))

        # we dont wanna be picked up
        self.powerupMaterial.addActions(
            conditions=("theyHaveMaterial",bs.getSharedObject('pickupMaterial')),
            actions=( ("modifyPartCollision","collide",False)))

        self.powerupMaterial.addActions(
            conditions=("theyHaveMaterial",bs.getSharedObject('footingMaterial')),
            actions=(("impactSound",self.dropSound,0.5,0.1)))

        self._powerupDist = []
        for p,freq in getDefaultPowerupDistribution():
            for i in range(int(freq)):
                if isinstance(bs.getSession(),bs.CoopSession) and p in ['hijump','tesla']: continue
                else: self._powerupDist.append(p)

    def getRandomPowerupType(self,forceType=None,excludeTypes=[]):
        """
        Returns a random powerup type (string).
        See bs.Powerup.powerupType for available type values.

        There are certain non-random aspects to this; a 'curse' powerup, for instance,
        is always followed by a 'health' powerup (to keep things interesting).
        Passing 'forceType' forces a given returned type while still properly interacting
        with the non-random aspects of the system (ie: forcing a 'curse' powerup will result
        in the next powerup being health).
        
        gameSpecificExcludeTypes include only the powerups that you don't want them in specific gamemodes where they
        are useless, like a Healing Bomb, why the hell would you want to heal enemies?
        """
        import weakref
        
        # Disable some powerups based on the gamemode
        self._gamemode = bs.getActivity().getName()
        self._map = bs.getActivity()._map.getName()
        self.healthPowerups = ['overdrive','health','healBombs']
        self.shieldCounters = ['grenades','digitalBombs','combatBombs','fireBombs','impactBombs', 'rangerBombs']
        
        #if bs.getConfig().get('Enable Hard Powerups',False):
        #if bs.getConfig()['Enable Hard Powerups'] == False:
        #    hardPowerups = ['dynamitePack','dizzyCake','hijump','tesla','speed','rangerBombs']
        ##elif bs.getConfig().get('Enable Hard Powerups',True): hardPowerups = []
        #elif bs.getConfig()['Enable Hard Powerups'] == True: hardPowerups = []
        #else: hardPowerups = []
        hardPowerups = []
        
        if (self._gamemode == 'Race' 
            or self._gamemode == 'Assault' 
            or self._gamemode == 'Hockey' 
            or self._gamemode == 'Chosen One'
            or self._map == 'A Space Odyssey' 
            or self._map == 'Happy Thoughts'): # Disable speed where completing the objective faster is essential
            speedDisable = ['speed']
        else:
            speedDisable = []
        if (self._map == 'Lake Frigid' 
            or self._map == 'Hockey Stadium' 
            or self._map == 'Football Stadium' 
            or self._map == 'Basketball Stadium' 
            or self._map == 'Bridgit' 
            or self._map == 'Monkey Face' 
            or self._map == 'Doom Shroom Large' 
            or self._map == 'Doom Shroom' 
            or self._map == 'Tower D' 
            or self._gamemode == 'Basketball' 
            or self._gamemode == 'Assault'            
            or self._map == 'Courtyard' 
            or self._map == 'Rampage' 
            or self._map == 'Toilet Donut' 
            or self._map == 'OUYA' 
            or self._map == 'Hovering Plank-o-Wood' 
            or self._map == 'Courtyard Night' 
            or self._map == 'Block Fortress' 
            or self._map == 'Mush Feud' 
            or self._map == 'Flapland' 
            or self._map == 'A Space Odyssey' 
            or self._map == 'Happy Thoughts' 
            or self._map == 'Basketball Stadium' 
            or isinstance(bs.getSession(),bs.CoopSession)): # Disable hi-jump on flat maps and Coop
            hijumpDisable = ['hijump']
        else: hijumpDisable = []
        if isinstance(bs.getSession(),bs.FreeForAllSession): notFFA=['healBombs','tesla'] # Disable Healing Bombs in FFA games
        else: notFFA=[]
            
        if isinstance(bs.getSession(),bs.FreeForAllSession) or isinstance(bs.getSession(),bs.CoopSession): teamsOnly=['tesla']
        else: teamsOnly=[]
            
        if forceType: t = forceType
        else:
            if self._lastPowerupType == 'curse': 
                t = random.choice(self.healthPowerups)
            elif self._lastPowerupType == 'shield' and not isinstance(bs.getSession(),bs.CoopSession) and not bs.getConfig()['Powerup Distribution'] == 'Classic':
                t = random.choice(self.shieldCounters)
            elif self._lastPowerupType == 'fireBombs':
                if random.random() >= 0.75: t = 'iceBombs'
                else: t = self._powerupDist[random.randint(0,len(self._powerupDist)-1)]
            elif self._lastPowerupType == 'iceBombs':
                if random.random() >= 0.75 and not bs.getConfig()['Powerup Distribution'] == 'Classic': t = 'fireBombs'
                else: t = self._powerupDist[random.randint(0,len(self._powerupDist)-1)]
            else:
                while True:
                    t = self._powerupDist[
                        random.randint(0, len(self._powerupDist)-1)]
                    if ((t not in excludeTypes)
                    and (t not in notFFA)
                    and (t not in teamsOnly)
                    and (t not in speedDisable)
                    and (t not in hijumpDisable)
                    and (t not in hardPowerups)):
                        break
        self._lastPowerupType = t
        return t


def getDefaultPowerupDistribution():
    try: pd = bs.getConfig()['Powerup Distribution']
    except Exception: pd = 'JRMP'
    bool = bs.getConfig()['Enable New Powerups']
    
    if isinstance(bs.getActivity(),bsMainMenu.MainMenuActivity): return (('tripleBombs',0),('iceBombs',0))
    if not isinstance(bs.getSession(),bs.CoopSession):
        if (pd == 'JRMP'):
            return (('tripleBombs',3),
                    ('iceBombs',1),
                    ('punch',1),
                    ('impactBombs',4),
                    ('landMines',3),
                    ('stickyBombs',4),
                    ('combatBombs',5),
                    ('dynamitePack',1),
                    ('rangerBombs',3),
                    ('knockerBombs',2),
                    ('grenades',4),
                    ('blastBuff',2),
                    ('fireBombs',3),
                    ('healBombs',1),
                    ('glueBombs',2),
                    ('shield',1),
                    ('overdrive',1),
                    ('health',1),
                    ('curse',2),
                    ('bunny',2 if bool == True else 0),
                    ('snoball',1 if bool == True else 0),
                    ('dizzyCake',1),
                    ('hunterBombs',4 if bool == True else 0),
                    ('magnet',2),
                    ('gloo',1 if bool == True else 0),
                    ('snowball',3 if bool == True else 0),
                    ('scatterBombs',3 if bool == True else 0),
                    ('hijump',0 if bs.getActivity()._disableHijump else 1),
                    ('speed',0 if bs.getActivity()._disableSpeed else 1),
                    ('bot',2 if bool == True else 0),
                    ('radiusBombs',4 if bool == True else 0),
                    ('infatuateBombs',2 if bool == True else 0),
                    ('clusterBomb',1 if bool == True else 0),
                    ('fireworkBombs',2 if bool == True else 0),
                    ('palette',3 if bool == True else 0),
                    ('pills',2 if bool == True else 0),
                    ('bloomingBombs',3 if bool == True else 0),
                    ('instantBomb',2 if not isinstance(bs.getSession(),bs.FreeForAllSession) or bool == True else 0),
                    ('digitalBombs',2 if bool == True else 0),
                    ('tesla',0 if isinstance(bs.getSession(),bs.CoopSession) or isinstance(bs.getSession(),bs.FreeForAllSession) else 2))
        if (pd == 'Classic'):
            return (('tripleBombs',3),
                    ('iceBombs',3),
                    ('punch',3),
                    ('impactBombs',3),
                    ('landMines',2),
                    ('stickyBombs',3),
                    ('shield',2),
                    ('health',1),
                    ('curse',1),
                    ('blastBuff',0),
                    ('overdrive',0),
                    ('combatBombs',0),
                    ('dynamitePack',0),
                    ('knockerBombs',0),
                    ('rangerBombs',0),
                    ('grenades',0),
                    ('fireBombs',0),
                    ('glueBombs',0),
                    ('healBombs',0),
                    ('hijump',0),
                    ('magnet',0),
                    ('dizzyCake',0),
                    ('speed',0),
                    #New Powerups
                    ('gloo',0),
                    ('clusterBomb',0),
                    ('bunny',0),
                    ('snoball',0),
                    ('scatterBombs',0),
                    ('fireworkBombs',0),
                    ('snowball',0),
                    ('instantBomb',0),
                    ('pills',0),
                    ('bot',0),
                    ('radiusBombs',0),
                    ('palette',0),
                    ('bloomingBombs',0),
                    ('hunterBombs',0),
                    ('digitalBombs',0),
                    ('infatuateBombs',0),
                    ('tesla',0))
        if (pd == 'Competetive'):
            return (('tripleBombs',0),
                    ('iceBombs',2),
                    ('punch',1),
                    ('impactBombs',3),
                    ('landMines',1),
                    ('stickyBombs',3),
                    ('combatBombs',3),
                    ('dynamitePack',2),
                    ('rangerBombs',1),
                    ('grenades',0),
                    ('dizzyCake',1),
                    ('knockerBombs',2),
                    ('blastBuff',0),
                    ('fireBombs',2),
                    ('glueBombs',1),
                    ('healBombs',1),
                    ('magnet',1),
                    ('shield',0),
                    ('overdrive',0),
                    ('health',0),
                    ('curse',0),
                    ('hijump',0 if bs.getActivity()._disableHijump else 1),
                    ('speed',0 if bs.getActivity()._disableSpeed else 1),
                    #New Powerups
                    ('bloomingBombs',1 if bool == True else 0),
                    ('clusterBomb',0),
                    ('fireworkBombs',1 if bool == True else 0),
                    ('bunny',0),
                    ('snoball',0),
                    ('gloo',0),
                    ('infatuateBombs',0),
                    ('snowball',1 if bool == True else 0),
                    ('pills',0),
                    ('hunterBombs',2 if bool == True else 0),
                    ('instantBomb',0),
                    ('bot',2 if bool == True else 0),
                    ('radiusBombs',0),
                    ('scatterBombs',1 if bool == True else 0),
                    ('digitalBombs',1 if bool == True else 0),
                    ('palette',0),
                    ('tesla',0))
        if (pd == 'No Powerups'):
            return (('tripleBombs',0),
                    ('iceBombs',0),
                    ('punch',0),
                    ('impactBombs',0),
                    ('landMines',0),
                    ('stickyBombs',0),
                    ('combatBombs',0),
                    ('dynamitePack',0),
                    ('rangerBombs',0),
                    ('grenades',0),
                    ('fireBombs',0),
                    ('healBombs',0),
                    ('magnet',0),
                    ('glueBombs',0),
                    ('knockerBombs',0),
                    ('shield',0),
                    ('overdrive',0),
                    ('dizzyCake',0),
                    ('blastBuff',0),
                    ('health',0),
                    ('curse',0),
                    ('hijump',0),
                    ('speed',0),
                    #New Powerups
                    ('pills',0),
                    ('clusterBomb',0),
                    ('fireworkBombs',0),
                    ('scatterBombs',0),
                    ('instantBomb',0),
                    ('bunny',0),
                    ('snoball',0),
                    ('infatuateBombs',0),
                    ('snowball',0),
                    ('gloo',0),
                    ('bloomingBombs',0),
                    ('radiusBombs',0),
                    ('hunterBombs',0),
                    ('bot',0),
                    ('digitalBombs',0),
                    ('palette',0),
                    ('tesla',0))
    else:
        return (('tripleBombs',1),
               ('iceBombs',4),
               ('punch',2),
               ('impactBombs',4),
               ('landMines',3),
               ('stickyBombs',3),
               ('combatBombs',5),
               ('dynamitePack',1),
               ('rangerBombs',3),
               ('knockerBombs',3),
               ('grenades',3),
               ('blastBuff',2),
               ('fireBombs',5),
               ('healBombs',1),
               ('glueBombs',1),
               ('shield',1),
               ('overdrive',1),
               ('health',2),
               ('curse',2),
               ('dizzyCake',3),
               ('magnet',4),
               ('hijump',0),
               ('speed',2),
               ('scatterBombs',4 if bool == True else 0),
               #New Powerups
               ('bloomingBombs',3 if bool == True else 0),
               ('pills',3 if bool == True else 0),
               ('fireworkBombs',1 if bool == True else 0),
               ('hunterBombs',4 if bool == True else 0),
               ('infatuateBombs',2 if bool == True else 0),
               ('bunny',2 if bool == True else 0),
               ('snoball',2 if bool == True else 0),
               ('gloo',2 if bool == True else 0),
               ('clusterBomb',1 if bool == True else 0),
               ('digitalBombs',3 if bool == True else 0),
               ('snowball',4 if bool == True else 0),
               ('bot',0),
               ('radiusBombs',4 if bool == True else 0),
               ('palette',1 if bool == True else 0),
               ('instantBomb',0),
               ('tesla',0))
                    
class Powerup(bs.Actor):
    """
    category: Game Flow Classes

    A powerup box.
    This will deliver a bs.PowerupMessage to anything that touches it
    which has the bs.PowerupFactory.powerupAcceptMaterial applied.

    Attributes:

       powerupType
          The string powerup type.  This can be 'tripleBombs', 'punch',
          'iceBombs', 'impactBombs', 'landMines', 'stickyBombs', 'shield',
          'health', or 'curse'.

       node
          The 'prop' bs.Node representing this box.
    """

    def __init__(self,position=(0,1,0),powerupType='tripleBombs',expire=True):
        """
        Create a powerup-box of the requested type at the requested position.

        see bs.Powerup.powerupType for valid type strings.
        """
        
        bs.Actor.__init__(self)

        factory = self.getFactory()
        self._powersGiven = False

        self.powerupType = powerupType;
        #The color defines how useful the 
        #powerup does
        #in the game.
        unknown = (0.5, 0.5, 0.5)
        common = (1.1, 1.1, 1.1)
        uncommon = (0.0, 1.6, 0.4)
        rare = (0.0, 0.25, 1.4)
        epic = (1.17, 0.5, 2.2)
        legendary = (2.0, 1.7, 0.0)

        if self.powerupType == 'tripleBombs':
            self.ptName = 'Triple Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = epic
            else:
           	self.ptC = (1,1,0)
        elif self.powerupType == 'punch':
            self.ptName = 'Boxing Gloves'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = epic
            else:
           	self.ptC = (1,0.3,0.3)
        elif self.powerupType == 'iceBombs':
            self.ptName = 'Ice Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = uncommon
            else:
           	self.ptC = (0,0.45,1.0)
        elif self.powerupType == 'impactBombs':
            self.ptName = 'Impact Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (0.6,0.6,0.6)
        elif self.powerupType == 'landMines':
            self.ptName = 'Land Mines'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (0.1,0.7,0)
        elif self.powerupType == 'stickyBombs':
            self.ptName = 'Sticky Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = epic
            else:
           	self.ptC = (0,1,0)
        elif self.powerupType == 'rangerBombs':
            self.ptName = 'Ranger Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (1,1,0.5)
        elif self.powerupType == 'combatBombs':
            self.ptName = 'Combat Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (0,1,1)
        elif self.powerupType == 'fireBombs':
            self.ptName = 'Fire Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = uncommon
            else:
           	self.ptC = (1,0.7,0)
        elif self.powerupType == 'dynamitePack':
            self.ptName = 'Dynamite Pack'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (1,0,0)
        elif self.powerupType == 'grenades':
            self.ptName = 'Grenades'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = uncommon
            else:
           	self.ptC = (0.57,0.82,0.6)
        elif self.powerupType == 'healBombs':
            self.ptName = 'Heal Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = legendary
            else:
           	self.ptC = (1,0.4,0.7)
        elif self.powerupType == 'knockerBombs':
            self.ptName = 'Knocker Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = common
            else:
           	self.ptC = (0.0,0.0,1.0)
        elif self.powerupType == 'shield':
            self.ptName = 'Energy Shield'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = epic
            else:
           	self.ptC = (0.7,0.5,1)
        elif self.powerupType == 'health':
            self.ptName = 'Med Kit'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = legendary
            else:
           	self.ptC = (1,0.9,0.9)
        elif self.powerupType == 'glueBombs':
            self.ptName = 'Glue Bucket'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (1,1,1)
        elif self.powerupType == 'digitalBombs':
            self.ptName = 'Digital Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (0.3,0.3,0.3)
        elif self.powerupType == 'overdrive':
            self.ptName = 'Overdrive'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = epic
            else:
           	self.ptC = (0.5,0,1)
        elif self.powerupType == 'curse':
            self.ptName = 'Curse'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = common
            else:
           	self.ptC = (0.3,0,0.45)
        elif self.powerupType == 'hijump':
            self.ptName = 'Hi-Jump'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (1,0.01,0.95)
        elif self.powerupType == 'speed':
            self.ptName = 'Speed Boots'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = common
            else:
           	self.ptC = (0.75,1,0.1)
        elif self.powerupType == 'magnet':
            self.ptName = 'Magnet Marbles'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = common
            else:
           	self.ptC = (0,0.5,1)
        elif self.powerupType == 'blastBuff':
            self.ptName = 'Bigger Blasts'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = epic
            else:
           	self.ptC = (1.2,0.8,0)
        elif self.powerupType == 'dizzyCake':
            self.ptName = 'Dizzy Cake'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (1.12,0.78,0.85)
        elif self.powerupType == 'tesla':
            self.ptName = 'Tesla'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = legendary
            else:
           	self.ptC = (1,0.5,0)
        #New Powerups!!
        elif self.powerupType == 'infatuateBombs':
            self.ptName = 'Infatuate Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (1.4,0.7,0.8)
        elif self.powerupType == 'instantBomb':
            self.ptName = 'Self-Destruct'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (1.2,0.6,0.3)
        elif self.powerupType == 'scatterBombs':
            self.ptName = 'Scatter Bomb'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = uncommon
            else:
           	self.ptC = (1.0,0.79,0.70)
        elif self.powerupType == 'snowball':
            self.ptName = 'Snowballs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = uncommon
            else:
           	self.ptC = (0.95,1,1)
        elif self.powerupType == 'gloo':
            self.ptName = 'Sticky Gloos'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = common
            else:
           	self.ptC = (1,0.8,0.9)
        elif self.powerupType == 'radiusBombs':
            self.ptName = 'Radius Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = common
            else:
           	self.ptC = (1.3,1.3,1.3)
        elif self.powerupType == 'bot':
            self.ptName = 'Wild Bot'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (0.9,0.7,1.1)
        elif self.powerupType == 'palette':
            self.ptName = 'Art Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = common
            else:
           	self.ptC = (1.0,0.5,0.5)
        elif self.powerupType == 'bloomingBombs':
            self.ptName = 'Splash Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (0.85,0.8,1.3)
        elif self.powerupType == 'snoball':
            self.ptName = 'Projectile Shooter'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = rare
            else:
           	self.ptC = (0.45,0.75,0.65)
        elif self.powerupType == 'bunny':
            self.ptName = 'Buddy Bot'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = legendary
            else:
           	self.ptC = (0.71,0.71,0.35)
        elif self.powerupType == 'fireworkBombs':
            self.ptName = 'Firework Cracker'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = legendary
            else:
           	self.ptC = (1.2,0.88,0.55)
        elif self.powerupType == 'clusterBomb':
            self.ptName = 'Trap Bomb'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = epic
            else:
           	self.ptC = (0.65,0.7,0.86)
        elif self.powerupType == 'pills':
            self.ptName = 'Pills'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = epic
            else:
           	self.ptC = (1,1.2,0.25)
        elif self.powerupType == 'hunterBombs':
            self.ptName = 'Hunter Bombs'
            if bs.getConfig().get('Powerup Text Color') == 'Powerup Text Color: Tier Based':
               self.ptC = uncommon
            else:
           	self.ptC = (0.6,0.2,0.2)
        
        else: #raise Exception("invalid powerupType: "+str(powerupType))
            self.ptName = 'Undefined'
            self.ptC = unknown

        if len(position) != 3: raise Exception("expected 3 floats for position")
        
        self.node = bs.newNode('prop',
                               delegate=self,
                               attrs={'body':'box',
                                      'position':position,
                                      'model':factory.model,
                                      'lightModel':factory.modelSimple,
                                      'shadowSize':0.5,
                                      'colorTexture':factory.texBomb,
                                      'reflection':'powerup',
                                      'reflectionScale':[factory.rscale],
                                      'materials':(factory.powerupMaterial,bs.getSharedObject('objectMaterial'),bs.getSharedObject('powerupMaterial'))})
        
        # Text for the powerup
        if bs.getConfig().get('Fancy Powerups',True):
            self.bubble = bs.newNode('shield', attrs={
            'position': (self.node.position[0],self.node.position[1]-1.8,self.node.position[2]),
            'color': (1,1,1),
            'radius': 1.2})
            self.node.connectAttr('position',self.bubble,'position')
            bubbleColor = {0: (2, 0, 0), 250: (2, 2, 0), 250 * 2: (0, 2, 0), 250 * 3: (0, 2, 2), 250 * 4: (2, 0, 2), 250 * 5: (0, 0, 2), 250 * 6: (2, 0, 0)}
            bsUtils.animateArray(self.bubble, 'color', 3, bubbleColor, True)
        
        
        # Text for the powerup
        if bs.getConfig().get('Fancy Powerups',True): 
            pt = bs.newNode('math',
                        owner=self.node,
                        attrs={
                            'input1': (
                                0, 0.87, 0),
                            'operation': 'add'
                        })
            self.node.connectAttr('position', pt, 'input2')
            self.pt = bs.newNode('text',
                             owner=self.node,
                             attrs={
                                'text': '',
                                'inWorld': True,
                                'shadow': 1,
                                'flatness': 0.9,
                                'scale': 0.1,
                                'hAlign': 'center',
                             })
            self.pt.text = self.ptName
            self.pt.color = self.ptC
            pt.connectAttr('output', self.pt, 'position')
            bs.animate(self.pt, 'scale', {0: 0.01, 140: 0.01, 600: 0.011, 900: 0.01, 1200: 0.01, 1500: 0.011, 1900:0.01}, True)
            #bsUtils.animateArray(self.pt, 'color', 3, {0: (2, 0, 0), 500: (0, 2, 0),1000: (0, 0, 2), 1500: (2, 2, 0), 2000: (0, 2, 2), 2500: (2, 0, 2), 2900: (2*random.random(), 2*random.random(), 2*random.random()), 3000: (1, 0, 0)}, True)
            bs.animate(self.pt,'opacity',{0:1.0})
        
        
        self.setPowerupType()
                                      
        bs.gameTimer(int(defaultPowerupInterval*0.5+random.randint(-3000,2000)),bs.WeakCall(self._shake))
        # animate in..
        curve = bs.animate(self.node,"modelScale",{0:0,140:1.6,200:1})
        bs.gameTimer(200,curve.delete)

        if expire:
            bs.gameTimer(defaultPowerupInterval-2500,bs.WeakCall(self._startFlashing))
            bs.gameTimer(defaultPowerupInterval-1000,bs.WeakCall(self.handleMessage,bs.DieMessage()))

    @classmethod
    def getFactory(cls):
        """
        Returns a shared bs.PowerupFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        if activity is None: 
            raise Exception("no current activity")
            #return None
        try: return activity._sharedPowerupFactory
        except Exception:
            f = activity._sharedPowerupFactory = PowerupFactory()
            return f
            
    def setPowerupType(self,randomType=False):
    
        factory =self.getFactory()
        
        if randomType: 
            self.powerupType = random.choice(['tripleBombs','punch','iceBombs','impactBombs','landMines','fireworkBombs',
                                              'stickyBombs','rangerBombs','combatBombs','fireBombs','radiusBombs','palette','infatuateBombs',
                                              'dynamitePack','grenades','knockerBombs','shield','health','gloo','snowball','scatterBombs',
                                              'glueBombs','overdrive','curse','magnet','blastBuff','dizzyCake'])
        
        if self.powerupType == 'tripleBombs': tex = factory.texBomb
        elif self.powerupType == 'punch': tex = factory.texPunch
        elif self.powerupType == 'iceBombs': tex = factory.texIceBombs
        elif self.powerupType == 'impactBombs': tex = factory.texImpactBombs
        elif self.powerupType == 'landMines': tex = factory.texLandMines
        elif self.powerupType == 'stickyBombs': tex = factory.texStickyBombs
        elif self.powerupType == 'rangerBombs': tex = factory.texRangerBombs
        elif self.powerupType == 'combatBombs': tex = factory.texCombatBombs
        elif self.powerupType == 'fireBombs': tex = factory.texFireBombs
        elif self.powerupType == 'dynamitePack': tex = factory.texDynamitePack
        elif self.powerupType == 'grenades': tex = factory.texGrenades
        elif self.powerupType == 'healBombs': tex = factory.texHealBombs
        elif self.powerupType == 'knockerBombs': tex = factory.texKnockerBombs
        elif self.powerupType == 'shield': tex = factory.texShield
        elif self.powerupType == 'health': tex = factory.texHealth
        elif self.powerupType == 'glueBombs': tex = factory.texGlueBombs
        elif self.powerupType == 'overdrive': tex = factory.texOverdrive
        elif self.powerupType == 'curse': tex = factory.texCurse
        elif self.powerupType == 'hijump': tex = factory.texHijump
        elif self.powerupType == 'speed': tex = factory.texSpeed
        elif self.powerupType == 'magnet': tex = factory.texMagnet
        elif self.powerupType == 'blastBuff': tex = factory.texBlast
        elif self.powerupType == 'dizzyCake': tex = factory.texCake
        elif self.powerupType == 'tesla': tex = factory.texTesla
        #New Powerups!!
        elif self.powerupType == 'bunny': tex = factory.texEgg
        elif self.powerupType == 'instantBomb': tex = factory.texInstantBomb
        elif self.powerupType == 'clusterBomb': tex = factory.texClusterBomb
        elif self.powerupType == 'fireworkBombs': tex = factory.texFireworkBombs
        elif self.powerupType == 'snoball': tex = factory.texSno
        elif self.powerupType == 'bloomingBombs': tex = factory.texBloomingBombs
        elif self.powerupType == 'infatuateBombs': tex = factory.texInfatuateBombs
        elif self.powerupType == 'digitalBombs': tex = factory.texDigitalBombs
        elif self.powerupType == 'scatterBombs': tex = factory.texScatterBombs
        elif self.powerupType == 'snowball': tex = factory.texSnowball
        elif self.powerupType == 'pills': tex = factory.texPills
        elif self.powerupType == 'gloo': tex = factory.texGloo
        elif self.powerupType == 'radiusBombs': tex = factory.texRadiusBombs
        elif self.powerupType == 'bot': tex = factory.texBot
        elif self.powerupType == 'palette': tex = factory.texPalette
        elif self.powerupType == 'hunterBombs': tex = factory.texHunterBombs
        
        else: raise Exception("invalid powerupType: "+str(powerupType))
        
        self.node.colorTexture = tex
        
            
    def _startFlashing(self):
        if self.node.exists(): self.node.flashing = True

    def _shake(self):
        if self.node.exists() and self.powerupType in ['overdrive','curse','magnet','hijump','speed','knocker']:
            bs.playSound(self.getFactory().boxShakeSound,0.8,position=self.node.position)
            curve = bs.animate(self.node,"modelScale",{0:1,
                                                       50:1.15,
                                                       100:1})
            self.node.handleMessage('impulse',self.node.position[0]+random.uniform(-0.05,0.05),
                                              self.node.position[1]+random.uniform(-0.05,0.05),
                                              self.node.position[2]+random.uniform(-0.05,0.05),
                                              0,0,0,
                                              100,100,0,0,
                                              random.uniform(-0.1,0.1),1,random.uniform(-0.1,0.1))
        
    def handleMessage(self,m):
        self._handleMessageSanityCheck()

        if isinstance(m,PowerupAcceptMessage):
           # self.light.delete()
            factory = self.getFactory()
            if self.powerupType == 'health':
                bs.playSound(factory.healthPowerupSound,3,position=self.node.position)
            if self.powerupType == 'overdrive':
                bs.playSound(factory.overdrivePowerupSound,3,position=self.node.position)
            bs.playSound(factory.powerupSound,3,position=self.node.position)
            self._powersGiven = True
            # Keep track on how many powerups you've collected total (used to get an achievement)
            bs.statAdd('Powerup Total')
            self.handleMessage(bs.DieMessage())

        elif isinstance(m,_TouchedMessage):
            if not self._powersGiven:
                node = bs.getCollisionInfo("opposingNode")
                if node is not None and node.exists():
                    #We won't tell the spaz about the bunny.  It'll just happen.
                    if self.powerupType == 'bunny':
                        bsUtils.PopupText(
                            'Buddy Bot',
                            color=(0.71,0.71,0.35),
                            scale=1.3,
                            position=self.node.position).autoRetain()
                        p=node.getDelegate().getPlayer()
                        if not 'bunnies' in p.gameData:
                            p.gameData['bunnies'] = BuddyBunny.BunnyBotSet(p)
                        p.gameData['bunnies'].doBunny()
                        self._powersGiven = True
                        self.handleMessage(bs.PowerupAcceptMessage())
                        self.handleMessage(bs.DieMessage())
                    #a Spaz doesn't know what to do with a snoball powerup. All the snowball functionality
                    #is handled through SnoBallz.py to minimize modifications to the original game files
                    elif self.powerupType == 'snoball':
                        bsUtils.PopupText(
                            'Shooter',
                            color=(0.45,0.75,0.65),
                            scale=1.3,
                            position=self.node.position).autoRetain()
                        spaz=node.getDelegate()
                        SnoBallz.snoBall().getFactory().giveBallz(spaz)
                        self._powersGiven = True
                        self.handleMessage(bs.PowerupAcceptMessage())
                        self.handleMessage(bs.DieMessage())
                    else:
                        node.handleMessage(PowerupMessage(self.powerupType,sourceNode=self.node))

        elif isinstance(m,bs.DieMessage):
            if bs.getConfig().get('Fancy Powerups',True): self.bubble.delete()
            if self.node.exists():
                if (m.immediate):
                    self.node.delete()
                else:
                    curve = bs.animate(self.node,"modelScale",{0:1,100:0})
                    bs.gameTimer(100,bs.Call(self.node.delete))

        elif isinstance(m,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())

        elif isinstance(m,bs.HitMessage):
            # cake "corrupts" the contents of the box and makes it jump, cuz funniez
            if m.hitSubType == 'cake' and m.hitSubTypeTrue:
                self.setPowerupType(randomType=True)
                self.node.handleMessage('impulse',self.node.position[0],self.node.position[1],self.node.position[2],
                                    0,0,0,
                                    250,250,0,0,0,1,0)
            # dont die on punches, hi-jump propel blasts and healing bomb blasts (thats annoying)
            elif m.hitType != 'punch' and m.hitSubType != 'hijump' and m.hitSubType != 'healing' and m.hitSubType != 'knocker' and m.hitSubType != 'splash' and m.hitSubType != 'infatuate':
                def _doStuff():
                    bs.Blast(position=self.node.position,
                            blastType='normal').autoRetain()
                if bs.getConfig().get('Cheat KAB',True): bs.gameTimer(99,bs.Call(_doStuff))
                self.handleMessage(bs.DieMessage())
        else:
            bs.Actor.handleMessage(self,m)
