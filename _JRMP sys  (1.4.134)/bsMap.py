import bs
import bsUtils
import bsUI
import time
import datetime
import bsInteractive
import bsInternal
import bsServerData
import weakref
import random
import bsVector

_maps = {}

def preloadPreviewMedia():
    bs.getModel('levelSelectButtonOpaque')
    bs.getModel('levelSelectButtonTransparent')
    for m in _maps.values():
        mapTexName = m.getPreviewTextureName()
        if mapTexName is not None: bs.getTexture(mapTexName)
    
def registerMap(m):
    """ Register a map class with the game. """
    if _maps.has_key(m.name):
        raise Exception("map \"" + m.name + "\" already registered")
    _maps[m.name] = m

def getFilteredMapName(name):
    """ filters a map name to account for name changes, etc so old configs still work """
    # some legacy name fallbacks...
    if name == 'AlwaysLand' or name == 'Happy Land': name = u'Happy Thoughts'
    if name == 'Hockey Arena': name = u'Hockey Stadium'
    return name

def getMapDisplayString(name):
    return bs.Lstr(translate=('mapsNames',name))

def getMapsSupportingPlayType(playType):
    """
    category: Media Functions

    Return a list of bs.Map types supporting a specified play-type (a string).
    Maps supporting a given play-type must provide a particular set of
    features or lend themselves to a certain style of play.

    Play Types:
    
    'melee' - general fighting map - has 2+ 'spawn' pts, 1+ 'powerupSpawn' pts
    
    'battleRoyale' - big fighting map - has a lot of 'spawn' pts +1 'powerupSpawn' pts and +1 'raceMine' points.'

    'teamFlag' - for CTF, etc - has 2+ 'spawn' pts, 2+ 'flag' pts, and 1+ 'powerupSpawn' pts

    'keepAway'- has 2+ 'spawn' pts, 1+ 'flagDefault' pts, and 1+ 'powerupSpawn' pts

    'conquest' - has 2+ 'flag' pts, 2+ 'spawnByFlag' pts, and 1+ 'powerupSpawn' pts

    'kingOfTheHill' - has 2+ 'spawn' pts, 1+ 'flagDefault' pts, and 1+ 'powerupSpawn' pts

    'hockey' - has 2 'goal' pts, 2+ 'spawn' pts, 1+ 'flagDefault' pts, 1+ 'powerupSpawn' pts

    'football' - has 2 'goal' pts, 2+ 'spawn' pts, 1+ 'flagDefault' pts, 1+ 'powerupSpawn' pts
    
    'race' - has 2+ 'racePoint' pts
    """
    
    # we also want to limit results to maps we own..
    #unOwnedMaps = _getUnOwnedMaps()
    #maps = [m[0] for m in _maps.items() if playType in m[1].playTypes and (m[0] not in unOwnedMaps)]
    maps = [m[0] for m in _maps.items() if playType in m[1].playTypes]
    
    maps.sort()
    return maps

def _getUnOwnedMaps():
    import bsUI
    import bsInternal
    unOwnedMaps = set()
    if bs.getEnvironment()['subplatform'] != 'headless':
        for mapSection in bsUI._getStoreLayout()['maps']:
            for m in mapSection['items']:
                if not bsInternal._getPurchased(m):
                    mInfo = bsUI._getStoreItem(m)
                    unOwnedMaps.add(mInfo['mapType'].name)
    return unOwnedMaps
    

def getMapClass(name):
    """ return a map type given a name """
    name = getFilteredMapName(name)
    try: return _maps[name]
    except Exception: raise Exception("Map not found: '"+name+"'")
    
    
class Map(bs.Actor):
    """
    category: Game Flow Classes

    A collection of terrain nodes, metadata, and other
    functionality comprising a game map.
    """
    defs = None
    name = "Map"
    playTypes = []
    winter = False

    @classmethod
    def preload(cls,onDemand=False):
        """ Preload map media.
        This runs the class's onPreload function if need be to get it ready to run.
        Preloading can be fired for a soon-to-be-needed map to speed its creation.
        This is a classmethod since it is not run on map instances but rather on
        the class as a whole before instances are made"""

        # store whether we're preloaded in the current activity
        activity = bs.getActivity()
        if activity is None: raise Exception("not in an activity")
        try: preloads = activity._mapPreloadData
        except Exception: preloads = activity._mapPreloadData = {}

        if not cls.name in preloads:
            if onDemand:
                print 'WARNING: map '+cls.name+' was not preloaded; you can reduce hitches by preloading your map.'
            preloads[cls.name] = cls.onPreload()
        return preloads[cls.name]
            #preloads[cls.name] = {}

    @classmethod
    def getPreviewTextureName(cls):
        """
        Return the name of the preview texture for this map.
        """
        return None

    @classmethod
    def onPreload(cls):
        """
        Called when the map is being preloaded;
        it should load any media it requires to
        class attributes on itself.
        """
        pass

    @classmethod
    def getName(cls):
        """
        Return the unique name of this map, in English.
        """
        return cls.name

    @classmethod
    def getMusicType(cls):
        """
        Returns a particular music-type string that should be played on
        this map; or None if the default music should be used.
        """
        return None

    def __init__(self,vrOverlayCenterOffset=None):
        """
        Instantiate a map.
        """
        import bsInternal
        bs.Actor.__init__(self)
        
        self.preloadData = self.preload(onDemand=True)

        #bsUtils.resetGlobals()
        
        # set some defaults
        bsGlobals = bs.getSharedObject('globals')
        
        aoiBounds = self.getDefBoundBox("areaOfInterestBounds")
        if aoiBounds is None:
            print 'WARNING: no "aoiBounds" found for map:',self.getName()
            aoiBounds = (-1,-1,-1,1,1,1)
        bsGlobals.areaOfInterestBounds = aoiBounds
        
        mapBounds = self.getDefBoundBox("levelBounds")
        if mapBounds is None:
            print 'WARNING: no "levelBounds" found for map:',self.getName()
            mapBounds = (-30,-10,-30,30,100,30)
        bsInternal._setMapBounds(mapBounds)

        try: bsGlobals.shadowRange = [self.defs.points[v][1] for v in ['shadowLowerBottom','shadowLowerTop','shadowUpperBottom','shadowUpperTop']]
        except Exception: pass

        # in vr, set a fixed point in space for the overlay to show up at..
        # by default we use the bounds center but allow the map to override it
        center = ((aoiBounds[0]+aoiBounds[3])*0.5,
                  (aoiBounds[1]+aoiBounds[4])*0.5,
                  (aoiBounds[2]+aoiBounds[5])*0.5)
        
        if vrOverlayCenterOffset is not None:
            center = (center[0]+vrOverlayCenterOffset[0],
                      center[1]+vrOverlayCenterOffset[1],
                      center[2]+vrOverlayCenterOffset[2])
        
        #print "TEMP - center ",center
        bsGlobals.vrOverlayCenter = center
        bsGlobals.vrOverlayCenterEnabled = True
        
        self.spawnPoints = self.getDefPoints("spawn") or [(0,0,0,0,0,0)]
        self.ffaSpawnPoints = self.getDefPoints("ffaSpawn") or [(0,0,0,0,0,0)]
        self.spawnByFlagPoints = self.getDefPoints("spawnByFlag") or [(0,0,0,0,0,0)]
        self.flagPoints = self.getDefPoints("flag") or [(0,0,0)]
        self.flagPoints = [p[:3] for p in self.flagPoints] # just want points
        self.flagPointDefault = self.getDefPoint("flagDefault") or (0,1,0)
        self.runaroundPathPoints = self.getDefPoints("b") or [(0,0,0,0,0,0)]
        self.powerupSpawnPoints = self.getDefPoints("powerupSpawn") or [(0,0,0)]
        self.powerupSpawnPoints = [p[:3] for p in self.powerupSpawnPoints] # just want points
        self.tntPoints = self.getDefPoints("tnt") or []
        self.tntPoints = [p[:3] for p in self.tntPoints] # just want points
        self.platformPoints = self.getDefPoints("platform") or []
        self.platformPoints = [p[:3] for p in self.platformPoints] # just want points
        self.bumperPoints = self.getDefPoints("bumper") or []
        self.bumperPoints = [p[:3] for p in self.bumperPoints] # just want points
        self.isHockey = False
        self.isFlying = False                       
        #def path():
               #p = bs.newNode('prop', attrs={'position':(-5.750,4.3515026107,2.0),'velocity':(2.0,1.0,0),'sticky':False,'body':'landMine','model':bs.getModel('landMine'),'colorTexture':bs.getTexture('logo'),'bodyScale':4.0,'reflection': 'powerup','density':9999999999999999,'reflectionScale': [1.0],'modelScale':4.0,'gravityScale':0,'shadowSize':0.0,'materials':[bs.getSharedObject('objectMaterial'),bs.getSharedObject('footingMaterial')]})
               #bsUtils.animateArray(p,"position",3,{0:(1.830634, 4.830635, 3.830636),10000:(4.8306378, 4.83063588, -6.830639),20000:(-5.422572086, 4.228850685, 2.803988636),25000:(-6.859406739, 4.429165244, -6.588618549),30000:(-6.859406739, 4.429165244, -6.588618549),35000:(3.148493267, 4.429165244, -6.588618549),40000:(1.830377363, 4.228850685, 2.803988636),45000:(-5.422572086, 4.228850685, 2.803988636),50000:(-5.422572086, 4.228850685, 2.803988636),55000:(1.830377363, 4.228850685, 2.803988636),60000:(3.148493267, 4.429165244, -6.588618549),70000:(1.830377363, 4.228850685, 2.803988636),75000:(3.148493267, 4.429165244, -6.588618549),80000:(-5.422572086, 4.228850685, 2.803988636),90000:(-6.859406739, 4.429165244, -6.588618549),95000:(-6.859406739, 4.429165244, -6.588618549)},loop = True)              
        #bs.gameTimer(100,bs.Call(path))
        self._nextFFAStartIndex = 0
        global timeOfDay
        timeNow = bs.checkTime(useInternet=False)
        if timeNow['month'] == 12 or timeNow['month'] == 1 or timeNow['month'] == 2:                
           self._emit = bs.Timer(15, bs.WeakCall(self.emit), repeat=True)

    def emit(self):
        pos = (-15+(random.random()*30),
               15,
               -15+(random.random()*30))

        vel1 = (-5.0 + random.random()*30.0) \
            * (-1.0 if pos[0] > 0 else 1.0)

        vel = (vel1,
               -50.0,
               random.uniform(-20, 20))
        
        bs.emitBGDynamics(
            position=pos,
            velocity=vel,
            count=5+random.randint(0,15),
            scale=0.4+random.random(), #0.4
            spread=0,
            chunkType='spark')
        
        if self.winter:
            winterSound = bs.getSound('winterWind')
            bs.newNode('sound',owner=self,attrs={'sound':winterSound,'volume':1.0})

    def _isPointNearEdge(self,p,running=False):
        "For bot purposes.."
        return False

    def getDefBoundBox(self,name):
        """Returns a 6 member bounds tuple or None if it is not defined."""
        try:
            b = self.defs.boxes[name]
            return (b[0]-b[6]/2.0,b[1]-b[7]/2.0,b[2]-b[8]/2.0,
                    b[0]+b[6]/2.0,b[1]+b[7]/2.0,b[2]+b[8]/2.0);
        except Exception:
            return None
        
    def getDefPoint(self,name):
        """Returns a single defined point or a default value in its absence."""
        try:
            return self.defs.points[name]
        except Exception:
            return None

    def getDefPoints(self,name):
        """
        Returns a list of points - as many sequential ones are defined
        (flag1, flag2, flag3), etc.
        """
        if self.defs and self.defs.points.has_key(name+"1"):
            pointList = []
            i = 1
            while self.defs.points.has_key(name+str(i)):
                p = self.defs.points[name+str(i)]
                if len(p) == 6:
                    pointList.append(p)
                else:
                    if len(p) != 3: raise Exception("invalid point")
                    pointList.append(p+(0,0,0))
                i += 1
            return pointList
        else:
            return None
        
    def getStartPosition(self,teamIndex):
        """
        Returns a random starting position in the map for the given team index.
        """
        pt = self.spawnPoints[teamIndex%len(self.spawnPoints)]
        xRange = (-0.5,0.5) if pt[3] == 0 else (-pt[3],pt[3])
        zRange = (-0.5,0.5) if pt[5] == 0 else (-pt[5],pt[5])
        pt = (pt[0]+random.uniform(*xRange),pt[1],pt[2]+random.uniform(*zRange))
        return pt

    def getFFAStartPosition(self,players):
        """
        Returns a random starting position in one of the FFA spawn areas.
        If a list of bs.Players is provided; the returned points will be
        as far from these players as possible.
        """

        # get positions for existing players
        playerPts = []
        for player in players:
            try:
                if player.actor is not None and player.actor.isAlive():
                    pt = bsVector.Vector(*player.actor.node.position)
                    playerPts.append(pt)
            except Exception,e:
                print 'EXC in getFFAStartPosition:',e


        def _getPt():
            pt = self.ffaSpawnPoints[self._nextFFAStartIndex]
            self._nextFFAStartIndex = (self._nextFFAStartIndex+1)%len(self.ffaSpawnPoints)
            xRange = (-0.5,0.5) if pt[3] == 0 else (-pt[3],pt[3])
            zRange = (-0.5,0.5) if pt[5] == 0 else (-pt[5],pt[5])
            pt = (pt[0]+random.uniform(*xRange),pt[1],pt[2]+random.uniform(*zRange))
            return pt

        if len(playerPts) == 0:
            return _getPt()
        else:
            # lets calc several start points and then pick whichever is farthest from all existing players
            farthestPtDist = -1.0
            farthestPt = None
            for i in range(10):
                testPt = bsVector.Vector(*_getPt())
                closestPlayerDist = 9999.0
                closestPlayerPt = None
                for pp in playerPts:
                    dist = (pp-testPt).length()
                    if dist < closestPlayerDist:
                        closestPlayerDist = dist
                        closestPlayerPt = pp
                if closestPlayerDist > farthestPtDist:
                    farthestPtDist = closestPlayerDist
                    farthestPt = testPt
            return tuple(farthestPt.data)

    def getFlagPosition(self,teamIndex):
        """
        Return a flag position on the map for the given team index.
        Pass None to get the default flag point.
        (used for things such as king-of-the-hill)
        """
        if teamIndex is None:
            return self.flagPointDefault[:3]
        else:
            return self.flagPoints[teamIndex%len(self.flagPoints)][:3]

    def handleMessage(self,m):
        if isinstance(m,bs.DieMessage): self.node.delete()
        else: bs.Actor.handleMessage(self,m)



######### now lets go ahead and register some maps #########


class HockeyStadium(Map):
    import hockeyStadiumDefs as defs
    name = "Hockey Stadium"
    discordName = 'hockey_stadium'

    playTypes = ['melee','hockey','teamFlag','keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'hockeyStadiumPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['models'] = (bs.getModel('hockeyStadiumOuter'),
                                       bs.getModel('hockeyStadiumInner'),
                                       bs.getModel('hockeyStadiumStands'))
        data['vrFillModel'] = bs.getModel('footballStadiumVRFill')
        data['collideModel'] = bs.getCollideModel('hockeyStadiumCollide')
        data['tex'] = bs.getTexture('hockeyStadium')
        data['standsTex'] = bs.getTexture('footballStadium')

        m = bs.Material()
        m.addActions(actions=('modifyPartCollision','friction',0.01))
        data['iceMaterial'] = m
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode("terrain",
                               delegate=self,
                               attrs={'model':self.preloadData['models'][0],
                                      'collideModel':self.preloadData['collideModel'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial'),self.preloadData['iceMaterial']]})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'vrOnly':True,
                          'lighting':False,
                          'background':True,
                          'colorTexture':self.preloadData['standsTex']})
        self.floor = bs.newNode("terrain",
                                attrs={"model":self.preloadData['models'][1],
                                       "colorTexture":self.preloadData['tex'],
                                       "opacity":0.92,
                                       "opacityInLowOrMediumQuality":1.0,
                                       "materials":[bs.getSharedObject('footingMaterial'),self.preloadData['iceMaterial']]})
        self.stands = bs.newNode("terrain",
                                 attrs={"model":self.preloadData['models'][2],
                                        "visibleInReflections":False,
                                        "colorTexture":self.preloadData['standsTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.floorReflection = True
        bsGlobals.debrisFriction = 0.3
        bsGlobals.debrisKillHeight = -0.3

        bsGlobals.tint = (1.2,1.3,1.33)
        bsGlobals.ambientColor = (1.15,1.25,1.6)
        bsGlobals.vignetteOuter = (0.66,0.67,0.73)
        bsGlobals.vignetteInner = (0.93,0.93,0.95)
        bsGlobals.vrCameraOffset = (0,-3.8,-1.1)
        bsGlobals.vrNearClip = 0.5

        self.isHockey = True

registerMap(HockeyStadium)


class FootballStadium(Map):
    import footballStadiumDefs as defs
    name = "Football Stadium"
    discordName = 'football_stadium'

    playTypes = ['melee','football','teamFlag','keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'footballStadiumPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel("footballStadium")
        data['vrFillModel'] = bs.getModel('footballStadiumVRFill')
        data['collideModel'] = bs.getCollideModel("footballStadiumCollide")
        data['tex'] = bs.getTexture("footballStadium")
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'model':self.preloadData['model'],
                                      'collideModel':self.preloadData['collideModel'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['tex']})
        g = bs.getSharedObject('globals')
        g.tint = (1.3,1.2,1.0)
        g.ambientColor = (1.3,1.2,1.0)
        g.vignetteOuter = (0.57,0.57,0.57)
        g.vignetteInner = (0.9,0.9,0.9)
        g.vrCameraOffset = (0,-4.2,-1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self,p,running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(FootballStadium)

class BasketballStadium(Map):
    import basketballStadiumLevelDefs as defs
    name = "Basketball Stadium"
    discordName = 'basketball_stadium'

    playTypes = ['melee','basketball','keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'basketballStadiumPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['modelFloor'] = bs.getModel("basketballFloor")
        data['modelWalls'] = bs.getModel("basketballWall")
        data['modelGoalies'] = bs.getModel("basketballGoalie")
        data['vrFillModel'] = bs.getModel('footballStadiumVRFill')
        data['collideModel'] = bs.getCollideModel("footballStadiumCollide")
        data['collideModelGoalies'] = bs.getCollideModel("basketballGoalieCollide")
        data['goalieTex'] = bs.getTexture("basketballGoalie")
        data['wallTex'] = bs.getTexture("footballStadium")
        data['floorTex'] = bs.getTexture("basketballCourt")
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'model':self.preloadData['modelFloor'],
                                      'collideModel':self.preloadData['collideModel'],
                                      'colorTexture':self.preloadData['floorTex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
                                      
        self.goalies = bs.newNode('terrain',
                               delegate=self,
                               attrs={'model':self.preloadData['modelGoalies'],
                                      'collideModel':self.preloadData['collideModelGoalies'],
                                      'colorTexture':self.preloadData['goalieTex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
                                      
        self.walls = bs.newNode('terrain',
                               delegate=self,
                               attrs={'model':self.preloadData['modelWalls'],
                                      'colorTexture':self.preloadData['wallTex']})
                                      
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['wallTex']})
        g = bs.getSharedObject('globals')
        g.tint = (1.3,1.2,1.0)
        g.ambientColor = (1.3,1.2,1.0)
        g.vignetteOuter = (0.57,0.57,0.57)
        g.vignetteInner = (0.9,0.9,0.9)
        g.vrCameraOffset = (0,-4.2,-1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self,p,running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(BasketballStadium)


class BridgitMap(Map):
    import bridgitLevelDefs as defs
    name = "Bridgit"
    discordName = 'bridgit'
    playTypes = ["melee","teamFlag",'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'bridgitPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['modelTop'] = bs.getModel("bridgitLevelTop")
        data['modelBottom'] = bs.getModel("bridgitLevelBottom")
        data['modelBG'] = bs.getModel("natureBackground")
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel("bridgitLevelCollide")
        data['tex'] = bs.getTexture("bridgitLevelColor")
        data['modelBGTex'] = bs.getTexture("natureBackgroundColor")
        data['collideBG'] = bs.getCollideModel("natureBackgroundCollide")

        data['railingCollideModel'] = bs.getCollideModel("bridgitLevelRailingCollide")
    
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision','friction',10.0))
        return data

    def __init__(self):
        Map.__init__(self)
        
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['modelTop'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['modelBottom'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['modelBG'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['modelBGTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['bgVRFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['modelBGTex']})
        self.railing = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['railingCollideModel'],
                                         'materials':[bs.getSharedObject('railingMaterial')],
                                         'bumper':True})
        self.bgCollide = bs.newNode('terrain',
                                    attrs={'collideModel':self.preloadData['collideBG'],
                                           'materials':[bs.getSharedObject('footingMaterial'),
                                                        self.preloadData['bgMaterial'],
                                                        bs.getSharedObject('deathMaterial')]})
                                                        
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1,1.2,1.3)
        bsGlobals.ambientColor = (1.1,1.2,1.3)
        bsGlobals.vignetteOuter = (0.65,0.6,0.55)
        bsGlobals.vignetteInner = (0.9,0.9,0.93)

registerMap(BridgitMap)


class BigGMap(Map):
    import bigGDefs as defs
    name = 'Big G'
    discordName = 'big_g'
    playTypes = ['race','melee','keepAway','teamFlag','kingOfTheHill','conquest','battleRoyale']

    @classmethod
    def getPreviewTextureName(cls):
        return 'bigGPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['modelTop'] = bs.getModel('bigG')
        data['modelBottom'] = bs.getModel('bigGBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('bigGCollide')
        data['tex'] = bs.getTexture('bigG')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['bumperCollideModel'] = bs.getCollideModel('bigGBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision','friction',10.0))
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'color':(0.7,0.7,0.7),
                                      'model':self.preloadData['modelTop'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['modelBottom'],
                                        'color':(0.7,0.7,0.7),
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['modelBG'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['modelBGTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['bgVRFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['modelBGTex']})
        self.railing = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['bumperCollideModel'],
                                         'materials':[bs.getSharedObject('railingMaterial')],
                                         'bumper':True})
        self.bgCollide = bs.newNode('terrain',
                                    attrs={'collideModel':self.preloadData['collideBG'],
                                           'materials':[bs.getSharedObject('footingMaterial'),self.preloadData['bgMaterial'],bs.getSharedObject('deathMaterial')]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1,1.2,1.3)
        bsGlobals.ambientColor = (1.1,1.2,1.3)
        bsGlobals.vignetteOuter = (0.65,0.6,0.55)
        bsGlobals.vignetteInner = (0.9,0.9,0.93)

registerMap(BigGMap)


class RoundaboutMap(Map):
    import roundaboutLevelDefs as defs
    name = 'Roundabout'
    discordName = 'roundabout'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'roundaboutPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('roundaboutLevel')
        data['modelBottom'] = bs.getModel('roundaboutLevelBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('roundaboutLevelCollide')
        data['tex'] = bs.getTexture('roundaboutLevelColor')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['railingCollideModel'] = bs.getCollideModel('roundaboutLevelBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision','friction',10.0))
        return data
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,-1,1))
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['modelBottom'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['modelBG'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['modelBGTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['bgVRFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['modelBGTex']})
        self.bgCollide = bs.newNode('terrain',
                                    attrs={'collideModel':self.preloadData['collideBG'],
                                           'materials':[bs.getSharedObject('footingMaterial'),self.preloadData['bgMaterial'],bs.getSharedObject('deathMaterial')]})
        self.railing = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['railingCollideModel'],
                                         'materials':[bs.getSharedObject('railingMaterial')],
                                         'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.0,1.05,1.1)
        bsGlobals.ambientColor = (1.0,1.05,1.1)
        bsGlobals.shadowOrtho = True
        bsGlobals.vignetteOuter = (0.63,0.65,0.7)
        bsGlobals.vignetteInner = (0.97,0.95,0.93)

registerMap(RoundaboutMap)


class MonkeyFaceMap(Map):
    import monkeyFaceLevelDefs as defs
    name = 'Monkey Face'
    discordName = 'monkey_face'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'monkeyFacePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('monkeyFaceLevel')
        data['bottomModel'] = bs.getModel('monkeyFaceLevelBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('monkeyFaceLevelCollide')
        data['tex'] = bs.getTexture('monkeyFaceLevelColor')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['railingCollideModel'] = bs.getCollideModel('monkeyFaceLevelBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision','friction',10.0))
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['bottomModel'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['modelBG'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['modelBGTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['bgVRFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['modelBGTex']})
        self.bgCollide = bs.newNode('terrain',
                                    attrs={'collideModel':self.preloadData['collideBG'],
                                           'materials':[bs.getSharedObject('footingMaterial'),self.preloadData['bgMaterial'],bs.getSharedObject('deathMaterial')]})
        self.railing = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['railingCollideModel'],
                                         'materials':[bs.getSharedObject('railingMaterial')],
                                         'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1,1.2,1.2)
        bsGlobals.ambientColor = (1.2,1.3,1.3)
        bsGlobals.vignetteOuter = (0.60,0.62,0.66)
        bsGlobals.vignetteInner = (0.97,0.95,0.93)
        bsGlobals.vrCameraOffset = (-1.4,0,0)

registerMap(MonkeyFaceMap)


class ZigZagMap(Map):
    import zigZagLevelDefs as defs
    name = 'Zigzag'
    discordName = 'zigzag'
    playTypes = ['melee','keepAway','teamFlag','conquest','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'zigzagPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('zigZagLevel')
        data['modelBottom'] = bs.getModel('zigZagLevelBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('zigZagLevelCollide')
        data['tex'] = bs.getTexture('zigZagLevelColor')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['railingCollideModel'] = bs.getCollideModel('zigZagLevelBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision','friction',10.0))
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['modelBG'],
                                     'lighting':False,
                                     'colorTexture':self.preloadData['modelBGTex']})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['modelBottom'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['bgVRFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['modelBGTex']})
        self.bgCollide = bs.newNode('terrain',
                                    attrs={'collideModel':self.preloadData['collideBG'],
                                           'materials':[bs.getSharedObject('footingMaterial'),self.preloadData['bgMaterial'],bs.getSharedObject('deathMaterial')]})
        self.railing = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['railingCollideModel'],
                                         'materials':[bs.getSharedObject('railingMaterial')],
                                         'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.0,1.15,1.15)
        bsGlobals.ambientColor = (1.0,1.15,1.15)
        bsGlobals.vignetteOuter = (0.57,0.59,0.63)
        bsGlobals.vignetteInner = (0.97,0.95,0.93)
        bsGlobals.vrCameraOffset = (-1.5,0,0)

registerMap(ZigZagMap)


class ThePadMap(Map):
    import thePadLevelDefs as defs
    name = 'The Pad'
    discordName = 'the_pad'
    playTypes = ['melee','keepAway','teamFlag','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'thePadPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('thePadLevel')
        data['bottomModel'] = bs.getModel('thePadLevelBottom')
        data['collideModel'] = bs.getCollideModel('thePadLevelCollide')
        data['tex'] = bs.getTexture('thePadLevelColor')
        data['trees'] = bs.getModel('trees')
        data['treesColor'] = bs.getTexture('treesColor')
        data['bgTex'] = bs.getTexture('menuBG')
        data['bgModel'] = bs.getModel('thePadBG') # fixme should chop this into vr/non-vr sections
        data['railingCollideModel'] = bs.getCollideModel('thePadLevelBumper')
        data['vrFillMoundModel'] = bs.getModel('thePadVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['bottomModel'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        self.trees = bs.newNode('terrain',
                                             attrs={'model':self.preloadData['trees'],
                                                    'lighting':False,
                                                    'reflection':'char',
                                                    'reflectionScale':[0.1],
                                                    'colorTexture':self.preloadData['treesColor']})
        self.railing = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['railingCollideModel'],
                                         'materials':[bs.getSharedObject('railingMaterial')],
                                         'bumper':True})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.56,0.55,0.47),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1,1.1,1.0)
        bsGlobals.ambientColor = (1.1,1.1,1.0)
        bsGlobals.vignetteOuter = (0.7,0.65,0.75)
        bsGlobals.vignetteInner = (0.95,0.95,0.93)

registerMap(ThePadMap)

class BouncyPadMap(Map):
    import bouncyPadLevelDefs as defs
    name = 'Bouncy Pad'
    discordName = 'the_pad'
    playTypes = ['melee','keepAway','teamFlag','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'thePadPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('thePadLevel')
        data['bottomModel'] = bs.getModel('thePadLevelBottom')
        data['collideModel'] = bs.getCollideModel('thePadLevelCollide')
        data['tex'] = bs.getTexture('thePadLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        data['bgModel'] = bs.getModel('thePadBG') # fixme should chop this into vr/non-vr sections
        data['railingCollideModel'] = bs.getCollideModel('thePadLevelBumper')
        data['vrFillMoundModel'] = bs.getModel('thePadVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['bottomModel'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        self.railing = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['railingCollideModel'],
                                         'materials':[bs.getSharedObject('railingMaterial')],
                                         'bumper':True})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.56,0.55,0.47),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.0,1.3,1.0)
        bsGlobals.ambientColor = (1.1,1.1,1.0)
        bsGlobals.vignetteOuter = (0.7,0.65,0.75)
        bsGlobals.vignetteInner = (0.95,0.95,0.93)

registerMap(BouncyPadMap)

class DoomShroomMap(Map):
    import doomShroomLevelDefsCOOP as defs
    name = 'Doom Shroom Large'
    discordName = 'doom_shroom'
    playTypes = ['melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'doomShroomPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('doomShroomLevelCOOP')
        data['collideModel'] = bs.getCollideModel('doomShroomLevelCollideCOOP')
        data['tex'] = bs.getTexture('doomShroomLevelColor')
        data['bgTex'] = bs.getTexture('doomShroomBGColor')
        data['bgModel'] = bs.getModel('doomShroomBG')
        data['vrFillModel'] = bs.getModel('doomShroomVRFill')
        data['stemModel'] = bs.getModel('doomShroomStemCOOP')
        data['collideBG'] = bs.getCollideModel('doomShroomStemCollideCOOP')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['bgTex']})
        self.stem = bs.newNode('terrain',
                               attrs={'model':self.preloadData['stemModel'],
                                      'lighting':False,
                                      'colorTexture':self.preloadData['tex']})
        self.bgCollide = bs.newNode('terrain',
                                    attrs={'collideModel':self.preloadData['collideBG'],
                                           'materials':[bs.getSharedObject('footingMaterial'),bs.getSharedObject('deathMaterial')]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.82,1.10,1.15)
        bsGlobals.ambientColor = (0.9,1.3,1.1)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (0.76,0.76,0.76)
        bsGlobals.vignetteInner = (0.95,0.95,0.99)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(DoomShroomMap)

class SnowballPitMap(Map):
    import snowballPitLevelDefs as defs
    name = 'Snowball Pit'
    discordName = 'snow_ball_pit'
    playTypes = ['melee']
    winter = True

    @classmethod
    def getPreviewTextureName(cls):
        return 'snowballPitPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('snowballPit')
        data['collideModel'] = bs.getCollideModel('snowballPit')
        data['playerWallCollideModel'] = bs.getCollideModel('snowballPitPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision','friction',0.0)))
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial',bs.getSharedObject('playerMaterial')),
            actions=(('modifyPartCollision','collide',False)))
        data['tex'] = bs.getTexture('snowballPit')
        data['bgTex'] = bs.getTexture('black')
        data['bgModel'] = bs.getModel('thePadBG')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        self.playerWall = bs.newNode('terrain',
                                     attrs={'collideModel':self.preloadData['playerWallCollideModel'],
                                            'affectBGDynamics':False,
                                            'materials':[self.preloadData['playerWallMaterial']]})

        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.82,1.10,1.15)
        bsGlobals.ambientColor = (0.9,1.3,1.1)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (0.36,0.36,0.36)
        bsGlobals.vignetteInner = (0.95,0.95,0.99)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(SnowballPitMap)

class DoomShroomMultiMap(Map):
    import doomShroomLevelDefs as defs
    name = 'Doom Shroom'
    discordName = 'doom_shroom'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'doomShroomPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('doomShroomLevel')
        data['collideModel'] = bs.getCollideModel('doomShroomLevelCollide')
        data['tex'] = bs.getTexture('doomShroomLevelColor')
        data['bgTex'] = bs.getTexture('doomShroomBGColor')
        data['bgModel'] = bs.getModel('doomShroomBG')
        data['vrFillModel'] = bs.getModel('doomShroomVRFill')
        data['stemModel'] = bs.getModel('doomShroomStem')
        data['collideBG'] = bs.getCollideModel('doomShroomStemCollide')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['bgTex']})
        self.stem = bs.newNode('terrain',
                               attrs={'model':self.preloadData['stemModel'],
                                      'lighting':False,
                                      'colorTexture':self.preloadData['tex']})
        self.bgCollide = bs.newNode('terrain',
                                    attrs={'collideModel':self.preloadData['collideBG'],
                                           'materials':[bs.getSharedObject('footingMaterial'),bs.getSharedObject('deathMaterial')]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.82,1.10,1.15)
        bsGlobals.ambientColor = (0.9,1.3,1.1)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (0.76,0.76,0.76)
        bsGlobals.vignetteInner = (0.95,0.95,0.99)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(DoomShroomMultiMap)

#class InnerCastleMap(Map):
    #import innerCastleLevelDefs as defs
    #name = 'Inner Castle'
    #discordName = 'inner_castle'
    #playTypes = ['melee','keepAway','teamFlag']

    #@classmethod
    #def getPreviewTextureName(cls):
        #return 'blank'

    #@classmethod
    #def onPreload(cls):
        #data = {}
        #data['model'] = bs.getModel('innerCastleLevel')
        #data['collideModel'] = bs.getCollideModel('innerCastleLevelCollide')
        #data['tex'] = bs.getTexture('stoneishFortLevelColor')
        #return data
    
    #def __init__(self):
        #Map.__init__(self)
        #self.node = bs.newNode('terrain',
                               #delegate=self,
                               #attrs={'collideModel':self.preloadData['collideModel'],
                                      #'model':self.preloadData['model'],
                                      #'colorTexture':self.preloadData['tex'],
                                      #'materials':[bs.getSharedObject('footingMaterial')]})
        #bsGlobals = bs.getSharedObject('globals')
        #bsGlobals.tint = (0.82,1.10,1.15)
        #bsGlobals.ambientColor = (0.9,1.3,1.1)
        #bsGlobals.shadowOrtho = False
        #bsGlobals.vignetteOuter = (0.76,0.76,0.76)
        #bsGlobals.vignetteInner = (0.95,0.95,0.99)

    #def _isPointNearEdge(self,p,running=False):
        #x = p.x()
        #z = p.z()
        #xAdj = x*0.125
        #zAdj = (z+3.7)*0.2
        #if running:
            #xAdj *= 1.4
            #zAdj *= 1.4
        #return (xAdj*xAdj+zAdj*zAdj > 1.0)

#registerMap(InnerCastleMap)

class LakeFrigidMap(Map):
    import lakeFrigidDefs as defs
    name = 'Lake Frigid'
    discordName = 'lake_frigid'
    playTypes = ['melee','keepAway','teamFlag','race']
    winter = True

    @classmethod
    def getPreviewTextureName(cls):
        return 'lakeFrigidPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('lakeFrigid')
        data['modelTop'] = bs.getModel('lakeFrigidTop')
        data['modelReflections'] = bs.getModel('lakeFrigidReflections')
        data['collideModel'] = bs.getCollideModel('lakeFrigidCollide')
        data['tex'] = bs.getTexture('lakeFrigid')
        data['texReflections'] = bs.getTexture('lakeFrigidReflections')
        #data['bgTex'] = bs.getTexture('lakeFrigidBGColor')
        #data['bgModel'] = bs.getModel('lakeFrigidBG')
        data['vrFillModel'] = bs.getModel('lakeFrigidVRFill')
        m = bs.Material()
        m.addActions(actions=('modifyPartCollision','friction',0.01))
        data['iceMaterial'] = m
        
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      # 'reflection':'soft',
                                      # 'reflectionScale':[0.65],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial'),self.preloadData['iceMaterial']]})
        # self.foo = bs.newNode('terrain',
        #                       attrs={'model':self.preloadData['bgModel'],
        #                              'lighting':False,
        #                              'background':True,
        #                              'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['modelTop'],
                          'lighting':False,
                          'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['modelReflections'],
                          'lighting':False,
                          'overlay':True,
                          'opacity':0.15,
                          'colorTexture':self.preloadData['texReflections']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['tex']})
        # self.stem = bs.newNode('terrain',
        #                        attrs={'model':self.preloadData['stemModel'],
        #                               'lighting':False,
        #                               'colorTexture':self.preloadData['tex']})
        # self.bgCollide = bs.newNode('terrain',
        #                             attrs={'collideModel':self.preloadData['collideBG'],
        #                                    'materials':[bs.getSharedObject('footingMaterial'),bs.getSharedObject('deathMaterial')]})
        g = bs.getSharedObject('globals')
        g.tint = (1,1,1)
        g.ambientColor = (1,1,1)
        g.shadowOrtho = True
        g.vignetteOuter = (0.86,0.86,0.86)
        g.vignetteInner = (0.95,0.95,0.99)

        g.vrNearClip = 0.5
        
        self.isHockey = True
        
    # def _isPointNearEdge(self,p,running=False):
    #     x = p.x()
    #     z = p.z()
    #     xAdj = x*0.125
    #     zAdj = (z+3.7)*0.2
    #     if running:
    #         xAdj *= 1.4
    #         zAdj *= 1.4
    #     return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(LakeFrigidMap)

class TipTopMap(Map):
    import tipTopLevelDefs as defs
    name = 'Tip Top'
    discordName = 'tip_top'
    playTypes = ['melee','keepAway','teamFlag','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'tipTopPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('tipTopLevel')
        data['bottomModel'] = bs.getModel('tipTopLevelBottom')
        data['collideModel'] = bs.getCollideModel('tipTopLevelCollide')
        data['tex'] = bs.getTexture('tipTopLevelColor')
        data['bgTex'] = bs.getTexture('tipTopBGColor')
        data['bgModel'] = bs.getModel('tipTopBG')
        data['railingCollideModel'] = bs.getCollideModel('tipTopLevelBumper')
        return data
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,-0.2,2.5))
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'color':(0.7,0.7,0.7),
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['bottomModel'],
                                        'lighting':False,
                                        'color':(0.7,0.7,0.7),
                                        'colorTexture':self.preloadData['tex']})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'color':(0.4,0.4,0.4),
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.railing = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['railingCollideModel'],
                                         'materials':[bs.getSharedObject('railingMaterial')],
                                         'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.8,0.9,1.3)
        bsGlobals.ambientColor = (0.8,0.9,1.3)
        bsGlobals.vignetteOuter = (0.79,0.79,0.69)
        bsGlobals.vignetteInner = (0.97,0.97,0.99)

registerMap(TipTopMap)


class CragCastleMap(Map):
    import cragCastleDefs as defs
    name = 'Crag Castle'
    discordName = 'crag_castle'
    playTypes = ['melee','keepAway','teamFlag','conquest']

    @classmethod
    def getPreviewTextureName(cls):
        return 'cragCastlePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('cragCastleLevel')
        data['bottomModel'] = bs.getModel('cragCastleLevelBottom')
        data['collideModel'] = bs.getCollideModel('cragCastleLevelCollide')
        data['tex'] = bs.getTexture('cragCastleLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        data['bgModel'] = bs.getModel('thePadBG') # fixme should chop this into vr/non-vr sections
        data['railingCollideModel'] = bs.getCollideModel('cragCastleLevelBumper')
        data['vrFillMoundModel'] = bs.getModel('cragCastleVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['bottomModel'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.railing = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['railingCollideModel'],
                                         'materials':[bs.getSharedObject('railingMaterial')],
                                         'bumper':True})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.2,0.25,0.2),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.shadowOrtho = True
        bsGlobals.shadowOffset = (0,0,-5.0)
        bsGlobals.tint = (1.15,1.05,0.75)
        bsGlobals.ambientColor = (1.15,1.05,0.75)
        bsGlobals.vignetteOuter = (0.6,0.65,0.6)
        bsGlobals.vignetteInner = (0.95,0.95,0.95)
        bsGlobals.vrNearClip = 1.0

registerMap(CragCastleMap)



class TowerDMap(Map):
    import towerDLevelDefs as defs
    name = 'Tower D'
    discordName = 'tower_d'
    playTypes = ['melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'towerDPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('towerDLevel')
        data['modelBottom'] = bs.getModel('towerDLevelBottom')
        data['collideModel'] = bs.getCollideModel('towerDLevelCollide')
        data['tex'] = bs.getTexture('towerDLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        data['bgModel'] = bs.getModel('thePadBG') # fixme: divide this into vr and non-vr parts
        data['playerWallCollideModel'] = bs.getCollideModel('towerDPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision','friction',0.0)))
        # anything that needs to hit the wall can apply this material
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial',data['collideWithWallMaterial']),
            actions=(('modifyPartCollision','collide',False)))
        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,1,1))
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.nodeBottom = bs.newNode('terrain',
                                     delegate=self,
                                     attrs={'model':self.preloadData['modelBottom'],
                                            'lighting':False,
                                            'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.53,0.57,0.5),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.playerWall = bs.newNode('terrain',
                                     attrs={'collideModel':self.preloadData['playerWallCollideModel'],
                                            'affectBGDynamics':False,
                                            'materials':[self.preloadData['playerWallMaterial']]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.15,1.11,1.03)
        bsGlobals.ambientColor = (1.2,1.1,1.0)
        bsGlobals.vignetteOuter = (0.7,0.73,0.7)
        bsGlobals.vignetteInner = (0.95,0.95,0.95)

    def _isPointNearEdge(self,p,running=False):
        # see if we're within edgeBox
        boxes = self.defs.boxes
        boxPosition = boxes['edgeBox'][0:3]
        boxScale = boxes['edgeBox'][6:9]
        boxPosition2 = boxes['edgeBox2'][0:3]
        boxScale2 = boxes['edgeBox2'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        x2 = (p.x() - boxPosition2[0])/boxScale2[0]
        z2 = (p.z() - boxPosition2[2])/boxScale2[2]
        # if we're outside of *both* boxes we're near the edge
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5) and (x2 < -0.5 or x2 > 0.5 or z2 < -0.5 or z2 > 0.5)

registerMap(TowerDMap)


class AlwaysLandMap(Map):
    import alwaysLandLevelDefs as defs
    name = 'Happy Thoughts'
    discordName = 'happy_thoughts'
    playTypes = ['melee','keepAway','teamFlag','conquest','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'alwaysLandPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('alwaysLandLevel')
        data['bottomModel'] = bs.getModel('alwaysLandLevelBottom')
        data['bgModel'] = bs.getModel('alwaysLandBG')
        data['collideModel'] = bs.getCollideModel('alwaysLandLevelCollide')
        data['tex'] = bs.getTexture('alwaysLandLevelColor')
        data['bgTex'] = bs.getTexture('alwaysLandBGColor')
        data['vrFillMoundModel'] = bs.getModel('alwaysLandVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    @classmethod
    def getMusicType(cls):
        return 'Flying'
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,-3.7,2.5))
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['bottomModel'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.2,0.25,0.2),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        g = bs.getSharedObject('globals')
        g.happyThoughtsMode = True
        g.shadowOffset = (0.0,8.0,5.0)
        g.tint = (1.3,1.23,1.0)
        g.ambientColor = (1.3,1.23,1.0)
        g.vignetteOuter = (0.64,0.59,0.69)
        g.vignetteInner = (0.95,0.95,0.93)
        g.vrNearClip = 1.0
        self.isFlying = True

        # throw out some tips on flying
        t = bs.newNode('text',
                       attrs={'text':bs.Lstr(resource='pressJumpToFlyText'),
                              'scale':1.2,
                              'maxWidth':800,
                              'position':(0,200),
                              'shadow':0.5,
                              'flatness':0.5,
                              'hAlign':'center',
                              'vAttach':'bottom'})
        c = bs.newNode('combine',owner=t,attrs={'size':4,'input0':0.3,'input1':0.9,'input2':0.0})
        bsUtils.animate(c,'input3',{3000:0,4000:1,9000:1,10000:0})
        c.connectAttr('output',t,'color')
        bs.gameTimer(10000,t.delete)
        
registerMap(AlwaysLandMap)


class StepRightUpMap(Map):
    import stepRightUpLevelDefs as defs
    name = 'Step Right Up'
    discordName = 'step_right_up'
    playTypes = ['melee','keepAway','teamFlag','conquest']

    @classmethod
    def getPreviewTextureName(cls):
        return 'stepRightUpPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('stepRightUpLevel')
        data['modelBottom'] = bs.getModel('stepRightUpLevelBottom')
        data['collideModel'] = bs.getCollideModel('stepRightUpLevelCollide')
        data['tex'] = bs.getTexture('stepRightUpLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        data['bgModel'] = bs.getModel('thePadBG') # fixme should chop this into vr/non-vr chunks
        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,-1,2))
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.nodeBottom = bs.newNode('terrain',
                                     delegate=self,
                                     attrs={'model':self.preloadData['modelBottom'],
                                            'lighting':False,
                                            'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.53,0.57,0.5),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.2,1.1,1.0)
        bsGlobals.ambientColor = (1.2,1.1,1.0)
        bsGlobals.vignetteOuter = (0.7,0.65,0.75)
        bsGlobals.vignetteInner = (0.95,0.95,0.93)

registerMap(StepRightUpMap)

class CourtyardMap(Map):
    import courtyardLevelDefs as defs
    name = 'Courtyard'
    discordName = 'courtyard'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'courtyardPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('courtyardLevel')
        data['modelBottom'] = bs.getModel('courtyardLevelBottom')
        data['collideModel'] = bs.getCollideModel('courtyardLevelCollide')
        data['tex'] = bs.getTexture('courtyardLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        data['bgModel'] = bs.getModel('thePadBG') # fixme - chop this into vr and non-vr chunks
        data['playerWallCollideModel'] = bs.getCollideModel('courtyardPlayerWall')
    
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision','friction',0.0)))

        # anything that needs to hit the wall should apply this.
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial',data['collideWithWallMaterial']),
            actions=('modifyPartCollision','collide',False))

        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['modelBottom'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})

        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.53,0.57,0.5),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        
        # in challenge games, put up a wall to prevent players
        # from getting in the turrets (that would foil our brilliant AI)
        if 'CoopSession' in str(type(bs.getSession())):
            self.playerWall = bs.newNode('terrain',
                                         attrs={'collideModel':self.preloadData['playerWallCollideModel'],
                                                'affectBGDynamics':False,
                                                'materials':[self.preloadData['playerWallMaterial']]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.2,1.17,1.1)
        bsGlobals.ambientColor = (1.2,1.17,1.1)
        bsGlobals.vignetteOuter = (0.6,0.6,0.64)
        bsGlobals.vignetteInner = (0.95,0.95,0.93)

    def _isPointNearEdge(self,p,running=False):
        # count anything off our ground level as safe (for our platforms)
        #if p.y() > 3.1: return False
        # see if we're within edgeBox
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(CourtyardMap)


class RampageMap(Map):
    import rampageLevelDefs as defs
    name = 'Rampage'
    discordName = 'rampage'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'rampagePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('rampageLevel')
        data['bottomModel'] = bs.getModel('rampageLevelBottom')
        data['collideModel'] = bs.getCollideModel('rampageLevelCollide')
        data['tex'] = bs.getTexture('rampageLevelColor')
        data['bgTex'] = bs.getTexture('rampageBGColor')
        data['bgTex2'] = bs.getTexture('rampageBGColor2')
        data['bgModel'] = bs.getModel('rampageBG')
        data['bgModel2'] = bs.getModel('rampageBG2')
        data['vrFillModel'] = bs.getModel('rampageVRFill')
        data['railingCollideModel'] = bs.getCollideModel('rampageBumper')
        return data
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,0,2))
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['bottomModel'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        self.bg2 = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel2'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex2']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['bgTex2']})
        self.railing = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['railingCollideModel'],
                                         'materials':[bs.getSharedObject('railingMaterial')],
                                         'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.2,1.1,0.97)
        bsGlobals.ambientColor = (1.3,1.2,1.03)
        bsGlobals.vignetteOuter = (0.62,0.64,0.69)
        bsGlobals.vignetteInner = (0.97,0.95,0.93)

    def _isPointNearEdge(self,p,running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(RampageMap)

class HappyTowerDMap(Map):
    import towerDLevelDefs as defs
    name = 'Happy Tower D'
    discordName = 'happy_d'
    playTypes = ['melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'towerDPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('towerDLevel')
        data['modelBottom'] = bs.getModel('towerDLevelBottom')
        data['collideModel'] = bs.getCollideModel('towerDLevelCollide')
        data['tex'] = bs.getTexture('towerDLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        data['bgModel'] = bs.getModel('thePadBG') # fixme: divide this into vr and non-vr parts
        data['playerWallCollideModel'] = bs.getCollideModel('towerDPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision','friction',0.0)))
        # anything that needs to hit the wall can apply this material
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial',data['collideWithWallMaterial']),
            actions=(('modifyPartCollision','collide',False)))
        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,1,1))
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.nodeBottom = bs.newNode('terrain',
                                     delegate=self,
                                     attrs={'model':self.preloadData['modelBottom'],
                                            'lighting':False,
                                            'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.53,0.57,0.5),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.playerWall = bs.newNode('terrain',
                                     attrs={'collideModel':self.preloadData['playerWallCollideModel'],
                                            'affectBGDynamics':False,
                                            'materials':[self.preloadData['playerWallMaterial']]})

        g = bs.getSharedObject('globals')
        g.tint = (1.15,1.11,1.03)
        deftint = (1.15,1.11,1.03)
        deftint2 = (1.16,1.12,1.04)
        g.ambientColor = (1.2,1.1,1.0)
        g.vignetteOuter = (0.7,0.73,0.7)
        g.vignetteInner = (0.95,0.95,0.95)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5
        self.stdtint = deftint
        deftint = (1.15,1.11,1.03)
        deftint2 = (1.16,1.12,1.04)

        def chckr():
            if not self.stdtint == bs.getSharedObject('globals').tint:
                self.stdtint = bs.getSharedObject('globals').tint
            else:
                bs.animateArray(bs.getSharedObject('globals'), 'tint', 3, {
                    0: deftint, 60000: deftint2, 90000: (1.2,0.6,0.6),
                    120000: (0.5,0.6,0.8), 180000: (0.5,0.7,1.46),
                    210000: (1.39,1.0,0.0), 240000: deftint
                    }, loop=True)

        chckr()
        bs.gameTimer(500, bs.Call(chckr), repeat=True)

    def _isPointNearEdge(self,p,running=False):
        # see if we're within edgeBox
        boxes = self.defs.boxes
        boxPosition = boxes['edgeBox'][0:3]
        boxScale = boxes['edgeBox'][6:9]
        boxPosition2 = boxes['edgeBox2'][0:3]
        boxScale2 = boxes['edgeBox2'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        x2 = (p.x() - boxPosition2[0])/boxScale2[0]
        z2 = (p.z() - boxPosition2[2])/boxScale2[2]
        # if we're outside of *both* boxes we're near the edge
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5) and (x2 < -0.5 or x2 > 0.5 or z2 < -0.5 or z2 > 0.5)

registerMap(HappyTowerDMap)

class ToiletDonutMap(Map):
    import toiletDonutLevelDefs as defs
    name = 'Toilet Donut'
    discordName = 'toilet_donut'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'toiletDonutPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('toiletDonutLevel')
        data['collideModel'] = bs.getCollideModel('toiletDonutLevelCollide')
        data['tex'] = bs.getTexture('toiletDonutLevelColor')
        data['bgTex'] = bs.getTexture('toiletDonutBGColor')
        data['bgModel'] = bs.getModel('toiletDonutBG')
        return data
		
    @classmethod
    def getMusicType(cls):
        return 'Toilet'
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.82,1.10,1.15)
        bsGlobals.ambientColor = (0.9,1.3,1.1)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (0.76,0.76,0.76)
        bsGlobals.vignetteInner = (0.95,0.95,0.99)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(ToiletDonutMap)

class ShinyShroomMap(Map):
    import doomShroomLevelDefsCOOP as defs
    name = 'Shiny Shroom'
    discordName = 'shiny_shroom'
    playTypes = ['melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'doomShroomPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data = {}
        data['model'] = bs.getModel('doomShroomLevelCOOP')
        data['collideModel'] = bs.getCollideModel('doomShroomLevelCollideCOOP')
        data['tex'] = bs.getTexture('doomShroomLevelColor')
        data['bgTex'] = bs.getTexture('doomShroomBGColor')
        data['bgModel'] = bs.getModel('doomShroomBG')
        data['vrFillModel'] = bs.getModel('doomShroomVRFill')
        data['stemModel'] = bs.getModel('doomShroomStemCOOP')
        data['collideBG'] = bs.getCollideModel('doomShroomStemCollideCOOP')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['bgTex']})
        self.stem = bs.newNode('terrain',
                               attrs={'model':self.preloadData['stemModel'],
                                      'lighting':False,
                                      'colorTexture':self.preloadData['tex']})
        self.bgCollide = bs.newNode('terrain',
                                    attrs={'collideModel':self.preloadData['collideBG'],
                                           'materials':[bs.getSharedObject('footingMaterial'),bs.getSharedObject('deathMaterial')]})

        g = bs.getSharedObject('globals')
        g.ambientColor = (0.9,1.3,1.1)
        g.vignetteOuter = (0.76,0.76,0.76)
        g.vignetteInner = (0.95,0.95,0.99)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5
        g.tint = (0.82,1.10,1.15)
        deftint = (0.83,1.11,1.16)
        deftint2 = (0.84, 1.12,1.16)
        self.stdtint = deftint

        def chckr():
            if not self.stdtint == bs.getSharedObject('globals').tint:
                self.stdtint = bs.getSharedObject('globals').tint
            else:
                bs.animateArray(bs.getSharedObject('globals'), 'tint', 3, {
                    0: deftint, 60000: deftint2, 90000: (1.2,0.6,0.6),
                    120000: (0.5,0.6,0.8), 180000: (0.5,0.7,1.46),
                    210000: (1.39,1.0,0.0), 240000: deftint
                    }, loop=True)

        chckr()
        bs.gameTimer(500, bs.Call(chckr), repeat=True)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(ShinyShroomMap)

class PillarBasesMap(Map):
    import pillarBasesLevelDefs as defs
    name = 'Pillar Bases'
    discordName = 'pillar_bases'
    playTypes = ['melee','keepAway','teamFlag','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'pillarBasesPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('pillarBasesLevel')
        data['bottomModel'] = bs.getModel('pillarBasesLevelBottom')
        data['collideModel'] = bs.getCollideModel('pillarBasesLevelCollide')
        data['railingCollideModel'] = bs.getCollideModel('pillarBasesLevelBumper')
        data['tex'] = bs.getTexture('pillarBasesLevelColor')
        data['bgTex'] = bs.getTexture('nightBG')
        data['bottomTex'] = bs.getTexture('pillarBasesRock')
        data['bgModel'] = bs.getModel('thePadBG') # fixme should chop this into vr/non-vr sections
        data['vrFillMoundModel'] = bs.getModel('thePadVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['bottomModel'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['bottomTex']})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        self.railing = bs.newNode('terrain',
                               attrs={'collideModel':self.preloadData['railingCollideModel'],
                                     'materials':[bs.getSharedObject('railingMaterial')],
                                     'bumper':True})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.56,0.55,0.47),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1,1.1,1.0)
        bsGlobals.ambientColor = (1.1,1.1,1.0)
        bsGlobals.shadowOrtho = True
        bsGlobals.vignetteOuter = (0.7,0.65,0.75)
        bsGlobals.vignetteInner = (0.95,0.95,0.93)
        bsGlobals.vrCameraOffset = (0,5,0)
        bsGlobals.vrNearClip = 0.5

registerMap(PillarBasesMap)

class OuyaMap(Map):
    import ouyaLevelDefs as defs
    name = 'OUYA'
    discordName = 'ouya'
    playTypes = ['melee','keepAway','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'ouyaPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('ouyaLevel')
        data['collideModel'] = bs.getCollideModel('ouyaLevelCollide')
        data['tex'] = bs.getTexture('ouyaLevelColor')
        data['bgTex'] = bs.getTexture('reflectionSharp_+y')
        data['bgModel'] = bs.getModel('ouyaBG')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})

        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.82,1.10,1.15)
        bsGlobals.ambientColor = (0.9,1.3,1.1)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (0.76,0.76,0.76)
        bsGlobals.vignetteInner = (0.95,0.95,0.99)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(OuyaMap)

class MorningMap(Map):
    import morningLevelDefs as defs
    name = 'Morning'
    discordName = 'morning'
    playTypes = ['melee','keepAway','kingOfTheHill','captureTheFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'morningPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('morningLevel')
        data['collideModel'] = bs.getCollideModel('morningLevelCollide')
        data['tex'] = bs.getTexture('morningLevelColor')
        data['bgTex'] = bs.getTexture('morningBG')
        data['bgModel'] = bs.getModel('thePadBG')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
                                     
        birdsSound = bs.getSound('morningBirds')
        bs.newNode('sound',owner=self.node,attrs={'sound':birdsSound,'volume':0.1})
                                     
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1,1.05,0.9)
        bsGlobals.ambientColor = (1.05,1.1,1.0)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (1,1,1)
        bsGlobals.vignetteInner = (0.99,0.99,0.98)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(MorningMap)


class MorningCoopMap(Map):
    import morningCOOPLevelDefs as defs
    name = 'Morning Coop'
    discordName = 'morning'
    playTypes = []

    @classmethod
    def getPreviewTextureName(cls):
        return 'morningPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('morningLevel')
        data['collideModel'] = bs.getCollideModel('morningLevelCollide')
        data['tex'] = bs.getTexture('morningLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        data['bgModel'] = bs.getModel('thePadBG')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
                                     
        birdsSound = bs.getSound('morningBirds')
        bs.newNode('sound',owner=self.node,attrs={'sound':birdsSound,'volume':0.1})
        self.wallMaterial = bs.Material()
        self.wallMaterial.addActions(
            conditions=(("theyHaveMaterial",bs.getSharedObject("powerupMaterial")),'or',("theyHaveMaterial",bs.getSharedObject("playerMaterial"))),
            actions=(("modifyPartCollision","collide",True),('modifyPartCollision','useNodeCollide',False)))
        self._walls = []
        self._walls.append(bs.NodeActor(bs.newNode('region',
                                                          attrs={'position':(5.80457, 4.50949, -11.0904),
                                                                 'scale':(2.5,15,20.5),
                                                                 'type': 'box',
                                                                 'materials':(self.wallMaterial,)})))
        self._walls.append(bs.NodeActor(bs.newNode('region',
                                                          attrs={'position':(-3.5802, 4.50949, -11.0904),
                                                                 'scale':(2.5,15,20.5),
                                                                 'type': 'box',
                                                                 'materials':(self.wallMaterial,)})))
        self._walls.append(bs.NodeActor(bs.newNode('region',
                                                          attrs={'position':(1.00527, 1.650, -0.4029),
                                                                 'scale':(20.5,15,4.5),
                                                                 'type': 'box',
                                                                 'materials':(self.wallMaterial,)})))
        
        
        self.d = bs.Blocker(position=(-2.95871, 4.0, -10.9904),
                           velocity=(0,0,0),size=1.5)
        self.d1 = bs.Blocker(position=(-2.95871, 4.0, -9.5060),
                           velocity=(0,0,0),size=1.5)
        self.d2 = bs.Blocker(position=(-2.95871, 4.0, -8.2590),
                           velocity=(0,0,0),size=1.57)
                           
                           
        self.d3= bs.Blocker(position=(5.28883, 4.0, -11.0904),
                           velocity=(0,0,0),size=1.5)
        self.d4 = bs.Blocker(position=(5.28883, 4.0, -9.5060),
                           velocity=(0,0,0),size=1.5)
        self.d5 = bs.Blocker(position=(5.28883, 4.0, -8.2590),
                           velocity=(0,0,0),size=1.57)
                           
        self.d6 = bs.Blocker(position=(5.08883, 1.7, -7.02092),
                           velocity=(0,0,1),size=1.6)
        self.d7 = bs.Blocker(position=(5.08883, 1.79, -5.4005),
                           velocity=(0,0,1),size=1.6)
        self.d8 = bs.Blocker(position=(5.08883, 1.7, -3.4162),
                           velocity=(0,0,1),size=1.6)
                           
        self.d9 = bs.Blocker(position=(-2.90568, 1.7, -6.91214),
                           velocity=(0,0,1),size=1.6)
        self.d10 = bs.Blocker(position=(-2.9484, 1.7, -3.8),
                           velocity=(0,0,1),size=1.6)
        self.d11 = bs.Blocker(position=(-2.9484, 1.7, -5.5),
                           velocity=(0,0,1),size=1.6)
                                     
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1,1.05,0.9)
        bsGlobals.ambientColor = (1.05,1.1,1.0)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (1,1,1)
        bsGlobals.vignetteInner = (0.99,0.99,0.98)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(MorningCoopMap)

class HoveringWoodMap(Map):
    import hoveringWoodLevelDefs as defs
    name = 'Hovering Plank-o-Wood'
    discordName = 'hovering_plank-o-wood'
    playTypes = ['melee','keepAway','conquest']

    @classmethod
    def getPreviewTextureName(cls):
        return 'hoveringWoodPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('hoveringWoodLevel')
        data['collideModel'] = bs.getCollideModel('hoveringWoodLevelCollide')
        data['tex'] = bs.getTexture('hoveringWoodLevelColor')
        data['bgTex'] = bs.getTexture('hoveringWoodBGColor')
        data['bgModel'] = bs.getModel('skysphere')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.15,1.10,0.82)
        bsGlobals.ambientColor = (1.2,1.3,1.0)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (1,1,1)
        bsGlobals.vignetteInner = (0.99,0.99,0.95)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(HoveringWoodMap)

class HoveringWoodNightMap(Map):
    import hoveringWoodLevelDefs as defs
    name = 'Hovering Plank-o-Wood Night'
    discordName = 'hovering_plank-o-wood night'
    playTypes = ['melee','keepAway','conquest']

    @classmethod
    def getPreviewTextureName(cls):
        return 'hoveringWoodPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('hoveringWoodLevel')
        data['collideModel'] = bs.getCollideModel('hoveringWoodLevelCollide')
        data['tex'] = bs.getTexture('hoveringWoodLevelColor')
        data['bgTex'] = bs.getTexture('spaceBGColor')
        data['bgModel'] = bs.getModel('skysphere')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.5,0.7,1.0)
        bsGlobals.ambientColor = (1.2,1.3,1.0)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (1,1,1)
        bsGlobals.vignetteInner = (0.99,0.99,0.95)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(HoveringWoodNightMap)

class AlwaysLandNightMap(Map):
    import alwaysLandLevelDefs as defs
    name = 'Brightland'
    discordName = 'brightland'
    playTypes = ['melee','keepAway','teamFlag','conquest','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'alwaysLandPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('alwaysLandLevel')
        data['bottomModel'] = bs.getModel('alwaysLandLevelBottom')
        data['bgModel'] = bs.getModel('alwaysLandBG')
        data['collideModel'] = bs.getCollideModel('alwaysLandLevelCollide')
        data['tex'] = bs.getTexture('alwaysLandLevelColor')
        data['bgTex'] = bs.getTexture('spaceBGColor')
        data['vrFillMoundModel'] = bs.getModel('alwaysLandVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    @classmethod
    def getMusicType(cls):
        return 'Flying'
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,-3.7,2.5))
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['bottomModel'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.2,0.25,0.2),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        g = bs.getSharedObject('globals')
        g.happyThoughtsMode = True
        g.shadowOffset = (0.0,8.0,5.0)
        g.tint = (2.0,1.7,0.8)
        g.ambientColor = (1.3,1.23,1.0)
        g.vignetteOuter = (0.64,0.59,0.69)
        g.vignetteInner = (0.95,0.95,0.93)
        g.vrNearClip = 1.0
        self.isFlying = True

        # throw out some tips on flying
        t = bs.newNode('text',
                       attrs={'text':bs.Lstr(resource='pressJumpToFlyText'),
                              'scale':1.2,
                              'maxWidth':800,
                              'position':(0,200),
                              'shadow':0.5,
                              'flatness':0.5,
                              'hAlign':'center',
                              'vAttach':'bottom'})
        c = bs.newNode('combine',owner=t,attrs={'size':4,'input0':0.3,'input1':0.9,'input2':0.0})
        bsUtils.animate(c,'input3',{3000:0,4000:1,9000:1,10000:0})
        c.connectAttr('output',t,'color')
        bs.gameTimer(10000,t.delete)
        
registerMap(AlwaysLandNightMap)

class FrozenLakeMap(Map):
    import lakeFrigidDefs as defs
    name = 'Frozen Lake'
    discordName = 'frozen_lake'
    playTypes = ['melee','keepAway','teamFlag','race']
    winter = False

    @classmethod
    def getPreviewTextureName(cls):
        return 'lakeFrigidPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('lakeFrigid')
        data['modelTop'] = bs.getModel('lakeFrigidTop')
        data['modelReflections'] = bs.getModel('lakeFrigidReflections')
        data['collideModel'] = bs.getCollideModel('lakeFrigidCollide')
        data['tex'] = bs.getTexture('lakeFrigid')
        data['texReflections'] = bs.getTexture('lakeFrigidReflections')
        #data['bgTex'] = bs.getTexture('lakeFrigidBGColor')
        #data['bgModel'] = bs.getModel('lakeFrigidBG')
        data['vrFillModel'] = bs.getModel('lakeFrigidVRFill')
        m = bs.Material()
        m.addActions(actions=('modifyPartCollision','friction',1.0))
        data['iceMaterial'] = m
        
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      # 'reflection':'soft',
                                      # 'reflectionScale':[0.65],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial'),self.preloadData['iceMaterial']]})
        # self.foo = bs.newNode('terrain',
        #                       attrs={'model':self.preloadData['bgModel'],
        #                              'lighting':False,
        #                              'background':True,
        #                              'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['modelTop'],
                          'lighting':False,
                          'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['modelReflections'],
                          'lighting':False,
                          'overlay':True,
                          'opacity':0.15,
                          'colorTexture':self.preloadData['texReflections']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['tex']})
        # self.stem = bs.newNode('terrain',
        #                        attrs={'model':self.preloadData['stemModel'],
        #                               'lighting':False,
        #                               'colorTexture':self.preloadData['tex']})
        # self.bgCollide = bs.newNode('terrain',
        #                             attrs={'collideModel':self.preloadData['collideBG'],
        #                                    'materials':[bs.getSharedObject('footingMaterial'),bs.getSharedObject('deathMaterial')]})
        g = bs.getSharedObject('globals')
        g.tint = (1,1,1)
        g.ambientColor = (1,1,1)
        g.shadowOrtho = True
        g.vignetteOuter = (0.86,0.86,0.86)
        g.vignetteInner = (0.95,0.95,0.99)

        g.vrNearClip = 0.5
        
        self.isHockey = False
        
    # def _isPointNearEdge(self,p,running=False):
    #     x = p.x()
    #     z = p.z()
    #     xAdj = x*0.125
    #     zAdj = (z+3.7)*0.2
    #     if running:
    #         xAdj *= 1.4
    #         zAdj *= 1.4
    #     return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(FrozenLakeMap)

class SnowyFrozenLakeMap(Map):
    import lakeFrigidDefs as defs
    name = 'Snowy Frozen Lake'
    discordName = 'snowy_frozen_lake'
    playTypes = ['melee','keepAway','teamFlag','race']
    winter = True

    @classmethod
    def getPreviewTextureName(cls):
        return 'lakeFrigidPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('lakeFrigid')
        data['modelTop'] = bs.getModel('lakeFrigidTop')
        data['modelReflections'] = bs.getModel('lakeFrigidReflections')
        data['collideModel'] = bs.getCollideModel('lakeFrigidCollide')
        data['tex'] = bs.getTexture('lakeFrigid')
        data['texReflections'] = bs.getTexture('lakeFrigidReflections')
        #data['bgTex'] = bs.getTexture('lakeFrigidBGColor')
        #data['bgModel'] = bs.getModel('lakeFrigidBG')
        data['vrFillModel'] = bs.getModel('lakeFrigidVRFill')
        m = bs.Material()
        m.addActions(actions=('modifyPartCollision','friction',0.01))
        data['iceMaterial'] = m
        
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      # 'reflection':'soft',
                                      # 'reflectionScale':[0.65],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial'),self.preloadData['iceMaterial']]})
        # self.foo = bs.newNode('terrain',
        #                       attrs={'model':self.preloadData['bgModel'],
        #                              'lighting':False,
        #                              'background':True,
        #                              'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['modelTop'],
                          'lighting':False,
                          'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['modelReflections'],
                          'lighting':False,
                          'overlay':True,
                          'opacity':0.15,
                          'colorTexture':self.preloadData['texReflections']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['tex']})
        # self.stem = bs.newNode('terrain',
        #                        attrs={'model':self.preloadData['stemModel'],
        #                               'lighting':False,
        #                               'colorTexture':self.preloadData['tex']})
        # self.bgCollide = bs.newNode('terrain',
        #                             attrs={'collideModel':self.preloadData['collideBG'],
        #                                    'materials':[bs.getSharedObject('footingMaterial'),bs.getSharedObject('deathMaterial')]})
        g = bs.getSharedObject('globals')
        g.tint = (1,1.2,1.8)
        g.ambientColor = (1,1,1)
        g.shadowOrtho = True
        g.vignetteOuter = (0.86,0.86,0.86)
        g.vignetteInner = (0.95,0.95,0.99)
        self._emit = bs.Timer(15, bs.WeakCall(self.emit), repeat=True)

    def emit(self):
        pos = (-15+(random.random()*30),
               15,
               -15+(random.random()*30))

        vel1 = (-5.0 + random.random()*30.0) \
            * (-1.0 if pos[0] > 0 else 1.0)

        vel = (vel1,
               -50.0,
               random.uniform(-20, 20))

        bs.emitBGDynamics(
            position=pos,
            velocity=vel,
            count=15,
            scale=0.4+random.random(),
            spread=0,
            chunkType='spark')

        g.vrNearClip = 0.5
        
        self.isHockey = True
        
    # def _isPointNearEdge(self,p,running=False):
    #     x = p.x()
    #     z = p.z()
    #     xAdj = x*0.125
    #     zAdj = (z+3.7)*0.2
    #     if running:
    #         xAdj *= 1.4
    #         zAdj *= 1.4
    #     return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(SnowyFrozenLakeMap)

class WhereEaglesDareMap(Map):
    import whereEaglesDareLevelDefs as defs
    name = 'Where Eagles Dare'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'whereEaglesDarePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('whereEaglesDareLevel')
        data['collideModel'] = bs.getCollideModel('whereEaglesDareLevelCollide')
        data['railingCollideModel'] = bs.getCollideModel('whereEaglesDareLevelBumper')
        data['tex'] = bs.getTexture('whereEaglesDareLevelColor')
        data['bgTex'] = bs.getTexture('rampageBGColor')
        data['bgTex2'] = bs.getTexture('rampageBGColor2')
        data['bgModel'] = bs.getModel('rampageBG')
        data['bgModel2'] = bs.getModel('rampageBG2')
        data['playerWallCollideModel'] = bs.getCollideModel('towerDPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision','friction',0.0)))
        # anything that needs to hit the wall can apply this material
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial',data['collideWithWallMaterial']),
            actions=(('modifyPartCollision','collide',False)))
        data['vrFillModel'] = bs.getModel('rampageVRFill')
        return data
		
    @classmethod
    def getMusicType(cls):
        return 'Where Eagles Dare'
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.bg2 = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel2'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex2']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['bgTex2']})
        self.railing = bs.newNode('terrain',
                               attrs={'collideModel':self.preloadData['railingCollideModel'],
                                     'materials':[bs.getSharedObject('railingMaterial')],
                                     'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.15,1.10,0.82)
        bsGlobals.ambientColor = (1.2,1.3,1.0)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (1,1,1)
        bsGlobals.vignetteInner = (0.99,0.99,0.95)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(WhereEaglesDareMap)

class CourtyardNightMap(Map):
    import courtyardLevelDefs as defs
    name = 'Courtyard Night'
    discordName = 'courtyard_night'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'courtyardNightPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('courtyardLevel')
        data['modelBottom'] = bs.getModel('courtyardLevelBottom')
        data['collideModel'] = bs.getCollideModel('courtyardLevelCollide')
        data['tex'] = bs.getTexture('courtyardNightLevelColor')
        data['bgTex'] = bs.getTexture('nightBG')
        data['bgModel'] = bs.getModel('thePadBG') # fixme - chop this into vr and non-vr chunks
        data['playerWallCollideModel'] = bs.getCollideModel('courtyardPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision','friction',0.0)))
        # anything that needs to hit the wall can apply this material
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(conditions=('theyDontHaveMaterial',data['collideWithWallMaterial']),actions=(('modifyPartCollision','collide',False)))
        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        
        return data
        
    @classmethod
    def getMusicType(cls):
        return 'Nightmare'

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
                          
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['modelBottom'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['tex']})

        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.53,0.57,0.5),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
                          
        # in challenge games, put up a wall to prevent players
        # from getting in the turrets (that would foil our brilliant AI)
        if 'CoopSession' in str(type(bs.getSession())):
            self.playerWall = bs.newNode('terrain',
                                         attrs={'collideModel':self.preloadData['playerWallCollideModel'],
                                                'affectBGDynamics':False,
                                                'materials':[self.preloadData['playerWallMaterial']]})
        
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.65,0.65,0.8)
        bsGlobals.ambientColor = (0.51,0.71,0.67)
        bsGlobals.vignetteOuter = (0.8,0.8,0.8)
        bsGlobals.vignetteInner = (1.0,1.0,1.0)
        

    def _isPointNearEdge(self,p,running=False):
        # count anything off our ground level as safe (for our platforms)
        #if p.y() > 3.1: return False
        # see if we're within edgeBox
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)
        
registerMap(CourtyardNightMap)

class BlockFortressMap(Map):
    import arenaLevelDefs as defs
    name = 'Block Fortress'
    discordName = 'block_fortress'
    playTypes = ['melee','keepAway','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'arenaPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('arenaLevel')
        data['collideModel'] = bs.getCollideModel('arenaLevelCollide')
        data['tex'] = bs.getTexture('arenaLevelColor')
        data['bgTex'] = bs.getTexture('arenaBG')
        data['bgModel'] = bs.getModel('thePadBG')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.8,0.8,0.8)
        bsGlobals.ambientColor = (0.6,0.6,0.6)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (1,1,1)
        bsGlobals.vignetteInner = (0.95,0.95,0.95)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(BlockFortressMap)

class BaconGreeceMap(Map):
    import baconGreeceLevelDefs as defs
    name = 'Bacon Greece'
    discordName = 'bacon_greece'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'baconGreecePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('baconGreeceVisible')
        data['water'] = bs.getModel('waterVisible')
        data['collideModel'] = bs.getCollideModel('baconGreeceCollision')
        data['railingCollideModel'] = bs.getCollideModel('baconGreeceRailing')
        data['tex'] = bs.getTexture('baconGreeceLevelColor')
        data['BGmodel'] = bs.getModel('baconGreeceBG')
        data['BGtex'] = bs.getTexture('baconGreeceBG')
        data['waterTex'] = [bs.getTexture('water1'),
                            bs.getTexture('water2'),
                            bs.getTexture('water3')]
        data['skyTex'] = bs.getTexture('hoveringWoodBGColor')
        data['skyModel'] = bs.getModel('skysphere')
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.water = bs.newNode('terrain',
                               attrs={'model':self.preloadData['water'],
                                      'lighting':False,
                                      'colorTexture':self.preloadData['waterTex'][0]})
        self.sky = bs.newNode('terrain',
                              attrs={'model':self.preloadData['skyModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['skyTex']})
        self.bg = bs.newNode('terrain',
                              attrs={'model':self.preloadData['BGmodel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['BGtex']})
        self.railing = bs.newNode('terrain',
                               attrs={'collideModel':self.preloadData['railingCollideModel'],
                                     'materials':[bs.getSharedObject('railingMaterial')],
                                     'bumper':True})
           
        seaSound = bs.getSound('seaAmbience')
        bs.newNode('sound',owner=self.water,attrs={'sound':seaSound,'volume':0.1})
        
        def waterAnim():
            if self.water.colorTexture == self.preloadData['waterTex'][0]:
                self.water.colorTexture = self.preloadData['waterTex'][1]
            elif self.water.colorTexture == self.preloadData['waterTex'][1]:
                self.water.colorTexture = self.preloadData['waterTex'][2]
            elif self.water.colorTexture == self.preloadData['waterTex'][2]:
                self.water.colorTexture = self.preloadData['waterTex'][0]
                
        bs.gameTimer(200,waterAnim,True)
                                         
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1,1.1,0.9)
        bsGlobals.ambientColor = (1.1,1.1,0.9)
        bsGlobals.vignetteOuter = (0.65,0.65,0.68)
        bsGlobals.vignetteInner = (0.95,0.95,0.93)

registerMap(BaconGreeceMap)

class ForestMap(Map):
    import forestDefs as defs
    name = "Clay Lands"
    discordName = 'clay lands'

    playTypes = ['melee','teamFlag','keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'natureBackgroundColor'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel("natureBackground")
        data['vrFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel("natureBackgroundCollide")
        data['tex'] = bs.getTexture("natureBackgroundColor")
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'model':self.preloadData['model'],
                                      'collideModel':self.preloadData['collideModel'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['tex']})

        g = bs.getSharedObject('globals')
        g.tint = (1.15,1.11,1.03)
        deftint = (1.15,1.11,1.03)
        deftint2 = (1.16,1.12,1.04)
        g.ambientColor = (1.2,1.1,1.0)
        g.vignetteOuter = (0.7,0.73,0.7)
        g.vignetteInner = (0.95,0.95,0.95)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5
        self.stdtint = deftint

        def chckr():
            if not self.stdtint == bs.getSharedObject('globals').tint:
                self.stdtint = bs.getSharedObject('globals').tint
            else:
                bs.animateArray(bs.getSharedObject('globals'), 'tint', 3, {
                    0: deftint, 60000: deftint2, 90000: (1.2,0.6,0.6),
                    120000: (0.5,0.7,0.9), 180000: (0.5,0.7,1.46),
                    210000: (1.39,1.0,0.0), 240000: deftint
                    }, loop=True)

        chckr()
        bs.gameTimer(500, bs.Call(chckr), repeat=True)

    def _isPointNearEdge(self,p,running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(ForestMap)

class MushFeudMap(Map):
    import mushFeudLevelDefs as defs
    name = 'Mush Feud'
    discordName = 'mush_feud'
    playTypes = ['melee','keepAway','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'mushFeudPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('mushFeudLevel')
        data['collideModel'] = bs.getCollideModel('mushFeudLevelCollide')
        data['tex'] = bs.getTexture('mushFeudLevelColor')
        data['skyTex'] = bs.getTexture('mushFeudSky')
        data['skyModel'] = bs.getModel('alwaysLandBG')
        data['bgTex'] = bs.getTexture('mushFeudBGColor')
        data['bgModel'] = bs.getModel('mushFeudBG')
        data['bgCollide'] = bs.getCollideModel('mushFeudBGCollide')
        data['vrFillMoundModel'] = bs.getModel('thePadVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['skyModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['skyTex']})
        self.bg = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        self.bgCollide = bs.newNode('terrain',
                                    attrs={'collideModel':self.preloadData['bgCollide'],
                                           'materials':[bs.getSharedObject('footingMaterial')]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.95,0.95,1.0)
        bsGlobals.ambientColor = (0.9,0.9,1.0)
        bsGlobals.vignetteOuter = (0.75,0.75,0.76)
        bsGlobals.vignetteInner = (0.94,0.94,0.95)

registerMap(MushFeudMap)

class SpaceMap(Map):
    import spaceLevelDefs as defs
    name = 'A Space Odyssey'
    discordName = 'a_space_odyssey'
    playTypes = ['melee','keepAway','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'spacePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('spaceLevel')
        data['bgModel'] = bs.getModel('spaceBG')
        data['collideModel'] = bs.getCollideModel('spaceLevelCollide')
        data['tex'] = bs.getTexture('spaceLevelColor')
        data['bgTex'] = bs.getTexture('spaceBGColor')
        data['vrFillMoundModel'] = bs.getModel('alwaysLandVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    @classmethod
    def getMusicType(cls):
        return 'Flying'
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,-3.7,2.5))
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillMoundModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'color':(0.2,0.25,0.2),
                          'background':True,
                          'colorTexture':self.preloadData['vrFillMoundTex']})
        g = bs.getSharedObject('globals')
        g.happyThoughtsMode = True
        g.shadowOffset = (0.0,8.0,5.0)
        g.tint = (1.3,1.23,1.0)
        g.ambientColor = (1.3,1.23,1.0)
        g.vignetteOuter = (0.64,0.59,0.69)
        g.vignetteInner = (0.95,0.95,0.93)
        g.vrNearClip = 1.0
        self.isFlying = True

        # throw out some tips on flying
        t = bs.newNode('text',
                       attrs={'text':bs.Lstr(resource='pressJumpToFlyText'),
                              'scale':1.2,
                              'maxWidth':800,
                              'position':(0,200),
                              'shadow':0.5,
                              'flatness':0.5,
                              'hAlign':'center',
                              'vAttach':'bottom'})
        c = bs.newNode('combine',owner=t,attrs={'size':4,'input0':0.3,'input1':0.9,'input2':0.0})
        bsUtils.animate(c,'input3',{3000:0,4000:1,9000:1,10000:0})
        c.connectAttr('output',t,'color')
        bs.gameTimer(10000,t.delete)
        
registerMap(SpaceMap)

class FlaplandMap(Map):
    import flaplandLevelDefs as defs
    name = 'Flapland'
    discordName = 'flapland'
    playTypes = ['melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'flaplandPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('flaplandTop')
        data['texTop'] = bs.getTexture('flaplandLevelColor')
        data['modelBottom'] = bs.getModel('flaplandBottom')
        data['texBottom'] = bs.getTexture('flaplandBG')
        data['collideModel'] = bs.getCollideModel('flaplandCollide')
        data['bgTex'] = bs.getTexture('hoveringWoodBGColor')
        data['bgModel'] = bs.getModel('skysphere')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['texTop'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
                                      
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['modelBottom'],
                                        'lighting':False,
                                        'colorTexture':self.preloadData['texBottom']})
                                        
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.05,1.0,0.72)
        bsGlobals.ambientColor = (1.2,1.3,1.0)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (1,1,1)
        bsGlobals.vignetteInner = (0.99,0.99,0.95)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(FlaplandMap)

class WhereEaglesDareNightMap(Map):
    import whereEaglesDareLevelDefs as defs
    name = 'Eagles Dare Night'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'whereEaglesDarePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('whereEaglesDareLevel')
        data['collideModel'] = bs.getCollideModel('whereEaglesDareLevelCollide')
        data['railingCollideModel'] = bs.getCollideModel('whereEaglesDareLevelBumper')
        data['tex'] = bs.getTexture('whereEaglesDareLevelColor')
        data['bgTex'] = bs.getTexture('spaceBGColor')
        data['bgTex2'] = bs.getTexture('spaceBGColor')
        data['bgModel'] = bs.getModel('rampageBG')
        data['bgModel2'] = bs.getModel('rampageBG2')
        data['playerWallCollideModel'] = bs.getCollideModel('towerDPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision','friction',0.0)))
        # anything that needs to hit the wall can apply this material
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial',data['collideWithWallMaterial']),
            actions=(('modifyPartCollision','collide',False)))
        data['vrFillModel'] = bs.getModel('rampageVRFill')
        return data
		
    @classmethod
    def getMusicType(cls):
        return 'Where Eagles Dare Night'
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.bg2 = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel2'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex2']})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['bgTex2']})
        self.railing = bs.newNode('terrain',
                               attrs={'collideModel':self.preloadData['railingCollideModel'],
                                     'materials':[bs.getSharedObject('railingMaterial')],
                                     'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.5,0.7,1.0)
        bsGlobals.ambientColor = (2,2,2)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (1,1,1)
        bsGlobals.vignetteInner = (0.99,0.99,0.95)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(WhereEaglesDareNightMap)

class FlaplandNightMap(Map):
    import flaplandLevelDefs as defs
    name = 'Flapland Night'
    discordName = 'flapland'
    playTypes = ['keepAway','melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'flaplandPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('flaplandTop')
        data['texTop'] = bs.getTexture('flaplandLevelColor')
        data['modelBottom'] = bs.getModel('flaplandBottom')
        data['texBottom'] = bs.getTexture('flaplandBG')
        data['collideModel'] = bs.getCollideModel('flaplandCollide')
        data['bgTex'] = bs.getTexture('spaceBGColor')
        data['bgModel'] = bs.getModel('skysphere')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'lightning':False,
                                      'colorTexture':self.preloadData['texTop'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
                                      
        self.bottom = bs.newNode('terrain',
                                 attrs={'model':self.preloadData['modelBottom'],
                                        'lighting':True,
                                        'colorTexture':self.preloadData['texBottom']})
                                        
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.5,0.4,0.7)
        bsGlobals.ambientColor = (3.85,3.85,3.95)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (1,1,1)
        bsGlobals.vignetteInner = (0.99,0.99,0.95)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(FlaplandNightMap)

class JRMPOnslaughtMap(Map):
    import jrmpOnslaughtLevelDefs as defs
    name = 'JRMP Onslaught'
    discordName = 'jrmp_onslaught'
    playTypes = ['melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'jrmpOnslaughtPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('jrmpOnslaughtLevel')
        data['collideModel'] = bs.getCollideModel('jrmpOnslaughtLevelCollide')
        data['tex'] = bs.getTexture('jrmpOnslaughtLevelColor')
        data['bgTex'] = bs.getTexture('jrmpOnslaughtBG')
        data['bgModel'] = bs.getModel('skysphere')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.9,0.9,1.1)
        bsGlobals.ambientColor = (1.1,1.2,1.25)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (0.86,0.86,0.87)
        bsGlobals.vignetteInner = (0.95,0.95,0.99)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(JRMPOnslaughtMap)

class JRMPRunaroundMap(Map):
    import jrmpRunaroundLevelDefs as defs
    name = 'JRMP Runaround'
    discordName = 'jrmp_runaround'
    playTypes = ['melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'jrmpRunaroundPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('jrmpRunaroundLevel')
        data['collideModel'] = bs.getCollideModel('jrmpRunaroundLevelCollide')
        
        data['slide'] = bs.getCollideModel('jrmpRunaroundSlide')
        
        data['slideMaterial'] = bs.Material()
        data['slideMaterial'].addActions(actions=(('modifyPartCollision','friction',0.0)))
        
        data['playerWallCollideModel'] = bs.getCollideModel('jrmpRunaroundPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision','friction',0.0)))
        # anything that needs to hit the wall can apply this material
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial',data['collideWithWallMaterial']),
            actions=(('modifyPartCollision','collide',False)))
        
        data['tex'] = bs.getTexture('jrmpRunaroundLevelColor')
        data['bgTex'] = bs.getTexture('jrmpOnslaughtBG')
        data['bgModel'] = bs.getModel('skysphere')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        self.slide = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['slide'],
                                      'affectBGDynamics':False,
                                      'materials':[self.preloadData['playerWallMaterial']]})
        self.playerWall = bs.newNode('terrain',
                                     attrs={'collideModel':self.preloadData['playerWallCollideModel'],
                                            'affectBGDynamics':False,
                                            'materials':[self.preloadData['playerWallMaterial']]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.9,0.9,1.1)
        bsGlobals.ambientColor = (1.1,1.2,1.25)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (0.86,0.86,0.87)
        bsGlobals.vignetteInner = (0.95,0.95,0.99)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(JRMPRunaroundMap)

class CartoonFortMap(Map):
    import stoneishFortLevelDefs as defs
    name = 'Stone-ish Fort'
    discordName = 'stone-ish_fort'
    playTypes = ['melee','keepAway','teamFlag','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'stoneishFortPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('stoneishFortLevel')
        data['modelBottom'] = bs.getModel('stoneishFortLevelBottom')
        data['collideModel'] = bs.getCollideModel('stoneishFortLevelCollide')
        data['platformCollideModel'] = bs.getCollideModel('stoneishFortPlatformCollide')
        data['tex'] = bs.getTexture('stoneishFortLevelColor')
        data['bottomTex'] = bs.getTexture('stoneishFortBottomLevelColor')
        data['bgTex'] = bs.getTexture('cartoonBG')
        data['bgModel'] = bs.getModel('skyplane') # fixme should chop this into vr/non-vr chunks
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.nodeBottom = bs.newNode('terrain',
                                     delegate=self,
                                     attrs={'model':self.preloadData['modelBottom'],
                                            'lighting':False,
                                            'colorTexture':self.preloadData['bottomTex']})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.platformLimiter = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['platformCollideModel'],
                                         'materials':[bs.getSharedObject('platformMaterial')],
                                         'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.0,1.0,1.1)
        bsGlobals.ambientColor = (1.2,1.1,1.2)
        bsGlobals.vignetteOuter = (0.7,0.65,0.7)
        bsGlobals.vignetteInner = (0.95,0.95,0.95)

registerMap(CartoonFortMap)

class StoneishFortMap(Map):
    import stoneishFortLevelDefs as defs
    name = 'Stoneish Fort'
    discordName = 'stoneish_fort'
    playTypes = ['melee','keepAway','teamFlag','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'stoneishFortPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('stoneishFortLevel')
        data['modelBottom'] = bs.getModel('stoneishFortLevelBottom')
        data['collideModel'] = bs.getCollideModel('stoneishFortLevelCollide')
        data['platformCollideModel'] = bs.getCollideModel('stoneishFortPlatformCollide')
        data['tex'] = bs.getTexture('stoneishFortLevelColor')
        data['bottomTex'] = bs.getTexture('stoneishFortBottomLevelColor')
        data['bgTex'] = bs.getTexture('cartoonBG')
        data['bgModel'] = bs.getModel('skyplane') # fixme should chop this into vr/non-vr chunks
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.nodeBottom = bs.newNode('terrain',
                                     delegate=self,
                                     attrs={'model':self.preloadData['modelBottom'],
                                            'lighting':False,
                                            'colorTexture':self.preloadData['bottomTex']})
        self.bg = bs.newNode('terrain',
                             attrs={'model':self.preloadData['bgModel'],
                                    'lighting':False,
                                    'background':True,
                                    'colorTexture':self.preloadData['bgTex']})
        self.platformLimiter = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['platformCollideModel'],
                                         'materials':[bs.getSharedObject('platformMaterial')],
                                         'bumper':True})
        g = bs.getSharedObject('globals')
        g.tint = (1.0,1.0,1.1)
        deftint = (1.1,1.0,1.2)
        deftint2 = (1.2,1.1,1.2)
        g.ambientColor = (1.2,1.1,1.2)
        g.vignetteOuter = (0.7,0.65,0.7)
        g.vignetteInner = (0.95,0.95,0.95)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5
        self.stdtint = deftint

        def chckr():
            if not self.stdtint == bs.getSharedObject('globals').tint:
                self.stdtint = bs.getSharedObject('globals').tint
            else:
                bs.animateArray(bs.getSharedObject('globals'), 'tint', 3, {
                    0: deftint, 60000: deftint2, 90000: (1.2,0.6,0.6),
                    120000: (0.5,0.6,0.8), 180000: (0.5,0.7,1.46),
                    210000: (1.39,1.0,0.0), 240000: deftint
                    }, loop=True)

        chckr()
        bs.gameTimer(500, bs.Call(chckr), repeat=True)

registerMap(StoneishFortMap)

class PowerupFactoryMap(Map):
    import powerupFactoryLevelDefs as defs
    name = 'Powerup Factory'
    discordName = 'powerup_factory'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'powerupFactoryPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('powerupFactoryLevel')
        data['bg'] = bs.getModel('powerupFactoryBG')
        data['collideModel'] = bs.getCollideModel('powerupFactoryLevelCollide')
        data['platformCollideModel'] = bs.getCollideModel('powerupFactoryPlatformCollide')
        data['tex'] = bs.getTexture('powerupFactoryLevelColor')
        data['bgTex'] = bs.getTexture('factoryBG')
        data['bgModel'] = bs.getModel('skysphere')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain',
                               delegate=self,
                               attrs={'collideModel':self.preloadData['collideModel'],
                                      'model':self.preloadData['model'],
                                      'colorTexture':self.preloadData['tex'],
                                      'materials':[bs.getSharedObject('footingMaterial')]})
        self.bg = bs.newNode('terrain',
                               delegate=self,
                               attrs={'model':self.preloadData['bg'],
                                      'colorTexture':self.preloadData['tex'],
                                      'background':True})
        self.sky = bs.newNode('terrain',
                              attrs={'model':self.preloadData['bgModel'],
                                     'lighting':False,
                                     'background':True,
                                     'colorTexture':self.preloadData['bgTex']})
        self.platformLimiter = bs.newNode('terrain',
                                  attrs={'collideModel':self.preloadData['platformCollideModel'],
                                         'materials':[bs.getSharedObject('platformMaterial')],
                                         'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.9,0.8,0.8)
        bsGlobals.ambientColor = (0.7,0.6,0.6)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (0.7,0.65,0.65)
        bsGlobals.vignetteInner = (0.98,0.94,0.94)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(PowerupFactoryMap)