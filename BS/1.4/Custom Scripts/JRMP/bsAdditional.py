import bs
import bsInternal
import bsGame
import random
import math
import weakref

class NightmareGame(bs.CoopGameActivity):

    tips = ['Are you sure you are brave enough to beat this stage?',
            'Go back to kindergarten! I\'m really serious!',
            'You should bring somebody with you, so I can kick your butt even more!',
            'You can\'t argue with me! I\'m a frickin\' code!',
            'You\'re doomed! Give up now!',
            'self.nightmareCrashGameError()',
            'This minigame is impossible. Why you\'re playing it?',
            '99% of BombSquad players can\'t even compete with me!']

    @classmethod
    def getName(cls):
        return 'Nightmare'

    @classmethod
    def getDescription(cls,sessionType):
        return "Survive the apocalypse!"

    def __init__(self,settings={}):

        settings['map'] = 'Courtyard Night'

        bs.CoopGameActivity.__init__(self,settings)

        # show messages when players die since it matters here..
        self.announcePlayerDeaths = True
        
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
        bs.playMusic('Nightmare')

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
                #The First wave. Let's start simple enough.
                {'entries':[
                        {'type':bs.ToughGuyBot,'point':'Left'},
                        {'type':bs.NinjaBot,'point':'Right'},
                        {'type':bs.ToughGuyBot,'point':'RightUpperMore'} if playerCount > 1 else None,
                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'} if playerCount > 1 else None,
                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                        ]},
                #Melbots incoming!
                {'entries':[
                        {'type':bs.MelBot,'point':'Left'},
                        {'type':bs.MelBot,'point':'Right'},
                        {'type':bs.MelBot,'point':'Top'},
                        {'type':bs.NinjaBot,'point':'Bottom'} if playerCount > 1 else None,
                        {'type':bs.FrostyBotStatic,'point':'TurretTopMiddle'},
                        ]},
                #Lotsa agents on the right. And then one suicide bomber on the left.
                {'entries':[
                        {'type':bs.AgentBot,'point':'TopRight'},
                        {'type':bs.AgentBot,'point':'RightUpperMore'} if playerCount > 1 else None,
                        {'type':bs.AgentBot,'point':'RightUpper'}, 
                        {'type':bs.AgentBot,'point':'RightLower'} if playerCount > 1 else None,
                        {'type':bs.AgentBot,'point':'RightLowerMore'} if playerCount > 2 else None,
                        {'type':bs.AgentBot,'point':'BottomRight'},
                        {'type':'delay','duration':2000},
                        {'type':bs.PirateBot,'point':'Left'},
                        {'type':'delay','duration':3000},
                        {'type':bs.PirateBot,'point':'Right'},
                        ]},
                #Bombs Away!
                {'entries':[
                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddleLeft'},
                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddleRight'},
                        ]},
                #Let the Spy Bots place the traps for you, ok?
                #and also you'll be chased down. To finish you off, I'll throw in some Mels
                {'entries':[
                        {'type':bs.ToughGuyBot,'point':'Left'},
                        {'type':bs.ToughGuyBot,'point':'LeftUpperMore'} if playerCount > 1 else None,
                        {'type':bs.ToughGuyBot,'point':'Right'},
                        {'type':bs.ToughGuyBot,'point':'RightUpperMore'} if playerCount > 1 else None,
                        {'type':bs.ToughGuyBot,'point':'Top'},
                        {'type':'delay','duration':3000},
                        {'type':bs.SpyBot,'point':'Top'},
                        {'type':bs.SpyBot,'point':'Bottom'} if playerCount > 2 else None,
                        {'type':'delay','duration':5000},
                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                        {'type':'delay','duration':7000},
                        {'type':bs.MelBotStatic,'point':'TurretTopMiddle'},
                        {'type':bs.MelBotStatic,'point':'TurretTopLeft'} if playerCount > 1 else None,
                        {'type':bs.MelBotStatic,'point':'TurretTopRight'} if playerCount > 1 else None,
                        {'type':bs.MelBot,'point':'Top'} if playerCount > 2 else None,
                        ]},
                #So many Fat Pigs!
                {'entries':[
                        {'type':bs.NinjaBot,'point':'Bottom'},
                        {'type':bs.MelDuperBot,'point':'Top'},
                        {'type':bs.MelBot,'point':'Left'} if playerCount > 1 else None,
                        {'type':bs.NinjaBot,'point':'Right'} if playerCount > 2 else None,
                        {'type':'delay','duration':2000},
                        {'type':bs.FrostyBotStatic,'point':'TurretTopMiddle'},
                        ]},
                #Party Time!
                {'entries':[
                        {'type':bs.ToughGuyBot,'point':'BottomRight'},
                        {'type':bs.LooieBot,'point':'Bottom'} if playerCount > 2 else None,
                        {'type':bs.ToughGuyBot,'point':'Right'} if playerCount > 1 else None,
                        {'type':bs.ToughGuyBot,'point':'Left'} if playerCount > 1 else None,
                        {'type':bs.ToughGuyBot,'point':'BottomLeft'},
                        {'type':bs.LooieBot,'point':'Top'},
                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'},
                        {'type':bs.MelBotStatic,'point':'TurretBottomLeft'},
                        {'type':bs.MelBotStatic,'point':'TurretBottomRight'},
                        ]},
                # BUNNIEZ
                {'entries':[
                        {'type':bs.BunnyBot,'point':'Right'},
                        {'type':bs.BunnyBot,'point':'Left'},
                        {'type':bs.BunnyBot,'point':'Top'},
                        {'type':bs.BunnyBot,'point':'Bottom'} if playerCount > 1 else None,
                        {'type':bs.BunnyBot,'point':'LeftLowerMore'} if playerCount > 1 else None,
                        {'type':bs.BunnyBot,'point':'RightLowerMore'} if playerCount > 1 else None,
                        {'type':bs.BunnyBot,'point':'Top'} if playerCount > 2 else None,
                        ]},
                #Something
                {'entries':[
                        {'type':bs.AgentBot,'point':'Left'},
                        {'type':bs.AgentBot,'point':'LeftUpperMore'} if playerCount > 1 else None,
                        {'type':bs.AgentBot,'point':'Right'},
                        {'type':bs.AgentBot,'point':'RightUpperMore'} if playerCount > 1 else None,
                        {'type':'delay','duration':3000},
                        {'type':bs.LooieBot,'point':'Top'},
                        {'type':bs.LooieBot,'point':'Bottom' if playerCount > 1 else None},
                        {'type':'delay','duration':5000},
                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                        {'type':'delay','duration':8000},
                        {'type':bs.FrostyBotStatic,'point':'TurretTopMiddle'},
                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'} if playerCount > 1 else None,
                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'} if playerCount > 1 else None,
                        ]},
                #What a smell of frozen kick-ass in the morning!
                {'entries':[
                        {'type':bs.NinjaBot,'point':'BottomRight'},
                        {'type':bs.NinjaBot,'point':'Bottom'} if playerCount > 1 else None,
                        {'type':bs.NinjaBot,'point':'BottomLeft'},
                        {'type':bs.NinjaBot,'point':'Left'},
                        {'type':bs.NinjaBot,'point':'Right'},
                        {'type':bs.FrostyBot,'point':'TurretTopMiddle'},
                        {'type':bs.FrostyBot,'point':'TurretBottomLeft'} if playerCount > 2 else None,
                        {'type':bs.FrostyBot,'point':'TurretBottomRight'} if playerCount > 2 else None,
                        ]},
                # LOOIEZ
                {'entries':[
                        {'type':bs.LooieBot,'point':'Right'},
                        {'type':bs.LooieBot,'point':'Left'},
                        {'type':bs.LooieBot,'point':'Top'},
                        {'type':bs.LooieBot,'point':'Bottom'},
                        {'type':bs.LooieBot,'point':'LeftUpperMore'} if playerCount > 1 else None,
                        {'type':bs.LooieBot,'point':'RightUpperMore'} if playerCount > 2 else None, 
                        {'type':bs.LooieBot,'point':'Left'} if playerCount > 2 else None,
                        {'type':bs.LooieBot,'point':'Right'} if playerCount > 3 else None,
                        ]},
                #MELS MELS MELS MELS MELS MELS
                {'entries':[
                        {'type':bs.MelBotStatic,'point':'TurretTopLeft'},
                        {'type':bs.MelBotStatic,'point':'TurretTopRight'},
                        {'type':bs.MelBotStatic,'point':'TurretBottomLeft'},
                        {'type':bs.MelBotStatic,'point':'TurretBottomRight'},
                        {'type':bs.MelBotStatic,'point':'TurretTopMiddleLeft'},
                        {'type':bs.MelBotStatic,'point':'TurretTopMiddleRight'},
                        ]},
                #Bomb Storm
                {'entries':[
                        {'type':bs.LooieBotShielded,'point':'Bottom'},
                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                        {'type':bs.FrostyBotStatic,'point':'TurretBottomLeft'} if playerCount > 1 else None,
                        {'type':bs.FrostyBotStatic,'point':'TurretBottomRight'},
                        {'type':bs.MelBotStatic,'point':'TurretTopMiddleLeft'},
                        {'type':bs.MelBotStatic,'point':'TurretTopMiddleRight'} if playerCount > 1 else None,
                        ]},
                #BUNNIEZ V2
                {'entries':[
                        {'type':bs.BunnyBot,'point':'Right'},
                        {'type':bs.BunnyBot,'point':'Left'},
                        {'type':bs.BunnyBot,'point':'Top'},
                        {'type':bs.BunnyBot,'point':'Bottom'},
                        {'type':bs.BunnyBot,'point':'LeftUpperMore'},
                        {'type':bs.BunnyBot,'point':'RightUpperMore'},
                        {'type':bs.BunnyBot,'point':'Right'} if playerCount > 1 else None,
                        {'type':bs.BunnyBot,'point':'Left'} if playerCount > 2 else None,
                        {'type':bs.BunnyBot,'point':'Top'} if playerCount > 3 else None,  
                        ]},
                #Tough Guys
                {'entries':[
                        {'type':bs.ToughGuyBotPro,'point':'Left'},
                        {'type':bs.ToughGuyBotPro,'point':'Right'},
                        {'type':bs.AgentBot,'point':'Top'},
                        {'type':bs.AgentBot,'point':'Bottom'},
                        {'type':'delay','duration':3000},
                        {'type':bs.SpyBot,'point':'Right'},
                        {'type':bs.SpyBot,'point':'Left'}  if playerCount > 3 else None,
                        {'type':bs.SpyBot,'point':'Top'} if playerCount > 2 else None,  
                        {'type':'delay','duration':7000},
                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'}, 
                        ]},
                #This is it! The last wave! Let's make it a huge clustefuck of Duper Melbots!
                #Impending doom incoming! (and also suicide bombers)
                {'entries':[
                        {'type':bs.LooieBot,'point':'LeftUpper'},
                        {'type':'delay','duration':1000},
                        {'type':bs.MelDuperBot,'point':'LeftLower'},
                        {'type':bs.MelBot,'point':'LeftLowerMore'} if playerCount > 2 else None,
                        {'type':'delay','duration':4000},
                        {'type':bs.PirateBot,'point':'RightUpper'},
                        {'type':'delay','duration':5000},
                        {'type':bs.MelDuperBot,'point':'RightUpper'},
                        {'type':bs.MelBot,'point':'RightUpperMore'} if playerCount > 2 else None,
                        {'type':'delay','duration':6000},
                        {'type':bs.PirateBot,'point':'Left'} if playerCount > 1 else None,
                        {'type':'delay','duration':7000},
                        {'type':bs.LooieBot,'point':'Right'},
                        {'type':'delay','duration':9000},
                        {'type':bs.LooieBotShielded,'point':'Up'},
                        {'type':bs.LooieBotShielded,'point':'Bottom'},
                        {'type':'delay','duration':11000},
                        {'type':bs.MelBotStatic,'point':'TurretTopLeft'},
                        {'type':bs.MelBotStatic,'point':'TurretTopRight'},
                        {'type':bs.MelBotStatic,'point':'TurretBottomLeft'} if playerCount > 1 else None,
                        {'type':bs.MelBotStatic,'point':'TurretBottomRight'} if playerCount > 1 else None,
                        {'type':bs.MelBotStatic,'point':'TurretTopMiddleLeft'},
                        {'type':bs.MelBotStatic,'point':'TurretTopMiddleRight'},
                        ]}
                ]
        self._dropPowerups(standardPoints=True,powerupType='overdrive')
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
                #unlockStr = bs.Lstr(resource='somethingUnlocked',subs=[('${ITEM}',resource='characterNames.Mictlan')])
                
                self.showZoomMessage(bs.Lstr(resource='survivedText'),scale=1.0,duration=4000)
        
                self.celebrate(20000)
                self._awardAchievement('Make It Through',sound=False)
                bs.gameTimer(baseDelay,bs.WeakCall(self._awardCompletionBonus))
                baseDelay += 1250
                bs.playSound(self._winSound)
                self.cameraFlash()
                bs.playMusic('Nightmare Victory')
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
            self._waveName = bs.Lstr(resource='nWave1')
        elif self._wave == 2:
            self._waveName = bs.Lstr(resource='nWave2')
        elif self._wave == 3:
            self._waveName = bs.Lstr(resource='nWave3')
        elif self._wave == 4:
            self._waveName = bs.Lstr(resource='nWave4')
        elif self._wave == 5:
            self._waveName = bs.Lstr(resource='nWave5')
        elif self._wave == 6:
            self._waveName = bs.Lstr(resource='nWave6')
        elif self._wave == 7:
            self._waveName = bs.Lstr(resource='nWave7')
        elif self._wave == 8:
            self._waveName = bs.Lstr(resource='nWave8')
        elif self._wave == 9:
            self._waveName = bs.Lstr(resource='nWave9')
        elif self._wave == 10:
            self._waveName = bs.Lstr(resource='nWave10')
        elif self._wave == 11:
            self._waveName = bs.Lstr(resource='nWave11')
        elif self._wave == 12:
            self._waveName = bs.Lstr(resource='nWave12')
        elif self._wave == 13:
            self._waveName = bs.Lstr(resource='nWave13')
        elif self._wave == 14:
            self._waveName = bs.Lstr(resource='nWave14')
        elif self._wave == 15:
            self._waveName = bs.Lstr(resource='nWave15')
        elif self._wave == 16:
            self._waveName = bs.Lstr(resource='nWave16')
        else:
            self._waveName = 'Who Cares!?'

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
                                                        'color':(1,0,0,1) if True else (0.7,0.0,0.0,1.0),
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
        super(NightmareGame,self).handleMessage(m)

    def endGame(self):
        # tell our bots to celebrate just to rub it in
        self._bots.finalCelebrate()
        
        self._gameOver = True
        self.doEnd('defeat',delay=2000)
        bs.playMusic('Nightmare Defeat')

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

class MarathonGame(bs.CoopGameActivity):

    tips = ['Are you sure you are brave enough to beat this stage?',
            'Go back to kindergarten! I\'m really serious!',
            'You should bring somebody with you, so I can kick your butt even more!',
            'You can\'t argue with me! I\'m a frickin code!',
            'You\'re doomed! Give up now!',
            'self.nightmareCrashGameError()',
            'This minigame is impossible. Why you\'re playing it?',
            '99% of BombSquad players can\'t even compete with me!']

    @classmethod
    def getName(cls):
        return 'Marathon'

    @classmethod
    def getDescription(cls,sessionType):
        return "Don\'t starve!"

    def __init__(self,settings={}):

        settings['map'] = 'Flapland'

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
        bs.playMusic('Marathon')

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
                            {'type':bs.ToughGuyBot,'spacing':50},
                            {'type':bs.BomberBot,'spacing':50},
                            ] * playerCount)},
                # 4
                {'entries':([
                            {'type':bs.NinjaBot,'spacing':50},
                            ] * playerCount)},
                # 5
                {'entries':([
                            {'type':bs.ToughGuyBot,'spacing':50},
                            ] * playerCount * 2)},
                # 6
                {'entries':([
                            {'type':bs.PirateBot,'spacing':100},
                            {'type':bs.BomberBot,'spacing':50},
                            ] * playerCount)},
                # 7
                {'entries':([
                            {'type':bs.LooieBot,'spacing':50},
                            ] * playerCount)},
                # 8
                {'entries':([
                            {'type':bs.ChickBot,'spacing':50},
                            ] * playerCount)},
                # 9
                {'entries':([
                            {'type':bs.CyborgBot,'spacing':50},
                            ] * playerCount)},  
                # 10
                {'entries':([
                            {'type':bs.ToughGuyBot,'spacing':50},
                            ] * playerCount * 3)},
                # 11
                {'entries':([
                            {'type':bs.LooieBot,'spacing':50},
                            {'type':bs.BomberBot,'spacing':50},
                            ] * playerCount)},
                # 12
                {'entries':([
                            {'type':bs.BomberBot,'spacing':50},
                            {'type':bs.MelBot,'spacing':50},
                            ] * playerCount)},
                # 13
                {'entries':([
                            {'type':bs.ToughGuyBotPro,'spacing':50},
                            ] * playerCount)},
                # 14
                {'entries':([
                            {'type':bs.LooieBot,'spacing':50},
                            {'type':bs.NinjaBot,'spacing':50},
                            ] * playerCount)},
                # 15
                {'entries':([
                            {'type':bs.NinjaBot,'spacing':50},
                            ] * playerCount * 2)},
                # 16
                {'entries':([
                            {'type':bs.AgentBot,'spacing':50},
                            {'type':bs.CyborgBot,'spacing':50},
                            ] * playerCount)},
                # 17
                {'entries':([
                            {'type':bs.ToughGuyBot,'spacing':50},
                            ] * playerCount * 4)}, 
                # 18
                {'entries':([
                            {'type':bs.BomberBot,'spacing':50},
                            {'type':bs.BomberBot,'spacing':50},
                            {'type':bs.LooieBotShielded,'spacing':50},
                            ] * playerCount)},   
                # 19
                {'entries':([
                            {'type':bs.CyborgBot,'spacing':50},
                            ] * playerCount * 2)},  
                # 20
                {'entries':([
                            {'type':bs.AgentBotShielded,'spacing':50},
                            {'type':bs.BomberBot,'spacing':50},
                            ] * playerCount)},
                # 21
                {'entries':([
                            {'type':bs.ToughGuyBot,'spacing':50},
                            {'type':bs.SpyBot,'spacing':50},
                            ] * playerCount)},
                # 22          
                {'entries':([
                            {'type':bs.NinjaBot,'spacing':50},
                            {'type':bs.FrostyBot,'spacing':50},
                            ] * playerCount)},
                # 23
                {'entries':([
                            {'type':bs.PirateBot,'spacing':50},
                            {'type':bs.NinjaBot,'spacing':50},
                            {'type':bs.BomberBot,'spacing':50},
                            ] * playerCount)},
                # 24
                {'entries':([
                            {'type':bs.MelBot,'spacing':50},
                            ] * playerCount * 4)},
                # 25
                {'entries':([
                            {'type':bs.CyborgBot,'spacing':50},
                            {'type':bs.CyborgBot,'spacing':50},
                            {'type':bs.SpyBot,'spacing':50},
                            ] * playerCount)},
                # 26
                {'entries':([
                            {'type':bs.ToughGuyBotPro,'spacing':50},
                            {'type':bs.SpyBot,'spacing':50},
                            ] * playerCount)},
                # 27
                {'entries':([
                            {'type':bs.LooieBotShielded,'spacing':50},
                            {'type':bs.SpyBot,'spacing':50},
                            ] * playerCount)},
                # 28
                {'entries':([
                            {'type':bs.ChickBotPro,'spacing':50},
                            {'type':bs.FrostyBot,'spacing':50},
                            ] * playerCount)},
                # 29
                {'entries':([
                            {'type':bs.CyborgBot,'spacing':50},
                            {'type':bs.ToughGuyBotPro,'spacing':50},
                            ] * playerCount)},  
                # 30
                {'entries':([
                            {'type':bs.MelBot,'spacing':50},
                            {'type':bs.MelBot,'spacing':50},
                            {'type':bs.LooieBot,'spacing':50},
                            ] * playerCount)},
                # 31
                {'entries':([
                            {'type':bs.LooieBotShielded,'spacing':50},
                            {'type':bs.PirateBot,'spacing':50},
                            {'type':bs.FrostyBot,'spacing':50},
                            ] * playerCount)},
                # 32
                {'entries':([
                            {'type':bs.LooieBotShielded,'spacing':50},
                            {'type':bs.AgentBotShielded,'spacing':50},
                            {'type':bs.BomberBotPro,'spacing':50},
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

            if self._wave == 16: self._awardAchievement('Half-Marathon',sound=True)
            won = (self._wave == len(self._waves))

            if won:

                self.showZoomMessage(bs.Lstr(resource='survivedText'),scale=1.0,duration=4000)
                self._awardAchievement('The Full Run',sound=False)
                self.celebrate(20000)
                self.cameraFlash()
                bs.playMusic('Marathon Victory')
                self._gameOver = True

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
        t = 0
        dt = 200
        botAngle = random.random()*360.0

        spawnTime = 500

        offs = 0 # debugging

        wave = self._waves[self._wave-1]


        entries = []

        entries += wave['entries']

        thisTimeBonus = 0
        thisFlawlessBonus = 0

        for info in entries:
            if info is None: continue

            botType = info['type']

            if botType == 'delay':
                spawnTime += info['duration']
                continue
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
        super(MarathonGame,self).handleMessage(m)

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

class ElusiveChallengeGame(bs.CoopGameActivity):

    tips = ['Memorization won\'t save you. You need to play skillfully.',
            'If you fail, you can always try the challenge tomorrow!',
            'Think over your decisions carefully, since you can\'t restart!',
            'Don\'t stall for powerups! Kill \'em all quickly!']

    @classmethod
    def getName(cls):
        return 'Elusive Challenge'

    @classmethod
    def getDescription(cls,sessionType):
        return "You've only got one shot at this!"

    def __init__(self,settings={}):
        
        settings['map'] = 'Courtyard'

        bs.CoopGameActivity.__init__(self,settings)

        # show messages when players die since it matters here..
        self.announcePlayerDeaths = True
        
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
        bs.playMusic('Last Stand')

        self._scoreBoard = bs.ScoreBoard(label=bs.Lstr(resource='scoreText'),scoreSplit=0.5)
        self._gameOver = False
        self._wave = 0
        self._canEndWave = True
        self._score = 0
        self._timeBonus = 0


    def onBegin(self):

        bs.CoopGameActivity.onBegin(self)
        self.setupStandardTimeLimit(190)
        
        playerCount = len(self.players)
        self._dingSound = bs.getSound('dingSmall')
        self._dingSoundHigh = bs.getSound('dingSmallHigh')
        
        import bsUtils
        bsUtils.ControlsHelpOverlay(delay=3000,lifespan=10000,bright=True).autoRetain()
        
        def levelGen():
        
            # try getting the time from an online server
            # if that fails, use device time
            
            time = bs.checkTime()
            seed = int(time['day']) + int(time['month'])*100 + int(time['year'])*10000 + 42
            
            random.seed(seed)
            bs.getConfig()['E63C15'] = seed
            bs.writeConfig()
            
            firstWord = [['Concrete','gray'],
                         ['Misty','gray'],
                         ['Patient','gray'],
                         ['Scrappy','gray'],
                         ['Blueberry','blue'],
                         ['Wavy','blue'],
                         ['Calm','blue'],
                         ['Aerial','blue'],
                         ['Oceanic','blue'],
                         ['Tactical','yellow'],
                         ['Desert','yellow'],
                         ['Focused','yellow'],
                         ['Sandy','yellow'],
                         ['Wonderful','purple'],
                         ['Magical','purple'],
                         ['Euphoric','purple'],
                         ['Magical','purple'],
                         ['Extraordinary','green'],
                         ['Poison','green'],
                         ['Careful','green'],
                         ['Nature','green'],
                         ['Strong','green'],
                         ['Crimson','red'],
                         ['Hellish','red'],
                         ['Fiery','red'],
                         ['Unsure','red'],
                         ['Dangerous','black'],
                         ['Inky','black'],
                         ['Blind','black'],
                         ['Redacted','black'],
                         ['Level Headed','default'],
                         ['Ordinary','default'],
                         ['Plain','default'],
                         ['Average','default']]
            firstWordChoice = random.choice(firstWord)
            
            if firstWordChoice[1] == 'default': color = (1.2,1.17,1.1)
            elif firstWordChoice[1] == 'gray': color = (0.8,0.8,0.8)
            elif firstWordChoice[1] == 'black': color = (0.6,0.6,0.6)
            elif firstWordChoice[1] == 'blue': color = (1.1,1.2,1.4)
            elif firstWordChoice[1] == 'yellow': color = (1.3,1.1,1.0)
            elif firstWordChoice[1] == 'purple': color = (1.1,0.9,1.25)
            elif firstWordChoice[1] == 'green': color = (1.05,1.2,1.0)
            elif firstWordChoice[1] == 'red': color = (1.3,1.13,1.0)
            bs.getSharedObject('globals').tint = color
                               
            secondWord = ['Mayhem','Chaos','Mess','Pizza','Oatmeal','Lagoon','Navy',
                          'Meatballs','Arena','Limbo','Eye','Box','Consequences',
                          'Boogie','Trip','Outskirts','Battle','War','Skirmish','Brawl',
                          'Fight','Challenge','Contest','Hustle','Combat','Bingo']
            
            self._waveName = firstWordChoice[0] + ' ' + random.choice(secondWord)
            
            botTurretVariant = random.choice([bs.BomberBotProStatic,bs.MelBotStatic,bs.FrostyBotStatic])
            
            botFighters = [bs.ToughGuyBot, 
                           bs.NinjaBot, 
                           bs.AliBot,
                           bs.ChickBot,
                           bs.MelBot,
                           bs.CyborgBot,
                           bs.AgentBot, 
                           bs.KnightBot]
            botProFighters = [bs.ToughGuyBotPro,
                              bs.ToughGuyBotPro,
                              bs.NinjaBotPro,
                              bs.ChickBotPro,
                              bs.MelDuperBot,
                              bs.CyborgBotPro,
                              bs.AgentBotShielded, 
                              bs.KnightBotPro]
            
            botFighterVariantNumber = random.randint(0,len(botFighters)-1)
            botFighterVariantNumber2 = random.randint(0,len(botFighters)-1)
            botFighterVariant = botFighters[botFighterVariantNumber]
            botFighterVariant2 = botFighters[botFighterVariantNumber2]
            botFighterVariantPro = botProFighters[botFighterVariantNumber]
            botFighterVariantPro2 = botProFighters[botFighterVariantNumber2]
            
            result = []
            self._presets = [
                                [ # Bots throw bombs from up
                                    {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                                        {'type':botTurretVariant,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotPro,'point':'Bottom'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':botTurretVariant,'point':'TurretTopLeft'},
                                        {'type':botTurretVariant,'point':'TurretTopRight'},
                                        {'type':botTurretVariant,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotPro,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotPro,'point':'TopRight'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':botTurretVariant,'point':'TurretTopLeft'},
                                        {'type':botTurretVariant,'point':'TurretTopRight'},
                                        {'type':botTurretVariant,'point':'TurretBottomLeft'},
                                        {'type':botTurretVariant,'point':'TurretBottomRight'},
                                        {'type':botTurretVariant,'point':'TurretTopMiddleLeft'},
                                        {'type':botTurretVariant,'point':'TurretTopMiddleRight'},
                                        {'type':botTurretVariant,'point':'TurretTopMiddle'},
                                        {'type':botTurretVariant,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':botTurretVariant,'point':'TopRight'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleRight'},
                                        {'type':random.choice([bs.FrostyBotStatic,bs.BomberBotProStaticShielded]),'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotProShielded,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotProShielded,'point':'TopRight'} if len(self.players) > 2 else None,
                                    ]},
                                ],
                                [ # Fighters + bombs
                                    {'entries':[
                                        {'type':botFighterVariant,'point':'Left'},
                                        {'type':botFighterVariant,'point':'Right'},
                                        {'type':botFighterVariant2,'point':'Top'} if len(self.players) > 2 else None,
                                        {'type':botTurretVariant,'point':'TurretTopMiddle'},
                                    ]},
                                    {'entries':[
                                        {'type':botFighterVariant2,'point':'Left'},
                                        {'type':random.choice([botFighterVariant,botFighterVariantPro]),'point':'Top'},
                                        {'type':botFighterVariant2,'point':'Right'},
                                        {'type':botFighterVariant,'point':'Bottom'} if len(self.players) > 2 else None,
                                        {'type':botTurretVariant,'point':'TurretTopMiddle'},
                                    ]},
                                    {'entries':[
                                        {'type':random.choice([botFighterVariant,botFighterVariantPro]),'point':'Left'},
                                        {'type':random.choice([botFighterVariant2,botFighterVariantPro2]),'point':'Top'},
                                        {'type':random.choice([botFighterVariant,botFighterVariantPro]),'point':'Right'},
                                        {'type':botFighterVariant2,'point':'Bottom'} if len(self.players) > 2 else None,
                                        {'type':botTurretVariant,'point':'TurretTopLeft'},
                                        {'type':botTurretVariant,'point':'TurretTopRight'},
                                    ]},
                                    {'entries':[
                                        {'type':random.choice([botFighterVariant,botFighterVariantPro]),'point':'TopRight'},
                                        {'type':random.choice([botFighterVariant,botFighterVariantPro]),'point':'Top'},
                                        {'type':random.choice([botFighterVariant,botFighterVariantPro]),'point':'TopLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                                        {'type':botTurretVariant,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':botFighterVariantPro2,'point':'Bottom'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':botFighterVariant2,'point':'Left'},
                                        {'type':random.choice([botFighterVariant2,botFighterVariantPro2]),'point':'TopLeft'},
                                        {'type':random.choice([botFighterVariant,botFighterVariantPro]),'point':'TopRight'},
                                        {'type':botFighterVariant,'point':'Right'},
                                        {'type':botTurretVariant,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddleLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddleRight'},
                                        {'type':botTurretVariant,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':botFighterVariantPro,'point':'Top'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':botFighterVariantPro,'point':'TopLeft'},
                                        {'type':botFighterVariantPro,'point':'TopRight'},
                                        {'type':botFighterVariantPro2,'point':'BottomRight'},
                                        {'type':botFighterVariantPro2,'point':'BottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                                        {'type':botTurretVariant,'point':'TurretBottomLeft'},
                                        {'type':botTurretVariant,'point':'TurretBottomRight'},
                                        {'type':botFighterVariantPro,'point':'Bottom'} if len(self.players) > 2 else None,
                                    ]},
                                ],
                                [ # Bunnies
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':random.choice(['Top','Left','Right'])},
                                        {'type':botFighterVariant,'point':'Bottom'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':'Right'},
                                        {'type':bs.BunnyBot,'point':'Left'},
                                        {'type':botFighterVariant,'point':'Bottom'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':'Left'},
                                        {'type':botFighterVariant,'point':random.choice(['Top','Bottom'])},
                                        {'type':bs.BunnyBot,'point':'Right'},
                                        {'type':bs.BunnyBot,'point':'Top'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':'TopLeft'},
                                        {'type':bs.BunnyBot,'point':'TopRight'},
                                        {'type':bs.BunnyBot,'point':'BottomRight'},
                                        {'type':bs.BunnyBot,'point':'BottomLeft'},
                                        {'type':botFighterVariant,'point':random.choice(['Top','Bottom'])} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':'TopRight'},
                                        {'type':bs.BunnyBot,'point':'Top'},
                                        {'type':bs.BunnyBot,'point':'TopLeft'},
                                        {'type':botFighterVariantPro,'point':'BottomLeft'},
                                        {'type':botFighterVariantPro,'point':'BottomRight'},
                                        {'type':bs.BomberBot,'point':'TurretTopMiddle'},
                                        {'type':bs.BunnyBot,'point':'Bottom'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':botFighterVariantPro,'point':'TopRight'},
                                        {'type':botFighterVariantPro,'point':'Top'},
                                        {'type':botFighterVariantPro,'point':'TopLeft'},
                                        {'type':bs.BunnyBot,'point':'BottomLeft'},
                                        {'type':bs.BunnyBot,'point':'Bottom'},
                                        {'type':bs.BunnyBot,'point':'BottomRight'},
                                        {'type':bs.BomberBot,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBot,'point':'TurretTopMiddle'}  if len(self.players) > 2 else None,
                                        {'type':bs.BomberBot,'point':'TurretTopRight'},
                                    ]},
                                ],
                                [ # Pirates and other
                                    {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                                        {'type':bs.PirateBot,'point':random.choice(['Left','TopLeft'])},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':random.choice(['Right','TopRight'])},
                                    ]},
                                    {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                                        {'type':bs.PirateBot,'point':'Right'},
                                        {'type':bs.PirateBot,'point':'Left'},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':random.choice(['Top','Bottom'])},
                                    ]},
                                    {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                                        {'type':botFighterVariant,'point':'Left'},
                                        {'type':botFighterVariant,'point':'Right'},
                                        {'type':'delay','duration':1000},
                                        {'type':bs.PirateBot,'point':'Top'},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':'BottomLeft'},
                                        {'type':bs.PirateBot,'point':'BottomRight'},
                                    ]},
                                    {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                                        {'type':botFighterVariant,'point':random.choice(['Left','Right'])},
                                        {'type':random.choice([botFighterVariant,botFighterVariantPro]),'point':random.choice(['Top','Bottom'])},
                                        {'type':botFighterVariant,'point':random.choice(['Left','Right'])},
                                        {'type':'delay','duration':1000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':random.choice(['Top','Bottom'])},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':'BottomLeft'},
                                        {'type':bs.PirateBot,'point':'BottomRight'},
                                    ]},
                                    {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':botFighterVariantPro,'point':'Left'},
                                        {'type':botFighterVariantPro,'point':random.choice(['Top','Bottom'])},
                                        {'type':botFighterVariantPro,'point':'Right'},
                                        {'type':'delay','duration':1000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':random.choice(['Top','Bottom'])},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':'BottomLeft'},
                                        {'type':bs.PirateBot,'point':'BottomRight'},
                                    ]},
                                    {'entries':[
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':'Left'},
                                        {'type':'delay','duration':1000},
                                        {'type':botFighterVariantPro,'point':'RightUpper'},
                                        {'type':botFighterVariantPro,'point':'RightLower'},
                                        {'type':'delay','duration':4000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':'Right'},
                                        {'type':'delay','duration':1000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':'Left'},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':random.choice(['Top','Bottom'])},
                                        {'type':bs.PirateBot,'point':random.choice(['Left','Right'])},
                                        {'type':bs.PirateBot,'point':random.choice(['Top','Bottom'])},
                                        {'type':bs.PirateBot,'point':random.choice(['Left','Right'])},
                                    ]},
                                ],
                                [ # Army Mix
                                    {'entries':[
                                        {'type':botFighterVariant,'point':'TopLeft'},
                                        {'type':botFighterVariant,'point':'TopRight'},
                                        {'type':'delay','duration':2000},
                                        {'type':botFighterVariant2,'point':'Bottom'},
                                        {'type':'delay','duration':1000},
                                        {'type':botFighterVariant,'point':random.choice(['Top','Bottom'])} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':botFighterVariant,'point':random.choice(['Top','Bottom'])},
                                        {'type':botFighterVariant2,'point':'RightLower'},
                                        {'type':botFighterVariant,'point':random.choice(['Top','Bottom'])} if len(self.players) > 2 else None,
                                        {'type':botFighterVariant2,'point':'LeftLower'},
                                    ]},
                                    {'entries':[
                                        {'type':botFighterVariant2,'point':'Left'},
                                        {'type':botFighterVariant,'point':'RightUpper'}, 
                                        {'type':botFighterVariant,'point':'Right'} if len(self.players) > 2 else None,
                                        {'type':botFighterVariant,'point':'RightLower'},
                                        {'type':botFighterVariant,'point':'BottomRight'},
                                        {'type':botFighterVariant2,'point':random.choice(['Left','LeftUpper','LeftLower'])},
                                    ]},
                                    {'entries':[
                                        {'type':botFighterVariantPro2,'point':'Right'},
                                        {'type':botFighterVariant,'point':'LeftUpper'}, 
                                        {'type':botFighterVariant,'point':'Left'} if len(self.players) > 2 else None,
                                        {'type':botFighterVariant,'point':'LeftLower'},
                                        {'type':botFighterVariant,'point':'BottomLeft'},
                                        {'type':botFighterVariantPro2,'point':'Left'},
                                    ]},
                                    {'entries':[
                                        {'type':botFighterVariantPro,'point':'TopLeft'},
                                        {'type':botFighterVariantPro,'point':'TopRight'},
                                        {'type':botFighterVariant2,'point':'RightLower'},
                                        {'type':botFighterVariantPro2,'point':random.choice(['Top','Bottom'])},
                                        {'type':botFighterVariant,'point':'LeftLower'},
                                    ]},
                                    {'entries':[
                                        {'type':botFighterVariantPro2,'point':'TopRight'},
                                        {'type':botFighterVariantPro2,'point':'TopLeft'},
                                        {'type':'delay','duration':5000},
                                        {'type':botFighterVariantPro,'point':'LeftUpper'},
                                        {'type':botFighterVariantPro,'point':'LeftLower'},
                                        {'type':'delay','duration':5000},
                                        {'type':botFighterVariantPro,'point':'Bottom'},
                                        {'type':'delay','duration':3000},
                                        {'type':botFighterVariantPro2,'point':'RightLower'},
                                        {'type':'delay','duration':3000},
                                        {'type':botFighterVariantPro2,'point':'RightUpper'},
                                        {'type':'delay','duration':3000},
                                        {'type':botFighterVariantPro2,'point':'Top'} if len(self.players) > 2 else None,
                                    ]},
                                ]
                            ]
            waves = []
            for wave_number in range(6):
                waves.append(random.choice(self._presets)[wave_number])

            return waves
    
        self._haveTnt = False
        self._excludePowerups = []
        self._waves = levelGen()
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
        s.impactScale = 0.8
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
            bs.Powerup(position=pt,powerupType=bs.Powerup.getFactory().getRandomPowerupType(excludeTypes=self._excludePowerups)).autoRetain()

    def doEnd(self,outcome,delay=0):

        if outcome == 'defeat':
            bs.getConfig()['E5Y2C9'] = 0
            bs.writeConfig()
            self.fadeToRed()

        if bs.getConfig()['Cheats Active'] == True:
            score = None
            failMessage = bs.Lstr(resource='cheaterText')
        elif self._wave >= 2:
            score = self._score
            failMessage = None
        else:
            score = None
            failMessage = bs.Lstr(resource='reachWave5Text')
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
                #unlockStr = bs.Lstr(resource='somethingUnlocked',subs=[('${ITEM}',resource='characterNames.Mictlan')])
                self.stopTimeLimit() # stop the timer - we won
                self.showZoomMessage(bs.Lstr(resource='victoryText'),scale=1.0,duration=4000)
                
                self._awardAchievement('First Timer',sound=False)
                
                try: timesWon = bs.getConfig()['E5Y2C9']
                except Exception: timesWon = 0
                
                timesWon += 1
                if timesWon >= 3: self._awardAchievement('Holy Trinity',sound=False)
                if timesWon >= 7: self._awardAchievement('Seven Levels of Awesome',sound=False)
                
                bs.getConfig()['E5Y2C9'] = timesWon
                bs.writeConfig()
                print timesWon
        
                self.celebrate(20000)
                bs.gameTimer(baseDelay,bs.WeakCall(self._awardCompletionBonus))
                baseDelay += 1250
                bs.playSound(self._winSound)
                self.cameraFlash()
                bs.playMusic('Victory')
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
                                                             'color':(1,1,0,1),
                                                             'shadow':1.0,
                                                             'flatness':1.0,
                                                             'position':(150,-35),
                                                             'scale':0.8,
                                                             'text':bs.Lstr(value='${A}: ${B}',subs=[('${A}',bs.Lstr(resource='timeBonusText')),('${B}',str(self._timeBonus))])}))
        bs.gameTimer(5000,bs.WeakCall(self._startTimeBonusTimer))
                                                             
        self._waveNameText = bs.NodeActor(bs.newNode('text',
                                                 attrs={'vAttach':'top',
                                                        'hAttach':'center',
                                                        'hAlign':'center',
                                                        'vrDepth':-10,
                                                        'color':(0,1,0,1),
                                                        'shadow':1.0,
                                                        'flatness':1.0,
                                                        'position':(-150,-65),
                                                        'scale':1.0,
                                                        'text':self._waveName}))
        
        self._waveText = bs.NodeActor(bs.newNode('text',
                                                 attrs={'vAttach':'top',
                                                        'hAttach':'center',
                                                        'hAlign':'center',
                                                        'vrDepth':-10,
                                                        'color':(1,1,1,1),
                                                        'shadow':1.0,
                                                        'flatness':1.0,
                                                        'position':(-150,-45),
                                                        'scale':1.3,
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
        super(ElusiveChallengeGame,self).handleMessage(m)

    def endGame(self):
        # tell our bots to celebrate just to rub it in
        self._bots.finalCelebrate()
        
        self._gameOver = True
        self.doEnd('defeat',delay=2000)
        bs.playMusic('Nightmare Defeat')

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

def afkKicker():
    roster = bsInternal._getGameRoster()
    for i in roster:
        if i['clientID'] == -1: continue # ignore the host
        
        if not i['clientID'] in bs.getActivity().afkClientList:
            bs.getActivity().afkClientList.append(i['clientID'])
            bs.getActivity().afkTimeoutList.append(bs.getActivity().afkTime)
            continue
            
        if i['players'] == []:
            position = bs.getActivity().afkClientList.index(i['clientID'])
            bs.getActivity().afkTimeoutList[position] -= 1
            if bs.getActivity().afkTimeoutList[position] <= 0: 
                bsInternal._disconnectClient(int(i['clientID']))
                del bs.getActivity().afkClientList[position]
                del bs.getActivity().afkTimeoutList[position]
        else:
            position = bs.getActivity().afkClientList.index(i['clientID'])
            bs.getActivity().afkTimeoutList[position] += 0.1
            if bs.getActivity().afkTimeoutList[position] >= bs.getActivity().afkTime: bs.getActivity().afkTimeoutList[position] = bs.getActivity().afkTime

def myOnBegin(func):
    def wrapper(self):
        self.afkClientList = []
        self.afkTimeoutList = []
        
        try: self.afkTime = bs.getConfig()["AFK Time"]
        except Exception: 
            bs.getConfig()["AFK Time"] = 0
            self.afkTime = 0
        
        if self.afkTime: self.afkCheckTimer = bs.netTimer(1000, afkKicker, True)
        func(self)
    return wrapper

bsGame.Activity.onBegin = myOnBegin(bsGame.Activity.onBegin)
