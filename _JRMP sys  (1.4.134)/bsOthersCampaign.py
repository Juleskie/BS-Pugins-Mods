import bs
import random
import bsSpaz
import bsInternal
import bsUtils
import bsGame
import random
import math
import weakref


#credit to shinji (for the level & content)
# 1
class Boss1Bot(bsSpaz.PirateBotRadius):
    """
    category: Bot Classes
    
    1st Boss.
    """
    color = (1,1,0)
    highlight = (1,1,0)
    impactScale = 0.4
    hitPoints = 1500
    startCursed = False
    defaultBlastRadius = 1.848
    defaultShields = True
    defaultName = "Boss #1"
    
# 2
class Boss2Bot(bsSpaz.AgentBotShielded):
    """
    category: Bot Classes
    
    2nd Boss.
    """
    character = 'Pascal'
    color = (1.0,1.7,2.0)
    highlight = (1.3,1.4,1.8)
    hitPoints = 5000    
    impactScale = 0.4   
    throwDistMax = 10.0
    throwDistMin = 0.0
    defaultBombType = 'snowball'
    defaultBoxingGloves = True
    defaultName = "Boss #2"

# 3
class Boss3Bot(bsSpaz.ToughGuyBot):
    """
    category: Bot Classes
    
    3rd Boss.
    """
    color = (0.13,0.13,0.13)
    highlight = (0.13,0.13,0.13)
    character = 'Agent Johnson'
    impactScale = 0.4
    punchiness = 0.3
    hitPoints = 5000    
    defaultSpeedBoots = True
    defaultName = "Boss #3"
# 4
class Boss4Bot(bsSpaz.CyborgBot):
    """
    category: Bot Classes
    
    4th Boss.
    """
    color = (2,2,2)
    highlight = (1,1.4,2.0)
    character = 'Taobao Mascot'
    hitPoints = 5000    
    impactScale = 0.4
    defaultBombType = 'dynamite'
    defaultName = "Boss #4"
    
#5
class Boss5Bot(bsSpaz.SpazBot):
    """
    category: Bot Classes
    
    5th Boss.
    """
    color = (0.8,0,2.0)
    highlight = (2,0.8,1.4)
    character = 'Zoe'
    impactScale = 0.4
    throwRate = 3.3
    throwDistMax = 3.0
    throwDistMin = 1.25
    chargeSpeedMax = 5.0
    chargeSpeedMin = 2.3
    runDistMin = 2.75
    run = True
    defaultBoxingGloves = True
    hitPoints = 5500    
    defaultBombType = 'combat'  
    defaultBombCount = 5
    defaultName = "Boss #5"
    
#6
class Boss6Bot(bsSpaz.SpazBot):
    """
    category: Bot Classes
    
    6th Boss.
    """
    color = (1.85,1.75,1.45)
    highlight = (2.25,1.30,0.45)
    character = 'Bernard'
    impactScale = 0.56
    hitPoints = 5900
    run = True
    punchiness = 0.85
    chargeDistMax = 12.5
    chargeDistMin = 4.9    
    throwDistMax = 1.9
    defaultBoxingGloves = True
    defaultBombType = 'ranger'  
    defaultBombCount = 3
    defaultName = "Boss #6"
# 7
class Boss7Bot(bsSpaz.BomberBotPro):
    """
    category: Bot Classes
    
    7th Boss.
    """
    color = (1.2,1.5,1.9)
    highlight = (2,2,3)
    character = 'Looie'
    impactScale = 0.4
    hitPoints = 5900
    throwRate = 1.6
    defaultBombType = 'magnet'  
    defaultBombCount = 5
    defaultName = "Boss #7"
    

class JRMPBossBattle(bs.CoopGameActivity): #CoopGame

    tips = []

    @classmethod
    def getName(cls):
        return 'JRMP Boss Battle'

    @classmethod
    def getDescription(cls,sessionType):
        return "Defeat all Waves!"

    def __init__(self,settings={}):

        settings['map'] = 'Courtyard'

        bs.CoopGameActivity.__init__(self,settings)

        # show messages when players die since it matters here..
        self.announcePlayerDeaths = True
        activity = bsInternal._getForegroundHostActivity()
        
        self._specialWaveSound = bs.getSound('nightmareSpecialWave')
        self._newWaveSound = bs.getSound('scoreHit01')
        self._winSound = bs.getSound("score")
        self._cashRegisterSound = bs.getSound('cashRegister')
        self._aPlayerHasBeenHurt = False

        # fixme - should use standard map defs..
        self._spawnCenter = (0,3,-2)
        self._tntSpawnPosition = (0,3,2.1)
        self._powerupCenter = (0,5,-1.6)
        self._powerupSpread = (4.6,2.7)
        

    def onTransitionIn(self):

        bs.CoopGameActivity.onTransitionIn(self)
        self._spawnInfoText = bs.NodeActor(bs.newNode("text",
                                                      attrs={'position':(15,-130),
                                                             'hAttach':"left",
                                                             'vAttach':"top",
                                                             'scale':0.55,
                                                             'color':(0.3,0.8,0.3,1.0),
                                                             'text':''}))
        bs.playMusic('FlagRunner')
                                                             
        self._scoreBoard = bs.ScoreBoard(label=bs.Lstr(resource='scoreText'),scoreSplit=0.5)
        self._gameOver = False
        self._wave = 0
        self._canEndWave = True
        self._score = 0
        self._timeBonus = 0


    def onBegin(self):

        bs.CoopGameActivity.onBegin(self)
        playerCount = len(self.players)
        self._dingSound = bs.getSound('dingSmall')
        self._dingSoundHigh = bs.getSound('dingSmallHigh')
        bs.getSharedObject('globals').tint = (1.1,1.0,1.2)
        #values = {0: (1*1.3, 0, 0), 19000: (0, 1*1.3, 0),19000*2: (0, 0, 1*1.3), 19000*3: (1*1.3, 0, 0)}
        #bs.animateArray(bs.getSharedObject('globals'), 'tint', 3,values, loop=True)
        
        import bsUtils
        bsUtils.ControlsHelpOverlay(delay=3000,lifespan=10000,bright=True).autoRetain()

        self._haveTnt = False
        self._excludePowerups = ['curse','dizzyCake','overdrive','combatBombs','leap','knockerBombs','candyBombs','blastBuff','fireworkBombs',
                                                     'gloo','magnet','scatterBombs','dynamiteBombs','speed','glueBombs','snoball','clusterBomb','iceBombs','pills','health','fireBombs',
                                                     'palette','digitalBombs','grenades','snowball','radiusBombs','dynamitePack','landMines','hunterBombs','bloomingBombs']
        self._waves = [
                # 1
                {'entries':[
                        {'type':bs.ToughGuyBot,'point':'Left'},
                        {'type':bs.ToughGuyBot,'point':'Right'},
                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                        {'type':bs.ToughGuyBot,'point':'RightUpper'} if playerCount > 1 else None,
                        {'type':bs.NinjaBot,'point':'TopRight'} if playerCount > 2 else None,
                        ]},
                # 2             
                {'entries':[
                        {'type':bs.MelBot,'point':'Left'},
                        {'type':bs.MelBot,'point':'Right'},
                        {'type':bs.MelBot,'point':'Top'} if playerCount > 2 else None,
                        {'type':bs.MelBot,'point':'Bottom'} if playerCount > 3 else None,
                        {'type':bs.FrostyBotStatic,'point':'TurretBottomLeft'},
                        {'type':bs.FrostyBotStatic,'point':'TurretBottomRight'},
                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddleLeft'},
                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddleLeft'} if playerCount > 2 else None,
                        ]},
                # 3
                {'entries':[
                            {'type':bs.NinjaBot,'point':'BottomRight'} if playerCount > 1 else None,
                            {'type':bs.NinjaBot,'point':'Bottom'},
                            {'type':bs.NinjaBot,'point':'BottomLeft'} if playerCount > 2 else None,
                            {'type':bs.NinjaBot,'point':'Left'},
                            {'type':bs.NinjaBot,'point':'LeftUpper'} if playerCount > 2 else None,
                            {'type':bs.NinjaBot,'point':'BottomHalfRight'},
                            {'type':bs.NinjaBot,'point':'Right'},
                            ]},
                #4 Boss 1
                {'entries':[
                            {'type':bs.PirateBot,'point':'Right'},
                            {'type':bs.BomberBot,'point':'Left'},
                            {'type':bs.MelBot,'point':'LeftUpper'},
                            {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'} if playerCount > 3 else None,
                            {'type':bs.ChickBotStatic,'point':'TurretBottomRight'},
                            {'type':bs.ChickBotStatic,'point':'TurretBottomLeft'},
                            {'type':bs.NinjaBot,'point':'LeftUpper'} if playerCount > 1 else None,
                            {'type':'delay','duration':7000},
                            {'type':bs.PirateBot,'point':'TopHalfRight'} if playerCount > 2 else None,
                            {'type':bs.PirateBot,'point':'Bottom'},
                            {'type':Boss1Bot,'point':'Top'},
                            ]},
                # 5
                {'entries':[
                            {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                            {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                            {'type':bs.BonesBot,'point':'BottomRight'},
                            {'type':bs.BonesBot,'point':'Bottom'},
                            {'type':bs.BonesBot,'point':'BottomHalfRight'},
                            {'type':bs.BonesBotPro,'point':'BottomLeft'} if playerCount > 1 else None,
                            {'type':bs.NinjaBotPro,'point':'BottomHalfLeft'} if playerCount > 2 else None,
                            {'type':bs.CyborgBotStatic,'point':'TurretTopMiddleRight'},
                            {'type':bs.CyborgBot,'point':'Right'},
                            {'type':bs.CyborgBot,'point':'RightUpper'} if playerCount > 2 else None,
                            {'type':bs.CyborgBotStatic,'point':'TurretTopMiddle'},
                            ]},
                # 6
                {'entries':[
                            {'type':bs.PirateBotRadius,'point':'Left'} if playerCount > 2 else None,
                            {'type':bs.PirateBotRadius,'point':'Right'},
                            {'type':bs.WizardBot,'point':'BottomLeft'},
                            {'type':bs.WizardBot,'point':'BottomRight'},
                            {'type':bs.WizardBotStatic,'point':'TurretBottomLeft'},
                            {'type':'delay','duration':5000},
                            {'type':bs.MelDuperBot,'point':'Right'} if playerCount > 1 else None,
                            {'type':bs.MelDuperBot,'point':'Left'} if playerCount > 1 else None,
                            {'type':bs.MelBotStatic,'point':'TurretBottomRight'},
                            {'type':bs.MelBotStatic,'point':'TurretBottomLeft'},
                            {'type':bs.MelBot,'point':'RightUpperMore'},
                            {'type':bs.MelBot,'point':'RightLower'},
                            ]},
                # 7
                {'entries':[
                        {'type':bs.RonnieBotStatic,'point':'TurretTopMiddle'},
                        {'type':bs.BunnyBot,'point':'TopRight'},
                        {'type':bs.BonesBot,'point':'RightUpperMore'},
                        {'type':bs.AgentBot,'point':'RightUpper'} if playerCount > 1 else None, 
                        {'type':bs.BonesBot,'point':'RightLower'},
                        {'type':bs.BonesBot,'point':'RightLowerMore'},
                        {'type':bs.BonesBot,'point':'RightLowerMore'} if playerCount > 1 else None,
                        {'type':bs.AgentBot,'point':'BottomRight'},
                        {'type':'delay','duration':2000},
                        {'type':bs.SpyBot,'point':'Left'},
                        {'type':bs.RonnieBot,'point':'TurretTopLeft'},
                        {'type':'delay','duration':3000},
                        {'type':bs.SpyBot,'point':'Right'},
                        ]},
                #8
                {'entries':[
                            {'type':'delay','duration':1000}, 
                            {'type':bs.ToughGuyBot,'point':'LeftUpperMore'},
                            {'type':'delay','duration':800}, 
                            {'type':bs.BomberBot,'point':'LeftUpper'},
                            {'type':'delay','duration':500}, 
                            {'type':bs.ToughGuyBot,'point':'Left'}, 
                            {'type':'delay','duration':500}, 
                            {'type':bs.ToughGuyBot,'point':'LeftLower'},
                            {'type':'delay','duration':3000}, 
                            {'type':bs.AgentBotShielded,'point':'LeftUpper'}, 
                            {'type':bs.ChickBot,'point':'TopRight'},
                            {'type':bs.ChickBot,'point':'Right'}, 
                            {'type':bs.ChickBot,'point':'RightUpperMore'}, 
                            {'type':bs.CyborgBotStatic,'point':'TurretTopMiddle'}, 
                            {'type':'delay','duration':7000}, 
                            {'type':Boss2Bot,'point':'Top'}, # 2 boss
                            ]},
                # 9
                {'entries':[
                            {'type':bs.BomberBotProShielded,'point':'TopLeft'},
                            {'type':bs.BomberBotProShielded,'point':'TopRight'},
                            {'type':bs.BomberBotProShielded,'point':'Top'} if playerCount > 3 else None,
                            {'type':bs.BomberBotProShielded,'point':'TopHalfLeft'} if playerCount > 1 else None,
                            {'type':bs.BomberBotProShielded,'point':'TopHalfRight'} if playerCount > 2 else None,
                            {'type':bs.BomberBotProStaticShielded,'point':'TurretTopLeft'},
                            {'type':bs.BomberBotProStaticShielded,'point':'TurretTopRight'},
                            {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomLeft'},
                            {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomRight'},
                            {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleLeft'},
                            {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleRight'},
                            {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddle'},
                            ]},  
                # 10
                {'entries':[
                            {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                            {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                            {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                            {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                            {'type':bs.ToughGuyBotPro,'point':'Left'},
                            {'type':bs.ToughGuyBotProShielded,'point':'LeftUpper'},
                            {'type':bs.ToughGuyBotPro,'point':'RightUpper'},
                            {'type':bs.ToughGuyBotProShielded,'point':'Right'},
                            {'type':bs.ToughGuyBotProShielded,'point':'RightUpperMore'} if playerCount > 1 else None,
                            {'type':bs.NinjaBotProShielded,'point':'TopLeft'},
                            {'type':bs.NinjaBotProShielded,'point':'TopRight'},
                            {'type':bs.NinjaBotProShielded,'point':'Top'} if playerCount > 1 else None,
                            {'type':bs.NinjaBotProShielded,'point':'Bottom'} if playerCount > 2 else None,
                            ]},
                #11 Boss 3
                {'entries':[
                            {'type':bs.JuiceBot,'point':'BottomHalfRight'},
                            {'type':bs.JuiceBot,'point':'BottomHalfLeft'},
                            {'type':bs.ChickBot,'point':'TopHalfRight'},
                            {'type':bs.BearBot,'point':'Top'},
                            {'type':bs.MelBotStatic,'point':'TurretTopMiddleLeft'},
                            {'type':bs.BomberBotProStatic,'point':'TurretTopMiddleRight'},
                            {'type':'delay','duration':7000},
                            {'type':bs.ToughGuyBot,'point':'Top'},
                            {'type':bs.PirateBotShielded,'point':'TopHalfLeft'},
                            {'type':bs.PirateBotShielded,'point':'TopHalfRight'},
                            {'type':bs.AgentBot,'point':'TopLeft'},
                            {'type':Boss3Bot,'point':'LeftLowerMore'},
                            ]},
                # 12
                {'entries':[
                             {'type':bs.MelDuperBot,'point':'Top'},
                             {'type':bs.MelDuperBot,'point':'TopRight'} if playerCount > 1 else None,
                             {'type':bs.MelDuperBot,'point':'TopLeft'} if playerCount > 2 else None,
                             {'type':bs.BunnyBot,'point':'LeftUpper'},
                             {'type':bs.BunnyBot,'point':'LeftLower'},
                             {'type':bs.BunnyBot,'point':'RightUpper'},
                             {'type':bs.NinjaBotPro,'point':'Right'},
                             {'type':bs.NinjaBotPro,'point':'Bottom'},
                             {'type':bs.PixelBotPro,'point':'BottomHalfLeft'},
                             ]},
                # 13
                {'entries':[
                            {'type':bs.AliBot,'point':'Right'},
                            {'type':bs.AliBot,'point':'Top'},
                            {'type':bs.SpyBot,'point':'BottomLeft'},
                            {'type':bs.AliBot,'point':'Left'},
                            {'type':bs.FrostyBotStatic,'point':'TurretBottomLeft'},
                            {'type':bs.FrostyBotStatic,'point':'TurretBottomRight'},
                            {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'} if playerCount > 1 else None,
                            {'type':bs.BomberBot,'point':'TopHalfLeft'} if playerCount > 2 else None,
                            {'type':'delay','duration':2000},
                            {'type':bs.LooieBot,'point':'LeftUpperMore'},
                            {'type':bs.ChickBotStatic,'point':'TurretTopMiddleLeft'},
                            {'type':bs.ChickBotStatic,'point':'TurretTopMiddleRight'},
                            ]},
                # 14
                {'entries':[
                            {'type':bs.MelBotStatic,'point':'TurretTopLeft'},
                            {'type':bs.MelBotStatic,'point':'TurretTopRight'},
                            {'type':bs.MelBotStatic,'point':'TurretBottomLeft'},
                            {'type':bs.MelBotStatic,'point':'TurretBottomRight'},
                            {'type':bs.MelBotStatic,'point':'TurretTopMiddleLeft'},
                            {'type':bs.MelBotStatic,'point':'TurretTopMiddleRight'},
                            {'type':bs.MelBot,'point':'Top'},
                            {'type':bs.MelBot,'point':'Bottom'} if playerCount > 2 else None,
                            {'type':bs.MelBot,'point':'Left'} if playerCount > 1 else None,
                            {'type':bs.MelBot,'point':'Right'},
                            {'type':bs.MelBot,'point':'LeftUpper'},
                            ]},
                #15 Boss 4
                {'entries':[
                            {'type':bs.AliBot,'point':'Right'},
                            {'type':bs.RonnieBot,'point':'Top'},
                            {'type':bs.CyborgBot,'point':'BottomLeft'},
                            {'type':bs.CyborgBot,'point':'BottomRight'},
                            {'type':bs.CyborgBotPro,'point':'Bottom'} if playerCount > 1 else None,
                            {'type':bs.AliBot,'point':'Left'},
                            {'type':'delay','duration':4000},
                            {'type':bs.FrostyBotStatic,'point':'TurretTopLeft'},
                            {'type':bs.WizardBotStatic,'point':'TurretTopRight'},
                            {'type':bs.WizardBotStatic,'point':'TurretTopMiddle'} if playerCount > 2 else None,
                            {'type':bs.AgentBotShielded,'point':'RightLower'},
                            {'type':Boss4Bot,'point':'TopLeft'},
                            ]},
                # 16
                {'entries':[
                            {'type':bs.ToughGuyBotPro,'point':'Right'},
                            {'type':bs.ToughGuyBotPro,'point':'RightLower'},
                            {'type':bs.AliBot,'point':'Left'},
                            {'type':bs.AliBot,'point':'LeftUpperMore'},
                            {'type':bs.SpyBotPro,'point':'Top'},
                            {'type':bs.PixelBot,'point':'LeftLower'},
                            {'type':bs.PixelBotPro,'point':'LeftLowerMore'} if playerCount > 1 else None,
                            {'type':bs.WizardBotStatic,'point':'TurrretTopLeft'} if playerCount > 2 else None,
                            {'type':bs.WizardBotStatic,'point':'TurrretTopRight'} if playerCount > 2 else None,
                            {'type':'delay','duration':7000},
                            {'type':bs.RonnieBotStatic,'point':'TurretTopRight'},
                            {'type':bs.MelBotStatic,'point':'TurretTopMiddle'},
                            {'type':bs.WizardBotStatic,'point':'TurretTopLeft'},
                            {'type':bs.FrostyBotStatic,'point':'TurretBottomLeft'},
                            {'type':bs.CyborgBotStatic,'point':'TurretBottomLeft'},
                            {'type':'delay','duration':3705},
                            {'type':bs.FrostyBot,'point':'BottomHalfLeft'},
                            {'type':bs.FrostyBot,'point':'BottomHalfRight'},
                            {'type':bs.NinjaBot,'point':'TopLeft'},
                            {'type':bs.NinjaBot,'point':'TopRight'},
                            ]},
                # 17
                {'entries':[
                            {'type':bs.CyborgBotStatic,'point':'TurretTopLeft'},
                            {'type':bs.CyborgBotStatic,'point':'TurretTopRight'},
                            {'type':bs.CyborgBotStatic,'point':'TurretBottomLeft'},
                            {'type':bs.CyborgBotStatic,'point':'TurretBottomRight'},
                            {'type':bs.CyborgBot,'point':'Top'},
                            {'type':bs.ZillBot,'point':'BottomLeft'},
                            {'type':bs.ZillBot,'point':'BottomRight'},
                            {'type':bs.AgentBotShielded,'point':'TopLeft'} if playerCount > 1 else None,
                            {'type':bs.CyborgBot,'point':'Bottom'},
                            {'type':'delay','duration':2000},
                            {'type':bs.ChickBot,'point':'BottomHalfLeft'},
                            {'type':bs.ChickBot,'point':'BottomHalfRight'},
                            {'type':bs.ChickBotPro,'point':'BottomRight'} if playerCount > 1 else None,
                            ]},
                # 18
                {'entries':[
                            {'type':bs.BearBotShielded,'point':'LeftLowerMore'},
                            {'type':bs.MelDuperBot,'point':'BottomHalfLeft'},
                            {'type':bs.KnightBot,'point':'Bottom'},
                            {'type':bs.KnightBot,'point':'Top'},
                            {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                            {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                            {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'},
                            {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                            {'type':'delay','duration':1780},
                            {'type':Boss5Bot,'point':'TopLeftEdge'},
                            {'type':'delay','duration':1320},
                            {'type':Boss6Bot,'point':'TopRightEdge'},
                            {'type':'delay','duration':2000},
                            {'type':bs.PascalBot,'point':'RightUpper'},
                            {'type':bs.PuckBot,'point':'TopHalfRight'},
                            {'type':'delay','duration':3500},
                            {'type':bs.LooieBot,'point':'RightUpperMore'},
                            {'type':bs.LooieBot,'point':'RightUpper'},
                            {'type':bs.LooieBot,'point':'Left'},
                            {'type':bs.MelBot,'point':'LeftLowerMore'} if playerCount > 1 else None,
                            {'type':bs.BearBot,'point':'Left'} if playerCount > 1 else None,
                            {'type':bs.BearBot,'point':'LeftUpper'} if playerCount > 2 else None,
                            ]},
                # 19 Boss 5 & 6
                {'entries':[
                            {'type':bs.LooieBotShielded,'point':'BottomLeft'},
                            {'type':bs.LooieBotPro,'point':'BottomRight'},
                            {'type':bs.SpyBot,'point':'TopHalfRight'},
                            {'type':bs.LooieBotPro,'point':'Top'} if playerCount > 1 else None,
                            {'type':'delay','duration':4500},
                            {'type':bs.PascalBot,'point':'LeftUpper'},
                            {'type':bs.AliBot,'point':'LeftUpperMore'} if playerCount > 1 else None,
                            {'type':bs.SpyBot,'point':'TurretTopMiddle'},
                            {'type':bs.BomberBotProStatic,'point':'TurretMiddle'},
                            {'type':'delay','duration':450},
                            {'type':bs.PirateBot,'point':'LeftUpper'},
                            {'type':bs.NinjaBot,'point':'TopHalfLeft'},
                            {'type':bs.NinjaBot,'point':'TopHalfRight'},
                            {'type':'delay','duration':450},
                            {'type':bs.PirateBot,'point':'Left'},
                            {'type':bs.AliBot,'point':'LeftLower'} if playerCount > 2 else None,
                            {'type':'delay','duration':600},
                            {'type':bs.MelBotStatic,'point':'TurretBottomRight'},
                            {'type':bs.MelBotStatic,'point':'TurretTopRight'},
                            {'type':bs.MelBotStatic,'point':'Left'},
                            ]},
                # 20 Boss 7
                {'entries':[
                            {'type':'delay','duration':4500},
                            {'type':bs.MelBotStatic,'point':'TurretTopMiddleLeft'},
                            {'type':bs.MelBotStatic,'point':'TurretTopMiddleRight'},
                            {'type':bs.LooieBot,'point':'Bottom'},
                            {'type':'delay','duration':8000},
                            {'type':bs.FrostyBotStatic,'point':'TurretBottomLeft'},
                            {'type':bs.FrostyBotStatic,'point':'TurretBottomRight'},
                            {'type':'delay','duration':125},
                            {'type':bs.ToughGuyBot,'point':'RightLowerMore'},
                            {'type':'delay','duration':600},
                            {'type':bs.ToughGuyBot,'point':'RightLower'},
                            {'type':'delay','duration':600},
                            {'type':bs.ToughGuyBot,'point':'Right'},
                            {'type':'delay','duration':600},
                            {'type':bs.ToughGuyBotPro,'point':'RightUpper'},
                            {'type':'delay','duration':600},
                            {'type':bs.ToughGuyBotPro,'point':'RightUpperMore'},
                            {'type':bs.ToughGuyBotProShielded,'point':'Right'} if playerCount > 1 else None,
                            {'type':bs.ToughGuyBotProShielded,'point':'RightLower'} if playerCount > 2 else None,
                            {'type':'delay','duration':4500},
                            {'type':bs.SpyBotPro,'point':'Left'},
                            {'type':bs.SpyBotPro,'point':'LeftUpper'},
                            {'type':bs.PuckBot,'point':'BottomLeft'},
                            {'type':bs.PuckBot,'point':'BottomHalfLeft'},
                            {'type':'delay','duration':8000},
                            {'type':bs.AgentBotShielded,'point':'Left'},
                            {'type':bs.AgentBotShielded,'point':'Right'},
                            {'type':bs.ChickBotProShielded,'point':'TopRight'},
                            {'type':bs.CyborgBotStatic,'point':'TurretBottomLeft'},
                            {'type':'delay','duration':19000},
                            {'type':bs.FrostyBotPro,'point':'Right'},
                            {'type':'delay','duration':1290},
                            {'type':bs.PixelBotPro,'point':'LeftUpperMore'},
                            {'type':'delay','duration':4500},
                            {'type':bs.ChickBotStatic,'point':'TurretTopMiddle'},
                            {'type':bs.SpyBotStatic,'point':'TurretTopMiddileLeft'},
                            {'type':'delay','duration':9381},
                            {'type':bs.WizardBot,'point':'TopRightEdge'},
                            {'type':bs.WizardBot,'point':'TopLeftEdge'},
                            {'type':'delay','duration':1200},
                            {'type':bs.PascalBotShielded,'point':'BottomRightEdge'},
                            {'type':bs.PixelBotPro,'point':'TopLeft'},
                            {'type':bs.BomberBotPro,'point':'BottomRight'},
                            {'type':'delay','duration':8000},
                            {'type':bs.AgentBotShielded,'point':'TopRight'},
                            {'type':bs.AgentBotShielded,'point':'TopLeft'},
                            {'type':bs.CyborgBotPro,'point':'Top'},
                            {'type':bs.MelBotStatic,'point':'TurretTopMiddle'},
                            {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                            {'type':bs.ChickBotPro,'point':'BottomHalfRight'},
                            {'type':bs.ChickBotPro,'point':'BottomHalfLeft'} if playerCount > 2 else None,
                            {'type':bs.AliBotPro,'point':'TopHalfRight'} if playerCount > 1 else None,
                            {'type':bs.MelBotStatic,'point':'TurretBottomRight'},
                            {'type':bs.LooieBotShielded,'point':'TurretTopLeft'},
                            {'type':bs.FrostyBotShielded,'point':'Right'},
                            {'type':Boss7Bot,'point':'Top'},
                            ]},
                ]
        self._dropPowerups(standardPoints=True,powerupType='shield')
        bs.gameTimer(4000,self._startPowerupDrops)
        if self._haveTnt:
            self._tntSpawner = bs.TNTSpawner(position=self._tntSpawnPosition)
        
        self.setupLowLifeWarningSound()
        
        self._updateScores()
        self._bots = bs.BotSet()

        bs.gameTimer(3500,self._startUpdatingWaves)


    def _onGotScoresToBeat(self,scores):
        self._showStandardScoresToBeatUI(scores)


    def _getDistribution(self,targetPoints,minDudes,maxDudes,groupCount,maxLevel):
        """ calculate a distribution of bad guys given some params """

        maxIterations = 10+maxDudes*2

        def _getTotals(groups):
            totalPoints = 0
            totalDudes = 0
            for group in groups:
                for entry in group:
                    dudes = entry[1]
                    totalPoints += entry[0]*dudes
                    totalDudes += dudes
            return totalPoints,totalDudes

        groups = []
        for g in range(groupCount):
            groups.append([])

        types = [1]
        if maxLevel > 1: types.append(2)
        if maxLevel > 2: types.append(3)
        if maxLevel > 3: types.append(4)

        for iteration in range(maxIterations):
            # see how much we're off our target by
            totalPoints,totalDudes = _getTotals(groups)
            diff = targetPoints - totalPoints
            dudesDiff = maxDudes - totalDudes
            # add an entry if one will fit
            value = types[random.randrange(len(types))]
            group = groups[random.randrange(len(groups))]
            if len(group) == 0: maxCount = random.randint(1,6)
            else: maxCount = 2*random.randint(1,3)
            maxCount = min(maxCount,dudesDiff)
            count = min(maxCount,diff/value)
            if count > 0:
                group.append((value,count))
                totalPoints += value*count
                totalDudes += count
                diff = targetPoints - totalPoints

            totalPoints,totalDudes = _getTotals(groups)
            full = (totalPoints >= targetPoints)

            if full:
                # every so often, delete a random entry just to shake up our distribution
                if random.random() < 0.2 and iteration != maxIterations-1:
                    entryCount = 0
                    for group in groups:
                        for entry in group:
                            entryCount += 1
                    if entryCount > 1:
                        delEntry = random.randrange(entryCount)
                        entryCount = 0
                        for group in groups:
                            for entry in group:
                                if entryCount == delEntry:
                                    group.remove(entry)
                                    break
                                entryCount += 1

                # if we don't have enough dudes, kill the group with the biggest point value
                elif totalDudes < minDudes and iteration != maxIterations-1:
                    biggestValue = 9999
                    biggestEntry = None
                    for group in groups:
                        for entry in group:
                            if entry[0] > biggestValue or biggestEntry is None:
                                biggestValue = entry[0]
                                biggestEntry = entry
                                biggestEntryGroup = group
                    if biggestEntry is not None: biggestEntryGroup.remove(biggestEntry)

                # if we've got too many dudes, kill the group with the smallest point value
                elif totalDudes > maxDudes and iteration != maxIterations-1:
                    smallestValue = 9999
                    smallestEntry = None
                    for group in groups:
                        for entry in group:
                            if entry[0] < smallestValue or smallestEntry is None:
                                smallestValue = entry[0]
                                smallestEntry = entry
                                smallestEntryGroup = group
                    smallestEntryGroup.remove(smallestEntry)

                # close enough.. we're done.
                else:
                    if diff == 0: break

        return groups


        
    def spawnPlayer(self,player):
        # we keep track of who got hurt each wave for score purposes
        player.gameData['hasBeenHurt'] = False
        pos = (self._spawnCenter[0]+random.uniform(-1.5,1.5),self._spawnCenter[1],self._spawnCenter[2]+random.uniform(-1.5,1.5))
        s = self.spawnPlayerSpaz(player,position=pos)
        s.impactScale = 1.00
        mat = self.getMap().preloadData['collideWithWallMaterial']
        s.node.materials += (mat,)
        s.node.rollerMaterials += (mat,)

    def _dropPowerup(self,index,powerupType=None):
        powerupType = bs.Powerup.getFactory().getRandomPowerupType(forceType=powerupType,excludeTypes=self._excludePowerups)
        bs.Powerup(position=self.getMap().powerupSpawnPoints[index],powerupType=powerupType).autoRetain()

    def _startPowerupDrops(self):
        import bsPowerup
        self._powerupDropTimer = bs.Timer(bsPowerup.coopPowerupDropRate,bs.WeakCall(self._dropPowerups),repeat=True)

    def _dropPowerups(self,standardPoints=False,powerupType=None):
        """ Generic powerup drop """

        if standardPoints:
            pts = self.getMap().powerupSpawnPoints
            for i,pt in enumerate(pts):
                bs.gameTimer(1000+i*500,bs.WeakCall(self._dropPowerup,i,powerupType if i == 0 else None))
        else:
            pt = (self._powerupCenter[0]+random.uniform(-1.0*self._powerupSpread[0],1.0*self._powerupSpread[0]),
                  self._powerupCenter[1],self._powerupCenter[2]+random.uniform(-self._powerupSpread[1],self._powerupSpread[1]))

            # drop one random one somewhere..
            bs.Powerup(position=pt,powerupType=bs.Powerup.getFactory().getRandomPowerupType(excludeTypes=self._excludePowerups)).autoRetain()

    def doEnd(self,outcome,delay=0):

        if outcome == 'defeat':
            self.fadeToRed()            

        if bs.getConfig()['Cheats Active'] == True:
            score = None
            failMessage = bs.Lstr(resource='cheaterText')
        elif self._wave >= 2:
            score = self._score
            failMessage = None
        else:
            score = None
            failMessage = bs.Lstr(resource='reachWave2Text')
        self.end({'outcome':outcome,'score':score,'failMessage':failMessage,'playerInfo':self.initialPlayerInfo},delay=delay)

    def _updateWaves(self):

        # if we have no living bots, go to the next wave
        if self._canEndWave and not self._bots.haveLivingBots() and not self._gameOver:

            self._canEndWave = False

            self._timeBonusTimer = None
            self._timeBonusText = None

            won = (self._wave == len(self._waves))

            # reward time bonus
            baseDelay = 4000 if won else 0

            if self._timeBonus > 0:
                bs.gameTimer(0,lambda: bs.playSound(self._cashRegisterSound))
                bs.gameTimer(baseDelay,bs.WeakCall(self._awardTimeBonus,self._timeBonus))
                baseDelay += 1000

            # reward flawless bonus
            if self._wave > 0:
                haveFlawless = False
                for player in self.players:
                    if player.isAlive() and player.gameData['hasBeenHurt'] == False:
                        haveFlawless = True
                        bs.gameTimer(baseDelay,bs.WeakCall(self._awardFlawlessBonus,player))
                    player.gameData['hasBeenHurt'] = False # reset
                if haveFlawless: baseDelay += 1000

            if won:
                import BuddyBunny
                for n in bs.getNodes():
                    if n.getNodeType() == 'spaz':
                        s = n.getDelegate()
                        if isinstance(s, BuddyBunny.BunnyBuddyBot):
                            if random.randint(1,3) == 1: s.node.handleMessage("celebrateR",20000)
                            elif random.randint(1,3) == 2: s.node.handleMessage("celebrateL",20000)
                            else: s.node.handleMessage("celebrate",20000)
                            bs.gameTimer(random.randint(60,350),bs.WeakCall(s.buddyAwesomeMoves),repeat=True)
                self.showZoomMessage(bs.Lstr(resource='survivedText'),scale=1.0,duration=4000)
        
                self.celebrate(20000)
                bs.gameTimer(baseDelay,bs.WeakCall(self._awardCompletionBonus))
                baseDelay += 1250
                bs.playSound(self._winSound)
                self.cameraFlash()
                self._gameOver = True

                # cant just pass delay to doEnd because our extra bonuses havnt been added yet
                # (once we call doEnd the score gets locked in)
                bs.gameTimer(baseDelay,bs.WeakCall(self.doEnd,'victory'))

                return

            self._wave += 1

            # short celebration after waves
            if self._wave > 1: self.celebrate(750)
                            
            bs.gameTimer(baseDelay,bs.WeakCall(self._startNextWave))

    def _awardCompletionBonus(self):
        bs.playSound(self._cashRegisterSound)
        for player in self.players:
            try:
                if player.isAlive():
                    self.scoreSet.playerScored(player,int(1000/len(self.initialPlayerInfo)),scale=1.4,color=(0.6,0.6,1.0,1.0),title=bs.Lstr(resource='completionBonusText'),screenMessage=False)
            except Exception,e:
                print 'EXC in _awardCompletionBonus',e
        
    def _awardTimeBonus(self,bonus):
        bs.playSound(self._cashRegisterSound)
        bs.PopupText(bs.Lstr(value='+${A} ${B}',subs=[('${A}',str(bonus)),('${B}',bs.Lstr(resource='timeBonusText'))]),
                     color=(1,1,0.5,1),
                     scale=1.0,
                     position=(0,3,-1)).autoRetain()
        self._score += self._timeBonus
        self._updateScores()

    def _awardFlawlessBonus(self,player):
        bs.playSound(self._cashRegisterSound)
        try:
            if player.isAlive():
                self.scoreSet.playerScored(player,self._flawlessBonus,scale=1.2,color=(0.6,1.0,0.6,1.0),title=bs.Lstr(resource='flawlessWaveText'),screenMessage=False)
        except Exception,e:
            print 'EXC in _awardFlawlessBonus',e
    
    def _startTimeBonusTimer(self):
        self._timeBonusTimer = bs.Timer(1000,bs.WeakCall(self._updateTimeBonus),repeat=True)
        
    def _updatePlayerSpawnInfo(self):

        # if we have no living players lets just blank this
        if not any(player.isAlive() for player in self.teams[0].players):
            self._spawnInfoText.node.text = ''
        else:
            t = ''
            for player in self.players:
                if not player.isAlive() and (player.gameData['respawnWave'] <= len(self._waves)):
                    t = bs.Lstr(value='${A}${B}\n',subs=[('${A}',t),('${B}',bs.Lstr(resource='onslaughtRespawnText',subs=[('${PLAYER}',player.getName()),('${WAVE}',str(player.gameData['respawnWave']))]))])
            self._spawnInfoText.node.text = t

    def _startNextWave(self):

        # this could happen if we beat a wave as we die..
        # we dont wanna respawn players and whatnot if this happens
        if self._gameOver: return
        
        # respawn applicable players
        if self._wave > 1 and not self.isWaitingForContinue():
            for player in self.players:
                if not player.isAlive() and player.gameData['respawnWave'] == self._wave:
                    self.spawnPlayer(player)

        self._updatePlayerSpawnInfo()

        self.showZoomMessage(bs.Lstr(value='${A} ${B}',subs=[('${A}',bs.Lstr(resource='waveText')),('${B}',str(self._wave))]),
                             scale=1.0,duration=1000,trail=True)
        bs.gameTimer(400,bs.Call(bs.playSound,self._newWaveSound))
        if self._wave == 4 or self._wave == 8 or self._wave == 12 or self._wave == 16:
            bs.gameTimer(400,bs.Call(bs.playSound,self._specialWaveSound))
        t = 0
        dt = 200
        botAngle = random.random()*360.0

        if self._wave == 1:
            spawnTime = 3973
            t += 500
        else:
            spawnTime = 2648

        #Wave Names
        if self._wave == 1:
            self._waveName = 'Tough Wall'
        elif self._wave == 2:
            self._waveName = 'Sticky Avalanche'
        elif self._wave == 3:
            self._waveName = 'Quad: Shadow Kill!'
        elif self._wave == 4:
            self._waveName = 'Blaster'
        elif self._wave == 5:
            self._waveName = 'Cracked Metal'
        elif self._wave == 6:
            self._waveName = 'Fats x Thins!'
        elif self._wave == 7:
            self._waveName = 'Invisible Agency'
        elif self._wave == 8:
            self._waveName = 'Electrix Boogalo'
        elif self._wave == 9:
            self._waveName = 'Bombardment!'
        elif self._wave == 10:
            self._waveName = 'Missing Punch'
        elif self._wave == 11:
            self._waveName = 'SS Agent Attack'
        elif self._wave == 12:
            self._waveName = 'Mixed Army'
        elif self._wave == 13:
            self._waveName = 'Giga Impacts'
        elif self._wave == 14:
            self._waveName = 'Sticky Situation'
        elif self._wave == 15:
            self._waveName = 'ERROR 404'
        elif self._wave == 16:
            self._waveName = 'A Terrible Chaos'
        elif self._wave == 17:
            self._waveName = 'Metalic Surge'
        elif self._wave == 18:
            self._waveName = 'Ugly And The Beast'
        elif self._wave == 19:
            self._waveName = 'Behind the Storm'
        elif self._wave == 20:
            self._waveName = 'FINAL WAVE!'
            values = {0: (1*1.6, 0, 0), 19000: (0, 1*1.6, 0),19000*2: (0, 0, 1*1.6), 19000*3: (1*1.6, 0, 0)}
            bs.shakeCamera(intensity=5.0)
            bs.playMusic('Flag Bomber')
            bs.getSharedObject('globals').tint = (0.5, 0.7, 1.0)
            try:
                bs.getActivity().getMap().node.reflection = 0
                bs.getActivity().getMap().node.reflectionScale = 2
            except:
                pass
            try:
                bs.getActivity().getMap().bg.reflection = 0
                bs.getActivity().getMap().bg.reflectionScale = 2
            except:
                pass
            try:
                bs.getActivity().getMap().floor.reflection = 0
                bs.getActivity().floor.reflectionScale = 2
            except:
                pass
            try:
                bs.getActivity().center.reflection = 0
                bs.getActivity().center.reflectionScale = 2
            except:
                pass
            #bs.animateArray(bs.getSharedObject('globals'), 'tint', 3,values, loop=True)
            values = {
                                0: (1*1.6, 0, 0), 6000: (0, 1*1.6, 0),
                                6000*2: (0, 0, 1*1.6), 6000*3: (1*1.6, 0, 0)
                            }
            bs.animateArray(
                                bs.getSharedObject('globals'), 'ambientColor',
                                3, values, loop=True)
            bs.screenMessage("be ready or...")
        else:
            self._waveName = 'Null'
        
        offs = 0 # debugging

        wave = self._waves[self._wave-1]


        entries = []

        try: botAngle = wave['baseAngle']
        except Exception: botAngle = 0

        entries += wave['entries']

        thisTimeBonus = 0
        thisFlawlessBonus = 0

        for info in entries:
            if info is None: continue

            botType = info['type']

            if botType == 'delay':
                spawnTime += info['duration']
                continue
            if botType is not None:
                thisTimeBonus += botType.pointsMult * 20
                thisFlawlessBonus += botType.pointsMult * 5
            # if its got a position, use that
            try: point = info['point']
            except Exception: point = None
            if point is not None:
                bs.gameTimer(t,bs.WeakCall(self.addBotAtPoint,point,botType,spawnTime))
                t += dt
            else:
                try: spacing = info['spacing']
                except Exception: spacing = 5.0
                botAngle += spacing*0.5
                if botType is not None:
                    bs.gameTimer(t,bs.WeakCall(self.addBotAtAngle,botAngle,botType,spawnTime))
                    t += dt
                botAngle += spacing*0.5
            
        # we can end the wave after all the spawning happens
        bs.gameTimer(t+spawnTime-dt+10,bs.WeakCall(self._setCanEndWave))

        # reset our time bonus
        self._timeBonus = thisTimeBonus
        self._flawlessBonus = thisFlawlessBonus
        vrMode = bs.getEnvironment()['vrMode']
        self._timeBonusText = bs.NodeActor(bs.newNode('text',
                                                      attrs={'vAttach':'top',
                                                             'hAttach':'center',
                                                             'hAlign':'center',
                                                             'vrDepth':-30,
                                                             'color':(0.1,1,0.1,1) if True else (1,1,0.5,1),
                                                             'shadow':1.0 if True else 0.5,
                                                             'flatness':1.0 if True else 0.5,
                                                             'position':(0,-80),
                                                             'scale':0.8 if True else 0.6,
                                                             'text':bs.Lstr(value='${A}: ${B}',subs=[('${A}',bs.Lstr(resource='timeBonusText')),('${B}',str(self._timeBonus))])}))
        
        bs.gameTimer(5000,bs.WeakCall(self._startTimeBonusTimer))
        self._waveText = bs.NodeActor(bs.newNode('text',
                                                 attrs={'vAttach':'top',
                                                        'hAttach':'center',
                                                        'hAlign':'center',
                                                        'vrDepth':-10,
                                                        'color':(1,1,1,1) if True else (0.7,0.7,0.7,1.0),
                                                        'shadow':1.0 if True else 0.7,
                                                        'flatness':1.0 if True else 0.5,
                                                        'position':(0,-40),
                                                        'scale':1.3 if True else 1.1,
                                                        'text':bs.Lstr(value='${A} ${B}',subs=[('${A}',bs.Lstr(resource='waveText')),('${B}',str(self._wave)+('/'+str(len(self._waves))))])}))
                                                        
        self._waveNameText = bs.NodeActor(bs.newNode('text',
                                                 attrs={'vAttach':'top',
                                                        'hAttach':'center',
                                                        'hAlign':'center',
                                                        'vrDepth':-10,
                                                        'color':(1,1,0,1) if True else (0.7,0.0,0.0,1.0),
                                                        'shadow':1.0 if True else 0.7,
                                                        'flatness':1.0 if True else 0.5,
                                                        'position':(0,-60),
                                                        'scale':1.0 if True else 0.8,
                                                        'text':self._waveName}))
                                                        

    def addBotAtPoint(self,point,spazType,spawnTime=1000):
        # dont add if the game has ended
        if self._gameOver: return
        pt = self.getMap().defs.points['botSpawn'+point]
        self._bots.spawnBot(spazType,pos=pt,spawnTime=spawnTime)
        
    def addBotAtAngle(self,angle,spazType,spawnTime=1000):

        # dont add if the game has ended
        if self._gameOver: return

        angleRadians = angle/57.2957795
        x = math.sin(angleRadians)*1.06
        z = math.cos(angleRadians)*1.06
        pt = (x/0.125,2.3,(z/0.2)-3.7)

        self._bots.spawnBot(spazType,pos=pt,spawnTime=spawnTime)

    def _updateTimeBonus(self):
        self._timeBonus = int(self._timeBonus * 0.93)
        if self._timeBonus > 0 and self._timeBonusText is not None:
            self._timeBonusText.node.text = bs.Lstr(value='${A}: ${B}',subs=[('${A}',bs.Lstr(resource='timeBonusText')),('${B}',str(self._timeBonus))])
        else: self._timeBonusText = None

    def _startUpdatingWaves(self):
        self._waveUpdateTimer = bs.Timer(2000,bs.WeakCall(self._updateWaves),repeat=True)
        
    def _updateScores(self):
        self._scoreBoard.setTeamValue(self.teams[0],self._score,maxScore=None)

        
    def handleMessage(self,m):

        if isinstance(m,bs.PlayerSpazHurtMessage):
            player = m.spaz.getPlayer()
            if player is None:
                bs.printError('FIXME: getPlayer() should no longer ever be returning None')
                return
            if not player.exists(): return
            player.gameData['hasBeenHurt'] = True
            self._aPlayerHasBeenHurt = True

        elif isinstance(m,bs.PlayerScoredMessage):
            self._score += m.score
            self._updateScores()

        elif isinstance(m,bs.PlayerSpazDeathMessage):
            self.__superHandleMessage(m) # augment standard behavior
            player = m.spaz.getPlayer()
            self._aPlayerHasBeenHurt = True
            # make note with the player when they can respawn
            if self._wave < 10: player.gameData['respawnWave'] = max(2,self._wave+1)
            elif self._wave < 15: player.gameData['respawnWave'] = max(2,self._wave+2)
            else: player.gameData['respawnWave'] = max(2,self._wave+3)
            bs.gameTimer(100,self._updatePlayerSpawnInfo)
            bs.gameTimer(100,self._checkRoundOver)

        elif isinstance(m,bs.SpazBotDeathMessage):
            pts,importance = m.badGuy.getDeathPoints(m.how)
            if m.killerPlayer is not None:
                try: target = m.badGuy.node.position
                except Exception: target = None
                try:
                    killerPlayer = m.killerPlayer
                    self.scoreSet.playerScored(killerPlayer,pts,target=target,kill=True,screenMessage=False,importance=importance)
                    bs.playSound(self._dingSound if importance == 1 else self._dingSoundHigh,volume=0.6)
                except Exception: pass
            # normally we pull scores from the score-set, but if there's no player lets be explicit..
            else: self._score += pts
            self._updateScores()
        else:
            self.__superHandleMessage(m)

    def _setCanEndWave(self):
        self._canEndWave = True

    def __superHandleMessage(self,m):
        super(JRMPBossBattle,self).handleMessage(m)

    def endGame(self):
        # tell our bots to celebrate just to rub it in
        self._bots.finalCelebrate()
        
        self._gameOver = True        
        self.doEnd('defeat',delay=2000)
        bs.playMusic('boo')

    def onContinue(self):
        for player in self.players:
            if not player.isAlive():
                self.spawnPlayer(player)
        
    def _checkRoundOver(self):
        """ see if the round is over in response to an event (player died, etc) """

        # if we already ended it doesn't matter
        if self.hasEnded(): return

        if not any(player.isAlive() for player in self.teams[0].players):
            # allow continuing after wave 1
            if self._wave > 1: self.continueOrEndGame()
            else: self.endGame()
            
class TowerMadness(bs.CoopGameActivity):

    @classmethod
    def getName(cls):
        return 'Tower Madness'

    @classmethod
    def getDescription(cls,sessionType):
        return "Kill all enemies"

    def __init__(self,settings={}):

        settings['map'] = 'Morning Coop'

        bs.CoopGameActivity.__init__(self,settings)

        # show messages when players die since it matters here..
        self.announcePlayerDeaths = True
        
        self._specialWaveSound = bs.getSound('nightmareSpecialWave')
        self._newWaveSound = bs.getSound('scoreHit01')
        self._winSound = bs.getSound("score")
        self._cashRegisterSound = bs.getSound('cashRegister')
        self._aPlayerHasBeenHurt = False

        # fixme - should use standard map defs..
        self._spawnCenter = (1.0, 3.6, -5.5)
        self._tntSpawnPosition = (0,-1.2,2.1)
        self._powerupCenter = (1.0438, 3.7, -6.5250)
        self._powerupSpread = (1.5,1.83)
        

    def onTransitionIn(self):

        bs.CoopGameActivity.onTransitionIn(self)
        self._spawnInfoText = bs.NodeActor(bs.newNode("text",
                                                      attrs={'position':(15,-130),
                                                             'hAttach':"left",
                                                             'vAttach':"top",
                                                             'scale':0.55,
                                                             'color':(0.3,0.8,0.3,1.0),
                                                             'text':''}))
        bs.playMusic('Flying')

        self._scoreBoard = bs.ScoreBoard(label=bs.Lstr(resource='scoreText'),scoreSplit=0.5)
        self._gameOver = False
        self._wave = 0
        self._canEndWave = True
        self._score = 0
        self._timeBonus = 0


    def onBegin(self):

        bs.CoopGameActivity.onBegin(self)
        playerCount = len(self.players)
        self._dingSound = bs.getSound('dingSmall')
        self._dingSoundHigh = bs.getSound('dingSmallHigh')
        
        import bsUtils
        bsUtils.ControlsHelpOverlay(delay=3000,lifespan=10000,bright=True).autoRetain()

        self._haveTnt = False
        self._excludePowerups = ['curse','landMines','knockerBombs','dizzyCake','clusterBomb','bunny','speed']
        self._waves = [
                {'entries':[
                            {'type':bs.BomberBot},
                            {'type':bs.ToughGuyBot},
                            {'type':bs.ToughGuyBot} if playerCount > 1 else None,
                            ]},
                {'entries':[
                            {'type':bs.CowBot},
                            {'type':bs.MelDuperBot} if playerCount > 2 else None,
                            {'type':bs.CyborgBot},
                            ]},
                {'entries':[
                            {'type':bs.DiceBot},
                            {'type':bs.SpyBot},
                            {'type':bs.BomberBot} if playerCount > 3 else None,
                            {'type':bs.NinjaBot} if playerCount > 1 else None,
                            ]},
                {'entries':[
                            {'type':bs.ToughGuyBot},
                            {'type':bs.ChickBot},
                            {'type':bs.ChickBotPro} if playerCount > 1 else None,
                            ]},
                {'entries':[
                            {'type':bs.LooieBot},
                            {'type':bs.LooieBot} if playerCount > 2 else None,
                            {'type':bs.BonesBot},
                            {'type':'delay','duration':450},
                            {'type':bs.NinjaBot} if playerCount > 1 else None,
                            ]},
                {'entries':[
                            {'type':bs.MelBot},
                            {'type':bs.MelBot},
                            {'type':'delay','duration':1500},
                            {'type':bs.ChickBot},
                            ]},
                {'entries':[
                            {'type':bs.FrostyBot},
                            {'type':bs.PascalBot},
                            {'type':bs.NinjaBot} if playerCount > 1 else None,
                            {'type':bs.NinjaBot} if playerCount > 2 else None,
                            ]},
                {'entries':[
                            {'type':bs.AgentBot},
                            {'type':bs.BomberBot},
                            {'type':'delay','duration':990},
                            {'type':bs.BomberBot},
                            {'type':bs.AgentBotPro} if playerCount > 3 else None,
                            ]},
                {'entries':[
                            {'type':bs.NinjaBot},
                            {'type':'delay','duration':2350},
                            {'type':bs.BearBot},
                            {'type':bs.DemonBot} if playerCount > 2 else None,
                            {'type':'delay','duration':1022},
                            {'type':bs.ToughGuyBot} if playerCount > 1 else None,
                            {'type':bs.MelBot},
                            ]},
                {'entries':[
                            {'type':bs.WizardBot},
                            {'type':bs.ChickBot},
                            {'type':bs.WizardBot},
                            {'type':'delay','duration':2256},
                            {'type':bs.LooieBotShielded} if playerCount > 2 else None,
                            ]},
                {'entries':[
                            {'type':bs.AliBot},
                            {'type':bs.AliBot},
                            {'type':'delay','duration':567},
                            {'type':bs.BomberBot},
                            {'type':'delay','duration':345},
                            {'type':bs.ChickBot} if playerCount > 1 else None,
                            {'type':bs.AliBot},
                            ]},
                {'entries':[
                            {'type':bs.ChickBot},
                            {'type':bs.CyborgBot},
                            {'type':'delay','duration':3000},
                            {'type':bs.ChickBot},
                            {'type':'delay','duration':3000},
                            {'type':bs.BunnyBot},
                            ]},
                {'entries':[
                            {'type':bs.CyborgBot},
                            {'type':'delay','duration':1886},
                            {'type':bs.MelBot},
                            {'type':bs.MelBot},
                            {'type':'delay','duration':2680},
                            {'type':bs.LooieBot},
                            ]},
                {'entries':[
                            {'type':bs.CowBot},
                            {'type':bs.FrostyBot},
                            {'type':'delay','duration':1729},
                            {'type':bs.SpyBot},
                            {'type':bs.SpyBot},
                            ]},
                {'entries':[
                            {'type':bs.AgentBot},
                            {'type':'delay','duration':2000},
                            {'type':bs.ToughGuyBot},
                            {'type':bs.MelBot},
                            {'type':'delay','duration':2000},
                            {'type':bs.RonnieBot},
                            {'type':bs.WizardBot},
                            {'type':bs.WizardBot},
                            ]},
                ]
        self._dropPowerups(standardPoints=True)
        bs.gameTimer(4000,self._startPowerupDrops)
        if self._haveTnt:
            self._tntSpawner = bs.TNTSpawner(position=self._tntSpawnPosition)
        
        self.setupLowLifeWarningSound()
        
        self._updateScores()
        self._bots = bs.BotSet()

        bs.gameTimer(3500,self._startUpdatingWaves)


    def _onGotScoresToBeat(self,scores):
        self._showStandardScoresToBeatUI(scores)


    def _getDistribution(self,targetPoints,minDudes,maxDudes,groupCount,maxLevel):
        """ calculate a distribution of bad guys given some params """

        maxIterations = 10+maxDudes*2

        def _getTotals(groups):
            totalPoints = 0
            totalDudes = 0
            for group in groups:
                for entry in group:
                    dudes = entry[1]
                    totalPoints += entry[0]*dudes
                    totalDudes += dudes
            return totalPoints,totalDudes

        groups = []
        for g in range(groupCount):
            groups.append([])

        types = [1]
        if maxLevel > 1: types.append(2)
        if maxLevel > 2: types.append(3)
        if maxLevel > 3: types.append(4)

        for iteration in range(maxIterations):
            # see how much we're off our target by
            totalPoints,totalDudes = _getTotals(groups)
            diff = targetPoints - totalPoints
            dudesDiff = maxDudes - totalDudes
            # add an entry if one will fit
            value = types[random.randrange(len(types))]
            group = groups[random.randrange(len(groups))]
            if len(group) == 0: maxCount = random.randint(1,6)
            else: maxCount = 2*random.randint(1,3)
            maxCount = min(maxCount,dudesDiff)
            count = min(maxCount,diff/value)
            if count > 0:
                group.append((value,count))
                totalPoints += value*count
                totalDudes += count
                diff = targetPoints - totalPoints

            totalPoints,totalDudes = _getTotals(groups)
            full = (totalPoints >= targetPoints)

            if full:
                # every so often, delete a random entry just to shake up our distribution
                if random.random() < 0.2 and iteration != maxIterations-1:
                    entryCount = 0
                    for group in groups:
                        for entry in group:
                            entryCount += 1
                    if entryCount > 1:
                        delEntry = random.randrange(entryCount)
                        entryCount = 0
                        for group in groups:
                            for entry in group:
                                if entryCount == delEntry:
                                    group.remove(entry)
                                    break
                                entryCount += 1

                # if we don't have enough dudes, kill the group with the biggest point value
                elif totalDudes < minDudes and iteration != maxIterations-1:
                    biggestValue = 9999
                    biggestEntry = None
                    for group in groups:
                        for entry in group:
                            if entry[0] > biggestValue or biggestEntry is None:
                                biggestValue = entry[0]
                                biggestEntry = entry
                                biggestEntryGroup = group
                    if biggestEntry is not None: biggestEntryGroup.remove(biggestEntry)

                # if we've got too many dudes, kill the group with the smallest point value
                elif totalDudes > maxDudes and iteration != maxIterations-1:
                    smallestValue = 9999
                    smallestEntry = None
                    for group in groups:
                        for entry in group:
                            if entry[0] < smallestValue or smallestEntry is None:
                                smallestValue = entry[0]
                                smallestEntry = entry
                                smallestEntryGroup = group
                    smallestEntryGroup.remove(smallestEntry)

                # close enough.. we're done.
                else:
                    if diff == 0: break

        return groups


        
    def spawnPlayer(self,player):
        # we keep track of who got hurt each wave for score purposes
        player.gameData['hasBeenHurt'] = False
        pos = (self._spawnCenter[0]+random.uniform(-1.5,1.5),self._spawnCenter[1],self._spawnCenter[2]+random.uniform(-1.5,1.5))
        s = self.spawnPlayerSpaz(player,position=pos)
        s.impactScale = 1.00

    def _dropPowerup(self,index,powerupType=None):
        powerupType = bs.Powerup.getFactory().getRandomPowerupType(excludeTypes=self._excludePowerups,forceType=powerupType)
        bs.Powerup(position=self.getMap().powerupSpawnPoints[index],powerupType=powerupType).autoRetain()

    def _startPowerupDrops(self):
        import bsPowerup
        self._powerupDropTimer = bs.Timer(bsPowerup.coopPowerupDropRate,bs.WeakCall(self._dropPowerups),repeat=True)

    def _dropPowerups(self,standardPoints=False,powerupType=None):
        """ Generic powerup drop """

        if standardPoints:
            pts = self.getMap().powerupSpawnPoints
            for i,pt in enumerate(pts):
                bs.gameTimer(1000+i*500,bs.WeakCall(self._dropPowerup,i,powerupType if i == 0 else None))
        else:
            pt = (self._powerupCenter[0]+random.uniform(-1.0*self._powerupSpread[0],1.0*self._powerupSpread[0]),
                  self._powerupCenter[1],self._powerupCenter[2]+random.uniform(-self._powerupSpread[1],self._powerupSpread[1]))

            # drop one random one somewhere..
            bs.Powerup(position=pt,powerupType=bs.Powerup.getFactory().getRandomPowerupType(excludeTypes=self._excludePowerups)).autoRetain()

    def doEnd(self,outcome,delay=0):

        if outcome == 'defeat':
            self.fadeToRed()

        if self._wave >= 2:
            score = self._score
            failMessage = None
        else:
            score = None
            failMessage = bs.Lstr(resource='reachWave2Text')
        self.end({'outcome':outcome,'score':score,'failMessage':failMessage,'playerInfo':self.initialPlayerInfo},delay=delay)

    def _updateWaves(self):

        # if we have no living bots, go to the next wave
        if self._canEndWave and not self._bots.haveLivingBots() and not self._gameOver:

            self._canEndWave = False

            self._timeBonusTimer = None
            self._timeBonusText = None

            won = (self._wave == len(self._waves))

            # reward time bonus
            baseDelay = 4000 if won else 0

            if self._timeBonus > 0:
                bs.gameTimer(0,lambda: bs.playSound(self._cashRegisterSound))
                bs.gameTimer(baseDelay,bs.WeakCall(self._awardTimeBonus,self._timeBonus))
                baseDelay += 1000

            # reward flawless bonus
            if self._wave > 0:
                haveFlawless = False
                for player in self.players:
                    if player.isAlive() and player.gameData['hasBeenHurt'] == False:
                        haveFlawless = True
                        bs.gameTimer(baseDelay,bs.WeakCall(self._awardFlawlessBonus,player))
                    player.gameData['hasBeenHurt'] = False # reset
                if haveFlawless: baseDelay += 1000

            if won:

                self.showZoomMessage(bs.Lstr(resource='victoryText'),scale=1.0,duration=4000)

                self.celebrate(20000)

                bs.gameTimer(baseDelay,bs.WeakCall(self._awardCompletionBonus))
                baseDelay += 850
                bs.playSound(self._winSound)
                self.cameraFlash()
                bs.playMusic('Victory')
                self._gameOver = True
                bs.gameTimer(baseDelay,bs.WeakCall(self.doEnd,'victory'))

                return

            self._wave += 1
            if self._wave > 1: self.celebrate(750)
                            
            bs.gameTimer(baseDelay,bs.WeakCall(self._startNextWave))

    def _awardCompletionBonus(self):
        bs.playSound(self._cashRegisterSound)
        for player in self.players:
            try:
                if player.isAlive():
                    self.scoreSet.playerScored(player,int(100/len(self.initialPlayerInfo)),scale=1.4,color=(0.6,0.6,1.0,1.0),title=bs.Lstr(resource='completionBonusText'),screenMessage=False)
            except Exception,e:
                print 'EXC in _awardCompletionBonus',e
        
    def _awardTimeBonus(self,bonus):
        bs.playSound(self._cashRegisterSound)
        bs.PopupText(bs.Lstr(value='+${A} ${B}',subs=[('${A}',str(bonus)),('${B}',bs.Lstr(resource='timeBonusText'))]),
                     color=(1,1,0.5,1),
                     scale=1.0,
                     position=(0,3,-1)).autoRetain()
        self._score += self._timeBonus
        self._updateScores()

    def _awardFlawlessBonus(self,player):
        bs.playSound(self._cashRegisterSound)
        try:
            if player.isAlive():
                self.scoreSet.playerScored(player,self._flawlessBonus,scale=1.2,color=(0.6,1.0,0.6,1.0),title=bs.Lstr(resource='flawlessWaveText'),screenMessage=False)
        except Exception,e:
            print 'EXC in _awardFlawlessBonus',e
    
    def _startTimeBonusTimer(self):
        self._timeBonusTimer = bs.Timer(1000,bs.WeakCall(self._updateTimeBonus),repeat=True)
        
    def _updatePlayerSpawnInfo(self):

        # if we have no living players lets just blank this
        if not any(player.isAlive() for player in self.teams[0].players):
            self._spawnInfoText.node.text = ''
        else:
            t = ''
            for player in self.players:
                if not player.isAlive() and (player.gameData['respawnWave'] <= len(self._waves)):
                    t = bs.Lstr(value='${A}${B}\n',subs=[('${A}',t),('${B}',bs.Lstr(resource='onslaughtRespawnText',subs=[('${PLAYER}',player.getName()),('${WAVE}',str(player.gameData['respawnWave']))]))])
            self._spawnInfoText.node.text = t

    def _startNextWave(self):

        # this could happen if we beat a wave as we die..
        # we dont wanna respawn players and whatnot if this happens
        if self._gameOver: return
        # lets loop through series of available locations to
        #spawn at, without occupying the same location.
        	
        
        # respawn applicable players
        if self._wave > 1 and not self.isWaitingForContinue():
            for player in self.players:
                if not player.isAlive() and player.gameData['respawnWave'] == self._wave:
                    self.spawnPlayer(player)

        self._updatePlayerSpawnInfo()

        self.showZoomMessage(bs.Lstr(value='${A} ${B}',subs=[('${A}',bs.Lstr(resource='waveText')),('${B}',str(self._wave))]),
                             scale=1.0,duration=1000,trail=True)
        bs.gameTimer(400,bs.Call(bs.playSound,self._newWaveSound))
        t = 0
        dt = 200
        botAngle = random.random()*360.0

        if self._wave == 1:
            spawnTime = 3973
            t += 500
        else:
            spawnTime = 2648

        offs = 0 # debugging

        wave = self._waves[self._wave-1]


        entries = []

        try: botAngle = wave['baseAngle']
        except Exception: botAngle = 0

        entries += wave['entries']

        thisTimeBonus = 0
        thisFlawlessBonus = 0
        
        self.rand_loc = ['TowerDown','TowerRight','TowerTop','TowerLeft','TowerUp','TowerUpLeft','TowerUpRight','TowerDownLeft','TowerDownRight']

        for info in entries:
            if info is None: continue

            botType = info['type']

            if botType == 'delay':
                spawnTime += info['duration']
                continue
            if botType is not None:
                thisTimeBonus += botType.pointsMult * 12
                thisFlawlessBonus += botType.pointsMult * 5
            
            pos = random.choice(self.rand_loc)
            bs.gameTimer(t,bs.WeakCall(self.addBotAtPoint,
            pos,botType,spawnTime))
            t += dt
            self.rand_loc.remove(pos)
            	
            
        # we can end the wave after all the spawning happens
        bs.gameTimer(t+spawnTime-dt+10,bs.WeakCall(self._setCanEndWave))

        # reset our time bonus
        self._timeBonus = thisTimeBonus
        self._flawlessBonus = thisFlawlessBonus
        vrMode = bs.getEnvironment()['vrMode']
        self._timeBonusText = bs.NodeActor(bs.newNode('text',
                                                      attrs={'vAttach':'top',
                                                             'hAttach':'center',
                                                             'hAlign':'center',
                                                             'vrDepth':-30,
                                                             'color':(1,1,0,1) if True else (1,1,0.5,1),
                                                             'shadow':1.0 if True else 0.5,
                                                             'flatness':1.0 if True else 0.5,
                                                             'position':(5,-60),
                                                             'scale':0.8 if True else 0.6,
                                                             'text':bs.Lstr(value='${A}: ${B}',subs=[('${A}',bs.Lstr(resource='timeBonusText')),('${B}',str(self._timeBonus))])}))
        
        bs.gameTimer(5000,bs.WeakCall(self._startTimeBonusTimer))
        self._waveText = bs.NodeActor(bs.newNode('text',
                                                 attrs={'vAttach':'top',
                                                        'hAttach':'center',
                                                        'hAlign':'center',
                                                        'vrDepth':-10,
                                                        'color':(1,1,1,1) if True else (0.7,0.7,0.7,1.0),
                                                        'shadow':1.0 if True else 0.7,
                                                        'flatness':1.0 if True else 0.5,
                                                        'position':(0,-40),
                                                        'scale':1.3 if True else 1.1,
                                                        'text':bs.Lstr(value='${A} ${B}',subs=[('${A}',bs.Lstr(resource='waveText')),('${B}',str(self._wave)+'/'+str(len(self._waves)))])}))
                                                        
    def addBotAtPoint(self,point,spazType,spawnTime=1000):
        # dont add if the game has ended
        if self._gameOver: return
        pt = self.getMap().defs.points['botSpawn'+point]
        self._bots.spawnBot(spazType,pos=pt,spawnTime=spawnTime)
        
    def addBotAtAngle(self,angle,spazType,spawnTime=1000):

        # dont add if the game has ended
        if self._gameOver: return

        angleRadians = angle/57.2957795
        x = math.sin(angleRadians)*1.06
        z = math.cos(angleRadians)*1.06
        pt = (x/0.125,2.3,(z/0.2)-3.7)

        self._bots.spawnBot(spazType,pos=pt,spawnTime=spawnTime)

    def _updateTimeBonus(self):
        self._timeBonus = int(self._timeBonus * 0.93)
        if self._timeBonus > 0 and self._timeBonusText is not None:
            self._timeBonusText.node.text = bs.Lstr(value='${A}: ${B}',subs=[('${A}',bs.Lstr(resource='timeBonusText')),('${B}',str(self._timeBonus))])
        else: self._timeBonusText = None

    def _startUpdatingWaves(self):
        self._waveUpdateTimer = bs.Timer(2000,bs.WeakCall(self._updateWaves),repeat=True)
        
    def _updateScores(self):
        self._scoreBoard.setTeamValue(self.teams[0],self._score,maxScore=None)

        
    def handleMessage(self,m):

        if isinstance(m,bs.PlayerSpazHurtMessage):
            player = m.spaz.getPlayer()
            if player is None:
                bs.printError('FIXME: getPlayer() should no longer ever be returning None')
                return
            if not player.exists(): return
            player.gameData['hasBeenHurt'] = True
            self._aPlayerHasBeenHurt = True

        elif isinstance(m,bs.PlayerScoredMessage):
            self._score += m.score
            self._updateScores()

        elif isinstance(m,bs.PlayerSpazDeathMessage):
            self.__superHandleMessage(m) # augment standard behavior
            player = m.spaz.getPlayer()
            self._aPlayerHasBeenHurt = True
            # make note with the player when they can respawn
            player.gameData['respawnWave'] = max(2,self._wave+1)
            bs.gameTimer(100,self._updatePlayerSpawnInfo)
            bs.gameTimer(100,self._checkRoundOver)

        elif isinstance(m,bs.SpazBotDeathMessage):
            pts,importance = m.badGuy.getDeathPoints(m.how)
            if m.killerPlayer is not None:
                try: target = m.badGuy.node.position
                except Exception: target = None
                try:
                    killerPlayer = m.killerPlayer
                    self.scoreSet.playerScored(killerPlayer,pts,target=target,kill=True,screenMessage=False,importance=importance)
                    bs.playSound(self._dingSound if importance == 1 else self._dingSoundHigh,volume=0.6)
                except Exception: pass
            # normally we pull scores from the score-set, but if there's no player lets be explicit..
            else: self._score += pts
            self._updateScores()
        else:
            self.__superHandleMessage(m)

    def _setCanEndWave(self):
        self._canEndWave = True

    def __superHandleMessage(self,m):
        super(TowerMadness,self).handleMessage(m)

    def endGame(self):
        # tell our bots to celebrate just to rub it in
        self._bots.finalCelebrate()
        
        self._gameOver = True
        self.doEnd('defeat',delay=2000)

    def onContinue(self):
        for player in self.players:
            if not player.isAlive():
                self.spawnPlayer(player)
        
    def _checkRoundOver(self):
        """ see if the round is over in response to an event (player died, etc) """

        # if we already ended it doesn't matter
        if self.hasEnded(): return

        if not any(player.isAlive() for player in self.teams[0].players):
            # allow continuing after wave 1
            if self._wave > 1: self.continueOrEndGame()
            else: self.endGame()
            
class NightMarathonGame(bs.CoopGameActivity):



    @classmethod
    def getName(cls):
        return 'Summer Nights'

    @classmethod
    def getDescription(cls,sessionType):
        return "Survive till end!"

    def __init__(self,settings={}):

        settings['map'] = 'Flapland Night'

        bs.CoopGameActivity.__init__(self,settings)

        # show messages when players die since it matters here..
        self.announcePlayerDeaths = True
        
        self._newWaveSound = bs.getSound('scoreHit01')
        self._winSound = bs.getSound("score")
        self._cashRegisterSound = bs.getSound('cashRegister')
        self._aPlayerHasBeenHurt = False

        # fixme - should use standard map defs..
        self._spawnCenter = (0,3,-5)
        self._powerupCenter = (0,3,-5)
        self._powerupSpread = (2.5,1.5)
            

    def onTransitionIn(self):

        bs.CoopGameActivity.onTransitionIn(self)
        self._spawnInfoText = bs.NodeActor(bs.newNode("text",
                                                      attrs={'position':(15,-130),
                                                             'hAttach':"left",
                                                             'vAttach':"top",
                                                             'scale':0.55,
                                                             'color':(0.3,0.8,0.3,1.0),
                                                             'text':''}))
        bs.playMusic('Marching')

        self._scoreBoard = bs.ScoreBoard(label=bs.Lstr(resource='scoreText'),scoreSplit=0.5)
        self._gameOver = False
        self._wave = 0
        self._canEndWave = True
        self._score = 0
        self._timeBonus = 0


    def onBegin(self):

        bs.CoopGameActivity.onBegin(self)
        playerCount = len(self.players)
        self._dingSound = bs.getSound('dingSmall')
        self._dingSoundHigh = bs.getSound('dingSmallHigh')
        
        import bsUtils
        bsUtils.ControlsHelpOverlay(delay=3000,lifespan=10000,bright=True).autoRetain()

        self._haveTnt = False
        self._excludePowerups = []
        self._waves = [
                # 1
                {'entries':([
                            {'type':bs.ToughGuyBot,'spacing':50},
                            ] * playerCount)},
                # 2             
                {'entries':([
                            {'type':bs.BomberBot,'spacing':50},
                            ] * playerCount)},
                # 3
                {'entries':([
                            {'type':bs.NinjaBot,'spacing':50},
                            ] * playerCount)},
                # 4
                {'entries':([
                            {'type':bs.ChickBot,'spacing':50},
                            ] * playerCount)},
                # 5
                {'entries':([
                            {'type':bs.ToughGuyBot,'spacing':50},
                            {'type':bs.BomberBot,'spacing':50},
                            ] * playerCount)},
                # 6
                {'entries':([
                            {'type':bs.ToughGuyBot,'spacing':100},
                            ] * playerCount * 2)},
                # 7
                {'entries':([
                            {'type':bs.BomberBot,'spacing':100},
                            ] * playerCount * 2)},
                # 8
                {'entries':([
                            {'type':bs.LooieBot,'spacing':50},
                            ] * playerCount)},
                # 9
                {'entries':([
                            {'type':bs.BearBot,'spacing':50},
                            {'type':bs.BomberBot,'spacing':50},
                            ] * playerCount)},  
                # 10
                {'entries':([
                            {'type':bs.BomberBot,'spacing':50},
                            {'type':bs.LooieBot,'spacing':50},
                            ] * playerCount)},
                # 11
                {'entries':([
                            {'type':bs.MelBot,'spacing':50},
                            {'type':bs.ToughGuyBot,'spacing':50},
                            ] * playerCount)},
                # 12
                {'entries':([
                            {'type':bs.NinjaBot,'spacing':50},
                            {'type':bs.SpyBot,'spacing':50},
                            ] * playerCount)},
                # 13
                {'entries':([
                            {'type':bs.BomberBotPro,'spacing':50},
                            ] * playerCount)},
                # 14
                {'entries':([
                            {'type':bs.NinjaBot,'spacing':50},
                            {'type':bs.ChickBot,'spacing':50},
                            ] * playerCount)},
                # 15
                {'entries':([
                            {'type':bs.BonesBot,'spacing':50},
                            {'type':bs.BearBot,'spacing':50},
                            ] * playerCount)},
                # 16
                {'entries':([
                            {'type':bs.CyborgBot,'spacing':50},
                            {'type':bs.ZillBot,'spacing':50},
                            ] * playerCount)},
                # 17
                {'entries':([
                            {'type':bs.BomberBot,'spacing':50},
                            {'type':bs.ToughGuyBot,'spacing':50},
                            {'type':bs.LooieBot,'spacing':50},
                            ] * playerCount)}, 
                # 18
                {'entries':([
                            {'type':bs.ChickBot,'spacing':50},
                            {'type':bs.LooieBotShielded,'spacing':50},
                            ] * playerCount)},   
                # 19
                {'entries':([
                            {'type':bs.ZillBot,'spacing':50},
                            {'type':bs.WizardBot,'spacing':50},
                            ] * playerCount)},  
                # 20
                {'entries':([
                            {'type':bs.SpyBot,'spacing':50},
                            {'type':bs.LooieBot,'spacing':50},
                            ] * playerCount)},
                # 21
                {'entries':([
                            {'type':bs.WizardBot,'spacing':50},
                            {'type':bs.PixelBot,'spacing':50},
                            ] * playerCount)},
                # 22          
                {'entries':([
                            {'type':bs.ToughGuyBotPro,'spacing':50},
                            {'type':bs.RonnieBot,'spacing':50},
                            ] * playerCount)},
                # 23
                {'entries':([
                            {'type':bs.FrostyBot,'spacing':50},
                            {'type':bs.NinjaBot,'spacing':50},
                            {'type':bs.BomberBot,'spacing':50},
                            ] * playerCount)},
                # 24
                {'entries':([
                            {'type':bs.PascalBot,'spacing':50},
                            {'type':bs.FrostyBot,'spacing':50},
                            ] * playerCount)},
                # 25
                {'entries':([
                            {'type':bs.AliBot,'spacing':50},
                            {'type':bs.BomberBot,'spacing':50},
                            {'type':bs.BomberBot,'spacing':50},
                            ] * playerCount)},
                # 26
                {'entries':([
                            {'type':bs.CyborgBotPro,'spacing':50},
                            {'type':bs.AgentBotShielded,'spacing':50},
                            ] * playerCount)},
                # 27
                {'entries':([
                            {'type':bs.LooieBotShielded,'spacing':50},
                            {'type':bs.JuiceBot,'spacing':50},
                            ] * playerCount)},
                # 28
                {'entries':([
                            {'type':bs.ChickBotProShielded,'spacing':50},
                            {'type':bs.NinjaBotProShielded,'spacing':50},
                            ] * playerCount)},
                # 29
                {'entries':([
                            {'type':bs.PascalBotShielded,'spacing':50},
                            {'type':bs.MelDuperBot,'spacing':50},
                            ] * playerCount)},  
                # 30
                {'entries':([
                            {'type':bs.BomberBotProShielded,'spacing':50},
                            {'type':bs.LooieBot,'spacing':50},
                            {'type':bs.LooieBot,'spacing':50},
                            ] * playerCount)},
                # 31
                {'entries':([
                            {'type':bs.BomberBotProShielded,'spacing':50},
                            {'type':bs.PirateBotShielded,'spacing':50},
                            {'type':bs.NinjaBotProShielded,'spacing':50},
                            ] * playerCount)},
                # 32
                {'entries':([
                            {'type':bs.CyborgBotPro,'spacing':50},
                            {'type':bs.AgentBotShielded,'spacing':50},
                            {'type':bs.FrostyBotShielded,'spacing':50},
                            ] * playerCount)},                                  
                ]
        self._dropPowerups(standardPoints=True)
        bs.gameTimer(4000,self._startPowerupDrops)
        
        self.setupLowLifeWarningSound()
        
        self._updateScores()
        self._bots = bs.BotSet()

        bs.gameTimer(1000,self._startUpdatingWaves)


    def _onGotScoresToBeat(self,scores):
        self._showStandardScoresToBeatUI(scores)


    def _getDistribution(self,targetPoints,minDudes,maxDudes,groupCount,maxLevel):
        """ calculate a distribution of bad guys given some params """

        maxIterations = 10+maxDudes*2

        def _getTotals(groups):
            totalPoints = 0
            totalDudes = 0
            for group in groups:
                for entry in group:
                    dudes = entry[1]
                    totalPoints += entry[0]*dudes
                    totalDudes += dudes
            return totalPoints,totalDudes

        groups = []
        for g in range(groupCount):
            groups.append([])

        types = [1]
        if maxLevel > 1: types.append(2)
        if maxLevel > 2: types.append(3)
        if maxLevel > 3: types.append(4)

        for iteration in range(maxIterations):
            # see how much we're off our target by
            totalPoints,totalDudes = _getTotals(groups)
            diff = targetPoints - totalPoints
            dudesDiff = maxDudes - totalDudes
            # add an entry if one will fit
            value = types[random.randrange(len(types))]
            group = groups[random.randrange(len(groups))]
            if len(group) == 0: maxCount = random.randint(1,6)
            else: maxCount = 2*random.randint(1,3)
            maxCount = min(maxCount,dudesDiff)
            count = min(maxCount,diff/value)
            if count > 0:
                group.append((value,count))
                totalPoints += value*count
                totalDudes += count
                diff = targetPoints - totalPoints

            totalPoints,totalDudes = _getTotals(groups)
            full = (totalPoints >= targetPoints)

            if full:
                # every so often, delete a random entry just to shake up our distribution
                if random.random() < 0.2 and iteration != maxIterations-1:
                    entryCount = 0
                    for group in groups:
                        for entry in group:
                            entryCount += 1
                    if entryCount > 1:
                        delEntry = random.randrange(entryCount)
                        entryCount = 0
                        for group in groups:
                            for entry in group:
                                if entryCount == delEntry:
                                    group.remove(entry)
                                    break
                                entryCount += 1

                # if we don't have enough dudes, kill the group with the biggest point value
                elif totalDudes < minDudes and iteration != maxIterations-1:
                    biggestValue = 9999
                    biggestEntry = None
                    for group in groups:
                        for entry in group:
                            if entry[0] > biggestValue or biggestEntry is None:
                                biggestValue = entry[0]
                                biggestEntry = entry
                                biggestEntryGroup = group
                    if biggestEntry is not None: biggestEntryGroup.remove(biggestEntry)

                # if we've got too many dudes, kill the group with the smallest point value
                elif totalDudes > maxDudes and iteration != maxIterations-1:
                    smallestValue = 9999
                    smallestEntry = None
                    for group in groups:
                        for entry in group:
                            if entry[0] < smallestValue or smallestEntry is None:
                                smallestValue = entry[0]
                                smallestEntry = entry
                                smallestEntryGroup = group
                    smallestEntryGroup.remove(smallestEntry)

                # close enough.. we're done.
                else:
                    if diff == 0: break

        return groups


        
    def spawnPlayer(self,player):
        # we keep track of who got hurt each wave for score purposes
        player.gameData['hasBeenHurt'] = False
        pos = (self._spawnCenter[0]+random.uniform(-0.5,0.5),self._spawnCenter[1],self._spawnCenter[2]+random.uniform(-0.5,0.5))
        s = self.spawnPlayerSpaz(player,position=pos)
        s.impactScale = 1.00
        
    def _dropPowerup(self,index,powerupType=None):
        powerupType = bs.Powerup.getFactory().getRandomPowerupType(forceType=powerupType)
        bs.Powerup(position=self.getMap().powerupSpawnPoints[index],powerupType=powerupType).autoRetain()

    def _startPowerupDrops(self):
        import bsPowerup
        self._powerupDropTimer = bs.Timer(bsPowerup.coopPowerupDropRate,bs.WeakCall(self._dropPowerups),repeat=True)

    def _dropPowerups(self,standardPoints=False,powerupType=None):
        """ Generic powerup drop """

        if standardPoints:
            pts = self.getMap().powerupSpawnPoints
            for i,pt in enumerate(pts):
                bs.gameTimer(1000+i*500,bs.WeakCall(self._dropPowerup,i,powerupType if i == 0 else None))
        else:
            pt = (self._powerupCenter[0]+random.uniform(-1.0*self._powerupSpread[0],1.0*self._powerupSpread[0]),
                  self._powerupCenter[1],self._powerupCenter[2]+random.uniform(-self._powerupSpread[1],self._powerupSpread[1]))

            # drop one random one somewhere..
            bs.Powerup(position=pt,powerupType=bs.Powerup.getFactory().getRandomPowerupType(excludeTypes=self._excludePowerups)).autoRetain()

    def doEnd(self,outcome,delay=0):

        if outcome == 'defeat':
            self.fadeToRed()
            bs.playMusic('boo')

        if bs.getConfig()['Cheats Active'] == True:
            score = None
            failMessage = bs.Lstr(resource='cheaterText')
        elif self._wave >= 1:
            score = self._score
            failMessage = None
        else:
            score = None
            failMessage = bs.Lstr(resource='reachWave8Text')
        self.end({'outcome':outcome,'score':score,'failMessage':failMessage,'playerInfo':self.initialPlayerInfo},delay=delay)

    def _updateWaves(self):

        # if we have no living bots, go to the next wave
        if self._canEndWave and not self._bots.haveLivingBots() and not self._gameOver:

            self._canEndWave = False

            won = (self._wave == len(self._waves))

            if won:

                self.showZoomMessage(bs.Lstr(resource='survivedText'),scale=1.0,duration=4000)
                self.celebrate(20000)
                self.cameraFlash()
                bs.playMusic('Marathon Victory')
                self._gameOver = True
                import BuddyBunny
                for n in bs.getNodes():
                    if n.getNodeType() == 'spaz':
                        s = n.getDelegate()
                        if isinstance(s, BuddyBunny.BunnyBuddyBot):
                            if random.randint(1,3) == 1: s.node.handleMessage("celebrateR",20000)
                            elif random.randint(1,3) == 2: s.node.handleMessage("celebrateL",20000)
                            else: s.node.handleMessage("celebrate",20000)
                            bs.gameTimer(random.randint(60,350),bs.WeakCall(s.buddyAwesomeMoves),repeat=True)

                # cant just pass delay to doEnd because our extra bonuses havnt been added yet
                # (once we call doEnd the score gets locked in)
                bs.gameTimer(3300,bs.WeakCall(self._awardCompletionBonus))
                bs.gameTimer(4475,bs.WeakCall(self.doEnd,'victory'))

                return

            self._wave += 1
                            
            bs.gameTimer(1,bs.WeakCall(self._startNextWave))

    def _awardCompletionBonus(self):
        bs.playSound(self._cashRegisterSound)
        for player in self.players:
            try:
                if player.isAlive():
                    self.scoreSet.playerScored(player,int(1000/len(self.initialPlayerInfo)),scale=1.4,color=(0.6,0.6,1.0,1.0),title=bs.Lstr(resource='completionBonusText'),screenMessage=False)
            except Exception,e:
                print 'EXC in _awardCompletionBonus',e
        
    def _updatePlayerSpawnInfo(self):

        # if we have no living players lets just blank this
        if not any(player.isAlive() for player in self.teams[0].players):
            self._spawnInfoText.node.text = ''
        else:
            t = ''
            for player in self.players:
                if not player.isAlive() and (player.gameData['respawnWave'] <= len(self._waves)):
                    t = bs.Lstr(value='${A}${B}\n',subs=[('${A}',t),('${B}',bs.Lstr(resource='onslaughtRespawnText',subs=[('${PLAYER}',player.getName()),('${WAVE}',str(player.gameData['respawnWave']))]))])
            self._spawnInfoText.node.text = t

    def _startNextWave(self):

        # this could happen if we beat a wave as we die..
        # we dont wanna respawn players and whatnot if this happens
        if self._gameOver: return
        
        # respawn applicable players
        if self._wave > 1 and not self.isWaitingForContinue():
            for player in self.players:
                if not player.isAlive() and player.gameData['respawnWave'] == self._wave:
                    self.spawnPlayer(player)

        self._updatePlayerSpawnInfo()

        self.showZoomMessage(bs.Lstr(value='${A} ${B}',subs=[('${A}',bs.Lstr(resource='waveText')),('${B}',str(self._wave))]),
                             scale=1.0,duration=1000,trail=True)
        bs.gameTimer(400,bs.Call(bs.playSound,self._newWaveSound))
        if self._wave == 4 or self._wave == 8 or self._wave == 12 or self._wave == 16:
            bs.gameTimer(400,bs.Call(bs.playSound,self._specialWaveSound))
        t = 0
        dt = 200
        botAngle = random.random()*360.0

        if self._wave == 1:
            spawnTime = 3973
            t += 500
        else:
            spawnTime = 2648

        offs = 0 # debugging

        wave = self._waves[self._wave-1]


        entries = []

        try: botAngle = wave['baseAngle']
        except Exception: botAngle = 0

        entries += wave['entries']

        thisTimeBonus = 0
        thisFlawlessBonus = 0

        for info in entries:
            if info is None: continue

            botType = info['type']

            if botType == 'delay':
                spawnTime += info['duration']
                continue
            if botType is not None:
                thisTimeBonus += botType.pointsMult * 20
                thisFlawlessBonus += botType.pointsMult * 5
            # if its got a position, use that
            try: point = info['point']
            except Exception: point = None
            if point is not None:
                bs.gameTimer(t,bs.WeakCall(self.addBotAtPoint,point,botType,spawnTime))
                t += dt
            else:
                try: spacing = info['spacing']
                except Exception: spacing = 5.0
                botAngle += spacing*0.5
                if botType is not None:
                    bs.gameTimer(t,bs.WeakCall(self.addBotAtAngle,botAngle,botType,spawnTime))
                    t += dt
                botAngle += spacing*0.5
            
        # we can end the wave after all the spawning happens
        bs.gameTimer(t+spawnTime-dt+10,bs.WeakCall(self._setCanEndWave))
        

        vrMode = bs.getEnvironment()['vrMode']
        self._waveText = bs.NodeActor(bs.newNode('text',
                                                 attrs={'vAttach':'top',
                                                        'hAttach':'center',
                                                        'hAlign':'center',
                                                        'vrDepth':-10,
                                                        'color':(1,1,1,1) if True else (0.7,0.7,0.7,1.0),
                                                        'shadow':1.0 if True else 0.7,
                                                        'flatness':1.0 if True else 0.5,
                                                        'position':(0,-40),
                                                        'scale':1.3 if True else 1.1,
                                                        'text':bs.Lstr(value='${A} ${B}',subs=[('${A}',bs.Lstr(resource='waveText')),('${B}',str(self._wave)+('/'+str(len(self._waves))))])}))
                                                        

    def addBotAtPoint(self,point,spazType,spawnTime=1000):
        # dont add if the game has ended
        if self._gameOver: return
        pt = self.getMap().defs.points['botSpawn'+point]
        self._bots.spawnBot(spazType,pos=pt,spawnTime=spawnTime)
        
    def addBotAtAngle(self,angle,spazType,spawnTime=1000):

        # dont add if the game has ended
        if self._gameOver: return
        angleRadians = angle/57.2957795
        x = math.sin(angleRadians)*1.0
        z = math.cos(angleRadians)*0.5
        pt = (x/0.125,2.8,(z/0.2)-3.7)

        self._bots.spawnBot(spazType,pos=pt,spawnTime=spawnTime)

    def _startUpdatingWaves(self):
        self._waveUpdateTimer = bs.Timer(2000,bs.WeakCall(self._updateWaves),repeat=True)
        
    def _updateScores(self):
        self._scoreBoard.setTeamValue(self.teams[0],self._score,maxScore=None)

        
    def handleMessage(self,m):

        if isinstance(m,bs.PlayerSpazHurtMessage):
            player = m.spaz.getPlayer()
            if player is None:
                bs.printError('FIXME: getPlayer() should no longer ever be returning None')
                return
            if not player.exists(): return
            player.gameData['hasBeenHurt'] = True
            self._aPlayerHasBeenHurt = True

        elif isinstance(m,bs.PlayerScoredMessage):
            self._score += m.score
            self._updateScores()

        elif isinstance(m,bs.PlayerSpazDeathMessage):
            self.__superHandleMessage(m) # augment standard behavior
            player = m.spaz.getPlayer()
            self._aPlayerHasBeenHurt = True
            # make note with the player when they can respawn
            if self._wave < 16: player.gameData['respawnWave'] = max(2,self._wave+1)
            elif self._wave < 24: player.gameData['respawnWave'] = max(2,self._wave+2)
            else: player.gameData['respawnWave'] = max(2,self._wave+3)
            
            bs.gameTimer(100,self._updatePlayerSpawnInfo)
            bs.gameTimer(100,self._checkRoundOver)

        elif isinstance(m,bs.SpazBotDeathMessage):
            pts,importance = m.badGuy.getDeathPoints(m.how)
            if m.killerPlayer is not None:
                try: target = m.badGuy.node.position
                except Exception: target = None
                try:
                    killerPlayer = m.killerPlayer
                    self.scoreSet.playerScored(killerPlayer,pts,target=target,kill=True,screenMessage=False,importance=importance)
                    bs.playSound(self._dingSound if importance == 1 else self._dingSoundHigh,volume=0.6)
                except Exception: pass
            # normally we pull scores from the score-set, but if there's no player lets be explicit..
            else: self._score += pts
            self._updateScores()
        else:
            self.__superHandleMessage(m)

    def _setCanEndWave(self):
        self._canEndWave = True

    def __superHandleMessage(self,m):
        super(NightMarathonGame,self).handleMessage(m)

    def endGame(self):
        # tell our bots to celebrate just to rub it in
        self._bots.finalCelebrate()
        
        self._gameOver = True
        self.doEnd('defeat',delay=2000)
        bs.playMusic('Marathon Defeat')

    def onContinue(self):
        for player in self.players:
            if not player.isAlive():
                self.spawnPlayer(player)
        
    def _checkRoundOver(self):
        """ see if the round is over in response to an event (player died, etc) """

        # if we already ended it doesn't matter
        if self.hasEnded(): return

        if not any(player.isAlive() for player in self.teams[0].players):
            # allow continuing after wave 1
            if self._wave > 1: self.continueOrEndGame()
            else: self.endGame()
            





class BreakthroughGame(bs.CoopGameActivity):

    @classmethod
    def getName(cls):
        return 'Breakthrough'

    @classmethod
    def getDescription(cls,sessionType):
        return "Kill all enemies."

    def __init__(self,settings={}):

        settings['map'] = 'Courtyard'

        bs.CoopGameActivity.__init__(self,settings)

        # show messages when players die since it matters here..
        self.announcePlayerDeaths = True
        
        self._newWaveSound = bs.getSound('scoreHit01')
        self._cashRegisterSound = bs.getSound('cashRegister')
        self._aPlayerHasBeenHurt = False
        self._winSound = bs.getSound("score")
        self._preset = settings['preset']

        # fixme - should use standard map defs..
        self._spawnCenter = (0,3,-2)
        self._tntSpawnPosition = (0,3,2.1)
        self._powerupCenter = (0,5,-1.6)
        self._powerupSpread = (4.6,2.7)
        

    def onTransitionIn(self):

        bs.CoopGameActivity.onTransitionIn(self)
        self._spawnInfoText = bs.NodeActor(bs.newNode("text",
                                                      attrs={'position':(15,-130),
                                                             'hAttach':"left",
                                                             'vAttach':"top",
                                                             'scale':0.55,
                                                             'color':(0.3,0.8,0.3,1.0),
                                                             'text':''}))
        bs.playMusic('Spy Brothers')

        self._scoreBoard = bs.ScoreBoard(label=bs.Lstr(resource='scoreText'),scoreSplit=0.5)
        self._gameOver = False
        self._wave = 0
        self._canEndWave = True
        self._score = 0
        self._timeBonus = 0


    def onBegin(self):

        bs.CoopGameActivity.onBegin(self)
        playerCount = len(self.players)
        self._dingSound = bs.getSound('dingSmall')
        self._dingSoundHigh = bs.getSound('dingSmallHigh')
        
        import bsUtils
        bsUtils.ControlsHelpOverlay(delay=3000,lifespan=10000,bright=True).autoRetain()

        self._haveTnt = False
        if self._preset == '1/7':
            self._text = "Powerups Banned: Overdrive, Heal Bombs, Impact Bombs & Shields"
            self._excludePowerups = ['overdrive','healBombs','shield','impactBombs']
            self.setupStandardTimeLimit(560)
            
            self._waves = [
                {'entries':[
                        {'type':bs.PixelBot,'point':'Left'},
                        {'type':'delay','duration':4500},
                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'} if playerCount > 1 else None,
                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'} if playerCount > 1 else None,
                        {'type':bs.BunnyBot,'point':'Right'},
                        {'type':bs.BunnyBot,'point':'Left'},
                        {'type':'delay','duration':5000},
                        {'type':bs.MelDuperBot,'point':'Top'},
                        ]},
                {'entries':[
                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddleRight'},
                        {'type':'delay','duration':500},
                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddleLeft'},
                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddle'} if playerCount > 2 else None,
                        {'type':bs.NinjaBot,'point':'BottomLeft'},
                        {'type':'delay','duration':844},
                        {'type':bs.ChickBot,'point':'Left'},
                        {'type':bs.ChickBot,'point':'LeftLower'},
                        {'type':'delay','duration':1650},
                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                        ]},
                {'entries':[
                        {'type':'delay','duration':5000},
                        {'type':bs.ChickBotPro,'point':'BottomLeft'},
                        {'type':bs.ChickBotPro,'point':'BottomRight'},
                        {'type':bs.ChickBotPro,'point':'TopLeft'},
                        {'type':bs.ChickBotPro,'point':'TopRight'},
                        {'type':'delay','duration':4200},
                        {'type':bs.CyborgBotStatic,'point':'TurretBottomRight'},
                        {'type':bs.CyborgBotStatic,'point':'TurretBottomLeft'},
                        {'type':bs.CyborgBotStatic,'point':'TurretTopRight'},
                        {'type':bs.CyborgBotStatic,'point':'TurretTopLeft'},
                        {'type':bs.LooieBot,'point':'Top'} if playerCount > 1 else None,
                        ]},
                {'entries':[
                        {'type':bs.FrostyBotStatic,'point':'TurretTopMiddle'},
                        {'type':bs.FrostyBotStatic,'point':'TurretTopMiddleLeft'},
                        {'type':'delay','duration':1000},
                        {'type':bs.JuiceBot,'point':'TopHalfRight'},
                        {'type':bs.JuiceBot,'point':'TopHalfLeft'},
                        {'type':bs.BomberBotPro,'point':'LeftUpper'},
                        {'type':bs.BomberBotPro,'point':'LeftLower'},
                        {'type':bs.NinjaBot,'point':'Right'},
                        {'type':bs.NinjaBot,'point':'RightUpperMore'} if playerCount > 1 else None,
                        {'type':'delay','duration':800},
                        {'type':bs.ChickBotPro,'point':'Bottom'},
                        ]},
                ]
        elif self._preset == '2/7':
            self._text = "Powerups Banned: Landmines, Fire Bombs, Speed Boots & Ice Bombs"
            self._excludePowerups = ['speed','landMine','fireBombs','iceBombs']
            self.setupStandardTimeLimit(880)
            
            self._waves = [
                {'entries':[
                        {'type':'delay','duration':900},
                        {'type':bs.ToughGuyBotPro,'point':random.choice(['Left','Right','Top','Bottom'])},
                        {'type':'delay','duration':850},
                        {'type':bs.ToughGuyBotPro,'point':random.choice(['Left','Right','Top','Bottom'])},
                        {'type':'delay','duration':900},
                        {'type':bs.ToughGuyBotPro,'point':random.choice(['Left','Right','Top','Bottom'])},
                        {'type':'delay','duration':900},
                        {'type':bs.ToughGuyBotPro,'point':random.choice(['Left','Right','Top','Bottom'])},
                        {'type':'delay','duration':1200},
                        {'type':bs.AgentBotShielded,'point':'TopLeft'} if playerCount > 1 else None,
                        {'type':bs.AgentBotShielded,'point':'TopLeft'} if playerCount > 1 else None,
                        {'type':bs.NinjaBot,'point':'Bottom'},
                        ]},
                {'entries':[
                        {'type':bs.MelBotStatic,'point':'TurretTopRight'},
                        {'type':bs.MelBotStatic,'point':'TurretBottomRight'},
                        {'type':bs.BonesBot,'point':'LeftLowerMore'},
                        {'type':bs.BonesBot,'point':'LeftUpper'},
                        {'type':'delay','duration':8000},
                        {'type':bs.ChickBotStatic,'point':'TurretTopLeft'},
                        {'type':bs.ChickBotStatic,'point':'TurretBottomLeft'},
                        {'type':'delay','duration':742},
                        {'type':bs.BomberBotPro,'point':'Top'} if playerCount > 2 else None,
                        {'type':bs.BonesBot,'point':'RightUpper'},
                        ]},
                {'entries':[
                        {'type':'delay','duration':5000},
                        {'type':bs.ChickBotPro,'point':'BottomLeft'},
                        {'type':bs.ChickBotPro,'point':'BottomRight'},
                        {'type':bs.ChickBotPro,'point':'TopLeft'},
                        {'type':bs.ChickBotPro,'point':'TopRight'},
                        {'type':'delay','duration':4200},
                        {'type':bs.CyborgBotStatic,'point':'TurretBottomRight'},
                        {'type':bs.CyborgBotStatic,'point':'TurretBottomLeft'},
                        {'type':bs.CyborgBotStatic,'point':'TurretTopRight'},
                        {'type':bs.CyborgBotStatic,'point':'TurretTopLeft'},
                        {'type':bs.LooieBot,'point':'Top'} if playerCount > 1 else None,
                        ]},
                {'entries':[
                        {'type':bs.FrostyBotStatic,'point':'TurretTopMiddle'},
                        {'type':bs.FrostyBotStatic,'point':'TurretTopMiddleLeft'},
                        {'type':'delay','duration':1000},
                        {'type':bs.JuiceBot,'point':'TopHalfRight'},
                        {'type':bs.JuiceBot,'point':'TopHalfLeft'},
                        {'type':bs.BomberBotPro,'point':'LeftUpper'},
                        {'type':bs.BomberBotPro,'point':'LeftLower'},
                        {'type':bs.NinjaBot,'point':'Right'},
                        {'type':bs.NinjaBot,'point':'RightUpperMore'} if playerCount > 1 else None,
                        {'type':'delay','duration':800},
                        {'type':bs.ChickBotPro,'point':'Bottom'},
                        ]},
                ]
        self._dropPowerups(standardPoints=True)
        bs.gameTimer(4000,self._startPowerupDrops)
        if self._haveTnt:
            self._tntSpawner = bs.TNTSpawner(position=self._tntSpawnPosition)
        
        self.setupLowLifeWarningSound()
        
        self._updateScores()
        self._bots = bs.BotSet()

        bs.gameTimer(3500,self._startUpdatingWaves)


    def _onGotScoresToBeat(self,scores):
        self._showStandardScoresToBeatUI(scores)


    def _getDistribution(self,targetPoints,minDudes,maxDudes,groupCount,maxLevel):
        """ calculate a distribution of bad guys given some params """

        maxIterations = 10+maxDudes*2

        def _getTotals(groups):
            totalPoints = 0
            totalDudes = 0
            for group in groups:
                for entry in group:
                    dudes = entry[1]
                    totalPoints += entry[0]*dudes
                    totalDudes += dudes
            return totalPoints,totalDudes

        groups = []
        for g in range(groupCount):
            groups.append([])

        types = [1]
        if maxLevel > 1: types.append(2)
        if maxLevel > 2: types.append(3)
        if maxLevel > 3: types.append(4)

        for iteration in range(maxIterations):
            # see how much we're off our target by
            totalPoints,totalDudes = _getTotals(groups)
            diff = targetPoints - totalPoints
            dudesDiff = maxDudes - totalDudes
            # add an entry if one will fit
            value = types[random.randrange(len(types))]
            group = groups[random.randrange(len(groups))]
            if len(group) == 0: maxCount = random.randint(1,6)
            else: maxCount = 2*random.randint(1,3)
            maxCount = min(maxCount,dudesDiff)
            count = min(maxCount,diff/value)
            if count > 0:
                group.append((value,count))
                totalPoints += value*count
                totalDudes += count
                diff = targetPoints - totalPoints

            totalPoints,totalDudes = _getTotals(groups)
            full = (totalPoints >= targetPoints)

            if full:
                # every so often, delete a random entry just to shake up our distribution
                if random.random() < 0.2 and iteration != maxIterations-1:
                    entryCount = 0
                    for group in groups:
                        for entry in group:
                            entryCount += 1
                    if entryCount > 1:
                        delEntry = random.randrange(entryCount)
                        entryCount = 0
                        for group in groups:
                            for entry in group:
                                if entryCount == delEntry:
                                    group.remove(entry)
                                    break
                                entryCount += 1

                # if we don't have enough dudes, kill the group with the biggest point value
                elif totalDudes < minDudes and iteration != maxIterations-1:
                    biggestValue = 9999
                    biggestEntry = None
                    for group in groups:
                        for entry in group:
                            if entry[0] > biggestValue or biggestEntry is None:
                                biggestValue = entry[0]
                                biggestEntry = entry
                                biggestEntryGroup = group
                    if biggestEntry is not None: biggestEntryGroup.remove(biggestEntry)

                # if we've got too many dudes, kill the group with the smallest point value
                elif totalDudes > maxDudes and iteration != maxIterations-1:
                    smallestValue = 9999
                    smallestEntry = None
                    for group in groups:
                        for entry in group:
                            if entry[0] < smallestValue or smallestEntry is None:
                                smallestValue = entry[0]
                                smallestEntry = entry
                                smallestEntryGroup = group
                    smallestEntryGroup.remove(smallestEntry)

                # close enough.. we're done.
                else:
                    if diff == 0: break

        return groups


        
    def spawnPlayer(self,player):
        # we keep track of who got hurt each wave for score purposes
        player.gameData['hasBeenHurt'] = False
        pos = (self._spawnCenter[0]+random.uniform(-1.5,1.5),self._spawnCenter[1],self._spawnCenter[2]+random.uniform(-1.5,1.5))
        s = self.spawnPlayerSpaz(player,position=pos)
        s.impactScale = 1.00
        mat = self.getMap().preloadData['collideWithWallMaterial']
        s.node.materials += (mat,)
        s.node.rollerMaterials += (mat,)

    def _dropPowerup(self,index,powerupType=None):
        powerupType = bs.Powerup.getFactory().getRandomPowerupType(forceType=powerupType)
        bs.Powerup(position=self.getMap().powerupSpawnPoints[index],powerupType=powerupType).autoRetain()

    def _startPowerupDrops(self):
        import bsPowerup
        self._powerupDropTimer = bs.Timer(bsPowerup.coopPowerupDropRate,bs.WeakCall(self._dropPowerups),repeat=True)

    def _dropPowerups(self,standardPoints=False,powerupType=None):
        """ Generic powerup drop """

        if standardPoints:
            pts = self.getMap().powerupSpawnPoints
            for i,pt in enumerate(pts):
                bs.gameTimer(1000+i*500,bs.WeakCall(self._dropPowerup,i,powerupType if i == 0 else None))
        else:
            pt = (self._powerupCenter[0]+random.uniform(-1.0*self._powerupSpread[0],1.0*self._powerupSpread[0]),
                  self._powerupCenter[1],self._powerupCenter[2]+random.uniform(-self._powerupSpread[1],self._powerupSpread[1]))

            # drop one random one somewhere..
            bs.Powerup(position=pt,powerupType=bs.Powerup.getFactory().getRandomPowerupType()).autoRetain()

    def doEnd(self,outcome,delay=0):

        if outcome == 'defeat':
            self.fadeToRed()

        if self._wave >= 2:
            score = self._score
            failMessage = None
        else:
            score = None
            failMessage = bs.Lstr(resource='reachWave2Text')
        self.end({'outcome':outcome,'score':score,'failMessage':failMessage,'playerInfo':self.initialPlayerInfo},delay=delay)

    def _updateWaves(self):

        # if we have no living bots, go to the next wave
        if self._canEndWave and not self._bots.haveLivingBots() and not self._gameOver:

            self._canEndWave = False

            self._timeBonusTimer = None
            self._timeBonusText = None

            won = (self._wave == len(self._waves))

            # reward time bonus
            baseDelay = 4000 if won else 0

            if self._timeBonus > 0:
                bs.gameTimer(0,lambda: bs.playSound(self._cashRegisterSound))
                bs.gameTimer(baseDelay,bs.WeakCall(self._awardTimeBonus,self._timeBonus))
                baseDelay += 1000

            # reward flawless bonus
            if self._wave > 0:
                haveFlawless = False
                for player in self.players:
                    if player.isAlive() and player.gameData['hasBeenHurt'] == False:
                        haveFlawless = True
                        bs.gameTimer(baseDelay,bs.WeakCall(self._awardFlawlessBonus,player))
                    player.gameData['hasBeenHurt'] = False # reset
                if haveFlawless: baseDelay += 1000

            if won:

                self.showZoomMessage(bs.Lstr(resource='victoryText'),scale=1.0,duration=4000)

                self.celebrate(20000)
                import BuddyBunny
                for n in bs.getNodes():
                    if n.getNodeType() == 'spaz':
                        s = n.getDelegate()
                        if isinstance(s, BuddyBunny.BunnyBuddyBot):
                            if random.randint(1,3) == 1: s.node.handleMessage("celebrateR",20000)
                            elif random.randint(1,3) == 2: s.node.handleMessage("celebrateL",20000)
                            else: s.node.handleMessage("celebrate",20000)
                            bs.gameTimer(random.randint(60,350),bs.WeakCall(s.buddyAwesomeMoves),repeat=True)

                bs.gameTimer(baseDelay,bs.WeakCall(self._awardCompletionBonus))
                baseDelay += 850
                bs.playSound(self._winSound)
                self.cameraFlash()
                bs.playMusic('Victory')
                self._gameOver = True
                bs.gameTimer(baseDelay,bs.WeakCall(self.doEnd,'victory'))

                return

            self._wave += 1
            if self._wave > 1: self.celebrate(750)
                            
            bs.gameTimer(baseDelay,bs.WeakCall(self._startNextWave))

    def _awardCompletionBonus(self):
        bs.playSound(self._cashRegisterSound)
        for player in self.players:
            try:
                if player.isAlive():
                    self.scoreSet.playerScored(player,int(100/len(self.initialPlayerInfo)),scale=1.4,color=(0.6,0.6,1.0,1.0),title=bs.Lstr(resource='completionBonusText'),screenMessage=False)
            except Exception,e:
                print 'EXC in _awardCompletionBonus',e
        
    def _awardTimeBonus(self,bonus):
        bs.playSound(self._cashRegisterSound)
        bs.PopupText(bs.Lstr(value='+${A} ${B}',subs=[('${A}',str(bonus)),('${B}',bs.Lstr(resource='timeBonusText'))]),
                     color=(1,1,0.5,1),
                     scale=1.0,
                     position=(0,3,-1)).autoRetain()
        self._score += self._timeBonus
        self._updateScores()

    def _awardFlawlessBonus(self,player):
        bs.playSound(self._cashRegisterSound)
        try:
            if player.isAlive():
                self.scoreSet.playerScored(player,self._flawlessBonus,scale=1.2,color=(0.6,1.0,0.6,1.0),title=bs.Lstr(resource='flawlessWaveText'),screenMessage=False)
        except Exception,e:
            print 'EXC in _awardFlawlessBonus',e
    
    def _startTimeBonusTimer(self):
        self._timeBonusTimer = bs.Timer(1000,bs.WeakCall(self._updateTimeBonus),repeat=True)
        
    def _updatePlayerSpawnInfo(self):

        # if we have no living players lets just blank this
        if not any(player.isAlive() for player in self.teams[0].players):
            self._spawnInfoText.node.text = ''
        else:
            t = ''
            for player in self.players:
                if not player.isAlive() and (player.gameData['respawnWave'] <= len(self._waves)):
                    t = bs.Lstr(value='${A}${B}\n',subs=[('${A}',t),('${B}',bs.Lstr(resource='onslaughtRespawnText',subs=[('${PLAYER}',player.getName()),('${WAVE}',str(player.gameData['respawnWave']))]))])
            self._spawnInfoText.node.text = t

    def _startNextWave(self):

        # this could happen if we beat a wave as we die..
        # we dont wanna respawn players and whatnot if this happens
        if self._gameOver: return
        
        # respawn applicable players
        if self._wave > 1 and not self.isWaitingForContinue():
            for player in self.players:
                if not player.isAlive() and player.gameData['respawnWave'] == self._wave:
                    self.spawnPlayer(player)

        self._updatePlayerSpawnInfo()

        self.showZoomMessage(bs.Lstr(value='${A} ${B}',subs=[('${A}',bs.Lstr(resource='waveText')),('${B}',str(self._wave))]),
                             scale=1.0,duration=1000,trail=True)
        bs.gameTimer(400,bs.Call(bs.playSound,self._newWaveSound))
        if self._wave == 4 or self._wave == 8 or self._wave == 12 or self._wave == 16:
            bs.gameTimer(400,bs.Call(bs.playSound,self._specialWaveSound))
        t = 0
        dt = 200
        botAngle = random.random()*360.0

        if self._wave == 1:
            spawnTime = 3973
            t += 500
        else:
            spawnTime = 2648

        offs = 0 # debugging

        wave = self._waves[self._wave-1]


        entries = []

        try: botAngle = wave['baseAngle']
        except Exception: botAngle = 0

        entries += wave['entries']

        thisTimeBonus = 0
        thisFlawlessBonus = 0

        for info in entries:
            if info is None: continue

            botType = info['type']

            if botType == 'delay':
                spawnTime += info['duration']
                continue
            if botType is not None:
                thisTimeBonus += botType.pointsMult * 20
                thisFlawlessBonus += botType.pointsMult * 5
            # if its got a position, use that
            try: point = info['point']
            except Exception: point = None
            if point is not None:
                bs.gameTimer(t,bs.WeakCall(self.addBotAtPoint,point,botType,spawnTime))
                t += dt
            else:
                try: spacing = info['spacing']
                except Exception: spacing = 5.0
                botAngle += spacing*0.5
                if botType is not None:
                    bs.gameTimer(t,bs.WeakCall(self.addBotAtAngle,botAngle,botType,spawnTime))
                    t += dt
                botAngle += spacing*0.5
            
        # we can end the wave after all the spawning happens
        bs.gameTimer(t+spawnTime-dt+10,bs.WeakCall(self._setCanEndWave))

        # reset our time bonus
        self._timeBonus = thisTimeBonus
        self._flawlessBonus = thisFlawlessBonus
        vrMode = bs.getEnvironment()['vrMode']
        self._timeBonusText = bs.NodeActor(bs.newNode('text',
                                                      attrs={'vAttach':'top',
                                                             'hAttach':'center',
                                                             'hAlign':'center',
                                                             'vrDepth':-30,
                                                             'color':(1,1,0,1) if True else (1,1,0.5,1),
                                                             'shadow':1.0 if True else 0.5,
                                                             'flatness':1.0 if True else 0.5,
                                                             'position':(-125,-60),
                                                             'scale':0.8 if True else 0.6,
                                                             'text':bs.Lstr(value='${A}: ${B}',subs=[('${A}',bs.Lstr(resource='timeBonusText')),('${B}',str(self._timeBonus))])}))
        
        bs.gameTimer(5000,bs.WeakCall(self._startTimeBonusTimer))
        self._waveText = bs.NodeActor(bs.newNode('text',
                                                 attrs={'vAttach':'top',
                                                        'hAttach':'center',
                                                        'hAlign':'center',
                                                        'vrDepth':-10,
                                                        'color':(1,1,1,1) if True else (0.7,0.7,0.7,1.0),
                                                        'shadow':1.0 if True else 0.7,
                                                        'flatness':1.0 if True else 0.5,
                                                        'position':(-130,-40),
                                                        'scale':1.3 if True else 1.1,
                                                        'text':bs.Lstr(value='${A} ${B}',subs=[('${A}',bs.Lstr(resource='waveText')),('${B}',str(self._wave)+('/'+str(len(self._waves))))])}))
        self._bans = bs.NodeActor(bs.newNode('text',
                                                 attrs={'vAttach':'top',
                                                        'hAttach':'center',
                                                        'hAlign':'center',
                                                        'vrDepth':-10,
                                                        'color':(0.45,0.67,0.82,1.2) if True else (0.7,0.7,0.7,1.0),
                                                        'shadow':1.0 if True else 0.7,
                                                        'flatness':1.0 if True else 0.5,
                                                        'position':(290,-22),
                                                        'scale':0.5 if True else 0.5,
                                                        'text':self._text}))
                                                        
    def addBotAtPoint(self,point,spazType,spawnTime=1000):
        # dont add if the game has ended
        if self._gameOver: return
        pt = self.getMap().defs.points['botSpawn'+point]
        self._bots.spawnBot(spazType,pos=pt,spawnTime=spawnTime)
        
    def addBotAtAngle(self,angle,spazType,spawnTime=1000):

        # dont add if the game has ended
        if self._gameOver: return

        angleRadians = angle/57.2957795
        x = math.sin(angleRadians)*1.06
        z = math.cos(angleRadians)*1.06
        pt = (x/0.125,2.3,(z/0.2)-3.7)

        self._bots.spawnBot(spazType,pos=pt,spawnTime=spawnTime)

    def _updateTimeBonus(self):
        self._timeBonus = int(self._timeBonus * 0.93)
        if self._timeBonus > 0 and self._timeBonusText is not None:
            self._timeBonusText.node.text = bs.Lstr(value='${A}: ${B}',subs=[('${A}',bs.Lstr(resource='timeBonusText')),('${B}',str(self._timeBonus))])
        else: self._timeBonusText = None

    def _startUpdatingWaves(self):
        self._waveUpdateTimer = bs.Timer(2000,bs.WeakCall(self._updateWaves),repeat=True)
        
    def _updateScores(self):
        self._scoreBoard.setTeamValue(self.teams[0],self._score,maxScore=None)

        
    def handleMessage(self,m):

        if isinstance(m,bs.PlayerSpazHurtMessage):
            player = m.spaz.getPlayer()
            if player is None:
                bs.printError('FIXME: getPlayer() should no longer ever be returning None')
                return
            if not player.exists(): return
            player.gameData['hasBeenHurt'] = True
            self._aPlayerHasBeenHurt = True

        elif isinstance(m,bs.PlayerScoredMessage):
            self._score += m.score
            self._updateScores()

        elif isinstance(m,bs.PlayerSpazDeathMessage):
            self.__superHandleMessage(m) # augment standard behavior
            player = m.spaz.getPlayer()
            self._aPlayerHasBeenHurt = True
            # make note with the player when they can respawn
            player.gameData['respawnWave'] = max(2,self._wave+3)
            bs.gameTimer(100,self._updatePlayerSpawnInfo)
            bs.gameTimer(100,self._checkRoundOver)

        elif isinstance(m,bs.SpazBotDeathMessage):
            pts,importance = m.badGuy.getDeathPoints(m.how)
            if m.killerPlayer is not None:
                try: target = m.badGuy.node.position
                except Exception: target = None
                try:
                    killerPlayer = m.killerPlayer
                    self.scoreSet.playerScored(killerPlayer,pts,target=target,kill=True,screenMessage=False,importance=importance)
                    bs.playSound(self._dingSound if importance == 1 else self._dingSoundHigh,volume=0.6)
                except Exception: pass
            # normally we pull scores from the score-set, but if there's no player lets be explicit..
            else: self._score += pts
            self._updateScores()
        else:
            self.__superHandleMessage(m)

    def _setCanEndWave(self):
        self._canEndWave = True

    def __superHandleMessage(self,m):
        super(BreakthroughGame,self).handleMessage(m)

    def endGame(self):
        # tell our bots to celebrate just to rub it in
        self._bots.finalCelebrate()
        
        self._gameOver = True
        self.doEnd('defeat',delay=2000)

    def onContinue(self):
        for player in self.players:
            if not player.isAlive():
                self.spawnPlayer(player)
        
    def _checkRoundOver(self):
        """ see if the round is over in response to an event (player died, etc) """

        # if we already ended it doesn't matter
        if self.hasEnded(): return

        if not any(player.isAlive() for player in self.teams[0].players):
            # allow continuing after wave 1
            if self._wave > 1: self.continueOrEndGame()
            else: self.endGame()






