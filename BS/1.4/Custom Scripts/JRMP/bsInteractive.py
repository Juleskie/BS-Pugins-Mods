import bs
import bsUtils
import bsSpaz
import bsBomb
import bsUtils
import random
import math
from bsVector import Vector

def diceSpawn():
    '''
    Spawn a dice near a random player.
    
    The first time this function is called on a timer is in the bsGame.py file
    Line 2185
    '''
    
    height = 4 # How high the dice has to spawn. Too high can make the dice spawn in OOB area.
    timeToNext = 15 # In Seconds
    
    if not hasattr(bs.getSession(),'_gDiceSpawned'):
        t = bs.newNode('text',
                       attrs={'text':bs.Lstr(resource='diceInfo'),
                              'scale':1.0,
                              'maxWidth':800,
                              'position':(0,200),
                              'shadow':0.5,
                              'flatness':0.5,
                              'hAlign':'center',
                              'vAttach':'bottom'})
        c = bs.newNode('combine',owner=t,attrs={'size':4,'input0':0.2,'input1':1.0,'input2':0.2})
        bsUtils.animate(c,'input3',{3000:0,4000:1,9000:1,10000:0})
        c.connectAttr('output',t,'color')
        bs.gameTimer(10000,t.delete)
        bs.getSession()._gDiceSpawned = True
        
    def _spawnDiceNoPlayers():
        radius = 1.0
        height = 1
        try:
            pos = random.choice(bs.getActivity()._map.powerupSpawnPoints)
            randomDice = bs.Dice(position=(pos[0]+random.uniform(-radius,radius),pos[1]+height,pos[2]+random.uniform(-radius,radius)),velocity=(0,0,0)).autoRetain()
        except AttributeError: pass
        
    if bs.getActivity().players != []: # Pick a random player if one is playing
        alivePlayers = []
        for player in bs.getActivity().players:
            if player.isAlive(): alivePlayers.append(player)
        if alivePlayers == []:
            _spawnDiceNoPlayers()
            return
        randomPlayer = random.choice(alivePlayers)
        player = bs.getActivity()._getPlayerNode(randomPlayer)
        pos = player.position
        radius = 0.1
        randomDice = bs.Dice(position=(pos[0]+random.uniform(-radius,radius),pos[1]+height,pos[2]+random.uniform(-radius,radius)),velocity=(0,0,0)).autoRetain()
    else: _spawnDiceNoPlayers()
    if not isinstance(bs.getSession(),bs.CoopSession): bs.gameTimer(timeToNext*1000,bs.Call(diceSpawn))

class InteractiveFactory(object):
    '''
    category: Game Flow Classes

    Wraps up media and other resources used by bs.Interactives
    A single instance of this is shared between all interactives
    and can be retrieved via bs.Interactive.getFactory().

    Attributes:
    
        platformModel
          The bs.Model of a moving platform.
          
        platformTex
         The bs.Texture for moving platforms
    '''
    
    def getRandomUnpackSound(self): 
        return self.diceUnpackSounds[random.randrange(len(self.diceUnpackSounds))]
    
    def __init__(self):
        '''
        Instantiate a InteractiveFactory.
        You shouldn't need to do this; call bs.Interactive.getFactory() to get a shared instance.
        '''
        
        # Media for moving platforms
        self.platformModel = bs.getModel('platform')
        self.platformTex = bs.getTexture('platformColor')
        self.platformRedTex = bs.getTexture('platformColorRed')
        self.platformMaterial = bs.Material()
        
        self.bumperModel = bs.getModel('bumper')
        self.bumperTex = bs.getTexture('bumperColor')
        self.bumperLitTex = bs.getTexture('bumperColorLit')
        self.bumperSound = bs.getSound('bumperHit')
        
        
        self.diceModel = bs.getModel('dice')
        self.diceTex = bs.getTexture('diceTex')
        self.diceImpactSound = bs.getSound('diceHit')
        self.diceSpawnSound = bs.getSound('diceSpawn')
        self.diceTotalResetSound = bs.getSound('diceReset')
        
        self.shatterSound = bs.getSound('shatter')
        
        self.glueStepSound = bs.getSound('dizzyCakeImpact')
        
        self.burgerModel = bs.getModel('burger')
        self.burgerTex = bs.getTexture('burger')
        
        self.diceUnpackSounds = (bs.getSound('diceUnpack1'),
                                 bs.getSound('diceUnpack2'),
                                 bs.getSound('diceUnpack3'))
                                 
        # Particles models and textures
        self.shrapnelDefaultModel = bs.getModel('shrapnel1')
        self.shrapnelClodModel = bs.getModel('shrapnelClod')
        self.shrapnelSnowModel = bs.getModel('shrapnelSnow')
        self.shrapnelGlitterModel = bs.getModel('glitter')
        self.shrapnelCombatTex = bs.getTexture('shrapnelCombat')
        self.shrapnelCakeTex = bs.getTexture('shrapnelCake')
        self.shrapnelSnowTex = bs.getTexture('shrapnelSnow')
        self.shrapnelGlitterTex = bs.getTexture('bombHealingColor')
        
        self.shrapnelGlueTex = bs.getTexture('shrapnelGlue')
        self.shrapnelGlueFireTex = bs.getTexture('shrapnelGlueFire')
        self.shrapnelGlueIceTex = bs.getTexture('shrapnelGlueIce')
        self.shrapnelMineTex = bs.getTexture('shrapnelMine')
        
        self.ashpileModel = bs.getModel('ashpile')
        self.ashpileTex = bs.getTexture('shrapnelAsh')
        self.candyTex = bs.getTexture('bombHealingColor')
        
        self.diceMaterial = bs.Material()
        self.diceMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('footingMaterial'))),
            actions=(('impactSound',self.diceImpactSound,2,1.0)))
        self.diceMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('platformMaterial'))),
            actions=(('modifyNodeCollision','collide',False),
                    ('modifyPartCollision','physical',False)))
        
        
        self.platformMaterial.addActions(
            conditions=('theyHaveMaterial',bs.getSharedObject('platformMaterial')),
            actions=(('modifyPartCollision','bounce',1.0),
                     ('modifyPartCollision','friction',0.0),
                     ('modifyPartCollision','damping',0.0))) 
                     
        self.glueMaterial = bs.Material()
        self.glueMaterial.addActions(
            actions=(('modifyPartCollision','stiffness',0.1),
                     ('modifyPartCollision','damping',1.0)))
        self.glueMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('playerMaterial')),'or',('theyHaveMaterial',bs.getSharedObject('footingMaterial'))),
            actions=(('message','ourNode','atConnect',SplatMessage())))
                
        self.bounceMaterial = bs.Material()
        self.bounceMaterial.addActions(
            conditions=('theyHaveMaterial', bs.getSharedObject('footingMaterial')),
            actions=(('message', 'ourNode', 'atConnect', 'footing', 1),
                     ('message', 'ourNode', 'atConnect', OnGroundMessage()),
                     ('modifyPartCollision', 'friction', 1),
                     ('message', 'ourNode', 'atDisconnect', 'footing', -1),
                     ('message', 'ourNode', 'atDisconnect', OnGroundMessage())))
                
        self.particleMaterial = bs.Material()
        self.particleMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('footingMaterial'))),
            actions=(('modifyNodeCollision','collide',True)))
        self.particleMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('platformMaterial'))),
            actions=(('modifyNodeCollision','collide',False),
                    ('modifyPartCollision','physical',False)))
        self.particleMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('footingMaterial')),'and',
                        ('theyHaveMaterial',bs.getSharedObject('objectMaterial'))),
            actions=(('modifyNodeCollision','collide',False),
                    ('modifyPartCollision','physical',False)))
        self.particleMaterial.addActions(
            conditions=(('theyDontHaveMaterial',bs.getSharedObject('footingMaterial'))),
            actions=(('modifyNodeCollision','collide',False),
                    ('modifyPartCollision','physical',False)))
        
    def onBegin(self):
        bs.GameActivity.onBegin(self) 

class SplatMessage(object):
    pass     

class OnGroundMessage(object):
    pass     
        
class MovingPlatform(bs.Actor):
    '''
    category: Game Flow Classes

    A platform that hovers in the air, allowing for players to pass large gaps or use them as elevators.
    If they can't move for an amount of time or they reach the maximum altitude, they stand for a bit and change direction.
    '''
    def __init__(self,position=(0,1,0),velocity=(0,0,0)):
        '''
        Instantiate with given values.
        '''
        bs.Actor.__init__(self)

        factory = self.getFactory()
        materials = [factory.platformMaterial,bs.getSharedObject('footingMaterial')]
        
        # Check for current map. We'll configure our moving platform based on that.
        self._map = bs.getActivity()._map.getName()
        
        if self._map == 'Powerup Factory': self._scale = 2.0
        elif self._map == 'Stone-ish Fort': self._scale = 1.9
        else: self._scale = 2.0
        
        self.node = bs.newNode('prop',
                               delegate=self,
                               owner=None,
                               attrs={'position':position,
                                      'velocity':velocity,
                                      'model':factory.platformModel,
                                      'lightModel':factory.platformModel,
                                      'body':'landMine',
                                      'bodyScale':self._scale,
                                      'modelScale':self._scale/2,
                                      'shadowSize':0.25,
                                      'density':2.0,
                                      'gravityScale':2.0,
                                      'colorTexture':factory.platformRedTex if self._map == 'Powerup Factory' else factory.platformTex,
                                      'reflection':'soft',
                                      'reflectionScale':[0.25],
                                      'materials':materials})
        
        # Each map has different gaps, so we should adjust their speed and direction change times for that.
        self.lastposition = self.node.position
        if self._map == 'Powerup Factory': self._moveHorizontal(6,2300)
        elif self._map == 'Stone-ish Fort': self._moveHorizontal(6,3200)
        else: self._moveHorizontal(7,2000)
                                          
    @classmethod
    def getFactory(cls):
        '''
        Returns a shared bs.InteractiveFactory object, creating it if necessary.
        '''
        activity = bs.getActivity()
        try: return activity._sharedInteractiveFactory
        except Exception:
            f = activity._sharedInteractiveFactory = InteractiveFactory()
            return f
    
    def _handleDie(self,m):
        self.node.delete()
        
    def _handleOOB(self,m):
        self.node.position = self.lastposition
            
    def handleMessage(self,m):
        if isinstance(m,bs.DieMessage): self._handleDie(m)
        elif isinstance(m,bs.OutOfBoundsMessage): self._handleOOB(m)
        
    def _moveHorizontal(self,value,time):
        '''
        Moves the platform horizontally back and forth.
        You spawn it in the middle of the path to make it move.
        velocity keeps the platform running and stable
        extraAcceleration makes the platform not slow down
        '''
        v = self.node.velocity
        def _safeSetAttr(node,attr,val):
            if node.exists(): setattr(node,attr,val)
        def _repeatMove():
            bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'velocity',(-value/3,0,0)))
            bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'extraAcceleration',(-value/1.5,0,0)))
            bs.gameTimer(time,bs.Call(_safeSetAttr,self.node,'velocity',(value/3,0,0)))
            bs.gameTimer(time,bs.Call(_safeSetAttr,self.node,'extraAcceleration',(value/1.5,0,0)))
            bs.gameTimer(time*2,bs.Call(_repeatMove))
        bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'velocity',(value/3,0,0)))
        bs.gameTimer(1,bs.Call(_safeSetAttr,self.node,'extraAcceleration',(value/1.5,0,0)))
        bs.gameTimer(time/2,bs.Call(_repeatMove))
                                          
class MovingPlatformSpawner(object):
    '''
    category: Game Flow Classes

    Creates a moving platform at the start of the map
    '''
    def __init__(self,position):
        '''
        Instantiate with a given position, movement behaviour and size
        '''
        self._position = position
        self._platform = MovingPlatform(position=self._position)
        
class Bumper(bs.Actor):
    '''
    category: Game Flow Classes

    Every prop and player that touches it, gets launched in the opposite direction
    '''
    def __init__(self,position=(0,1,0)):
        '''
        Instantiate with given values.
        '''
        bs.Actor.__init__(self)

        factory = self.getFactory()
        
        self.bumperMaterial = bs.Material()
        # Make the bumper truly on the ground
        self.bumperMaterial.addActions(
            conditions=(('theyHaveMaterial', bs.getSharedObject('footingMaterial'))),
            actions=(('modifyPartCollision','stiffness',0.1),
                     ('modifyPartCollision','damping',1.0),
                     ('modifyPartCollision','bounce',0.0)))
        self.bumperMaterial.addActions(
            conditions=((('theyDontHaveMaterial', bs.getSharedObject('footingMaterial'))),'and',(('theyDontHaveMaterial', factory.particleMaterial))),
            actions=(('modifyPartCollision','collide',True),
                     # Make Sticky Bombs unable to stick to the bumpers.
                     ('modifyPartCollision','physical',False),
                     ('modifyPartCollision','bounce',1.0),
                     ('call','atConnect', self.launch)))
        self.bumperMaterial.addActions(
            conditions=(('theyHaveMaterial', factory.particleMaterial)),
            actions=(('modifyPartCollision','collide',False),
                     ('modifyPartCollision','physical',False)))
                     
                                     
        materials = [self.bumperMaterial,bs.getSharedObject('footingMaterial')]
        
        self.node = bs.newNode('prop',
                                   delegate=self,
                                   owner=None,
                                   attrs={'position':position,
                                          'velocity':(0,0,0),
                                          'model':factory.bumperModel,
                                          'lightModel':factory.bumperModel,
                                          'body':'box',
                                          'bodyScale':1.25,
                                          'modelScale':1.25,
                                          'shadowSize':0.5,
                                          'density':4.0,
                                          'gravityScale':2.0,
                                          'colorTexture':factory.bumperTex,
                                          'reflection':'soft',
                                          'reflectionScale':[0.25],
                                          'materials':materials})
        self.bumperLight = bs.newNode('light',
                               owner=self.node,
                               attrs={'position':self.node.position,
                                      'radius':0.0,
                                      'intensity':0.0,
                                      'heightAttenuated':False,
                                      'color': (1.0,0.0,0.0)})
        self.node.connectAttr('position',self.bumperLight,'position')
                                          
    @classmethod
    def getFactory(cls):
        '''
        Returns a shared bs.InteractiveFactory object, creating it if necessary.
        '''
        activity = bs.getActivity()
        try: return activity._sharedInteractiveFactory
        except Exception:
            f = activity._sharedInteractiveFactory = InteractiveFactory()
            return f
            
    def launch(self):
        self.node = bs.getCollisionInfo('sourceNode')
        node = bs.getCollisionInfo('opposingNode')
        factory = self.getFactory()
        
        # Launch stuff depending on what they are
        # Change strength accordingly (player ragdolls are harder to move than bombs)
        if node.getNodeType() == 'spaz': 
            node.handleMessage("knockout", 50.0)
            self.force = 225
            self.teleForce = self.force/8
        else: 
            self.force = 100
            self.teleForce = self.force/3
        
        # Make a juicy animation for the model
        bs.animate(self.node,'modelScale',{0:2.0,
                                           100:1.4,
                                           250:1.25})
        bs.animate(self.bumperLight,'radius',{0:0.25,
                                              250:0.0},loop=False)
        bs.animate(self.bumperLight,'intensity',{0:0.75,
                                                 250:0.0},loop=False)
                                           
        # Make a flashy animation for the texture
        self.node.colorTexture = factory.bumperLitTex
        def litOff(): self.node.colorTexture = factory.bumperTex
        bs.gameTimer(200,litOff)

        # Play a sound effect
        bs.playSound(factory.bumperSound,volume=0.35,position=self.node.position)
        
        # Launch that bastard away from the bumper
        # These calculations are neccessary to make the bumper act more like a knocking back sphere rather than a knocking back box.
        directionX = (node.position[0] - self.node.position[0]) * 1.25
        directionY = node.position[1] - self.node.position[1] + 0.25
        directionZ = (node.position[2] - self.node.position[2]) * 1.25 
        
        calc = math.sqrt(pow(directionX,2)+pow(directionY,2)+pow(directionZ,2))
        calc = (directionX/calc,directionY/calc,directionZ/calc)
        
        node.handleMessage('impulse',self.node.position[0],self.node.position[1],self.node.position[2],
                                node.velocity[0],node.velocity[1],node.velocity[2],
                                self.force,self.teleForce,0,0,calc[0],calc[1],calc[2])
                                    
    def _handleDie(self,m):
        self.node.delete()
        
    def _handleOOB(self,m):
        self.handleMessage(bs.DieMessage())
            
    def handleMessage(self,m):
        if isinstance(m,bs.DieMessage): self._handleDie(m)
        elif isinstance(m,bs.OutOfBoundsMessage): self._handleOOB(m)
        
class BumperSpawner(object):
    '''
    category: Game Flow Classes

    Creates a jump pad at the start of the map
    '''
    def __init__(self,position):
        '''
        Instantiate with a given position, movement behaviour and size
        '''
        self._position = position
        self._bumper = Bumper(position=self._position)

class Dice(bs.Actor):
    '''
    category: Game Flow Classes

    A dice that can be picked up and thrown. 
    Punching the box spawns a random bomb or makes a random event to occur.
    It cannot be destroyed by bombs.
    
    '''
    def __init__(self,position=(0,1,0),velocity=(0,0,0)):
        '''
        Instantiate with given values.
        '''
        bs.Actor.__init__(self)

        factory = self.getFactory()
        materials = [bs.getSharedObject('objectMaterial'),factory.diceMaterial] 
        
        self.node = bs.newNode('prop',
                                   delegate=self,
                                   owner=None,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'model':factory.diceModel,
                                          'lightModel':factory.diceModel,
                                          'body':'crate',
                                          'bodyScale':0.7,
                                          'shadowSize':0.4,
                                          'density':2.0,
                                          'gravityScale':1.0,
                                          'colorTexture':factory.diceTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[0.35],
                                          'materials':materials})
                                          
        bsUtils.animate(self.node,'modelScale',{0:0, 200:1, 260:0.8})
        bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*4),spread=0.5,chunkType='spark')
        bs.emitBGDynamics(position=position,emitType='distortion',spread=1.0)
        bs.playSound(factory.diceSpawnSound,volume=0.5,position=position)
        
        # Expire if you exist for too long
        bs.gameTimer(22000,bs.WeakCall(self._startFlashing))
        bs.gameTimer(25000,bs.WeakCall(self.handleMessage,bs.DieMessage()))
        
    def _startFlashing(self):
        if self.node.exists(): self.node.flashing = True
    
    def unpackDice(self,who):
        '''
        This function allows the dice to drop random things on punching.
        There's a chance for a random event to happen aswell.
        It also generates some VFX and sounds.
        '''
        
        factory = self.getFactory()
        position = self.node.position
        velocity = self.node.velocity
        
        bs.playSound(factory.getRandomUnpackSound(),volume=2.0,position=position)
        try:
            self.playerUnpacked = who.actor # Some events affect the guy who punched the dice. It's good to have it referenced early on just in case.
        except: return
        
        # Do some particles
        bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),spread=0.25,chunkType='spark');
        bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*4),spread=0.25,scale=0.5,chunkType='rock');
        bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*4),spread=0.25,scale=0.5,chunkType='rock');
        
        # Choose a random outcome
        #if bs.getActivity().getName() == 'JRMP Campaign':
        
        #import bsCampaign
        #bsCampaign.CampaignGame.spawnDiceBot(self.node,position)
        
        # If dice effect is used, add to the stats
        bs.statAdd('Dice Effects Initiated')
        
        self.randomEvent = random.randint(0,16)
        #oldY = self.node.extraAcceleration[1]
        
        if self.randomEvent == 0: # It's raining Dice!
            self.text = 'diceEvents.diceRain'
            self.height = 5
            self.radius = 1 # How far from the player the dice can spawn
            
            def spawnDice():
                self.randomPlayer = random.choice(self.getActivity().players)
                self.player = bs.getActivity()._getPlayerNode(self.randomPlayer)
                pos = self.player.position
                dice = bs.Dice(position=(pos[0]+random.randrange(-self.radius,self.radius),pos[1]+self.height,pos[2]+random.randrange(-self.radius,self.radius)),velocity=(0,0,0)).autoRetain()
            
            for i in range(3):
                bs.gameTimer(i*500,bs.Call(spawnDice))
                i += 1
            
        elif self.randomEvent == 1: # Living Injustice!
            self.text = 'diceEvents.living'
            
            # Select a random player from the list of living players and curse them
            alivePlayers = []
            for player in bs.getActivity().players:
                if player.isAlive(): alivePlayers.append(player)
            if alivePlayers == []: pass
            else:
                self.player = random.choice(alivePlayers).actor
                if random.randint(0,1) == 1: self.player.curse()
                else: self.player.handleMessage(bs.HealMessage())
                
        elif self.randomEvent == 2: # Ironskin
            self.text = 'diceEvents.iron'
            self.playerUnpacked.handleMessage(bs.DiceMessage('ironskin',True))
        elif self.randomEvent == 3: # Curse-oh-no!
            self.text = 'diceEvents.overdriveCurse'
            self.playerUnpacked.handleMessage(bs.DiceMessage('overdriveCurse',False))
        elif self.randomEvent == 4: # Curse of the Pig
            self.text = 'diceEvents.pigCurse'
            for i in range(len(self.getActivity().players)):
                try: 
                    self.player = self.getActivity().players[i].actor
                    self.player.handleMessage(bs.DiceMessage('pigCurse',False))
                except: pass
        elif self.randomEvent == 5: # You're on the Viewfinder!
            self.text = 'diceEvents.impactRain'
            self.playerUnpacked.handleMessage(bs.DiceMessage('impactRain',False))
        elif self.randomEvent == 6: # So... cold...
            self.text = 'diceEvents.freeze'
            self.freezeSound = bs.getSound('freeze')
            bs.playSound(self.freezeSound,volume=1.0,position=self.node.position)
            self.playerUnpacked.handleMessage(bs.FreezeMessage())
        elif self.randomEvent == 7: # Good Burger...
            self.text = 'diceEvents.goodBurger'
            self.playerUnpacked.handleMessage(bs.DiceMessage('goodBurger',False))
        elif self.randomEvent == 8: # Human Rocket
            self.text = 'diceEvents.hijumpBoost'
            self.playerUnpacked.handleMessage(bs.DiceMessage('hijumpBoost',True)) 
        elif self.randomEvent == 9: # Total Reset
            self.text = 'diceEvents.totalReset'
            bs.playSound(factory.diceTotalResetSound,volume=1.0,position=self.node.position)
            alivePlayers = []
            for player in bs.getActivity().players:
                if player.isAlive(): alivePlayers.append(player)
            if alivePlayers == []: pass
            else:
                for target in alivePlayers:
                    self.player = target.actor
                    self.player.handleMessage(bs.DiceMessage('totalReset',False))
        elif self.randomEvent == 10: #  Low Gravity!
            self.text = 'diceEvents.lowGravity'
            self.playerUnpacked.handleMessage(bs.DiceMessage('lowGravity',True))
            pass
        elif self.randomEvent == 11:
            self.text = 'diceEvents.powerups'
            self.playerUnpacked.handleMessage(bs.DiceMessage('powerups',True))
            
        elif self.randomEvent == 12:
            self.text = 'diceEvents.bot'
            try: botset = self.getActivity()._hitmenBots
            except: 
                self.getActivity()._hitmenBots = bs.BotSet()
                botset = self.getActivity()._hitmenBots
            self.radius = 1
            self.height = 0
            for x in range(random.choice([2,3,5])):
                self.randomPlayer = random.choice(self.getActivity().players)
                self.player = bs.getActivity()._getPlayerNode(self.randomPlayer)
                pts = self.player.position
                botset.spawnBot(bs.AgentBot, pos=(pts[0]+random.randrange(-self.radius,self.radius),pts[1]+self.height,pts[2]+random.randrange(-self.radius,self.radius)), spawnTime = 1000+1000*x)
            botset.startMoving()
        elif self.randomEvent == 13: # Kaboom
            self.text = 'diceEvents.kaboom'
            self.playerUnpacked.handleMessage(bs.DiceMessage('kaboom',False))
        elif self.randomEvent == 14:
        	self.text = 'diceEvents.iceMeteor'
        	self.playerUnpacked.handleMessage(bs.DiceMessage('iceMeteor',False))
        elif self.randomEvent == 15:
        	p = self.node.position
        	for cav in range(1,5):
        	    bs.BouncyBall((p[0]/cav*1.5,p[1]+(cav*0.55),p[2]*(0.18*cav)),(0,0,0)).autoRetain()
        	self.text = 'diceEvents.bouncyBalls'
        elif self.randomEvent == 16:
            self.text = 'diceEvents.tntPowerups'
            for p in bs.getNodes():
                if p.getNodeType() == 'prop' and isinstance(p.getDelegate(),bs.Powerup):
                    try:
                        def _spawnTNT(pos): bs.Blast(position=pos,
                                                     blastType=random.choice(['normal','grenade']),
                                                     sourcePlayer=self.playerUnpacked.sourcePlayer).autoRetain()
                        p.handleMessage(bs.DieMessage())
                        bs.gameTimer(random.randint(10,500),bs.Call(_spawnTNT,p.position))
                    except: pass
        bsUtils.PopupText((bs.Lstr(resource=self.text)),
                                        color=(0.9,0.9,0.9),
                                        scale=2.0,
                                        position=self.node.position).autoRetain()
                   
                
                                          
    @classmethod
    def getFactory(cls):
        '''
        Returns a shared bs.InteractiveFactory object, creating it if necessary.
        '''
        activity = bs.getActivity()
        try: return activity._sharedInteractiveFactory
        except Exception:
            f = activity._sharedInteractiveFactory = InteractiveFactory()
            return f
            
    def handleMessage(self,m):
        self._handleMessageSanityCheck()
    
        if isinstance(m,bs.DieMessage):
            if self.node.exists():
                if (m.immediate):
                    self.node.delete()
                else:
                    curve = bs.animate(self.node,'modelScale',{0:0.8,100:0})
                    bs.gameTimer(100,self.node.delete)
    
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())
    
        elif isinstance(m,bs.HitMessage):
            # do some effect after punching and die afterwards
            if m.hitType == 'punch':
                self.unpackDice(m.sourcePlayer)
                self.handleMessage(bs.DieMessage())
            #elif m.hitType == '':
            #    self.handleMessage(bs.DieMessage())
        else:
            bs.Actor.handleMessage(self,m)
        
class Particle(bs.Actor):
    
    def __init__(self,position=(0,0,0),velocity=(0,0,0),type='combatFluid',size=1.0,decayTime=7000):
        '''
        Instantiate with given values.
        '''
        bs.Actor.__init__(self)

        factory = self.getFactory()
        materials = [factory.particleMaterial]
        
        # Load stuff
        if type == 'combatFluid':
            model = factory.shrapnelClodModel
            modelScale = 1.0
            body = 'landMine'
            texture = factory.shrapnelCombatTex
            reflection = 'soft'
        elif type == 'landMine':
            model = factory.shrapnelDefaultModel
            modelScale = 1.0
            body = 'landMine'
            texture = factory.shrapnelMineTex
            reflection = 'soft'
        elif type == 'cake':
            model = factory.shrapnelClodModel
            modelScale = 1.0
            body = 'landMine'
            texture = factory.shrapnelCakeTex
            reflection = 'soft'
        elif type == 'petals':
            model = factory.shrapnelGlitterModel
            modelScale = 1.0
            body = 'landMine'
            texture = random.choice([bs.getTexture('spaceBGColor'),bs.getTexture('cartoonBG')])
            reflection = 'powerup'
        elif type == 'snow':
            model = factory.shrapnelSnowModel 
            modelScale = 1.0
            body = 'landMine'
            texture = factory.shrapnelSnowTex
            reflection = 'soft'
        elif type == 'blooms':
            model = factory.ashpileModel
            modelScale = 1.0
            body = 'landMine'
            texture = random.choice([bs.getTexture('spaceBGColor'),bs.getTexture('cartoonBG')])
            reflection = 'powerup'
        elif type == 'glitter':
            model = factory.shrapnelGlitterModel
            modelScale = 1.0
            body = 'landMine'
            texture = factory.shrapnelGlitterTex
            reflection = 'powerup'
        elif type == 'ashpile':
            model = factory.ashpileModel
            modelScale = 1.0
            body = 'landMine'
            texture = factory.ashpileTex
            reflection = 'soft'
        elif type == 'candy':
            model = factory.shrapnelSnowModel
            modelScale = 1.2
            body = 'landMine'
            texture = factory.candyTex
            reflection = 'powerup'
        else:
            raise Exception("invalid particle type: " + type)
            return
        self.type = type
    
        self.node = bs.newNode('prop',
                    delegate=self,
                    owner=None,
                    attrs={'position':position,
                           'velocity':velocity,
                           'model':model,
                           'modelScale':modelScale*size,
                           'lightModel':model,
                           'body':body,
                           'bodyScale':1.0,
                           'shadowSize':0.0000001,
                           'colorTexture':texture,
                           'reflection':reflection,
                           'reflectionScale':[1.0],
                           'materials':materials})
        
        if type == 'ashpile': bsUtils.animate(self.node,"modelScale",{0:0.0,100:modelScale*size, decayTime:0})
        elif type == 'candy': bsUtils.animate(self.node,"modelScale",{0:0.0,100:modelScale*size, decayTime:0})
        else: bsUtils.animate(self.node,"modelScale",{0:modelScale*size, decayTime:0})
        
        # We don't want to spam with particles if it's a low-end machine, like a phone.
        chance = random.random()
        if bs.getEnvironment()['platform'] in ['android','ios']:
            if chance < 0.4: self.handleMessage(bs.DieMessage())
        elif bs.getEnvironment()['platform'] in ['windows','linux','mac']:
            if chance < 0.2: self.handleMessage(bs.DieMessage())
        
        def remove(): self.node.delete
        bs.gameTimer(decayTime,bs.Call(remove))
        
    @classmethod
    def getFactory(cls):
        '''
        Returns a shared bs.InteractiveFactory object, creating it if necessary.
        '''
        activity = bs.getActivity()
        try: return activity._sharedInteractiveFactory
        except Exception:
            f = activity._sharedInteractiveFactory = InteractiveFactory()
            return f
            
    def handleMessage(self,m):
        self._handleMessageSanityCheck()
    
        if isinstance(m,bs.DieMessage):
            if self.node.exists(): self.node.delete()
            
        elif isinstance(m,bs.HitMessage):
            if m.hitSubType == 'fire' and self.type == 'snow':
                self.handleMessage(bs.DieMessage())
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())
            
class BouncyBall(bs.Actor):
    
    def __init__(self,position=(0,0,0),velocity=(0,0,0)):
        '''
        Instantiate with given values.
        '''
        bs.Actor.__init__(self)

        factory = self.getFactory()
        materials = [bs.getSharedObject('objectMaterial'),factory.bounceMaterial]
    
        self.node = bs.newNode('prop',
                    delegate=self,
                    owner=None,
                    attrs={'position':position,
                           'velocity':velocity,
                           'model':bs.getModel('frostyPelvis'),
                           'modelScale':1.2,
                           'lightModel':bs.getModel('frostyPelvis'),
                           'body':'sphere',
                           'bodyScale':1.2,
                           'density':0.6,
                           'gravityScale':1.0,
                           'shadowSize':0.00001,
                           'colorTexture': bs.getTexture('gameCircleIcon'),
                           'reflection':'soft',
                           'reflectionScale':[0.855],
                           'materials':materials})
        
    @classmethod
    def getFactory(cls):
        '''
        Returns a shared bs.InteractiveFactory object, creating it if necessary.
        '''
        activity = bs.getActivity()
        try: return activity._sharedInteractiveFactory
        except Exception:
            f = activity._sharedInteractiveFactory = InteractiveFactory()
            return f
            
    def handleMessage(self,m):
        self._handleMessageSanityCheck()
    
        if isinstance(m,bs.DieMessage):
            if self.node.exists(): self.node.delete()
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())
        elif isinstance(m,OnGroundMessage):
            def bounce_us():
            	if self.node.velocity[1] <= 0.1500: return
                bs.playSound(bs.getSound('bunnyJump'),volume=1.0,position=self.node.position)
                
                vel,pos = self.node.velocity, self.node.position
                self.node.handleMessage('impulse',pos[0],pos[1],pos[2],
                                vel[0],vel[1]+2.0,vel[2],
                                vel[0],2,vel[2],0,0,0,0)
            bs.gameTimer(10,bs.WeakCall(bounce_us))

class Blocker(bs.Actor):
    
    def __init__(self,position=(0,0,0),velocity=(0,0,0),size=0.5,stayput=False):
        '''
        Instantiate with given values.
        '''
        bs.Actor.__init__(self)

    
        self.node = bs.newNode('prop',
                    delegate=self,
                    attrs={'position':position,
                           'velocity':velocity,
                           'model':bs.getModel('tnt'),
                           'lightModel':bs.getModel('tnt'),
                           'body':'crate',
                           'modelScale':size,
                           'bodyScale':size,
                           'density':1.0,
                           'gravityScale':2.0,
                           'shadowSize':0.00001,
                           'colorTexture': bs.getTexture('tntClassic'),
                           'reflection':'soft',
                           'reflectionScale':[0.855],
                           'materials':[]})
            
    def handleMessage(self,m):
        self._handleMessageSanityCheck()
    
        if isinstance(m,bs.DieMessage):
            if self.node.exists(): self.node.delete()
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())

class Glue(bs.Actor):
    
    def __init__(self,position=(0,0,0),velocity=(0,0,0),decayTime=7000):
        '''
        Instantiate with given values.
        '''
        bs.Actor.__init__(self)

        factory = self.getFactory()
        materials = [bs.getSharedObject('objectMaterial'),factory.glueMaterial]
        
        self._lastStickySoundTime = 0
        
        self.state = None
    
        self.node = bs.newNode('prop',
                    delegate=self,
                    owner=None,
                    attrs={'position':position,
                           'velocity':velocity,
                           'model':factory.shrapnelClodModel,
                           'modelScale':1.5,
                           'lightModel':factory.shrapnelClodModel,
                           'body':'sphere',
                           'bodyScale':0.85,
                           'density':1.0,
                           'gravityScale':1.0,
                           'shadowSize':0.1,
                           'sticky':True,
                           'colorTexture': factory.shrapnelGlueTex, # bs.getTexture('bombHealingColor')
                           'reflection':'soft',
                           'reflectionScale':[1.4],
                           'materials':materials})
        
        bs.gameTimer(decayTime,bs.WeakCall(self.handleMessage,bs.DieMessage()))
        
        bsUtils.animate(self.node,"modelScale",{0:0, 250:2.0, 500:1.5, decayTime-200:1.35,decayTime:0})
        
    def spawnIceShrapnel(self):
        # momentary flash of light
        light = bs.newNode('light',
                           attrs={'position':self.node.position,
                                  'radius':0.1,
                                  'heightAttenuated':False,
                                  'color': (0.8,0.8,1.0)})
        
        bs.animate(light,'intensity',{0:3.0, 40:0.1, 80:0.07, 300:0})
        bsUtils.animate(self.node,"modelScale",{0:1.4,300:0})
        bs.gameTimer(300,light.delete)
        bs.gameTimer(300,bs.WeakCall(self.handleMessage,bs.DieMessage()))
        # emit ice chunks..
        bs.emitBGDynamics(position=self.node.position,
                          velocity=self.node.velocity,
                          count=int(random.random()*10.0+10.0),scale=0.5,spread=0.15,chunkType='ice');
        bs.emitBGDynamics(position=self.node.position,
                          velocity=self.node.velocity,
                          count=int(random.random()*10.0+10.0),scale=0.25,spread=0.15,chunkType='ice');

        bs.playSound(self.getFactory().shatterSound,0.5,position=self.node.position)
        
    @classmethod
    def getFactory(cls):
        '''
        Returns a shared bs.InteractiveFactory object, creating it if necessary.
        '''
        activity = bs.getActivity()
        try: return activity._sharedInteractiveFactory
        except Exception:
            f = activity._sharedInteractiveFactory = InteractiveFactory()
            return f
            
    def handleMessage(self,m):
        self._handleMessageSanityCheck()
    
        if isinstance(m,bs.DieMessage):
            if self.node.exists(): self.node.delete()
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())
        elif isinstance(m,bs.HealMessage):
            self.handleMessage(bs.DieMessage())
        elif isinstance(m,bs.HitMessage):
            factory = self.getFactory()
            if self.state == 'ice': self.spawnIceShrapnel()
            else:  
                if m.hitSubType == 'fire':
                    self.state = 'fire'
                    self.node.gravityScale = 1.0
                    self.node.sticky = False
                    self.node.colorTexture = factory.shrapnelGlueFireTex
                    self.node.reflection = 'soft'
                    self.node.materials = [bs.getSharedObject('objectMaterial'),bs.getSharedObject('fireMaterial')]
                elif m.hitSubType == 'cake':
                    self.node.sticky = True
                    self.node.colorTexture = bs.getTexture('bombStickyColor')
                    self.node.reflection = 'soft'
                    self.node.density = 30.0
                elif m.hitSubType == 'candy':
                    self.node.gravityScale = 1.0
                    self.node.sticky = True
                    self.state = 'candy'
                    self.node.colorTexture = bs.getTexture('bombHealingColor')
                    self.node.reflection = 'powerup'
                elif m.hitSubType == 'ranger':
                    self.node.gravityScale = 0.1733005
                    self.node.sticky = False
                    self.node.reflection = 'powerup'
                    self.node.colorTexture = bs.getTexture('white')
                elif m.hitSubType in ['ice','iceMeteor']:
                    def iceTick(): 
                        if self.node.exists(): self.state = 'ice'
                    bs.gameTimer(50,iceTick)
                    self.state = 'startIce'
                    self.node.gravityScale = 1.0
                    self.node.sticky = False
                    self.node.colorTexture = factory.shrapnelGlueIceTex
                    self.node.reflection = 'powerup'
                    self.node.materials = [bs.getSharedObject('objectMaterial'),bs.getSharedObject('iceMaterial')]
                
            self.node.handleMessage("impulse",m.pos[0],m.pos[1],m.pos[2],
                                m.velocity[0],m.velocity[1],m.velocity[2],
                                m.magnitude,m.velocityMagnitude,m.radius,0,m.velocity[0],m.velocity[1],m.velocity[2])
        elif isinstance(m,bs.PickedUpMessage):
            if self.state == 'ice': self.spawnIceShrapnel()
            node = bs.getCollisionInfo("opposingNode")
            if bs.getGameTime() - self._lastStickySoundTime > 2000:
                self._lastStickySoundTime = bs.getGameTime()
                if node.getNodeType() == 'spaz': bs.playSound(self.getFactory().glueStepSound,0.25,position=self.node.position)
                
class StickyNet(bs.Actor):
    
    def __init__(self,position=(0,0,0),velocity=(0,0,0)):
        '''
        Instantiate with given values.
        '''
        bs.Actor.__init__(self)

        factory = self.getFactory()
        materials = [bs.getSharedObject('objectMaterial')]
        
        self._lastStickySoundTime = 0 
        self.pointsForMove = 0
    
        self.node = bs.newNode('prop',
                    delegate=self,
                    owner=None,
                    attrs={'position':position,
                           'velocity':velocity,
                           'model':bs.getModel('landMine'),
                           'modelScale':2, #1.05
                           'lightModel':bs.getModel('landMine'),
                           'body':'crate',
                           'bodyScale':0.79, #0.74
                           'density':9999,
                           'gravityScale':0.75,
                           'shadowSize':0.1,
                           'sticky':True,
                           'colorTexture': bs.getTexture('achievementWall'),
                           'reflection':'soft',
                           'reflectionScale':[0.5],
                           'materials':materials})
    
        bs.gameTimer(25000,bs.WeakCall(self.handleMessage,bs.DieMessage()))
        self.node.extraAcceleration = (0,-15,0)
        bsUtils.animate(self.node,"modelScale",{0:0, 150:1.2}) #1.05
        #bsUtils.animateArray(self.node,"position",3,{0:(p[0],p[1]-1.0,p[2]),150:(p[0],p[1]-1.0,p[2]),350:(p[0],p[1]-1.0,p[2]),450:(p[0],p[1]-1.0,p[2]),690:(p[0],p[1]-1.0,p[2]),990:(p[0],p[1]-1.0,p[2]),1290:(p[0],p[1]-1.0,p[2]),1567:(p[0],p[1]-1.0,p[2]),1900:(p[0],p[1]-1.0,p[2])},loop = False)
        	
        
    @classmethod
    def getFactory(cls):
        '''
        Returns a shared bs.InteractiveFactory object, creating it if necessary.
        '''
        activity = bs.getActivity()
        try: return activity._sharedInteractiveFactory
        except Exception:
            f = activity._sharedInteractiveFactory = InteractiveFactory()
            return f
            
    def handleMessage(self,m):
        self._handleMessageSanityCheck()
    
        if isinstance(m,bs.DieMessage):
            if self.node.exists(): self.node.delete()
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())
        elif isinstance(m,bs.HealMessage):
            self.handleMessage(bs.DieMessage())