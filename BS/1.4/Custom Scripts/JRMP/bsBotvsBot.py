#Maded by Froshlee14
import bs,random, bsSpaz,bsBomb,bsUtils, bsInternal,bsMainMenu,bsPowerup,math
from bsSpaz import _PunchHitMessage,_PickupMessage

def bsGetAPIVersion():
    return 4

def bsGetGames():
    return [BotsVsBots]
	
def bsGetLevels():
    return [bs.Level('Bots vs Bots', displayName='${GAME}',gameType=BotsVsBots,previewTexName='rampagePreview',settings={})]

	
class MelBot(bsSpaz.SpazBot):
    character = 'Mel'
    punchiness = 0.9
    throwiness = 0.1
    run = True
    chargeDistMin = 4.0
    chargeDistMax = 10.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 0.0
    throwDistMax = 4.0
    throwRate = 2.0
    defaultBombType = 'sticky'
    defaultBombCount = 1
		
class FroshBot(bsSpaz.SpazBot):
    color=(0.13,0.13,0.13)
    highlight=(0.2,1,1)
    character = 'Bernard'
    run = True
    throwiness = 0.2
    punchiness = 0.9
    chargeDistMax = 1.0
    chargeSpeedMin = 0.3
    chargeSpeedMax = 1.0
	
class RobotBot(bsSpaz.ToughGuyBot):
    color=(0.5,0.5,0.5)
    highlight=(0,10,0)
    character = 'B-9000'
    chargeSpeedMin = 0.3
    chargeSpeedMax = 1.0

    def handleMessage(self,m):

        super(self.__class__, self).handleMessage(m)
        def _safeSetAttr(node,attr,val):
            if node.exists(): setattr(node,attr,val)
        bs.gameTimer(500,bs.Call(_safeSetAttr,self.node,'hockey',True))

class PascalBot(bsSpaz.SpazBot):
    color=(0,0,3)
    highlight=(0.2,0.2,1)
    character = 'Pascal'
    bouncy = True
    run = True
    punchiness = 0.8
    throwiness = 0.1
    chargeSpeedMin = 0.5
    chargeSpeedMax = 0.8

    def handleMessage(self,m):
        if isinstance(m, _PunchHitMessage):
            node = bs.getCollisionInfo("opposingNode")
            try:
                node.handleMessage(bs.FreezeMessage())
                bs.playSound(bs.getSound('freeze'))
            except Exception: print('Cant freeze')
            super(self.__class__, self).handleMessage(m)
        elif isinstance(m, bs.FreezeMessage):pass
        else: super(self.__class__, self).handleMessage(m)
	
class NewBotSet(bsSpaz.BotSet):
    def _update(self):
        try:
            botList = self._botLists[self._botUpdateList] = [b for b in self._botLists[self._botUpdateList] if b.exists()]
        except Exception:
            bs.printException("error updating bot list: "+str(self._botLists[self._botUpdateList]))
        self._botUpdateList = (self._botUpdateList+1)%self._botListCount
        playerPts = []
        for n in bs.getNodes():
                if n.getNodeType() == 'spaz':
                    s = n.getDelegate()
                    if isinstance(s,bsSpaz.PlayerSpaz):
                        if s.isAlive():
                            playerPts.append((bs.Vector(*n.position), bs.Vector(*n.velocity)))
                    if isinstance(s,bsSpaz.SpazBot):
                        if not s in self.getLivingBots():
                            playerPts.append((bs.Vector(*n.position), bs.Vector(*n.velocity)))

        for b in botList:
            b._setPlayerPts(playerPts)
            b._updateAI()

class BotsVsBots(bs.TeamGameActivity):
    
    @classmethod
    def getName(cls):
        return 'Bots vs Bots'
    
    @classmethod
    def getDescription(cls,sessionType):
        return 'Enjoy the battle.'

    @classmethod
    def getSupportedMaps(cls,sessionType):
        return ['Football Stadium']

    @classmethod
    def getSettings(cls,sessionType):
        return [("Epic Mode",{'default':False}),
                       ("Bots per Team",{'minValue':1,'maxValue':20,'default':6,'increment':1}),
                    ("Spaz",{'default':random.choice([True,False])}),
                    ("Kronk",{'default':random.choice([True,False])}),
                    ("Zoe",{'default':random.choice([True,False])}),
                    ("Jack Morgan",{'default':random.choice([True,False])}),
                    ("Mel",{'default':random.choice([True,False])}),
                    ("Snake Shadow",{'default':random.choice([True,False])}),
                    ("Bones",{'default':random.choice([True,False])}),
                    ("Bernard",{'default':random.choice([True,False])}),
                    ("Agent Johnson",{'default':random.choice([True,False])}),
                    ("Frosty",{'default':random.choice([True,False])}),
                    ("Pascal",{'default':random.choice([True,False])}),
                    ("Pixel",{'default':random.choice([True,False])}),
                    ("Wizard",{'default':random.choice([True,False])}),
                    ("Taobao Mascot",{'default':random.choice([True,False])}),
                    ("B-9000",{'default':random.choice([True,False])}),
                    ("Milk",{'default':random.choice([True,False])}),
                    ("Sir Bombalot",{'default':random.choice([True,False])}),
                    ("Willy",{'default':random.choice([True,False])}),
                    ("Easter Bunny",{'default':random.choice([True,False])}),
                    ("Santa Claus",{'default':random.choice([True,False])}),
                    ("Juice-Boy",{'default':random.choice([True,False])}),
                    ("Spy",{'default':random.choice([True,False])}),
                    ("Looie",{'default':random.choice([True,False])}),
                    ("Klaymen",{'default':random.choice([True,False])}),
                    ("Ronnie",{'default':random.choice([True,False])}),
                    ("AVGN",{'default':random.choice([True,False])}),
                    ("Mictlan",{'default':random.choice([True,False])}),
                    ("Lucy Chance",{'default':random.choice([True,False])}),
                    ("Zill",{'default':random.choice([True,False])}),
                    ("Puck",{'default':random.choice([True,False])}),
                    ("TNT",{'default':random.choice([True,False])}),
                    ("B.I.T.S",{'default':random.choice([True,False])})]
    
    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if (issubclass(sessionType,bs.TeamsSession)
                        or issubclass(sessionType,bs.FreeForAllSession)
                        or issubclass(sessionType,bs.CoopSession)) else False

    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)
        self._spawnCenter = (0,3,-5)
        if self.settings['Epic Mode']: self._isSlowMotion = True
        
    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Epic' if self.settings['Epic Mode'] else 'Survival')

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self._bots = NewBotSet()
        self._botset = bs.BotSet()
        self._bots2 = NewBotSet()
		
        self._hasEnded = False

        for i in range(self.settings['Bots per Team']):
            bPos = (-12,1.5,random.randrange(-4,5))
            bs.gameTimer(0,bs.Call(self._bots.spawnBot,self._getRandomBotType(),pos=bPos,spawnTime=4000,onSpawnCall=bs.Call(self.setRedTeam)))
            bPos = (12,1.5,random.randrange(-4,5))
            bs.gameTimer(0,bs.Call(self._bots2.spawnBot,self._getRandomBotType(),pos=bPos,spawnTime=4000,onSpawnCall=bs.Call(self.setBlueTeam)))
		
    def setRedTeam(self,spaz):
        spaz.node.color = (2.0,0.75,0.35)

    def setBlueTeam(self,spaz):
        spaz.node.color = (0.2,1.75,2.5)
		
    def _getRandomBotType(self):
        bt = []
        if self.settings['Spaz']: bt += [bs.SpazBot]
        if self.settings['Kronk']: bt += [bs.ToughGuyBot]
        if self.settings['Zoe']: bt += [bs.ChickBot]
        if self.settings['Jack Morgan']: bt += [bs.PirateBot]
        if self.settings['Mel']: bt += [bs.MelBot]
        if self.settings['Snake Shadow']: bt += [bs.NinjaBot]
        if self.settings['Bones']: bt += [bs.BonesBot]
        if self.settings['Bernard']: bt += [bs.BearBot]
        if self.settings['Agent Johnson']: bt += [bs.AgentBot]
        if self.settings['Frosty']: bt += [bs.FrostyBot]
        if self.settings['Pascal']: bt += [bs.PascalBot]
        if self.settings['Pixel']: bt += [bs.PixelBot]
        if self.settings['Wizard']: bt += [bs.WizardBot]
        if self.settings['Taobao Mascot']: bt += [bs.AliBot]
        if self.settings['B-9000']: bt += [bs.CyborgBot]
        if self.settings['Milk']: bt += [bs.CowBot]
        if self.settings['Sir Bombalot']: bt += [bs.KnightBot]
        if self.settings['Willy']: bt += [bs.JesterBot]
        if self.settings['Easter Bunny']: bt += [bs.BunnyBot]
        if self.settings['Santa Claus']: bt += [bs.SantaBot]
        if self.settings['Juice-Boy']: bt += [bs.JuiceBot]
        if self.settings['Spy']: bt += [bs.SpyBot]
        if self.settings['Looie']: bt += [bs.LooieBot]
        if self.settings['Klaymen']: bt += [bs.KlayBot]
        if self.settings['Ronnie']: bt += [bs.RonnieBot]
        if self.settings['AVGN']: bt += [bs.SoldierBot]
        if self.settings['Mictlan']: bt += [bs.DemonBot]
        if self.settings['Lucy Chance']: bt += [bs.DiceBot]
        if self.settings['Zill']: bt += [bs.ZillBot]
        if self.settings['Puck']: bt += [bs.PuckBot]
        if self.settings['TNT']: bt += [bs.TNTBot]
        if self.settings['B.I.T.S']: bt += [bs.ArmoredBot]
        return (random.choice(bt))
               
    def spawnPlayer(self,player):
        # we keep track of who got hurt each wave for score purposes
        player.gameData['hasBeenHurt'] = False
        pos = (1000,10000,10000)
        s = self.spawnPlayerSpaz(player,position=pos)
        mat = self.getMap().preloadData['collideWithWallMaterial']
        s.node.materials += (mat,)
        s.node.rollerMaterials += (mat,)
 
    def handleMessage(self,m):
        if isinstance(m,bs.SpazBotDeathMessage):
            bs.pushCall(self._checkEndGame)
            bs.TeamGameActivity.handleMessage(self,m) 
        else:
            bs.TeamGameActivity.handleMessage(self,m)
			
    def _checkEndGame(self):
        if self._hasEnded: return
        if len(self._bots.getLivingBots()) == 0:
            self.endGame(winners=' Blue',color=(0,0,1))
            self._hasEnded = True
        elif len(self._bots2.getLivingBots()) == 0:
            self.endGame(winners=' Red',color=(1,0,0))
            self._hasEnded = True
			
    def showZoomMessage(self,message,color=(0.9,0.4,0.0),position=None,scale=0.8,duration=2000,trail=False):
        try: times = self._zoomMessageTimes
        except Exception: self._zoomMessageTimes = {}
        i = 0
        curTime = bs.getGameTime()
        while True:
            if i not in self._zoomMessageTimes or self._zoomMessageTimes[i] < curTime:
                self._zoomMessageTimes[i] = curTime + duration
                break
            i += 1
        if position == None: position = (0,200-i*100)
        bsUtils.ZoomText(message,lifespan=duration,jitter=2.0,position=position,scale=scale,maxWidth=800, trail=trail,color=color).autoRetain()
			
    def endGame(self,winners=None,color=(1,1,1)):
        msg = (str(winners) + ' team win')
        self.showZoomMessage(msg,scale=1.0,duration=3000,trail=True,color=color)
        self.cameraFlash()
        self._botset.celebrate(99999999)
        bs.gameTimer(19000,self.fadeEnd)
		
    def fadeEnd(self):
        def callback():
            bsInternal._unlockAllInput()
            bsInternal._newHostSession(bsMainMenu.MainMenuSession)
        bsInternal._fadeScreen(False, time=500, endCall=callback)
        bsInternal._lockAllInput()