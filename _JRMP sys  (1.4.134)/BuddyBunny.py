import random
import weakref
import bs
import bsInternal
import bsSpaz
import bsUtils
import bsMainMenu
import bsUI
import math

class BunnyBuddyBot(bsSpaz.SpazBot):
    '''
    category: Bot Classes
    
    A speedy attacking melee bot.
    '''
    color = (1, 1, 1)
    highlight = (1.0, 0.5, 0.5)
    character = 'Easter Bunny'
    defaultBombCount = 1
    pointsMult = 0
    traitors = []
    
    def __init__(self, player):
        '''
        Instantiate a spaz-bot.
        '''
        self.color = player.color
        self.highlight = player.highlight
        self.character = random.choice(["Spaz","Kronk","Zoe","Jack Morgan","Mel","Snake Shadow","Klaymen","Lucy Chance",
        "Bones","Bernard","Agent Johnson","Frosty","Pascal","Pixel","B-9000","Taobao Mascot","Santa Claus","Easter Bunny",
        "Looie","Mictlan","Spy","Juice-Boy","Ronnie","Milk","Grumbledorf","Grambeldorfe","Puck","Zill","B.I.T.S","Sir Bombalot","Willy",
        "AVGN","Exploder","Cute Spaz"])
        self.bombShape = random.choice(["Regular","Bumpy","Pinecone","Ring","Canister","Unusual",
                                                                    "Sci-Fi","Prism","Drawing"])
        bsSpaz.Spaz.__init__(self, color=self.color, highlight=self.highlight, character=self.character,bombShape=self.bombShape,
                             sourcePlayer=None, startInvincible=False, canAcceptPowerups=True)
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
        self.blastType2 = 'normal'
        self._lastChargeDist = 0.0
        self._running = False
        self._lastJumpTime = 0
        if random.randint(1,30) == 25: self._aggressive = True
        else: self._aggressive = False
        self.xv = [
        'random','bouncy','fighter',
        'random','fighter','random',
        'bomber','random','bomber',
        'fighter','grabber','random',
        'bomber','tackler','fighter',
        'hittler','crazy','random',
        'random','bouncy','random',
        'static','random','charger',
        'charger','bomber','random']
        self.role = random.choice(self.xv)
        if self.role == 'random':
            punchiness = random.randint(0.0,1.0)
            throwiness = random.randint(0.0,1.0)
            run = random.choice([False,True,False,False])
            tackle = random.choice([False,True,False,False])
            bouncy = random.choice([False,False,False,False,True,False,False])
            throwDistMin = random.randint(0.0,10.0)
            throwDistMax = random.randint(0.0,10.0)
            throwRate = random.randint(0.0,10.0)
            chargeDistMin = random.randint(0.0,10.0)
            chargeDistMax = random.randint(0.0,10.0)
            chargeSpeedMin = random.randint(0.0,10.0)
            chargeSpeedMax = random.randint(0.0,10.0)
            runDistMax = random.randint(0.0,10.0)
            runDistMin = random.randint(0.0,10.0) 
        else:
            if self.role == 'bomber':
                self.throwRate = 1.0
            elif self.role == 'fighter':
                self.punchiness = 0.9
                self.chargeDistMax = 9999.0
                self.chargeSpeedMin = 1.0
                self.chargeSpeedMax = 1.0
                self.throwDistMin = 9999
                self.throwDistMax = 9999
            elif self.role == 'tackler':
                self.punchiness = 1.0
                self.run = True
                self.tackle = True
                self.chargeDistMin = 2.0
                self.chargeDistMax = 9999.0
                self.chargeSpeedMin = 1.0
                self.chargeSpeedMax = 1.0
                self.throwDistMin = 9999
                self.throwDistMax = 9999
            elif self.role == 'grabber':
                self.punchiness = 1.0
                self.run = True
                self.isGrabber = True            
                self.chargeDistMin = 10.0
                self.chargeDistMax = 9999.0
                self.chargeSpeedMin = 1.0
                self.chargeSpeedMax = 1.0
                self.throwDistMin = 9999
                self.throwDistMax = 9999
            elif self.role == 'charger':
                self.punchiness = 1.0
                self.run = True
                self.chargeDistMin = 10.0
                self.chargeDistMax = 9999.0
                self.chargeSpeedMin = 1.0
                self.chargeSpeedMax = 1.0
                self.throwDistMin = 9999
                self.throwDistMax = 9999
            elif self.role == 'hittler':
                self.punchiness = 0.9
                self.throwiness = 1.0
                self.run = True
                self.chargeDistMin = 4.0
                self.chargeDistMax = 10.0
                self.chargeSpeedMin = 1.0
                self.chargeSpeedMax = 1.0
                self.throwDistMin = 0.0
                self.throwDistMax = 4.0
                self.throwRate = 2.0
            elif self.role == 'crazy':
                self.punchiness = 0.8
                self.throwiness = 1.0
                self.run = True
                self.bouncy = True
                self.chargeDistMin = 10.0
                self.chargeDistMax = 9999.0
                self.chargeSpeedMin = 1.0
                self.chargeSpeedMax = 1.0
                self.throwDistMin = 2
                self.throwDistMax = 9999
                self.throwRate = 10.0
            elif self.role == 'static':
                self.static = True
                self.throwDistMin = 0.0
                self.throwDistMax = 14.0
            elif self.role == 'bouncy':
                self.punchiness = 0.95
                self.run = True
                self.bouncy = True
                self.chargeDistMin = 10.0
                self.chargeDistMax = 9999.0
                self.chargeSpeedMin = 1.0
                self.chargeSpeedMax = 1.0
                self.throwDistMin = 9999
                self.throwDistMax = 9999
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        #If we hit a aggressive Buddy Bot, add the hitter to the bot's target list.
        if isinstance(m,bs.HitMessage):
            if m.sourcePlayer is not None and m.sourcePlayer.exists() and self._aggressive == True:
            	#set the Bot's name
                self.node.name = "Angered"
                self.node.nameColor = (1,0,0)
                BunnyBuddyBot.traitors.append(m.sourcePlayer)
            if BunnyBuddyBot.traitors == []: pass
        
class BunnyBotSet(bsSpaz.BotSet):
    '''
    category: Bot Classes
    
    A container/controller for one or more bs.SpazBots.
    '''
    def __init__(self, sourcePlayer):
        '''
        Create a bot-set.
        '''
        # we spread our bots out over a few lists so we can update them in a staggered fashion
        self._botListCount = 5
        self._botAddList = 0
        self._botUpdateList = 0
        self._botLists = [[] for i in range(self._botListCount)]
        self._spawnSound = bs.getSound('spawn')
        self._spawningCount = 0
        self.startMovingBunnies()
        self.sourcePlayer = sourcePlayer
        

    def doBunny(self):
        self.spawnBot(BunnyBuddyBot, self.sourcePlayer.actor.node.position, 2000, self.setupBunny)

    def startMovingBunnies(self):
        self._botUpdateTimer = bs.Timer(50, bs.WeakCall(self._bUpdate), repeat=True)

    def _spawnBot(self, botType, pos, onSpawnCall):
        spaz = botType(self.sourcePlayer)
        bs.playSound(self._spawnSound, position=pos)
        spaz.node.handleMessage('flash')
        spaz.node.isAreaOfInterest = 0
        spaz.handleMessage(bs.StandMessage(pos, random.uniform(0, 360)))
        self.addBot(spaz)
        self._spawningCount -= 1
        if onSpawnCall is not None: onSpawnCall(spaz)

    def _bUpdate(self):
        #bs.screenMessage(str(self.lastPlayerAttackedBy))
        # update one of our bot lists each time through..
        # first off, remove dead bots from the list
        # (we check exists() here instead of dead.. we want to keep them around even if they're just a corpse)
        try:
            botList = self._botLists[self._botUpdateList] = \
                [b for b in self._botLists[self._botUpdateList] if b.exists()]
        except Exception:
            bs.printException('error updating bot list: '+str(self._botLists[self._botUpdateList]))

        self._botUpdateList = (self._botUpdateList+1)%self._botListCount
        # update our list of attack points for the bots to use
        playerPts = []
        playerPts2 = []
        try:
            #if player.isAlive() and not (player is self.sourcePlayer):
            #    playerPts.append((bs.Vector(*player.actor.node.position),
            #                     bs.Vector(*player.actor.node.velocity)))
            for n in bs.getNodes():
                if n.getNodeType() == 'spaz':
                    s = n.getDelegate()
                   # if isinstance(s, BunnyBuddyBot):
                      #  if bs.getSession().bs.CoopSession: return
                    if isinstance(s, bsSpaz.SpazBot):
                        #if s.isAlive():
                        if not s in self.getLivingBots():
                            if hasattr(s, 'sourcePlayer'):
                                if not s.sourcePlayer is self.sourcePlayer:
                                    playerPts.append((bs.Vector(*n.position), bs.Vector(*n.velocity)))
                                    playerPts2.append((bs.Vector(*n.position), bs.Vector(*n.velocity)))
                            else:
                            	playerPts2.append((bs.Vector(*n.position), bs.Vector(*n.velocity)))
                                playerPts.append((bs.Vector(*n.position), bs.Vector(*n.velocity)))
                    elif isinstance(s, bsSpaz.PlayerSpaz):
                        try:
                            if not (s.getPlayer().getTeam() is self.sourcePlayer.getTeam()):
                                if s.isAlive():
                                    playerPts.append((bs.Vector(*n.position), bs.Vector(*n.velocity)))
                                    playerPts2.append((bs.Vector(*n.position), bs.Vector(*n.velocity)))
                        except:
                            pass
        except Exception:
            bs.printException('error on bot-set _update')
            
        for player in bs.getActivity().players:
            try:
                if player in BunnyBuddyBot.traitors:
                    playerPts2.append((bs.Vector(*player.actor.node.position),
                                     bs.Vector(*player.actor.node.velocity)))
            except Exception:
                bs.printException('error on bot-set _update')
            
        for b in botList:
            b._setPlayerPts(playerPts)
            if b.node.name == "Angered":
            	b._setPlayerPts(playerPts2)
            b._updateAI()

    def setupBunny(self, spaz):
        spaz.sourcePlayer = self.sourcePlayer
        spaz.color = self.sourcePlayer.color
        spaz.highlight = self.sourcePlayer.highlight
        spaz.node.name = self.sourcePlayer.getName()+'\'s Buddy'
