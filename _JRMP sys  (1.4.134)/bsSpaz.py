import bs
import bsUtils
import bsInteractive
import bsAchievement
import bsBomb
import bsMainMenu
import bsInternal
import random
import datetime
import weakref
import math


# list of defined spazzes
appearances = {}

def getAppearances(includeLocked=True,includeAchievement=False):
    import bsInternal
    disallowed = []
    if not includeLocked:
        # hmm yeah this'll be tough to hack...
        if not bsInternal._getPurchased('characters.santa'): disallowed.append('Santa Claus')
        if not bsInternal._getPurchased('characters.frosty'): disallowed.append('Frosty')
        if not bsInternal._getPurchased('characters.bones'): disallowed.append('Bones')
        if not bsInternal._getPurchased('characters.bernard'): disallowed.append('Bernard')
        if not bsInternal._getPurchased('characters.pixie'): disallowed.append('Pixel')
        if not bsInternal._getPurchased('characters.pascal'): disallowed.append('Pascal')
        if not bsInternal._getPurchased('characters.actionhero'): disallowed.append('Todd McBurton')
        if not bsInternal._getPurchased('characters.taobaomascot'): disallowed.append('Taobao Mascot')
        if not bsInternal._getPurchased('characters.agent'): disallowed.append('Agent Johnson')
        if not bsInternal._getPurchased('characters.jumpsuit'): disallowed.append('Lee')
        if not bsInternal._getPurchased('characters.assassin'): disallowed.append('Zola')
        if not bsInternal._getPurchased('characters.cowboy'): disallowed.append('Butch')
        if not bsInternal._getPurchased('characters.witch'): disallowed.append('Witch')
        if not bsInternal._getPurchased('characters.warrior'): disallowed.append('Warrior')
        if not bsInternal._getPurchased('characters.superhero'): disallowed.append('Middle-Man')
        if not bsInternal._getPurchased('characters.alien'): disallowed.append('Alien')
        if not bsInternal._getPurchased('characters.oldlady'): disallowed.append('OldLady')
        if not bsInternal._getPurchased('characters.gladiator'): disallowed.append('Gladiator')
        if not bsInternal._getPurchased('characters.wizard'): disallowed.append('Grumbledorf')
        if not bsInternal._getPurchased('characters.wrestler'): disallowed.append('Wrestler')
        if not bsInternal._getPurchased('characters.operasinger'): disallowed.append('Gretel')
        if not bsInternal._getPurchased('characters.pixie'): disallowed.append('Pixie')
        if not bsInternal._getPurchased('characters.robot'): disallowed.append('Robot')
        if not bsInternal._getPurchased('characters.cyborg'): disallowed.append('B-9000')
        if not bsInternal._getPurchased('characters.bunny'): disallowed.append('Easter Bunny')
        if not bsInternal._getPurchased('characters.kronk'): disallowed.append('Kronk')
        if not bsInternal._getPurchased('characters.zoe'): disallowed.append('Zoe')
        if not bsInternal._getPurchased('characters.jackmorgan'): disallowed.append('Jack Morgan')
        if not bsInternal._getPurchased('characters.mel'): disallowed.append('Mel')
        if not bsInternal._getPurchased('characters.snakeshadow'): disallowed.append('Snake Shadow')
        
        # Custom characters that can be obtained from the store
        if not bsInternal._getPurchased('characters.wizard_mr'): disallowed.append('Grambeldorfe')
        if not bsInternal._getPurchased('characters.cow_mr'): disallowed.append('Milk')
        if not bsInternal._getPurchased('characters.knight_mr'): disallowed.append('Sir Bombalot')
        if not bsInternal._getPurchased('characters.jester_mr'): disallowed.append('Willy')
        
    #if not includeAchievement:
    #    # Custom characters that can only be obtained with achievements
    #    if not bsAchievement.getAchievement('Make It Through').isComplete(): disallowed.append('Mictlan')
    #    if not bsAchievement.getAchievement('Half-Marathon').isComplete(): disallowed.append('Zill')
    #    if not bsAchievement.getAchievement('Stayin\' Alive').isComplete(): disallowed.append('Spy')
    #    if not bsAchievement.getAchievement('Onslaught God').isComplete(): disallowed.append('Juice-Boy')
        
    # AVGN swears. ALOT! What If you have dem kids to play this crap? No problemo!
    if bsInternal._getSetting('Kid Friendly Mode'): disallowed.append('AVGN')   
    return [s for s in appearances.keys() if s not in disallowed]

gPowerupWearOffTime = 20000  

# CLASS PUNCH STATS
gBasePunchPowerScale = 1.2 #1.3
gBasePunchCooldown = 450

gSpeedPunchPowerScale = 1.0 #1.0
gSpeedPunchCooldown = 425

gSuperPunchPowerScale = 1.9 #2.0
gSuperPunchCooldown = 900 #1000

gBackflipCooldown  = 7000

gPunchPowerDecrease = 0.18
gPunchTimes = 4

gPickupCounterDamage = 350

gDodgeDamageResistance = 0.35
gDodgeCooldown = 3000

# Fire bomb related stuff
# Damage is dealt 4 times a second
gFireDuration =  8000 #8000
gFireDamage = 29 #38

# BOT COLORS
gLameBotColor = (1.2,0.9,0.2)
gLameBotHighlight = (1.0,0.5,0.6)

gDefaultBotColor = (0.6,0.6,0.6)
gDefaultBotHighlight = (0.1,0.3,0.1)

gProBotColor = (1.0,0.2,0.1)
gProBotHighlight = (0.6,0.1,0.05)

# CURSE EXPLOSION RADIUS
gRegularCurseExplosionCOOP = 2.0
gOverchargedCurseExplosionCOOP = 4.0

gRegularCurseExplosion = 4.0
gOverchargedCurseExplosion = 6.0

gRegularCurseExplosionPARTY = 3.0
gOverchargedCurseExplosionPARTY = 5.0


class _PickupMessage(object):
    'We wanna pick something up'
    pass

class _KickHitMessage(object):
    'Message saying an object was hit'
    pass

class _PunchHitMessage(object):
    'Message saying an object was hit'
    pass
    
class _PlayerTouchMessage(object):
    'Message saying a player touched another player'
    pass

class _CurseExplodeMessage(object):
    'We are cursed and should blow up now.'
    pass

class _BombDiedMessage(object):
    "A bomb has died and thus can be recycled"
    pass
    
class _FootConnectMessage(object):
    'Player stands on ground'
    pass
    
class _FootDisconnectMessage(object):
    'Player stops touching the ground'
    pass

class Appearance(object):
    """Create and fill out one of these suckers to define a spaz appearance"""
    def __init__(self,name):

        self.name = name

        if appearances.has_key(self.name):
            raise Exception("spaz appearance name \"" + self.name + "\" already exists.")

        appearances[self.name] = self
        self.colorTexture = ""
        self.headModel = ""
        self.torsoModel = ""
        self.pelvisModel = ""
        self.upperArmModel = ""
        self.foreArmModel = ""
        self.handModel = ""
        self.upperLegModel = ""
        self.lowerLegModel = ""
        self.toesModel = ""
        self.jumpSounds = []
        self.attackSounds = []
        self.impactSounds = []
        self.deathSounds = []
        self.pickupSounds = []
        self.fallSounds = []
        self.style = 'spaz'
        self.defaultColor = None
        self.defaultHighlight = None

class SpazFactory(object):
    """
    Category: Game Flow Classes

    Wraps up media and other resources used by bs.Spaz instances.
    Generally one of these is created per bs.Activity and shared
    between all spaz instances.  Use bs.Spaz.getFactory() to return
    the shared factory for the current activity.

    Attributes:

       impactSoundsMedium
          A tuple of bs.Sounds for when a bs.Spaz hits something kinda hard.

       impactSoundsHard
          A tuple of bs.Sounds for when a bs.Spaz hits something really hard.

       impactSoundsHarder
          A tuple of bs.Sounds for when a bs.Spaz hits something really really hard.

       singlePlayerDeathSound
          The sound that plays for an 'importan' spaz death such as in co-op games.

       punchSound
          A standard punch bs.Sound.
       
       punchSoundsStrong
          A tuple of stronger sounding punch bs.Sounds.

       punchSoundStronger
          A really really strong sounding punch bs.Sound.

       swishSound
          A punch swish bs.Sound.

       blockSound
          A bs.Sound for when an attack is blocked by invincibility.

       shatterSound
          A bs.Sound for when a frozen bs.Spaz shatters.

       splatterSounds
          A bs.Sound for when a bs.Spaz blows up via curse.

       spazMaterial
          A bs.Material applied to all of parts of a bs.Spaz.

       rollerMaterial
          A bs.Material applied to the invisible roller ball body that a bs.Spaz uses for locomotion.
    
       punchMaterial
          A bs.Material applied to the 'fist' of a bs.Spaz.

       pickupMaterial
          A bs.Material applied to the 'grabber' body of a bs.Spaz.

       curseMaterial
          A bs.Material applied to a cursed bs.Spaz that triggers an explosion.
    """
    
    def getRandomSplatterSound(self):
        'Return a random splatter bs.Sound from the factory.'
        return self.splatterSounds[random.randrange(len(self.splatterSounds))]

    def _preload(self,character):
        """
        Preload media that will be needed for a given character.
        """
        self._getMedia(character)

    def __init__(self):
        """
        Instantiate a factory object.
        """        
        # Nothing
        self.nullModel = bs.getModel('zero')
        
        # Flesh characters
        self.impactSoundsMedium = (bs.getSound('impactMedium'),
                                bs.getSound('impactMedium2'),
                                bs.getSound('impactMedium3'),
                                bs.getSound('impactMedium4'),
                                bs.getSound('impactMedium5'),
                                bs.getSound('impactMedium6'),
                                bs.getSound('impactMedium7'))
        self.impactSoundsHard = (bs.getSound('impactHard'),
                                bs.getSound('impactHard2'),
                                bs.getSound('impactHard3'),
                                bs.getSound('impactHard4'),
                                bs.getSound('impactHard5'),
                                bs.getSound('impactHard6'))
        self.impactSoundsHarder = (bs.getSound('impactGiant'),
                                   bs.getSound('impactGiant2'),
                                   bs.getSound('impactGiant3'),
                                   bs.getSound('impactGiant4'),
                                   bs.getSound('impactGiant5'),
                                   bs.getSound('impactGiant6'))
        # Metal characters (mainly robots)
        self.impactMetalSoundsMedium = (bs.getSound('impactMediumMetal1'),
                                bs.getSound('impactMediumMetal2'))
        self.impactMetalSoundsHard = (bs.getSound('impactHardMetal1'),
                                bs.getSound('impactHardMetal2'))
        self.impactMetalSoundsHarder = (bs.getSound('impactGiantMetal1'),
                                bs.getSound('impactGiantMetal2'))
                                
        # Cardboard characters (for example Juicebox)
        self.impactCardboardSoundsMedium = (bs.getSound('impactMediumCardboard1'),
                                bs.getSound('impactMediumCardboard2'))
        self.impactCardboardSoundsHard = (bs.getSound('impactHardCardboard1'),
                                bs.getSound('impactHardCardboard2'))
        self.impactCardboardSoundsHarder = (bs.getSound('impactGiantCardboard1'),
                                bs.getSound('impactGiantCardboard2'))
        
        self.singlePlayerDeathSound = bs.getSound('playerDeath')
        self.playerDissolveSound = bs.getSound('playerDissolve')
        self.styleSound = bs.getSound('style')
        
        self.punchSound = bs.getSound('punch01')
        self.punchWeakSound = bs.getSound('punchWeak01')
        self.punchSoundsStrong = (bs.getSound('punchStrong01'),
                                  bs.getSound('punchStrong02'))
        self.punchResetSound = bs.getSound('powerdown01')
        self.punchSoundStronger = (bs.getSound('superPunch'))
        
        self.dashRechargeSound = bs.getSound('swish')
        
        # Accolade sound effects
        self.powerPunchSounds = (bs.getSound('owThatHurts1'),
                                bs.getSound('owThatHurts2'))
        self.gibKillSound = bs.getSound('gibKill')
        self.mineKillSound = bs.getSound('landMineKill')
        self.hijumpedSound = bs.getSound('hijumped')
        
        self.mysterySound = bs.getSound('diceMystery')
        self.homeRunSound = bs.getSound('homeRun')
        self.swishSounds = (bs.getSound('punchSwish1'),
                          bs.getSound('punchSwish2'))
        self.pickupCounterSound = bs.getSound('pickupCounter')
                          
        self.burningSound = bs.getSound('fireLit')
        
        self.ninjaGrabSound = bs.getSound('ninja1') #ninja1
        self.ninjaThrowSound = bs.getSound('ninja2') #ninja2
        
        self.curseBuffedSound = bs.getSound('explosionBuffed')
                          
        self.dizzySound = bs.getSound('dizzy')
        self.dizzyEndSound = bs.getSound('dizzyEnd')
        
        self.crowdClapSound = bs.getSound('crowdClap')
        self.crowdOhhSound = bs.getSound('crowdOhh')
        
        self.hijumpMidairSound = bs.getSound('hijumpMidair')
        self.hijumpLandSound = bs.getSound('hijumpLand')
        
        self.blockSound = bs.getSound('block')
        self.splatterSounds = [bs.getSound('splatter1'),
                               bs.getSound('splatter2'),
                               bs.getSound('splatter3'),
                               bs.getSound('splatter4'),
                               bs.getSound('splatter5'),
                               bs.getSound('splatter6')]
        self.splatterExtremeSound = bs.getSound('splatterExtreme')
        self.shatterSound = bs.getSound('shatter')
        
        self.splashSound = bs.getSound('splash')
        
        # Punch Stamina
        self.punchStaminaSound = bs.getSound('punchStamina')
        self.punchParrySound = bs.getSound('punchParry')
        
        # Speed Up and Down sounds for the Speed Boots powerup
        self.speedUpSound = bs.getSound('speedUp')
        self.speedDownSound = bs.getSound('speedDown')
        
        # Dodge Roll
        self.dodgeSound = bs.getSound('dodge')
        self.dodgeHitSound = bs.getSound('dodgeHit')
        
        # Curse Sounds
        self.curseSound = bs.getSound('curse')
        self.curseOffensiveSound = bs.getSound('curseOffensive')
        
        self.spazMaterial = bs.Material()
        self.rollerMaterial = bs.Material()
        self.punchMaterial = bs.Material()
        self.kickMaterial = bs.Material()
        self.pickupMaterial = bs.Material()
        self.curseMaterial = bs.Material()

        footingMaterial = bs.getSharedObject('footingMaterial')
        objectMaterial = bs.getSharedObject('objectMaterial')
        playerMaterial = bs.getSharedObject('playerMaterial')
        regionMaterial = bs.getSharedObject('regionMaterial')
        
        fireMaterial = bs.getSharedObject('fireMaterial')
        
        # send footing messages to spazzes so they know when they're on solid ground
        # eww this should really just be built into the spaz node
        self.rollerMaterial.addActions(
            conditions=('theyHaveMaterial', footingMaterial),
            actions=(('message', 'ourNode', 'atConnect', 'footing', 1),
                     ('message', 'ourNode', 'atConnect', _FootConnectMessage()),
                     ('modifyPartCollision', 'friction', 1),
                     ('message', 'ourNode', 'atDisconnect', 'footing', -1),
                     ('message', 'ourNode', 'atDisconnect', _FootDisconnectMessage())))

        self.spazMaterial.addActions(
            conditions=('theyHaveMaterial', footingMaterial),
            actions=(('message', 'ourNode', 'atConnect', 'footing', 1),
                     ('message', 'ourNode', 'atConnect', _FootConnectMessage()),
                     ('modifyPartCollision', 'friction', 1),
                     ('message', 'ourNode', 'atDisconnect', 'footing', -1),
                     ('message', 'ourNode', 'atDisconnect', _FootDisconnectMessage())))
                     
        self.spazMaterial.addActions(
            conditions=(('theyHaveMaterial',playerMaterial),'and',('theyAreDifferentNodeThanUs',)),
            actions=(('message','ourNode','atConnect',_PlayerTouchMessage())))
                     
        # react to touching fiery stuff
        self.spazMaterial.addActions(
            conditions=('theyHaveMaterial',fireMaterial),
            actions=(('message','ourNode','atConnect',bs.FireMessage(int(gFireDuration*0.628),None))))
        self.rollerMaterial.addActions(
            conditions=('theyHaveMaterial',fireMaterial),
            actions=(('message','ourNode','atConnect',bs.FireMessage(int(gFireDuration*0.628),None))))
                     
        self.kickMaterial.addActions(conditions=('theyAreDifferentNodeThanUs',), actions=(('message', 'ourNode', 'atConnect', _KickHitMessage())))
                     
        # punches
        self.punchMaterial.addActions(
            conditions=('theyAreDifferentNodeThanUs',),
            actions=(('modifyPartCollision','collide',True),
                     ('modifyPartCollision','physical',False),
                     ('message','ourNode','atConnect',_PunchHitMessage())))
        # pickups
        self.pickupMaterial.addActions(
            conditions=(('theyAreDifferentNodeThanUs',),'and',('theyHaveMaterial',objectMaterial)),
            actions=(('modifyPartCollision','collide',True),
                     ('modifyPartCollision','physical',False),
                     ('message','ourNode','atConnect',_PickupMessage())))
        # curse
        self.curseMaterial.addActions(
            conditions=(('theyAreDifferentNodeThanUs',),'and',('theyHaveMaterial',playerMaterial)),
            actions=('message','ourNode','atConnect',_CurseExplodeMessage()))


        self.footImpactSounds = (bs.getSound('footImpact01'),
                                 bs.getSound('footImpact02'),
                                 bs.getSound('footImpact03'))

        self.footSkidSound = bs.getSound('skid01')
        self.footRollSound = bs.getSound('scamper01')

        self.rollerMaterial.addActions(
            conditions=('theyHaveMaterial',footingMaterial),
            actions=(('impactSound',self.footImpactSounds,1,0.2),
                     ('skidSound',self.footSkidSound,20,0.05),
                     ('rollSound',self.footRollSound,20,5.0)))

        self.skidSound = bs.getSound('gravelSkid')

        self.spazMaterial.addActions(
            conditions=('theyHaveMaterial',footingMaterial),
            actions=(('impactSound',self.footImpactSounds,20,6),
                     ('skidSound',self.skidSound,2.0,1),
                     ('rollSound',self.skidSound,2.0,1)))

        self.shieldUpSound = bs.getSound('shieldUp')
        self.shieldDownSound = bs.getSound('shieldDown')
        self.shieldHitSound = bs.getSound('shieldHit')
        self.shieldDecaySound = bs.getSound('shieldDecay')
        self.shieldIdleSound = bs.getSound('shieldIdle')
        self.healthPowerupSound = bs.getSound("healthPowerup")
        
        self.delinSound = bs.getSound("delin")

        # we dont want to collide with stuff we're initially overlapping
        # (unless its marked with a special region material)
        self.spazMaterial.addActions(
            conditions=( (('weAreYoungerThan', 51),'and',('theyAreDifferentNodeThanUs',)),
                         'and',('theyDontHaveMaterial',regionMaterial)),
            actions=( ('modifyNodeCollision','collide',False)))
            
        #self.spazBurnMaterial = self.spazMaterial
        #import bsBomb
        #self.spazBurnMaterial.addActions(
        #    conditions=(('theyHaveMaterial',bs.getSharedObject('objectMaterial'))),
        #    actions=(('message','theirNode','atConnect',bsBomb.ExplodeMessage())))
        
        self.spazMedia = {}

    def _getStyle(self,character):
        return appearances[character].style
        
    def _getMedia(self,character):

        t = appearances[character]
        if not self.spazMedia.has_key(character):
            m = self.spazMedia[character] = {
                'jumpSounds':[bs.getSound(s) for s in t.jumpSounds],
                'attackSounds':[bs.getSound(s) for s in t.attackSounds],
                'impactSounds':[bs.getSound(s) for s in t.impactSounds],
                'deathSounds':[bs.getSound(s) for s in t.deathSounds],
                'pickupSounds':[bs.getSound(s) for s in t.pickupSounds],
                'fallSounds':[bs.getSound(s) for s in t.fallSounds],
                'colorTexture':bs.getTexture(t.colorTexture),
                'colorMaskTexture':bs.getTexture(t.colorMaskTexture),
                'headModel':bs.getModel(t.headModel),
                'torsoModel':bs.getModel(t.torsoModel),
                'pelvisModel':bs.getModel(t.pelvisModel),
                'upperArmModel':bs.getModel(t.upperArmModel),
                'foreArmModel':bs.getModel(t.foreArmModel),
                'handModel':bs.getModel(t.handModel),
                'upperLegModel':bs.getModel(t.upperLegModel),
                'lowerLegModel':bs.getModel(t.lowerLegModel),
                'toesModel':bs.getModel(t.toesModel)
            }
        else:
            m = self.spazMedia[character]
        return m

class Spaz(bs.Actor):
    """
    category: Game Flow Classes
    
    Base class for various Spazzes.
    A Spaz is the standard little humanoid character in the game.
    It can be controlled by a player or by AI, and can have
    various different appearances.  The name 'Spaz' is not to be
    confused with the 'Spaz' character in the game, which is just
    one of the skins available for instances of this class.

    Attributes:

       node
          The 'spaz' bs.Node.
    """
    
    pointsMult = 1
    curseTime = 8000

    defaultBombType = 'normal'
    defaultBombCount = 1
    defaultBlastRadius = 2.0 #2.0
    defaultBoxingGloves = False
    defaultShields = False
    defaultSpeedBoots = False
    impactScale = 1.0
    hitPoints = 1000
    isBoss = False
    noPoints = False
    freezeImmune = False
    fireImmune = False

    def __init__(self,color=(1,1,1),highlight=(0.5,0.5,0.5),character="Spaz",sourcePlayer=None,bombShape='Regular',catchphrases=[],startInvincible=True,canAcceptPowerups=True,powerupsExpire=False,demoMode=False):
        """
        Create a new spaz with the requested color, character, etc.
        """
        
        bs.Actor.__init__(self)
        activity = self.getActivity()
        
        factory = self.getFactory()

        self.playBigDeathSound = False

        # translate None into empty player-ref
        if sourcePlayer is None: sourcePlayer = bs.Player(None)
        
        # scales how much impacts affect us (most damage calcs)
        self._impactScale = self.impactScale
        self._impactScale *= 1.0
        
        self.currentlyPunching = False
        
        try: self._gamemode = bs.getActivity().getName()
        except: self._gamemode = None
        try: self._map = bs.getActivity()._map.getName()
        except: self._map = None
        
        self.footing = False
        self.hijumpSound = None
        
        self.punchCombo = 0
        self.punchComboCooldown = 1300
        self.punchComboTimer = None
        
        self.lowGravityTimer = None
        self.alreadyHealed = False
        self.healStacks = 0
        
        self.shieldDecayed = False
        
        # if you're moving fast in mid-air, you can deal damage on player touched
        # this variable prevents dealing damage multiple times
        self.midairCannonball = False
        self.midairDamaged = True
        self.timeToMidairCannonball = None
        
        
        
        self._character = character
        self.freezeImmune = self.freezeImmune
        self.fireImmune = self.fireImmune
        self.isBoss = self.isBoss
        self.noPoints = self.noPoints
        self.sourcePlayer = sourcePlayer
        self._dead = False
        self._punchPowerScale = gBasePunchPowerScale
        self._punchCooldown = gBasePunchCooldown
        self.fly = bs.getSharedObject('globals').happyThoughtsMode
        if self.defaultSpeedBoots: self._hockey = True
        else: 
            self._hockey = activity._map.isHockey
        self._punchedNodes = set()
        self._kickedNodes = set()
        self._kick = False
        self._cursed = False
        self._connectedToPlayer = None
        
        self.punches = 0
        
        self.bombShape = bombShape
        
        # Controls the ninja throw sounds
        self.ninjaGrabbed = False
        self.ninjaThrow = False
        
        self.spazHoldingMe = bs.Node(None)
                     
        materials = [factory.spazMaterial,bs.getSharedObject('objectMaterial'),bs.getSharedObject('playerMaterial')]
        rollerMaterials = [factory.rollerMaterial,bs.getSharedObject('playerMaterial')]
        extrasMaterials = []
        
        if canAcceptPowerups:
            pam = bs.Powerup.getFactory().powerupAcceptMaterial
            materials.append(pam)
            rollerMaterials.append(pam)
            extrasMaterials.append(pam)
            
        media = factory._getMedia(character)
        
        self.node = bs.newNode(type="spaz",
                               delegate=self,
                               attrs={'color':color,
                                      'behaviorVersion':0 if demoMode else 1,
                                      'demoMode':True if demoMode else False,
                                      'highlight':highlight,
                                      'jumpSounds':media['jumpSounds'],
                                      'attackSounds':media['attackSounds'],
                                      'impactSounds':media['impactSounds'],
                                      'deathSounds':[factory.delinSound] if random.randint(0,75) == 0 else media['deathSounds'],
                                      'pickupSounds':media['pickupSounds'],
                                      'fallSounds':media['fallSounds'],
                                      'colorTexture':media['colorTexture'],
                                      'colorMaskTexture':media['colorMaskTexture'],
                                      'headModel':media['headModel'],
                                      'torsoModel':media['torsoModel'],
                                      'pelvisModel':media['pelvisModel'],
                                      'upperArmModel':media['upperArmModel'],
                                      'foreArmModel':media['foreArmModel'],
                                      'handModel':media['handModel'],
                                      'upperLegModel':media['upperLegModel'],
                                      'lowerLegModel':media['lowerLegModel'],
                                      'toesModel':media['toesModel'],
                                      'style':factory._getStyle(character),
                                      'fly':self.fly,
                                      'hockey':self._hockey,
                                      'materials':materials,
                                      'rollerMaterials':rollerMaterials,
                                      'extrasMaterials':extrasMaterials,
                                      'punchMaterials':(factory.punchMaterial,bs.getSharedObject('attackMaterial')),
                                      'pickupMaterials':(factory.pickupMaterial,bs.getSharedObject('pickupMaterial')),
                                      'invincible':startInvincible,
                                      'sourcePlayer':sourcePlayer})
        timeNow = bs.checkTime(useInternet=False)
        if (bs.getConfig().get('Cheat FP',True) or (timeNow['month'] == 4 and
                                                    timeNow['day'] == 1)) and character == 'Mel':                
            self.sounds = [bs.getSound('dumb01'),
                           bs.getSound('dumb02'),
                           bs.getSound('dumb03'),
                           bs.getSound('dumb04'),
                           bs.getSound('dumb05'),
                           bs.getSound('dumb06'),
                           bs.getSound('dumb07'),
                           bs.getSound('dumb08'),
                           bs.getSound('dumb09'),
                           bs.getSound('dumb10'),]
            self.node.attackSounds = self.sounds
            self.node.jumpSounds = self.sounds
            self.node.impactSounds = self.sounds
            self.node.pickupSounds = self.sounds
            self.node.deathSounds = [bs.getSound('dumbDeath01')]
            self.node.fallSounds = [bs.getSound('dumbFall01')]
        self.shield = None
        
        if startInvincible:
            def _safeSetAttr(node,attr,val):
                if node.exists(): setattr(node,attr,val)
            if bs.getConfig().get('Invulnerable Mode',True):
                self.invincibilityTimer = bs.Timer(1500,bs.Call(_safeSetAttr,self.node,'invincible',True))
            else:
                self.invincibilityTimer = bs.Timer(1500,bs.Call(_safeSetAttr,self.node,'invincible',False))

        self.hitPoints = self.hitPoints
        self.hitPointsMax = self.hitPoints
        
        #How much HP you can receive from Overdrive powerup
        self.hitPointsOverdrive = 1000
        #How much HP you need to have until you'll be cursed
        self.hitPointsOverdriveTooMuch = 2000
        
        #Is the character on fire?
        self.onFire = False
        
        self.bombCount = self.defaultBombCount
        self._maxBombCount = self.defaultBombCount
        self.bombTypeDefault = self.defaultBombType
        self.bombType = self.bombTypeDefault
        self.bombShape = bombShape
        self.catchphrases = catchphrases
        self.stockBombCount = 0
        self.stockBombType = None
        self.blastRadius = self.defaultBlastRadius
        self.blastRadiusBuffed = False
        self.powerupsExpire = powerupsExpire
        self._hasBoxingGloves = False
        self._hasSpeedBoots = False
        self.bloomDamageStacks = 0
        self.loop = 0
        self.cc_timer = None
        
        self._jumpCooldown = 50
        self._afterJump = False
        self._duringDodge = False
        self._ableToDodge = True
        
        self._pickupCooldown = 0
        self.pickupCounterVictim = False
        
        self._bombCooldown = 0
        self._hasBoxingGloves = False
        
        if self.defaultBoxingGloves: self.equipBoxingGloves()
        if self.defaultShields: self.equipShields()
            
        self.lastPunchTime = -9999
        self.lastJumpTime = -9999
        self.lastPickupTime = -9999
        self.lastRunTime = -9999
        self.lastBackflipTime = -9999
        self._backflipCooldown = gBackflipCooldown
        self._lastRunValue = 0
        self.lastBombTime = -9999
        self._turboFilterTimes = {}
        self._turboFilterTimeBucket = 0
        self._turboFilterCounts = {}
        self.frozen = False
        self.dizzy = False
        self.burning = False
        self.shattered = False
        self.overcharged = False # If it's true, curse explosion is going to be lethal
        self._lastHitTime = None
        self._numTimesHit = 0
        
        if not bs.getConfig()['HP Bar'] == 'HP Bar Off':
            self._showhp()

        self._droppedBombCallbacks = []
        # deprecated stuff.. need to make these into lists
        self.punchCallback = None
        self.pickUpPowerupCallback = None
        
        if bs.getConfig().get('Cheat IHTHG',True) and self.sourcePlayer.exists():
            self.equipShields()
            self.equipBoxingGloves()
            self.hitPoints = self.hitPointsOverdriveTooMuch
        
        # catchphrase text
        self.duringCatchphrase = False
        self._catchphraseTextOffset = bs.newNode('math', owner=self.node, attrs={
            'input1': (0.0, 2.3, -0.15),
            'operation': 'add'})
        self.node.connectAttr('torsoPosition', self._catchphraseTextOffset, 'input2')
            
        self._catchphraseText = bs.newNode('text',
                                   owner=self.node,
                                   attrs={'inWorld':True,
                                          'text':'',
                                          'scale':0.0,
                                          'shadow':1.0,
                                          'maxWidth':250,
                                          'color':(1,1,1),
                                          'vAlign':'top',
                                          'hAlign':'center'})
        self._catchphraseTextOffset.connectAttr('output',self._catchphraseText,'position')
        self._catchphraseText.opacity = 0.8
            
        # punch stamina gauge
        #self.punchStaminaTextOffset = bs.newNode('math', owner=self.node, attrs={
        #    'input1': (0.0, 0.9, -0.15),
        #    'operation': 'add'})
        #self.node.connectAttr('torsoPosition', self.punchStaminaTextOffset, 'input2')
        #self.punchStaminaText = bs.newNode('text', owner=self.node, attrs={
                     #  'text': bs.getSpecialChar('hal')+" "+bs.getSpecialChar('hal')+" "+bs.getSpecialChar('hal'),
                     #  'inWorld': True,
                     #  'shadow': 0.4,
                    #   'color': (1,1,1,1),
                 #      'flatness': 0,
                    #   'scale': 0.01,
                 #      'hAlign': 'center'})
       # self.punchStaminaTextOffset.connectAttr('output', self.punchStaminaText, 'position')
       # if not self.sourcePlayer.exists(): self.punchStaminaText.scale = 0.0 # hide punch stamina for bots
       # bs.animate(self.punchStaminaText,'opacity',{0:0,
                #                                    500:1.0},loop=False)
        
        # counter/parry info
        self.counterTextOffset = bs.newNode('math', owner=self.node, attrs={
            'input1': (0.0, -0.85, 0.25),
            'operation': 'add'})
        self.node.connectAttr('torsoPosition', self.counterTextOffset, 'input2')
        
        self.counterText = bs.newNode('text', owner=self.node, attrs={
                       'text': '',
                       'inWorld': True,
                       'shadow': 0.5,
                       'color': (highlight[0],highlight[1],highlight[2]),
                       'flatness': 0.5,
                       'scale': 0.0175,
                       'hAlign': 'center'})
        self.counterText.opacity = 0.0
        self.counterTextOffset.connectAttr('output', self.counterText, 'position')
        
        # backflip cooldown info
        self.backflipCooldownTextOffset = bs.newNode('math', owner=self.node, attrs={
            'input1': (1.89, 0.8, 0.25),
            'operation': 'add'})
        self.node.connectAttr('torsoPosition', self.backflipCooldownTextOffset, 'input2')
        
        self.backflipCooldownText = bs.newNode('text', owner=self.node, attrs={
                       'text': '3.0',
                       'inWorld': True,
                       'text':'Backflip Ready',
                       'shadow': 1.0,
                       'color': (color[0],color[1],color[2]),
                       'flatness': 0.5,
                       'scale': 0.01,
                       'hAlign': 'right'})
        self.backflipCooldownText.opacity = 0.0
        self.backflipCooldownTextOffset.connectAttr('output', self.backflipCooldownText, 'position')
        
        # dash cooldown info
        self.dashCooldownTextOffset = bs.newNode('math', owner=self.node, attrs={
            'input1': (-0.5, 0.5, 0.25),
            'operation': 'add'})
        self.node.connectAttr('torsoPosition', self.dashCooldownTextOffset, 'input2')
        
        self.dashCooldownText = bs.newNode('text', owner=self.node, attrs={
                       'text': '3.0',
                       'inWorld': True,
                       'text':'Dash\nReady',
                       'shadow': 1.0,
                       'color': (1,1,0.5),
                       'flatness': 0.5,
                       'scale': 0.01,
                       'hAlign': 'right'})
        self.dashCooldownText.opacity = 0.0
        self.dashCooldownTextOffset.connectAttr('output', self.dashCooldownText, 'position')
    
    def _showhp(self):
        if self.node is None and not self.node.exists():
            return
        hp = bs.newNode('math',
                        owner=self.node,
                        attrs={
                            'input1': (
                                0, 1.4, 0) if self.sourcePlayer.exists(
                                ) else (0, 1.4, 0),
                            'operation': 'add'
                        })
        self.node.connectAttr('torsoPosition', hp, 'input2')
        self.hp = bs.newNode('text',
                             owner=self.node,
                             attrs={
                                'text': '',
                                'inWorld': True,
                                'shadow': 1,
                                'flatness': 0.9,
                                'scale': 0.1,
                                'hAlign': 'center',
                             })
        hp.connectAttr('output', self.hp, 'position')
        bs.animate(self.hp, 'scale', {0: 0.0, 1200: 0.007})
        bs.animate(self.hp,'opacity',{0:1.0})
        
        def _update():
            if not self.hp.exists():
                self.hpTimer = None
            if bs.getConfig()['HP Bar'] == 'Show HP Bar':
                perc = 1
                string3 = ' '
            else:
                perc = 0.1
                string3 = '%'
            if self.shield is not None:
                currentHP = self.shieldHitPoints
                maxHP = self.shieldHitPointsMax
                self.hp.color=(0.2,0,1)
                string1 = 'SHP: '
            elif self.shield is None:
                currentHP = self.hitPoints
                maxHP = self.hitPointsMax
                self.hp.color=(0.1,1,0.1)
                string1 = 'HP: '
                if self.hitPoints < self.hitPointsMax * 0.3:
                    self.hp.color=(1,0.1,0.1)
                elif self.hitPoints < self.hitPointsMax * 0.6:
                    self.hp.color=(1,1,0)
            if bs.getConfig().get('Show Max HP In HP Bar',True):
                string2 = '/' + str(int(maxHP*perc))
            else:
                string2 = ''
            self.hp.text = string1 + str(int(currentHP*perc)) + string2 + string3
        self.hpTimer = bs.Timer(200,bs.Call(_update), repeat=True)
        
    def catchphrase(self):
        """
        Show a random catchphrase above player's head
        """
        if not self.node.exists() and self.duringCatchphrase: return
        if random.randint(0,1): 
            try: self._catchphraseText.text = random.choice(self.catchphrases)
            except: return
            def sound():
                self.node.handleMessage(random.choice(['celebrate','celebrateL','celebrateR']),1000)
                self.node.handleMessage("attackSound")
            #bs.playSound(random.choice(self.getFactory()._getMedia(self._character)['jumpSounds']),1.5,self.node.position)
            time = random.randint(500,1500)
            self.soundTimer = bs.Timer(time,bs.Call(sound))
            self.duringCatchphrase = True
            def _timeout(): self.duringCatchphrase = False
            bs.animate(self._catchphraseText,'scale',{time:0,
                                                    time+150:0.03,
                                                    time+400:0.02,
                                                    time+2800:0.015,
                                                    time+3000:0.0},loop=False)
            bs.gameTimer(time+3000,_timeout)
                                                    
    def punchComboReset(self): 
        self.punchCombo = 0
        
    def lightningPower(self):
        """
        After collecting the Overdrive powerup, show some WACKY EFFECTZ, OOOH
        just to highlight the power.
        """  
        self.nova = bs.newNode('light',
                           attrs={'position':self.node.position,
                                  'color': (1.0,0.2,1.0),
                                  'volumeIntensityScale': 0.5})     
        bs.animate(self.nova,'intensity',{0:0,150:1.0,400:0},loop=False)
        bs.gameTimer(400,self.nova.delete)    
        bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=int(8.0+random.random()*45),scale=1.0,spread=3,chunkType='spark');

    def killFire(self):
        def dummy(): pass
        if self.node.exists():
            self.litSound.delete()
            
            factory = self.getFactory()
            def deleteLight(): self.flameLight.delete()
            self.onFire = False
            bs.animate(self.flameLight,'intensity',{0:0.5,1000:0.0},loop=False)
            flameDie = bs.Timer(1000,bs.Call(deleteLight))
            self.fireDamageTimer = bs.Timer(1,bs.Call(dummy))
            self.fireTimer = bs.Timer(1,bs.Call(dummy))
        
    def fire(self,source,time):
        """
        This function handles setting our Spaz on fire and reacting to it.
        """
   
        factory = self.getFactory()
        if time == None: self.time = self.fireDuration
        else: self.time = time
        
        
        def fireDamage():
            # Deal damage every time this function is called (if the target has the onFire tag)
            if self.onFire:
                if random.randint(1,6) == 1: self.node.handleMessage("hurtSound")
                self.node.handleMessage(bs.HitMessage(flatDamage=(gFireDamage/4)+(0.02*(self.hitPointsMax-self.hitPoints)),hitSubType='fire',sourcePlayer=source))
                self.fireDamageTimer = bs.Timer(250,bs.Call(fireDamage))
                
                for fire in range(1,5):
                   try: bs.emitBGDynamics(position=self.node.position,velocity=(0,random.randint(0,10),0),count=int(1+random.random()*12),scale=random.random()*5,spread=random.uniform(0.1,0.4),chunkType='sweat')
                   except AttributeError: pass
            else:
                self.fireDamageTimer = bs.Timer(1,bs.Call(dummy))
                self.litSound.delete()
                self.killFire()      
        def dummy(): pass
        
        # Was the victim on fire before?
        if not self.onFire:
            import math
        
            # Set the variable and necessary timers to make it work
            self.onFire = True
            bs.emitBGDynamics(position=self.node.position,velocity=(0,0,0),count=10,emitType='tendrils',tendrilType='smoke')
            
            self.fireTimer = bs.Timer(self.time,bs.Call(self.killFire))
            self.fireDamageTimer = bs.Timer(250,bs.Call(fireDamage),repeat=True)
            
            self.litSound = bs.newNode('sound',owner=self.node,attrs={'sound':factory.burningSound,'volume':0.55})
            self.node.connectAttr('positionCenter',self.litSound,'position')
            
            # Create a visualization
            self.flameLight = bs.newNode('light',
                               owner=self.node,
                               attrs={'position':self.node.position,
                                      'radius':0.15,
                                      'heightAttenuated':False,
                                      'color': (1.0,0.5,0.0)})
            bs.animate(self.flameLight,'intensity',{0:0.5,150:0.35,275:0.65,350:0.9,400:0.5},loop=True)
            self.node.connectAttr('positionCenter',self.flameLight,'position')
            
        else:
            # Reset the timer if Spaz was already lit
            self.fireTimer = bs.Timer(gFireDuration,bs.Call(self.killFire))
        
    def diceEffect(self,type,special):
        """
        Does some stuff after hitting the dice.
        """
        
        # Do some stuff depending on the type
        if type == 'ironskin':
            self.node.style = 'cyborg'
            if self._impactScale != 1.0: return
            self._impactScale = self._impactScale*0.55
        elif type == 'kaboom':
            blast = bs.Blast(position=self.node.position,
                       hitType='normal',hitSubType='normal',
                       blastRadius=9.0,
                       blastType='normal',
                       sourcePlayer=self.sourcePlayer).autoRetain()
        elif type == 'overdriveCurse':
            self.overcharged = True
            self.curse()
        elif type == 'hijumpBoost':
            self.node.handleMessage(bs.PowerupMessage(powerupType='hijump'))
            self.stockBombCount = 8
            self.node.counterText = 'x'+str(self.stockBombCount)
        elif type == 'lowGravity':
            def _lowGrav():
                if self.node.exists() and not self.footing:
                    self.node.handleMessage('impulse',self.node.position[0],self.node.position[1],self.node.position[2],
                                    0,0,0,
                                    15,15,0,0,0,1,0)
            self.lowGravityTimer = bs.Timer(50,bs.Call(_lowGrav),repeat=True)
        elif type == 'powerups':
            import bsPowerup
            import random
            bs.shakeCamera(2)
            bs.emitBGDynamics(
                        position=(self.node.position[0],
                                  self.node.position[1]+4,
                                  self.node.position[2]),
                        velocity=(0, 0, 0),
                        count=700,
                        spread=0.7,
                        chunkType='spark')
            bs.Powerup(
                        position=(self.node.position[0]+random.uniform(-2.9,2.9),
                                  self.node.position[1]+3,
                                  self.node.position[2]+random.uniform(-2.9,2.9)),
                        powerupType=bsPowerup.PowerupFactory().getRandomPowerupType(),
                        expire=True).autoRetain()

            bs.Powerup(
                        position=(self.node.position[0]+random.uniform(-2.9,2.9),
                                  self.node.position[1]+3,
                                  self.node.position[2]+random.uniform(-2.9,2.9)),
                        powerupType=bsPowerup.PowerupFactory().getRandomPowerupType(),
                        expire=True).autoRetain()

            bs.Powerup(
                        position=(self.node.position[0]+random.uniform(-2.9,2.9),
                                  self.node.position[1]+3,
                                  self.node.position[2]+random.uniform(-2.9,2.9)),
                        powerupType=bsPowerup.PowerupFactory().getRandomPowerupType(),
                        expire=True).autoRetain()

            bs.Powerup(
                        position=(self.node.position[0]+random.uniform(-2.9,2.9),
                                  self.node.position[1]+3,
                                  self.node.position[2]+random.uniform(-2.9,2.9)),
                        powerupType=bsPowerup.PowerupFactory().getRandomPowerupType(),
                        expire=True).autoRetain()
            
        elif type == 'totalReset':
            def dummy(): pass
            self._bombWearOffFlashTimer = bs.Timer(1,bs.Call(dummy))
            self._bombWearOffTimer = bs.Timer(1,bs.Call(dummy))
            self._multiBombWearOffFlashTimer = bs.Timer(1,bs.Call(dummy))
            self._multiBombWearOffTimer = bs.Timer(1,bs.Call(dummy))
            self._boxingGlovesWearOffFlashTimer = bs.Timer(1,bs.Call(dummy))
            self._boxingGlovesWearOffTimer = bs.Timer(1,bs.Call(dummy))
            self._slowDurationTimer = None
            self._jumpCooldown = 50
        
            self.node.jumpPressed = True
            self.node.jumpPressed = False
            
            self.bombType = self.defaultBombType
            
            t = bs.getGameTime()
            self.node.miniBillboard1StartTime = t
            self.node.miniBillboard1EndTime = t+1
            self.node.miniBillboard2StartTime = t
            self.node.miniBillboard2EndTime = t+1
            self.node.miniBillboard3StartTime = t
            self.node.miniBillboard3EndTime = t+1
            
            self.stockBombType = None
            self.node.counterText = ''
            self.stockBombCount = 0
            
            self.node.billboardOpacity = 0.0
            
            self.lowGravityTimer = None
            self.regenTimer = None
            self.endRegenTimer = None
            
            if self.shield != None:
                self.shieldSound.delete()
                self.shield.delete()
                self.shield = None
                bs.playSound(self.getFactory().shieldDownSound,1.0,position=self.node.position)
            
            self.setBombCount(self.defaultBombCount)
            self.blastRadiusBuffed = False
            
            self._hasSpeedBoots = False
            self._hasBoxingGloves = False
            self.alreadyHealed = False
            self.healStacks = 0
            self.node.boxingGloves = 0
            
            if self._cursed:
                if self.overcharged:
                    self.overcharged = False
                    self.overchargedLight.delete()
                    
                self._cursed = False
                self.sound.delete() # Stop the curse sound
                # remove cursed material
                factory = self.getFactory()
                for attr in ['materials','rollerMaterials']:
                    materials = getattr(self.node,attr)
                    if factory.curseMaterial in materials:
                        setattr(self.node,attr,tuple(m for m in materials if m != factory.curseMaterial))
                self.node.curseDeathTime = 0
            if (self.hitPoints > self.hitPointsOverdriveTooMuch):
                self.hitPoints = self.hitPointsOverdriveTooMuch
            elif (self.hitPoints < self.hitPointsMax):
                self.hitPoints = self.hitPointsMax
            else:
                self.hitPoints = self.hitPoints
            self.node.hurt = 0
            self._lastHitTime = None
            self._numTimesHit = 0
            if self.onFire: self.killFire()
            
            
        elif type == 'pigCurse':
            self.node.handleMessage(bs.PowerupMessage(powerupType='stickyBombs')) # Gives the player Sticky Bombs
            self.node.handleMessage(bs.PowerupMessage(powerupType='tripleBombs')) # Triple Bombs!
            
            # Let's change some models around
            self.sounds = [bs.getSound('mel01'),
                           bs.getSound('mel02'),
                           bs.getSound('mel03'),
                           bs.getSound('mel04'),
                           bs.getSound('mel05'),
                           bs.getSound('mel06'),
                           bs.getSound('mel07'),
                           bs.getSound('mel08'),
                           bs.getSound('mel09'),
                           bs.getSound('mel10'),]
            self.node.attackSounds = self.sounds
            self.node.jumpSounds = self.sounds
            self.node.impactSounds = self.sounds
            self.node.pickupSounds = self.sounds
            self.node.deathSounds = [bs.getSound('melDeath01')]
            self.node.fallSounds = [bs.getSound('melFall01')]
            self.node.colorTexture = bs.getTexture('melColor')
            self.node.colorMaskTexture = bs.getTexture('melColorMask')
            self.node.headModel = bs.getModel('melHead')
            self.node.torsoModel = bs.getModel('melTorso')
            self.node.pelvisModel = bs.getModel('kronkPelvis')
            self.node.upperArmModel = bs.getModel('melUpperArm')
            self.node.upperLegModel = bs.getModel('melUpperLeg')
            self.node.foreArmModel = bs.getModel('melForeArm')
            self.node.handModel = bs.getModel('melHand')
            self.node.toesModel = bs.getModel('melToes')
            self.node.lowerLegModel = bs.getModel('melLowerLeg')
            self.node.color=gDefaultBotColor
            self.node.highlight=gDefaultBotHighlight
            self.node.style = 'mel'
        elif type == 'iceMeteor':
            def icyMeteor():
                import random
                self.height = 5.6
                pos = self.node.position
                vel = (self.node.velocity[0]/1.5,self.node.velocity[1]/1.5,self.node.velocity[2]/1.5)
                bomb = bs.Bomb(position=(pos[0]+random.uniform(-4.2,4.2),pos[1]+self.height,pos[2]+random.uniform(-4.2,4.2)),velocity=(0,0,0),owner=self.node,sourcePlayer=self.sourcePlayer,bombType='iceMeteor').autoRetain()
            bs.gameTimer(190,icyMeteor)
        elif type == 'impactRain':
            import random
            def drop():
                try:
                    self.height = 5
                    pos = self.node.position
                    vel = (self.node.velocity[0]/1.5,self.node.velocity[1]/1.5,self.node.velocity[2]/1.5)
                    bomb = bs.Bomb(position=(pos[0]+vel[0],pos[1]+self.height,pos[2]+vel[2]),velocity=(0,2,0),sourcePlayer=self.sourcePlayer,owner=self.node,bombType='impact').autoRetain()
                except AttributeError: pass
            for i in range(15):
                try:
                    bs.gameTimer(i*200,bs.Call(drop))
                    i += 1
                except AttributeError: pass
        elif type == 'goodBurger':
            self.burgerSound = bs.getSound('goodburger')
            bs.playSound(self.burgerSound,volume=1.25)
            def drop():
                self.height = 5
                pos = self.node.position
                vel = (self.node.velocity[0]/1.5,self.node.velocity[1]/1.5,self.node.velocity[2]/1.5)
                bomb = bs.Bomb(position=(pos[0]+vel[0],pos[1]+self.height,pos[2]+vel[2]),velocity=(0,0,0),owner=self.node,sourcePlayer=self.sourcePlayer,bombType='burger').autoRetain()
            bs.gameTimer(3200,bs.Call(drop))
        else:
            raise Exception('type doesn\'t exist')
            
        # Create some partcles if it's an effect worth showing. It has to be a spiral.
        if special:
            def particle(x,y,z): 
                try:
                    import random
                    self.x = x*1
                    self.y = y*1
                    bs.emitBGDynamics(position=(self.node.position[0]+self.x,self.node.position[1]+self.y,self.node.position[2]+z),velocity=self.node.velocity,count=random.randrange(10,15),scale=0.8,spread=0.05,chunkType='spark')
                except AttributeError: pass
            
            self.diceAura = bs.newNode('light',
                           attrs={'position':self.node.position,
                                  'color': (1.0,1.0,1.0),
                                  'volumeIntensityScale': 0.5})     
            bs.animate(self.diceAura,'intensity',{0:0,350:0.25,2000:0},loop=False)
            self.node.connectAttr('position',self.diceAura,'position')
            bs.gameTimer(2000,self.diceAura.delete)   
            
            bs.playSound(self.getFactory().mysterySound,volume=1.0,position=self.node.position)
            self.space = 75
            self.height = 0.075
            bs.gameTimer(1,bs.Call(particle,0,0,1))
            bs.gameTimer(self.space,bs.Call(particle,0.5,self.height,0.5))
            bs.gameTimer(self.space*2,bs.Call(particle,1,self.height*2,0))
            bs.gameTimer(self.space*3,bs.Call(particle,0.5,self.height*3,-0.5))
            bs.gameTimer(self.space*4,bs.Call(particle,0,self.height*4,-1))
            bs.gameTimer(self.space*5,bs.Call(particle,-0.5,self.height*5,-0.5))
            bs.gameTimer(self.space*6,bs.Call(particle,-1,self.height*6,0))
            bs.gameTimer(self.space*7,bs.Call(particle,-0.5,self.height*7,0.5))
            bs.gameTimer(self.space*8,bs.Call(particle,0,self.height*8,1))
            bs.gameTimer(self.space*9,bs.Call(particle,0.5,self.height*9,0.5))
            bs.gameTimer(self.space*10,bs.Call(particle,0.5,self.height*10,0.5))
            bs.gameTimer(self.space*11,bs.Call(particle,1,self.height*11,0))
            bs.gameTimer(self.space*12,bs.Call(particle,0.5,self.height*12,-0.5))
            bs.gameTimer(self.space*13,bs.Call(particle,0,self.height*13,-1))
            bs.gameTimer(self.space*14,bs.Call(particle,-0.5,self.height*14,-0.5))
            bs.gameTimer(self.space*15,bs.Call(particle,-1,self.height*15,0))
            bs.gameTimer(self.space*16,bs.Call(particle,-0.5,self.height*16,0.5))
            bs.gameTimer(self.space*17,bs.Call(particle,0,self.height*17,1))
            bs.gameTimer(self.space*18,bs.Call(particle,0.5,self.height*18,0.5))
            bs.gameTimer(self.space*19,bs.Call(particle,1,self.height*19,0))
            bs.gameTimer(self.space*20,bs.Call(particle,0.5,self.height*20,-0.5))
            bs.gameTimer(self.space*21,bs.Call(particle,0,self.height*21,-1))
            bs.gameTimer(self.space*22,bs.Call(particle,-0.5,self.height*22,-0.5))
            bs.gameTimer(self.space*23,bs.Call(particle,-1,self.height*23,0))
            bs.gameTimer(self.space*24,bs.Call(particle,-0.5,self.height*24,0.5))
            bs.gameTimer(self.space*25,bs.Call(particle,0,self.height*25,1))
            bs.gameTimer(self.space*26,bs.Call(particle,0.5,self.height*26,0.5))
        
    def onFinalize(self):
        bs.Actor.onFinalize(self)

        # release callbacks/refs so we don't wind up with dependency loops..
        self._droppedBombCallbacks = []
        self.punchCallback = None
        self.pickUpPowerupCallback = None
        
    def addDroppedBombCallback(self,call):
        """
        Add a call to be run whenever this Spaz drops a bomb.
        The spaz and the newly-dropped bomb are passed as arguments.
        """
        self._droppedBombCallbacks.append(call)
                            
    def isAlive(self):
        """
        Method override; returns whether ol' spaz is still kickin'.
        """
        return not self._dead
        
    @classmethod
    def getFactory(cls):
        """
        Returns the shared bs.SpazFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        if activity is None: 
            #return None
            raise Exception("no current activity")
        try: return activity._sharedSpazFactory
        except Exception:
            f = activity._sharedSpazFactory = SpazFactory()
            return f

    def exists(self):
        return self.node.exists()

    def _hideScoreText(self):
        if self._scoreText.exists():
            bs.animate(self._scoreText,'scale',{0:self._scoreText.scale,200:0})
            
    def _turboFilterAddPress(self, source):
        """
        Can pass all button presses through here; if we see an obscene number
        of them in a short time let's shame/pushish this guy for using turbo
        """
        t = bs.getNetTime()
        tBucket = int(t/1000)
        if tBucket == self._turboFilterTimeBucket:
            # add only once per timestep (filter out buttons triggering multiple actions)
            if t != self._turboFilterTimes.get(source, 0):
                self._turboFilterCounts[source] = self._turboFilterCounts.get(source, 0) + 1
                self._turboFilterTimes[source] = t
                # (uncomment to debug; prints what this count is at)
                # bs.screenMessage(str(source)+" "+str(self._turboFilterCounts[source]))
                if self._turboFilterCounts[source] == 15:
                    
                    # knock 'em out.  That'll learn 'em.
                    self.node.handleMessage("knockout", 500.0)

                    # also issue periodic notices about who is turbo-ing
                    realTime = bs.getRealTime()
                    global gLastTurboSpamWarningTime
                    if realTime > gLastTurboSpamWarningTime + 30000:
                        gLastTurboSpamWarningTime = realTime
                        bs.screenMessage(bs.Lstr(translate=('statements','Warning to ${NAME}:  turbo / button-spamming knocks you out.'),subs=[('${NAME}',self.node.name)]),color=(1,0.5,0))
                        bs.playSound(bs.getSound('error'))
        else:
            self._turboFilterTimes = {}
            self._turboFilterTimeBucket = tBucket
            self._turboFilterCounts = {source:1}

    def setScoreText(self,t,color=(1,1,0.4),flash=False):
        """
        Utility func to show a message momentarily over our spaz that follows him around;
        Handy for score updates and things.
        """
        colorFin = bs.getSafeColor(color)[:3]
        if not self.node.exists(): return
        try: exists = self._scoreText.exists()
        except Exception: exists = False
        if not exists:
            startScale = 0.0
            m = bs.newNode('math',owner=self.node,attrs={'input1':(0,1.4,0),'operation':'add'})
            self.node.connectAttr('torsoPosition',m,'input2')
            self._scoreText = bs.newNode('text',
                                          owner=self.node,
                                          attrs={'text':t,
                                                 'inWorld':True,
                                                 'shadow':1.0,
                                                 'flatness':1.0,
                                                 'color':colorFin,
                                                 'scale':0.02,
                                                 'hAlign':'center'})
            m.connectAttr('output',self._scoreText,'position')
        else:
            self._scoreText.color=colorFin
            startScale = self._scoreText.scale
            self._scoreText.text = t
        if flash:
            combine = bs.newNode("combine",owner=self._scoreText,attrs={'size':3})
            sc = 1.8
            offs = 0.5
            t = 300
            for i in range(3):
                c1 = offs+sc*colorFin[i]
                c2 = colorFin[i]
                bs.animate(combine,'input'+str(i),{0.5*t:c2,
                                                   0.75*t:c1,
                                                   1.0*t:c2})
            combine.connectAttr('output',self._scoreText,'color')
            
        bs.animate(self._scoreText,'scale',{0:startScale,200:0.02})
        self._scoreTextHideTimer = bs.Timer(1000,bs.WeakCall(self._hideScoreText))


    def onPickUpPress(self):
        """
        Called to 'press pick-up' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        t = bs.getGameTime()
        
        opposingNode = self.spazHoldingMe
        if self.pickupCounterVictim and opposingNode.holdNode.exists() and self.node.dead != True: 
            opposingNode.holdNode = bs.Node(None)
            force = 200
            counterForce = 100
            directionX = (opposingNode.position[0] - self.node.position[0]) * 1.5
            directionY = (opposingNode.position[1] - self.node.position[1]) + 1
            directionZ = (opposingNode.position[2] - self.node.position[2]) * 1.5
            opposingNode.handleMessage("knockout", 300.0)
            # The guy who failed the counter gets launched away
            opposingNode.handleMessage('impulse',self.node.position[0],self.node.position[1],self.node.position[2],
                                opposingNode.velocity[0],opposingNode.velocity[1],opposingNode.velocity[2],
                                force,force,0,0,directionX,directionY,directionZ)
            # Make sure the guy who does the countering stays on the ground (apply force down)
            self.node.handleMessage('impulse',self.node.position[0],self.node.position[1],self.node.position[2],
                                0,0,0,
                                counterForce,counterForce,0,0,0,-1,0)
                                
            self.counterText.text = "Counter!"
            bs.animate(self.counterText,'opacity',{0:0.5,
                                                   500:1.0,
                                                   1500:0.0},loop=False)
                                
            # The guy who failed the counter receives some damage
            opposingNode.handleMessage(bs.HitMessage(flatDamage=gPickupCounterDamage,hitSubType='pickupCounter',sourcePlayer=self.node.sourcePlayer))
            
            bs.playSound(self.getFactory().pickupCounterSound,2.0,position=self.node.position)
            counterExp = bs.newNode("explosion",
                                    attrs={'position':(self.node.position[0],self.node.position[1]+0.25,self.node.position[2]),
                                           'velocity':(0,0,0),
                                           'color':self.node.color,
                                           'radius':1,
                                           'big':False})
            self.counterLight = bs.newNode('light',
            attrs={'position':opposingNode.position,
                    'color': self.node.highlight,
                    'radius':1,
                    'volumeIntensityScale': 0.25}) 
            bs.animate(self.counterLight,'intensity',{0:1,500:0},loop=False)
            bs.statAdd('Pickups Countered')
            return
        
        if self.node.holdNode.exists() and self.ninjaThrow: 
            self.ninjaThrow = False
            bs.playSound(self.getFactory().ninjaThrowSound,0,position=self.node.position)
        
        if t - self.lastPickupTime >= self._pickupCooldown:
            self.node.pickUpPressed = True
            self.lastPickupTime = t
        self._turboFilterAddPress('pickup')
        
        def _safeSetAttr(node,attr,val):
            if node.exists(): setattr(node,attr,val)

        if not self.getActivity()._map.isHockey:
            if self._hasSpeedBoots and self.node.run > 0.5:
                if self.node.holdNode.exists():
                    bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'hockey',True))
                else:
                    bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'hockey',False))

    def onPickUpRelease(self):
        """
        Called to 'release pick-up' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        self.node.pickUpPressed = False

    def _onHoldPositionPress(self):
        """
        Called to 'press hold-position' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.holdPositionPressed = True
        self._turboFilterAddPress('holdposition')

    def _onHoldPositionRelease(self):
        """
        Called to 'release hold-position' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.holdPositionPressed = False
        
    def punchReset(self):
        """
        Reset the punch cooldown after not punching for long
        """
        self.punches = 0
        if self._hasBoxingGloves: 
            self._punchCooldown = gSuperPunchCooldown
            self._punchPowerScale = gSuperPunchPowerScale
        elif self._hasSpeedBoots:
            self._punchCooldown = gSpeedPunchCooldown
            self._punchPowerScale = gSpeedPunchPowerScale
        else: 
            self._punchCooldown = gBasePunchCooldown
            self._punchPowerScale = gBasePunchPowerScale

    def onPunchPress(self):
        """
        Called to 'press punch' on this spaz;
        used for player or AI connections.
        """
        
        if not self.node.exists() or self.frozen or self.node.knockout > 0.0: return
        calc = bs.getGameTime() - self.lastPunchTime
        def _midAir(): self._afterJump = False
        self._afterJumpTimer = bs.gameTimer(60,bs.Call(_midAir))
        self._dash()
        # Punch leniency. You don't need to wait perfect amount of time for the next punch to occur.
        if calc >= self._punchCooldown*0.7:
            def _punch():
                self.punchPressed = False
                if self.punchCallback is not None: 
                    self.punchCallback(self)
                
                self._punchedNodes = set() # reset this..
                self.lastPunchTime = bs.getGameTime()
                
                # Punching too much will increase the cooldown, stop punching for a while to restart it
                self.punches += 1
                if self.punches > gPunchTimes: self.punches = gPunchTimes 
                if self._hasBoxingGloves: 
                    self._punchPowerScale = gSuperPunchPowerScale - (self.punches*gPunchPowerDecrease)
                elif self._hasSpeedBoots:
                    self._punchPowerScale = gSpeedPunchPowerScale - (self.punches*gPunchPowerDecrease)
                else: 
                    self._punchPowerScale = gBasePunchPowerScale - (self.punches*gPunchPowerDecrease)
                self.punchResetTimer = bs.Timer((self._punchCooldown+500),bs.WeakCall(self.punchReset))
                
                self.node.punchPressed = True
                if not self.node.holdNode.exists():
                    punches = self.getFactory().swishSounds
                    punch = punches[random.randrange(len(punches))]
                    bs.gameTimer(100,bs.WeakCall(self._safePlaySound,punch,0.6))
                self._turboFilterAddPress('punch')
            
            bs.gameTimer(max(1,self._punchCooldown-calc),bs.Call(_punch))
            
                
                
    def _dash(self):
        isMoving = abs(self.node.moveUpDown) >= 0.75 or abs(self.node.moveLeftRight) >= 0.75
        if isMoving and self._afterJump and not self.node.holdNode.exists() and self._ableToDodge:
            dashPower = 350
            pos = self.node.position
            vel = self.node.velocity
            
            self._ableToDodge = False
            def _cooldownRefresh(): 
                self._ableToDodge = True
                if self.node.exists():
                    bs.playSound(self.getFactory().dashRechargeSound,0.5,position=self.node.position)
                    bs.animate(self.dashCooldownText,'opacity',{0:1.0,300:1.0,750:0.0},loop=False)
            bs.gameTimer(gDodgeCooldown,bs.Call(_cooldownRefresh))
            
            self.node.handleMessage("flash")
            
            #self.node.handleMessage("knockout", 100.0)
            def _dashSound(step): self.node.handleMessage("jumpSound")
                            
            self.node.handleMessage("impulse",pos[0],pos[1]+0.6,pos[2],
                                    0,0,0,
                                    dashPower,0,0,0,self.node.moveLeftRight,0,-self.node.moveUpDown)
            self.node.handleMessage('celebrate',400)  
            self.dashSound = bs.Timer(50,bs.Call(_dashSound,1))
            
                                    
            
            self._duringDodge = True
            def _noResistance(): self._duringDodge = False
            self.dodgeResistanceTimer = bs.Timer(200,bs.Call(_noResistance))
            
            self.dodgeLight = bs.newNode('light',
                        attrs={'position':self.node.position,
                                'color': (1,1,1),
                                'volumeIntensityScale': 1.0}) 
            bs.animate(self.dodgeLight,'intensity',{0:0,100:0.5,200:0},loop=False)
            bs.gameTimer(200,self.dodgeLight.delete) 
            
            dashExp = bs.newNode("explosion", attrs={
                'position':pos,
                'velocity':(0,0,0),
                'radius':0.5,})
                                    
            def _trail():
                bs.emitBGDynamics(position=self.node.position,
                    chunkType='sweat',
                    count=5,
                    scale=3.0,
                    spread=0.6);
                bs.emitBGDynamics(position=self.node.position,
                    chunkType='spark',
                    count=5,
                    scale=1.0,
                    spread=0.1);
            bs.gameTimer(5,bs.Call(_trail))
            bs.gameTimer(155,bs.Call(_trail))
            bs.gameTimer(220,bs.Call(_trail))
            bs.gameTimer(280,bs.Call(_trail))
                    
                                    
            bs.playSound(self.getFactory().dodgeSound,1.0,position=self.node.position)
                
    
    def buddyAwesomeMoves(self):
        self.node.handleMessage('attackSound')
        self.node.moveLeftRight = random.randint(-1.0,1.0)
        self.node.moveUpDown = random.randint(-1.0,1.0)
        if random.randrange(1,100) > 85:
            self.onPunchPress()
            self.onJumpPress()
            self.onPunchRelease()
            self.onJumpRelease()
        if random.randrange(1,15) < 4: 
            self.onJumpPress()
            self.onJumpRelease()
        if random.randrange(1,40) < 15: 
            self.onPickUpPress()
            self.onPickUpRelease()
        
    def _safePlaySound(self,sound,volume):
        """
        Plays a sound at our position if we exist.
        """
        if self.node.exists():
            bs.playSound(sound,volume,self.node.position)
        
    def onPunchRelease(self):
        """
        Called to 'release punch' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.punchPressed = False

    def onBombPress(self):
        """
        Called to 'press bomb' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        
        if self._dead or self.frozen: return
        if (self.stockBombType != 'hijump' or self.defaultBombType != 'hijump') and self.node.knockout > 0.0: return # Ignore stun when Hijump is used
        t = bs.getGameTime()
        if t - self.lastBombTime >= self._bombCooldown:
            self.lastBombTime = t
            self.node.bombPressed = True
            
            def _safeSetAttr(node,attr,val):
                if node.exists(): setattr(node,attr,val)
        
            # Use Speed Boots if you have them.
            if not self.getActivity()._map.isHockey and self._hasSpeedBoots and self.node.run > 0.5 and self.node.holdNode.exists():
                bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'hockey',True))
            
            if not self.node.holdNode.exists(): self.dropBomb()
        self._turboFilterAddPress('bomb')

    def onBombRelease(self):
        """
        Called to 'release bomb' on this spaz; 
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.bombPressed = False
        
    def onJumpPress(self):
        """
        Called to 'press jump' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        t = bs.getGameTime()
        if t - self.lastJumpTime >= self._jumpCooldown:
            self.node.jumpPressed = True
            self._afterJump = True
            def _midAir(): self._afterJump = False
            self._afterJumpTimer = bs.gameTimer(55,bs.Call(_midAir))
            if bs.getConfig().get('Cheat RJ',True) and self.footing:
                self._jumpCooldown = 550
                self.node.handleMessage('impulse',self.node.position[0],self.node.position[1],self.node.position[2],
                                        0,0,0,
                                        200,200,0,0,0,1,0)
            if self.lowGravityTimer is not None and self.footing:
                self.node.handleMessage('impulse',self.node.position[0],self.node.position[1],self.node.position[2],
                                        0,0,0,
                                        100,100,0,0,0,1,0)
            if bs.getGameTime() - self.lastPunchTime<=350 and self.node.punchPressed and self.node.jumpPressed and bs.getGameTime() - self.lastBackflipTime >= self._backflipCooldown and bs.getConfig()['Enable Backflips'] == True:
                if not self._kick:
                    factory = self.getFactory()
                    self._kick = True
                    #add kick material
                    for attr in ['materials', 'rollerMaterials']:
                        materials = getattr(self.node, attr)
                        if not factory.kickMaterial in materials:
                            setattr(self.node, attr, materials + (factory.kickMaterial,))
                self.node.handleMessage("impulse",self.node.position[0],self.node.position[1]-3,self.node.position[2],self.node.velocity[0],self.node.velocity[1],self.node.velocity[2],50*self.node.run,10*self.node.run,0,0,self.node.velocity[0],self.node.velocity[1],self.node.velocity[2])
                self.node.handleMessage("impulse",self.node.position[0],self.node.position[1]-5,self.node.position[2],self.node.velocity[0],self.node.velocity[1],self.node.velocity[2],50*self.node.run,20*self.node.run,0,0,self.node.velocity[0],self.node.velocity[1],self.node.velocity[2])
                self.node.handleMessage("impulse",self.node.position[0],self.node.position[1]-5,self.node.position[2],0,10,0,50,20,0,0,0,10,0)
                bs.emitBGDynamics(position=(self.node.position[0],self.node.position[1]-0.2,self.node.position[2]), velocity=(self.node.velocity[0]*5,self.node.velocity[1]*2,self.node.velocity[2]), count=random.randrange(12,20), scale=0.35, spread=0.31, chunkType='spark')
                def _stopSlowmo(): bs.getSharedObject('globals').slowMotion = False
                def _startSlowmo(): bs.getSharedObject('globals').slowMotion = True
                #if not bs.getActivity()._isSlowMotion: # Slow down the game for a brief moment
                #    bs.netTimer(15,bs.Call(_startSlowmo)) #15
                #    bs.netTimer(60,bs.Call(_stopSlowmo)) #60
                self._kickedNodes = set()
                def _backflipText():
                    if self.node.exists():
                        bs.animate(self.backflipCooldownText,'opacity',{0:1.0,300:1.0,750:0.0},loop=False)
                bs.gameTimer(gBackflipCooldown,bs.Call(_backflipText))
                self.lastBackflipTime = t
            self.lastJumpTime = t
        self._turboFilterAddPress('jump')

    def onJumpRelease(self):
        """
        Called to 'release jump' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        self.node.jumpPressed = False
        if self._kick and bs.getConfig()['Enable Backflips'] == True:
            self._kick = False
            # remove kick material
            factory = self.getFactory()
            for attr in ['materials', 'rollerMaterials']:
                materials = getattr(self.node, attr)
                if factory.kickMaterial in materials:
                    setattr(self.node, attr, tuple(m for m in materials if m != factory.kickMaterial))

    def onRun(self,value):
        """
        Called to 'press run' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        
        t = bs.getGameTime()
        self.lastRunTime = t
        self.node.run = value

        # filtering these events would be tough since its an analog
        # value, but lets still pass full 0-to-1 presses along to
        # the turbo filter to punish players if it looks like they're turbo-ing
        if self._lastRunValue < 0.01 and value > 0.99:
            self._turboFilterAddPress('run')
            
        self._lastRunValue = value
        
        def _safeSetAttr(node,attr,val):
            if node.exists(): setattr(node,attr,val)
        
        # Use Speed Boots if you have them.
        if not self.getActivity()._map.isHockey:
            if self._hasSpeedBoots and value > 0.5 and not self.node.holdNode.exists():
                bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'hockey',True))
            else:
                bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'hockey',False))

    def onFlyPress(self):
        """
        Called to 'press fly' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.flyPressed = True
        self._turboFilterAddPress('fly')

    def onFlyRelease(self):
        """
        Called to 'release fly' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.flyPressed = False

    def onMove(self,x,y):
        """
        Called to set the joystick amount for this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.handleMessage("move",x,y)
        
    def onMoveUpDown(self,value):
        """
        Called to set the up/down joystick amount on this spaz;
        used for player or AI connections.
        value will be between -32768 to 32767
        WARNING: deprecated; use onMove instead.
        """
        if not self.node.exists(): return
        if self.dizzy: value *= -1
        self.node.moveUpDown = value

    def onMoveLeftRight(self,value):
        """
        Called to set the left/right joystick amount on this spaz;
        used for player or AI connections.
        value will be between -32768 to 32767
        WARNING: deprecated; use onMove instead.
        """
        if not self.node.exists(): return
        if self.dizzy: value *= -1
        self.node.moveLeftRight = value

    def onPunched(self,damage):
        """
        Called when this spaz gets punched.
        """
        pass

    def onKicked(self,damage):
        """
        Called when this spaz gets kicked.
        """
        pass

    def getDeathPoints(self,how):
        'Get the points awarded for killing this spaz'
        numHits = float(max(1,self._numTimesHit))
        # base points is simply 10 for 1-hit-kills and 5 otherwise
        importance = 2 if numHits < 2 else 1
        return ((10 if numHits < 2 else 5) * self.pointsMult,importance)

    def curse(self):
        """
        Give this poor spaz a curse;
        he will explode in 8 seconds.
        """
        if not self._cursed:
            if self.stockBombType == 'healBomb' and self.stockBombCount > 0: # Don't curse the players that have Healing Bombs in their inventory. Instead of cursing, remove one from the stock.
                self.setStockBombs('removeOne')
                self.node.handleMessage(bs.HealMessage(self.sourcePlayer))
            else:
                factory = self.getFactory()
                self._cursed = True
                if bs.getConfig().get('Offensive Curse Sound', True):
                    self.sound = bs.newNode('sound',owner=self.node,attrs={'sound':factory.curseOffensiveSound,'volume':1.0})
                else:
                    self.sound = bs.newNode('sound',owner=self.node,attrs={'sound':factory.curseSound,'volume':1.0})
                if self.overcharged == True:
                    self.overchargedLight = bs.newNode('light',
                           owner=self.node,
                           attrs={'position':self.node.position,
                                  'color': (0.6,0.05,0.6),
                                  'volumeIntensityScale': 0.25})   
                    bs.animate(self.overchargedLight,'intensity',{0:1.0,500:0.2},loop=True)
                    self.node.connectAttr('position',self.overchargedLight,'position')
                try: self.node.connectAttr('position',self.sound,'position')
                except StandardError: pass
                # add the curse material..
                for attr in ['materials','rollerMaterials']:
                    materials = getattr(self.node,attr)
                    if not factory.curseMaterial in materials:
                        setattr(self.node,attr,materials + (factory.curseMaterial,))
                # -1 specifies no time limit
                if self.curseTime == -1:
                    self.node.curseDeathTime = -1
                else:
                    if self.overcharged: 
                        self.node.curseDeathTime = bs.getGameTime()+12000
                        self.curseExplodeTimer = bs.Timer(12000,bs.WeakCall(self.curseExplode))
                    else: 
                        self.node.curseDeathTime = bs.getGameTime()+self.curseTime
                        self.curseExplodeTimer = bs.Timer(self.curseTime,bs.WeakCall(self.curseExplode))
        else:
            if not self.curseTime == -1:
                self.node.curseDeathTime = bs.getGameTime()+8000
                self.curseExplodeTimer = bs.Timer(8000,bs.WeakCall(self.curseExplode))
            
    def equipBoxingGloves(self):
        """
        Give this spaz some boxing gloves.
        """
        activity = self.getActivity()
        factory = self.getFactory()
        
        self.node.boxingGloves = 1
        self._hasBoxingGloves = True
        def _safeSetAttr(node,attr,val):
            if node.exists(): setattr(node,attr,val)
        if not self.getActivity()._map.isHockey: bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'hockey',False))
        self._hasSpeedBoots = False
        self._punchPowerScale = gSuperPunchPowerScale
        self._punchCooldown = gSuperPunchCooldown
        self.punchResetTimer = bs.Timer(1,bs.WeakCall(self.punchReset))
        
    def equipSpeed(self):
        """
        Give this spaz speed boots.
        """
        factory = self.getFactory()
        bs.playSound(factory.speedUpSound,position=self.node.position)
        self._hasBoxingGloves = False
        self._hasSpeedBoots = True
        def _safeSetAttr(node,attr,val):
            if node.exists(): setattr(node,attr,val)

        if not self.getActivity()._map.isHockey:
            if self._hasSpeedBoots and self.node.run > 0.5 and not self.node.holdNode.exists():
                bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'hockey',True))
            else:
                bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'hockey',False))
        
        self.node.boxingGloves = 0
        self._punchPowerScale = gSpeedPunchPowerScale
        self._punchCooldown = gSpeedPunchCooldown
        self.punchResetTimer = bs.Timer(1,bs.WeakCall(self.punchReset))
        
    def accolade(self,type,player,whoKilled):
        """
        Do some lights and a text for perfoming difficult maneuvers
        
        types
            The type of accolade you want to highlight. Available types:
            crit | gibKill | hijump
        """
        
        factory = self.getFactory()
        text = bs.Lstr(resource=type)
        
        def _stopSlowmo(): bs.getSharedObject('globals').slowMotion = False
        def _startSlowmo(): bs.getSharedObject('globals').slowMotion = True
        
        # apply some additional rules for FFA/Teams
        if not isinstance(bs.getSession(),bs.CoopSession):
            try: 
                if player.getTeam() != whoKilled.getTeam(): pass
                else: return # accolade won't be awarded if performed on your teammate
            except StandardError: pass # if for some reason you cannot get the team, assume it's the enemy and as such it counts
        
        if type == 'crit': 
            color=(1,0,0)
            sounds = self.getFactory().powerPunchSounds
            sound = sounds[random.randrange(len(sounds))]
            self.style(player,1,sound=False) # add style points for FFA/Team games
            if bs.getConfig().get('Camera Shake', True):
                bs.shakeCamera(intensity=1.0)
            bs.statAdd('CRIT Count')
            if not bs.getActivity()._isSlowMotion: # Slow down the game for a brief moment to underscore the power of the punch
                bs.netTimer(15,bs.Call(_startSlowmo))
                bs.netTimer(60,bs.Call(_stopSlowmo))
            
        elif type == 'gibKill':
            # style points handled somewhere else in GIBBED case
            color=(0,1,1)
            sound = factory.gibKillSound
            bs.statAdd('GIBBED Count')
        elif type == 'mineKill':
            color=(0.1,0.7,0)
            sound = factory.mineKillSound
            bs.statAdd('MINEXECUTION Count')
            self.style(player,2,sound=False) # add style points for FFA/Team games
        elif type == 'hijumpKill':
            color=(1,0,1)
            sound = factory.hijumpedSound
            bs.statAdd('HI-JUMPED Count')
            self.style(player,2,sound=False) # add style points for FFA/Team games
            if not bs.getActivity()._isSlowMotion: # Slow down the game for a brief moment to underscore the power of the jump
                bs.netTimer(15,bs.Call(_startSlowmo))
                bs.netTimer(60,bs.Call(_stopSlowmo))
        else:
            raise Exception('type not defined. Available: crit | gibKill | mineKill | hijumpKill')
            return
            
        bsUtils.PopupText((text),
            color=color,
            scale=1.6,
            position=self.node.position).autoRetain()
        self.light = bs.newNode('light',
            attrs={'position':self.node.position,
                    'color': color,
                    'volumeIntensityScale': 1.0}) 
        bs.animate(self.light,'intensity',{0:0,250:1.5,750:0},loop=False)
        bs.gameTimer(750,self.light.delete)  
        self.sweat = bs.emitBGDynamics(position=self.node.position,
                    chunkType='sweat',
                    count=60,
                    scale=4.0,
                    spread=0.6);
        self.sparks = bs.emitBGDynamics(position=self.node.position,
                    chunkType='spark',
                    count=45,
                    scale=1.0,
                    spread=1.0);
        bs.playSound(sound,2.0,position=self.node.position)
        
        player.actor.catchphrase()
        

    def equipShields(self):
        """
        Give this spaz a nice energy shield.
        """

        if not self.node.exists(): raise Exception('Can\'t equip shields; no node.')
        
        factory = self.getFactory()
        if self.shield is None: 
            self.shield = bs.newNode('shield',owner=self.node,
                                    attrs={'color':self.node.color,'radius':1.3})
            self.node.connectAttr('positionCenter',self.shield,'position')
            self.shieldSound = bs.newNode('sound',owner=self.node,attrs={'sound':factory.shieldIdleSound,'volume':0.55})
            self.node.connectAttr('position',self.shieldSound,'position')
        self.shieldHitPoints = self.shieldHitPointsMax = 800
        self.shield.hurt = 0
        self.shieldDecayed = False
        self.shield.radius = 1.3
        self.shield.color=self.node.color
        bs.playSound(factory.shieldUpSound,1.0,position=self.node.position)
        if not isinstance(bs.getSession(),bs.CoopSession):
            self.shieldDecayTimer = bs.Timer(20000,bs.WeakCall(self.shieldDecay)) # Only decay shields outside of Coop sessions
        
    def shieldDecay(self):
        factory = self.getFactory()
        if self.shield is not None:
            t = self.node.position
            self.shieldHitPoints = 0.000001
            self.shield.delete()
            self.shieldSound.delete()
            self.shieldDecayed = True
            self.shield = None
            self.shield = bs.newNode('shield',owner=self.node,
                                    attrs={'color':(0.7,0.7,0.7),'radius':1.0})
            self.node.connectAttr('positionCenter',self.shield,'position')
            bs.playSound(self.getFactory().shieldDecaySound,1.0,position=self.node.position)
            # emit some cool lookin sparks when the shield decays
            bs.emitBGDynamics(position=(t[0],t[1]+0.9,t[2]),
                            velocity=self.node.velocity,
                            count=random.randrange(30,50),scale=0.3,spread=1,chunkType='spark')
            self.shield.hurt = 1.0



            
    def style(self,player,points=1,sound=True):
        # add style points for FFA/Team games
        if not isinstance(bs.getSession(),bs.CoopSession):
            if bs.getActivity()._crowdActive and random.randint(0,1): 
                def _sound(): bs.playSound(self.getFactory().crowdClapSound,1.0)
                bs.gameTimer(600,_sound)
            if sound: bs.playSound(self.getFactory().styleSound,2.0,position=self.node.position)
            bs.getActivity().scoreSet.playerStyle(player,points)
            pass
        
    def handleMessage(self,m):
        import bsInternal
        self._handleMessageSanityCheck()

        if isinstance(m,bs.PickedUpMessage):
            self.node.handleMessage("hurtSound")
            self.node.handleMessage("pickedUp")
            # this counts as a hit
            self._numTimesHit += 1
            #opposingNode = m.node
         #   self.spazHoldingMe = opposingNode
            
            # Pick-up Counter mechanic
            self.pickupCounterVictim = True
            def _turnOff(): self.pickupCounterVictim = False
            try:
                bs.gameTimer(int(self._pickupCooldown*0.25),bs.Call(_turnOff))
            except StandardError: pass

        elif isinstance(m,bs.ShouldShatterMessage):
            # eww; seems we have to do this in a timer or it wont work right
            # (since we're getting called from within update() perhaps?..)
            bs.gameTimer(1,bs.WeakCall(self.shatter))

        elif isinstance(m,bs.ImpactDamageMessage):
            # eww; seems we have to do this in a timer or it wont work right
            # (since we're getting called from within update() perhaps?..)
            bs.gameTimer(1,bs.WeakCall(self._hitSelf,m.intensity))

        elif isinstance(m,bs.PowerupMessage):
            self.scale = 1.3 # Powerup Notification text size
            if self._dead: return True
            if self.pickUpPowerupCallback is not None:
                self.pickUpPowerupCallback(self)

            if (m.powerupType == 'tripleBombs'):
                tex = bs.Powerup.getFactory().texBomb
                self._flashBillboard(tex)
                self.setBombCount(3)
                self.blastRadiusBuffed = False
                self.blastRadius = self.defaultBlastRadius
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='tripleBombs')),
                                            color=(1,1,0),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard1Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard1StartTime = t
                    self.node.miniBillboard1EndTime = t+gPowerupWearOffTime
                    self._multiBombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._multiBombWearOffFlash))
                    self._multiBombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._multiBombWearOff))
            elif (m.powerupType == 'blastBuff'):
                tex = bs.Powerup.getFactory().texBlast
                self._flashBillboard(tex)
                self.setBombCount(self.defaultBombCount)
                self.blastRadiusBuffed = True
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='blastBuff')),
                                            color=(1,1,0),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard1Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard1StartTime = t
                    self.node.miniBillboard1EndTime = t+gPowerupWearOffTime
                    self._multiBombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._blastBuffWearOffFlash))
                    self._multiBombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._blastBuffWearOff))
            elif m.powerupType == 'landMines':
                self.setStockBombs('landMine')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='landMine')),
                                            color=(0.1,0.7,0),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'grenades':
                self.setStockBombs('grenade')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='grenade')),
                                            color=(0.57,0.82,0.6),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'hijump':
                self.setStockBombs('hijump')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='hijump')),
                                            color=(1,0.01,0.95),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'glueBombs':
                self.setStockBombs('glue')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='glue')),
                                            color=(1,1,1),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'healBombs':
                # if frozen, on fire or cursed, use up the healing bomb immediatey
                if self.frozen or self.onFire or self._cursed:
                    self.setStockBombs('removeOne')
                    self.node.handleMessage(bs.HealMessage(self.sourcePlayer))
                else: self.setStockBombs('healBomb')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='healBomb')),
                                            color=(1,0.4,0.7),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'dizzyCake':
                self.setStockBombs('cake')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='cakeBomb')),
                                            color=(1,1,1),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'clusterBomb':
                self.setStockBombs('cluster')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText("Trap Bomb",
                                            color=(0.65,0.7,0.86),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'gloo':
                self.setStockBombs('gloo')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText(
                                            'Gloo',
                                            color=(1,0.8,0.9),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'hunterBombs':
                self.bombType = 'hunter'
                tex = bs.getTexture("achievementFootballShutout")
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText(
                                            'Hunter Bombs',
                                            color=(0.6,0.2,0.2),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'digitalBombs':
                self.bombType = 'fraction'
                tex = bs.getTexture("black")
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText(
                                            'Digital Bombs',
                                            color=(0.3,0.3,0.3),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'infatuateBombs':
                self.bombType = 'infatuate'
                tex = bs.getTexture("bombHealingColor")
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText(
                                            'Infatuate Bombs',
                                            color=(1.4,0.7,0.8),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'scatterBombs':
                self.setStockBombs('scatter')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText(
                                            'Scatter Bomb',
                                            color=(1.0,0.79,0.70),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'tesla':
                self.setStockBombs('tesla')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='tesla')),
                                            color=(1,0.5,0),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'impactBombs':
                self.bombType = 'impact'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='impactBomb')),
                                            color=(0.6,0.6,0.6),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif m.powerupType == 'instantBomb':
                self.setStockBombs('instant')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText("Self-Destruct",
                                            color=(1.2,0.6,0.3),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'knockerBombs':
                self.bombType = 'knocker'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='knockerBomb')),
                                            color=(0.0,0.0,1.0),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif m.powerupType == 'stickyBombs':
                self.bombType = 'sticky'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='stickyBomb')),
                                            color=(0,1,0),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif m.powerupType == 'rangerBombs':
                self.bombType = 'ranger'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='rangerBomb')),
                                            color=(1,1,0.5),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif m.powerupType == 'combatBombs':
                self.bombType = 'combat'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='combatBomb')),
                                            color=(0,1,1),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif m.powerupType == 'dynamitePack':
                self.bombType = 'dynamite'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='dynamitePack')),
                                            color=(1,0,0),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif m.powerupType == 'punch':
                self._hasBoxingGloves = True
                self._hasSpeedBoots = False
                tex = bs.Powerup.getFactory().texPunch
                self._flashBillboard(tex)
                self.equipBoxingGloves()
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='punch')),
                                            color=(1,0.3,0.3),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.boxingGlovesFlashing = 0
                    self.node.miniBillboard3Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard3StartTime = t
                    self.node.miniBillboard3EndTime = t+gPowerupWearOffTime
                    self._boxingGlovesWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._glovesWearOffFlash))
                    self._boxingGlovesWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._glovesWearOff))
            elif m.powerupType == 'speed':
                tex = bs.Powerup.getFactory().texSpeed
                self._flashBillboard(tex)
                self.equipSpeed()
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='speed')),
                                            color=(0.75,1,0.1),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard3Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard3StartTime = t
                    self.node.miniBillboard3EndTime = t+gPowerupWearOffTime
                    self._boxingGlovesWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._speedWearOffFlash))
                    self._boxingGlovesWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._speedWearOff))
                    
            elif m.powerupType == 'shield':
                self.equipShields()
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='shield')),
                                            color=(0.7,0.5,1),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif m.powerupType == 'curse':
                self.curse()
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='curse')),
                                            color=(0.3,0,0.45),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif (m.powerupType == 'iceBombs'):
                self.bombType = 'ice'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='iceBomb')),
                                            color=(0,0.45,1.0),
                                            scale=1.0,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif (m.powerupType == 'bot'):
                try: botset = self.getActivity()._hitmenBots
                except:
                    self.getActivity()._hitmenBots = bs.BotSet()
                    botset = self.getActivity()._hitmenBots
                self.radius = 1
                self.height = 0
                for x in range(1):
                   pts = self.node.position
                   botset.spawnBot(random.choice([bs.SpazBot,
                                                           bs.ToughGuyBot,
                                                           bs.ChickBot,
                                                           bs.PirateBot,
                                                           bs.PirateBotRadius,
                                                           bs.MelBot,
                                                           bs.NinjaBot,
                                                           bs.BonesBot,
                                                           bs.BearBot,
                                                           bs.AgentBot,
                                                           bs.FrostyBot,
                                                           bs.PascalBot,
                                                           bs.WizardBot,
                                                           bs.PixelBot,
                                                           bs.BunnyBot,
                                                           bs.SantaBot,
                                                           bs.CyborgBot,
                                                           bs.DemonBot,
                                                           bs.AliBot,
                                                           bs.KlayBot,
                                                           bs.JesterBot,
                                                           bs.ZillBot,
                                                           bs.RonnieBot,
                                                           bs.JuiceBot,
                                                           bs.KnightBot,
                                                           bs.SoldierBot,
                                                           bs.DiceBot,
                                                           bs.CowBot,
                                                           bs.PuckBot,
                                                           bs.ArmoredBot,
                                                           bs.SpyBot, 
                                                           bs.LooieBot]), pos=(pts[0]+random.randrange(-self.radius,self.radius),pts[1]+self.height,pts[2]+random.randrange(-self.radius,self.radius)), spawnTime = 1000+1000*x)
                botset.startMoving()
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText(
                        'Wild Bot',
                         color=(0.9,0.7,1.1),
                         scale=self.scale,
                         position=self.node.position).autoRetain()
                                           
            elif (m.powerupType == 'fireBombs'):
                self.bombType = 'fire'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='fireBomb')),
                                            color=(1,0.7,0),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif (m.powerupType == 'pills'):
                def _endRegen(): #Clear up some variables.
                    self.alreadyHealed = False
                    self.regenTimer = None
                    self.healStacks = 0
                def _regenHP():
                    if not self.node.exists(): #Lets clear up some variables if the spaz is dead.
                       self.alreadyHealed = False
                       self.regenTimer = None
                       self.endRegenTimer = None
                       self.healStacks = 0
                    self.hitPoints = self.hitPoints + self.healStacks
                    if self.hitPoints >= self.hitPointsMax: #We put this so the regen effect wont pass our health bar limit.
                        self.hitPoints = self.hitPointsMax
                        self.node.hurt = 0.0
                        
                    if not self.hitPoints == self.hitPointsMax and not self._dead: #We only show the message if the player's health is not full and is alive.
                        bsUtils.PopupText('+' + str(self.healStacks),
                                            color=(0,1.15,0),
                                            scale=0.9,
                                            position=self.node.position).autoRetain()
                self.healStacks = 55 - (13 if self.alreadyHealed else 0) + self.healStacks #Increases stack each time the player pick this powerup.
                if not self.alreadyHealed: #Lets keep a track on the player if it has the effect, to avoid timer stacking.
                    self.regenTimer = bs.Timer(250,bs.Call(_regenHP),repeat=True)
                    self.endRegenTimer = bs.Timer(20000,bs.Call(_endRegen))
                    self.alreadyHealed = True
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText('Pills',
                                            color=(1,1.2,0.25),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif (m.powerupType == 'palette'):
                self.bombType = 'palette'
                tex = bs.getTexture("logo")
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText('Palette Bomb',
                                            color=(1.0,0.5,0.5),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif (m.powerupType == 'snowball'):
                self.bombType = 'snowball'
                tex = bs.getTexture("shrapnelSnow")
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText(
                                           'Snowballs',
                                            color=(0.95,1,1),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif (m.powerupType == 'radiusBombs'):
                self.bombType = 'radius'
                tex = bs.getTexture("gameCenterIcon")
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText(
                                           'Radius Bombs',
                                            color=(1.4,1.4,1.4),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif (m.powerupType == 'fireworkBombs'):
                self.setStockBombs('firework')
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText(
                                           'Firework Cracker',
                                            color=(1.2,0.88,0.55),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif (m.powerupType == 'bloomingBombs'):
                self.bombType = 'splash'
                tex = bs.getTexture("spaceBGColor")
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText(
                                           'Splash Bombs',
                                            color=(0.85,0.8,1.3),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif (m.powerupType == 'magnet'):
                self.bombType = 'magnet'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='magnet')),
                                            color=(0,0.5,1),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif (m.powerupType == 'health'):
                if self.overcharged == True: self.overchargedLight.delete() # Stop the overcharged light
                if self._cursed:
                    self.overcharged = False
                    self._cursed = False
                    self.sound.delete() # Stop the curse sound
                    # remove cursed material
                    factory = self.getFactory()
                    for attr in ['materials','rollerMaterials']:
                        materials = getattr(self.node,attr)
                        if factory.curseMaterial in materials:
                            setattr(self.node,attr,tuple(m for m in materials if m != factory.curseMaterial))
                    self.node.curseDeathTime = 0
                if (self.hitPoints > self.hitPointsOverdriveTooMuch):
                    self.hitPoints = self.hitPointsOverdriveTooMuch
                elif (self.hitPoints < self.hitPointsMax):
                    self.hitPoints = self.hitPointsMax
                else:
                    self.hitPoints = self.hitPoints
                self._flashBillboard(bs.Powerup.getFactory().texHealth)
                self.node.hurt = 0
                self._lastHitTime = None
                self._numTimesHit = 0
                if self.onFire: self.killFire()
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='health')),
                                            color=(1,0.9,0.9),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
            elif (m.powerupType == 'overdrive'):
                def _safeSetAttr(node,attr,val):
                    if node.exists(): setattr(node,attr,val)
                bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'invincible',True))
                self.node.handleMessage('celebrateR',400)
                self.invincibilityTimer = bs.Timer(3000,bs.Call(_safeSetAttr,self.node,'invincible',False))
                if self._cursed:
                    self.lightningPower()
                    self.overcharged = True
                    self.curseExplode()
                if (self.hitPoints >= self.hitPointsOverdriveTooMuch):
                    self.overcharged = True
                    self.curse()
                self.hitPoints = self.hitPoints + self.hitPointsOverdrive
                self._flashBillboard(bs.Powerup.getFactory().texOverdrive)
                self.lightningPower()
                self.node.hurt = 0
                self._lastHitTime = None
                self._numTimesHit = 0
                if bs.getConfig()['Powerup Popups'] == True:
                    bsUtils.PopupText((bs.Lstr(resource='overdrive')),
                                            color=(0.5,0,1),
                                            scale=self.scale,
                                            position=self.node.position).autoRetain()
                
            self.node.handleMessage("flash")
            if m.sourceNode.exists():
                m.sourceNode.handleMessage(bs.PowerupAcceptMessage())
            return True

        elif isinstance(m,bs.FreezeMessage):
            if self.freezeImmune: return
            if not self.node.exists(): return
            if self._duringDodge:
                if m.source != self.sourcePlayer: 
                    try: 
                        if self.sourcePlayer.getTeam() != m.source.getTeam(): self.style(self.sourcePlayer)
                    except StandardError: pass
                return
            if self.node.invincible == True:
                bs.playSound(self.getFactory().blockSound,1.0,position=self.node.position)
                return
            if self.shield is not None: return
            if self.onFire:
                self.killFire()
                return
            if not self.frozen:
                if self.stockBombType == 'healBomb' and self.stockBombCount > 0: # Don't freeze the players that have Healing Bombs in their inventory. Instead of freezing, remove one from the stock.
                    self.setStockBombs('removeOne')
                    self.node.handleMessage(bs.HealMessage(self.sourcePlayer))
                else:
                    self.frozen = True
                    self.node.frozen = 1
                    bs.gameTimer(5000,bs.WeakCall(self.handleMessage,bs.ThawMessage()))
                    # instantly shatter if we're already dead (otherwise its hard to tell we're dead)
                    if self.hitPoints <= 0:
                        self.shatter()

        elif isinstance(m,bs.ThawMessage):
            if self.frozen and not self.shattered and self.node.exists():
                self.frozen = False
                self.node.frozen = 0
                # If ice is thawed, add to the stats
                bs.statAdd('Ice Thawed')
                
        elif isinstance(m,bs.DiceMessage):
            if not self.node.exists(): return
            self.diceEffect(m.type,m.special)
           
        elif isinstance(m,bs.FireMessage):
            if self.fireImmune: return
            if not self.node.exists(): return
            if self._duringDodge: 
                try: 
                    if self.sourcePlayer.getTeam() != m.source.getTeam(): self.style(self.sourcePlayer)
                except StandardError: pass
                return
            if self.node.invincible == True:
                bs.playSound(self.getFactory().blockSound,1.0,position=self.node.position)
                return
            if self.stockBombType == 'healBomb' and self.stockBombCount > 0:
                self.setStockBombs('removeOne')
                self.node.handleMessage(bs.HealMessage(self.sourcePlayer))
                return
            if self.frozen:
                self.node.handleMessage(bs.ThawMessage())
                return
            self.fire(m.source,m.time)
            # If ice is thawed, add to the stats
            bs.statAdd('Spazes Lit on Fire')
                
        elif isinstance(m,bs.HealMessage):
            if not self.node.exists(): return
            # only heal yourself and members of your team
            try:
                if m.source.getTeam() != self.sourcePlayer.getTeam():
                    # and deal damage to enemies
                    self.node.handleMessage("hurtSound")
                    self.node.handleMessage(bs.HitMessage(flatDamage=250,
                                             hitType='heal',
                                             sourcePlayer=m.source))
                    return
            except StandardError:
                # damage bots aswell
                self.node.handleMessage("hurtSound")
                self.node.handleMessage(bs.HitMessage(flatDamage=250,
                                         hitType='heal',
                                         sourcePlayer=m.source))
                return
            
            factory = self.getFactory()
            def _safeSetAttr(node,attr,val):
                if node.exists(): setattr(node,attr,val)
            bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'invincible',True))
            self.invincibilityTimer = bs.Timer(350,bs.Call(_safeSetAttr,self.node,'invincible',False))
            if self.overcharged: self.overchargedLight.delete()
            if self._cursed:
                self._cursed = False
                self.sound.delete() # Stop the curse sound
                # remove cursed material
                for attr in ['materials','rollerMaterials']:
                    materials = getattr(self.node,attr)
                    if factory.curseMaterial in materials:
                        setattr(self.node,attr,tuple(m for m in materials if m != factory.curseMaterial))
                self.node.curseDeathTime = 0
                bs.statAdd('Curse Cures') # If curse is cured, add to the stats
            if (self.hitPoints <= self.hitPointsMax):
                self.hitPoints = self.hitPointsMax
                bs.playSound(factory.healthPowerupSound,3,position=self.node.position)
            if (self.hitPoints >= self.hitPointsOverdriveTooMuch):
                self.hitPoints = self.hitPointsOverdriveTooMuch
                bs.playSound(factory.healthPowerupSound,3,position=self.node.position)
            if (self.shield is not None): 
                if self.shieldDecayed: 
                    self.shieldSound = bs.newNode('sound',owner=self.node,attrs={'sound':factory.shieldIdleSound,'volume':0.55})
                    self.node.connectAttr('position',self.shieldSound,'position')
                    self.catchphrase()
                    self.style(m.source)
                self.equipShields()
                bs.statAdd('Shield Repairs') # If shield is repared, add to the stats
            if self.dizzy:
                self.dizzy  = False
            if self.onFire: 
                self.killFire()
                bs.statAdd('Fire Extinguishes') # If fire is extinguished, add to the stats
            bs.gameTimer(1,bs.WeakCall(self.handleMessage,bs.ThawMessage()))
            self.node.hurt = 0
            self._lastHitTime = None
            self._numTimesHit = 0
                
        elif isinstance(m,bs.DizzyMessage):
            if not self.node.exists(): return
            if self._dead: return
            if self.shield is not None: return
            if self._duringDodge:
                if m.source != self.sourcePlayer: 
                    try: 
                        if self.sourcePlayer.getTeam() != m.source.getTeam(): self.style(self.sourcePlayer)
                    except StandardError: pass
                return
            if self.node.invincible == True:
                bs.playSound(self.getFactory().blockSound,1.0,position=self.node.position)
                return
            self.dizzy = True
            self.node.handleMessage('celebrate',5000)
            bs.statAdd('Dizzy Characters')
            def dizzyIndicator():
                try:
                    if self._dead: return
                    self.node.handleMessage("flash")
                    bs.emitBGDynamics(position=(self.node.position[0],self.node.position[1],self.node.position[2]),velocity=self.node.velocity,count=random.randrange(6,20),scale=0.7,spread=0.2,chunkType='spark')
                    bs.emitBGDynamics(position=(self.node.position[0],self.node.position[1],self.node.position[2]),velocity=self.node.velocity,count=random.randrange(10,26),scale=2.0,spread=0.4,chunkType='sweat')
                except AttributeError: 
                    pass
            def unDizzy():
                if self._dead: return
                self.dizzy = False
                try:
                    self.onMoveUpDown(-self.node.moveUpDown)
                    self.onMoveLeftRight(-self.node.moveLeftRight)
                    bs.playSound(self.getFactory().dizzyEndSound,1.0,position=self.node.position)
                except AttributeError: pass
            def move(node,x,y):
                if self._dead: return
                self.node.moveLeftRight = x
                self.node.moveUpDown = y
                self.node.punchPressed = True
                self.node.punchPressed = False
            def sound():
                if self._dead: return
                bs.playSound(self.getFactory().dizzySound,2.0,position=self.node.position)
                self.node.jumpPressed = True
                self.node.jumpPressed = False
            space = 30
            bs.gameTimer(1+space*1,bs.Call(sound))
            bs.gameTimer(1+space*1,bs.Call(move,self.node,1,0))
            bs.gameTimer(1+space*2,bs.Call(move,self.node,1,1))
            bs.gameTimer(1+space*3,bs.Call(move,self.node,0,1))
            bs.gameTimer(1+space*4,bs.Call(move,self.node,-1,1))
            bs.gameTimer(1+space*5,bs.Call(move,self.node,-1,0))
            bs.gameTimer(1+space*6,bs.Call(move,self.node,-1,-1))
            bs.gameTimer(1+space*7,bs.Call(move,self.node,0,-1))
            bs.gameTimer(1+space*8,bs.Call(move,self.node,1,-1))
            
            bs.gameTimer(1+space*9,bs.Call(move,self.node,1,0))
            bs.gameTimer(1+space*10,bs.Call(move,self.node,1,1))
            bs.gameTimer(1+space*11,bs.Call(move,self.node,0,1))
            bs.gameTimer(1+space*12,bs.Call(move,self.node,-1,1))
            bs.gameTimer(1+space*13,bs.Call(move,self.node,-1,0))
            bs.gameTimer(1+space*14,bs.Call(move,self.node,-1,-1))
            bs.gameTimer(1+space*15,bs.Call(move,self.node,0,-1))
            bs.gameTimer(1+space*16,bs.Call(move,self.node,1,-1))
            
            bs.gameTimer(1+space*17,bs.Call(sound))
            bs.gameTimer(1+space*17,bs.Call(move,self.node,1,0))
            bs.gameTimer(1+space*18,bs.Call(move,self.node,1,1))
            bs.gameTimer(1+space*19,bs.Call(move,self.node,0,1))
            bs.gameTimer(1+space*20,bs.Call(move,self.node,-1,1))
            bs.gameTimer(1+space*21,bs.Call(move,self.node,-1,0))
            bs.gameTimer(1+space*22,bs.Call(move,self.node,-1,-1))
            bs.gameTimer(1+space*23,bs.Call(move,self.node,0,-1))
            bs.gameTimer(1+space*24,bs.Call(move,self.node,1,-1))
            
            bs.gameTimer(1+space*25,bs.Call(move,self.node,1,0))
            bs.gameTimer(1+space*26,bs.Call(move,self.node,1,1))
            bs.gameTimer(1+space*27,bs.Call(move,self.node,0,1))
            bs.gameTimer(1+space*28,bs.Call(move,self.node,-1,1))
            bs.gameTimer(1+space*29,bs.Call(move,self.node,-1,0))
            bs.gameTimer(1+space*30,bs.Call(move,self.node,-1,-1))
            bs.gameTimer(1+space*31,bs.Call(move,self.node,0,-1))
            bs.gameTimer(1+space*32,bs.Call(move,self.node,1,-1))
            
            bs.gameTimer(1+space*33,bs.Call(sound))
            bs.gameTimer(1+space*33,bs.Call(move,self.node,1,0))
            bs.gameTimer(1+space*34,bs.Call(move,self.node,1,1))
            bs.gameTimer(1+space*35,bs.Call(move,self.node,0,1))
            bs.gameTimer(1+space*36,bs.Call(move,self.node,-1,1))
            bs.gameTimer(1+space*37,bs.Call(move,self.node,-1,0))
            bs.gameTimer(1+space*38,bs.Call(move,self.node,-1,-1))
            bs.gameTimer(1+space*39,bs.Call(move,self.node,0,-1))
            bs.gameTimer(1+space*40,bs.Call(move,self.node,1,-1))
            
            bs.gameTimer(1+space*41,bs.Call(move,self.node,1,0))
            bs.gameTimer(1+space*42,bs.Call(move,self.node,1,1))
            bs.gameTimer(1+space*43,bs.Call(move,self.node,0,1))
            bs.gameTimer(1+space*44,bs.Call(move,self.node,-1,1))
            bs.gameTimer(1+space*45,bs.Call(move,self.node,-1,0))
            bs.gameTimer(1+space*46,bs.Call(move,self.node,-1,-1))
            bs.gameTimer(1+space*47,bs.Call(move,self.node,0,-1))
            bs.gameTimer(1+space*48,bs.Call(move,self.node,1,-1))
            
            bs.gameTimer(1+space*49,bs.Call(move,self.node,0,0))
            bs.gameTimer(1+space*50,bs.Call(move,self.node,1,0))
            bs.gameTimer(1+space*51,bs.Call(move,self.node,0,-1))
            bs.gameTimer(1+space*52,bs.Call(move,self.node,1,1))
            bs.gameTimer(1+space*53,bs.Call(move,self.node,0,-1))
            bs.gameTimer(1+space*54,bs.Call(move,self.node,-1,1))
            bs.gameTimer(1+space*55,bs.Call(move,self.node,1,0))
            bs.gameTimer(1+space*56,bs.Call(move,self.node,1,-1))
            bs.gameTimer(5000,bs.Call(unDizzy))
            
            bs.gameTimer(1,bs.Call(dizzyIndicator))
            bs.gameTimer(500,bs.Call(dizzyIndicator))
            bs.gameTimer(1000,bs.Call(dizzyIndicator))
            bs.gameTimer(1500,bs.Call(dizzyIndicator))
            bs.gameTimer(2000,bs.Call(dizzyIndicator))
            bs.gameTimer(2500,bs.Call(dizzyIndicator))
            bs.gameTimer(3000,bs.Call(dizzyIndicator))
            bs.gameTimer(3500,bs.Call(dizzyIndicator))
            bs.gameTimer(4000,bs.Call(dizzyIndicator))
            bs.gameTimer(4500,bs.Call(dizzyIndicator))
            bs.gameTimer(5000,bs.Call(dizzyIndicator))

        elif isinstance(m,bs.HitMessage):
            if not self.node.exists(): return
            if self.node.invincible == True:
                bs.playSound(self.getFactory().blockSound,1.0,position=self.node.position)
                return True
                
            # if we were recently hit, don't count this as another
            # (so punch flurries and bomb pileups essentially count as 1 hit)
            gameTime = bs.getGameTime()
            if self.hitPoints <= 0:
               self.random = random.randint(1,50)
               if self.random == 12:
                  self.shatter(extreme=random.choice([False,True,False,True,False,False]))
            if self._lastHitTime is None or gameTime-self._lastHitTime > 1000:
                self._numTimesHit += 1
                self._lastHitTime = gameTime
           
            critPunched = False
            mag = m.magnitude * self._impactScale
            velocityMag = m.velocityMagnitude * self._impactScale
            if (m.hitSubType == 'fire' and self.frozen and m.hitSubTypeTrue) or (m.hitSubType == 'ice' and self.onFire and m.hitSubTypeTrue):
                mag = 0
                velocityMag = 0
            elif (m.hitSubType == 'fire' and self.onFire and m.hitSubTypeTrue): # Deal extra damage with Fire bombs if you're already lit
                mag *= 1.25
                velocityMag *= 1.25

            self.hiJumped = False
            if m.hitSubType == 'knocker' and m.hitSubTypeTrue: damageScale = 0.005
            elif m.hitSubType == 'tesla' and m.hitSubTypeTrue: damageScale = 0.1
            elif m.hitSubType == 'hijump' and m.hitSubTypeTrue:
                damageScale = 0.01
            elif m.hitSubType == 'cake' and m.hitSubTypeTrue:
                damageScale = 1.5 # Cake deals more damage without knocking back so much
            elif m.hitSubType == 'gloo' and m.hitSubTypeTrue:
                damageScale = 0.095
            elif m.hitSubType == 'splash':
                self.bloomDamageStacks += 0.46
                bsUtils.PopupText(str(self.bloomDamageStacks) + '+',
                                            color=(0.8,0.5,1.1),
                                            scale=1.0,
                                            position=self.node.position).autoRetain()
                damageScale = self.bloomDamageStacks
            elif m.hitSubType == 'hunter':
                self.hitPoints -= 450
                if self.hitPoints <= 1:
                    self.handleMessage(bs.DieMessage())
                #damageScale = self.hitPoints * (0.3/129)
            elif m.hitSubType == 'infatuate' and m.hitSubTypeTrue:
                damageScale = 0.001
                def idiotic_move():
                    self.loop += 1
                    if self.loop >= 20:
                        self.loop = 0
                        self.cc_timer = None
                    self.node.moveUpDown = random.choice([-1.0,1.0])
                    self.node.moveLeftRight = random.choice([-1.0,1.0])
                    if random.randint(1,6) == 1:
                        self.onJumpPress()
                        self.onJumpRelease()
                    if random.randint(1,6) == 1:
                        self.onPunchPress()
                        self.onPunchRelease()
                    if random.randint(1,6) == 1:
                        self.onPickUpPress()
                        self.onPickUpRelease()
                    if random.randint(1,6) == 1:
                        self.onBombPress()
                        self.onBombRelease()
                def do_infatuate():
                    bs.gameTimer(random.randrange(50,270),idiotic_move)
                self.cc_timer = bs.Timer(100,bs.WeakCall(do_infatuate),repeat=True)
            elif m.hitSubType == 'palette' and m.hitSubTypeTrue:
                if self._dead or self.shield is not None and self.shield.exists(): return
                damageScale = 0.15
                self._impactScale = self._impactScale + 0.17
                #TAGS
                self.colorTex = [
                'neoSpazColor',
                'kronkColor',
                'zoeColor',
                'jackColor',
                'melColor',
                'ninjaColor',
                'bonesColor',
                'bearColor',
                'agentColor',
                'frostyColor',
                'penguinColor',
                'pixieColor',
                'wizardColor',
                'bunnyColor',
                'santaColor',
                'cyborgColor',
                'aliColor',
                'looieColor',
                'spyColor',
                'cowColor',
                'lucyColor',
                'klaymanColor',
                'willyColor',
                'grambelColor',
                'ronnieColor',
                'mictlanColor',
                'zillColor',
                'knightColor',
                'avgnColor',
                'juiceBoyColor']
                # V COLORMASK V
                self.colorMaskTex = [
                'neoSpazColorMask',
                'kronkColorMask',
                'zoeColorMask',
                'jackColorMask',
                'melColorMask',
                'ninjaColorMask',
                'bonesColorMask',
                'bearColorMask',
                'agentColorMask',
                'frostyColorMask',
                'penguinColorMask',
                'pixieColorMask',
                'wizardColorMask',
                'bunnyColorMask',
                'santaColorMask',
                'cyborgColorMask',
                'aliColorMask',
                'looieColorMask',
                'spyColorMask',
                'cowColorMask',
                'grambelColorMask',
                'lucyColorMask',
                'klaymanColorMask',
                'willyColorMask',
                'ronnieColorMask',
                'mictlanColorMask',
                'zillColorMask',
                'avgnColorMask',
                'knightColorMask',
                'juiceBoyColorMask']
                #V   HEAD    V
                self.head = [
                'neoSpazHead',
                'kronkHead',
                'zoeHead',
                'jackHead',
                'melHead',
                'ninjaHead',
                'bonesHead',
                'bearHead',
                'agentHead',
                'frostyHead',
                'penguinHead',
                'pixieHead',
                'wizardHead',
                'bunnyHead',
                'santaHead',
                'cyborgHead',
                'aliHead',
                'looieHead',
                'spyHead',
                'cowHead',
                'lucyHead',
                'klaymanHead',
                'grambelHead',
                'willyHead',
                'ronnieHead',
                'mictlanHead',
                'zillHead',
                'knightHead',
                'avgnHead']
                #V TORSO V
                self.torso = [
                'neoSpazTorso',
                'kronkTorso',
                'zoeTorso',
                'jackTorso',
                'melTorso',
                'ninjaTorso',
                'bonesTorso',
                'bearTorso',
                'agentTorso',
                'frostyTorso',
                'penguinTorso',
                'pixieTorso',
                'wizardTorso',
                'bunnyTorso',
                'santaTorso',
                'cyborgTorso',
                'aliTorso',
                'looieTorso',
                'spyTorso',
                'cowTorso',
                'lucyTorso',
                'klaymanTorso',
                'grambelTorso',
                'willyTorso',
                'ronnieTorso',
                'mictlanTorso',
                'zillBody',
                'knightTorso']
                #V PELVIS V
                self.pelvis = [
                'neoSpazPelvis',
                'kronkPelvis',
                'zoePelvis',
                'ninjaPelvis',
                'bonesPelvis',
                'bearPelvis',
                'agentPelvis',
                'frostyPelvis',
                'penguinPelvis',
                'pixiePelvis',
                'wizardPelvis',
                'bunnyPelvis',
                'cyborgPelvis',
                'aliPelvis',
                'spyPelvis',
                'cowPelvis',
                'grambelPelvis',
                'lucyPelvis',
                'knightPelvis']
                #V UPPER ARM V
                self.upperArm = [
                'neoSpazUpperArm',
                'kronkUpperArm',
                'zoeUpperArm',
                'melUpperArm',
                'jackUpperArm',
                'ninjaUpperArm',
                'bonesUpperArm',
                'bearUpperArm',
                'agentUpperArm',
                'frostyUpperArm',
                'penguinUpperArm',
                'pixieUpperArm',
                'wizardUpperArm',
                'bunnyUpperArm',
                'cyborgUpperArm',
                'aliUpperArm',
                'willyUpperArm',
                'ronnieUpperArm',
                'spyUpperArm',
                'cowUpperArm',
                'grambelUpperArm',
                'lucyUpperArm',
                'klaymanUpperArm',
                'mictlanUpperArm',
                'juiceBoyUpperArm',
                'zillUpperArm', 
                'lucyUpperArm',
                'knightUpperArm']
                #V UPPER LEG V
                self.upperLeg = [
                'neoSpazUpperLeg',
                'kronkUpperLeg',
                'zoeUpperLeg',
                'melUpperLeg',
                'jackUpperLeg',
                'ninjaUpperLeg',
                'bonesUpperLeg',
                'bearUpperLeg',
                'agentUpperLeg',
                'frostyUpperLeg',
                'penguinUpperLeg',
                'pixieUpperLeg',
                'wizardUpperLeg',
                'bunnyUpperLeg',
                'cyborgUpperLeg',
                'aliUpperLeg',
                'willyUpperLeg',
                'ronnieUpperLeg',
                'spyUpperLeg',
                'cowUpperLeg',
                'grambelUpperLeg',
                'lucyUpperLeg',
                'klaymanUpperLeg',
                'mictlanUpperLeg',
                'juiceBoyUpperLeg',
                'zillUpperLeg', 
                'lucyUpperLeg',
                'knightUpperLeg']
                #V FORE ARM V
                self.foreArm = [
                'neoSpazForeArm',
                'kronkForeArm',
                'zoeForeArm',
                'melForeArm',
                'jackForeArm',
                'ninjaForeArm',
                'bonesForeArm',
                'bearForeArm',
                'agentForeArm',
                'frostyForeArm',
                'penguinForeArm',
                'pixieForeArm',
                'wizardForeArm',
                'bunnyForeArm',
                'cyborgForeArm',
                'aliForeArm',
                'willyForeArm',
                'ronnieForeArm',
                'spyForeArm',
                'cowForeArm',
                'grambelForeArm',
                'lucyForeArm',
                'klaymanForeArm',
                'mictlanForeArm',
                'juiceBoyForeArm',
                'zillForeArm', 
                'lucyForeArm',
                'knightForeArm']
                #V HAND V
                self.hand = [
                'neoSpazHand',
                'kronkHand',
                'zoeHand',
                'melHand',
                'jackHand',
                'ninjaHand',
                'bonesHand',
                'bearHand',
                'agentHand',
                'frostyHand',
                'penguinHand',
                'pixieHand',
                'wizardHand',
                'bunnyHand',
                'cyborgHand',
                'aliHand',
                'willyHand',
                'ronnieHand',
                'spyHand',
                'cowHand',
                'grambelHand',
                'lucyHand',
                'klaymanHand',
                'mictlanHand',
                'juiceBoyHand',
                'zillHand', 
                'lucyHand',
                'looieHand',
                'knightHand']
                #V TOES V
                self.toes = [
                'neoSpazToes',
                'kronkToes',
                'zoeToes',
                'melToes',
                'jackToes',
                'ninjaToes',
                'bonesToes',
                'bearToes',
                'agentToes',
                'frostyToes',
                'penguinToes',
                'pixieToes',
                'wizardToes',
                'bunnyToes',
                'cyborgToes',
                'aliToes',
                'willyToes',
                'ronnieToes',
                'spyToes',
                'cowToes',
                'grambelToes',
                'lucyToes',
                'klaymanToes',
                'mictlanToes',
                'juiceBoyToes',
                'zillToes', 
                'lucyToes',
                'knightToes']
                #V LOWER LEG V
                self.lowerLeg = [
                'neoSpazLowerLeg',
                'kronkLowerLeg',
                'zoeLowerLeg',
                'melLowerLeg',
                'jackLowerLeg',
                'ninjaLowerLeg',
                'bonesLowerLeg',
                'bearLowerLeg',
                'agentLowerLeg',
                'frostyLowerLeg',
                'penguinLowerLeg',
                'pixieLowerLeg',
                'wizardLowerLeg',
                'bunnyLowerLeg',
                'cyborgLowerLeg',
                'aliLowerLeg',
                'willyLowerLeg',
                'ronnieLowerLeg',
                'spyLowerLeg',
                'cowLowerLeg',
                'grambelLowerLeg',
                'lucyLowerLeg',
                'klaymanLowerLeg',
                'mictlanLowerLeg',
                'juiceBoyLowerLeg',
                'zillLowerLeg', 
                'lucyLowerLeg',
                'looieLowerLeg',
                'knightLowerLeg']
                self.node.colorTexture = bs.getTexture(random.choice(self.colorTex))
                self.node.colorMaskTexture = bs.getTexture(random.choice(self.colorMaskTex))
                self.node.headModel = bs.getModel(random.choice(self.head))
                self.node.torsoModel = bs.getModel(random.choice(self.torso))
                self.node.pelvisModel = bs.getModel(random.choice(self.pelvis))
                self.node.upperArmModel = bs.getModel(random.choice(self.upperArm))
                self.node.upperLegModel = bs.getModel(random.choice(self.upperLeg))
                self.node.foreArmModel = bs.getModel(random.choice(self.foreArm))
                self.node.handModel = bs.getModel(random.choice(self.hand))
                self.node.toesModel = bs.getModel(random.choice(self.toes))
                self.node.lowerLegModel = bs.getModel(random.choice(self.lowerLeg))
                self.node.style = random.choice(['spaz','kronk','female','pixie','agent','cyborg','bunny','ali','penguin','mel','frosty','bear'])
            else:
                damageScale = 0.22

            # if they've got a shield, deliver it to that instead..
            if self.shield is not None:

                if m.flatDamage: 
                    damage = m.flatDamage * self._impactScale
                    # Fire deals extra damage to shields, completely melting it
                    if self.onFire:
                        damage *= 12
                        bs.playSound(self.getFactory().shieldDownSound,0.5,position=self.node.position)
                else:
                    # hit our spaz with an impulse but tell it to only return theoretical damage; not apply the impulse..
                    self.node.handleMessage("impulse",m.pos[0],m.pos[1],m.pos[2],
                                            m.velocity[0],m.velocity[1],m.velocity[2],
                                            mag,velocityMag,m.radius,1,m.forceDirection[0],m.forceDirection[1],m.forceDirection[2])
                                            
                                            
                    damage = damageScale * self.node.damage

                # Deal no damage to self
                if m.hitSubType == 'hijump' and m.sourcePlayer == self.node.sourcePlayer: pass
                else: self.shieldHitPoints -= damage

                self.shield.hurt = 1.0 - self.shieldHitPoints/self.shieldHitPointsMax
                # its a cleaner event if a hit just kills the shield without damaging the player..
                # however, massive damage events should still be able to damage the player..
                # this hopefully gives us a happy medium.
                maxSpillover = 450
                if self.shieldHitPoints <= 0:
                    # fixme - transition out perhaps?..
                    self.shield.delete()
                    self.shield = None
                    self.shieldDecayed = False
                    bs.playSound(self.getFactory().shieldDownSound,1.0,position=self.node.position)
                    self.shieldSound.delete()
                    # emit some cool lookin sparks when the shield dies
                    t = self.node.position
                    bs.emitBGDynamics(position=(t[0],t[1]+0.9,t[2]),
                                      velocity=self.node.velocity,
                                      count=random.randrange(20,30),scale=0.6,spread=0.6,chunkType='spark')

                else:
                    bs.playSound(self.getFactory().shieldHitSound,0.5,position=self.node.position)

                # emit some cool lookin sparks on shield hit
                bs.emitBGDynamics(position=m.pos,
                                  velocity=(m.forceDirection[0]*1.0,
                                            m.forceDirection[1]*1.0,
                                            m.forceDirection[2]*1.0),
                                  count=min(30,5+int(damage*0.005)),scale=0.3,spread=0.3,chunkType='spark')


                # if they passed our spillover threshold, pass damage along to spaz
                if self.shieldHitPoints <= -maxSpillover:
                    leftoverDamage = -maxSpillover-self.shieldHitPoints
                    shieldLeftoverRatio = leftoverDamage/damage

                    # scale down the magnitudes applied to spaz accordingly..
                    mag *= shieldLeftoverRatio
                    velocityMag *= shieldLeftoverRatio
                else:
                    return True # good job shield!
            else: shieldLeftoverRatio = 1.0

            if m.flatDamage:
                damage = m.flatDamage * self._impactScale * shieldLeftoverRatio
            else:
                # Make Hijump explosions extra powerful (but only for the enemies!)
                if m.hitSubType == 'hijump' and m.sourcePlayer != self.node.sourcePlayer:
                    self.hiJumped = True
                    mag *= 4
                    velocityMag *= 4
                    
                # Decrease knockback during dodge
                if self._duringDodge:
                    bs.statAdd('Close-Call Dodges')
                    mag *= 0.1
                    velocityMag *= 0.1
            
                # hit it with an impulse and get the resulting damage
                self.node.handleMessage("impulse",m.pos[0],m.pos[1],m.pos[2],
                                        m.velocity[0],m.velocity[1],m.velocity[2],
                                        mag,velocityMag,m.radius,0,m.forceDirection[0],m.forceDirection[1],m.forceDirection[2])

                damage = damageScale * self.node.damage
                if self.hiJumped: damage *= 6 # Deal extra damage to enemies knocked in the air by Hijump
                
                # Receive less damage during a dodge
                if self._duringDodge: 
                    damage *= gDodgeDamageResistance
                else:
                    self.node.handleMessage("hurtSound")

            # play punch impact sound based on damage if it was a punch
            if m.hitType == 'kick':

                self.onKicked(damage)
                if damage > 1000:
                    bsUtils.PopupText("#Holy Shit!",color=(1,0.5,0),scale=1.4,position=self.node.position).autoRetain()
                    self.node.shattered = 2

                if damage > 800:
                    bsUtils.PopupText("Critical Hit!",color=(0.0,1.0,0.6),scale=1.4,position=self.node.position).autoRetain()
                    
                            # if damage was significant, lets show it
                if damage > 350:
                    bsUtils.showDamageCount('-' + str(int(damage/10)) + "%",
                                            m.pos, m.forceDirection)
                                               
                # lets always add in a super-punch sound with boxing
                # gloves just to differentiate them
                if damage > 355:
                    sounds = self.getFactory().punchSoundsStrong
                    sound = sounds[random.randrange(len(sounds))]
                else: sound = self.getFactory().punchSound
                bs.playSound(sound, 1.0, position=self.node.position)

                # throw up some chunks
                bs.emitBGDynamics(position=m.pos,
                                  velocity=(m.forceDirection[0]*0.5,
                                            m.forceDirection[1]*0.5,
                                            m.forceDirection[2]*0.5),
                                  count=min(10, 1+int(damage*0.0025)),
                                  scale=0.3, spread=0.03);

                bs.emitBGDynamics(position=m.pos,
                                  chunkType='sweat',
                                  velocity=(m.forceDirection[0]*1.3,
                                            m.forceDirection[1]*1.3+5.0,
                                            m.forceDirection[2]*1.3),
                                  count=min(30, 1+int(damage*0.04)),
                                  scale=0.6,
                                  spread=0.28);
                # momentary flash
                hurtiness = damage*1.2
                kickPos = (m.pos[0]+m.forceDirection[0]*0.02,
                            m.pos[1]+m.forceDirection[1]*0.02,
                            m.pos[2]+m.forceDirection[2]*0.02)
                
            if m.hitType == 'punch':

                self.onPunched(damage)

                # if damage was significant, lets show it
                if damage > 400: bsUtils.showDamageCount('-'+str(int(damage/10))+"%",m.pos,m.forceDirection)
                                               
                # lets always add in a super-punch sound with boxing gloves just to differentiate them
                if m.hitSubType == 'superPunch':
                    sounds = self.getFactory().punchSoundsStrong
                    sound = sounds[random.randrange(len(sounds))]
                    bs.playSound(sound,0.39,position=self.node.position)
                if damage > 1000 and m.hitSubType == 'superPunch' and m.sourcePlayer.exists(): 
                    critPunched = True
                    self.accolade('crit',m.sourcePlayer,self.sourcePlayer)
                    self.shatter(extreme=False)
                elif damage > 600:
                    sounds = self.getFactory().punchSoundsStrong
                    sound = sounds[random.randrange(len(sounds))]
                    bs.playSound(sound,1.0,position=self.node.position)
                elif damage > 450:
                    sound = self.getFactory().punchSound
                    bs.playSound(sound,2.0,position=self.node.position)
                else: 
                    sound = self.getFactory().punchWeakSound
                    bs.playSound(sound,2.0,position=self.node.position)
                    
                self.ninjaGrabbed = True
                def _ninjaOff(): self.ninjaGrabbed = False
                bs.gameTimer(200, _ninjaOff)

                # throw up some chunks
                bs.emitBGDynamics(position=m.pos,
                                  velocity=(m.forceDirection[0]*0.5,
                                            m.forceDirection[1]*0.5,
                                            m.forceDirection[2]*0.5),
                                  count=min(10,1+int(damage*0.0025)),scale=0.3,spread=0.03);

                bs.emitBGDynamics(position=m.pos,
                                  chunkType='sweat',
                                  velocity=(m.forceDirection[0]*1.3,
                                            m.forceDirection[1]*1.3+5.0,
                                            m.forceDirection[2]*1.3),
                                  count=min(30,1+int(damage*0.04)),
                                  scale=1.0,
                                  spread=0.28);
                # momentary flash
                hurtiness = damage*0.003
                punchPos = (m.pos[0]+m.forceDirection[0]*0.02,
                            m.pos[1]+m.forceDirection[1]*0.02,
                            m.pos[2]+m.forceDirection[2]*0.02)
                if bs.getConfig().get('Cheat KAB',True):
                    bs.Blast(position=punchPos,
                             blastType='fake',
                             sourcePlayer=self.sourcePlayer).autoRetain()
                            
                flashColor = (1.0,0.8,0.4)
                light = bs.newNode("light",
                                   attrs={'position':punchPos,
                                          'radius':0.12+hurtiness*0.12,
                                          'intensity':0.3*(1.0+1.0*hurtiness),
                                          'heightAttenuated':False,
                                          'color':flashColor})
                bs.gameTimer(60,light.delete)


                flash = bs.newNode("flash",
                                   attrs={'position':punchPos,
                                          'size':0.17+0.17*hurtiness,
                                          'color':flashColor})
                bs.gameTimer(60,flash.delete)

            if m.hitType == 'impact':
                bs.emitBGDynamics(position=m.pos,
                                  velocity=(m.forceDirection[0]*2.0,
                                            m.forceDirection[1]*2.0,
                                            m.forceDirection[2]*2.0),
                                  count=min(10, 1+int(damage*0.01)),
                                  scale=0.4, spread=0.1);
            if self.hitPoints > 0:

                # its kinda crappy to die from impacts, so lets reduce impact damage
                # by a reasonable amount if it'll keep us alive
                if m.hitType == 'impact' and damage > self.hitPoints:
                    # drop damage to whatever puts us at 10 hit points, or 200 less than it used to be
                    # whichever is greater (so it *can* still kill us if its high enough)
                    # hijumping players get a bit of a leeway, so it's harder to die from falling during these jumps
                    if self.hijumpSound: newDamage = damage*0.5
                    else: newDamage = max(damage-200,self.hitPoints-10)
                    damage = newDamage
                    chances = random.randint(1,20)
                    if chances == 1:
                        self.shatter(extreme=random.choice([True,False,False,False,True,False]))

                self.node.handleMessage("flash")
                # if we're holding something, drop it
                if damage > 0.0 and self.node.holdNode.exists() and not m.hitSubType in ['fire','tesla_zap']:
                    self.node.holdNode = bs.Node(None)
                # Deal no damage to self when hijumping
                if m.hitSubType == 'hijump' and m.sourcePlayer == self.node.sourcePlayer: pass
                else:
                    self.hitPoints -= damage
                    self.node.hurt = 1.0 - self.hitPoints/self.hitPointsMax
                # if we're cursed, *any* damage blows us up
                if self._cursed and damage > 0:
                    # don't blow yourself up when hijumping
                    if m.hitSubType == 'hijump' and m.sourcePlayer == self.node.sourcePlayer: pass
                    else: bs.gameTimer(50,bs.WeakCall(self.curseExplode,m.sourcePlayer))
                # if we're frozen, shatter.. otherwise die if we hit zero
                if self.frozen and (damage > 200 or self.hitPoints <= 0):
                    self.shatter()
                elif self.hitPoints <= 0:
                    if m.hitSubType == 'ranger' and m.hitSubTypeTrue: 
                        self.node.style = 'ali'
                        self.node.colorTexture = bs.getTexture('white')
                        self.node.colorMaskTexture = bs.getTexture('black')
                        self.shatter(False,'ranger')
                        t = self.node.position
                        self.style(m.sourcePlayer,1) # add style points for FFA/Team games
                        bs.emitBGDynamics(position=(t[0],t[1]+0.9,t[2]),
                                      velocity=self.node.velocity,
                                      count=random.randrange(60,80),scale=1,spread=1,chunkType='spark')
                    elif m.hitSubType == 'fire' and m.hitSubTypeTrue: self.shatter(False,'fire')
                    elif m.hitSubType == 'tnt' and m.sourcePlayer.exists():
                        try: 
                            if self.sourcePlayer.getTeam() != m.sourcePlayer.getTeam(): self.style(m.sourcePlayer,1)
                        except StandardError: pass
                    elif m.hitType == 'dash' and m.sourcePlayer.exists():
                        # give a style point if the target got finished off with a tackle
                        # bonus points if executed after doing three consecutive hits beforehand
                        if m.sourcePlayer.actor.punchCombo > 2: 
                            try: 
                                if self.sourcePlayer.getTeam() != m.sourcePlayer.getTeam(): self.style(m.sourcePlayer,3)
                            except StandardError: pass
                        else:
                            self.style(m.sourcePlayer,1)
                    self.node.handleMessage(bs.DieMessage(how='impact'))

            # if we're dead, take a look at the smoothed damage val
            # (which gives us a smoothed average of recent damage) and shatter
            # us if its grown high enough
            if self.hitPoints <= 0:
                damageAvg = self.node.damageSmoothed * damageScale
                    
                if m.hitSubType == 'hijump' and damageAvg > 100 and m.sourcePlayer.exists():
                    self.shatter()
                    self.accolade('hijumpKill',m.sourcePlayer,self.sourcePlayer)
                    return
                    
                if m.hitType == 'punch' and m.hitSubType == 'landMine' and m.sourcePlayer != self.sourcePlayer and m.sourcePlayer.exists():
                    self.accolade('mineKill',m.sourcePlayer,self.sourcePlayer)
                    self.shatter()
                    return
                  
                if damageAvg > 950:
                    # If you get gibbed by a Combat Bomb and it isn't your bomb, you get an accolade
                    if m.hitSubType == 'combat' and m.sourcePlayer != self.sourcePlayer and m.sourcePlayer.exists() and m.hitSubTypeTrue:
                        self.random = random.randint(1,2)
                        if self.random == 1 and self.hitPoints <= 0:
                            self.shatter()
                        if m.srcNode.getDelegate().blastRadiusBuffed: self.style(m.sourcePlayer,1,sound=False)
                        else: self.style(m.sourcePlayer,2,sound=False)
                        self.accolade('gibKill',m.sourcePlayer,self.sourcePlayer)
                elif damageAvg > 2000: self.shatter(extreme=True)
                
                    

        elif isinstance(m,_BombDiedMessage):
            self.bombCount += 1
        
        elif isinstance(m,bs.DieMessage):
            wasDead = self._dead
            self._dead = True
            self.updateCallback = None
            self.hitPoints = 0
            self.random = random.randint(1,37)
            if self.random == 1:
               self.shatter(extreme=random.choice([True,False,False,False,False,False,False,False,False,False]))
            if m.immediate: self.node.delete()
            elif self.node.exists():
                factory = self.getFactory() 
                def _dummy(): pass
                self.collapseRestoreSoundTimer = bs.Timer(1,_dummy)
                self.collapseRestoreTimer = bs.Timer(1,_dummy)
                self.node.hurt = 1.0
                if self.playBigDeathSound and not wasDead:
                    bs.playSound(factory.singlePlayerDeathSound)
                self.node.dead = True
                bs.gameTimer(2000,self.node.delete) #2000
                if m.how=='fall' and bs.getActivity()._map.getName() == 'Bacon Greece': # If you die by falling OOB and it's Bacon Greece map, make a splash sound effect shortly after
                    def splash(): bs.playSound(factory.splashSound,volume=1.0,position=self.node.position)
                    bs.gameTimer(600,splash)

        elif isinstance(m,bs.OutOfBoundsMessage):
            if self._cursed: self.sound.delete() # Stop the curse sound
            if self.overcharged: self.overchargedLight.delete() # Stop the overcharged light
            self.handleMessage(bs.DieMessage(how='fall'))

        elif isinstance(m,bs.StandMessage):
            self._lastStandPos = (m.position[0],m.position[1],m.position[2])
            self.node.handleMessage("stand",m.position[0],m.position[1],m.position[2],m.angle)
            
        elif isinstance(m,_FootConnectMessage): 
            if self.hijumpSound:
                bs.playSound(self.getFactory().hijumpLandSound,1.0,position=self.node.position)
                self.hijumpSound.delete()
                self.hijumpSound = None
            self.midairCannonball = False
            self.midairDamaged = False
            self.footing = True
                
        elif isinstance(m,_FootDisconnectMessage): 
            self.midairCannonball = False
            self.midairDamaged = False
            def _ableToDamage(): self.midairCannonball = True
            self.timeToMidairCannonball = bs.gameTimer(200,_ableToDamage)
            self.footing = False

        elif isinstance(m,_CurseExplodeMessage):
            self.curseExplode()

        elif isinstance(m,_KickHitMessage):
            node = bs.getCollisionInfo("opposingNode")

            # only allow one hit per node per punch
            if (node is not None and node.exists()
                and not node in self._kickedNodes
                and self.onJumpPress and self.onPunchPress):
            
                
                kickMomentumAngular = ((self.node.punchMomentumAngular or self.node.run) * 0.25)
                kickPower = (self.node.punchPower or self.node.run) * 0.25

                # ok here's the deal:  we pass along our base velocity for use
                # in the impulse damage calculations since that is a more
                # predictable value than our fist velocity, which is rather
                # erratic. ...however we want to actually apply force in the
                # direction our fist is moving so it looks better.. so we still
                # pass that along as a direction ..perhaps a time-averaged
                # fist-velocity would work too?.. should try that.
                
                # if its something besides another spaz, just do a muffled punch
                # sound
                if node.getNodeType() == 'spaz':
                    node.handleMessage("knockout",random.randint(90.0,200.0))
                

                t = (self.node.position[0],self.node.position[1],self.node.position[2])
                kickDir = (self.node.velocity[0]+0.7,self.node.velocity[1]+1.7,self.node.velocity[2]+0.7)
                v = self.node.velocity

                node.handleMessage(
                    bs.HitMessage(
                        pos=t,
                        velocity=v,
                        magnitude=kickPower*kickMomentumAngular*110.0,
                        velocityMagnitude=kickPower*45,
                        radius=-1000,
                        srcNode=self.node,
                        sourcePlayer=self.sourcePlayer,
                        forceDirection = kickDir,
                        hitType='punch'))

        elif isinstance(m,_PunchHitMessage):
        
            node,body = bs.getCollisionInfo('opposingNode','opposingBody')

            # only allow one hit per node per punch
            if node is not None and node.exists() and not node in self._punchedNodes:
                # if punching someone's hand and they're punching, don't deal damage and get knocked away
                if node.getNodeType() == 'spaz' and body == 2:
                    if self.currentlyPunching and node.getDelegate().currentlyPunching:
                        # compare punch cooldowns, the guy who punched later gets punished
                        if self.lastPunchTime >= node.getDelegate().lastPunchTime:
                            directionX = -(node.position[0] - self.node.position[0])
                            directionY = -(node.position[1] - self.node.position[1])+0.5
                            directionZ = -(node.position[2] - self.node.position[2])
                            print node.getDelegate().sourcePlayer
                            
                            bs.playSound(self.getFactory().punchParrySound,3.0,position=node.position)
                            bs.newNode("explosion",
                                    attrs={'position':self.node.punchPosition,
                                            'velocity':(node.punchVelocity[0],node.punchVelocity[1],node.punchVelocity[2]),
                                            'color':node.highlight,
                                            'radius':0.7,
                                            'big':False})
                            bs.emitBGDynamics(position=self.node.punchPosition,
                                  velocity=node.punchVelocity,
                                  count=15,scale=0.4,spread=0.6,chunkType='spark')
                            bs.emitBGDynamics(position=self.node.punchPosition,emitType='distortion',spread=0.7)
                            self.node.handleMessage("impulse",node.position[0],node.position[1]+0.2,node.position[2],
                                                    0,0,0,
                                                    250,250,0,0,directionX,directionY,directionZ)
                            self.node.handleMessage("knockout", 500.0)
                            
                            node.getDelegate().counterText.text = "Parry!"
                            bs.animate(node.getDelegate().counterText,'opacity',{0:0.5,
                                                                                 400:1.0,
                                                                                 1250:0.0},loop=False)
                                                   
                        return
                
                punchMomentumAngular = self.node.punchMomentumAngular * self._punchPowerScale * 0.9
                punchPower = self.node.punchPower * self._punchPowerScale
                if self.onFire: punchPower *= 1.25

                # ok here's the deal:  we pass along our base velocity for use in the
                # impulse damage calculations since that is a more predictable value
                # than our fist velocity, which is rather erratic.
                # ...however we want to actually apply force in the direction our fist
                # is moving so it looks better.. so we still pass that along as a direction
                # ..perhaps a time-averased fist-velocity would work too?.. should try that.
                
                # if its something besides another spaz, just do a muffled punch sound
                if node.getNodeType() != 'spaz':
                    if self._character in ['Juice-Boy','Frosty','Exploder','Lucy Chance']:
                        sounds = self.getFactory().impactCardboardSoundsMedium
                    elif self.node.style == 'cyborg':
                        sounds = self.getFactory().impactMetalSoundsMedium
                    else:
                        sounds = self.getFactory().impactSoundsMedium
                    sound = sounds[random.randrange(len(sounds))]
                    bs.playSound(sound,1.0,position=self.node.position)
                else:
                    bs.statAdd('Punches Hit')
                    if self.onFire: node.handleMessage(bs.FireMessage(gFireDuration/2,self.sourcePlayer))

                t = self.node.punchPosition
                punchDir = self.node.punchVelocity
                v = self.node.punchMomentumLinear

                self._punchedNodes.add(node)
                if bs.getConfig().get('Cheat OPM',True):
                    punchMagnitude = punchPower*punchMomentumAngular*60.0*40
                    velocityMagnitude = punchPower*10
                else:
                    punchMagnitude = punchPower*punchMomentumAngular*60.0
                    velocityMagnitude = punchPower*40
                    
                self.currentlyPunching = False
                node.handleMessage(bs.HitMessage(pos=t,
                                                velocity=v,
                                                magnitude=punchMagnitude,
                                                velocityMagnitude=velocityMagnitude,
                                                radius=0,
                                                srcNode=self.node,
                                                sourcePlayer=self.sourcePlayer,
                                                forceDirection = punchDir,
                                                hitType='punch',
                                                hitSubType='superPunch' if self._hasBoxingGloves else 'default'))
                # also apply opposite to ourself for the first punch only
                # ..this is given as a constant force so that it is more noticable for slower punches
                # where it matters.. for fast awesome looking punches its ok if we punch 'through' the target
                mag = -400.0
                if self._hockey: mag *= 0.5
                if len(self._punchedNodes) == 1:  
                    self.node.handleMessage("kickBack",t[0],t[1],t[2],
                                                                          punchDir[0],punchDir[1],punchDir[2],mag)
                                                                          
                if node.getNodeType() == 'spaz':
                    self.punchCombo += 1
                    self.punchComboTimer = bs.Timer(self.punchComboCooldown,bs.WeakCall(self.punchComboReset))
                                                                          
                held = self.node.holdNode
                if held == node:
                    def _throwOff(): self.ninjaThrow = False
                    bs.gameTimer(750, _throwOff)
                    
                    self.ninjaThrow = True
                    bs.playSound(self.getFactory().ninjaGrabSound,0,position=self.node.position)

                if self.hijumpSound and punchMagnitude > 10 and node.getNodeType() == 'spaz': # give style points when punching players mid-air
                    try: 
                        if self.sourcePlayer.getTeam() != node.sourcePlayer.getTeam():
                            self.catchphrase()
                            self.style(self.sourcePlayer,3)
                    except StandardError: pass

        elif isinstance(m,_PickupMessage):
            opposingNode,opposingBody = bs.getCollisionInfo('opposingNode','opposingBody')

            if opposingNode is None or not opposingNode.exists(): return True

            # dont allow picking up of invincible dudes
            try:
                if opposingNode.invincible == True: return True
            except Exception: pass

            #if we're grabbing the pelvis of a non-shattered spaz, we wanna grab the torso instead
            if opposingNode.getNodeType() == 'spaz' and not opposingNode.shattered and opposingBody == 4:
                opposingBody = 1
            #if we're grabbing a frozen body by its head and no kids are watching, rip if off, play a sound effect and a catchphrase - truly gruesome.
            elif opposingNode.getNodeType() == 'spaz' and opposingNode.frozen and not opposingNode.shattered and opposingBody == 0 and not bsInternal._getSetting('Kid Friendly Mode'):
                bs.playSound(self.getFactory().splatterSounds[0],4.0,position=self.node.position)
                opposingNode.handleMessage(bs.ShouldShatterMessage())
                bs.emitBGDynamics(position=opposingNode.position,
                                velocity=opposingNode.velocity,
                                count=int(random.random()*10.0+10.0),scale=0.7,spread=0.4,chunkType='ice');
                bs.emitBGDynamics(position=opposingNode.position,
                                velocity=opposingNode.velocity,
                                count=int(random.random()*10.0+10.0),scale=0.4,spread=0.4,chunkType='ice');
                try: 
                    if self.sourcePlayer.getTeam() != opposingNode.sourcePlayer.getTeam():
                        self.catchphrase()
                        self.style(self.sourcePlayer)
                except StandardError: pass
            if self.onFire:
                if opposingNode.getNodeType() == 'spaz': opposingNode.handleMessage(bs.FireMessage(gFireDuration/6,self.sourcePlayer))
                elif opposingNode.colorTexture == bs.getTexture('shrapnelGlue'):
                    opposingNode.handleMessage(bs.HitMessage(hitSubType='fire'))
            # special case - if we're holding a flag, dont replace it
            # ( hmm - should make this customizable or more low level )
            held = self.node.holdNode
            if (held is not None and held.exists()
                and held.getNodeType() == 'flag'): return True
            self.node.holdBody = opposingBody # needs to be set before holdNode
            self.node.holdNode = opposingNode        
      #      if opposingNode.getNodeType() == 'spaz': opposingNode.holdNode = bs.Node(None)
      #      held = self.node.holdNode
       #     if held is not None and held.exists() and held.getNodeType() == 'flag':
       #         return True
        #        
        #    self.lastPickupTime = bs.getGameTime()-(self._pickupCooldown*0.85) # Reduce pickup cooldown if you pick something up (counts only on release)
        #        
        #    self.node.holdBody = opposingBody # needs to be set before holdNode
        #    self.node.holdNode = opposingNode
        elif isinstance(m,_PlayerTouchMessage):
            opposingNode = bs.getCollisionInfo('opposingNode')
            if self.onFire and opposingNode.onFire == False: opposingNode.handleMessage(bs.FireMessage(gFireDuration/2.65,self.sourcePlayer))
            
            pos = self.node.position
            oPos = opposingNode.position
            vel = self.node.velocity
            oVel = opposingNode.velocity
            
            def _stopSlowmo(): bs.getSharedObject('globals').slowMotion = False
            def _startSlowmo(): bs.getSharedObject('globals').slowMotion = True
            
            speed = math.sqrt(math.pow(oVel[0]-vel[0],2)+math.pow(oVel[1]-vel[1],2)+math.pow(oVel[2]-vel[2],2))*100
            
            # if you hit someone during a dodge
            if self._duringDodge:
            
                # knock anybody who gets in your way
                if not bs.getActivity()._isSlowMotion:
                    bs.netTimer(1,bs.Call(_startSlowmo))
                    bs.netTimer(int(min(40,speed*0.05)),bs.Call(_stopSlowmo))
                
                if self.onFire: opposingNode.handleMessage(bs.  FireMessage(gFireDuration/2,self.sourcePlayer))
                if opposingNode.invincible:
                    bs.playSound(self.getFactory().blockSound,1.0,position=self.node.position)
                else:
                    opposingNode.handleMessage(bs.HitMessage(flatDamage=speed*0.40,
                                             hitType='dash',
                                             sourcePlayer=self.sourcePlayer))
                    opposingNode.handleMessage("impulse",self.node.position[0],self.node.position[1],self.node.position[2],
                                        pos[0],pos[1],pos[2],
                                        speed*0.045,speed*0.045,0,0,vel[0],1,vel[2])
                def _stun(): self.node.handleMessage("knockout", 200.0)
                self.node.handleMessage("kickBack",oPos[0],oPos[1],oPos[2],
                                        -vel[0],-vel[1],-vel[2],speed*0.95)
                self.node.handleMessage("knockout", 500.0)
                bs.gameTimer(500,_stun)
                                         
                bs.playSound(self.getFactory().dodgeHitSound,2.0,position=pos)
                                        
                # deal damage only once, hence remove the dash status
                self._duringDodge = False
            elif (not self.footing 
                  and (self.node.knockout > 0 or self._dead) 
                  and self.midairCannonball 
                  and not self.midairDamaged 
                  and speed > 2000):
                if opposingNode is not None and opposingNode.exists() and not opposingNode in self._punchedNodes and opposingNode.holdNode != self.node:
                    self._punchedNodes.add(opposingNode)
                    mag = speed*0.05
                    velMag = mag*5
                    
                    bs.playSound(self.getFactory().dodgeHitSound,min(mag*0.05,0.75),position=opposingNode.positionCenter)
                    opposingNode.handleMessage("hurtSound")
                    opposingNode.handleMessage("impulse",oPos[0],oPos[1],oPos[2],
                                        pos[0],pos[1],pos[2],
                                        speed*0.05,speed*0.05,0,0,vel[0],1,vel[2])
                    opposingNode.handleMessage("knockout", speed*0.5)
                    opposingNode.handleMessage(bs.HitMessage(flatDamage=speed*0.45,
                                             hitType='impact',
                                             sourcePlayer=self.sourcePlayer))
            self.midairDamaged = True
        else:
            bs.Actor.handleMessage(self,m)

    def dropBomb(self):
        """
        Tell the spaz to drop one of his bombs, and returns
        the resulting bomb object.
        If the spaz has no bombs or is otherwise unable to
        drop a bomb, returns None.
        """

        if (self.stockBombCount <=0 and self.bombCount <= 0) or self.frozen: return
        p = self.node.positionForward
        v = self.node.velocity
        
        if self.stockBombCount > 0:
            if self.stockBombType == 'landMine':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'landMine'
            elif self.stockBombType == 'healBomb':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'healing'
            elif self.stockBombType == 'grenade':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'grenade'
            elif self.stockBombType == 'scatter':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'scatter'
            elif self.stockBombType == 'cake':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'cake'
            elif self.stockBombType == 'gloo':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'gloo'
            elif self.stockBombType == 'instant':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'instant'
            elif self.stockBombType == 'firework':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'firework'
            elif self.stockBombType == 'cluster':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'cluster'
            elif self.stockBombType == 'tesla':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'tesla'
            elif self.stockBombType == 'hijump':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'hijump'
            elif self.stockBombType == 'glue':
                droppingBomb = False
                self.stockBombCount -= 1
                bombType = 'glue'
            else:
                droppingBomb = True
                bombType = self.bombType
        else:
            droppingBomb = True
            if bs.getConfig().get('Cheat EXP',True):
                types = (['normal'] * 3 +
                        ['ice'] * 2 +
                        ['fire'] * 2 +
                        ['combat'] * 2 +
                        ['ranger'] * 2 +
                        ['dynamite'] * 2 +
                        ['impact'] +
                        ['snowball'] +
                        ['grenade'] * 2 +
                        ['knocker'] * 2 +
                        ['magnet'] +
                        ['glue'] +
                        ['cake'] +
                        ['tesla'])
                bombType = random.choice(types)
            else: bombType = self.bombType
            
        if bombType == 'hijump' or self.stockBombType == 'hijump': 
            # Make a jump sound and don't stun the Spaz
            def _jump(node):
                node.handleMessage("jumpSound")
                node.handleMessage("celebrate",250)
            bs.gameTimer(75,bs.Call(_jump,self.node))
            
            # Make Spaz jump
            self.force = 90
            self.teleForce = self.force
            
            pos = self.node.position
            vel = (self.node.velocity[0],self.node.velocity[1],self.node.velocity[2])
            
            self.node.handleMessage("impulse",pos[0],pos[1],pos[2],
                                    0,0,0,
                                    self.force,self.teleForce,0,0,vel[0],1,vel[2])
            
                                    
        if self.stockBombCount == 0: self.stockBombType = None

        if bombType == 'hijump': # Hijump shouldn't be Radius Buffed
            if self.onFire: self.killFire() # Extinguish yourself if on fire
            self._punchedNodes = set()
            self.footing = False
            if not self.hijumpSound and not self.shield:
                self.hijumpSound = bs.newNode('sound',owner=self.node,attrs={'sound':self.getFactory().hijumpMidairSound,'volume':0.5})
                self.node.connectAttr('positionCenter',self.hijumpSound,'position')
            
            self.node.handleMessage('celebrateR',500)
            bomb = bs.Bomb(position=(p[0],p[1],p[2]),
                   velocity=(v[0],v[1],v[2]),
                   bombType=bombType,
                   blastRadius=self.defaultBlastRadius,
                   blastRadiusBuffed=False,
                   sourcePlayer=self.sourcePlayer,
                   owner=self.node).autoRetain()
        else:
            bomb = bs.Bomb(position=(p[0],p[1],p[2]),
                   velocity=(v[0],v[1],v[2]),
                   bombType=bombType,
                   blastRadius=self.blastRadius,
                   blastRadiusBuffed=self.blastRadiusBuffed,
                   sourcePlayer=self.sourcePlayer,
                   bombShape=self.bombShape,
                   owner=self.node).autoRetain()
                       
        if droppingBomb:
            self.bombCount -= 1
            bomb.node.addDeathAction(bs.WeakCall(self.handleMessage,_BombDiedMessage()))

        self._pickUp(bomb.node)

        for c in self._droppedBombCallbacks: c(self,bomb)
        
        if self.stockBombCount > 0: 
            self.node.counterText = 'x'+str(self.stockBombCount)
        else:
            self.stockBombType = None
            self.node.counterText = ''

        return bomb

    def _pickUp(self,node):
        if self.node.exists() and node.exists():
            if self._hasSpeedBoots and not self.getActivity()._map.isHockey:
                def _safeSetAttr(node,attr,val):
                    if node.exists(): setattr(node,attr,val)
                bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'hockey',False))
        
            self.node.holdBody = 0 # needs to be set before holdNode
            self.node.holdNode = node
            
    def setStockBombs(self,type):
        """
        Set the number of bombs of limited quantities that spaz is carrying
        """
        if not self.node.exists(): return
        
        if type == 'hijump': 
            self.maxCount = 6
            self.addCount = 3
            self.tex = bs.Powerup.getFactory().texHijump
        elif type == 'landMine': 
            self.maxCount = 3
            self.addCount = 3
            self.tex = bs.Powerup.getFactory().texLandMines
        elif type == 'cake': 
            self.maxCount = 1
            self.addCount = 1
            self.tex = bs.Powerup.getFactory().texCake
        elif type == 'tesla': 
            self.maxCount = 1
            self.addCount = 1
            self.tex = bs.Powerup.getFactory().texTesla
        elif type == 'glue': 
            self.maxCount = 2
            self.addCount = 1
            self.tex = bs.Powerup.getFactory().texGlueBombs
        elif type == 'grenade': 
            self.maxCount = 4
            self.addCount = 2
            self.tex = bs.Powerup.getFactory().texGrenades
        elif type == 'gloo': 
            self.maxCount = 5
            self.addCount = 3
            self.tex = bs.Powerup.getFactory().texGloo
        elif type == 'instant': 
            self.maxCount = 1
            self.addCount = 1
            self.tex = bs.Powerup.getFactory().texInstantBomb
        elif type == 'cluster': 
            self.maxCount = 1
            self.addCount = 1
            self.tex = bs.Powerup.getFactory().texClusterBomb
        elif type == 'scatter': 
            self.maxCount = 5
            self.addCount = 1
            self.tex = bs.Powerup.getFactory().texScatterBombs
        elif type == 'firework': 
            self.maxCount = 1
            self.addCount = 1
            self.tex = bs.Powerup.getFactory().texFireworkBombs
        elif type == 'healBomb': 
            self.maxCount = 2
            self.addCount = 1
            self.tex = bs.Powerup.getFactory().texHealBombs
        elif type == 'removeOne':
            self.stockBombCount -= 1
            if self.stockBombCount > 0: 
                self.node.counterText = 'x'+str(self.stockBombCount)
            else:
                self.stockBombCount = 0
                self.stockBombType = None
                self.node.counterText = ''
            return
        else:
            raise Exception('This type does not exist! Available: hijump | landmine | cake | grenade | healBomb | removeOne | cluster | gloo | scatter')
            return
        
        if self.stockBombType == type: self.stockBombCount += self.addCount
        else: self.stockBombCount = self.addCount
        self.stockBombType = type
        if self.stockBombCount > self.maxCount: self.stockBombCount = self.maxCount
        
        if self.stockBombCount != 0:
            self.node.counterText = 'x'+str(self.stockBombCount)
            self.node.counterTexture = self.tex
        elif self.stockBombType == None:
            self.node.counterText = ''
        else:
            self.node.counterText = ''

    def curseExplode(self,sourcePlayer=None):
        """
        Explode the poor spaz as happens when
        a curse timer runs out.
        """

        # convert None to an empty player-ref
        if sourcePlayer is None: sourcePlayer = bs.Player(None)
        
        if self._cursed and self.node.exists():
            self.sound.delete() # Stop the curse sound
            if self.overcharged == True: 
                try: self.overchargedLight.delete() # Remove the overcharged light
                except AttributeError:
                    self.overchargedLight = bs.newNode('light',
                           attrs={'position':self.node.position,
                                  'color': (0.6,0.05,0.6),
                                  'volumeIntensityScale': 0.25}) 
                    self.overchargedLight.delete()
            self.shatter(extreme=True)
            
            activity = self._activity()
            if activity:
                if self.overcharged:
                    self.blastType = 'overdrive'
                    if bs.getConfig().get('Party Mode', True): self.radius = gOverchargedCurseExplosionPARTY
                    elif isinstance(bs.getSession(),bs.CoopSession): self.radius = gOverchargedCurseExplosionCOOP
                    else: self.radius = gOverchargedCurseExplosion
                else:
                    self.blastType = self.blastType2
                    if bs.getConfig().get('Party Mode', True): self.radius = gRegularCurseExplosionPARTY
                    elif isinstance(bs.getSession(),bs.CoopSession): self.radius = self.defaultBlastRadius
                    else: self.radius = gRegularCurseExplosion
                    
            if self.blastRadiusBuffed: 
                bs.playSound(self.getFactory().curseBuffedSound,1.5,position=self.node.position)
                self.buffExplode = bs.newNode('light',
                            attrs={'position':self.node.position,
                                    'color': (1.0,1.0,0.2),
                                    'radius':0.5,
                                    'volumeIntensityScale': 0.5})     
                bs.animate(self.buffExplode,'intensity',{0:0,100:2,500:0},loop=False)
                bs.gameTimer(500,self.buffExplode.delete)
                self.radius += 2.0

            bs.Blast(position=self.node.position,
                 velocity=self.node.velocity,
                 blastRadius=self.radius,blastType=self.blastType,
                 sourcePlayer=sourcePlayer if sourcePlayer.exists() else self.sourcePlayer).autoRetain()
            self.handleMessage(bs.DieMessage())
            self._cursed = False

    def shatter(self,extreme=False,type='normal'):
        """
        Break the poor spaz into little bits.
        """
        if self.shattered: return
        self.shattered = True
        if self.frozen:
            # momentary flash of light
            light = bs.newNode('light',
                               attrs={'position':self.node.position,
                                      'radius':0.5,
                                      'heightAttenuated':False,
                                      'color': (0.8,0.8,1.0)})
            
            bs.animate(light,'intensity',{0:3.0, 40:0.5, 80:0.07, 300:0})
            bs.gameTimer(300,light.delete)
            # emit ice chunks..
            bs.emitBGDynamics(position=self.node.position,
                              velocity=self.node.velocity,
                              count=int(random.random()*10.0+10.0),scale=0.6,spread=0.2,chunkType='ice');
            bs.emitBGDynamics(position=self.node.position,
                              velocity=self.node.velocity,
                              count=int(random.random()*10.0+10.0),scale=0.3,spread=0.2,chunkType='ice');

            bs.playSound(self.getFactory().shatterSound,1.0,position=self.node.position)
        else:
            import bsInternal
            import bsSnowballSkirmish
            # Snowball Skirmish is a wholesome minigame - don't dismember
            if isinstance(bs.getActivity(),bsSnowballSkirmish.SnowballSkirmishGame): return
            if type == 'ranger':
                def _sound(): bs.playSound(self.getFactory().playerDissolveSound,1.0,position=self.node.position)
                bs.gameTimer(int(round(1+random.random()*100)),_sound)
            elif type == 'fire':
                self.node.style = 'ali'
                self.node.colorTexture = bs.getTexture('shrapnelAsh')
                self.node.colorMaskTexture = bs.getTexture('black')
                bs.Particle(self.node.position,
                            self.node.velocity,
                            'ashpile',
                            0.5)
            elif not bsInternal._getSetting('Kid Friendly Mode'):
                if bs.getActivity()._crowdActive and random.randint(0,1) == 1: 
                    def _sound(): bs.playSound(self.getFactory().crowdOhhSound,6.5)
                    bs.gameTimer(300,_sound)
                if extreme: 
                    bs.playSound(self.getFactory().splatterExtremeSound,4.0,position=self.node.position)
                else: 
                    bs.playSound(self.getFactory().getRandomSplatterSound(),4.0,position=self.node.position)
        self.handleMessage(bs.DieMessage())
        self.node.shattered = 2 if extreme else 1

    def _hitSelf(self,intensity):

        # clean exit if we're dead..
        try: pos = self.node.position
        except Exception: return

        self.handleMessage(bs.HitMessage(flatDamage=50.0*intensity,
                                         pos=pos,
                                         forceDirection=self.node.velocity,
                                         hitType='impact'))
        if intensity > 5: 
            if self._character in ['Juice-Boy','Frosty','Exploder','Lucy Chance']:
                sounds = self.getFactory().impactCardboardSoundsHarder
            elif self._character in ['B-9000','Zill','Puck','Sir Bombalot','Bones']:
                sounds = self.getFactory().impactMetalSoundsHarder
            else:
                sounds = self.getFactory().impactSoundsHarder
        elif intensity > 2: 
            if self._character in ['Juice-Boy','Frosty','Exploder','Lucy Chance']:
                sounds = self.getFactory().impactCardboardSoundsHard
            elif self._character in ['B-9000','Zill','Puck','Sir Bombalot','Bones']:
                sounds = self.getFactory().impactMetalSoundsHard
            else:
                sounds = self.getFactory().impactSoundsHard
        else: 
            if self._character in ['Juice-Boy','Frosty','Exploder','Lucy Chance']:
                sounds = self.getFactory().impactCardboardSoundsMedium
            elif self._character in ['B-9000','Zill','Puck','Sir Bombalot','Bones']:
                sounds = self.getFactory().impactMetalSoundsMedium
            else:
                sounds = self.getFactory().impactSoundsMedium
        s = sounds[random.randrange(len(sounds))]
        bs.playSound(s,position=pos,volume=4)
        
    def _getBombTypeTex(self):
        bombFactory = bs.Powerup.getFactory()
        if self.bombType == 'sticky': return bombFactory.texStickyBombs
        elif self.bombType == 'ice': return bombFactory.texIceBombs
        elif self.bombType == 'fire': return bombFactory.texFireBombs
        elif self.bombType == 'ranger': return bombFactory.texRangerBombs
        elif self.bombType == 'combat': return bombFactory.texCombatBombs
        elif self.bombType == 'knocker': return bombFactory.texKnockerBombs
        elif self.bombType == 'dynamite': return bombFactory.texDynamitePack
        elif self.bombType == 'impact': return bombFactory.texImpactBombs
        elif self.bombType == 'healing': return bombFactory.texHealBombs
        elif self.bombType == 'magnet': return bombFactory.texMagnet
        elif self.bombType == 'firework': return bombFactory.texFireworkBombs
        elif self.bombType == 'infatuate': return bombFactory.texInfatuateBombs
        elif self.bombType == 'fraction': return bombFactory.texDigitalBombs
        elif self.bombType == 'snowball': return bombFactory.texSnowball
        elif self.bombType == 'palette': return bombFactory.texPalette
        elif self.bombType == 'radius': return bombFactory.texRadiusBombs
        elif self.bombType == 'hunter': return bombFactory.texHunterBombs
        elif self.bombType == 'splash': return bombFactory.texBloomingBombs
        else: raise Exception()
        
    def _flashBillboard(self,tex):
        self.node.billboardTexture = tex
        self.node.billboardCrossOut = False
        bs.animate(self.node,"billboardOpacity",{0:0.0,250:1.0,500:0.0})

    def setBombCount(self,count):
        # we cant just set bombCount cuz some bombs may be laid currently
        # so we have to do a relative diff based on max
        diff = count - self._maxBombCount
        self._maxBombCount += diff
        self.bombCount += diff
        
    def _speedWearOffFlash(self):
        if self.node.exists():
            self.node.billboardTexture = bs.Powerup.getFactory().texSpeed
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _speedWearOff(self):
        factory = self.getFactory()
        self._hasSpeedBoots = False
        def _safeSetAttr(node,attr,val):
            if node.exists(): setattr(node,attr,val)
        bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'hockey',False))
        self._punchPowerScale = gBasePunchPowerScale
        self._punchCooldown = gBasePunchCooldown
        self.punchResetTimer = bs.Timer(1,bs.WeakCall(self.punchReset))
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,position=self.node.position)
            bs.playSound(factory.speedDownSound,position=self.node.position)
            self.node.billboardOpacity = 0.0

    def _glovesWearOffFlash(self):
        if self.node.exists():
            self.node.boxingGlovesFlashing = 1
            self.node.billboardTexture = bs.Powerup.getFactory().texPunch
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _glovesWearOff(self):
        self._punchPowerScale = gBasePunchPowerScale
        self._punchCooldown = gBasePunchCooldown
        self._hasBoxingGloves = False
        self._hasSpeedBoots = False
        self.punchResetTimer = bs.Timer(1,bs.WeakCall(self.punchReset))
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,position=self.node.position)
            self.node.boxingGloves = 0
            self.node.billboardOpacity = 0.0
            
    def _blastBuffWearOffFlash(self):
        if self.node.exists():
            self.node.billboardTexture = bs.Powerup.getFactory().texBlast
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _blastBuffWearOff(self):
        self.setBombCount(self.defaultBombCount)
        self.blastRadiusBuffed = False
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,position=self.node.position)
            self.node.billboardOpacity = 0.0

    def _multiBombWearOffFlash(self):
        if self.node.exists():
            self.node.billboardTexture = bs.Powerup.getFactory().texBomb
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _multiBombWearOff(self):
        self.setBombCount(self.defaultBombCount)
        self.blastRadiusBuffed = False
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,position=self.node.position)
            self.node.billboardOpacity = 0.0

    def _bombWearOffFlash(self):
        if self.node.exists():
            self.node.billboardTexture = self._getBombTypeTex()
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _bombWearOff(self):
        self.bombType = self.bombTypeDefault
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,position=self.node.position)
            self.node.billboardOpacity = 0.0

class PlayerSpazDeathMessage(object):
    """
    category: Message Classes

    A bs.PlayerSpaz has died.

    Attributes:

       spaz
          The bs.PlayerSpaz that died.

       killed
          If True, the spaz was killed;
          If False, they left the game or the round ended.

       killerPlayer
          The bs.Player that did the killing, or None.

       how
          The particular type of death.
    """
    def __init__(self,spaz,wasKilled,killerPlayer,how):
        """
        Instantiate a message with the given values.
        """
        self.spaz = spaz
        self.killed = wasKilled
        self.killerPlayer = killerPlayer
        self.how = how

class PlayerSpazHurtMessage(object):
    """
    category: Message Classes

    A bs.PlayerSpaz was hurt.

    Attributes:

       spaz
          The bs.PlayerSpaz that was hurt
    """
    def __init__(self,spaz):
        """
        Instantiate with the given bs.Spaz value.
        """
        self.spaz = spaz


class PlayerSpaz(Spaz):
    """
    category: Game Flow Classes
    
    A bs.Spaz subclass meant to be controlled by a bs.Player.

    When a PlayerSpaz dies, it delivers a bs.PlayerSpazDeathMessage
    to the current bs.Activity. (unless the death was the result of the
    player leaving the game, in which case no message is sent)

    When a PlayerSpaz is hurt, it delivers a bs.PlayerSpazHurtMessage
    to the current bs.Activity.
    """


    def __init__(self,color=(1,1,1),highlight=(0.5,0.5,0.5),character="Spaz",player=None,bombShape='Regular',powerupsExpire=True):
        """
        Create a spaz for the provided bs.Player.
        Note: this does not wire up any controls;
        you must call connectControlsToPlayer() to do so.
        """
        # convert None to an empty player-ref
        if player is None: player = bs.Player(None)

        self._player = player
        
        # set the player's own bomb shape and catchphrases
        # if the "database" is empty, leave it at default
        if self._player != bs.Player(None):
            for list in bsUtils.gPlayerBombShapes:
                if list[0] == self._player: 
                    bombShape = list[1]
                    continue
            for phrases in bsUtils.gPlayerCatchphraseData:
                if phrases[0] == self._player: 
                    catchphrases = phrases[1]
                    continue
        
        
        
        
        
        
        
        Spaz.__init__(self,color=color,highlight=highlight,character=character,sourcePlayer=player,bombShape=bombShape,startInvincible=True,powerupsExpire=False if bs.getConfig().get('No Time Limit Powerups',True) else True,catchphrases=catchphrases)
        self.lastPlayerAttackedBy = None # FIXME - should use empty player ref
        self.lastAttackedTime = 0
        self.lastAttackedType = None
        self.heldCount = 0
        if bs.getConfig().get('Permanent Boxing Gloves',True):
            self.equipBoxingGloves()
        if bs.getConfig().get('Gain Shield',True):
            self.equipShields()
        if bs.getConfig().get('Unlimited Bombs',True):
            self.bombCount = 100
        self.blastType2 = 'normal'
            
        if bs.getConfig().get('Rainbow Skin', True): self.rainbow()
        #####self._defense()#######
        self.lastPlayerHeldBy = None # FIXME - should use empty player ref here

        # grab the node for this player and wire it to follow our spaz (so players' controllers know where to draw their guides, etc)
        if player.exists():
            playerNode = bs.getActivity()._getPlayerNode(player)
            self.node.connectAttr('torsoPosition',playerNode,'position')

    def __superHandleMessage(self,m):
        super(PlayerSpaz,self).handleMessage(m)
        
        
    def rainbow(self):
        colors = {0: (2, 0, 0),
                        500: (2, 2, 0),
                        1000: (0, 2, 0),
                        1500: (0, 2, 2),
                        2000: (2, 0, 2),
                        2500: (0, 0, 2),
                        3000: (2, 2, 2,),
                        3500: (1, 0, 0),
                        4000: (1, 0, 0),
                        4500: (1, 1, 0),
                        5000: (0, 1, 0),
                        5500: (0, 1, 1),
                        6000: (1, 0, 1),
                        6500: (0, 0, 1),
                        7000: (1, 0, 0),
                        7500: (0, 0, 0)}
        highlights = {0: (0, 0, 0),
                        500: (1, 0, 0),
                        1000: (0, 0, 1),
                        1500: (1, 0, 1),
                        2000: (0, 1, 1),
                        2500: (0, 1, 0),
                        3000: (1, 1, 0,),
                        3500: (1, 0, 0),
                        4000: (1, 0, 0),
                        4500: (2, 2, 2),
                        5000: (0, 0, 2),
                        5500: (2, 0, 2),
                        6000: (0, 2, 2),
                        6500: (0, 2, 0),
                        7000: (2, 2, 0),
                        7500: (2, 0, 0)}
        bsUtils.animateArray(self.node, 'color', 3, colors, True)
        bsUtils.animateArray(self.node, 'highlight', 3, highlights, True)
        
    def getPlayer(self):
        """
        Return the bs.Player associated with this spaz.
        Note that while a valid player object will always be
        returned, there is no guarantee that the player is still
        in the game.  Call bs.Player.exists() on the return value
        before doing anything with it.
        """
        return self._player

    def connectControlsToPlayer(self,enableJump=True,enablePunch=True,enablePickUp=True,enableBomb=True,enableRun=True,enableFly=True):
        """
        Wire this spaz up to the provided bs.Player.
        Full control of the character is given by default
        but can be selectively limited by passing False
        to specific arguments.
        """

        player = self.getPlayer()
        
        # reset any currently connected player and/or the player we're now wiring up
        if self._connectedToPlayer is not None:
            if player != self._connectedToPlayer: player.resetInput()
            self.disconnectControlsFromPlayer()
        else: player.resetInput()

        player.assignInputCall('upDown',self.onMoveUpDown)
        player.assignInputCall('leftRight',self.onMoveLeftRight)
        player.assignInputCall('holdPositionPress',self._onHoldPositionPress)
        player.assignInputCall('holdPositionRelease',self._onHoldPositionRelease)
        
        self.enableJump = enableJump
        self.enablePickUp = enablePickUp
        self.enablePunch = enablePunch
        self.enableBomb = enableBomb
        self.enableFly = enableFly
        
        if enableJump:
            player.assignInputCall('jumpPress',self.onJumpPress)
            player.assignInputCall('jumpRelease',self.onJumpRelease)
        if enablePickUp:
            player.assignInputCall('pickUpPress',self.onPickUpPress)
            player.assignInputCall('pickUpRelease',self.onPickUpRelease)
        if enablePunch:
            player.assignInputCall('punchPress',self.onPunchPress)
            player.assignInputCall('punchRelease',self.onPunchRelease)
        if enableBomb:
            player.assignInputCall('bombPress',self.onBombPress)
            player.assignInputCall('bombRelease',self.onBombRelease)
        if enableRun:
            player.assignInputCall('run',self.onRun)
        if enableFly:
            player.assignInputCall('flyPress',self.onFlyPress)
            player.assignInputCall('flyRelease',self.onFlyRelease)

        self._connectedToPlayer = player

        
    def disconnectControlsFromPlayer(self):
        """
        Completely sever any previously connected
        bs.Player from control of this spaz.
        """
        if self._connectedToPlayer is not None:
            self._connectedToPlayer.resetInput()
            self._connectedToPlayer = None
            # send releases for anything in case its held..
            self.onMoveUpDown(0)
            self.onMoveLeftRight(0)
            self._onHoldPositionRelease()
            self.onJumpRelease()
            self.onPickUpRelease()
            self.onPunchRelease()
            self.onBombRelease()
            self.onRun(0.0)
            self.onFlyRelease()
        else: print 'WARNING: disconnectControlsFromPlayer() called for non-connected player'

    def handleMessage(self,m):
        self._handleMessageSanityCheck()

        # keep track of if we're being held and by who most recently
        if isinstance(m,bs.PickedUpMessage):
            self.__superHandleMessage(m) # augment standard behavior
            self.heldCount += 1
            pickedUpBy = m.node.sourcePlayer 
            if self.ninjaGrabbed: 
                def _throwOff(): m.node.getDelegate().ninjaThrow = False
                bs.gameTimer(750, _throwOff)
                m.node.getDelegate().ninjaThrow = True
                
                bs.playSound(self.getFactory().ninjaGrabSound,0,position=self.node.position)
            if pickedUpBy is not None and pickedUpBy.exists():
                self.lastPlayerHeldBy = pickedUpBy

        elif isinstance(m,bs.DroppedMessage):
            self.__superHandleMessage(m) # augment standard behavior
            self.heldCount -= 1
            if self.heldCount < 0:
                print "ERROR: spaz heldCount < 0"
                
            # let's count someone dropping us as an attack..
            try: pickedUpBy = m.node.sourcePlayer
            except Exception: pickedUpBy = None
            if pickedUpBy is not None and pickedUpBy.exists():
                self.lastPlayerAttackedBy = pickedUpBy
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = ('pickedUp','default')
            
        elif isinstance(m,bs.DieMessage):

            # report player deaths to the game
            if not self._dead:

                # immediate-mode or left-game deaths don't count as 'kills'
                killed = (m.immediate==False and m.how!='leftGame')

                activity = self._activity()

                if not killed:
                    killerPlayer = None
                else:
                    # if this player was being held at the time of death, the holder is the killer
                    if self.heldCount > 0 and self.lastPlayerHeldBy is not None and self.lastPlayerHeldBy.exists():
                        killerPlayer = self.lastPlayerHeldBy
                    else:
                        # otherwise, if they were attacked by someone in the last few seconds,
                        # that person's the killer.. otherwise it was a suicide.
                        # FIXME - currently disabling suicides in Co-Op since all bot kills would
                        # register as suicides; need to change this from lastPlayerAttackedBy to
                        # something like lastActorAttackedBy to fix that.
                        if self.lastPlayerAttackedBy is not None and self.lastPlayerAttackedBy.exists() and bs.getGameTime() - self.lastAttackedTime < 4000:
                            killerPlayer = self.lastPlayerAttackedBy
                        else:
                            # ok, call it a suicide unless we're in co-op
                            if activity is not None and not isinstance(activity.getSession(), bs.CoopSession):
                                killerPlayer = self.getPlayer()
                            else:
                                killerPlayer = None
                            
                if killerPlayer is not None and not killerPlayer.exists():
                    killerPlayer = None

                # only report if both the player and the activity still exist
                if killed and activity is not None and self.getPlayer().exists():
                    activity.handleMessage(PlayerSpazDeathMessage(self, killed, killerPlayer, m.how))                   
            self.__superHandleMessage(m) # augment standard behavior

        # keep track of the player who last hit us for point rewarding
        elif isinstance(m,bs.HitMessage):
            if m.sourcePlayer is not None and m.sourcePlayer.exists():
                self.lastPlayerAttackedBy = m.sourcePlayer
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = (m.hitType,m.hitSubType)
            self.__superHandleMessage(m) # augment standard behavior
            activity = self._activity()
            if activity is not None:
                activity.handleMessage(PlayerSpazHurtMessage(self))
        else:
            Spaz.handleMessage(self,m)


class RespawnIcon(object):
    """
    category: Game Flow Classes

    An icon with a countdown that appears alongside the screen;
    used to indicate that a bs.Player is waiting to respawn.
    """
    
    def __init__(self,player,respawnTime):
        """
        Instantiate with a given bs.Player and respawnTime (in milliseconds)
        """
        activity = bs.getActivity()
        onRight = False
        self._visible = True
        if isinstance(bs.getSession(),bs.TeamsSession):
            onRight = player.getTeam().getID()%2==1
            # store a list of icons in the team
            try: respawnIcons = player.getTeam().gameData['_spazRespawnIconsRight']
            except Exception: respawnIcons = player.getTeam().gameData['_spazRespawnIconsRight'] = {}
            offsExtra = -20
        else:
            onRight = False
            # store a list of icons in the activity
            try: respawnIcons = activity._spazRespawnIconsRight
            except Exception: respawnIcons = activity._spazRespawnIconsRight = {}
            if isinstance(activity.getSession(),bs.FreeForAllSession): offsExtra = -150
            else: offsExtra = -20

        try: maskTex = player.getTeam().gameData['_spazRespawnIconsMaskTex']
        except Exception: maskTex = player.getTeam().gameData['_spazRespawnIconsMaskTex'] = bs.getTexture('characterIconMask')

        # now find the first unused slot and use that
        index = 0
        while index in respawnIcons and respawnIcons[index]() is not None and respawnIcons[index]()._visible: index += 1
        respawnIcons[index] = weakref.ref(self)

        offs = offsExtra + index*-53
        icon = player.getIcon()
        texture = icon['texture']
        hOffs = -10
        self._image = bs.NodeActor(bs.newNode('image',
                                              attrs={'texture':texture,
                                                     'tintTexture':icon['tintTexture'],
                                                     'tintColor':icon['tintColor'],
                                                     'tint2Color':icon['tint2Color'],
                                                     'maskTexture':maskTex,
                                                     'position':(-40-hOffs if onRight else 40+hOffs,-180+offs),
                                                     'scale':(32,32), #32,32
                                                     'opacity':1.0,
                                                     'absoluteScale':True,
                                                     'attach':'topRight' if onRight else 'topLeft'}))
        
        bs.animate(self._image.node,'opacity',{0:0,200:0.7})

        self._name = bs.NodeActor(bs.newNode('text',
                                             attrs={'vAttach':'top',
                                                    'hAttach':'right' if onRight else 'left',
                                                    'text':player.getName(),
                                                    'maxWidth':100,
                                                    'hAlign':'center',
                                                    'vAlign':'center',
                                                    'shadow':1.0,
                                                    'flatness':1.0,
                                                    'color':bs.getSafeColor(icon['tintColor']),
                                                    'scale':0.5,
                                                    'position':(-40-hOffs if onRight else 40+hOffs,-205+49+offs)}))
        
        bs.animate(self._name.node,'scale',{0:0,100:0.5})

        self._text = bs.NodeActor(bs.newNode('text',
                                             attrs={'position':(-60-hOffs if onRight else 60+hOffs,-192+offs),
                                                    'hAttach':'right' if onRight else 'left',
                                                    'hAlign':'right' if onRight else 'left',
                                                    'scale':0.9,
                                                    'shadow':0.5,
                                                    'flatness':0.5,
                                                    'vAttach':'top',
                                                    'color':bs.getSafeColor(icon['tintColor']),
                                                    'text':''}))
        
        bs.animate(self._text.node,'scale',{0:0,100:0.9})

        self._respawnTime = bs.getGameTime()+respawnTime
        self._update()
        self._timer = bs.Timer(1000,bs.WeakCall(self._update),repeat=True)

    def _update(self):
        remaining = int(round(self._respawnTime-bs.getGameTime())/1000.0)
        if remaining > 0:
            if self._text.node.exists():
                self._text.node.text = str(remaining)
        else: self._clear()
            
    def _clear(self):
        self._visible = False
        self._image = self._text = self._timer = self._name = None
        


class SpazBotPunchedMessage(object):
    """
    category: Message Classes


    A bs.SpazBot got punched.

    Attributes:

       badGuy
          The bs.SpazBot that got punched.

       damage
          How much damage was done to the bs.SpazBot.
    """
    def __init__(self,badGuy,damage):
        """
        Instantiate a message with the given values.
        """

        self.badGuy = badGuy
        self.damage = damage

class SpazBotDeathMessage(object):
    """
    category: Message Classes


    A bs.SpazBot has died.

    Attributes:

       badGuy
          The bs.SpazBot that was killed.

       killerPlayer
          The bs.Player that killed it (or None).

       how
          The particular type of death.
    """
    def __init__(self,badGuy,killerPlayer,how):
        """
        Instantiate with given values.
        """
        self.badGuy = badGuy
        self.killerPlayer = killerPlayer
        self.how = how


        
class SpazBot(Spaz):
    """
    category: Bot Classes

    A really dumb AI version of bs.Spaz.
    Add these to a bs.BotSet to use them.

    Note: currently the AI has no real ability to
    navigate obstacles and so should only be used
    on wide-open maps.

    When a SpazBot is killed, it delivers a bs.SpazBotDeathMessage
    to the current activity.

    When a SpazBot is punched, it delivers a bs.SpazBotPunchedMessage
    to the current activity.
    """

    
    palette = None
    bombShape = 'Regular'
    character = 'Spaz' #Change through different color palettes and characters depending on the value here
    color=gDefaultBotColor
    highlight=gDefaultBotHighlight
    defaultName = " " #Adds a name to this spaz
    defaultBombType = 'normal'
    defaultBombCount = 3
    defaultBlastRadius = 2.0
    defaultBlastBuff = False # gives our bot a sparkly powered bomb to throw
    defaultSpeedBoots = False #Makes our bot go Super Saiyan
    defaultInvincibility = False
    startCursed = False
    isGrabber = False
    noPoints = False
    bouncy = False
    isBoss = False
    tackle = False
    static = False
    run = False
    impactScale = 1.0
    hitPoints = 1000
    runDistMin = 0.0 # how close we can be to continue running
    chargeDistMin = 0.0 # when we can start a new charge
    chargeDistMax = 2.0 # when we can start a new charge
    chargeSpeedMin = 0.4
    chargeSpeedMax = 1.0
    throwDistMin = 5.0
    throwDistMax = 9.0
    throwiness = 0.7
    throwRate = 1.0
    punchiness = 0.5

    def __init__(self):
        """
        Instantiate a spaz-bot.
        """
        # Check the palette
        if self.palette in ['spy']:
            self.colors = [(1,1,1),(0.1,0.1,0.1),(0.5,0.5,0.5)]
            self.color = random.choice(self.colors)
            if self.color == (1,1,1):
                self.highlight = random.choice([(0.1,0.1,0.1),(0.5,0.5,0.5)])
            elif self.color == (0.1,0.1,0.1):
                self.highlight = random.choice([(1,1,1),(0.5,0.5,0.5)])
            elif self.color == (0.5,0.5,0.5):
                self.highlight = random.choice([(1,1,1),(0.1,0.1,0.1)])
        elif self.palette in ['wizard']:
            self.character = random.choice(['Grumbledorf','Grambeldorfe'])
        elif self.palette in ['wizard_pro']:
            self.character = random.choice(['Grumbledorf','Grambeldorfe'])
            self.defaultShields = random.choice([True,False])
        elif self.palette in ['juice']:
            self.highlight=(random.uniform(0.0,1.0),random.uniform(0.0,1.0),random.uniform(0.0,1.0))
            self.juice_type = random.choice(['fire','ice','normal','knocker','cake','ranger','overdrive','healing','palette'])
            self.defaultBombType = self.juice_type
            if self.juice_type == 'normal':
                self.color=(1,0.9,0.8)
            elif self.juice_type == 'fire':
                self.color=(1.45,0.29,0)
            elif self.juice_type == 'ice':
                self.color=(0.2,1,1.30)
            elif self.juice_type == 'knocker':
                self.color=(0.6,0.35,1.2)
            elif self.juice_type == 'cake':
                self.color=(1.17,0.3,0.59)
            elif self.juice_type == 'ranger':
                self.color=(1.10,0.73,0)
            elif self.juice_type == 'overdrive':
                self.color=(0.3,0,0.55)
            elif self.juice_type == 'healing':
                self.color=(1.3,0.8,1)
            elif self.juice_type == 'palette':
                self.color=(0.65,0.5,0.52)
        elif self.palette in ['mictlan']:
            if random.randint(0,1) == 1:
                self.fireImmune = True
                self.color=(0,1,1)
                self.highlight=(1,0,0)
            else:
                self.freezeImmune = True
                self.color=(1,0,0)
                self.highlight=(0.1,0.1,1.5)
        elif self.palette in ['spaz']:
            self.types = ['default','red','blue']
            self.chosen = random.choice(self.types)
            if self.chosen == 'default': self.highlight=gDefaultBotHighlight
            elif self.chosen == 'red': self.highlight=(0.2,0.1,0.1)
            elif self.chosen == 'blue': self.highlight=(0.1,0.1,0.2)
        
        
        Spaz.__init__(self,color=self.color,highlight=self.highlight,character=self.character,
                      sourcePlayer=None,bombShape=self.bombShape,startInvincible=False,canAcceptPowerups=False)

        # if you need to add custom behavior to a bot, set this to a callable which takes one
        # arg (the bot) and returns False if the bot's normal update should be run and True if not
        self.updateCallback = None
        self._map = weakref.ref(bs.getActivity().getMap())

        self.lastPlayerAttackedBy = None # FIXME - should use empty player-refs
        self.lastAttackedTime = 0
        self.lastAttackedType = None
        self.targetPointDefault = None
        self.heldCount = 0
        self.lastPlayerHeldBy = None # FIXME - should use empty player-refs here
        self.targetFlag = None
        self._chargeSpeed = 0.5*(self.chargeSpeedMin+self.chargeSpeedMax)
        self._leadAmount = 0.5
        self._mode = 'wait'
        self._chargeClosingIn = False
        self._lastChargeDist = 0.0
        self._running = False
        self._lastJumpTime = 0
        self.runaroundInPath = False
        self._punchCooldown = gBasePunchCooldown
        self._punchPowerScale = gBasePunchPowerScale
        self.node.invincible = self.defaultInvincibility
        self.isGrabber = self.isGrabber
        self.blastType2 = self.bombType
        self.node.name = self.defaultName
        self.timeNow = bs.checkTime(useInternet=False)
        if self.timeNow['hour'] in [6, 18, 12, 24]:
            self.x = 350
        else:
            self.x = 500
        self.value = random.randint(1,self.x)
        if self.value == 1:
           self._neon = bs.Timer(10,bs.WeakCall(self._Neon),repeat=False)
           self.node.name = 'Shiny'
           self.pointsMult = self.pointsMult+2
           bs.statAdd('Shiny Bots Seen')
        
        # these cooldowns didnt exist when these bots were calibrated, so take them out of the equation
        self._jumpCooldown = 0
        self._pickupCooldown = 0 #350
        self._flyCooldown = 0
        self._bombCooldown = 0

        if self.startCursed: self.curse()
        if self.defaultBlastBuff: self.blastRadiusBuffed = True

    def _Neon(self):
        colors = {0: (2, 0, 0),500: (2, 2, 0),1000: (0, 2, 0),1500: (0, 2, 2),2000: (2, 0, 2),2500: (0, 0, 2),3000: (2, 2, 2,),3500: (1, 0, 0),4000: (1, 0, 0),4500: (1, 1, 0),5000: (0, 1, 0),5500: (0, 1, 1),6000: (1, 0, 1),6500: (0, 0, 1),7000: (1, 0, 0),7500: (0, 0, 0)}
        highlights = {0: (0, 0, 0),500: (1, 0, 0),1000: (0, 0, 1),1500: (1, 0, 1),2000: (0, 1, 1),2500: (0, 1, 0),3000: (1, 1, 0,),3500: (1, 0, 0),4000: (1, 0, 0),4500: (2, 2, 2),5000: (0, 0, 2),5500: (2, 0, 2),6000: (0, 2, 2),6500: (0, 2, 0),7000: (2, 2, 0),7500: (2, 0, 0)}
        bsUtils.animateArray(self.node, 'color', 3, colors, True)
        bsUtils.animateArray(self.node, 'nameColor', 3, colors, True)
        bsUtils.animateArray(self.node, 'highlight', 3, highlights, True)
    
    def _getTargetPlayerPt(self):
        """ returns the default player pt we're targeting """
        bp = bs.Vector(*self.node.position)
        closestLen = None
        closestVel = None
        for pp,pv in self._playerPts:

            l = (pp-bp).length()
            # ignore player-points that are significantly below the bot
            # (keeps bots from following players off cliffs)
            if (closestLen is None or l < closestLen) and (pp[1] > bp[1] - 5.0):
                closestLen = l
                closestVel = pv
                closest = pp
        if closestLen is not None:
            return (bs.Vector(closest[0],closest[1],closest[2]),
                    bs.Vector(closestVel[0],closestVel[1],closestVel[2]))
        else:
            return None,None

    def _setPlayerPts(self,pts):
        """
        Provide the spaz-bot with the locations of players.
        """
        self._playerPts = pts

    def _updateAI(self):
        """
        Should be called periodically to update the spaz' AI
        """
        if self.updateCallback is not None:
            if self.updateCallback(self) == True:
                return # true means bot has been handled

        t = self.node.position
        ourPos = bs.Vector(t[0],0,t[2])
        canAttack = True

        # if we're a flag-bearer, we're pretty simple-minded - just walk towards the flag and try to pick it up
        if self.targetFlag is not None:

            if not self.targetFlag.node.exists():
                # our flag musta died :-C
                self.targetFlag = None
                return
            if self.node.holdNode.exists():
                try: holdingFlag = (self.node.holdNode.getNodeType() == 'flag')
                except Exception: holdingFlag = False
            else: holdingFlag = False
            # if we're holding the flag, just walk left
            if holdingFlag:
                # just walk left
                self.node.moveLeftRight = -0.5 if self.dizzy else -1.0
                self.node.moveUpDown = 0.0
            # otherwise try to go pick it up
            else:
                targetPtRaw = bs.Vector(*self.targetFlag.node.position)
                targetVel = bs.Vector(0,0,0)
                diff = (targetPtRaw-ourPos)
                diff = bs.Vector(diff[0],0,diff[2]) # dont care about y
                dist = diff.length()
                toTarget = diff.normal()*-1 if self.dizzy else diff.normal()

                # if we're holding some non-flag item, drop it
                if self.node.holdNode.exists():
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
                    return

                # if we're a runner, run only when not super-near the flag
                if self.run and dist > 3.0:
                    self._running = True
                    self.node.run = 1.0
                else:
                    self._running = False
                    self.node.run = 0.0

                self.node.moveLeftRight = toTarget.x()
                self.node.moveUpDown = -toTarget.z()
                if dist < 1.25:
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
            return
        # not a flag-bearer.. if we're holding anything but a bomb, drop it
        else:
            if self.node.holdNode.exists():
                try: holdingBomb = (self.node.holdNode.getNodeType() in ['bomb','prop'])
                except Exception: holdingBomb = False
                if not holdingBomb:
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
                    return
            
        targetPtRaw,targetVel = self._getTargetPlayerPt()

        if targetPtRaw is None:
            # use default target if we've got one
            if self.targetPointDefault is not None:
                targetPtRaw = self.targetPointDefault
                targetVel = bs.Vector(0,0,0)
                canAttack = False
            # with no target, we stop moving and drop whatever we're holding
            else:
                self.node.moveLeftRight = 0
                self.node.moveUpDown = 0
                if self.node.holdNode.exists():
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
                return

        # we dont want height to come into play
        targetPtRaw.data[1] = 0
        targetVel.data[1] = 0

        distRaw = (targetPtRaw-ourPos).length()
        # use a point out in front of them as real target (more out in front the farther from us they are)
        targetPt = targetPtRaw + targetVel*distRaw*0.3*self._leadAmount

        diff = (targetPt-ourPos)
        dist = diff.length()
        toTarget = diff.normal()*-1 if self.dizzy else diff.normal()

        if self._mode == 'throw':
            # we can only throw if alive and well..
            if not self._dead and not self.node.knockout:

                timeTillThrow = self._throwReleaseTime-bs.getGameTime()

                if not self.node.holdNode.exists():
                    # if we havnt thrown yet, whip out the bomb
                    if not self._haveDroppedThrowBomb:
                        self.dropBomb()
                        self._haveDroppedThrowBomb = True
                    # otherwise our lack of held node means we successfully released our bomb.. lets retreat now
                    else:
                        self._mode = 'flee'

                # oh crap we're holding a bomb.. better throw it.
                elif timeTillThrow <= 0:
                    # jump and throw..
                    def _safePickup(node):
                        if node.exists():
                            self.node.pickUpPressed = True
                            self.node.pickUpPressed = False
                    if dist > 5.0:
                        self.node.jumpPressed = True
                        self.node.jumpPressed = False
                        bs.gameTimer(100,bs.Call(_safePickup,self.node)) # throws
                    else:
                        bs.gameTimer(1,bs.Call(_safePickup,self.node)) # throws

                if self.static:
                    if timeTillThrow < 300: speed = 1.0
                    elif timeTillThrow < 700 and dist > 3.0: speed = -1.0 # whiplash for long throws
                    else: speed = 0.02
                else:
                    if timeTillThrow < 700:
                        # right before throw charge full speed towards target
                        speed = 1.0
                    else:
                        # earlier we can hold or move backward for a whiplash
                        speed = 0.0125
                self.node.moveLeftRight = toTarget.x() * speed
                self.node.moveUpDown = toTarget.z() * -1.0 * speed

        elif self._mode == 'charge':
            if random.random() < 0.3:
                self._chargeSpeed = random.uniform(self.chargeSpeedMin,self.chargeSpeedMax)

                # if we're a runner we run during charges *except when near an edge (otherwise we tend to fly off easily)
                if self.run and distRaw > self.runDistMin:
                    self._leadAmount = 0.3
                    self._running = True
                    self.node.run = 1.0
                else:
                    self._leadAmont = 0.01
                    self._running = False
                    self.node.run = 0.0

            self.node.moveLeftRight = toTarget.x() * self._chargeSpeed
            self.node.moveUpDown = toTarget.z() * -1.0*self._chargeSpeed

        elif self._mode == 'wait':
            # every now and then, aim towards our target.. other than that, just stand there
            if bs.getGameTime()%1234 < 100:
                self.node.moveLeftRight = toTarget.x() * (400.0/33000)
                self.node.moveUpDown = toTarget.z() * (-400.0/33000)
            else:
                self.node.moveLeftRight = 0
                self.node.moveUpDown = 0

        elif self._mode == 'flee':
            # even if we're a runner, only run till we get away from our target (if we keep running we tend to run off edges)
            if self.run and dist < 2.0:
                self._running = True
                self.node.run = 1.0
            else:
                self._running = False
                self.node.run = 0.0
            self.node.moveLeftRight = toTarget.x() * -1.0
            self.node.moveUpDown = toTarget.z()

        # we might wanna switch states unless we're doing a throw (in which case thats our sole concern)
        if self._mode != 'throw':

            # if we're currently charging, keep track of how far we are from our target..
            # when this value increases it means our charge is over (ran by them or something)
            if self._mode == 'charge':
                if self._chargeClosingIn and dist < 3.0 and dist > self._lastChargeDist:
                    self._chargeClosingIn = False
                self._lastChargeDist = dist

            # if we have a clean shot, throw!
            if dist >= self.throwDistMin and dist < self.throwDistMax and random.random() < self.throwiness and canAttack:
                self._mode = 'throw'
                self._leadAmount = (0.4+random.random()*0.6) if distRaw > 4.0 else (0.1+random.random()*0.4)
                self._haveDroppedThrowBomb = False
                self._throwReleaseTime = bs.getGameTime() + (1.0/self.throwRate)*(800 + int(1300*random.random()))

            # if we're static, always charge (which for us means barely move)
            elif self.static:
                self._mode = 'wait'
                
            # if we're too close to charge (and arent in the middle of an existing charge) run away
            elif dist < self.chargeDistMin and not self._chargeClosingIn:
                # ..unless we're near an edge, in which case we got no choice but to charge..
                if self._map()._isPointNearEdge(ourPos,self._running):
                    if self._mode != 'charge':
                        self._mode = 'charge'
                        self._leadAmount = 0.2
                        self._chargeClosingIn = True
                        self._lastChargeDist = dist
                else:
                    self._mode = 'flee'

            # we're within charging distance, backed against an edge, or farther than our max throw distance.. chaaarge!
            elif dist < self.chargeDistMax or dist > self.throwDistMax or self._map()._isPointNearEdge(ourPos,self._running):
                if self._mode != 'charge':
                    self._mode = 'charge'
                    self._leadAmount = 0.01
                    self._chargeClosingIn = True
                    self._lastChargeDist = dist

            # we're too close to throw but too far to charge - either run away or just chill if we're near an edge
            elif dist < self.throwDistMin:
                # charge if either we're within charge range or cant retreat to throw
                self._mode = 'flee'

            # do some awesome jumps if we're running
            if ((self._running and dist > 1.2 and dist < 2.2 and bs.getGameTime()-self._lastJumpTime > 1000)
                or (self.bouncy and bs.getGameTime()-self._lastJumpTime > 400 and random.random() < 0.5)):
                self._lastJumpTime = bs.getGameTime()
                self.node.jumpPressed = True
                self.node.jumpPressed = False

                
            # throw punches when real close (or tackle)
            if dist < (1.6 if self._running else 1.2) and canAttack:
                if random.random() < self.punchiness:
                    if self.tackle and self._ableToDodge:
                        self.onJumpPress()
                        self.onPunchPress()
                        self.onJumpRelease()
                        self.onPunchRelease()
                    elif self.isGrabber:
                        self.node.pickUpPressed = True
                        self.node.pickUpPressed = False
                    else:
                        self.onPunchPress()
                        self.onPunchRelease()

    def __superHandleMessage(self,m):
        super(SpazBot,self).handleMessage(m)

    def onPunched(self,damage):
        """
        Method override; sends a bs.SpazBotPunchedMessage to the current activity.
        """
        bs.getActivity().handleMessage(SpazBotPunchedMessage(self,damage))

    def onFinalize(self):
        Spaz.onFinalize(self)
        # we're being torn down; release
        # our callback(s) so there's no chance of them
        # keeping activities or other things alive..
        self.updateCallback = None

        
    def handleMessage(self,m):
        self._handleMessageSanityCheck()

        # keep track of if we're being held and by who most recently
        if isinstance(m,bs.PickedUpMessage):
            self.__superHandleMessage(m) # augment standard behavior
            self.heldCount += 1
            pickedUpBy = m.node.sourcePlayer
            if pickedUpBy is not None and pickedUpBy.exists():
                self.lastPlayerHeldBy = pickedUpBy

        elif isinstance(m,bs.DroppedMessage):
            self.__superHandleMessage(m) # augment standard behavior
            self.heldCount -= 1
            if self.heldCount < 0:
                print "ERROR: spaz heldCount < 0"
            # let's count someone dropping us as an attack..
            try:
                if m.node.exists(): pickedUpBy = m.node.sourcePlayer
                else: pickedUpBy = bs.Player(None) # empty player ref
            except Exception,e:
                print 'EXC on SpazBot DroppedMessage:',e
                pickedUpBy = bs.Player(None) # empty player ref

            if pickedUpBy.exists():
                self.lastPlayerAttackedBy = pickedUpBy
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = ('pickedUp','default')
            
        elif isinstance(m,bs.DieMessage):
        
            # report normal deaths for scoring purposes
            if not self._dead and not m.immediate:

                # if this guy was being held at the time of death, the holder is the killer
                if self.heldCount > 0 and self.lastPlayerHeldBy is not None and self.lastPlayerHeldBy.exists():
                    killerPlayer = self.lastPlayerHeldBy
                else:
                    # otherwise if they were attacked by someone in the last few seconds
                    # that person's the killer.. otherwise it was a suicide
                    if self.lastPlayerAttackedBy is not None and self.lastPlayerAttackedBy.exists() and bs.getGameTime() - self.lastAttackedTime < 4000:
                        killerPlayer = self.lastPlayerAttackedBy
                    else:
                        killerPlayer = None
                activity = self._activity()

                if killerPlayer is not None and not killerPlayer.exists(): killerPlayer = None
                if activity is not None: 
                    if killerPlayer is not None: bs.statAdd('Bot Kills')
                    activity.handleMessage(SpazBotDeathMessage(self,killerPlayer,m.how))
            self.__superHandleMessage(m) # augment standard behavior

        # keep track of the player who last hit us for point rewarding
        elif isinstance(m,bs.HitMessage):
            if m.sourcePlayer is not None and m.sourcePlayer.exists():
                self.lastPlayerAttackedBy = m.sourcePlayer
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = (m.hitType,m.hitSubType)
            self.__superHandleMessage(m)
        else:
            Spaz.handleMessage(self,m)
                        
class BunnyBot(SpazBot):
    """
    category: Bot Classes
    
    A speedy attacking melee bot.
    """

    palette = None
    color=(1,1,1)
    highlight=(1.0,0.5,0.5)
    character = 'Easter Bunny'
    punchiness = 0.95
    run = True
    bouncy = True
    defaultBoxingGloves = True
    defaultBombCount = 0
    chargeDistMin = 10.0
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    pointsMult = 2

class BunnyBotShielded(BunnyBot):
    """
    category: Bot Classes
    
    A speedy attacking melee bot
    with shield.
    """
    palette = None
    color=(1,0.7,1)
    highlight=(1.0,0.15,0.15)
    character = 'Easter Bunny'
    defaultShields = True
    pointsMult = 3

class BomberBot(SpazBot):
    """
    category: Bot Classes
    
    A bot that throws regular bombs
    and occasionally punches.
    """
    bombShape = 'Regular'
    color=(0.3, 0.6, 1.3)
    highlight=(0.05, 0.3, 0.7)
    character='Spaz'
    punchiness=0.3
    
class WizardBot(BomberBot):
    """
    category: Bot Classes
    
    A bot that throws knocker bombs.
    """
    palette = 'wizard'
    color=(0.66,0.30,1.15)
    highlight= (0.06,0.15,0.4)
    throwRate = 0.85
    defaultBombType = 'knocker'
    
class WizardBotPro(WizardBot):
    """
    category: Bot Classes
    
    A wizard with shield.
    """
    palette = 'wizard_pro'
    color=gProBotColor
    highlight=gProBotHighlight
    defaultBoxingGloves = True
    pointsMult = 4
    throwRate = 1.007
    
class WizardBotStatic(WizardBot):
    """
    category: Bot Classes
    
    A bot that throws knocker bombs and stays.
    """
    static = True
    throwRate = 1.3
    throwDistMin = 0.0
    throwDistMax = 14.0

class BomberBotLame(BomberBot):
    """
    category: Bot Classes
    
    A less aggressive yellow version of bs.BomberBot.
    """
    color=gLameBotColor
    highlight=gLameBotHighlight
    palette = None
    punchiness = 0.2
    throwRate = 0.7
    throwiness = 0.1
    chargeSpeedMin = 0.6
    chargeSpeedMax = 0.6

class BomberBotStaticLame(BomberBotLame):
    """
    category: Bot Classes
    
    A less aggressive yellow version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0

class BomberBotStatic(BomberBot):
    """
    category: Bot Classes
    
    A version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0


class BomberBotPro(BomberBot):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot.
    """
    pointsMult = 2
    color=gProBotColor
    highlight=gProBotHighlight
    defaultBombCount = 3
    defaultBoxingGloves = True
    punchiness = 0.7
    throwRate = 1.3
    run = True
    runDistMin = 6.0

class BomberBotProShielded(BomberBotPro):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot
    who starts with shields.
    """
    pointsMult = 3
    defaultShields = True

class BomberBotProStatic(BomberBotPro):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0

class BomberBotProStaticShielded(BomberBotProShielded):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot
    who starts with shields and
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0

class ToughGuyBot(SpazBot):
    """
    category: Bot Classes
    
    A manly bot who walks and punches things.
    """
    character = 'Kronk'
    color=(0.4, 0.5, 0.4)
    palette = 'spaz'
    punchiness = 0.9
    defaultBombCount = 0
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    
class ToughGuyBotLame(ToughGuyBot):
    """
    category: Bot Classes
    
    A less aggressive yellow version of bs.ToughGuyBot.
    """
    color=gLameBotColor
    highlight=gLameBotHighlight
    punchiness = 0.3
    chargeSpeedMin = 0.6
    chargeSpeedMax = 0.6
    
class BonesBot(ToughGuyBotLame):
    """
    category: Bot Classes
    
    A very resistant bot that slowly moves towards the player and hits hard with his Boxing Gloves.
    """ 
    character = 'Bones'
    color=(0.6,0.9,1)
    highlight=(0.6,0.9,1)
    hitPoints = 1750
    impactScale = 0.68
    defaultBoxingGloves = True
    
class BonesBotPro(BonesBot):
    """
    category: Bot Classes
    
    A very hard resistant bot that speedily moves towards the player and hits hard with his Boxing Gloves.
    """ 
    character = 'Bones'
    color=gProBotColor
    highlight=gProBotHighlight
    impactScale = 0.55
    hitPoints = 1750
    chargeSpeedMin = 0.71
    chargeSpeedMax = 0.71

class ToughGuyBotPro(ToughGuyBot):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.ToughGuyBot.
    """
    color=gProBotColor
    highlight=gProBotHighlight
    run = True
    runDistMin = 4.0
    defaultBoxingGloves = True
    punchiness = 0.95
    pointsMult = 2

class ToughGuyBotProShielded(ToughGuyBotPro):
    """
    category: Bot Classes
    
    A more aggressive version of bs.ToughGuyBot
    who starts with shields.
    """
    defaultShields = True
    pointsMult = 3

class NinjaBot(SpazBot):
    """
    category: Bot Classes
    
    A speedy attacking melee bot.
    """
    character = 'Snake Shadow'
    color=(1.0,1.0,1.0)
    highlight=(0.55,0.8,0.55)
    palette = None
    run = True
    punchiness = 1.0
    chargeDistMin = 10.0
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    defaultBombCount = 0
    throwDistMin = 9999
    throwDistMax = 9999
    pointsMult = 2
    
class NinjaBotLame(NinjaBot):
    """
    category: Bot Classes
    
    A less aggressive yellow version
    of bs.NinjaBot.
    """
    color=gLameBotColor
    highlight=gLameBotHighlight
    punchiness = 0.5
    chargeSpeedMax = 2.6
    chargeSpeedMin = 2.0
    runDistMax = 1.2
    palette = None
    
class NinjaBotPro(NinjaBot):
    """
    category: Bot Classes
    
    A more aggressive red bs.NinjaBot.
    """
    color=gProBotColor
    highlight=gProBotHighlight
    palette = None
    defaultShields = False
    defaultBoxingGloves = True
    pointsMult = 3

class NinjaBotProShielded(NinjaBotPro):
    """
    category: Bot Classes
    
    A more aggressive red bs.NinjaBot
    who starts with shields.
    """
    defaultShields = True
    pointsMult = 4
    
class KnightBot(SpazBot):
    """
    category: Bot Classes
    
    A speedy attacking bot that tackles.
    """
    character = 'Sir Bombalot'
    palette = 'spaz'
    punchiness = 1.0
    hitPoints = 1250
    run = True
    tackle = True
    defaultBombCount = 0
    chargeDistMin = 2.0
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    pointsMult = 2
    
class KnightBotPro(KnightBot):
    """
    category: Bot Classes
    
    A more aggressive red bs.KnightBot.
    """
    color=gProBotColor
    highlight=gProBotHighlight
    palette = None
    defaultShields = False
    defaultBoxingGloves = True
    pointsMult = 3
    
class KnightBotProShielded(KnightBotPro):
    """
    category: Bot Classes
    
    A more aggressive red bs.KnightBot
    who starts with shields.
    """
    defaultShields = True
    pointsMult = 4

class ChickBot(SpazBot):
    """
    category: Bot Classes
    
    A slow moving bot with impact bombs.
    """
    character = 'Zoe'
    palette = 'spaz'
    punchiness = 0.75
    throwiness = 0.7
    chargeDistMax = 1.0
    chargeSpeedMin = 0.3
    chargeSpeedMax = 0.5
    throwDistMin = 3.5
    throwDistMax = 5.5
    defaultBombType = 'impact'
    pointsMult = 2

class ChickBotLame(ChickBot):
    """
    category: Bot Classes
    
    A less aggressive yellow version
    of bs.ChickBot.
    """
    color=gLameBotColor
    highlight=gLameBotHighlight
    palette = None
    punchiness = 0.3
    throwiness = 0.4
    throwDistMax = 4.25

class ChickBotStaticLame(ChickBotLame):
    """
    category: Bot Classes
    
    A less aggressive yellow version
    of bs.ChickBot, that stays in one place.
    """
    static = True

class ChickBotStatic(ChickBot):
    """
    category: Bot Classes
    
    A bs.ChickBot who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0
    throwDistMax = 10.5
    throwRate = 1.7

class ChickBotPro(ChickBot):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.ChickBot.
    """
    palette = None
    color=gProBotColor
    highlight=gProBotHighlight
    defaultBombCount = 3
    defaultBoxingGloves = True
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    punchiness = 0.9
    throwRate = 1.3
    run = True
    runDistMin = 6.0
    pointsMult = 3

class ChickBotProShielded(ChickBotPro):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.ChickBot
    who starts with shields.
    """
    defaultShields = True
    pointsMult = 4

class MelBot(SpazBot):
    """
    category: Bot Classes
    
    A crazy bot who runs and throws sticky bombs.
    """
    character = 'Mel'
    palette = 'spaz'
    punchiness = 0.9
    throwiness = 1.0
    run = True
    chargeDistMin = 4.0
    chargeDistMax = 10.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 0.0
    throwDistMax = 4.0
    throwRate = 2.0
    bombShape = 'Bumpy'
    defaultBombType = 'sticky'
    defaultBombCount = 3
    pointsMult = 3

class MelBotLame(MelBot):
    """
    category: Bot Classes
    
    A less crazy yellow version,
    of bs.MelBot.
    """
    palette = None
    color=gLameBotColor
    throwDistMax = 6.0
    throwDistMin = 4.0
    punchiness = 0.31
    throwiness = 0.6
    chargeSpeedMax = 2.5
    highlight=gLameBotHighlight
    pointsMult = 2

class MelBotStaticLame(MelBotLame):
    """
    category: Bot Classes
    
    A less crazy yellow version,
    of bs.MelBot that stays in one place.
    """
    static = True

class MelBotStatic(MelBot):
    """
    category: Bot Classes
    
    A crazy bot who throws sticky-bombs but generally stays in one place.
    """
    static = True
    throwDistMin = 0.0
    throwDistMax = 10.0
    
class MelDuperBot(MelBot):
    """
    A crazy bot who runs and throws sticky bombs.
    He has a shield and doesn't like you as a person
    and will do everything to make you puke and give
    you headaches.
    """
    palette = None
    color=gProBotColor
    highlight=gProBotHighlight
    defaultShields = True
    defaultBoxingGloves = True
    throwRate = 3.0
    defaultBombCount = 5
    pointsMult = 4

class PirateBot(SpazBot):
    """
    category: Bot Classes
    
    A bot who runs and explodes in 8 seconds.
    """
    palette = 'spaz'
    color = (1.0,0.15,0.15)
    character = 'Jack Morgan'
    run = True
    defaultBombCount = 0
    chargeDistMin = 0.0
    chargeDistMax = 9999
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    curseTime = 8000
    startCursed = True
    pointsMult = 3

class PirateBotNoTimeLimit(PirateBot):
    """
    category: Bot Classes
    
    A bot who runs but does not explode on his own.
    """
    curseTime = -1

class PirateBotShielded(PirateBot):
    """
    category: Bot Classes
    
    A bs.PirateBot who starts with shields.
    """
    defaultShields = True
    pointsMult = 5
    
class PirateBotRadius(PirateBot):
    """
    category: Bot Classes
    
    A bot who runs and can explode on its own when close enough.
    """
    palette = None
    color=(1,0.3,0.5)
    defaultBombType = 'hijump'
    defaultBombCount = 1
    defaultBlastRadius = 3.0
    throwDistMin = 0
    throwDistMax = 3.0
    curseTime = -1
    
class TNTBot(PirateBot):
    """
    category: Bot Classes
    
    A bot who runs and explodes in 20 seconds.
    """
    character = 'Exploder'
    palette = None
    color=(1,1,1)
    highlight=(1,1,1)
    defaultBlastRadius = 10.0
    defaultInvincibility = True
    pointsMult = 5
    curseTime = 20000
    
class AliBot(PirateBot):
    """
    category: Bot Classes
    
    A bot that runs extremely fast and will not stop until he gets you. 
    """
    character='Taobao Mascot'
    startCursed=False
    defaultSpeedBoots = True
    punchiness = 0.025
    hitPoints = 1000
    pointsMult = 3
    
class AliBotPro(AliBot):
    """
    category: Bot Classes
    
    A bot that runs extremely fast and will not stop until he gets you.
    Ow and he's tankier too
    """
    color=(0.2,0.2,1)
    palette = None
    highlight=(1,0,0)
    punchiness = 0.075
    pointsMult = 3


class FrostyBot(SpazBot):
    """
    category: Bot Classes
    
    A bot that throws ice bombs
    and occasionally punches.
    """
    character='Frosty'
    punchiness=0.3
    color=(0.5,0.5,1)
    highlight=(1,0.5,0)
    defaultBombType = 'ice'
    pointsMult = 4

class FrostyBotStatic(FrostyBot):
    """
    category: Bot Classes
    
    A bot that throws ice bombs
    and stays in one place most of the time.
    """
    static = True
    throwDistMin = 0.0

class FrostyBotShielded(FrostyBot):
    """
    category: Bot Classes
    
    A crazed maniac. This time with shields!
    """
    color=(0.2,0.2,1)
    highlight=(1,0,0)
    defaultShields = True
    pointsMult = 5
    
class FrostyBotPro(FrostyBot):
    """
    category: Bot Classes
    
    A crazed maniac. This time with gloves!
    """
    color=(0.2,0.2,1)
    highlight=(1,0,0)
    run = True
    runDistMax = 3.6
    runDistMin = 1.3
    chargeDistMax = 4.1
    chargeDistMin = 1.3
    throwDistMin = 1.5
    throwDistMax = 3.0
    punchiness = 0.55
    chargeSpeedMax = 2.68
    defaultBoxingGloves = True
    pointsMult = 4

class AgentBot(MelBot):
    """
    category: Bot Classes
    
    A crazy bot who runs and throws impact bombs.
    """
    character = 'Agent Johnson'
    color=(0.1,0.1,0.1)
    throwRate = 3
    defaultBombType = 'impact'
    pointsMult = 2

class AgentBotPro(AgentBot):
    """
    category: Bot Classes
    
    Agent Bot with gloves
    """
    color=(1,0.1,0.1)
    highlight=(0.3,0.1,0.1)
    defaultBoxingGloves = True
    pointsMult = 3

class AgentBotShielded(AgentBot):
    """
    category: Bot Classes
    
    Agent Bot with armor
    """
    color=(1,0.1,0.1)
    highlight=(0.3,0.1,0.1)
    defaultShields = True
    pointsMult = 3

class CyborgBot(SpazBot):
    """
    category: Bot Classes
    
    A slow moving bot with combat bombs.
    """
    palette = None
    character = 'B-9000'
    highlight=(0,1,1)
    punchiness = 1.0
    throwiness = 1.0
    chargeDistMax = 1.0
    chargeSpeedMin = 0.3
    chargeSpeedMax = 0.5
    throwRate = 1.5
    throwDistMin = 4.5
    throwDistMax = 6.5
    defaultBombType = 'combat'
    pointsMult = 2

class CyborgBotPro(CyborgBot):
    """
    category: Bot Classes
    
    A more aggressive moving bot with combat bombs.
    """
    character = 'B-9000'
    highlight=(1.0,0.1,0.1)
    chargeDistMax = 1.0
    chargeSpeedMin = 0.5
    chargeSpeedMax = 0.8
    throwRate = 1.7
    throwDistMin = 5.0
    throwDistMax = 7.0
    defaultShields = True
    pointsMult = 4
    
class CyborgBotStatic(CyborgBot):
    """
    category: Bot Classes
    
    A bot with combat bombs and stay in place.
    """
    throwDistMin = 0.0
    throwRate = 1.33
    static = True
    
class SpyBot(SpazBot):
    """
    category: Bot Classes
    
    A slow moving bot that ocasionally throws land mines.
    """
    palette = 'spy'
    character = 'Spy'
    punchiness = 0.5
    throwiness = 1.0
    throwRate = 1.5
    chargeDistMax = 4
    throwRate = 1.5
    chargeSpeedMin = 1
    chargeSpeedMax = 1
    throwDistMin = 3
    throwDistMax = 9999
    defaultBombCount = 5
    defaultBombType = 'landMine'
    pointsMult = 2
    
class LooieBot(SpazBot):
    """
    category: Bot Classes
    
    A crazed maniac (probably on drugs) that jumps everywhere, throws bombs everywhere and will punch you hard if you're not careful.
    """
    palette = None
    color=(1,0.7,0.0)
    highlight=(1,1,1)
    character = 'Looie'
    punchiness = 0.8
    throwiness = 1.0
    run = True
    bouncy = True
    chargeDistMin = 10.0
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 2
    throwDistMax = 9999
    pointsMult = 4
    bombShape = 'Regular'
    throwRate = 10.0
    defaultBombCount = 6
    
class LooieBotPro(LooieBot):
    """
    category: Bot Classes
    
    A crazed maniac. This time with gloves!
    """
    color=(1,0.0,0.0)
    highlight=(1,1,1)
    defaultBoxingGloves = True
    pointsMult = 4
    
class LooieBotShielded(LooieBot):
    """
    category: Bot Classes
    
    A crazed maniac. This time with shields!
    """
    color=(1,0.0,0.0)
    highlight=(1,1,1)
    defaultShields = True
    pointsMult = 4
    
class PascalBot(LooieBot):
    """
    category: Bot Classes
    
    A jumpy bot who throws ice bombs everywhere.
    """
    palette = 'spaz'
    color=(0.3,0.5,0.8)
    defaultBombType = 'ice'
    character = 'Pascal'
    pointMult = 3
    
class PascalBotShielded(PascalBot):
    """
    category: Bot Classes
    
    A freezer with shields.
    """
    palette = None
    color=gProBotColor
    highlight=gProBotHighlight
    defaultShields = True
    pointMult = 4
    
class ZillBot(CyborgBot):
    """
    category: Bot Classes
    
    A bot that chaos the battle.
    """
    character = 'Zill'
    palette = None
    defaultBombType = 'fraction'
    defaultBombCount = 3
    chargeSpeedMax = 5.75
    chargeDistMax = 3.5
    chargeDistMin = 1.75
    throwRate = 0.76
    color=(0,0,0.3)
    highlight=(0.9,0.95,1)
    pointsMult = 2
    
class ZillBotPro(ZillBot):
    """
    category: Bot Classes
    
    A armored bot that throws chasing bombs.
    """
    palette = None
    defaultBoxingGloves = True
    color=(1.0,0.6,0.7)
    highlight=(1.0,0.35,0.35)
    pointsMult = 2
    
class SpyBotStatic(SpyBot):
    """
    category: Bot Classes
    
    A bot that throws landmines and stays in one place.
    """
    palette = None
    static = True
    throwDistMin = 0.0
    throwDistMax = 6.0
    pointsMult = 2
    
class SpyBotPro(SpyBot):
    """
    category: Bot Classes
    
    A spy with shield.
    """
    palette = None
    defaultShields = True
    color=gProBotColor
    highlight=(1,1,1)
    pointsMult = 2
    
class SantaBot(SpazBot):
    """
    category: Bot Classes
    
    A santa bot that ataks with snowballs.
    """
    palette=None
    character='Santa Claus'
    highlight=(1,1,1)
    color=(1.0,0.0,0.0)
    defaultBombType='snowball'
    freezeImmune=True
    throwDistMin=0.0
    throwDistMax=9999.0
    chargeSpeedMin=0.025
    chargeSpeedMax=0.1
    throwRate=1.5
    punchiness=0.0
    
class DemonBot(ToughGuyBot):
    """
    category: Bot Classes
    
    A frail temperated bot from the depths!
    """
    palette = 'mictlan'
    color=(0,1,1)
    highlight=(0,0,0)
    character = 'Mictlan'
    punchiness = 0.57
    hitPoints = 795
    run = True
    chargeSpeedMax = 1.05
    
    
    def handleMessage(self,m):
        if isinstance(m, _PunchHitMessage):
            node = bs.getCollisionInfo("opposingNode")
            try:
                if self.color == (0,1,1):
                    node.handleMessage(bs.FreezeMessage())
                    bs.playSound(bs.getSound('freeze'))
                else:
                    node.handleMessage(bs.FireMessage(int(gFireDuration*0.4503)))
            except Exception: print('Cant freeze nor burn')
            super(self.__class__, self).handleMessage(m)
        else: super(self.__class__, self).handleMessage(m)
    
class PixelBot(SpazBot):
    """
    category: Bot Classes
    
    A dashing fairy that christens enemies.
    """
    palette = None
    character = 'Pixel'
    color=(1.0, 0.9, 0.8)
    highlight=(1.3, 0.8, 1.0)
    chargeDistMax = 6.87
    defaultBombType = 'healing'
    defaultBlastRadius = 1.3995
    defaultBombCount = 1
    punchiness = 2.0
    throwRate = 1.5
    runDistMin = 2.0
    runDistMax = 7.5
    throwRate = 1.5
    bouncy = True
    tackle = True
    run = True
    pointsMult = 3
    
class PixelBotPro(PixelBot):
    """
    category: Bot Classes
    
    A fairy bot with pro features.
    """
    palette = None
    color=(0.6,0.25,0.25)
    highlight=(1.2,0.35,0.0)
    defaultBoxingGloves = True
    defaultShields = True
    
class PixelBotStatic(PixelBot):
    """
    category: Bot Classes
    
    A love-death thrower, that stays in one place.
    """
    static = True
    throwDistMin = 0.0
    
class JesterBot(MelBot):
    """
    category: Bot Classes
    
    A jester bot with infatuate bombs.
    """
    character = 'Willy'
    palette = 'spaz'
    color=(0.1,0.1,0.4)
    runDistMin = 4.5
    runDistMax = 5.0
    throwRate = 0.97
    throwiness = 0.68
    chargeDistMax = 3.35
    defaultBlastRadius = 2.2
    defaultBombType = 'infatuate'
    defaultBombCount = 3
    
class ArmoredBot(ToughGuyBot):
    """
    category: Bot Classes
    
    A shielded bot that has high
    defensive armor.
    """
    palette = 'spaz'
    character = 'B.I.T.S'
    run = True
    color=(0.5,0.5,0.5)
    chargeSpeedMax = 5.0
    runDistMin = 2.44
    runDistMax = 4.22
    
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self.armored_stat = bs.Timer(random.randint(100,1500),bs.WeakCall(self._armorSet),repeat=True)
    def _armorSet(self):
        if not self.node.exists():
           self.armored_stat = None
        self.node.invincible = random.choice([True,False])
        if self.node.invincible: self.node.color=(0,0,0)
        if not self.node.invincible: self.node.color=(2,2,2)
    
class RonnieBot(SpazBot):
    """
    category: Bot Classes
    
    A bot that throws fire bombs at you.
    """
    character = 'Ronnie'
    bombShape = 'Bumpy'
    palette = None
    highlight=(1,1,1)
    color=(1,0.5,0.5)
    throwDistMax = 6.7
    throwDistMin = 1.0
    chargeSpeedMax = 1.41
    chargeSpeedMin = 0.29
    defaultBombCount = 3
    defaultBombType = 'fire'
    
class RonnieBotStatic(RonnieBot):
    """
    category: Bot Classes
    
    A stay bot that toss fire bombs
    """
    static = True
    throwDistMin = 0.0
    
    
class KlayBot(SpazBot):
    """
    category: Bot Classes
    
    A normal bot with blasts buff.
    """
    palette = None
    character = 'Klaymen'
    color=(1,0.5,0.0)
    highlight=(1,1,0)
    bombShape = 'Prism'
    defaultBlastBuff = True
    chargeSpeedMax = 2.9
    chargeDistMax = 4.75
    chargeDistMin = 3.6
    runDistMin = 1.78
    pointsMult = 3
   
class KlayBotStatic(KlayBot):
    """
    category: Bot Classes
    
    A static bot who throws strong bombs.
    """
    static = True
    throwDistMin = 0.0
   
class KlayBotPro(KlayBot):
    """
    category: Bot Classes
    
    A normal bot with boxing gloves and blast buffs.
    """
    palette = None
    color=gProBotColor
    highlight=gProBotHighlight
    defaultBoxingGloves = True
    pointsMult = 3
    
class KlayBotProShielded(KlayBotPro):
    """
    category: Bot Classes
    
    A normal bot with gloves and shields.
    """
    defaultShields = True
    
class BearBot(ChickBot):
    """
    category: Bot Classes
    
    A bot that throws radius bombs.
    """
    palette = None
    character = 'Bernard'
    color=(1,0.8,0.5)
    highlight=(0.6,0.5,0.8)
    throwRate = 0.79
    chargeSpeedMin = 3.5
    chargeDistMax = 5.0
    chargeDistMin = 1.0
    defaultBombCount = 3
    defaultBombType = 'radius'
    bombShape = 'Canister'
    pointsMult = 3
    
class BearBotShielded(BearBot):
    """
    category: Bot Classes
    
    A armored bot with area bombs.
    """
    palette = None
    color=(1,0.7,0.8)
    highlight=gProBotHighlight
    defaultShields = True
    pointsMult = 3
    
class PuckBot(ToughGuyBot):
    """
    category: Bot Classes
    
    A resistant bot that grabs
    enemies they see. Is immune to both burning
    and freezing.
    """
    palette = 'spaz'
    character = 'Puck'
    color=(1.1,1.2,1.3)
    punchiness = 10.0
    impactScale = 0.88
    freezeImmune=True
    fireImmune=True
    isGrabber = True
    run = True
    pointsMult = 3
    
class JuiceBot(KnightBot):
    """
    category: Bot Classes
    
    A tackle suicider bot, has random
    explosion types.
    """
    palette = 'juice'
    character = 'Juice-Boy'
    defaultBlastRadius = 6.17
    startCursed = True
    hitPoints = 1000
    
class CowBot(SpazBot):
    """
    category: Bot Classes
    
    A cow bot that throws gloo.
    """
    palette = None
    character = 'Milk'
    color=(1,1,1)
    highlight=(1,0.3,0.5)
    chargeSpeedMax = 1.0
    chargeDistMax = 3.0
    chargeDistMin = 0.55
    throwiness = 0.62
    throwRate = 1.4
    punchiness = 1.5
    impactScale = 0.97
    defaultBombType = 'gloo'
    defaultBombCount = 3
    
class CowBotStatic(CowBot):
    """
    category: Bot Classes
    
    A bot that throws sticky objects.
    """
    static = True
    throwDistMin = 0.0
    throwDistMax = 3.8
    throwRate = 0.65
    
class CowBotShielded(CowBot):
    """
    category: Bot Classes
    
    A bot that throws sticky glues (shielded).
    """
    palette = None
    character = 'Milk'
    color=(1,1,1)
    highlight=(1,0,0)
    defaultShields = True
    
class SoldierBot(NinjaBot):
    """
    category: Bot Classes
    
    A fast bot who booms.
    """
    palette = None
    character = 'AVGN'
    color=(0.4,0.2,0.1)
    runDistMin = 1.2
    runDistMax = 3.4
    character = 'AVGN'
    defaultBombType = 'instant'
    defaultBlastRadius = 2.4
    defaultBombCount = 1
    throwDistMin = 0
    throwDistMax = 3.0
    run = True
    pointsMult = 2
    
class DiceBot(ChickBot):
    """
    category: Bot Classes
    
    A fast bot who throws impacts.
    """
    palette = None
    character = 'Lucy Chance'
    color=(0.8,0,1.0)
    highlight=(0,0,0)
    randomBomb = True
    chargeDistMax = 4.7
    chargeDistMin = 1.0
    chargeSpeedMax = 3.0
    chargeSpeedMin = 1.0
    runDistMax = 2.1
    throwDistMax = 3.0
    throwDistMin = 0.7
    
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self.bset = bs.Timer(150,bs.WeakCall(self._setbomb),repeat=True)
    def _setbomb(self):
        if not self.node.exists():
            self.bset = None
        self.bombShape = random.choice(["Regular","Bumpy","Pinecone","Ring","Canister","Unusual","Sci-Fi","Prism","Drawing"])
        self.bombType = random.choice(['normal','normal','grenade','normal','normal','normal','ice','fire','fire','normal','impact','normal','ranger','combat','knocker','normal','normal'])
    
class BotSet(object):
    """
    category: Bot Classes
    
    A container/controller for one or more bs.SpazBots.
    """
    def __init__(self):
        """
        Create a bot-set.
        """
        # we spread our bots out over a few lists so we can update them in a staggered fashion
        self._botListCount = 5
        self._botAddList = 0
        self._botUpdateList = 0
        self._botLists = [[] for i in range(self._botListCount)]
        self._spawnSound = bs.getSound('spawn')
        self._spawningCount = 0
        self.startMoving()

    def __del__(self):
        self.clear()

    def spawnBot(self,botType,pos,spawnTime=3000,onSpawnCall=None):
        bsUtils.Spawner(pt=pos,
                        spawnTime=spawnTime,
                        sendSpawnMessage=False,
                        spawnCallback=bs.Call(self._spawnBot,botType,pos,onSpawnCall))
        self._spawningCount += 1

    def _spawnBot(self,botType,pos,onSpawnCall):
        spaz = botType()
        bs.playSound(self._spawnSound,position=pos)
        spaz.node.handleMessage("flash")
        spaz.node.isAreaOfInterest = 0
        spaz.handleMessage(bs.StandMessage(pos,random.uniform(0,360)))
        self.addBot(spaz)
        self._spawningCount -= 1
        if onSpawnCall is not None: onSpawnCall(spaz)
        
    def haveLivingBots(self):
        """
        Returns whether any bots in the set are alive or in the process of spawning.
        """
        haveLiving = any((any((not a._dead for a in l)) for l in self._botLists))
        haveSpawning = True if self._spawningCount > 0 else False
        return (haveLiving or haveSpawning)


    def getLivingBots(self):
        """
        Returns the living bots in the set.
        """
        bots = []
        for l in self._botLists:
            for b in l:
                if not b._dead: bots.append(b)
        return bots

    def _update(self): 
        try:
            botList = self._botLists[self._botUpdateList] = [b for b in self._botLists[self._botUpdateList] if b.exists()]
        except Exception:
            bs.printException("error updating bot list: "+str(self._botLists[self._botUpdateList]))
        self._botUpdateList = (self._botUpdateList+1)%self._botListCount

        # update our list of player points for the bots to use
        playerPts = []
        # Make our bots attack Buddy Bots.
        import BuddyBunny
        try:
            for n in bs.getNodes():
                if n.getNodeType() == 'spaz':
                    s = n.getDelegate()
                    if isinstance(s, BuddyBunny.BunnyBuddyBot):
                        if not s in self.getLivingBots():
                        #if s.isAlive():
                            playerPts.append((bs.Vector(*n.position), bs.Vector(*n.velocity)))

        except Exception:
            bs.printException('error on bot-set _update')
            
        for player in bs.getActivity().players:
            try:
                if player.isAlive():
                    playerPts.append((bs.Vector(*player.actor.node.position),
                                     bs.Vector(*player.actor.node.velocity)))
            except Exception:
                bs.printException('error on bot-set _update')

        for b in botList:
            b._setPlayerPts(playerPts)
            b._updateAI()

    def clear(self):
        """
        Immediately clear out any bots in the set.
        """
        # dont do this if the activity is shutting down or dead
        activity = bs.getActivity(exceptionOnNone=False)
        if activity is None or activity.isFinalized(): return
        
        for i in range(len(self._botLists)):
            for b in self._botLists[i]:
                b.handleMessage(bs.DieMessage(immediate=True))
            self._botLists[i] = []
        
    def celebrate(self,duration):
        """
        Tell all living bots in the set to celebrate momentarily
        while continuing onward with their evil bot activities.
        """
        for l in self._botLists:
            for b in l:
                if b.node.exists():
                    b.node.handleMessage('celebrate',duration)

    def startMoving(self):
        self._botUpdateTimer = bs.Timer(50,bs.WeakCall(self._update),repeat=True)
                    
    def stopMoving(self):
        """
        Tell all bots to stop moving and stops
        updating their AI.
        Useful when players have won and you want the
        enemy bots to just stand and look bewildered.
        """
        self._botUpdateTimer = None
        for l in self._botLists:
            for b in l:
                if b.node.exists():
                    b.node.moveLeftRight = 0
                    b.node.moveUpDown = 0
        
    def finalCelebrate(self):
        """
        Tell all bots in the set to stop what they were doing
        and just jump around and celebrate.  Use this when
        the bots have won a game.
        """
        self._botUpdateTimer = None
        # at this point stop doing anything but jumping and celebrating
        for l in self._botLists:
            for b in l:
                if b.node.exists():
                    b.node.moveLeftRight = 0
                    b.node.moveUpDown = 0
                    bs.gameTimer(random.randrange(0,750),bs.Call(b.node.handleMessage,'celebrate',10000))
                    taunt = random.choice(['default','default','wave','wave','jumpSpin','rotate','dash','idle','crazy'])
                    if taunt == 'default':
                        jumpDuration = random.randrange(300,400)
                        j = random.randrange(0,200)
                        for i in range(10):
                            def _jump():
                                if b.node.exists():
                                    b.node.jumpPressed = True
                                    b.node.jumpPressed = False
                                    b.node.handleMessage('attackSound')
                            j += jumpDuration
                            _jump()
                            bs.gameTimer(j,bs.Call(_jump))
                    if taunt == 'crazy':
                        def _crazy():
                            if b.node.exists():
                                b.node.jumpPressed = True
                                b.onBombPress()
                                b.onJumpPress()
                                b.node.pickUpPressed = True
                                b.onJumpRelease()
                                b.onBombRelease()
                                b.node.punchPressed = False
                                b.node.pickUpPressed = False
                                b.node.handleMessage('attackSound')
                        _crazy()
                        bs.gameTimer(random.randint(100,790),bs.Call(_crazy),repeat=True)
                    elif taunt == 'rotate':
                        turnTime = 300
                        def _stop():
                            if b.node.exists():
                                b.node.moveUpDown = 0.0
                                b.node.moveLeftRight = 0.0
                        b.node.moveUpDown = -1.0
                        b.node.moveLeftRight = 0
                        bs.gameTimer(50,bs.Call(_stop))
                        def _start():
                            for i in range(10):
                                def _down(): 
                                    if b.node.exists():
                                        b.node.moveUpDown = -1.0
                                        b.node.moveLeftRight = 0
                                def _right():
                                    if b.node.exists():
                                        b.node.moveUpDown = 0.0
                                        b.node.moveLeftRight = 1.0
                                def _up():
                                    if b.node.exists():
                                        b.node.moveUpDown = 1.0
                                        b.node.moveLeftRight = 0.0
                                def _left(): 
                                    if b.node.exists():
                                        b.node.moveUpDown = 0.0
                                        b.node.moveLeftRight = -1.0
                                bs.gameTimer(1+i*200,_right)
                                bs.gameTimer(100+i*200,_down)
                                bs.gameTimer(200+i*200,_left)
                                bs.gameTimer(300+i*200,_up)
                        bs.gameTimer(random.randrange(300,1000),bs.Call(_start))
                    elif taunt == 'jumpSpin':
                        turnTime = 300
                        def _stop():
                            if b.node.exists():
                                b.node.moveUpDown = 0.0
                                b.node.moveLeftRight = 0.0
                        b.node.moveUpDown = -1.0
                        b.node.moveLeftRight = 0
                        bs.gameTimer(50,bs.Call(_stop))
                        def _start():
                            def _down():
                                if b.node.exists():
                                    b.node.moveUpDown = -1.0
                                    b.node.moveLeftRight = 0
                            def _right():
                                if b.node.exists():
                                    b.node.moveUpDown = 0.0
                                    b.node.moveLeftRight = 1.0
                            def _up():
                                if b.node.exists():
                                    b.node.moveUpDown = 1.0
                                    b.node.moveLeftRight = 0.0
                            def _left(): 
                                if b.node.exists():
                                    b.node.moveUpDown = 0.0
                                    b.node.moveLeftRight = -1.0
                            def _stop():
                                if b.node.exists():
                                    b.node.moveUpDown = 0.0
                                    b.node.moveLeftRight = 0.0
                            if b.node.exists():
                                b.node.jumpPressed = True
                                b.node.jumpPressed = False
                                b.node.handleMessage('attackSound')
                                bs.gameTimer(1,_left)
                                bs.gameTimer(120,_up)
                                bs.gameTimer(240,_right)
                                bs.gameTimer(360,_down)
                                bs.gameTimer(480,_stop)
                        bs.gameTimer(random.randrange(300,1000),bs.Call(_start))
                    elif taunt == 'dash':
                        b.node.moveUpDown = -1.0
                        b.node.moveLeftRight = 0
                        def _stop():
                            if b.node.exists():
                                b.node.moveUpDown = 0.0
                                b.node.moveLeftRight = 0.0
                        bs.gameTimer(10,bs.Call(_stop))
                        b.node.jumpPressed = True
                        b.node.jumpPressed = False
                        def _start():
                            b.node.moveUpDown = -1.0
                            b.node.moveLeftRight = 0
                            def _dash():
                                b.node.moveUpDown = -1.0
                                b.onJumpPress()
                                b.onPunchPress()
                                b.onJumpRelease()
                                b.onPunchRelease()
                            bs.gameTimer(random.randrange(50,200),bs.Call(_dash))
                        bs.gameTimer(random.randrange(100,200),bs.Call(_start))
                    elif taunt == 'wave':
                        b.node.moveUpDown = -1.0
                        b.node.moveLeftRight = 0
                        def _stop():
                            if b.node.exists():
                                b.node.moveUpDown = 0.0
                                b.node.moveLeftRight = 0.0
                        bs.gameTimer(50,bs.Call(_stop))
                        bs.gameTimer(random.randrange(0,750),bs.Call(b.node.handleMessage,'celebrateR',10000))
                    bs.gameTimer(random.randrange(0,1000),bs.Call(b.node.handleMessage,'attackSound'))
                    bs.gameTimer(random.randrange(1000,2000),bs.Call(b.node.handleMessage,'attackSound'))
                    bs.gameTimer(random.randrange(2000,3000),bs.Call(b.node.handleMessage,'attackSound'))

    def addBot(self,bot):
        """
        Add a bs.SpazBot instance to the set.
        """
        self._botLists[self._botAddList].append(bot)
        self._botAddList = (self._botAddList+1)%self._botListCount


# define our built-in characters...


###############  SPAZ   ##################
t = Appearance("Spaz")

t.colorTexture = "neoSpazColor"
t.colorMaskTexture = "neoSpazColorMask"

t.iconTexture = "neoSpazIcon"
t.iconMaskTexture = "neoSpazIconColorMask"

t.headModel = "neoSpazHead"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'spaz'


###############  Cute-Spaz   ##################
t = Appearance("Cute Spaz")

t.colorTexture = "neoSpazColor"
t.colorMaskTexture = "neoSpazColorMask"

t.iconTexture = "cuteSpaz"
t.iconMaskTexture = "neoSpazIconColorMask"

t.headModel = "neoSpazHead"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "zoeUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["zoeJump01",
              "zoeJump02",
              "zoeJump03"]
t.attackSounds=["zoeAttack01",
                "zoeAttack02",
                "zoeAttack03",
                "zoeEff",
                "zoeAttack04"]
t.impactSounds=["zoeEff",
                "zoeOw",
                "spazOw"]
t.deathSounds=["zoeScream01"]
t.pickupSounds=["zoeEff","zoePickup01"]
t.fallSounds=["zoeFall01"]

t.style = 'ninja'


###############  Zoe   ##################
t = Appearance("Zoe")

t.colorTexture = "zoeColor"
t.colorMaskTexture = "zoeColorMask"

t.defaultColor = (0.6,0.6,0.6)
t.defaultHighlight = (0,1,0)

t.iconTexture = "zoeIcon"
t.iconMaskTexture = "zoeIconColorMask"

t.headModel = "zoeHead"
t.torsoModel = "zoeTorso"
t.pelvisModel = "zoePelvis"
t.upperArmModel = "zoeUpperArm"
t.foreArmModel = "zoeForeArm"
t.handModel = "zoeHand"
t.upperLegModel = "zoeUpperLeg"
t.lowerLegModel = "zoeLowerLeg"
t.toesModel = "zoeToes"

t.jumpSounds=["zoeJump01",
              "zoeJump02",
              "zoeJump03"]
t.attackSounds=["zoeAttack01",
                "zoeAttack02",
                "zoeAttack03",
                "zoeAttack04"]
t.impactSounds=["zoeImpact01",
                "zoeImpact02",
                "zoeImpact03",
                "zoeImpact04"]
t.deathSounds=["zoeDeath01"]
t.pickupSounds=["zoePickup01"]
t.fallSounds=["zoeFall01"]

t.style = 'female'


###############  Ninja   ##################
t = Appearance("Snake Shadow")

t.colorTexture = "ninjaColor"
t.colorMaskTexture = "ninjaColorMask"

t.defaultColor = (1,1,1)
t.defaultHighlight = (0.55,0.8,0.55)

t.iconTexture = "ninjaIcon"
t.iconMaskTexture = "ninjaIconColorMask"

t.headModel = "ninjaHead"
t.torsoModel = "ninjaTorso"
t.pelvisModel = "ninjaPelvis"
t.upperArmModel = "ninjaUpperArm"
t.foreArmModel = "ninjaForeArm"
t.handModel = "ninjaHand"
t.upperLegModel = "ninjaUpperLeg"
t.lowerLegModel = "ninjaLowerLeg"
t.toesModel = "ninjaToes"

ninjaAttacks = ['ninjaAttack'+str(i+1)+'' for i in range(7)]
ninjaHits = ['ninjaHit'+str(i+1)+'' for i in range(8)]
ninjaJumps = ['ninjaAttack'+str(i+1)+'' for i in range(7)]

t.jumpSounds=ninjaJumps
t.attackSounds=ninjaAttacks
t.impactSounds=ninjaHits
t.deathSounds=["ninjaDeath1"]
t.pickupSounds=ninjaAttacks
t.fallSounds=["ninjaFall1"]

t.style = 'ninja'


###############  Kronk   ##################
t = Appearance("Kronk")

t.colorTexture = "kronk"
t.colorMaskTexture = "kronkColorMask"

t.defaultColor = (0.4,0.5,0.4)
t.defaultHighlight = (1,0.5,0.3)

t.iconTexture = "kronkIcon"
t.iconMaskTexture = "kronkIconColorMask"

t.headModel = "kronkHead"
t.torsoModel = "kronkTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "kronkUpperArm"
t.foreArmModel = "kronkForeArm"
t.handModel = "kronkHand"
t.upperLegModel = "kronkUpperLeg"
t.lowerLegModel = "kronkLowerLeg"
t.toesModel = "kronkToes"

kronkSounds = ["kronk1",
              "kronk2",
              "kronk3",
              "kronk4",
              "kronk5",
              "kronk6",
              "kronk7",
              "kronk8",
              "kronk9",
              "kronk10"]
t.jumpSounds=kronkSounds
t.attackSounds=kronkSounds
t.impactSounds=kronkSounds
t.deathSounds=["kronkDeath"]
t.pickupSounds=kronkSounds
t.fallSounds=["kronkFall"]

t.style = 'kronk'

###############  MEL   ##################
t = Appearance("Mel")

t.colorTexture = "melColor"
t.colorMaskTexture = "melColorMask"

t.defaultColor = (1,1,1)
t.defaultHighlight = (0.1,0.6,0.1)

t.iconTexture = "melIcon"
t.iconMaskTexture = "melIconColorMask"

t.headModel =     "melHead"
t.torsoModel =    "melTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "melUpperArm"
t.foreArmModel =  "melForeArm"
t.handModel =     "melHand"
t.upperLegModel = "melUpperLeg"
t.lowerLegModel = "melLowerLeg"
t.toesModel =     "melToes"

melSounds = ["mel01",
             "mel02",
             "mel03",
             "mel04",
             "mel05",
             "mel06",
             "mel07",
             "mel08",
             "mel09",
             "mel10"]

t.attackSounds = melSounds
t.jumpSounds = melSounds
t.impactSounds = melSounds
t.deathSounds=["melDeath01"]
t.pickupSounds = melSounds
t.fallSounds=["melFall01"]

t.style = 'mel'


###############  Jack Morgan   ##################

t = Appearance("Jack Morgan")

t.colorTexture = "jackColor"
t.colorMaskTexture = "jackColorMask"

t.defaultColor = (1,0.2,0.1)
t.defaultHighlight = (1,1,0)

t.iconTexture = "jackIcon"
t.iconMaskTexture = "jackIconColorMask"

t.headModel =     "jackHead"
t.torsoModel =    "jackTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "jackUpperArm"
t.foreArmModel =  "jackForeArm"
t.handModel =     "jackHand"
t.upperLegModel = "jackUpperLeg"
t.lowerLegModel = "jackLowerLeg"
t.toesModel =     "jackToes"

hitSounds = ["jackHit01",
             "jackHit02",
             "jackHit03",
             "jackHit04",
             "jackHit05",
             "jackHit06",
             "jackHit07"]

sounds = ["jack01",
          "jack02",
          "jack03",
          "jack04",
          "jack05",
          "jack06"]

t.attackSounds = sounds
t.jumpSounds = sounds
t.impactSounds = hitSounds
t.deathSounds=["jackDeath01"]
t.pickupSounds = sounds
t.fallSounds=["jackFall01"]

t.style = 'pirate'


###############  SANTA   ##################

t = Appearance("Santa Claus")

t.colorTexture = "santaColor"
t.colorMaskTexture = "santaColorMask"

t.defaultColor = (1,0,0)
t.defaultHighlight = (1,1,1)

t.iconTexture = "santaIcon"
t.iconMaskTexture = "santaIconColorMask"

t.headModel =     "santaHead"
t.torsoModel =    "santaTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "santaUpperArm"
t.foreArmModel =  "santaForeArm"
t.handModel =     "santaHand"
t.upperLegModel = "santaUpperLeg"
t.lowerLegModel = "santaLowerLeg"
t.toesModel =     "santaToes"

hitSounds = ['santaHit01','santaHit02','santaHit03','santaHit04']
sounds = ['santa01','santa02','santa03','santa04','santa05']

t.attackSounds = sounds
t.jumpSounds = sounds
t.impactSounds = hitSounds
t.deathSounds=["santaDeath"]
t.pickupSounds = sounds
t.fallSounds=["santaFall"]

t.style = 'santa'

###############  FROSTY   ##################

t = Appearance("Frosty")

t.colorTexture = "frostyColor"
t.colorMaskTexture = "frostyColorMask"

t.defaultColor = (0.5,0.5,1)
t.defaultHighlight = (1,0.5,0)

t.iconTexture = "frostyIcon"
t.iconMaskTexture = "frostyIconColorMask"

t.headModel =     "frostyHead"
t.torsoModel =    "frostyTorso"
t.pelvisModel = "frostyPelvis"
t.upperArmModel = "frostyUpperArm"
t.foreArmModel =  "frostyForeArm"
t.handModel =     "frostyHand"
t.upperLegModel = "frostyUpperLeg"
t.lowerLegModel = "frostyLowerLeg"
t.toesModel =     "frostyToes"

frostySounds = ['frosty01','frosty02','frosty03','frosty04','frosty05']
frostyHitSounds = ['frostyHit01','frostyHit02','frostyHit03']

t.attackSounds = frostySounds
t.jumpSounds = frostySounds
t.impactSounds = frostyHitSounds
t.deathSounds=["frostyDeath"]
t.pickupSounds = frostySounds
t.fallSounds=["frostyFall"]

t.style = 'frosty'

###############  BONES  ##################

t = Appearance("Bones")

t.colorTexture = "bonesColor"
t.colorMaskTexture = "bonesColorMask"

t.defaultColor = (0.6,0.9,1)
t.defaultHighlight = (0.6,0.9,1)

t.iconTexture = "bonesIcon"
t.iconMaskTexture = "bonesIconColorMask"

t.headModel =     "bonesHead"
t.torsoModel =    "bonesTorso"
t.pelvisModel =   "bonesPelvis"
t.upperArmModel = "bonesUpperArm"
t.foreArmModel =  "bonesForeArm"
t.handModel =     "bonesHand"
t.upperLegModel = "bonesUpperLeg"
t.lowerLegModel = "bonesLowerLeg"
t.toesModel =     "bonesToes"

bonesSounds =    ['bones1','bones2','bones3']
bonesHitSounds = ['bones1','bones2','bones3']

t.attackSounds = bonesSounds
t.jumpSounds = bonesSounds
t.impactSounds = bonesHitSounds
t.deathSounds=["bonesDeath"]
t.pickupSounds = bonesSounds
t.fallSounds=["bonesFall"]

t.style = 'bones'

# bear ###################################

t = Appearance("Bernard")

t.colorTexture = "bearColor"
t.colorMaskTexture = "bearColorMask"

t.defaultColor = (0.7,0.5,0.0)
#t.defaultHighlight = (0.6,0.5,0.8)

t.iconTexture = "bearIcon"
t.iconMaskTexture = "bearIconColorMask"

t.headModel =     "bearHead"
t.torsoModel =    "bearTorso"
t.pelvisModel =   "bearPelvis"
t.upperArmModel = "bearUpperArm"
t.foreArmModel =  "bearForeArm"
t.handModel =     "bearHand"
t.upperLegModel = "bearUpperLeg"
t.lowerLegModel = "bearLowerLeg"
t.toesModel =     "bearToes"

bearSounds =    ['bear1','bear2','bear3','bear4']
bearHitSounds = ['bearHit1','bearHit2']

t.attackSounds = bearSounds
t.jumpSounds = bearSounds
t.impactSounds = bearHitSounds
t.deathSounds=["bearDeath"]
t.pickupSounds = bearSounds
t.fallSounds=["bearFall"]

t.style = 'bear'

# Penguin ###################################

t = Appearance("Pascal")

t.colorTexture = "penguinColor"
t.colorMaskTexture = "penguinColorMask"

t.defaultColor = (0.3,0.5,0.8)
t.defaultHighlight = (1,0,0)

t.iconTexture = "penguinIcon"
t.iconMaskTexture = "penguinIconColorMask"

t.headModel =     "penguinHead"
t.torsoModel =    "penguinTorso"
t.pelvisModel =   "penguinPelvis"
t.upperArmModel = "penguinUpperArm"
t.foreArmModel =  "penguinForeArm"
t.handModel =     "penguinHand"
t.upperLegModel = "penguinUpperLeg"
t.lowerLegModel = "penguinLowerLeg"
t.toesModel =     "penguinToes"

penguinSounds =    ['penguin1','penguin2','penguin3','penguin4']
penguinHitSounds = ['penguinHit1','penguinHit2']

t.attackSounds = penguinSounds
t.jumpSounds = penguinSounds
t.impactSounds = penguinHitSounds
t.deathSounds=["penguinDeath"]
t.pickupSounds = penguinSounds
t.fallSounds=["penguinFall"]

t.style = 'penguin'


# Ali ###################################
t = Appearance("Taobao Mascot")
t.colorTexture = "aliColor"
t.colorMaskTexture = "aliColorMask"
t.defaultColor = (1,0.5,0)
t.defaultHighlight = (1,1,1)
t.iconTexture = "aliIcon"
t.iconMaskTexture = "aliIconColorMask"
t.headModel =     "aliHead"
t.torsoModel =    "aliTorso"
t.pelvisModel =   "aliPelvis"
t.upperArmModel = "aliUpperArm"
t.foreArmModel =  "aliForeArm"
t.handModel =     "aliHand"
t.upperLegModel = "aliUpperLeg"
t.lowerLegModel = "aliLowerLeg"
t.toesModel =     "aliToes"
aliSounds =    ['ali1','ali2','ali3','ali4']
aliHitSounds = ['aliHit1','aliHit2']
t.attackSounds = aliSounds
t.jumpSounds = aliSounds
t.impactSounds = aliHitSounds
t.deathSounds=["aliDeath"]
t.pickupSounds = aliSounds
t.fallSounds=["aliFall"]
t.style = 'ali'

# cyborg ###################################
t = Appearance("B-9000")
t.colorTexture = "cyborgColor"
t.colorMaskTexture = "cyborgColorMask"
t.defaultColor = (0.5,0.5,0.5)
t.defaultHighlight = (1,0,0)
t.iconTexture = "cyborgIcon"
t.iconMaskTexture = "cyborgIconColorMask"
t.headModel =     "cyborgHead"
t.torsoModel =    "cyborgTorso"
t.pelvisModel =   "cyborgPelvis"
t.upperArmModel = "cyborgUpperArm"
t.foreArmModel =  "cyborgForeArm"
t.handModel =     "cyborgHand"
t.upperLegModel = "cyborgUpperLeg"
t.lowerLegModel = "cyborgLowerLeg"
t.toesModel =     "cyborgToes"
cyborgSounds =    ['cyborg1','cyborg2','cyborg3','cyborg4']
cyborgHitSounds = ['cyborgHit1','cyborgHit2']
t.attackSounds = cyborgSounds
t.jumpSounds = cyborgSounds
t.impactSounds = cyborgHitSounds
t.deathSounds=["cyborgDeath"]
t.pickupSounds = cyborgSounds
t.fallSounds=["cyborgFall"]
t.style = 'cyborg'

# Agent ###################################
t = Appearance("Agent Johnson")
t.colorTexture = "agentColor"
t.colorMaskTexture = "agentColorMask"
t.defaultColor = (0.3,0.3,0.33)
t.defaultHighlight = (1,0.5,0.3)
t.iconTexture = "agentIcon"
t.iconMaskTexture = "agentIconColorMask"
t.headModel =     "agentHead"
t.torsoModel =    "agentTorso"
t.pelvisModel =   "agentPelvis"
t.upperArmModel = "agentUpperArm"
t.foreArmModel =  "agentForeArm"
t.handModel =     "agentHand"
t.upperLegModel = "agentUpperLeg"
t.lowerLegModel = "agentLowerLeg"
t.toesModel =     "agentToes"
agentSounds =    ['agent1','agent2','agent3','agent4']
agentHitSounds = ['agentHit1','agentHit2']
t.attackSounds = agentSounds
t.jumpSounds = agentSounds
t.impactSounds = agentHitSounds
t.deathSounds=["agentDeath"]
t.pickupSounds = agentSounds
t.fallSounds=["agentFall"]
t.style = 'agent'

# Pixie ###################################
t = Appearance("Pixel")
t.colorTexture = "pixieColor"
t.colorMaskTexture = "pixieColorMask"
t.defaultColor = (0,1,0.7)
t.defaultHighlight = (0.65,0.35,0.75)
t.iconTexture = "pixieIcon"
t.iconMaskTexture = "pixieIconColorMask"
t.headModel =     "pixieHead"
t.torsoModel =    "pixieTorso"
t.pelvisModel =   "pixiePelvis"
t.upperArmModel = "pixieUpperArm"
t.foreArmModel =  "pixieForeArm"
t.handModel =     "pixieHand"
t.upperLegModel = "pixieUpperLeg"
t.lowerLegModel = "pixieLowerLeg"
t.toesModel =     "pixieToes"
pixieSounds =    ['pixie1','pixie2','pixie3','pixie4']
pixieHitSounds = ['pixieHit1','pixieHit2']
t.attackSounds = pixieSounds
t.jumpSounds = pixieSounds
t.impactSounds = pixieHitSounds
t.deathSounds=["pixieDeath"]
t.pickupSounds = pixieSounds
t.fallSounds=["pixieFall"]
t.style = 'pixie'

# B.I.T.S ###################################
t = Appearance("B.I.T.S")
t.colorTexture = "pixieColor"
t.colorMaskTexture = "pixieColorMask"
t.defaultColor = (0,1,0.7)
t.defaultHighlight = (0.65,0.35,0.75)
t.iconTexture = "pixieIcon"
t.iconMaskTexture = "pixieIconColorMask"
t.headModel =     "pixieHead"
t.torsoModel =    "pixieTorso"
t.pelvisModel =   "pixiePelvis"
t.upperArmModel = "santaUpperArm"
t.foreArmModel =  "pixieForeArm"
t.handModel =     "pixieHand"
t.upperLegModel = "bonesUpperLeg"
t.lowerLegModel = "frostyLowerLeg"
t.toesModel =     "pixieToes"
pixieSounds =    ['pixie1','pixie2','pixie3','pixie4']
pixieHitSounds = ['pixieHit1','pixieHit2']
t.attackSounds = pixieSounds
t.jumpSounds = pixieSounds
t.impactSounds = pixieHitSounds
t.deathSounds=["pixieDeath"]
t.pickupSounds = pixieSounds
t.fallSounds=["pixieFall","zoeFall01"]
t.style = 'female'

# Bunny ###################################
t = Appearance("Easter Bunny")
t.colorTexture = "bunnyColor"
t.colorMaskTexture = "bunnyColorMask"
t.defaultColor = (1,1,1)
t.defaultHighlight = (1,0.5,0.5)
t.iconTexture = "bunnyIcon"
t.iconMaskTexture = "bunnyIconColorMask"
t.headModel =     "bunnyHead"
t.torsoModel =    "bunnyTorso"
t.pelvisModel =   "bunnyPelvis"
t.upperArmModel = "bunnyUpperArm"
t.foreArmModel =  "bunnyForeArm"
t.handModel =     "bunnyHand"
t.upperLegModel = "bunnyUpperLeg"
t.lowerLegModel = "bunnyLowerLeg"
t.toesModel =     "bunnyToes"
bunnySounds =    ['bunny1','bunny2','bunny3','bunny4']
bunnyHitSounds = ['bunnyHit1','bunnyHit2']
t.attackSounds = bunnySounds
t.jumpSounds = ['bunnyJump']
t.impactSounds = bunnyHitSounds
t.deathSounds=["bunnyDeath"]
t.pickupSounds = bunnySounds
t.fallSounds=["bunnyFall"]
t.style = 'bunny'

# Ronnie ###################################
t = Appearance("Ronnie")
t.colorTexture = "ronnieColor"
t.colorMaskTexture = "ronnieColorMask"
t.defaultColor = (1,0.5,0.5)
t.defaultHighlight = (1,1,1)
t.iconTexture = "ronnieIcon"
t.iconMaskTexture = "ronnieIconColorMask"
t.headModel =     "ronnieHead"
t.torsoModel =    "ronnieTorso"
t.pelvisModel =   "aliPelvis"
t.upperArmModel = "ronnieUpperArm"
t.foreArmModel =  "ronnieForeArm"
t.handModel =     "ronnieHand"
t.upperLegModel = "ronnieUpperLeg"
t.lowerLegModel = "ronnieLowerLeg"
t.toesModel =     "ronnieToes"
ronnieSounds =    ['ronnie1','ronnie2','ronnie3','ronnie4','ronnie5','ronnie6','ronnie7']
ronnieHitSounds = ['ronniePain1','ronniePain2','ronniePain3','ronniePain4','ronniePain5']
t.attackSounds = ronnieSounds
t.jumpSounds = ronnieSounds
t.impactSounds = ronnieHitSounds
t.deathSounds=['ronnieDeath1','ronnieDeath2']
t.pickupSounds = ronnieSounds
t.fallSounds=["ronnieFall"]
t.style = 'ali'

##CUSTOM CHARACTERS BELOW
# Looie ###################################
t = Appearance("Looie")
t.colorTexture = "looieColor"
t.colorMaskTexture = "looieMask"
t.defaultColor = (1,0.7,0.0)
t.defaultHighlight = (1,1,1)
t.iconTexture = "looieIcon"
t.iconMaskTexture = "looieIconMask"
t.headModel =     "looieHead"
t.torsoModel =    "looieBody"
t.pelvisModel =   "zero"
t.upperArmModel = "zero"
t.foreArmModel =  "zero"
t.handModel =     "looieHand"
t.upperLegModel = "zero"
t.lowerLegModel = "looieLowerLeg"
t.toesModel =     "zero"
looieSounds =    ['looie1','looie2','looie3','looie4','looie5','looie6','looie7']
looieHitSounds = ['looiePain1','looiePain2','looiePain3','looiePain4','looiePain5']
t.attackSounds = looieSounds
t.jumpSounds = looieSounds
t.impactSounds = looieHitSounds
t.deathSounds=['looieDeath1','looieDeath2','looieDeath3']
t.pickupSounds = looieSounds
t.fallSounds=["looieFall1","looieFall2"]
t.style = 'agent'

# AVGN ###################################
t = Appearance("AVGN")
t.colorTexture = "avgnColor"
t.colorMaskTexture = "avgnColorMask"
t.defaultColor = (1,1,1)
t.defaultHighlight = (0.53,0.28,0.14)
t.iconTexture = "avgnIcon"
t.iconMaskTexture = "avgnIconColorMask"
t.headModel =     "agentHead"
t.torsoModel =    "agentTorso"
t.pelvisModel =   "agentPelvis"
t.upperArmModel = "agentUpperArm"
t.foreArmModel =  "agentForeArm"
t.handModel =     "agentHand"
t.upperLegModel = "agentUpperLeg"
t.lowerLegModel = "agentLowerLeg"
t.toesModel =     "agentToes"
agentSounds =    ['avgn1','avgn2','avgn3','avgn4']
agentHitSounds = ['avgnPain1','avgnPain2','avgnPain3']
t.attackSounds = agentSounds
t.jumpSounds = agentSounds
t.impactSounds = agentHitSounds
t.deathSounds=["avgnDeath1","avgnDeath2","avgnDeath3","avgnDeath4","avgnDeath5"]
t.pickupSounds = agentSounds
t.fallSounds=["avgnFall1","avgnFall2","avgnFall3"]
t.style = 'agent'

# Zill ###################################
t = Appearance("Zill")
t.colorTexture = "zillColor"
t.colorMaskTexture = "zillColorMask"
t.defaultColor = (0.1,1,0.1)
t.defaultHighlight = (1,1,0)
t.iconTexture = "zillIcon"
t.iconMaskTexture = "zillIconColorMask"
t.headModel =     "zillHead"
t.torsoModel =    "zillBody"
t.pelvisModel =   "zero"
t.upperArmModel = "zillUpperArm"
t.foreArmModel =  "zillForeArm"
t.handModel =     "zillHand"
t.upperLegModel = "zillUpperLeg"
t.lowerLegModel = "zillLowerLeg"
t.toesModel =     "zero"
t.attackSounds = ['zillAttack1','zillAttack2','zillAttack3','zillAttack4','zillAttack5']
t.jumpSounds = ['zillJump1','zillJump2','zillJump3','zillJump4']
t.impactSounds = ['zillPain1','zillPain2','zillPain3','zillPain4','zillPain5']
t.pickupSounds = ['zillPickup1','zillPickup2','zillPickup3','zillPickup4','zillPickup5']
t.deathSounds=['zillDeath1','zillDeath2','zillDeath3','zillDeath4']
t.fallSounds=["zillFall1","zillFall2"]
t.style = 'cyborg'

# Spy ###################################
t = Appearance("Spy")
t.colorTexture = "spyColor"
t.colorMaskTexture = "spyColorMask"
t.defaultColor = (1,1,1)
t.defaultHighlight = (0.1,0.1,0.1)
t.iconTexture = "spyIcon"
t.iconMaskTexture = "spyIconColorMask"
t.headModel =     "spyHead"
t.torsoModel =    "spyTorso"
t.pelvisModel =   "spyPelvis"
t.upperArmModel = "spyUpperArm"
t.foreArmModel =  "spyForeArm"
t.handModel =     "spyHand"
t.upperLegModel = "spyUpperLeg"
t.lowerLegModel = "spyLowerLeg"
t.toesModel =     "spyToes"
t.attackSounds = ['spyAttack1','spyAttack2','spyAttack3','spyAttack4']
t.jumpSounds = ['spyJump1','spyJump2','spyJump3','spyJump4','spyJump5']
t.impactSounds = ['spyPain1','spyPain2','spyPain3','spyPain4']
t.deathSounds=['spyDeath1','spyDeath2','spyDeath3','spyDeath4','spyDeath5']
t.pickupSounds = ['spyPickup1','spyPickup2']
t.fallSounds=["spyFall1"]
t.style = 'agent'

# Mictlan ###################################
t = Appearance("Mictlan")
t.colorTexture = "mictlanColor"
t.colorMaskTexture = "mictlanColorMask"
t.defaultColor = (0.1,1,1)
t.defaultHighlight = (0.1,0.1,0.1)
t.iconTexture = "mictlanIcon"
t.iconMaskTexture = "mictlanIconColorMask"
t.headModel =     "zero"
t.torsoModel =    "mictlanTorso"
t.pelvisModel =   "aliPelvis"
t.upperArmModel = "mictlanUpperArm"
t.foreArmModel =  "mictlanForeArm"
t.handModel =     "mictlanHand"
t.upperLegModel = "mictlanUpperLeg"
t.lowerLegModel = "mictlanLowerLeg"
t.toesModel =     "mictlanToes"
mictlanSounds =    ['mictlan1','mictlan2','mictlan3','mictlan4','mictlan5','mictlan6','mictlan7','mictlan8']
mictlanHitSounds = ['mictlanPain1','mictlanPain2','mictlanPain3']
t.attackSounds = mictlanSounds
t.jumpSounds = mictlanSounds
t.impactSounds = mictlanHitSounds
t.deathSounds=["mictlanDeath"]
t.pickupSounds = mictlanSounds
t.fallSounds=["mictlanFall"]
t.style = 'agent'

# Wizard ###################################
t = Appearance("Grumbledorf")
t.colorTexture = "wizardColor"
t.colorMaskTexture = "wizardColorMask"
t.defaultColor = (0.2,0.4,1.0)
t.defaultHighlight = (0.06,0.15,0.4)
t.iconTexture = "wizardIcon"
t.iconMaskTexture = "wizardIconColorMask"
t.headModel =     "wizardHead"
t.torsoModel =    "wizardTorso"
t.pelvisModel =   "wizardPelvis"
t.upperArmModel = "wizardUpperArm"
t.foreArmModel =  "wizardForeArm"
t.handModel =     "wizardHand"
t.upperLegModel = "wizardUpperLeg"
t.lowerLegModel = "wizardLowerLeg"
t.toesModel =     "wizardToes"
wizardSounds =    ['wizard1','wizard2','wizard3','wizard4']
wizardHitSounds = ['wizardHit1','wizardHit2']
t.attackSounds = wizardSounds
t.jumpSounds = wizardSounds
t.impactSounds = wizardHitSounds
t.deathSounds=["wizardDeath"]
t.pickupSounds = wizardSounds
t.fallSounds=["wizardFall"]
t.style = 'agent'

# Milk (Cow Character) ###################################
t = Appearance("Milk")
t.colorTexture = "cowColor"
t.colorMaskTexture = "cowColorMask"
t.defaultColor = (1,1,1)
t.defaultHighlight = (1,0.3,0.5)
t.iconTexture = "cowIcon"
t.iconMaskTexture = "cowIconColorMask"
t.headModel =     "cowHead"
t.torsoModel =    "cowTorso"
t.pelvisModel =   "cowPelvis"
t.upperArmModel = "cowUpperArm"
t.foreArmModel =  "cowForeArm"
t.handModel =     "cowHand"
t.upperLegModel = "cowUpperLeg"
t.lowerLegModel = "cowLowerLeg"
t.toesModel =     "cowToes"
cowSounds =    ['cow1','cow2','cow3','cow4']
t.attackSounds = cowSounds
t.jumpSounds = cowSounds
t.impactSounds = cowSounds
t.deathSounds = ["cowDeath"]
t.pickupSounds = cowSounds
t.fallSounds = ["cowFall"]
t.style = 'bear'

# JuiceBoy ###################################
t = Appearance("Juice-Boy")
t.colorTexture = "juiceBoyColor"
t.colorMaskTexture = "juiceBoyColorMask"
t.defaultColor = (0.2,1,0.2)
t.defaultHighlight = (1,1,0)
t.iconTexture = "juiceBoyIcon"
t.iconMaskTexture = "juiceBoyIconColorMask"
t.headModel =     "zero"
t.torsoModel =    "juiceBoyTorso"
t.pelvisModel =   "zero"
t.upperArmModel = "juiceBoyUpperArm"
t.foreArmModel =  "juiceBoyForeArm"
t.handModel =     "juiceBoyHand"
t.upperLegModel = "juiceBoyUpperLeg"
t.lowerLegModel = "juiceBoyLowerLeg"
t.toesModel =     "juiceBoyToes"
juiceSounds = ['juice1','juice2','juice3','juice4','juice5','juice6']
t.attackSounds = juiceSounds
t.jumpSounds = juiceSounds
t.impactSounds = juiceSounds
t.deathSounds = ["juiceDeath"]
t.pickupSounds = juiceSounds
t.fallSounds = ["juiceFall"]
t.style = 'agent'

# Sir Bombalot (Knight) ###################################
t = Appearance("Sir Bombalot")
t.colorTexture = "knightColor"
t.colorMaskTexture = "knightColorMask"
t.defaultColor = (0.5,0.5,0.5)
t.defaultHighlight = (1,0.15,0.15)
t.iconTexture = "knightIcon"
t.iconMaskTexture = "knightIconColorMask"
t.headModel =     "knightHead"
t.torsoModel =    "knightTorso"
t.pelvisModel =   "knightPelvis"
t.upperArmModel = "knightUpperArm"
t.foreArmModel =  "knightForeArm"
t.handModel =     "knightHand"
t.upperLegModel = "knightUpperLeg"
t.lowerLegModel = "knightLowerLeg"
t.toesModel =     "knightToes"
knightSounds =    ['knight1','knight2','knight3','knight4','knight5','knight6']
t.attackSounds = knightSounds
t.jumpSounds = knightSounds
t.impactSounds = ['knightPain1','knightPain2','knightPain3','knightPain4']
t.deathSounds=['knightDeath1','knightDeath2']
t.pickupSounds = knightSounds
t.fallSounds=['knightFall']
t.style = 'cyborg'

# Willy ###################################
t = Appearance("Willy")

t.colorTexture = "willyColor"
t.colorMaskTexture = "willyColorMask"

t.defaultColor = (0.5,0.25,1.0)
t.defaultHighlight = (1,1,0)

t.iconTexture = "willyIcon"
t.iconMaskTexture = "willyIconColorMask"

t.headModel =     "willyHead"
t.torsoModel =    "willyTorso"
t.pelvisModel = "zero"
t.upperArmModel = "willyUpperArm"
t.foreArmModel =  "willyForeArm"
t.handModel =     "willyHand"
t.upperLegModel = "zero"
t.lowerLegModel = "willyLowerLeg"
t.toesModel =     "willyToes"

willySounds = ["willy1",
             "willy2",
             "willy3",
             "willy4",
             "willy5",
             "willy6",
             "willy7",
             "willy8",
             "willy9",
             "willy10",
             "willy11",
             "willy12",
             "willy13",
             "willy14"]

t.attackSounds = willySounds
t.jumpSounds = willySounds
t.impactSounds = ['willy4','willy6','willyPain1','willyPain2']
t.deathSounds=["willyDeath1","willyDeath2","willyDeath3","willyDeath4"]
t.pickupSounds = willySounds
t.fallSounds=["willyFall"]

t.style = 'agent'

# Grambeldorfe ###################################
t = Appearance("Grambeldorfe")
t.colorTexture = "grambelColor"
t.colorMaskTexture = "grambelColorMask"
t.defaultColor = (0.5,0.25,1.0)
t.defaultHighlight = (1,1,0)
t.iconTexture = "grambelIcon"
t.iconMaskTexture = "grambelIconColorMask"
t.headModel =     "grambelHead"
t.torsoModel =    "grambelTorso"
t.pelvisModel =   "grambelPelvis"
t.upperArmModel = "grambelUpperArm"
t.foreArmModel =  "grambelForeArm"
t.handModel =     "grambelHand"
t.upperLegModel = "grambelUpperLeg"
t.lowerLegModel = "grambelLowerLeg"
t.toesModel =     "grambelToes"
grambelSounds =    ['grambel1','grambel2','grambel3','grambel4','grambel5']
grambelHitSounds = ['grambelPain1','grambelPain2','grambelPain3']
t.attackSounds = grambelSounds
t.jumpSounds = grambelSounds
t.impactSounds = grambelHitSounds
t.deathSounds=["grambelDeath1","grambelDeath2","grambelDeath3","grambelDeath4",]
t.pickupSounds = ['grambelPickup1','grambelPickup2']
t.fallSounds=["grambelFall"]
t.style = 'agent'

# Puck ###Free But Nice###############
t = Appearance("Puck")

t.colorTexture = "puckColor"
t.colorMaskTexture = "puckColor"

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (1, 0.5, 0.5)

t.iconTexture = "powerupShield"
t.iconMaskTexture = "powerupShield"

t.headModel =     "puck"
t.torsoModel =    "zero"
t.pelvisModel =   "zero"
t.upperArmModel = "kronkUpperArm"
t.foreArmModel =  "kronkForeArm"
t.handModel =     "kronkHand"
t.upperLegModel = "kronkUpperLeg"
t.lowerLegModel = "kronkLowerLeg"
t.toesModel =     "kronkToes"

puckSounds =    ['corkPop','boxDrop','click01','combatBombDeployed']
t.attackSounds = puckSounds
t.jumpSounds = puckSounds
t.impactSounds = ['block','crystalHit','diceHit']
t.deathSounds=["bombDrop01","bombDrop02"]
t.pickupSounds = puckSounds
t.fallSounds=["blip"]

t.style = 'cyborg'

# TNT ################
t = Appearance("Exploder")

t.colorTexture = "tntClassic"
t.colorMaskTexture = "tntClassic"

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (1, 1, 1)

t.iconTexture = "tntClassic"
t.iconMaskTexture = "tntClassic"

t.headModel =     "powerupSimple"
t.torsoModel =    "ninjaTorso"
t.pelvisModel =   "ninjaPelvis"
t.upperArmModel = "ninjaUpperArm"
t.foreArmModel =  "ninjaForeArm"
t.handModel =     "ninjaHand"
t.upperLegModel = "ninjaUpperLeg"
t.lowerLegModel = "ninjaLowerLeg"
t.toesModel =     "ninjaToes"

noSounds =    ['']
t.attackSounds = noSounds
t.jumpSounds = noSounds
t.impactSounds = ['']
t.deathSounds=[""]
t.pickupSounds = noSounds
t.fallSounds=[""]

t.style = 'cyborg'

# Lucy Chance - WORK IN PROGRESS###################################
t = Appearance("Lucy Chance")

t.colorTexture = "lucyColor"
t.colorMaskTexture = "lucyColorMask"

t.defaultColor = (0.6,0.6,0.6)
t.defaultHighlight = (0,1,0)

t.iconTexture = "lucyIcon"
t.iconMaskTexture = "lucyIconColorMask"

t.headModel = "lucyHead"
t.torsoModel = "lucyTorso"
t.pelvisModel = "lucyPelvis"
t.upperArmModel = "lucyUpperArm"
t.foreArmModel = "lucyForeArm"
t.handModel = "lucyHand"
t.upperLegModel = "lucyUpperLeg"
t.lowerLegModel = "lucyLowerLeg"
t.toesModel = "lucyToes"

lucySounds =    ['ali1','ali2','ali3','ali4']
lucyHitSounds = ['aliHit1','aliHit2']
t.attackSounds = lucySounds
t.jumpSounds = lucySounds
t.impactSounds = lucyHitSounds
t.deathSounds=["aliDeath"]
t.pickupSounds = lucySounds
t.fallSounds=["aliFall"]

t.style = 'agent'

# Klaymen ###################################
t = Appearance("Klaymen")
t.colorTexture = "klaymanColor"
t.colorMaskTexture = "klaymanColorMask"
t.defaultColor = (1,0.1,0.1)
t.defaultHighlight = (1,0.7,0.0)
t.iconTexture = "klaymanIcon"
t.iconMaskTexture = "klaymanIconColorMask"
t.headModel =     "klaymanHead"
t.torsoModel =    "klaymanTorso"
t.pelvisModel =   "zero"
t.upperArmModel = "klaymanUpperArm"
t.foreArmModel =  "klaymanForeArm"
t.handModel =     "klaymanHand"
t.upperLegModel = "klaymanUpperLeg"
t.lowerLegModel = "klaymanLowerLeg"
t.toesModel =     "klaymanToes"
klaymanSounds =    ['klayman1','klayman2','klayman2','klayman3','klayman3','klayman4']
klaymanHitSounds = ['klayman1','klayman4']
t.attackSounds = klaymanSounds
t.jumpSounds = klaymanSounds
t.impactSounds = klaymanHitSounds
t.deathSounds=["klaymanDeath1","klaymanDeath2","klaymanDeath3"]
t.pickupSounds = klaymanSounds
t.fallSounds=["klaymanFall"]
t.style = 'agent'