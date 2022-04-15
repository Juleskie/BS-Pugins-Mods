#Made by Froshlee14 Real MAKER
#Changed the code a bit, by Me
import bs
import random

def bsGetAPIVersion():
    return 4

def bsGetGames():
    return [RunningBombsGame] 

class RunningBombsGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Dodgeball'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName':'Survived',
                'scoreType':'milliseconds',
                'scoreVersion':'B'}
    
    @classmethod
    def getDescription(cls,sessionType):
        return 'Don\'t touch the kill zones.'

    # we're currently hard-coded for one map..
    @classmethod
    def getSupportedMaps(cls,sessionType):
        return ['Football Stadium']

    @classmethod
    def getSettings(cls,sessionType):
        return [("Epic Mode",{'default':False}),("Jumping Rope Mode",{'default':True})]
    
    # we support teams, free-for-all, and co-op sessions
    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if (issubclass(sessionType,bs.TeamsSession)
                        or issubclass(sessionType,bs.FreeForAllSession)
                        or issubclass(sessionType,bs.CoopSession)) else False

    def __init__(self,settings):        
        bs.TeamGameActivity.__init__(self,settings)
        if self.settings['Epic Mode']: self._isSlowMotion=True
        self.announcePlayerDeaths = True
        self._lastPlayerDeathTime = None

        #prevent a safe zone from player              
        self.killPlayerRegionMaterial = bs.Material()
        self.killPlayerRegionMaterial.addActions(
            conditions=("theyHaveMaterial",bs.getSharedObject('playerMaterial')),
            actions=(("modifyPartCollision","collide",True),
                     ("modifyPartCollision","physical",False),
                     ("call","atConnect",self._killPlayer)))

        # we need this region because if not exists, the bombs creates a earthquake XD
        self.killBombRegionMaterial = bs.Material()
        self.killBombRegionMaterial.addActions(
            conditions=("theyHaveMaterial",bs.Bomb.getFactory().bombMaterial),
            actions=(("modifyPartCollision","collide",True),
                     ("modifyPartCollision","physical",False),
                     ("call","atConnect",self._killBomb)))

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Epic' if self.settings['Epic Mode'] else 'Scary')

    # called when our game actually starts
    def onBegin(self):

        bs.TeamGameActivity.onBegin(self)

        # set up the two score regions
        self._scoreRegions = []

        defs = self.getMap().defs
        self._scoreRegions.append(bs.NodeActor(bs.newNode('region',
                                                          attrs={'position':defs.boxes['goal1'][0:3],
                                                                 'scale':defs.boxes['goal1'][6:9],
                                                                 'type': 'box',
                                                                 'materials':(self.killPlayerRegionMaterial,)})))
        
        self._scoreRegions.append(bs.NodeActor(bs.newNode('region',
                                                          attrs={'position':defs.boxes['goal2'][0:3],
                                                                 'scale':defs.boxes['goal2'][6:9],
                                                                 'type': 'box',
                                                                 'materials':(self.killBombRegionMaterial,self.killPlayerRegionMaterial)})))

        self._meteorTime = 3000
        t = 7500 if len(self.players) > 2 else 4000
        if self.settings['Epic Mode']: t /= 4
        bs.gameTimer(t,self._decrementMeteorTime,repeat=True)
        t = 3000
        if self.settings['Epic Mode']: t /= 4
        bs.gameTimer(t,self._setMeteorTimer)
        self._timer = bs.OnScreenTimer()
        bs.gameTimer(4000,self._timer.start)

        
    def spawnPlayer(self,player):
        spaz = self.spawnPlayerSpaz(player)
        spaz._impactScale = 0.0 
        spaz.connectControlsToPlayer(enablePunch=False,
                                     enableBomb=False,
                                     enablePickUp=False)
        spaz.playBigDeathSound = True

    def _killPlayer(self):
        regionNode,playerNode = bs.getCollisionInfo('sourceNode','opposingNode')
        try: player = playerNode.getDelegate().getPlayer()
        except Exception: player = None
        region = regionNode.getDelegate()
        if player.exists():
         player.actor.handleMessage(bs.DieMessage())
         player.actor.shatter()
         #bs.screenMessage(bs.Lstr(translate=('statements',"Killing ${NAME} for skipping part of the track!"),subs=[('${NAME}',player.getName(full=True))]),color=(1,0,0))

    def _killBomb(self):
        regionNode,bombNode = bs.getCollisionInfo('sourceNode','opposingNode')
        try: bomb = bombNode.getDelegate()
        except Exception: bomb = None
        region = regionNode.getDelegate()
        if bomb.exists():
         bomb.handleMessage(bs.DieMessage())

    def handleMessage(self,m):
        if isinstance(m,bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self,m) # (augment standard behavior)
            deathTime = bs.getGameTime()           
            # record the player's moment of death
            m.spaz.getPlayer().gameData['deathTime'] = deathTime

            # in co-op mode, end the game the instant everyone dies (more accurate looking)
            # in teams/ffa, allow a one-second fudge-factor so we can get more draws
            if isinstance(self.getSession(),bs.CoopSession):
                # teams will still show up if we check now.. check in the next cycle
                bs.pushCall(self._checkEndGame)
                self._lastPlayerDeathTime = deathTime # also record this for a final setting of the clock..
            else:
                bs.gameTimer(1000,self._checkEndGame)

        else:
            # default handler:
            bs.TeamGameActivity.handleMessage(self,m)

    def _checkEndGame(self):
        livingTeamCount = 0
        for team in self.teams:
            for player in team.players:
                if player.isAlive():
                    livingTeamCount += 1
                    break

        # in co-op, we go till everyone is dead.. otherwise we go until one team remains
        if isinstance(self.getSession(),bs.CoopSession):
            if livingTeamCount <= 0: self.endGame()
        else:
            if livingTeamCount <= 1: self.endGame()
        
    def _setMeteorTimer(self):
        bs.gameTimer(int((1.0+0.5*random.random())*self._meteorTime),self._dropBombCluster)
        
    def _dropBombCluster(self):

        # random note: code like this is a handy way to plot out extents and debug things
        if False:
            bs.newNode('locator',attrs={'position':(8,6,-5.5)})
            bs.newNode('locator',attrs={'position':(8,6,-2.3)})
            bs.newNode('locator',attrs={'position':(-7.3,6,-5.5)})
            bs.newNode('locator',attrs={'position':(-7.3,6,-2.3)})

        # drop several bombs in series..
		
        delay = 0
        for i in range(random.randrange(1,3)):
            # drop them somewhere within our bounds with velocity pointing toward the opposite side
            vel = (-20,2,0)
            bs.gameTimer(delay,bs.Call(self._dropBomb,vel))
            delay += 100
        self._setMeteorTimer()

    def _dropBomb(self,velocity):
    	bombs = 'basketball' #['normal','normal','knocker','normal','fire','normal','normal','healing','normal','ice','normal','normal','normal','normal','tnt','normal','normal','normal']
        x = [-5.2,-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.2,5.3,5.4]
        if self.settings['Jumping Rope Mode']:
         for i in x:
          pos=(13.4,1,i)
          b = bs.Bomb(position=(pos[0],pos[1]-0.2,pos[2]),velocity=velocity,bombType=random.choice(bombs),blastRadius=1).autoRetain()
        else:
         pos=(13.4,1,random.choice(x))
         b = bs.Bomb(position=(pos[0],pos[1]-0.2,pos[2]),velocity=velocity,bombType=random.choice(bombs),blastRadius=1).autoRetain()
 
    def _decrementMeteorTime(self):
        if self.settings['Jumping Rope Mode']:
         self._meteorTime = max(10,int(self._meteorTime*0.9))
        else:
         self._meteorTime = max(10,int(self._meteorTime*0.6))

    def endGame(self):

        curTime = bs.getGameTime()
        
        # mark 'death-time' as now for any still-living players
        # and award players points for how long they lasted.
        # (these per-player scores are only meaningful in team-games)
        for team in self.teams:
            for player in team.players:

                # throw an extra fudge factor +1 in so teams that
                # didn't die come out ahead of teams that did
                if 'deathTime' not in player.gameData: player.gameData['deathTime'] = curTime+1
                    
                # award a per-player score depending on how many seconds they lasted
                # (per-player scores only affect teams mode; everywhere else just looks at the per-team score)
                score = (player.gameData['deathTime']-self._timer.getStartTime())/1000
                if 'deathTime' not in player.gameData: score += 50 # a bit extra for survivors
                self.scoreSet.playerScored(player,score,screenMessage=False)

        # stop updating our time text, and set the final time to match
        # exactly when our last guy died.
        self._timer.stop(endTime=self._lastPlayerDeathTime)
        
        # ok now calc game results: set a score for each team and then tell the game to end
        results = bs.TeamGameResults()

        # remember that 'free-for-all' mode is simply a special form of 'teams' mode
        # where each player gets their own team, so we can just always deal in teams
        # and have all cases covered
        for team in self.teams:

            # set the team score to the max time survived by any player on that team
            longestLife = 0
            for player in team.players:
                longestLife = max(longestLife,(player.gameData['deathTime'] - self._timer.getStartTime()))
            results.setTeamScore(team,longestLife)

        self.end(results=results)
