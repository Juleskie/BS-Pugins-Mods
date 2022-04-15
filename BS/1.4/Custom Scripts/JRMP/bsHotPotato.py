import bs
import random

def bsGetAPIVersion():
    return 4
    
def bsGetGames():
    return [HotPotatoGame]
    
class Icon(bs.Actor):
        
    def __init__(self,player,position,scale,nameScale=1.0,nameMaxWidth=115.0,shadow=1.0):
        bs.Actor.__init__(self)

        self._player = player
        self._nameScale = nameScale

        self._outlineTex = bs.getTexture('characterIconMask')
        
        icon = player.getIcon()
        self.node = bs.newNode('image',
                               owner=self,
                               attrs={'texture':icon['texture'],
                                      'tintTexture':icon['tintTexture'],
                                      'tintColor':icon['tintColor'],
                                      'vrDepth':400,
                                      'tint2Color':icon['tint2Color'],
                                      'maskTexture':self._outlineTex,
                                      'opacity':1.0,
                                      'absoluteScale':True,
                                      'attach':'bottomCenter'})
        self._nameText = bs.newNode('text',
                                    owner=self.node,
                                    attrs={'text':player.getName(),
                                           'color':bs.getSafeColor(player.getTeam().color),
                                           'hAlign':'center',
                                           'vAlign':'center',
                                           'vrDepth':410,
                                           'maxWidth':nameMaxWidth,
                                           'shadow':shadow,
                                           'flatness':1.0,
                                           'hAttach':'center',
                                           'vAttach':'bottom'})
        self._infectText = bs.newNode('text',
                                     owner=self.node,
                                     attrs={'text':'Marked!',
                                            'color':(1,0.1,0.0),
                                            'hAlign':'center',
                                            'vrDepth':430,
                                            'shadow':1.0,
                                            'flatness':1.0,
                                            'hAttach':'center',
                                            'vAttach':'bottom'})
        self.setPositionAndScale(position,scale)

    def setPositionAndScale(self,position,scale):
        self.node.position = position
        self.node.scale = [70.0*scale]
        self._nameText.position = (position[0],position[1]+scale*52.0)
        self._nameText.scale = 1.0*scale*self._nameScale
        self._infectText.position = (position[0],position[1]-scale*52.0)
        self._infectText.scale = 1.0*scale
        
    def updateForInfection(self):
        if self._player.exists():
            infected = self._player.gameData['infected']
            eliminated = self._player.gameData['eliminated']
        if infected: 
            self._infectText.text = 'Marked!'
            self._nameText.flatness = 0.0
            self.node.color = (1.0,0.7,0.7)
        else: 
            self._infectText.text = ''
            self._nameText.flatness = 1.0
            self.node.color = (1.0,1.0,1.0)
        if eliminated:
            self._nameText.opacity = 0.2
            self.node.color = (0.7,0.3,0.3)
            self.node.opacity = 0.2
        
    def handlePlayerSpawned(self):
        if not self.node.exists(): return
        self.node.opacity = 1.0

    def handlePlayerDied(self):
        if not self.node.exists(): return
        self._infectText.text = 'TIME OUT!'
        bs.animate(self._infectText,'opacity',{0:1.0,1000:0.0})
        bs.animate(self.node,'opacity',{0:1.0,50:0.0,100:1.0,150:0.0,200:1.0,250:0.0,
                                        300:1.0,350:0.0,400:1.0,450:0.0,500:1.0,550:0.2})

class PotatoPlayerSpaz(bs.PlayerSpaz):
    
    def __init__(self, *args, **kwargs):
        
        super(self.__class__, self).__init__(*args, **kwargs)
        
        # infected light
        self.infectionLight = bs.newNode('light',
                               owner=self.node,
                               attrs={'position':self.node.position,
                                      'radius':0.15,
                                      'intensity':0.0,
                                      'heightAttenuated':False,
                                      'color': (1.0,0.0,0.0)})
        bs.animate(self.infectionLight,'radius',{0:0.1,300:0.15,600:0.1},loop=True)
        self.node.connectAttr('positionCenter',self.infectionLight,'position')
        
        # infected timer
        self.infectionTimerOffset = bs.newNode('math', owner=self.node, attrs={
            'input1': (0, 1.2, 0),
            'operation': 'add'})
        
        self.node.connectAttr('torsoPosition', self.infectionTimerOffset, 'input2')
        
        self.infectionTimerText = bs.newNode('text', owner=self.node, attrs={
            'text': "999",
            'inWorld': True,
            'shadow': 0.4,
            'color': (1.0,0.2,0.2,0.0),
            'flatness': 0,
            'scale': 0.02,
            'hAlign': 'center'})
        
        self.infectionTimerOffset.connectAttr('output', self.infectionTimerText, 'position')
    
    def handleMessage(self, m):
        if isinstance(m, bs.HitMessage):
            if not self.node.exists():
                return
            
            # get infected
            if m.sourcePlayer in bs.getActivity().players and m.sourcePlayer.gameData['infected']: 
                if self.sourcePlayer == m.sourcePlayer: pass
                else:
                    bs.getActivity().infect(self.sourcePlayer)
                    bs.getActivity().infectRemove(m.sourcePlayer)
            
            # if we were recently hit, don't count this as another
            # (so punch flurries and bomb pileups essentially count as 1 hit)
            gameTime = bs.getGameTime()
            if self._lastHitTime is None or gameTime - self._lastHitTime > 1000:
                self._numTimesHit += 1
                self._lastHitTime = gameTime

            mag = m.magnitude * self._impactScale
            velocityMag = m.velocityMagnitude * self._impactScale

            damageScale = 0.22

            if m.flatDamage:
                damage = m.flatDamage * self._impactScale
            else:
                # hit it with an impulse and get the resulting damage
                self.node.handleMessage("impulse",m.pos[0],m.pos[1],m.pos[2],
                                        m.velocity[0],m.velocity[1],m.velocity[2],
                                        mag,velocityMag,m.radius,0,m.forceDirection[0],m.forceDirection[1],m.forceDirection[2])

                damage = damageScale * self.node.damage
                self.node.handleMessage("hurtSound")

            # play punch impact sound based on damage if it was a punch
            if m.hitType == 'punch':

                self.onPunched(damage)

                if damage > 500:
                    sounds = self.getFactory().punchSoundsStrong
                    sound = sounds[random.randrange(len(sounds))]
                else: sound = self.getFactory().punchSound
                bs.playSound(sound, 1.0, position=self.node.position)

                # throw up some chunks
                bs.emitBGDynamics(position=m.pos,
                                  velocity=(m.forceDirection[0]*0.5,
                                            m.forceDirection[1]*0.5,
                                            m.forceDirection[2]*0.5),
                                  count=min(10, 1+int(damage*0.0025)), scale=0.3, spread=0.03)

                bs.emitBGDynamics(position=m.pos,
                                  chunkType='sweat',
                                  velocity=(m.forceDirection[0]*1.3,
                                            m.forceDirection[1]*1.3+5.0,
                                            m.forceDirection[2]*1.3),
                                  count=min(30, 1 + int(damage * 0.04)),
                                  scale=0.9,
                                  spread=0.28)
                # momentary flash
                hurtiness = damage*0.003
                hurtiness = min(hurtiness, 750 * 0.003)
                punchPos = (m.pos[0]+m.forceDirection[0]*0.02,
                            m.pos[1]+m.forceDirection[1]*0.02,
                            m.pos[2]+m.forceDirection[2]*0.02)
                flashColor = (1.0, 0.8, 0.4)
                light = bs.newNode("light",
                                   attrs={'position':punchPos,
                                          'radius':0.12+hurtiness*0.12,
                                          'intensity':0.3*(1.0+1.0*hurtiness),
                                          'heightAttenuated':False,
                                          'color':flashColor})
                bs.gameTimer(60, light.delete)


                flash = bs.newNode("flash",
                                   attrs={'position':punchPos,
                                          'size':0.17+0.17*hurtiness,
                                          'color':flashColor})
                bs.gameTimer(60, flash.delete)

            if m.hitType == 'impact':
                bs.emitBGDynamics(position=m.pos,
                                  velocity=(m.forceDirection[0]*2.0,
                                            m.forceDirection[1]*2.0,
                                            m.forceDirection[2]*2.0),
                                  count=min(10, 1 + int(damage * 0.01)), scale=0.4, spread=0.1)
        else: super(self.__class__, self).handleMessage(m)
    
class HotPotatoGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Hot Potato'

    @classmethod
    def getDescription(cls,sessionType):
        return 'A random player gets marked.\nPass the mark to other players.\nMarked player gets eliminated when time runs out.\nLast one standing wins!'
        
    def getInstanceDescription(self):
        return 'Pass the mark to someone else before you explode!'
        
    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if issubclass(sessionType,bs.FreeForAllSession) else False
        
    @classmethod
    def getSupportedMaps(cls,sessionType):
        return bs.getMapsSupportingPlayType("melee")
        
    @classmethod
    def getScoreInfo(cls):
        return {'scoreName':'Survived'}
        
    @classmethod
    def getSettings(cls,sessionType):
        return [("Elimination Timer",{'minValue':1,'default':15,'increment':1}),
                ('Epic Mode',{'default':False})]
                
    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)
        if self.settings['Epic Mode']: self._isSlowMotion = True
        
        self._tickSound = bs.getSound('tick')
        self._dangerTickSound = bs.getSound('punchStamina')
        self._infectedSound = bs.getSound('nightmareSpecialWave')
        self._playerEliminatedSound = bs.getSound('playerDeath')
                
    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Epic' if self.settings['Epic Mode'] else 'Where Eagles Dare')

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self.setupStandardPowerupDrops(enablePowerups=False,enableTNT=False,enableHazards=True)
            
        self._eliminationTimer = None
        self.eliminationTimerDisplay = 0
        
        # end the game if there's only one player
        if len(self.players) < 2:
            self.players[0].getTeam().gameData['survivor'] = True
            self._endGameTimer = bs.Timer(1250,bs.WeakCall(self.endGame))
        else:
            # pick a random player to get the infection
            def startInfect():
                if len(self.players) <= 1: 
                    self.endGame()
                    return
                else: self.infect(random.choice(self.getAlivePlayers()),False)
            self._infectTimer = bs.Timer(2000 if self._isSlowMotion else 4400,startInfect) # infect the first player, sync to music, cause fun
            
        self._updateIcons()
            
    def onPlayerJoin(self, player):

        player.gameData['infected'] = False
        player.getTeam().gameData['survivor'] = False
        player.gameData['fallTimes'] = 0

        # no longer allowing mid-game joiners here... too easy to exploit
        if self.hasBegun():
            player.gameData['eliminated'] = True
            player.gameData['icons'] = []
            bs.screenMessage(bs.Lstr(resource='playerDelayedJoinText',subs=[('${PLAYER}',player.getName(full=True))]),color=(0,1,0))
            return
            
        player.gameData['eliminated'] = False

        # create our icon and spawn
        player.gameData['icons'] = [Icon(player,position=(0,50),scale=0.8)]
        self.spawnPlayer(player)

        # dont waste time doing this until begin
        if self.hasBegun():
            self._updateIcons()
            
    def _updateIcons(self):
        # in free-for-all mode, everyone is just lined up along the bottom
        count = len(self.teams)
        xOffs = 100
        x = xOffs*(count-1) * -0.5
        for i,team in enumerate(self.teams):
            player = team.players[0]
            for icon in player.gameData['icons']:
                icon.setPositionAndScale((x,50),0.8)
                icon.updateForInfection()
            x += xOffs
        
    def infect(self, victim, passing=True):
        victim.gameData['infected'] = True
        victim.actor.infectionLight.intensity = 1.5
        victim.actor.infectionTimerText.color = (victim.actor.infectionTimerText.color[0],
                                                 victim.actor.infectionTimerText.color[1],
                                                 victim.actor.infectionTimerText.color[2],
                                                 1.0)
                                                 
        bs.emitBGDynamics(position=victim.actor.node.position,velocity=victim.actor.node.velocity,count=int(8.0+random.random()*40),scale=1.0,spread=1,chunkType='spark');
                                                 
        if not passing:
            bs.playSound(self._infectedSound, 1.0, victim.actor.node.position)
            self.eliminationTimerDisplay = self.settings['Elimination Timer']
            bs.gameTimer(self.settings['Elimination Timer']*1000, bs.Call(self._infectEliminate))
            self._infectTickTimer = bs.Timer(1000, bs.Call(self._infectTick), repeat=True)
            
        victim.actor.infectionTimerText.text = str(self.eliminationTimerDisplay)
        self._updateIcons()
                                                 
    def infectRemove(self, victim):
        victim.gameData['infected'] = False
        victim.actor.infectionLight.intensity = 0.0
        victim.actor.infectionTimerText.color = (victim.actor.infectionTimerText.color[0],
                                                 victim.actor.infectionTimerText.color[1],
                                                 victim.actor.infectionTimerText.color[2],
                                                 0.0)
        self._updateIcons()
                                                 
    def _infectTick(self):
        target = None
        for player in self.players:
            if player.isAlive(): pass
            if player.gameData['infected']: 
                target = player
                break
                
        if self.eliminationTimerDisplay > 1: 
            if not target: 
                bs.printException("error: tried to update the infection timer for non existent target, this shouldn't happen")
                return
            
            bs.playSound(self._tickSound, 1.0, target.actor.node.position)
            self.eliminationTimerDisplay -= 1
            if self.eliminationTimerDisplay <= 3: bs.playSound(self._dangerTickSound, 1.0, target.actor.node.position)
            target.actor.infectionTimerText.text = str(self.eliminationTimerDisplay)
        else: 
            self.eliminationTimerDisplay -= 1
            self._infectTickTimer = None
                                            
    def _infectEliminate(self):
        target = None
        for player in self.players:
            if player.gameData['infected']: 
                target = player
                break
                
        if not target: 
            bs.printException("error: tried to eliminate a non-existent target, this shouldn't happen")
            return
            
        target.gameData['infected'] = False
        target.gameData['eliminated'] = True
        self._updateIcons()
        
        target.actor.infectionTimerText.text = 'TIME OUT!'
        bs.animate(target.actor.infectionTimerText,'scale',{0:0.01,
                                                             300:0.02,
                                                             800:0.02,
                                                             1200:0.0})
        
        bs.Blast(position=target.actor.node.position,
                 velocity=target.actor.node.velocity,
                 blastRadius=2.0,sourcePlayer=target).autoRetain()
        bs.emitBGDynamics(position=target.actor.node.position,velocity=target.actor.node.velocity,count=int(16.0+random.random()*60),scale=1.5,spread=2,chunkType='spark');
        target.actor.handleMessage(bs.DieMessage(how='infection'))
        target.actor.shatter()
        
        bs.playSound(self._playerEliminatedSound, 1.0)
        
        alivePlayers = self.getAlivePlayers()
        if len(alivePlayers) == 1: 
            alivePlayers[0].getTeam().gameData['survivor'] = True
            self._endGameTimer = bs.Timer(1000 if self._isSlowMotion else 1750,bs.WeakCall(self.endGame))
            return
            
        # find a new victim
        def startInfect():
            if len(self.players) <= 1: 
                self.endGame()
                return
            else: self.infect(random.choice(alivePlayers),False)
        self._infectTimer = bs.Timer(4500,startInfect)
        
    def getAlivePlayers(self):
        alivePlayers = []
        for player in self.players:
            if player.gameData['eliminated']: continue # ignore players who haven't joined yet or have been eliminated
            if player.isAlive(): alivePlayers.append(player)
        return alivePlayers
        
    def spawnPlayer(self, player, oob=False):
        
        position = self.getMap().getFFAStartPosition(self.players)
        position = (position[0],position[1]-0.3,position[2])
        angle = None

        name = player.getName()

        lightColor = bs.getNormalizedColor(player.color)
        displayColor = bs.getSafeColor(player.color, targetIntensity=0.75)

        spaz = PotatoPlayerSpaz(color=player.color,
                             highlight=player.highlight,
                             character=player.character,
                             player=player)
        player.setActor(spaz)
        
        spaz.node.name = name
        spaz.node.nameColor = displayColor
        spaz.connectControlsToPlayer()
        self.scoreSet.playerGotNewSpaz(player, spaz)
        
        # move to the stand position and add a flash of light
        spaz.handleMessage(bs.StandMessage(position, angle if angle is not None else random.uniform(0, 360)))
        t = bs.getGameTime()
        bs.playSound(self._spawnSound, 1, position=spaz.node.position)
        light = bs.newNode('light', attrs={'color': lightColor})
        spaz.node.connectAttr('position', light, 'position')
        bs.animate(light, 'intensity', {0: 0, 250: 1, 500: 0})
        bs.gameTimer(500, light.delete)
        
        # if infected, give it the light, etc
        try: 
            if player.gameData['infected']: self.infect(player)
        except KeyError: pass
        
        # stun the player for a couple of seconds if they died by falling
        # this prevents insta-teleporting around the map by purposefully jumping off cliffs
        # give the marked player some leeway on that front
        if oob: 
            if not player.gameData['infected']: 
                player.gameData['fallTimes'] += 1
                bs.PopupText("Fall Penalty!",
                    color=(1,0.3,0) if player.gameData['fallTimes'] >= 4 else (1,1,0),
                    scale=2.0 if player.gameData['fallTimes'] >= 4 else 1.6,
                    position=spaz.node.position).autoRetain()
                def knock(): spaz.node.handleMessage("knockout", 500.0)
                if player.gameData['fallTimes'] >= 2: bs.gameTimer(1000,knock)
                if player.gameData['fallTimes'] >= 4: bs.gameTimer(2000,knock)
                spaz.node.handleMessage("knockout", 500.0)
        
    # various high-level game events come through this method
    def handleMessage(self, m):
        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self, m) # augment standard behavior
            player = m.spaz.getPlayer()
            
            # if a player gets eliminated, don't respawn
            if m.how == 'infection':
                # if we have any icons, update their state
                for icon in player.gameData['icons']:
                    icon.handlePlayerDied()
                return
            self.spawnPlayer(player, True if m.how=='fall' else False)
        else:
            # default handler:
            super(self.__class__, self).handleMessage(m)

    def endGame(self):
        # game's over - set a score for each team and tell our activity to finish
        ourResults = bs.TeamGameResults()
        for team in self.teams: ourResults.setTeamScore(team,team.gameData['survivor'])
        self.end(results=ourResults)