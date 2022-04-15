import bs
import bsUtils
from bsVector import Vector
import bsSpaz
import random
import math
import weakref


# list of defined bomb shapes
shapes = {}

def getShapes(includeLocked=False):
    import bsInternal
    import bsAchievement
    disallowed = []
    #if not includeLocked:
        #disallowed.append(('Regular','bombNormalPreview'))
        #disallowed.append(('Bumpy','bombBumpyPreview'))
        #disallowed.append(('Pinecone','bombPinePreview'))
        #disallowed.append(('Unusual','bombSpinPreview'))
        #disallowed.append(('Ring','bombRingPreview'))
        #disallowed.append(('Drawing','bombDrawPreview'))
    return [s for s in shapes.keys() if s not in disallowed]
    
class Shape(object):
    """Create and fill out one of these suckers to define a bomb shape appearance"""
    def __init__(self,name):

        self.name = name

        if shapes.has_key(self.name):
            raise Exception("bomb shape name \"" + self.name + "\" already exists.")

        shapes[self.name] = self
        self.iconTexture = ""
        self.shapeModel = ""
        self.explosionSounds = []
        self.reflection = ""
        self.reflectionScale = 1.0
        
class BombFactory(object):
    """
    category: Game Flow Classes

    Wraps up media and other resources used by bs.Bombs
    A single instance of this is shared between all bombs
    and can be retrieved via bs.Bomb.getFactory().

    Attributes:

       bombModel
          The bs.Model of a standard or ice bomb.

       stickyBombModel
          The bs.Model of a sticky-bomb.

       impactBombModel
          The bs.Model of an impact-bomb.

       landMinModel
          The bs.Model of a land-mine.

       tntModel
          The bs.Model of a tnt box.

       regularTex
          The bs.Texture for regular bombs.

       iceTex
          The bs.Texture for ice bombs.

       stickyTex
          The bs.Texture for sticky bombs.

       impactTex
          The bs.Texture for impact bombs.

       impactLitTex
          The bs.Texture for impact bombs with lights lit.

       landMineTex
          The bs.Texture for land-mines.

       landMineLitTex
          The bs.Texture for land-mines with the light lit.

       tntTex
          The bs.Texture for tnt boxes.

       hissSound
          The bs.Sound for the hiss sound an ice bomb makes.

       debrisFallSound
          The bs.Sound for random falling debris after an explosion.

       woodDebrisFallSound
          A bs.Sound for random wood debris falling after an explosion.

       explodeSounds
          A tuple of bs.Sounds for explosions.

       freezeSound
          A bs.Sound of an ice bomb freezing something.

       fuseSound
          A bs.Sound of a burning fuse.

       activateSound
          A bs.Sound for an activating impact bomb.

       warnSound
          A bs.Sound for an impact bomb about to explode due to time-out.

       bombMaterial
          A bs.Material applied to all bombs.

       normalSoundMaterial
          A bs.Material that generates standard bomb noises on impacts, etc.

       stickyMaterial
          A bs.Material that makes 'splat' sounds and makes collisions softer.

       landMineNoExplodeMaterial
          A bs.Material that keeps land-mines from blowing up.
          Applied to land-mines when they are created to allow land-mines to
          touch without exploding.

       landMineBlastMaterial
          A bs.Material applied to activated land-mines that causes them to exlode on impact.

       impactBlastMaterial
          A bs.Material applied to activated impact-bombs that causes them to exlode on impact.

       blastMaterial
          A bs.Material applied to bomb blast geometry which triggers impact events with what it touches.

       dinkSounds
          A tuple of bs.Sounds for when bombs hit the ground.

       stickyImpactSound
          The bs.Sound for a squish made by a sticky bomb hitting something.

       rollSound
          bs.Sound for a rolling bomb.
    """

    def getRandomExplodeSound(self):
        'Return a random explosion bs.Sound from the factory.'
        return self.explodeSounds[random.randrange(len(self.explodeSounds))]
        
    def getRandomGrenadeSound(self):
        'Return a random explosion bs.Sound from the factory.'
        return self.grenadeExplodeSounds[random.randrange(len(self.grenadeExplodeSounds))]
        
    def getRandomTNTExplodeSound(self):
        'Return a random explosion bs.Sound from the factory.'
        return self.tntSounds[random.randrange(len(self.tntSounds))]

    def __init__(self):
        """
        Instantiate a BombFactory.
        You shouldn't need to do this; call bs.Bomb.getFactory() to get a shared instance.
        """

        self.bombModel = bs.getModel('bomb')
        self.shrapnelClodModel = bs.getModel('shrapnelClod')
        self.stickyBombModel = bs.getModel('bombSticky')
        self.impactBombModel = bs.getModel('impactBomb')
        self.landMineModel = bs.getModel('landMine')
        self.combatBombModel = bs.getModel('combatBomb')
        self.miniDynamiteModel = bs.getModel('miniDynamite')
        self.crystalModel = bs.getModel('bombRanger')
        self.dynamiteModel = bs.getModel('dynamitePack')
        self.healingBombModel = bs.getModel('bombHealing')
        self.grenadeBombModel = bs.getModel('bombGrenade')
        self.basketballModel = bs.getModel('bombBasketball')
        self.cakeBombModel = bs.getModel('dizzyCake')
        self.snowballModel = bs.getModel('snowball')
        #Palette Bomb
        self.paletteBombModel = bs.getModel('bomb')
        
        self.tntModel = bs.getModel('tnt')
        self.tntClassicModel = bs.getModel('tntClassic')
        
        self.glueBombModel = bs.getModel('bombGlue')
        self.splashBombModel = bs.getModel('bombBasketball')
        self.glueTex = bs.getTexture('bombGlueColor')
        
        self.teslaPadModel = bs.getModel('teslaPad')
        self.teslaPadTex = bs.getTexture('teslaPadColor')
        self.teslaShieldHitSound = bs.getSound('teslaShieldHit')
        self.teslaShieldIdleSound = bs.getSound('teslaShieldIdle')
        
        self.burgerModel = bs.getModel('burger')
        self.burgerTex = bs.getTexture('burger')
        
        self.regularTex = bs.getTexture('bombColor')
        #gloo
        self.shrapnelGlueTex = bs.getTexture('shrapnelGlue')
        self.iceTex = bs.getTexture('bombColorIce')
        self.rangerTex = bs.getTexture('bombRangerColor')
        self.stickyTex = bs.getTexture('bombStickyColor')
        self.fireTex = bs.getTexture('bombFireColor')
        self.combatTex = bs.getTexture('bombCombatColor')
        self.combatLitTex = bs.getTexture('bombCombatLitColor')
        self.impactTex = bs.getTexture('impactBombColor')
        self.impactLitTex = bs.getTexture('impactBombColorLit')
        self.healingTex = bs.getTexture('bombHealingColor')
        self.snowballTex = bs.getTexture('snowballColor')
        # Palette Bomb
        self.paletteTex = bs.getTexture('logo')
        
        self.landMineTex = bs.getTexture('landMine')
        self.landMineDamagedTex = bs.getTexture('landMineDamaged')
        self.landMineLitTex = bs.getTexture('landMineLit')
        
        self.tntTex = bs.getTexture('tnt')
        self.tntClassicTex = bs.getTexture('tntClassic')
        #Custom Bombs
        self.lightTex = bs.getTexture('aliColor')
        self.scatterBombsTex = bs.getTexture('tntClassic')
        self.radiusTex = bs.getTexture('white')
        self.clusterTex = bs.getTexture('achievementWall')
        self.hunterTex = bs.getTexture('powerupCurse')
        self.splashBombTex = bs.getTexture('cartoonBG')
        
        self.dynamiteTex = bs.getTexture('dynamitePackTex')
        self.basketballTex = bs.getTexture('bombBasketballColor')
        self.knockerTex = bs.getTexture('bombKnockerColor')
        self.cakeTex = bs.getTexture('dizzyCakeColor')
        
        self.nullModel = bs.getModel('zero')
        
        # Magnet Marble stuff
        self.magnetBombModel = bs.getModel('bombMagnet')
        self.magnetTex = bs.getTexture('magnetBombColor')
        self.magnetActivateSound = bs.getSound('magnetActivate')
        self.magnetExpireSound = bs.getSound('magnetTimeOut')
        self.magnetJumpSound = bs.getSound('magnetJump')
        self.magnetMumbleSounds = (bs.getSound('magnetMumble1'),
                                    bs.getSound('magnetMumble2'),
                                    bs.getSound('magnetMumble3'))
                                    
        self.landMineDamageSound = bs.getSound('landMineDamage')
        
        # Grenade Textures
        self.grenade3Tex = bs.getTexture('grenadeColor3') # 3 second fuse
        self.grenade2Tex = bs.getTexture('grenadeColor2') # 2 second fuse
        self.grenade1Tex = bs.getTexture('grenadeColor1') # 1 second fuse
        self.grenadeExTex = bs.getTexture('grenadeColorEx') # Just before explosion

        self.healingSound = bs.getSound('healingExplosion')
        self.hissSound = bs.getSound('hiss')
        self.overdriveExplosionSound = bs.getSound('overdriveExplosion')
        self.debrisFallSound = bs.getSound('debrisFall')
        self.woodDebrisFallSound = bs.getSound('woodDebrisFall')
        self.metalDebrisFallSound = bs.getSound('metalDebrisFall')
        self.pinOutSound = bs.getSound('grenadePinOut')
        self.glueImpactSound = bs.getSound('glueImpact')
        self.hijumpSound = bs.getSound('hijump')
        self.dynamiteFuseSound = bs.getSound('fuseDynamite')
        
        # Ranger Bomb sounds
        self.crystalChargeSound = bs.getSound('crystalCharge')
        self.crystalBeatSound = bs.getSound('crystalBeat')
        self.crystalDinkSound = bs.getSound('crystalHit')
        self.crystalExplosionSound = bs.getSound('crystalExplosion')
        
        # Dizzy cake Sounds
        self.cakeSpawnSound = bs.getSound('dizzyCakePull')
        self.cakeImpactSound = bs.getSound('dizzyCakeImpact')
        self.cakeExplosionSound = bs.getSound('dizzyCakeExplode')
        self.cake1Sound = bs.getSound('dizzyCake1')
        self.cake2Sound = bs.getSound('dizzyCake2')
        self.cake3Sound = bs.getSound('dizzyCake3')
        self.cake4Sound = bs.getSound('dizzyCake4')
        self.cake5Sound = bs.getSound('dizzyCake5')
        self.cake6Sound = bs.getSound('dizzyCake6')
        self.cake7Sound = bs.getSound('charSelectFFAMusic')
        
        # Combat Bomb sounds
        self.combatBombDeployedSound = bs.getSound('combatBombDeployed')
        self.combatBombReadySound = bs.getSound('combatBombReady')
        self.combatExplosionSound = bs.getSound('combatBombExplosion')
        
        # Grenade Explosions
        self.grenadeExplodeSounds = (bs.getSound('grenadeExplosion01'),
                              bs.getSound('grenadeExplosion02'),
                              bs.getSound('grenadeExplosion03'))

        self.explodeSounds = (bs.getSound('explosion01'),
                              bs.getSound('explosion02'),
                              bs.getSound('explosion03'),
                              bs.getSound('explosion04'),
                              bs.getSound('explosion05'))
        self.snowballSounds = (bs.getSound('snowball1'),
                               bs.getSound('snowball2'))
        self.explodeBuffedSound = bs.getSound('explosionBuffed')
        self.knockerExplosionSound = bs.getSound('knockerExplosion')
                              
        self.tntSounds = (bs.getSound('tntExplode1'),
                              bs.getSound('tntExplode2'),
                              bs.getSound('tntExplode3'))

        self.freezeSound = bs.getSound('freeze')
        self.fireSound = bs.getSound('fire')
        self.fuseSound = bs.getSound('fuse01')
        self.activateSound = bs.getSound('activateBeep')
        self.warnSound = bs.getSound('warnBeep')
        self.paletteExplosionSound = bs.getSound('laser')

        # set up our material so new bombs dont collide with objects
        # that they are initially overlapping
        self.bombMaterial = bs.Material()
        self.normalSoundMaterial = bs.Material()
        self.crystalSoundMaterial = bs.Material()
        self.basketballSoundMaterial = bs.Material()
        self.cakeSoundMaterial = bs.Material()
        self.stickyMaterial = bs.Material()

        self.bombMaterial.addActions(
            conditions=((('weAreYoungerThan',100),'or',('theyAreYoungerThan',100)),
                        'and',('theyHaveMaterial',bs.getSharedObject('objectMaterial'))),
            actions=(('modifyNodeCollision','collide',False)))
        
        # don't collide with the invisible platform, but collide with the platform itself
        self.bombMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('platformMaterial')),
                       'and',('theyDontHaveMaterial',bs.getSharedObject('footingMaterial'))),
            actions=(('modifyNodeCollision','collide',False),
                     ('modifyPartCollision','physical',False)))

        # we want pickup materials to always hit us even if we're currently not
        # colliding with their node (generally due to the above rule)
        self.bombMaterial.addActions(
            conditions=('theyHaveMaterial',bs.getSharedObject('pickupMaterial')),
            actions=(('modifyPartCollision','useNodeCollide',False)))
        
        self.bombMaterial.addActions(actions=('modifyPartCollision','friction',0.3))

        self.landMineNoExplodeMaterial = bs.Material()
        self.landMineBlastMaterial = bs.Material()
        self.landMineBlastMaterial.addActions(
            conditions=(('weAreOlderThan',200),
                        'and',('theyAreOlderThan',200),
                        'and',('evalColliding',),
                        'and',(('theyDontHaveMaterial',self.landMineNoExplodeMaterial),
                               'and',(('theyHaveMaterial',bs.getSharedObject('objectMaterial')),
                                      'or',('theyHaveMaterial',bs.getSharedObject('playerMaterial')),
                                      'or',('theyHaveMaterial',self.bombMaterial)))),
            actions=(('message','ourNode','atConnect',ImpactMessage())))
        
        self.teslaMaterial = bs.Material()
        self.teslaBarrierMaterial = bs.Material()
        self.teslaBarrierMaterial.addActions(
            conditions=(('evalNotColliding',),'and',('theyHaveMaterial',self.bombMaterial),'and',('theyDontHaveMaterial',self.teslaMaterial)),
            #actions=(('modifyPartCollision','collide',True),
            #         ('modifyPartCollision','physical',False),
            #('message','theirNode','atConnect',bs.TeslaMessage(1))))
            actions=(('modifyPartCollision','collide',True),
                     ('modifyPartCollision','physical',True),
                     ('modifyPartCollision','bounce',1),
                     ('modifyPartCollision','stiffness',1),
                     ('modifyPartCollision','friction',0),
                     ('message','theirNode','atConnect',bs.TeslaMessage(1))))
            
        self.magnetBlastMaterial = bs.Material()
        self.magnetMaterial = bs.Material()
        self.magnetBlastMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('playerMaterial'))),
            actions=(('message','ourNode','atConnect',ImpactMessage())))
            
        self.magnetMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('footingMaterial')),'or',('theyHaveMaterial',bs.getSharedObject('objectMaterial'))),
            actions=(('modifyPartCollision','friction',1.0),
                     ('modifyPartCollision','stiffness',0.1),
                     ('modifyPartCollision','damping',1.0),
                     ('message','ourNode','atConnect',ArmMessage())))
        
        
        self.impactBlastMaterial = bs.Material()
        self.impactBlastMaterial.addActions(
            conditions=(('weAreOlderThan',200),
                        'and',('theyAreOlderThan',200),
                        'and',('evalColliding',),
                        'and',(('theyHaveMaterial',bs.getSharedObject('footingMaterial')),
                               'or',('theyHaveMaterial',bs.getSharedObject('objectMaterial')))),
            actions=(('message','ourNode','atConnect',ImpactMessage())))
        

        self.blastMaterial = bs.Material()
        self.blastMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('objectMaterial'))),
            actions=(('modifyPartCollision','collide',True),
                     ('modifyPartCollision','physical',False),
                     ('message','ourNode','atConnect',ExplodeHitMessage())))

        self.dinkSounds = (bs.getSound('bombDrop01'),
                           bs.getSound('bombDrop02'))
        self.basketballHitSound = (bs.getSound('basketballHit'))
        self.stickyImpactSound = bs.getSound('stickyImpact')
        self.stickyImpactPlayerSound = bs.getSound('stickyImpactPlayer')
        

        self.rollSound = bs.getSound('bombRoll01')

        # collision sounds
        self.normalSoundMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('footingMaterial'))),
            actions=(('impactSound',self.dinkSounds,1,0.6),
                     ('rollSound',self.rollSound,3,0.2)))
                     
        self.crystalSoundMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('footingMaterial')),'or',('theyHaveMaterial',bs.getSharedObject('platformMaterial'))),
            actions=(('impactSound',self.crystalDinkSound,2,0.8)))
                     
        self.basketballSoundMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('footingMaterial')),'or',('theyHaveMaterial',bs.getSharedObject('platformMaterial'))),
            actions=(('impactSound',self.basketballHitSound,2,0.8),
                     ('rollSound',self.rollSound,0,0)))
                     
        self.cakeSoundMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('footingMaterial')),'or',('theyHaveMaterial',bs.getSharedObject('platformMaterial'))),
            actions=(('impactSound',self.cakeImpactSound,1,0.8)))

        self.stickyMaterial.addActions(
            actions=(('modifyPartCollision','stiffness',0.1),
                     ('modifyPartCollision','damping',1.0)))

        self.stickyMaterial.addActions(
            conditions=(('theyHaveMaterial',bs.getSharedObject('playerMaterial')),'or',('theyHaveMaterial',bs.getSharedObject('footingMaterial'))),
            actions=(('message','ourNode','atConnect',SplatMessage())))
            
        self.bombShapeMedia = {}
        
    def _getMedia(self,shape):

        t = shapes[shape]
        if not self.bombShapeMedia.has_key(shape):
            m = self.bombShapeMedia[shape] = {
                'iconTexture':bs.getTexture(t.iconTexture),
                'shapeModel':bs.getModel(t.shapeModel),
                'explosionSounds':[bs.getSound(s) for s in t.explosionSounds],
                'explosionVolume':float(t.explosionVolume),
                'reflection':str(t.reflection),
                'reflectionScale':int(t.reflectionScale),
            }
        else:
            m = self.bombShapeMedia[shape]
        return m

class SplatMessage(object):
    pass

class ExplodeMessage(object):
    pass

class ImpactMessage(object):
    """ impact bomb touched something """
    pass
    
class TeslaMessage(object):
    """ a  bomb touched a tesla shield """
    pass

class ArmMessage(object):
    pass

class WarnMessage(object):
    pass
    
class DeployMessage(object):
    """ combat bomb is pulled out """
    pass

class ReadyMessage(object):
    """ combat bomb is about to explode """
    pass
    
class HealMessage(object):
    """ removes bombs without destroying them (works in collaboration with a Healing Bomb) """
    pass
    
class DizzyMessage(object):
    """ forces players and bots to make random inputs (Dizzy cake explosion) """
    pass   
    
class ExplodeHitMessage(object):
    "Message saying an object was hit"
    def __init__(self):
        pass

class Blast(bs.Actor):
    """
    category: Game Flow Classes

    An explosion, as generated by a bs.Bomb.
    """
    def __init__(self,position=(0,1,0),velocity=(0,0,0),blastRadius=2.0,blastType="normal",blastRadiusBuffed=False,sourcePlayer=None,hitType='explosion',hitSubType='normal',hitSubTypeTrue=True):
        """
        Instantiate with given values.
        """
        bs.Actor.__init__(self)

        
        factory = Bomb.getFactory()

        self.blastType = blastType
        self.sourcePlayer = sourcePlayer
        
        self.blastRadiusBuffed = blastRadiusBuffed

        self.hitType = hitType;
        self.hitSubType = hitSubType;

        # blast radius
        self.radius = blastRadius
        
        if self.blastType == 'knocker':
            self.node = bs.newNode('region',
                               attrs={'position':(position[0],position[1]-0.5,position[2]), # move down a bit so we throw more stuff upward
                                      'scale':(self.radius,self.radius+0.25,self.radius),
                                      'type':'sphere',
                                      'materials':(factory.blastMaterial,bs.getSharedObject('attackMaterial'))},
                               delegate=self)
        elif self.blastType in ['miniDynamite','dynamite']:
            self.node = bs.newNode('region',
                               attrs={'position':(position[0],position[1]+0.25,position[2]),
                                      'scale':(self.radius,self.radius,self.radius),
                                      'type':'sphere',
                                      'materials':(factory.blastMaterial,bs.getSharedObject('attackMaterial'))},
                               delegate=self)
        elif self.blastType == 'hijump':
            self.node = bs.newNode('region',
                               attrs={'position':(position[0],position[1]-0.5,position[2]), # move down a bit so we can damage players below easier
                                      'scale':(self.radius,self.radius,self.radius),
                                      'type':'sphere',
                                      'materials':(factory.blastMaterial,bs.getSharedObject('attackMaterial'))},
                               delegate=self)
        elif self.blastType == 'fraction':
            self.node = bs.newNode('region',
                               attrs={'position':(position[0],position[1]-0.5,position[2]), # move down a bit so we can damage players below easier
                                      'scale':(self.radius,self.radius,self.radius),
                                      'type':'box',
                                      'materials':(factory.blastMaterial,bs.getSharedObject('attackMaterial'))},
                               delegate=self)
        elif self.blastType != ['fake']:
            self.node = bs.newNode('region',
                               attrs={'position':(position[0],position[1]-0.1,position[2]), # move down a bit so we throw more stuff upward
                                      'scale':(self.radius,self.radius,self.radius),
                                      'type':'sphere',
                                      'materials':(factory.blastMaterial,bs.getSharedObject('attackMaterial'))},
                               delegate=self)

        bs.gameTimer(50,self.node.delete)

        # throw in an explosion and flash
        explosion = bs.newNode("explosion", attrs={
            'position':position,
            'velocity':(velocity[0],max(-1.0,velocity[1]),velocity[2]),
            'radius':self.radius,
            'big':(self.blastType in ['tnt','tntC'] or self.blastType == 'ranger' or self.blastType == 'grenade')})
                                      
        if self.blastType in ["ice","snowball","iceMeteor"]:
            explosion.color = (0,0.05,0.4)
            
        if self.blastType == "fire":
            explosion.color = (1.25,0.8,0.8)
            
        if self.blastType == "infatuate":
            explosion.color = (1.4,0.7,0.8)
            
        if self.blastType == "fraction":
            explosion.color = (0,10,10)
  
        if self.blastType == "palette":
            self.paletteColor = (random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]),
                                          random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]),
                                         random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]))
            explosion.color = self.paletteColor #random.choice(self.colors)  

        if self.blastType == "burger":
            explosion.color = (1.0,0.1,0.1)    
            
        if self.blastType == "scatter":
            explosion.color = (1.0,0.4,0.2)
            
        if self.blastType == "ranger":
            explosion.color = (1,1,0)
            
        if self.blastType == "overdrive":
            explosion.color = (0.8,0.36,0.4)
            
        if self.blastType == "cluster":
            explosion.color = (0.5,0.5,0.5)
            
        if self.blastType == "cake":
            self.colors = [(1,0.15,0.15),(1,1,0),(1,0.3,0.5),(0.2,1,0.2),(0.5,0.25,1.0)]
            self.cakeColor = random.choice(self.colors)
            explosion.color = self.cakeColor
            
        if self.blastType == "combat":
            explosion.color = (0,0,1)
            
        if self.blastType == "knocker":
            explosion.color = (0.2,0.2,0.6)
            
        if self.blastType == "tesla":
            explosion.color = (0.2,0.4,0.2)
            
        if self.blastType in ["firework","fireworkE"]:
            explosion.color = (random.uniform(0.2,1.35),random.uniform(0.2,1.35),random.uniform(0.2,1.35))
            
        if self.blastType == "instant":
            explosion.color = (1.4,0.2,0.2)
            
        if self.blastType == "tnt":
            explosion.color = (0,1,0)
            
        if self.blastType == "splash":
            explosion.color = (0.95,0.7,1.25)
            
        if self.blastType == "healing":
            explosion.color = (1,0,0.3)
            
        if self.blastType == "hunter":
            explosion.color = (1.0,0.4,0.17)
            
        if self.blastType == "hijump":
            explosion.color = (1,0.01,0.95)
            
        if self.blastType == "gloo":
            explosion.color = (0.0,0.0,0.0)
            

        if not self.blastType in ['ice','snowball']: bs.emitBGDynamics(position=position,velocity=velocity,count=int(1.0+random.random()*4),emitType='tendrils',tendrilType='thinSmoke')
        if self.blastType != 'combat' and self.blastType != 'knocker': bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*4),emitType='tendrils',tendrilType='ice' if self.blastType in ['ice','snowball'] else 'smoke')
        bs.emitBGDynamics(position=position,emitType='distortion',spread=1.0 if self.blastType in ['tnt','tntC'] else 2.0)

        # and emit some shrapnel..
        if self.blastType == 'ice':
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=30,spread=2.0,scale=0.4,chunkType='ice',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(5+random.random()*5),scale=0.45,chunkType='ice');
                for i in range(2+random.randint(1,3)):
                    bs.Particle(position,
                                (velocity[0]+random.uniform(-3,3),velocity[1]+random.uniform(0,1),velocity[2]+random.uniform(-3,3)),
                                'snow',
                                random.uniform(0.3,0.55))
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'scatter': #
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8), scale=0.1,
                                  chunkType='spark');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8), scale=0.1,
                                  chunkType='spark');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=20, scale=0.7, chunkType='spark',
                                  emitType='stickers');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(8.0+random.random()*15), scale=0.1,
                                  spread=1.5, chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'iceMeteor':
            def _doEmit():
                bs.emitBGDynamics(
                        position=position,
                        velocity=(0, 0, 0),
                        count=2000,
                        scale=0.6,
                        spread=0.7, chunkType = 'ice');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'snowball':
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=15,spread=1.0,scale=0.2,chunkType='ice',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(3+random.random()*3),scale=0.25,chunkType='ice');
                for i in range(1+random.randint(0,1)):
                    bs.Particle(position,
                                (velocity[0]+random.uniform(-2,2),velocity[1]+random.uniform(0,1),velocity[2]+random.uniform(-2,2)),
                                'snow',
                                random.uniform(0.1,0.35))
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit

        elif self.blastType == 'overdrive':
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*16),scale=0.5, spread=1.0,chunkType='spark');
                bs.emitBGDynamics(position=position,velocity=velocity,count=8,scale=1.0,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=25,scale=0.3,chunkType='spark',emitType='stickers');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'sticky':
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),spread=0.7,chunkType='slime');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),scale=0.5, spread=0.7,chunkType='slime');
                bs.emitBGDynamics(position=position,velocity=velocity,count=15,scale=0.6,chunkType='slime',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=20,scale=0.7,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(6.0+random.random()*12),scale=0.8,spread=1.5,chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'cake':
            def _doEmit():
                for i in range(2+random.randint(0,10)): # Dizzy Cake dough (big chunks)
                    bs.Particle(position,
                               (velocity[0]+random.uniform(-6,6),velocity[1]+random.uniform(5,10),velocity[2]+random.uniform(-6,6)),
                               'cake',
                               random.uniform(0.1,1.0))
                for i in range(4+random.randint(0,20)): # Dizzy Cake dough
                    bs.Particle(position,
                               (velocity[0]+random.uniform(-6,6),velocity[1]+random.uniform(5,10),velocity[2]+random.uniform(-6,6)),
                               'cake',
                               random.uniform(0.001,0.5))
                for i in range(1+random.randint(0,16)): # Dizzy Cake dough
                    bs.Particle(position,
                               (velocity[0]+random.uniform(-6,6),velocity[1]+random.uniform(5,10),velocity[2]+random.uniform(-6,6)),
                               'snow',
                               random.uniform(0.001,0.6))
                for i in range(1+random.randint(0,4)): # Dizzy Cake dough
                    bs.Particle(position,
                               (velocity[0]+random.uniform(-6,6),velocity[1]+random.uniform(5,10),velocity[2]+random.uniform(-6,6)),
                               'candy',
                               random.uniform(0.001,0.750))
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'hunter':
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),scale=0.8,chunkType='metal');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),scale=0.4,chunkType='metal');
                bs.emitBGDynamics(position=position,velocity=velocity,count=20,scale=0.7,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(8.0+random.random()*15),scale=0.8,spread=1.5,chunkType='spark');
                #bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*16),spread=0.9,chunkType='slime');
                #bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*16),scale=0.5, spread=1.0,chunkType='slime');
                for i in range(4+random.randint(1,5)): # Dizzy Cake dough (big chunks)
                    bs.Particle(position,
                               (velocity[0]+random.uniform(-3,3),velocity[1]+random.uniform(2.34,4.8005),velocity[2]+random.uniform(-3,3)),
                               'ashpile',
                               random.uniform(0.1,0.2))
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'dynamite':
            def _doEmit():
                    bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),chunkType='rock');
                    bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),scale=0.8,chunkType='rock');
                    bs.emitBGDynamics(position=position,velocity=velocity,count=int(8.0+random.random()*20),scale=0.7,spread=1.5,chunkType='spark');
                    bs.emitBGDynamics(position=position,velocity=velocity,count=60,scale=1.0,spread=3.0,chunkType='spark',emitType='stickers');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'impact': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),scale=0.8,chunkType='metal');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),scale=0.4,chunkType='metal');
                bs.emitBGDynamics(position=position,velocity=velocity,count=20,scale=0.7,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(8.0+random.random()*15),scale=0.8,spread=1.5,chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'palette': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),scale=0.8,chunkType='metal');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),scale=0.4,chunkType='metal');
                bs.emitBGDynamics(position=position,velocity=velocity,count=20,scale=0.7,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(8.0+random.random()*15),scale=0.8,spread=1.5,chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'combat': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*15),scale=0.9,chunkType='metal');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*15),scale=0.5,chunkType='metal');
                bs.emitBGDynamics(position=position,velocity=velocity,count=30,scale=0.7,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(8.0+random.random()*20),scale=0.7,spread=1.5,chunkType='spark');
                for i in range(1+random.randint(0,3)): # Combat Bomb fluids (big chunks)
                    bs.Particle(position,
                                (velocity[0]+random.uniform(-10,10),velocity[1]+random.uniform(-10,10),velocity[2]+random.uniform(-10,10)),
                                'combatFluid',
                                random.uniform(0.1,0.5))
                for i in range(4+random.randint(0,5)): # Combat Bomb fluids
                    bs.Particle(position,
                                (velocity[0]+random.uniform(-10,10),velocity[1]+random.uniform(-10,10),velocity[2]+random.uniform(-10,10)),
                                'combatFluid',
                                random.uniform(0.01,0.3))
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'knocker': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*30),scale=0.5,chunkType='ice');
                bs.emitBGDynamics(position=position,velocity=velocity,count=30,scale=0.3,spread=3.0,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(32.0+random.random()*40),scale=1.0,spread=3.0,chunkType='spark');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),emitType='tendrils',tendrilType='ice')
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'hijump': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=15,scale=1.0,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(8.0+random.random()*20),scale=0.3,spread=3.0,chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType in ['firework','fireworkE']: # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=500, scale=0.84,
                                  chunkType='spark');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=95, scale=0.55,emitType='stickers',
                                  chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'healing': # regular bomb shrapnel
            def _doEmit():
                for i in range(3+random.randint(2,7)):
                    bs.Particle((position[0],position[1]+0.25,position[2]),
                            (velocity[0]+random.uniform(-3,3),velocity[1]+random.uniform(5,10),velocity[2]+random.uniform(-3,3)),
                            'glitter',
                            random.uniform(0.15,0.5))
                bs.emitBGDynamics(position=position,velocity=velocity,count=60,scale=1.0,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(16.0+random.random()*100),scale=1.0,spread=1.5,chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'splash': # regular bomb shrapnel
            def _doEmit():
                for i in range(2+random.randint(2,6)):
                    bs.Particle((position[0]+random.uniform(-1.0,1.0),position[1]+0.25,position[2]+random.uniform(-1.0,1.0)),
                            (velocity[0],velocity[1],velocity[2]),
                            'petals',
                            random.uniform(0.2,0.4129))
                for i in range(1+random.randint(1,2)):
                    bs.Particle((position[0]+random.uniform(-1.0,1.0),position[1]+0.25,position[2]+random.uniform(-1.0,1.0)),
                            (velocity[0],velocity[1],velocity[2]),
                            'blooms',
                            random.uniform(0.1,0.1513))
                bs.emitBGDynamics(position=position,velocity=velocity,count=60,scale=1.0,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(16.0+random.random()*100),scale=1.0,spread=1.5,chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'infatuate': # regular bomb shrapnel
            def _doEmit():
                for i in range(6+random.randint(2,19)):
                    bs.Particle((position[0]+0.5,position[1]+0.5,position[2]+0.5),
                            (velocity[0]+random.uniform(-3,3),velocity[1]+random.uniform(5,10),velocity[2]+random.uniform(-3,3)),
                            'glitter',
                            random.uniform(0.15,0.5))
                for i in range(6+random.randint(2,16)):
                    bs.Particle((position[0]+0.7,position[1]+0.3,position[2]+0.7),
                            (velocity[0]+random.uniform(-3,3),velocity[1]+1,velocity[2]+random.uniform(-3,3)),
                            'candy',
                            random.uniform(0.05,0.3505))
                bs.emitBGDynamics(position=position,velocity=velocity,count=20,scale=1.5,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(16.0+random.random()*100),scale=1.0,spread=1.5,chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'ranger': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*20),scale=2.9,chunkType='spark');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*20),scale=1.7,chunkType='spark');
                bs.emitBGDynamics(position=position,velocity=velocity,count=50,scale=0.7,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(8.0+random.random()*45),scale=1.2,spread=3,chunkType='spark');
            bs.gameTimer(50,_doEmit)
            
        elif self.blastType == 'radius': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*20),scale=1.5,chunkType='spark');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*20),scale=1.2,chunkType='spark');
                bs.emitBGDynamics(position=position,velocity=velocity,count=50,scale=0.7,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(8.0+random.random()*45),scale=1.0,spread=3,chunkType='spark');
            bs.gameTimer(50,_doEmit)
            bs.gameTimer(60,_doEmit)
            bs.gameTimer(70,_doEmit)
            
        elif self.blastType == 'landMine': 
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),scale=0.5,chunkType='rock');
                for i in range(1+random.randint(1,6)):
                    bs.Particle(position,
                                (velocity[0]+random.uniform(-4,4),velocity[1]+random.uniform(2,6),velocity[2]+random.uniform(-4,4)),
                                'landMine',
                                random.uniform(0.05,0.15))
            bs.gameTimer(50,_doEmit)
            
        elif self.blastType == 'sticky':
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),spread=1.0,chunkType='slime');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*16),scale=0.5, spread=0.7,chunkType='slime');
                bs.emitBGDynamics(position=position,velocity=velocity,count=15,scale=0.6,chunkType='slime',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=20,scale=0.3,chunkType='spark',emitType='stickers');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(6.0+random.random()*12),scale=0.8,spread=1.5,chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit
            
        elif self.blastType == 'grenade': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(6.0+random.random()*15),scale=0.8,chunkType='rock');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(6.0+random.random()*30),scale=0.5,chunkType='rock');
            bs.gameTimer(50,_doEmit)
            
        elif self.blastType == 'instant': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(9.7+random.random()*15),scale=0.35,chunkType='rock');
                bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.4+random.random()*30),scale=0.2,chunkType='metal');
            bs.gameTimer(50,_doEmit)

        else: # regular or land mine bomb shrapnel
            def _doEmit():
                if not self.blastType in ['tnt','tntC','miniDynamite','fake']:
                    bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),chunkType='rock');
                    bs.emitBGDynamics(position=position,velocity=velocity,count=int(4.0+random.random()*8),scale=0.5,chunkType='rock');
                if self.blastType != 'miniDynamite':
                    bs.emitBGDynamics(position=position,velocity=velocity,count=30,scale=0.7,chunkType='spark',emitType='stickers');
                    bs.emitBGDynamics(position=position,velocity=velocity,count=int(18.0+random.random()*20),scale=1.0 if self.blastType in ['tnt','tntC'] else 0.8,spread=1.5,chunkType='spark');

                # tnt throws metal chunks
                if self.blastType == 'tnt':
                    def _emitMetal():
                        bs.emitBGDynamics(position=position,velocity=velocity,count=int(35.0+random.random()*50),scale=1.5,spread=1,chunkType='metal');
                    bs.gameTimer(10,_emitMetal)
                elif self.blastType == 'fraction':
                    def _emitMetal():
                        bs.emitBGDynamics(position=position,velocity=velocity,count=int(35.0+random.random()*50),scale=random.random()*1.0,spread=1,chunkType='metal');
                    bs.gameTimer(10,_emitMetal)
                # or wood, depending on the TNT type
                elif self.blastType == 'tntC':
                    def _emitSplinters():
                        bs.emitBGDynamics(position=position, velocity=velocity,
                                          count=int(20.0+random.random()*30),
                                          scale=1.2, spread=1.0,
                                          chunkType='splinter');
                    bs.gameTimer(10,_emitSplinters)
                
                # every now and then do a sparky one (don't do it for dynamite clusters)
                if self.blastType in ['tnt','tntC'] or (random.random() < 0.1 and self.blastType != 'miniDynamite'):
                    def _emitExtraSparks():
                        bs.emitBGDynamics(position=position, velocity=velocity,
                                          count=int(10.0+random.random()*20),
                                          scale=0.8, spread=1.5,
                                          chunkType='spark');
                    bs.gameTimer(20,_emitExtraSparks)
                        
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit

        if self.blastType == 'tnt':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (0.4,0.7,0.4),
                                  'volumeIntensityScale': 10.0})
        elif self.blastType == 'ranger':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (1,1,1),
                                  'volumeIntensityScale': 100.0})
        elif self.blastType == 'palette':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]),
                                          random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]),
                                         random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])),
                                  'volumeIntensityScale': 100.0})
        elif self.blastType == 'overdrive':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (1.0,0.56,1.0),
                                  'volumeIntensityScale': 100.0})
        elif self.blastType == 'instant':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (1.4,0.2,0.2),
                                  'volumeIntensityScale': 79.5})
        elif self.blastType == 'combat':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (0.2,0.69,0.9),
                                  'volumeIntensityScale': 50.0})
        elif self.blastType == 'healing':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (1,0.73,1),                                  
                                  'volumeIntensityScale': 10.0})
        elif self.blastType in ['firework','fireworkE']:
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (random.uniform(0.2,1.35),random.uniform(0.2,1.35),random.uniform(0.2,1.35)),                                  
                                  'volumeIntensityScale': 10.0})
        elif self.blastType == 'hunter':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (0.6,0.2,0.2),                                  
                                  'volumeIntensityScale': 7.5})
        elif self.blastType == 'fraction':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (0,3,3),                                  
                                  'volumeIntensityScale': 8.6})
        elif self.blastType == 'infatuate':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (1.4,0.7,0.8),                                  
                                  'volumeIntensityScale': 10.0})                      
        elif self.blastType == 'hijump':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (1,0.05,0.95),                                  
                                  'volumeIntensityScale': 5.0})
        elif self.blastType == 'splash':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (0.85,0.3,1),                                  
                                  'volumeIntensityScale': 5.0})
        elif self.blastType == 'knocker':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (0.0,0.0,1.0),
                                  'volumeIntensityScale': 5.0})
        elif self.blastType == 'tesla':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (0.0,0.5,0.0),
                                  'volumeIntensityScale': 5.0})
        elif self.blastType == 'burger':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (1.0,0.5,0.0),
                                  'volumeIntensityScale': 5.0})
        elif self.blastType == 'cake':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': self.cakeColor,
                                  'volumeIntensityScale': 5.0})
        elif self.blastType == 'iceMeteor':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (0.6,0.6,1.2),
                                  'volumeIntensityScale': 10.0})
        elif self.blastType == 'snowball':
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (0.6,0.6,1.0),
                                  'volumeIntensityScale': 2.0})
        else:
            light = bs.newNode('light',
                           attrs={'position':position,
                                  'color': (0.6,0.6,1.0) if self.blastType == 'ice' else (1,0.3,0.1),
                                  'volumeIntensityScale': 10.0})

        s = random.uniform(0.6,0.9)
        scorchRadius = lightRadius = self.radius
        if self.blastType in ['tnt','tntC']:
            lightRadius *= 1.4
            scorchRadius *= 1.15
            s *= 3.0
        elif self.blastType == 'ranger':
            lightRadius *= 1.6
            s *= 2.0
        elif self.blastType == 'fraction':
            lightRadius *= 0.85
            s *= 2.0
        elif self.blastType == 'overdrive':
            lightRadius *= 1.8
            s *= 1.15
        elif self.blastType == 'combat':
            lightRadius *= 0.5
            s *= 2.0
        elif self.blastType == 'splash':
            lightRadius *= 0.75
            s *= 1.0
        elif self.blastType in ['miniDynamite','fireworkE']:
            lightRadius *= 0.15
            s *= 1.0
        elif self.blastType == 'iceMeteor':
            lightRadius *= 1.0
            s *= 1.0
        elif self.blastType == 'instant':
            lightRadius *= 0.7
            s *= 1.65
            
        iScale = 1.6
        bsUtils.animate(light,"intensity",{0:2.0*iScale, int(s*20):0.1*iScale, int(s*25):0.2*iScale, int(s*50):17.0*iScale, int(s*60):5.0*iScale, int(s*80):4.0*iScale, int(s*200):0.6*iScale, int(s*2000):0.00*iScale, int(s*3000):0.0})
        bsUtils.animate(light,"radius",{0:lightRadius*0.2, int(s*50):lightRadius*0.55, int(s*100):lightRadius*0.3, int(s*300):lightRadius*0.15, int(s*1000):lightRadius*0.05})
        bs.gameTimer(int(s*3000),light.delete)

        # make a scorch that fades over time
        scorch = bs.newNode('scorch',
                        attrs={'position':position,'size':scorchRadius*0.5,'big':(self.blastType in ['tnt','tntC'] or self.blastType == 'ranger' or self.blastType == 'grenade')})
        if self.blastType in ['ice','snowball','iceMeteor']:
            scorch.color = (1,1,1.5)
            
        if self.blastType == 'knocker':
            scorch.color = (1,1,1.5)
            
        if self.blastType in ['firework','fireworkE']:
            scorch.color = (random.uniform(0.2,1.35),random.uniform(0.2,1.35),random.uniform(0.2,1.35))
        
        if self.blastType == 'palette':
            scorch.color = (random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]),
                                          random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]),
                                         random.choice([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]))
            
        if self.blastType == 'ranger':
            scorch.color = (2,2,2)
            
        if self.blastType == 'cluster':
            scorch.color = (0.55,0.55,0.55)
            
        if self.blastType == 'splash':
            scorch.color = (0.6,1.35,1.20)
            
        if self.blastType == 'fraction':
            scorch.color = (0,3,3)
            
        if self.blastType == 'hijump':
            scorch.color = (0.7,0.05,0.65)
           
        if self.blastType == 'firework':
            scorch.color = (1,0.9,0.6)
           
        if self.blastType == 'healing':
            scorch.color = (2,1.73,2)
            
        if self.blastType == 'infatuate':
            scorch.color = (1.4,0.7,0.8)
            
        if self.blastType in ['tnt','tesla']:
            scorch.color = (0.4,0.7,0.4)
            
        if self.blastType == 'instant':
            scorch.color = (1.4,0.2,0.2)

        if self.blastType == 'cake':
            scorch.color = self.cakeColor     
            

        bsUtils.animate(scorch,"presence",{3000:1, 13000:0})
        bs.gameTimer(13000,scorch.delete)
        bs.gameTimer(8000,explosion.delete)

        if self.blastType == 'ice': bs.playSound(factory.hissSound,position=light.position)
        if self.blastType == 'ranger': bs.playSound(factory.crystalExplosionSound,position=light.position)  
        if self.blastType == 'palette': bs.playSound(factory.paletteExplosionSound,position=light.position)  
        if self.blastType == 'glue': bs.playSound(factory.glueImpactSound,2,position=self.node.position)
        if self.blastType == 'burger':
            bs.playSound(factory.cakeImpactSound,position=light.position)  
            bs.playSound(factory.getRandomTNTExplodeSound(),position=light.position)
            def _extraBoom():
                bs.playSound(factory.getRandomTNTExplodeSound(),position=light.position)
            bs.gameTimer(250,_extraBoom)
            
        p = light.position
        sparks = [bs.getSound('sparkle01'),bs.getSound('sparkle02'),bs.getSound('sparkle03')]
        if self.blastType == 'combat': bs.playSound(factory.combatExplosionSound,position=p)
        elif self.blastType in ['knocker','fireworkE','firework']: bs.playSound(factory.knockerExplosionSound,volume=4.0,position=p)
        elif self.blastType == 'grenade': bs.playSound(factory.getRandomGrenadeSound(),volume=1.0,position=p)  
        elif self.blastType == 'hijump': bs.playSound(factory.hijumpSound,volume=2.0,position=p)  
        elif self.blastType == 'splash': bs.playSound(bs.getSound('teslaShieldHit'),volume=1.3,position=p)
        elif self.blastType == 'infatuate': bs.playSound(random.choice(sparks),volume=0.85,position=p)
        elif self.blastType == 'cake': bs.playSound(factory.cakeExplosionSound,volume=3.0,position=p)  
        elif self.blastType == 'snowball': bs.playSound(random.choice(factory.snowballSounds),volume=1.0,position=p)  
        elif self.blastType == 'overdrive':
            bs.playSound(factory.overdriveExplosionSound,volume=2.0,position=p)
            bs.playSound(factory.getRandomExplodeSound(),volume=1.0,position=p)
        else:
            if self.blastType != 'miniDynamite':
                if self.blastType == 'glue': vol=0.5
                else: vol=0.8
                bs.playSound(factory.getRandomExplodeSound(),volume=vol,position=p)
                bs.playSound(factory.debrisFallSound,position=p)
        
        if bs.getConfig().get('Camera Shake', True):
            if self.blastType == 'ranger':
                bs.shakeCamera(intensity=2.0)
            elif self.blastType == 'overdrive':
                bs.shakeCamera(intensity=6.5)
            elif self.blastType == 'cake':
                bs.shakeCamera(intensity=1.2)
            elif self.blastType == 'instant':
                bs.shakeCamera(intensity=1.89)
            elif self.blastType == 'grenade':
                bs.shakeCamera(intensity=1.5)
            elif self.blastType == 'fire':
                bs.shakeCamera(intensity=0.25)
            elif self.blastType == 'hijump':
                bs.shakeCamera(intensity=0.1)
            elif self.blastType == 'combat':
                bs.shakeCamera(intensity=0.5)
            elif self.blastType == 'knocker':
                bs.shakeCamera(intensity=0.75)
            else:
                if not self.blastType in ['miniDynamite','fake','snowball']:
                    bs.shakeCamera(intensity=5.0 if self.blastType in ['tnt','tntC'] else 1.0)
        # set scattering here
        elif self.blastType == 'scatter':
        	#1.8578
            def _blasts():
            	angle = random.uniform(0.0,360.0) #face to which angle?
                radius = 0.01 * random.uniform(12,160) #size of circle
                x = math.sin(angle)*radius #length
                z = math.cos(angle)*radius #width
                
                bs.Blast(position=(position[0]+x,position[1],position[2]+z),
                       hitType='radius',hitSubType='normal',
                       blastRadius=blastRadius/2.9847,
                       blastType='miniDynamite',
                       sourcePlayer=self.sourcePlayer).autoRetain()
            bs.gameTimer(435+random.randint(10,95), _blasts)
            bs.gameTimer(490+random.randint(10,95), _blasts)
            bs.gameTimer(530+random.randint(10,95), _blasts)
            bs.gameTimer(530+random.randint(10,95), _blasts)
            bs.gameTimer(615+random.randint(10,95), _blasts)
            bs.gameTimer(645+random.randint(10,95), _blasts)
            bs.gameTimer(659+random.randint(10,95), _blasts)
            bs.gameTimer(685+random.randint(10,95), _blasts)
            bs.gameTimer(817+random.randint(10,95), _blasts)
            bs.gameTimer(845+random.randint(10,95), _blasts)
            bs.gameTimer(859+random.randint(10,95), _blasts)
            bs.gameTimer(877+random.randint(10,95), _blasts)
            bs.gameTimer(950+random.randint(10,95), _blasts)
            bs.gameTimer(970+random.randint(10,95), _blasts)
            bs.gameTimer(1003+random.randint(10,95), _blasts)
        elif self.blastType == 'firework':
            def _explosion():
            	columns = [-1.5,-0.4,0.4,1.5]
            	rows = [-1.5,-0.4,0.4,1.5]
            	p = position
                bs.Blast(position=(p[0]+random.choice(columns),p[1],p[2]+random.choice(rows)),
                       hitType='fireworkE',hitSubType='normal',
                       blastRadius=1.35,
                       blastType='fireworkE',
                       sourcePlayer=self.sourcePlayer).autoRetain()
            for i in range(1,42):
                bs.gameTimer(i*200,_explosion)
            for l in range(1,30):
                bs.gameTimer(l*random.randint(29,260),_explosion)
        elif self.blastType == 'iceMeteor':
            def _icy1():
                pos = position
                bs.Blast(position=(pos[0],pos[1],pos[2]),
                       hitType='ice',hitSubType='ice',
                       blastRadius=2.729,
                       blastType='ice').autoRetain()                
            bs.gameTimer(101,_icy1)
        if self.blastType in ['tnt','tntC']:
            bs.playSound(factory.getRandomExplodeSound(),position=p)
            def _extraBoom():
                bs.playSound(factory.getRandomTNTExplodeSound(),position=p,volume=1.3)
            bs.gameTimer(150,_extraBoom)
            def _extraDebrisSound():
                bs.playSound(factory.debrisFallSound,position=p)
                if self.blastType == 'tnt': bs.playSound(factory.metalDebrisFallSound,position=p)
                elif self.blastType == 'tntC': bs.playSound(factory.woodDebrisFallSound,position=p)
            if self.blastType == 'tnt': bs.gameTimer(700,_extraDebrisSound)
            elif self.blastType == 'tntC': bs.gameTimer(400,_extraDebrisSound)

    def handleMessage(self,m):
        self._handleMessageSanityCheck()
        
        if isinstance(m,bs.DieMessage):
            self.node.delete()

        elif isinstance(m,ExplodeHitMessage):
            node = bs.getCollisionInfo("opposingNode")
            if node is not None:
                try:
                    t = self.node.position
    
                    # new
                    mag = 2000.0
                    if self.blastType == 'ice': mag *= 0.5
                    elif self.blastType == 'impact': mag *= 1.0
                    elif self.blastType == 'snowball': mag *= 1.2
                    elif self.blastType == 'infatuate': mag *= 0.001
                    elif self.blastType == 'fraction': mag *= 1.27
                    elif self.blastType == 'burger': mag *= 1.25
                    elif self.blastType == 'iceMeteor': mag *= 2.2
                    elif self.blastType == 'instant': mag *= 1.9
                    elif self.blastType == 'fire': mag *= 0.1
                    elif self.blastType == 'palette': mag *= 0.003
                    elif self.blastType == 'tesla': mag *= 2.0
                    elif self.blastType == 'landMine': mag *= 2.5 # 2.5 Not influenced
                    elif self.blastType in ['tnt','tntC']: mag *= 2.0 #normal 2.0
                    elif self.blastType == 'knocker': mag *= 1.5
                    elif self.blastType == 'cluster': mag *= 0.15
                    elif self.blastType == 'combat': mag *= 1.4
                    elif self.blastType == 'dynamite': mag *= 0.9
                    elif self.blastType == 'miniDynamite': mag *= 1.15
                    elif self.blastType == 'ranger': mag *= 1.2
                    elif self.blastType == 'grenade': mag *= 1.2
                    elif self.blastType == 'overdrive': mag *= 1.2
                    elif self.blastType == 'healing': mag *= 0.0
                    elif self.blastType == 'hijump': mag *= 1.25
                    elif self.blastType == 'cake': mag *= 0.1
                    elif self.blastType == 'scatter': mag *= 0.3
                    elif self.blastType == 'gloo': mag *= 0.0
                    elif self.blastType == 'hunter': mag *= 0.1
                    elif self.blastType == 'radius': mag *= 0.6
                    elif self.blastType == 'firework': mag *= 0.0
                    elif self.blastType == 'fireworkE': mag *= 0.25
                    elif self.blastType == 'splash': mag *= 0.04
                    
                    if self.blastType not in ['glue','healing','fake']:
                        if self.blastType in ['snowball','splash'] and self.sourcePlayer == node.sourcePlayer: return
                            
                        node.handleMessage(bs.HitMessage(pos=t,
                                                            srcNode=self.node,
                                                            velocity=(0,0,0),
                                                            magnitude=mag,
                                                            hitType=self.hitType,
                                                            hitSubType=self.hitSubType,
                                                            radius=self.radius,
                                                            sourcePlayer=self.sourcePlayer))
                        
                    if self.blastType == "ice":
                        bs.playSound(Bomb.getFactory().freezeSound,10,position=t)
                        node.handleMessage(bs.FreezeMessage(self.sourcePlayer))
                        
                    if self.blastType == "cake":
                        node.handleMessage(bs.DizzyMessage(self.sourcePlayer))
                        
                        
                    if self.blastType == "fire":
                        bs.playSound(Bomb.getFactory().fireSound,10,position=t)
                        import bsSpaz
                        node.handleMessage(bs.FireMessage(bsSpaz.gFireDuration,self.sourcePlayer))
                        
                    if self.blastType == "healing":
                        bs.playSound(Bomb.getFactory().healingSound,10,position=t)
                        node.handleMessage(bs.HealMessage(self.sourcePlayer))
                        
                except AttributeError: pass
                    
        else:
            bs.Actor.handleMessage(self,m)

class Bomb(bs.Actor):
    """
    category: Game Flow Classes
    
    A bomb and its variants such as land-mines and tnt-boxes.
    """

    def __init__(self,position=(0,1,0),velocity=(0,0,0),bombType='normal',blastRadius=2.0,blastRadiusBuffed=False,sourcePlayer=None,bombShape='Regular',owner=None,hitSubTypeTrue=True):
        """
        Create a new Bomb.
        
        bombType can be 'ice','impact','landMine','normal','sticky', 'ranger', or 'tnt'.
        Note that for impact or landMine bombs you have to call arm()
        before they will go off.
        """
        bs.Actor.__init__(self)

        factory = self.getFactory()

        if not bombType in ('ice','iceMeteor','impact','snowball','landMine','hunter','normal','instant','burger','sticky','ranger','infatuate','tnt','combat','glue','magnet','knocker','splash','dynamite','fraction','miniDynamite','fire','healing','grenade','hijump','basketball','cake','tesla','gloo','radius','palette','scatter','firework','cluster'): raise Exception("invalid bomb type: " + bombType)
        if bombType == 'tnt': self.bombType = random.choice(['tnt','tntC'])
        else: self.bombType = bombType

        self._exploded = False
        self._armed = False
        
        self.teslaActive = False
        self.teslaHealthMax = 1500
        self.teslaHealth = self.teslaHealthMax
        self.teslaDamage = 20

        if self.bombType == 'sticky': self._lastStickySoundTime = 0
        self.blastRadius = blastRadius
        if self.bombType == 'ice': self.blastRadius *= 1.1
        elif self.bombType == 'iceMeteor': self.blastRadius *= 1.76
        elif self.bombType == 'gloo': self._lastStickySoundTime = 0
        elif self.bombType == 'fire': self.blastRadius *= 1.1
        elif self.bombType == 'impact': self.blastRadius *= 0.6
        elif self.bombType == 'splash': self.blastRadius *= 1.2
        elif self.bombType == 'snowball': self.blastRadius *= 0.5
        elif self.bombType == 'glue': self.blastRadius *= 0.5
        elif self.bombType == 'instant': self.blastRadius *= 1.62
        elif self.bombType == 'fraction': self.blastRadius *= 1.5
        elif self.bombType == 'cluster': self.blastRadius *= 0.35
        elif self.bombType == 'burger': self.blastRadius *= 2.5
        elif self.bombType == 'infatuate': self.blastRadius *= 1.27
        elif self.bombType == 'combat': self.blastRadius *= 0.75
        elif self.bombType == 'magnet': self.blastRadius *= 0.75
        elif self.bombType == 'knocker': self.blastRadius *= 1.5
        elif self.bombType == 'cake': self.blastRadius *= 2.3
        elif self.bombType == 'dynamite': self.blastRadius *= 0.55
        elif self.bombType == 'miniDynamite': self.blastRadius *= 0.55
        elif self.bombType == 'landMine': self.blastRadius *= 0.7
        elif self.bombType in ['tnt','tntC']: self.blastRadius *= 1.6 #1.6
        elif self.bombType == 'ranger': self.blastRadius *= 1.6
        elif self.bombType == 'overdrive': self.blastRadius *= 1.0
        elif self.bombType == 'healing': self.blastRadius *= 1.2
        elif self.bombType == 'grenade': self.blastRadius *= 1.45
        elif self.bombType == 'hijump': self.blastRadius *= 1.0
        elif self.bombType == 'tesla': self.blastRadius *= 1.25
        elif self.bombType == 'gloo': self.blastRadius *= 0.0
        elif self.bombType == 'radius': self.blastRadius *= 1.5
        elif self.bombType == 'hunter': self.blastRadius *= 1.13
        elif self.bombType == 'palette': self.blastRadius *= 1.24
        elif self.bombType == 'firework': self.blastRadius *= 0.0
        elif self.bombType == 'fireworkE': self.blastRadius *= 1.0
        
        if (not blastRadiusBuffed and bs.getConfig().get('Party Mode', True) and 
           not isinstance(bs.getSession(),bs.CoopSession) and 
           random.randint(0,10) == 0 and 
           not self.bombType in ['hijump','burger','cluster']):
            blastRadiusBuffed = True
        
        if blastRadiusBuffed: self.blastRadius += 0.55

        self._explodeCallbacks = []
        
        # the player this came from
        self.sourcePlayer = sourcePlayer

        # by default our hit type/subtype is our own, but we pick up types of whoever
        # sets us off so we know what caused a chain reaction
        self.hitType = 'explosion'
        self.hitSubType = self.bombType
        self.hitSubTypeTrue = hitSubTypeTrue
        
        if self.bombType == 'landMine': self.mineDamaged = False

        # if no owner was provided, use an unconnected node ref
        if owner is None: owner = bs.Node(None)

        # the node this came from
        self.owner = owner
        
        self.bombShape = []
        self.bombShape.append(factory._getMedia(bombShape)['shapeModel']) # [0]
        self.bombShape.append(factory._getMedia(bombShape)['explosionSounds']) # [1]
        self.bombShape.append(factory._getMedia(bombShape)['explosionVolume']) # [2]
        self.bombShape.append(factory._getMedia(bombShape)['reflection']) # [3]
        self.bombShape.append(factory._getMedia(bombShape)['reflectionScale']) # [4]

        # adding footing-materials to things can screw up jumping and flying since players carrying those things
        # and thus touching footing objects will think they're on solid ground..
        # perhaps we don't wanna add this even in the tnt case?..
        
        if self.bombType == 'cake':
            materials = (factory.bombMaterial, )
        else:
            materials = (factory.bombMaterial, bs.getSharedObject('objectMaterial'))
            
        if self.bombType in ['impact','snowball','healing','glue','splash','iceMeteor']: materials = materials + (factory.impactBlastMaterial,)
        elif self.bombType == 'landMine': materials = materials + (factory.landMineNoExplodeMaterial,)

        if self.bombType == 'sticky': materials = materials + (factory.stickyMaterial,)
        elif self.bombType == 'gloo': materials = materials + (factory.stickyMaterial,)
        elif self.bombType == 'ranger': materials = materials + (factory.crystalSoundMaterial,)
        elif self.bombType == 'cake': materials = materials + (factory.cakeSoundMaterial,)
        elif self.bombType == 'basketball': materials = materials + (factory.basketballSoundMaterial,)
        else: materials = materials + (factory.normalSoundMaterial,)
        
        if self.bombType == 'magnet': materials = materials + (factory.magnetMaterial,)
        elif self.bombType == 'tesla': materials = materials + (factory.teslaMaterial,)
        

        if self.bombType == 'landMine':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':(position[0],position[1],position[2]),
                                          'velocity':(velocity[0],velocity[1],velocity[2]),
                                          'model':factory.landMineModel,
                                          'lightModel':factory.landMineModel,
                                          'body':'landMine',
                                          'shadowSize':0.44,
                                          'colorTexture':factory.landMineTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.0],
                                          'materials':materials})
                                          
        elif self.bombType == 'tesla':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':(position[0],position[1],position[2]),
                                          'velocity':(velocity[0],velocity[1],velocity[2]),
                                          'model':factory.teslaPadModel,
                                          'lightModel':factory.teslaPadModel,
                                          'body':'landMine',
                                          'shadowSize':0.44,
                                          'colorTexture':factory.teslaPadTex,
                                          'reflection':'char',
                                          'reflectionScale':[0.5],
                                          'materials':materials})

        elif self.bombType in ['tnt','tntC']:
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'model':factory.tntModel if self.bombType == 'tnt' else factory.tntClassicModel,
                                          'lightModel':factory.tntModel if self.bombType == 'tnt' else factory.tntClassicModel,
                                          'body':'crate',
                                          'shadowSize':0.5,
                                          'colorTexture':factory.tntTex if self.bombType == 'tnt' else factory.tntClassicTex,
                                          'reflection':'soft',
                                          'reflectionScale':[0.23],
                                          'materials':materials})
                                          
        elif self.bombType == 'cake':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':(position[0],position[1],position[2]), #'position':(position[0]+(velocity[0]/12*-1),position[1]+0.4,position[2]+(velocity[2]/12*-1)), 
                                          # Dizzy Cake doesn't have bomb material to prevent picking it up, but it spawns incorrectly. These calculations are made to prevent it.
                                          'velocity':(velocity[0],velocity[1],velocity[2]),
                                          'model':factory.cakeBombModel,
                                          'lightModel':factory.cakeBombModel,
                                          'body':'landMine',
                                          'density':1.0,
                                          'shadowSize':0.1,
                                          'colorTexture':factory.cakeTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[0.25],
                                          'materials':materials})
            self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
            
        elif self.bombType == 'miniDynamite':
            fuseTime = 1
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'model':factory.nullModel,
                                          'lightModel':factory.miniDynamiteModel,
                                          'body':'crate',
                                          'shadowSize':0.1,
                                          'modelScale':0.1,
                                          'bodyScale':0.1,
                                          'colorTexture':factory.dynamiteTex,
                                          'reflection':'soft',
                                          'reflectionScale':[0.1],
                                          'materials':materials})
                                          
        elif self.bombType == 'instant':
            fuseTime = 1
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':(position[0],position[1]-0.8,position[2]),
                                          'velocity':(velocity[0],velocity[1]-0.8,velocity[2]),
                                          'model':None,
                                          'lightModel':None,
                                          'body':'sphere',
                                          'shadowSize':0.1,
                                          'modelScale':0.1,
                                          'bodyScale':0.1,
                                          'colorTexture':None,
                                          'reflection':'soft',
                                          'reflectionScale':[0.1],
                                          'materials':materials})
                                          
        elif self.bombType == 'impact':
            fuseTime = 10000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',
                                          'model':factory.impactBombModel,
                                          'shadowSize':0.3,
                                          'colorTexture':factory.impactTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.5],
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
        elif self.bombType == 'iceMeteor':
            fuseTime = 10000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',
                                          'model':factory.snowballModel,
                                          'shadowSize':0.3,
                                          'colorTexture':factory.snowballTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.5],
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
        elif self.bombType == 'splash':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',
                                          'model':factory.splashBombModel,
                                          'shadowSize':0.3,
                                          'colorTexture':factory.splashBombTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.25],
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
        elif self.bombType == 'scatter':
            fuseTime = 3000
            self.node = bs.newNode('bomb',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',
                                          'model':factory.impactBombModel,
                                          'shadowSize':0.3,
                                          'colorTexture':factory.scatterBombsTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.5],
                                          'materials':materials})
            bsUtils.animate(self.node,'fuseLength',{0:1,fuseTime:0})
        elif self.bombType == 'cluster':
            fuseTime = 2750
            self.node = bs.newNode('bomb',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',
                                          'model':bs.getModel("bomb"),
                                          'shadowSize':0.3,
                                          'colorTexture':factory.clusterTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.2],
                                          'materials':materials})
            bsUtils.animate(self.node,'fuseLength',{0:1,fuseTime:0})
        elif self.bombType == 'firework':
            fuseTime = 99999
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'landMine',
                                          'model':bs.getModel("platform"),
                                          'lightModel':bs.getModel("platform"),
                                          'shadowSize':0.3,
                                          'density':0.5,
                                          'colorTexture':factory.lightTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.05],
                                          'materials':materials})
            self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
        elif self.bombType == 'fraction':
            fuseTime = 3000
            self.node = bs.newNode('bomb',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'crate',
                                          'model':bs.getModel("powerupSimple"),
                                          'shadowSize':0.3,
                                          'bodyScale':0.6,
                                          'density':2.9,
                                          'colorTexture':bs.getTexture('black'),
                                          'reflection':'powerup',
                                          'reflectionScale':[2.0],
                                          'materials':materials})
            self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
            bsUtils.animate(self.node,'fuseLength',{0:1,fuseTime:0})
        elif self.bombType == 'hunter':
            fuseTime = 2900
            self.node = bs.newNode('bomb',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',
                                          'model':bs.getModel("bomb"),
                                          'shadowSize':0.3,
                                          'colorTexture':factory.hunterTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[0.75],
                                          'materials':materials})
            bsUtils.animate(self.node,'fuseLength',{0:1,fuseTime:0})
        elif self.bombType == 'snowball':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',
                                          'model':factory.snowballModel,
                                          'shadowSize':0.3,
                                          'colorTexture':factory.snowballTex,
                                          'reflection':'soft',
                                          'reflectionScale':[0.5],
                                          'materials':materials})
        elif self.bombType == 'burger':
            fuseTime = 790
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'crate',
                                          'model':factory.burgerModel,
                                          'density':2.0,
                                          'gravityScale':1.25,
                                          'bodyScale':0.75,
                                          'shadowSize':0.3,
                                          'colorTexture':factory.burgerTex,
                                          'reflection':'soft',
                                          'reflectionScale':[0.25],
                                          'materials':materials})
            
        elif self.bombType == 'hijump':
            fuseTime = 1
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',
                                          'model':factory.nullModel,
                                          'shadowSize':0.3,
                                          'colorTexture':factory.impactTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.5],
                                          'materials':materials})
            
        elif self.bombType == 'healing':
            fuseTime = 5000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',
                                          'model':factory.healingBombModel,
                                          'shadowSize':0.3,
                                          'colorTexture':factory.healingTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.8],
                                          'materials':materials}) 
            self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
            
        elif self.bombType == 'radius':
            fuseTime = 3000
            self.node = bs.newNode('bomb', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'body': 'sphere',
                'materials': materials})
            bsUtils.animate(self.node,'fuseLength',{0:1,fuseTime:0})
            self.light1 = bs.newNode('shield', owner=self.node, attrs={
                   'color': (2,2,2),
                   'radius': 0.55})
            #self.light2 = bs.newNode('shield', owner=self.node, attrs={
         #          'color': (1,1,1),
             #      'radius': 0.5})
        #    self.light3 = bs.newNode('shield', owner=self.node, attrs={
         #          'color': (1,1,1),
        #           'radius': 0.4})
       #     self.light4 = bs.newNode('shield', owner=self.node, attrs={
         #          'color': (1,1,1),
      #             'radius': 0.3})
            self.node.connectAttr('position', self.light1, 'position')
      #      self.node.connectAttr('position', self.light2, 'position')
       #     self.node.connectAttr('position', self.light3, 'position')
       #     self.node.connectAttr('position', self.light4, 'position')
            
        elif self.bombType == 'combat':
            fuseTime = 2000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'model':factory.combatBombModel,
                                          'lightModel':factory.combatBombModel,
                                          'body':'sphere',
                                          'shadowSize':0.5,
                                          'colorTexture':factory.combatTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.0],
                                          'materials':materials})
            self.deployedFirstTimer = bs.Timer(300,bs.WeakCall(self.handleMessage,DeployMessage()))
            self.deployedTimer = bs.Timer(1200,bs.WeakCall(self.handleMessage,DeployMessage()))
            self.readyTimer = bs.Timer(fuseTime-250,bs.WeakCall(self.handleMessage,ReadyMessage()))
            
        elif self.bombType == 'glue':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'model':factory.glueBombModel,
                                          'lightModel':factory.glueBombModel,
                                          'body':'sphere',
                                          'shadowSize':0.5,
                                          'colorTexture':factory.glueTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[0.5],
                                          'materials':materials})
            
        elif self.bombType == 'magnet':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'model':factory.magnetBombModel,
                                          'lightModel':factory.basketballModel,
                                          'body':'sphere',
                                          'shadowSize':0.5,
                                          'colorTexture':factory.magnetTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.0],
                                          'materials':materials})
            self._magnetDropped = False
            
        elif self.bombType == 'gloo':
            fuseTime = 20000
            self.node = bs.newNode('prop',
                    delegate=self,
                    attrs={'position':position,
                           'velocity':velocity,
                           'model':factory.basketballModel,
                           'lightModel':factory.basketballModel,
                           'body':'sphere',
                           'density':0.96,
                           'shadowSize':0.1,
                           'colorTexture': factory.shrapnelGlueTex,
                           'reflection':'soft',
                           'reflectionScale':[1.0],
                           'materials':materials})
            self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
            if blastRadiusBuffed:
                self.dieTimer = bs.Timer(30000,bs.WeakCall(self.handleMessage,bs.DieMessage()))
            else: self.dieTimer = bs.Timer(20000,bs.WeakCall(self.handleMessage,bs.DieMessage()))
            
        elif self.bombType == 'basketball':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'model':factory.basketballModel,
                                          'lightModel':factory.basketballModel,
                                          'body':'sphere',
                                          'shadowSize':0.5,
                                          'colorTexture':factory.basketballTex,
                                          'reflection':'soft',
                                          'reflectionScale':[0.35],
                                          'materials':materials})       
            
        elif self.bombType == 'grenade':
            fuseTime = 3000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'model':factory.grenadeBombModel,
                                          'lightModel':factory.grenadeBombModel,
                                          'body':'sphere',
                                          'shadowSize':0.1,
                                          'colorTexture':factory.grenade3Tex,
                                          'reflection':'soft',
                                          'reflectionScale':[0.5],
                                          'materials':materials})
            self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
        else:
            fuseTime = 3000
            if self.bombType == 'sticky':
                sticky = True
                rType = 'sharper'
                rScale = 1.8
                self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
            elif self.bombType == 'infatuate':
                sticky = False
                rType = 'sharper'
                rScale = 1.9
            elif self.bombType == 'palette':
                sticky = False
                rType = 'sharper'
                rScale = 1.0
            elif self.bombType == 'ranger':
                fuseTime = 4000
                sticky = False
                model = factory.crystalModel
                rType = 'sharper'
                rScale = 1.8
                self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
            elif self.bombType == 'dynamite':
                fuseTime = 3000
                sticky = False
                model = factory.dynamiteModel
                rType = 'sharper'
                rScale = 0.8
                self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
            else:
                sticky = False
                rType = 'sharper'
                rScale = 1.8
            if self.bombType == 'ice': 
                tex = factory.iceTex
                self.deployedTimer = bs.Timer(1,bs.WeakCall(self.handleMessage,DeployMessage()))
            elif self.bombType == 'sticky': tex = factory.stickyTex
            elif self.bombType == 'dynamite': tex = factory.dynamiteTex
            elif self.bombType == 'fire': tex = factory.fireTex
            elif self.bombType == 'palette': tex = factory.paletteTex
            elif self.bombType == 'ranger': tex = factory.rangerTex
            elif self.bombType == 'infatuate': tex = factory.healingTex
            elif self.bombType == 'knocker': tex = factory.knockerTex
            elif self.bombType == 'basketball': tex = factory.basketballTex
            # Overdrive bomb doesn't exist, but it's only used for the explosion. I'm gonna add the texture anyway.
            else: tex = factory.regularTex
            
            # handle custom bomb shapes
            if self.bombType in ['normal','ice','fire','knocker','sticky','palette','infatuate']: 
                rType = self.bombShape[3]
                rScale = self.bombShape[4]
                model = self.bombShape[0]
            
            
            self.node = bs.newNode('bomb',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'model':model,
                                          'shadowSize':0.3,
                                          'colorTexture':tex,
                                          'sticky':sticky,
                                          'owner':owner,
                                          'reflection':rType,
                                          'reflectionScale':[rScale],
                                          'materials':materials})
            if self.bombType == 'knocker': self.node.flashing = 1
            
            sound = bs.newNode('sound',owner=self.node,attrs={'sound':factory.fuseSound,'volume':0.25})
            self.node.connectAttr('position',sound,'position')
            bsUtils.animate(self.node,'fuseLength',{0:1,fuseTime:0})

        # light the fuse!!!
        if self.bombType not in ('landMine','tesla','tnt','tntC','basketball','cake','magnet','glue','snowball'):
            bs.gameTimer(fuseTime,bs.WeakCall(self.handleMessage,ExplodeMessage()))

        if self.bombType not in ('landMine','tesla','tnt','tntC','basketball','cake','magnet','glue','snowball'): bsUtils.animate(self.node,"modelScale",{0:0, 200:1.3, 260:1, fuseTime-80:1, fuseTime-20:0.7, fuseTime:1.8})
        else: bsUtils.animate(self.node,"modelScale",{0:0, 200:1.3, 260:1})
        
        if blastRadiusBuffed:
            if self.bombType != 'miniDynamite':
                def buffedSparks():
                    if self.node.exists():
                        bs.emitBGDynamics(position=(self.node.position[0],self.node.position[1],self.node.position[2]),velocity=self.node.velocity,count=random.randrange(3,10),scale=0.4,spread=0.1,chunkType='spark')
                        bs.gameTimer(10,bs.Call(buffedSparks))
                self.blastBuffed = True
                
                bs.gameTimer(400,bs.Call(buffedSparks))
                self.lightBuff = bs.newNode('light',
                            owner=self.node,
                            attrs={'position':self.node.position,
                                    'radius':0.05,
                                    'intensity':2.0,
                                    'color': (1.2,1.0,0.0),
                                    'volumeIntensityScale': 1.0}) 
                self.node.connectAttr('position',self.lightBuff,'position')
                bs.animate(self.lightBuff,'intensity',{0:2.0,500:1.0,1000:2.0},loop=True)
                bs.animate(self.lightBuff,'radius',{0:0.05,250:0.1,500:0.05},loop=True)
            else:
                self.blastBuffed = False
        else:
            self.blastBuffed = False

    def getSourcePlayer(self):
        """
        Returns a bs.Player representing the source of this bomb.
        """
        if self.sourcePlayer is None: return bs.Player(None) # empty player ref
        return self.sourcePlayer
        
    @classmethod
    def getFactory(cls):
        """
        Returns a shared bs.BombFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        try: return activity._sharedBombFactory
        except Exception:
            f = activity._sharedBombFactory = BombFactory()
            return f

    def onFinalize(self):
        bs.Actor.onFinalize(self)
        # release callbacks/refs so we don't wind up with dependency loops..
        self._explodeCallbacks = []
        
    def _handleDie(self,m):
        if self.node.exists() and self.bombType == 'cake':
            if self.cakeActive:
                bs.getActivity()._cakeMusicCount -= 1
                if bs.getActivity()._cakeMusicCount <= 0: 
                    bs.getActivity()._cakeMusicCount = 0
                    bsUtils.gMusic.volume = bs.getActivity()._cakeMusicVolume
        if self.node.exists(): self.node.delete()
        
    def _handleOOB(self,m):
        if self.bombType != 'burger': self.handleMessage(bs.DieMessage())

    def _handleImpact(self,m):
        node,body = bs.getCollisionInfo("opposingNode","opposingBody")
        # if we're an impact bomb and we came from this node, don't explode...
        # alternately if we're hitting another impact-bomb from the same source, don't explode...
        try: nodeDelegate = node.getDelegate()
        except Exception: nodeDelegate = None
        if node.exists():
            if (self.bombType in ['impact','snowball','healing','glue','splash','iceMeteor'] and
               (node is self.owner or (isinstance(nodeDelegate,Bomb) and 
                nodeDelegate.bombType in ['impact','snowball','healing','glue','splash','iceMeteor'] and 
                nodeDelegate.owner is self.owner))): return
            else: 
                if self.bombType == 'landMine':
                    # Detonate the land mine only if we're fast enough, so accidental deaths by touching do not happen
                    speed = math.sqrt(pow(node.velocity[0],2) + pow(node.velocity[1],2) + pow(node.velocity[2],2))
                    if not isinstance(bs.getSession(),bs.CoopSession) and speed < 1.3: return
                    
                self.handleMessage(ExplodeMessage())
                
    def _handleTesla(self,m):
        node,body = bs.getCollisionInfo("opposingNode","opposingBody")
        
        barrier = node.getDelegate()
        
        barrier.teslaHealth -= 80 #80
        barrier.teslaArea.hurt = 1.0 - float(barrier.teslaHealth)/barrier.teslaHealthMax
        
        bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=int(4.0+random.random()*20),scale=1.0,spread=2,chunkType='spark');
        
        bs.playSound(self.getFactory().teslaShieldHitSound,0.9,position=self.node.position)
        
        directionX = (node.position[0] - self.node.position[0]) * 1.25
        directionY = node.position[1] - self.node.position[1] + 0.25
        directionZ = (node.position[2] - self.node.position[2]) * 1.25 
        
        calc = math.sqrt(pow(directionX,2)+pow(directionY,2)+pow(directionZ,2))
        calc = (directionX/calc,directionY/calc,directionZ/calc)
        
        self.node.handleMessage('impulse',barrier.teslaArea.position[0],barrier.teslaArea.position[1],barrier.teslaArea.position[2],
                                0,0,0,
                                200,200,0,0,calc[0],calc[1],calc[2])
            
        if barrier.teslaHealth <= 0: barrier.explode()
            

    def _handleDropped(self,m):
        if self.bombType in ['landMine','cake','tesla']:
            self.armTimer = bs.Timer(1250,bs.WeakCall(self.handleMessage,ArmMessage()))
            
        elif self.bombType == 'magnet': self._magnetDropped = True
            
        elif self.bombType == 'glue':
            self.armTimer = bs.Timer(100,bs.WeakCall(self.handleMessage,ArmMessage()))

        # once we've thrown a sticky bomb we can stick to it..
        elif self.bombType == 'sticky':
            def _safeSetAttr(node,attr,value):
                if node.exists(): setattr(node,attr,value)
            #bs.gameTimer(250,bs.Call(_safeSetAttr,self.node,'stickToOwner',True))
            bs.gameTimer(250,lambda: _safeSetAttr(self.node,'stickToOwner',True))
        elif self.bombType == 'gloo': #self.bombType == 'sticky'
            def _safeSetAttr(node,attr,value):
                if node.exists(): setattr(node,attr,value)
            #bs.gameTimer(250,bs.Call(_safeSetAttr,self.node,'stickToOwner',True))
            bs.gameTimer(250,lambda: _safeSetAttr(self.node,'sticky',True))

    def _handleSplat(self,m):
        node = bs.getCollisionInfo("opposingNode")
        if node is not self.owner and bs.getGameTime() - self._lastStickySoundTime > 1000:
            self._lastStickySoundTime = bs.getGameTime()
            bs.playSound(self.getFactory().stickyImpactSound,2.0,position=self.node.position)
            if node.getNodeType() == 'spaz': bs.playSound(self.getFactory().stickyImpactPlayerSound,1.0,position=self.node.position)

    def addExplodeCallback(self,call):
        """
        Add a call to be run when the bomb has exploded.
        The bomb and the new blast object are passed as arguments.
        """
        self._explodeCallbacks.append(call)
        
    def explode(self):
        """
        Blows up the bomb if it has not yet done so.
        """
        if self.blastBuffed: 
            try:
                bs.playSound(self.getFactory().explodeBuffedSound,self.blastRadius/1.35,position=self.node.position)
                bs.gameTimer(1,self.lightBuff.delete)
                self.lightExplode = bs.newNode('light',
                            attrs={'position':self.node.position,
                                    'color': (1.0,1.0,0.2),
                                    'volumeIntensityScale': 0.5})     
                bs.animate(self.lightExplode,'intensity',{0:0,100:self.blastRadius/2,500:0},loop=False)
                bs.gameTimer(500,self.lightExplode.delete)  
            except AttributeError: pass
            
        if self.bombType == 'cluster':
            try:
                #E E
                #E X
                p = self.node.position
                bs.StickyNet((p[0]+0.4,p[1]+2.9,p[2]+0.9),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]+1.2,p[1]+2.9,p[2]+0.9),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]+0.4,p[1]+2.9,p[2]),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]+1.2,p[1]+2.9,p[2]),
                    (0,0,0)).autoRetain()
                #E E
                #X E
                bs.StickyNet((p[0]-0.4,p[1]+2.9,p[2]+0.9),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]-1.2,p[1]+2.9,p[2]+0.9),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]-0.4,p[1]+2.9,p[2]),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]-1.2,p[1]+2.9,p[2]),
                    (0,0,0)).autoRetain()
                #X E
                #E E
                bs.StickyNet((p[0]-0.4,p[1]+2.9,p[2]-1.8),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]-1.2,p[1]+2.9,p[2]-1.8),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]-0.4,p[1]+2.9,p[2]-0.9),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]-1.2,p[1]+2.9,p[2]-0.9),
                    (0,0,0)).autoRetain()
                #E X
                #E E
                bs.StickyNet((p[0]+0.4,p[1]+2.9,p[2]-1.8),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]+1.2,p[1]+2.9,p[2]-1.8),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]+0.4,p[1]+2.9,p[2]-0.9),
                    (0,0,0)).autoRetain()
                bs.StickyNet((p[0]+1.2,p[1]+2.9,p[2]-0.9),
                    (0,0,0)).autoRetain()
            except: pass
            
        if self.bombType == 'glue':
            try:
                p = self.node.position
                v = self.node.velocity
                if self.blastBuffed: 
                    maxTime = 10000
                    glueRadius = 3
                else:
                    maxTime = 8000
                    glueRadius = 2
                    
                centerDistance = 0.3
                distance = 0.7
                distance2 = 0.55
                height = 3
                timeIncrement = 1500
                
                if not bs.getActivity().getMap().isFlying:
                    for x in range(-1,2,2):
                        for y in range(-1,2,2):
                            bs.Glue((p[0]+(centerDistance*x),p[1],p[2]+(centerDistance*y)),
                                (0,height,0),
                                maxTime).autoRetain()
                else:
                    bs.Glue((p[0],p[1],p[2]),
                            (0,height,0),
                            maxTime).autoRetain()
                    for i in range(glueRadius):
                        bs.Glue((p[0]+distance+(i*distance),p[1],p[2]),
                        (0,height,0),maxTime-timeIncrement-(i*timeIncrement)).autoRetain()
                        
                        bs.Glue((p[0]-distance-(i*distance),p[1],p[2]),
                        (0,height,0),maxTime-timeIncrement-(i*timeIncrement)).autoRetain()
                
                if not bs.getActivity().getMap().isFlying:
                    for i in range(glueRadius):
                        bs.Glue((p[0]+distance+(i*distance),p[1],p[2]),
                        (0,height,0),
                        maxTime-timeIncrement-(i*timeIncrement)).autoRetain()
                        bs.Glue((p[0]-distance-(i*distance),p[1],p[2]),
                        (0,height,0),
                        maxTime-timeIncrement-(i*timeIncrement)).autoRetain()
                        bs.Glue((p[0],p[1],p[2]+distance+(i*distance)),
                        (0,height,0),
                        maxTime-timeIncrement-(i*timeIncrement)).autoRetain()
                        bs.Glue((p[0],p[1],p[2]-distance-(i*distance)),
                        (0,height,0),
                        maxTime-timeIncrement-(i*timeIncrement)).autoRetain()
                        bs.Glue((p[0]-distance2-(i*distance2),p[1],p[2]-distance2-(i*distance2)),
                        (0,height,0),
                        maxTime-timeIncrement-(i*timeIncrement)).autoRetain()
                        bs.Glue((p[0]+distance2+(i*distance2),p[1],p[2]+distance2+(i*distance2)),
                        (0,height,0),
                        maxTime-timeIncrement-(i*timeIncrement)).autoRetain()
                        bs.Glue((p[0]+distance2+(i*distance2),p[1],p[2]-distance2-(i*distance)),
                        (0,height,0),
                        maxTime-timeIncrement-(i*timeIncrement)).autoRetain()
                        bs.Glue((p[0]-distance2-(i*distance2),p[1],p[2]+distance2+(i*distance2)),
                        (0,height,0),
                        maxTime-timeIncrement-(i*timeIncrement)).autoRetain()
            except: pass
                
        if not self.bombType in ['basketball','gloo']: # Basketballs and Hot Volts cannot be destroyed by bombs
            if self._exploded: return
            self._exploded = True
            activity = self.getActivity()
            if self.bombType == 'healing':
                bs.playSound(self.getFactory().healingSound,1,position=self.node.position)
            if activity is not None and self.node.exists():
                if self.bombType == 'dynamite':
                    blast = Blast(position=self.node.position,velocity=self.node.velocity,
                            blastRadius=self.blastRadius,blastType=self.bombType,blastRadiusBuffed=self.blastBuffed,
                            sourcePlayer=self.sourcePlayer,hitType=self.bombType,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    for c in self._explodeCallbacks: c(self,blast)
                    t = self.node.position
                    # Determines how far apart these clusters are
                    self.bombDistance = 0.9
                    # a1
                    Blast(position=(t[0]+(self.bombDistance*1), t[1], t[2]),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # b1                                                                                                                                                                  
                    Blast(position=(t[0]-(self.bombDistance*1), t[1], t[2]),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # c1                                                                                                                                                                  
                    Blast(position=(t[0], t[1], t[2]+(self.bombDistance*1)),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # d1                                                                                                                                                                  
                    Blast(position=(t[0], t[1], t[2]-(self.bombDistance*1)),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # a2                                                                                                                                                                  
                    Blast(position=(t[0]+(self.bombDistance*2), t[1], t[2]),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # b2                                                                                                                                                                  
                    Blast(position=(t[0]-(self.bombDistance*2), t[1], t[2]),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # c2                                                                                                                                                                  
                    Blast(position=(t[0], t[1], t[2]+(self.bombDistance*2)),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # d2                                                                                                                                                                  
                    Blast(position=(t[0], t[1], t[2]-(self.bombDistance*2)),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # a3                                                                                                                                                                  
                    Blast(position=(t[0]+(self.bombDistance*3), t[1], t[2]),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # b3                                                                                                                                                                  
                    Blast(position=(t[0]-(self.bombDistance*3), t[1], t[2]),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # c3                                                                                                                                                                 
                    Blast(position=(t[0], t[1], t[2]+(self.bombDistance*3)),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    # d3                                                                                                                                                                  
                    Blast(position=(t[0], t[1], t[2]-(self.bombDistance*3)),velocity=(0,2,0),blastRadius=self.blastRadius,blastType='miniDynamite',sourcePlayer=self.sourcePlayer,hitType=self.bombType,blastRadiusBuffed=self.blastBuffed,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                elif self.bombType == 'hijump':
                    blast = Blast(position=(self.node.position[0],self.node.position[1]-1.15,self.node.position[2]),        velocity=self.node.velocity,
                            blastRadius=self.blastRadius,blastType=self.bombType,blastRadiusBuffed=self.blastBuffed,sourcePlayer=self.sourcePlayer,hitType=self.bombType,hitSubType=self.hitSubType).autoRetain()
                    for c in self._explodeCallbacks: c(self,blast)
                else:
                    if self.hitType == 'punch': hit = 'punch'
                    else: hit = 'impact'
                    blast = Blast(position=self.node.position,velocity=self.node.velocity,
                                blastRadius=self.blastRadius,blastType=self.bombType,blastRadiusBuffed=self.blastBuffed,sourcePlayer=self.sourcePlayer,hitType=hit,hitSubType=self.hitSubType,hitSubTypeTrue=self.hitSubTypeTrue).autoRetain()
                    for c in self._explodeCallbacks: c(self,blast)
                    
            # if the bomb explodes, count that to the statistics
            bs.statAdd('Bomb Explosions')
            
            # handle custom bomb shapes
            if self.bombType in ['normal','ice','fire','knocker','sticky','palette','infatuate']: 
                sound = self.bombShape[1]
                try: volume = self.bombShape[2]
                except: volume = 0.0
                if not sound: pass
                else: 
                    try: bs.playSound(random.choice(sound),volume,position=self.node.position)
                    except AttributeError: pass
            
            # we blew up so we need to go away
            bs.gameTimer(1,bs.WeakCall(self.handleMessage,bs.DieMessage()))
        

    def _handleWarn(self,m):
        if self.textureSequence.exists():
            self.textureSequence.rate = 30
            bs.playSound(self.getFactory().warnSound,0.5,position=self.node.position)

    def _addMaterial(self,material):
        if not self.node.exists(): return
        materials = self.node.materials
        if not material in materials:
            self.node.materials = materials + (material,)
            
    def deploy(self):
        # Used for complex bomb animations, sounds or effects. Everything here is great!
        if not self.node.exists(): return
        factory = self.getFactory()
        if self.bombType == 'combat':
            self.light = bs.newNode('light',
                            attrs={'position':self.node.position,
                                    'color': (0.02,0.069,0.09),
                                    'volumeIntensityScale': 0.5})
            self.textureSequence = bs.newNode('textureSequence',
                                                owner=self.node,
                                                attrs={'inputTextures':(factory.combatTex,
                                                                        factory.combatLitTex),'rate':5})
            self.node.connectAttr('position',self.light,'position')
            self.textureSequence.connectAttr('outputTexture',self.node,'colorTexture')
            bs.animate(self.light,'intensity',{0:10, 200:0},loop=False)  
            
            bs.gameTimer(200,self.textureSequence.delete)
            bs.gameTimer(200,self.light.delete)
            bs.playSound(factory.combatBombDeployedSound,0.3,position=self.node.position)
        elif self.bombType == 'iceMeteor':
            bsUtils.animate(self.node, 'modelScale', {0:0, 
                                   200:3.5})
        elif self.bombType == 'ice':
            bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=10,spread=0.5,scale=0.3,chunkType='ice',emitType='stickers');
            bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=int(2+random.random()*2),scale=0.25,chunkType='ice');
            for i in range(6+random.randint(4,8)):
                bs.Particle(self.node.position,
                           (self.node.velocity[0]+random.uniform(-6,6),self.node.velocity[1],self.node.velocity[2]+random.uniform(-6,6)),
                           'snow',
                           random.uniform(0.05,0.25))
        elif self.bombType == 'snowball':
            bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=7,spread=0.3,scale=0.2,chunkType='ice',emitType='stickers');
            bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=int(1+random.random()*2),scale=0.1,chunkType='ice');
            for i in range(1+random.randint(0,1)):
                bs.Particle(self.node.position,
                           (self.node.velocity[0]+random.uniform(-6,6),self.node.velocity[1],self.node.velocity[2]+random.uniform(-6,6)),
                           'snow',
                           random.uniform(0.01,0.05))
        elif self.bombType == 'sticky':
            bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=int(2.0+random.random()*4),spread=0.4,chunkType='slime');
            bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=int(2.0+random.random()*4),scale=0.2, spread=0.4,chunkType='slime');
            bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=5,scale=0.3,chunkType='slime',emitType='stickers');
        elif self.bombType == 'gloo': 
            bsUtils.animate(self.node,"modelScale",{0:0, 250:1.14, 500:1.14, 30000-200:1.35,30000:0})
        elif self.bombType == 'firework': 
            bsUtils.animate(self.node,"modelScale",{0:0, 90:0.63})
        elif self.bombType == 'cake': 
            position = self.node.position
            velocity = self.node.velocity
            bs.playSound(factory.cakeSpawnSound,1,position)
            self.cakeActive = False
            for i in range(1+random.randint(1,3)): # Dizzy Cake dough (big chunks)
                bs.Particle(position,
                            (velocity[0]+random.uniform(-6,6),velocity[1]+random.uniform(-6,6),velocity[2]+random.uniform(-6,6)),
                            'cake',
                            random.uniform(0.3,0.85))
            for i in range(3+random.randint(4,7)): # Dizzy Cake dough
                bs.Particle(position,
                            (velocity[0]+random.uniform(-6,6),velocity[1]+random.uniform(-6,6),velocity[2]+random.uniform(-6,6)),
                            'cake',
                            random.uniform(0.1,0.5))
            for i in range(2+random.randint(2,5)): # Dizzy Cake dough
                bs.Particle(position,
                            (velocity[0]+random.uniform(-6,6),velocity[1]+random.uniform(-6,6),velocity[2]+random.uniform(-6,6)),
                            'infatuate',
                            random.uniform(0.1,0.5))
        elif self.bombType == 'grenade':
            t = self.node.position
            bs.playSound(factory.pinOutSound,1,position=self.node.position)
            bs.emitBGDynamics(position=(t[0], t[1], t[2]),velocity=(0.25, 0.25, 0.35),count=1,scale=1.5,spread=0.1,chunkType='rock');
            self.textureSequence = bs.newNode('textureSequence',
                                                owner=self.node,
                                                attrs={'inputTextures':(factory.grenade3Tex,
                                                                        factory.grenade2Tex,
                                                                        factory.grenade1Tex,
                                                                        factory.grenadeExTex),'rate':975})
            self.textureSequence.connectAttr('outputTexture',self.node,'colorTexture')       
            bsUtils.animate(self.node, 'modelScale', {0:0, 
                                   200:1.3,
                                   260:1,
                                   380:1.2,
                                   2950:1.0,
                                   3050:10.0,
                                   3100:12.0})
            bs.gameTimer(3250,self.textureSequence.delete)
        elif self.bombType == 'fraction':
            bsUtils.animate(self.node, 'modelScale', {0:0, 
                                   200:0.799})
        elif self.bombType == 'dynamite':
            t = self.node.position
            bs.playSound(factory.dynamiteFuseSound,1.25,position=self.node.position)
        elif self.bombType == 'splash':
            bsUtils.animate(self.node, 'modelScale', {50:1.0,
                                   200:0.9,
                                   380:1.05,
                                   500:1.0,
                                   1000:0.95,
                                   1500:1.0,
                                   1800:0.9,
                                   2175:1.0}, True)
        elif self.bombType == 'ranger':
            self.rangerBeats = bs.newNode('sound',owner=self.node,attrs={'sound':factory.crystalBeatSound,'volume':1.0})
            def charge(): 
                try:
                    self.node.flashing = 1
                    bs.playSound(factory.crystalChargeSound,1.0,position=self.node.position)
                except: pass
            self.chargeSound = bs.Timer(3400,bs.Call(charge))
            bsUtils.animate(self.node, 'modelScale', {0:0,
                                   200:1.3,
                                   260:1,
                                   1000:1.10,
                                   1500:0.95,
                                   2000:1.05,
                                   2500:0.90,
                                   3000:1.1,
                                   3500:0.85,
                                   3800:1.15,
                                   3900:0.5,
                                   4000:5.0})
        elif self.bombType == 'healing':
            bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=int(6.0+random.random()*50),scale=0.8,spread=1.0,chunkType='spark');
            bsUtils.animate(self.node, 'modelScale', {0:0,
                                   200:1.3,
                                   260:1,
                                   500:1.1,
                                   1000:1.0,
                                   1500:1.1,
                                   1950:1.0,
                                   2375:1.1,
                                   2725:1.0,
                                   3075:1.1,
                                   3350:1.0,
                                   3625:1.1,
                                   3725:1.0,
                                   3825:1.1,
                                   3925:1.0,
                                   4025:1.1,
                                   4125:1.0,
                                   4225:1.1,
                                   4325:1.0,
                                   4425:1.1,
                                   4525:1.0,
                                   4625:1.1,
                                   4725:1.0,
                                   4825:1.1,
                                   4925:1.0,
                                   5000:2.0})
        elif self.bombType == 'hijump':
            self.light = bs.newNode('light',
                            attrs={'position':self.node.position,
                                    'color': (1,0.01,0.95),
                                    'volumeIntensityScale': 0.5})   
            bs.animate(self.light,'intensity',{0:2, 1000:0},loop=False)                                    
            bs.gameTimer(500,self.light.delete)
            
    def ready(self):
        # An alternative node for advanced sounds, effects or functions of bombs!
        if not self.node.exists(): return
        factory = self.getFactory()
        if self.bombType == 'combat':
            self.light = bs.newNode('light',
                            attrs={'position':self.node.position,
                                    'color': (0.0,0.49,0.7),
                                    'volumeIntensityScale': 0.5})
            self.textureSequence = bs.newNode('textureSequence',
                                                owner=self.node,
                                                attrs={'inputTextures':(factory.combatTex,
                                                                        factory.combatLitTex),'rate':10})
            self.node.connectAttr('position',self.light,'position')
            self.textureSequence.connectAttr('outputTexture',self.node,'colorTexture')
            
            bs.animate(self.light,'intensity',{0:2.5, 250:0},loop=False)  
            bs.gameTimer(250,self.textureSequence.delete)
            bs.gameTimer(250,self.light.delete)
            bs.playSound(factory.combatBombReadySound,0.3,position=self.node.position)
        elif self.bombType == 'tesla':
            self.teslaHealth -= 5
            self.teslaArea.hurt = 1.0 - float(self.teslaHealth)/self.teslaHealthMax
            if self.teslaHealth <= 0: self.explode()
            if random.randint(0,1): bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=int(4.0+random.random()*20),scale=1.0,spread=0.5,chunkType='spark');
            
            
            # Assume everyone's dead until proven living
            alivePlayers = False
            
            spazList = []
            for n in bs.getNodes():
                if n.getNodeType() == 'spaz': spazList.append(n)
            
            if not spazList: return
            
            # Get the position for every player inside to damage
            for player in spazList:
                try:
                    if player.getDelegate().exists() and not player.getDelegate()._dead:
                        alivePlayers = True
                        distanceX = player.position[0] - self.node.position[0]
                        distanceY = player.position[1] - self.node.position[1]
                        distanceZ = player.position[2] - self.node.position[2]
                        distance = math.sqrt(pow(distanceX,2) + pow(distanceY,2) + pow(distanceZ,2))
                        if distance < self.blastRadius*1.3: 
                            # Harm enemies, heal allies
                            if self.sourcePlayer.getTeam() != player.getDelegate().sourcePlayer.getTeam():
                                player.handleMessage(bs.HitMessage(flatDamage=self.teslaDamage,hitSubType='tesla_zap',sourcePlayer=self.sourcePlayer))
                except AttributeError: pass
                        
            if not alivePlayers: return
            
        elif self.bombType == 'magnet':
            bs.gameTimer(50,bs.WeakCall(self.handleMessage,ReadyMessage()))
            
            self._existenceTimer += 1
            # Assume everyone's dead until proven living
            alivePlayers = False
            playerNearest = None
            distanceNearest = float('inf')
            
            # How many players are currently in the game? Do nothing if none are present.
            spazList = []
            for n in bs.getNodes():
                if n.getNodeType() == 'spaz': spazList.append(n)
            
            if not spazList: return
            
            # Get the position for every player
            for player in spazList:
                playerSpaz = player
                if not player.getDelegate()._dead:
                    alivePlayers = True
                    distanceX = playerSpaz.position[0] - self.node.position[0]
                    distanceY = playerSpaz.position[1] - self.node.position[1]
                    distanceZ = playerSpaz.position[2] - self.node.position[2]
                    distance = math.sqrt(pow(distanceX,2) + pow(distanceY,2) + pow(distanceZ,2))
                    if distance < distanceNearest:
                        playerNearest = player
                        distanceNearest = distance
                        distanceNearestX = distanceX
                        distanceNearestY = distanceY
                        distanceNearestZ = distanceZ
            if not alivePlayers: return
            
            # Handle random noises
            self._mumbleCounter += random.randint(1,5)
            if self._mumbleCounter >= 60:
                self._mumbleCounter = 0
                sounds = self.getFactory().magnetMumbleSounds
                sound = sounds[random.randrange(len(sounds))]
                bs.playSound(sound,0.5,position=self.node.position)
                
            # Weigh down the bomb based on how long it exists
            self.node.gravityScale = 1.0 + (self._existenceTimer*0.005)
            
            # Push the bomb to the nearest player
            self.node.handleMessage('impulse',self.node.position[0],self.node.position[1],self.node.position[2],
                0,0,0,
                15+(self._existenceTimer*0.25),15+(self._existenceTimer*0.25),0,0,distanceNearestX,max(0,distanceNearestY/5),distanceNearestZ)
            
            # Calculate speed. If the bomb is way too slow, assumes it's stuck and forces a jump.
            speed = math.sqrt(pow(self.node.velocity[0],2) + pow(self.node.velocity[1],2) + pow(self.node.velocity[2],2))
            self._idleCounter -= 0.1
            if self._idleCounter < 0: self._idleCounter = 0
            if speed < 3:
                self._idleCounter += 1
                if self._idleCounter >= 10:
                    bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=int(4.0+random.random()*4),emitType='tendrils',tendrilType='smoke')
                    self.node.handleMessage('impulse',self.node.position[0],self.node.position[1],self.node.position[2],
                                0,0,0,
                                150+(self._jumpCounter*25),100+(self._jumpCounter*17),0,0,self.node.position[0],self.node.position[1]+5,self.node.position[2])
                    self._idleCounter = 0
                    self._jumpCounter += 1
                    bs.playSound(factory.magnetJumpSound,1.0,position=self.node.position)
            
    def moreFlames(self):
        """
        Just a slightly delayed additional particle effects
        """
        self.light = bs.newNode('light',
                            attrs={'position':self.node.position,
                                    'color': (1.0,0.49,0.15),
                                    'volumeIntensityScale': 0.5})
        bs.gameTimer(200,self.light.delete)
        
    def arm(self):
        """
        Arms land-mines and impact-bombs so
        that they will explode on impact.
        """
        if not self.node.exists(): return
        factory = self.getFactory()
        if self.bombType == 'landMine':
            self.textureSequence = bs.newNode('textureSequence',
                                              owner=self.node,
                                              attrs={'inputTextures':(factory.landMineLitTex,
                                                                      factory.landMineTex),'rate':30})
            self.textureSequence.connectAttr('outputTexture',self.node,'colorTexture')
            bs.playSound(factory.activateSound,0.5,position=self.node.position)
            bs.gameTimer(500,self.textureSequence.delete)
            # we now make it explodable.
            bs.gameTimer(250,bs.WeakCall(self._addMaterial,factory.landMineBlastMaterial))
            self._armed = True
        elif self.bombType == 'tesla':
        
            # don't create a shield etc if the pad was already active
            if self.teslaActive: return
            self.teslaActive = True
            self.teslaArea = bs.newNode('shield',owner=self.node,
                                        attrs={'color':self.sourcePlayer.color,
                                               'radius':self.blastRadius*2,
                                               'alwaysShowHealthBar':True})
            self.node.connectAttr('position',self.teslaArea,'position')
            
            sound = bs.newNode('sound',owner=self.node,attrs={'sound':factory.teslaShieldIdleSound,'volume':0.4})
            self.node.connectAttr('position',sound,'position')
            
            self.zone = bs.newNode('locator',owner=self.node,
                                   attrs={'shape':'circle',
                                   'position':self.node.position,
                                   'color':self.sourcePlayer.color,
                                   'opacity':0.05,
                                   'size':[0.0],
                                   'drawBeauty':True,
                                   'additive':True})
            self.node.connectAttr('position',self.zone,'position')
            bs.animateArray(self.zone,'size',1,{0:[0.0],150:[self.blastRadius*3],200:[self.blastRadius*2.5]})
            
            self.teslaBarrier = bs.newNode('region',owner=self.node,delegate=self,
                                    attrs={'position':self.node.position,
                                           'scale':(self.blastRadius,self.blastRadius,self.blastRadius),
                                           'type':'sphere',
                                           'materials':[factory.teslaBarrierMaterial]})
            self.node.connectAttr('position',self.teslaBarrier,'position')
            
            self.teslaArea.hurt = 0
            self.teslaHealth = self.teslaHealthMax
            
            bsUtils.animate(self.node,"modelScale",{0:1.0, 150:1.1, 300:1},True)
             
            self.teslaTimer = bs.Timer(250,bs.WeakCall(self.handleMessage,ReadyMessage()),True)

        elif self.bombType == 'glue':
            def _spawnGlue():
                if self.node.exists():
                    bs.Glue(self.node.position,
                        (0,1,0),
                        4000).autoRetain()
                    bs.gameTimer(150,_spawnGlue)
            bs.gameTimer(150,_spawnGlue)
        elif self.bombType == 'magnet' and not self._armed and self._magnetDropped:
            self._armed = True
            self._idleCounter = 0
            self._mumbleCounter = 0
            self._jumpCounter = 0
            self._existenceTimer = 0
            
            self.light = bs.newNode('light',
                            owner=self.node,
                            attrs={'position':self.node.position,
                                    'color': (1.0,0.0,0.0),
                                    'volumeIntensityScale': 0.5})
            c = bs.newNode("combine",attrs={'input0':1.0,'input1':0.0,'input2':0.0,'size':3})
            bs.animate(c,'input0',{
                0:1.0, # Red
                850:0.0, # Blue
                1250:0.5}) # Purple
            bs.animate(c,'input1',{
                0:0.0, # Red
                850:0.0, # Blue
                1250:0.0}) # Purple
            bs.animate(c,'input2',{
                0:0.0, # Red
                850:1.0, # Blue
                1250:1.0}) # Purple
            c.connectAttr('output',self.light,'color')
            bs.animate(self.light,'intensity',{
                0:0.0,
                250:1.2,
                1000:1.2,
                1250:0.35})
            self.node.connectAttr('position',self.light,'position')
            #self.magnetRing = bs.newNode('shield',
            #                            owner=self.node,
            #                            attrs={'color':(0.5,0,1.0),'radius':0.8})
            #self.magnetRing.hurt = 0.0
            #bs.animate(self.magnetRing,'radius',{
            #    0:0.0,
            #    250:1.0,
            #    350:1.2,
            #    550:1.0,
            #    1000:0.8,})
            #self.node.connectAttr('position',self.magnetRing,'position')
            bs.playSound(factory.magnetActivateSound,1.0,position=self.node.position)
            
            def expiration():
                if self.node.exists():
                    self.expireSound = bs.newNode('sound',owner=self.node,attrs={'sound':factory.magnetExpireSound,'volume':1.0})
                    self.node.connectAttr('position',self.expireSound,'position')
                    self.light.color = (1.0,0.0,0.0)
                    self.light.intensity = 0.65
            bs.gameTimer(100,bs.WeakCall(self.handleMessage,ReadyMessage()))
            bs.gameTimer(125,bs.WeakCall(self._addMaterial,factory.magnetBlastMaterial))
            self.expireTimer = bs.Timer(5900,expiration)
            bs.gameTimer(10000,bs.WeakCall(self.handleMessage,ExplodeMessage()))
        elif self.bombType == 'impact':
            self.textureSequence = bs.newNode('textureSequence',
                                              owner=self.node,
                                              attrs={'inputTextures':(factory.impactLitTex,
                                                                      factory.impactTex,
                                                                      factory.impactTex),'rate':100})
            bs.gameTimer(250,bs.WeakCall(self._addMaterial,factory.landMineBlastMaterial))
            self.textureSequence.connectAttr('outputTexture',self.node,'colorTexture')
            bs.playSound(factory.activateSound,0.5,position=self.node.position)
        elif self.bombType == 'cake':
            self.outcome = random.randint(1,7)
            self.light = bs.newNode('light',
                        attrs={'position':self.node.position,
                                'color': (0.7,0.7,0.7),
                                'volumeIntensityScale': 1.0}) 
            self.node.connectAttr('position',self.light,'position')
            
            try: bs.getActivity()._cakeMusicCount += 1
            except: 
                bs.getActivity()._cakeMusicCount = 0
                if bsUtils.gMusic.volume != 0.0: bs.getActivity()._cakeMusicVolume = bsUtils.gMusic.volume
                bs.getActivity()._cakeMusicCount += 1
            try:
                if bs.getActivity()._cakeMusicCount > 0: bsUtils.gMusic.volume = 0.0
            except NoneType: pass
            
            self.cakeActive = True
            
            if self.outcome == 1: # Hornzy
                bs.animate(self.light,'intensity',{0:0.5,580:0.0},loop=True)
                self.sound = factory.cake1Sound
                self.time = 3450
            elif self.outcome == 2: # Polish National Anthem
                bs.animate(self.light,'intensity',{0:0.5,455:0.0},loop=True)
                self.sound = factory.cake2Sound
                self.time = 4600
            elif self.outcome == 3: # Jingle
                bs.animate(self.light,'intensity',{0:0.5,610:0.0},loop=True)
                self.sound = factory.cake3Sound
                self.time = 2600
            elif self.outcome == 4: # Circus
                bs.animate(self.light,'intensity',{0:0.5,595:0.0},loop=True)
                self.sound = factory.cake4Sound
                self.time = 3450 #8900
            elif self.outcome == 5: # Hard Rock
                bs.animate(self.light,'intensity',{0:0.5,470:0.0},loop=True)
                self.sound = factory.cake5Sound
                self.time = 3935
            elif self.outcome == 6: # Slap Funk
                bs.animate(self.light,'intensity',{0:0.5,565:0.0},loop=True)
                self.sound = factory.cake6Sound
                self.time = 4425
            elif self.outcome == 7: # Fun Trumpet
                bs.animate(self.light,'intensity',{0:0.5,490:0.0},loop=True)
                self.sound = factory.cake7Sound
                self.time = 4967
                
            if bs.getActivity()._isSlowMotion: 
                self.musicTime = self.time * 2.6
                self.time = int(self.time * 0.8)
            else: 
                self.musicTime = self.time
                
            self.cakeMusic = bs.newNode('sound',owner=self.node,attrs={'sound':self.sound,'volume':1.0})
            
            # This little line prevents the music from looping when the game is paused
            if self.outcome == 3: bs.netTimer(int(self.musicTime+50),bs.Call(self.cakeMusic.delete))
            elif self.outcome in [4,6]: bs.netTimer(int(self.musicTime+300),bs.Call(self.cakeMusic.delete))
            else: bs.netTimer(int(self.musicTime+500),bs.Call(self.cakeMusic.delete))
            
            self.cakeZone = bs.newNode('locator',owner=self.node,
                                   attrs={'shape':'circleOutline',
                                   'position':self.node.position,
                                   'color':(1,1,1),
                                   'opacity':0.0,
                                   'size':[self.blastRadius*2.05],
                                   'drawBeauty':False,
                                   'additive':True})
            bs.animate(self.cakeZone, 'opacity', {0:0.0,self.time:0.05})
            self.node.connectAttr('position',self.cakeZone,'position')
            
            bs.gameTimer(self.time,bs.WeakCall(self.handleMessage,ExplodeMessage()))
            bs.gameTimer(self.time,self.light.delete)
            bs.animate(self.node, 'modelScale', {0:1.0,
                                                 250:1.2,
                                                 int(round(self.time/4)):1.0,
                                                 int(round(self.time/2)):1.2,
                                                 int(round(self.time/1.3325)):1.0,
                                                 self.time:1.3})
        else: return
        
    def _handleHit(self,m):
        isPunch = (m.srcNode.exists() and m.srcNode.getNodeType() == 'spaz')
        
        if not self._exploded and isPunch and self.bombType in ['landMine']:
            if m.sourcePlayer not in [None]:
                self.hitType = 'punch'
                self.hitSubType = 'landMine'
                bs.gameTimer(150,bs.WeakCall(self.handleMessage,ExplodeMessage()))
        elif not self._exploded and isPunch and not self.bombType in ['landMine','tesla','burger','cake','basketball']:
            self.node.handleMessage("impulse",self.node.position[0],self.node.position[1],self.node.position[2],
                                0,0,0,
                                m.magnitude*2,m.velocityMagnitude*2,0,0,m.velocity[0],m.velocity[1],m.velocity[2])
                
        else: 
            # normal bombs are triggered by non-punch impacts..  impact-bombs by all impacts
            if not self._exploded and not isPunch or self.bombType in ['impact','snowball','landMine']:
                # also lets change the owner of the bomb to whoever is setting us off..
                # (this way points for big chain reactions go to the person causing them)
                if m.sourcePlayer not in [None]:
                    if self.bombType not in ['tesla','cake']: self.sourcePlayer = m.sourcePlayer
    
                    # also inherit the hit type (if a landmine sets off by a bomb, the credit should go to the mine)
                    # the exception is TNT.  TNT always gets credit.
                    # Knocker and Dizzy Cake here is an exception to not bug out the damage scale calculations.
                    if self.bombType not in ['tnt','tntC','burger','landMine','cake','knocker','tesla']:
                        self.hitType = m.hitType
                        self.hitSubType = m.hitSubType
    
                if m.hitSubType not in ['healing','hijump','knocker','cake','tesla','splash','infatuate']: # Only the bombs not mentioned in this line will cause other bombs to explode (insane blast radius or something)
                    if self.bombType == 'landMine':
                        if not self.mineDamaged and self._armed: 
                            factory = self.getFactory()
                            bs.emitBGDynamics(position=self.node.position,velocity=self.node.velocity,count=int(2.0+random.random()*4),scale=0.4,chunkType='rock');
                            for i in range(2+random.randint(1,6)):
                                bs.Particle(self.node.position,
                                            (self.node.velocity[0]+random.uniform(-3,3),self.node.velocity[1]+random.uniform(2,5),self.node.velocity[2]+random.uniform(-3,3)),
                                            'landMine',
                                            random.uniform(0.01,0.1))
                            bs.playSound(factory.landMineDamageSound,position=self.node.position,volume=2.0)
                            self.node.colorTexture = factory.landMineDamagedTex
                            self.mineDamaged = True
                            return
                    # retain bomb's unique abilities if the types match up
                    if self.bombType == m.hitSubType: self.hitSubTypeTrue = True
                    else: self.hitSubTypeTrue = False
                    if self.bombType != 'tesla': bs.gameTimer(100+int(random.random()*100),bs.WeakCall(self.handleMessage,ExplodeMessage()))
        self.node.handleMessage("impulse",m.pos[0],m.pos[1],m.pos[2],
                                m.velocity[0],m.velocity[1],m.velocity[2],
                                m.magnitude,m.velocityMagnitude,m.radius,0,m.velocity[0],m.velocity[1],m.velocity[2])

        if m.srcNode.exists():
            pass
            #print 'FIXME HANDLE KICKBACK ON BOMB IMPACT'
            # bs.nodeMessage(m.srcNode,"impulse",m.srcBody,m.pos[0],m.pos[1],m.pos[2],
            #                     -0.5*m.force[0],-0.75*m.force[1],-0.5*m.force[2])
            
    def _dizzy(self):
        alivePlayers = False
        playerNearest = None
        distanceSpaz = []
        distanceNearest = float('inf')
        
        # How many players are currently in the game? Do nothing if none are present.
        spazList = []
        for n in bs.getNodes():
            if n.getNodeType() == 'spaz': spazList.append(n)
        
        if not spazList: return
        
        # Get the position for every player
        for player in spazList:
            playerSpaz = player
            if not player.getDelegate()._dead:
                alivePlayers = True
                distanceX = playerSpaz.position[0] - self.node.position[0]
                distanceY = playerSpaz.position[1] - self.node.position[1]
                distanceZ = playerSpaz.position[2] - self.node.position[2]
                distance = math.sqrt(pow(distanceX,2) + pow(distanceY,2) + pow(distanceZ,2))
                if distance < distanceNearest:
                    playerNearest = player
                    distanceNearest = distance
                    distanceNearestX = distanceX
                    distanceNearestY = distanceY
                    distanceNearestZ = distanceZ
        if not alivePlayers: return
        
        # Push the bomb to the nearest player
        self.node.handleMessage('impulse',self.node.position[0],self.node.position[1],self.node.position[2],
            0,0,0,
            300,300,0,0,distanceNearestX,distanceNearestY+1,distanceNearestZ)
        
        
    def dissolve(self):
        """
        This command basically makes the bomb die, because of the Healing Bomb.
        """
        bs.playSound(self.getFactory().hissSound,3,position=self.node.position)
        if self.bombType not in ['basketball','burger']: self.handleMessage(bs.DieMessage())
        elif self.bombType == 'healing': self.handleMessage(bs.ExplodeMessage())
        else: self.handleMessage(bs.DieMessage())
        
    def handleMessage(self,m):
        if isinstance(m,ExplodeMessage): self.explode()
        elif isinstance(m,ImpactMessage): self._handleImpact(m)
        elif isinstance(m,bs.TeslaMessage): self._handleTesla(m)
        elif isinstance(m,bs.PickedUpMessage):
            # change our source to whoever just picked us up *only* if its None
            # and only if it's not armed (to avoid picking up land-mines and claiming ownership)
            # this way we can get points for killing bots with their own bombs
            # hmm would there be a downside to this?...
            if self.sourcePlayer is not None and not self._armed:
                if self.bombType != 'tesla': self.sourcePlayer = m.node.sourcePlayer
                
            # if we're a land-mine that got armed, explode
            if self.bombType == 'landMine' and self._armed: 
                def detonate(): self.handleMessage(ExplodeMessage())
                bs.gameTimer(100,detonate)
        elif isinstance(m,SplatMessage): self._handleSplat(m)
        elif isinstance(m,bs.DroppedMessage): self._handleDropped(m)
        elif isinstance(m,bs.DizzyMessage): self._dizzy()
        elif isinstance(m,bs.HitMessage): self._handleHit(m)
        elif isinstance(m,bs.DieMessage): self._handleDie(m)
        elif isinstance(m,bs.OutOfBoundsMessage): self._handleOOB(m)
        elif isinstance(m,ArmMessage): self.arm()
        elif isinstance(m,WarnMessage): self._handleWarn(m)
        elif isinstance(m,bs.HealMessage): self.dissolve()
        elif isinstance(m,ReadyMessage): self.ready()
        elif isinstance(m,DeployMessage): self.deploy()
        else: bs.Actor.handleMessage(self,m)

class TNTSpawner(object):
    """
    category: Game Flow Classes

    Regenerates TNT at a given point in space every now and then.
    """
    def __init__(self,position,respawnTime=30000):
        """
        Instantiate with a given position and respawnTime (in milliseconds).
        """
        self._position = position
        self._tnt = None
        self._update()
        self._updateTimer = bs.Timer(1000,bs.WeakCall(self._update),repeat=True)
        self._respawnTime = int(respawnTime)
        self._waitTime = 0
        
    def _update(self):
        tntAlive = self._tnt is not None and self._tnt.node.exists()
        if not tntAlive:
            # respawn if its been long enough.. otherwise just increment our how-long-since-we-died value
            if self._tnt is None or self._waitTime >= self._respawnTime:
                self._tnt = Bomb(position=self._position,bombType='tnt')
                self._waitTime = 0
            else: 
                self._waitTime += 1000
                
t = Shape("Regular")
t.iconTexture = "bombNormalPreview"
t.shapeModel = "bomb"
t.explosionSounds = ["explosion01"]
t.explosionVolume = 0.0
t.reflection = 'sharper'
t.reflectionScale = 1.0

t = Shape("Bumpy")
t.iconTexture = "bombBumpyPreview"
t.shapeModel = "bombSticky"
t.explosionSounds = ["explosionBumpy01",
                     "explosionBumpy02"]
t.explosionVolume = 1.3
t.reflection = 'sharper'
t.reflectionScale = 1.0

t = Shape("Pinecone")
t.iconTexture = "bombPinePreview"
t.shapeModel = "bombPinecone"
t.explosionSounds = ["explosionPine01"]
t.explosionVolume = 1.3
t.reflection = 'soft'
t.reflectionScale = 0.8

t = Shape("Ring")
t.iconTexture = "bombRingPreview"
t.shapeModel = "bombRing"
t.explosionSounds = ["laser"]
t.explosionVolume = 0.8
t.reflection = 'sharper'
t.reflectionScale = 1.0

t = Shape("Canister")
t.iconTexture = "bombCanisterPreview"
t.shapeModel = "bombCanister"
t.explosionSounds = ["metalHit","metalHit2","metalHit3"]
t.explosionVolume = 3.0
t.reflection = 'sharper'
t.reflectionScale = 0.5

t = Shape("Unusual")
t.iconTexture = "bombSpinPreview"
t.shapeModel = "bombSpin"
t.explosionSounds = ["explosionSpin01"]
t.explosionVolume = 0.3
t.reflection = 'powerup'
t.reflectionScale = 1.0

t = Shape("Sci-Fi")
t.iconTexture = "bombScifiPreview"
t.shapeModel = "bombScifi"
t.explosionSounds = ["explosionScifi"]
t.explosionVolume = 1.5
t.reflection = 'powerup'
t.reflectionScale = 0.75

t = Shape("Prism")
t.iconTexture = "bombPrismPreview"
t.shapeModel = "bombPrism"
t.explosionSounds = ["bombPrism"]
t.explosionVolume = 0.8
t.reflection = 'powerup'
t.reflectionScale = 1.5

t = Shape("Drawing")
t.iconTexture = "bombDrawPreview"
t.shapeModel = "bombDrawing"
t.explosionSounds = ["explosionDraw01",
                     "explosionDraw02"]
t.explosionVolume = 1.5
t.reflection = 'char'

t.reflectionScale = 0.0

t = Shape("Cake")
t.iconTexture = "bombNormalPreview"
t.shapeModel = "dizzyCake"
t.explosionSounds = ["dizzyCakeExplode"]
t.explosionVolume = 1.0
t.reflection = 'powerup'

t.reflectionScale = 1.47