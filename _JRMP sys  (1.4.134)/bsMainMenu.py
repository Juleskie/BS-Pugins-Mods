import bs
import bsUtils
import bsUI
import bsSpaz
import random
import time
import datetime
import weakref
import bsInternal
import bsServerData

gDidInitialTransition = False
gStartTime = time.time()

    
class MainMenuActivity(bs.Activity):

    def __init__(self, settings={}):
        bs.Activity.__init__(self,settings)
        
        global timeOfDay
        self.timeNow = bs.checkTime()
        if self.timeNow['hour'] <= 4 or self.timeNow['hour'] >= 20: timeOfDay = 'night'
        elif self.timeNow['hour'] <= 9: timeOfDay = 'morning'
        elif self.timeNow['hour'] >= 17: timeOfDay = 'evening'
        else: timeOfDay = 'day'
        
    def onTransitionIn(self):
        import bsInternal
        bs.Activity.onTransitionIn(self)

        global gDidInitialTransition

        random.seed()
        
        # update Discord Rich Presence status
        import richPresence
        richPresence.discordMenu()

        self._logoNode = None
        self._customLogoTexName = None
        
        self._wordActors = []

        env = bs.getEnvironment()
        
        if not gDidInitialTransition:
            bs.getConfig()['Cheats Active'] = False
            bs.getConfig()['Cheat RJ'] = False
            bs.getConfig()['Cheat EXP'] = False
            bs.getConfig()['Cheat FP'] = False
            bs.getConfig()['Cheat KAB'] = False
            bs.getConfig()['Cheat OPM'] = False
            bs.getConfig()['Cheat IHTHG'] = False
            bs.writeConfig()
            
        # setup variables early on if you don't have them
        config = {'Enable Hard Powerups':False,
                  'Powerup Popups':True,
                  'Fancy Powerups':False,
                  'Offensive Curse Sound':True,
                  'Camera Shake':False,
                  'Rainbow Skin':False,
                  'Invulnerable Mode':False,
                  'Gain Shield':False,
                  'Unlimited Bombs':False,
                  'Enable Backflips':False,
                  'Enable New Powerups':True,
                  'Permanent Boxing Gloves':False,
                  'No Time Limit Powerups':False,
                  'Party Mode':False,
                  'HP Bar':'HP Bar Off',
                  'Powerup Distribution':'JRMP'}
        for key, value in config.iteritems():
            try: variable = bs.getConfig()[key]
            except Exception: bs.getConfig()[key] = value
        
        # FIXME - shouldn't be doing things conditionally based on whether the host is vr mode or not
        # (clients may not be or vice versa) - any differences need to happen at the engine level
        # so everyone sees things in their own optimal way
        vrMode = bs.getEnvironment()['vrMode']

        self.myName = bs.NodeActor(bs.newNode('text',
                                              attrs={'vAttach':'bottom',
                                                     'hAlign':'center',
                                                     'color':(1.0,1.0,1.0,1.0) if vrMode else (0.5,0.6,0.5,0.6),
                                                     'flatness':1.0,
                                                     'shadow':1.0 if vrMode else 0.5,
                                                     'scale':0.9 if (env['interfaceType'] == 'small' or vrMode) else 0.7, # FIXME need a node attr for this (smallDeviceExtraScale or something)
                                                     'position':(0,10),
                                                     'vrDepth':-10,
                                                     'text':u'\xa9 2019 Eric Froemling'}))
        self.modpack = bs.NodeActor(bs.newNode('text',
                                              attrs={'vAttach':'bottom',
                                                     'hAlign':'left',
                                                     'color':(1.0,1.0,1.0,1.0) if vrMode else (0.5,0.6,0.5,0.6),
                                                     'flatness':1.0,
                                                     'shadow':1.0 if vrMode else 0.5,
                                                     'scale':0.9 if (env['interfaceType'] == 'phone' or vrMode) else 0.7, # FIXME need a node attr for this (smallDeviceExtraScale or something)
                                                     'position': (-600,10),
                                                     'vrDepth':-10,
                                                     'text':'Modpack created by TheMikirog'}))
        
        # throw up some text that only clients can see so they know that the host is navigating menus
        # while they're just staring at an empty-ish screen..
        self._hostIsNavigatingText = bs.NodeActor(bs.newNode('text',
                                                      attrs={'text':bs.Lstr(resource='hostIsNavigatingMenusText',subs=[('${HOST}',bsInternal._getAccountDisplayString())]),
                                                             'clientOnly':True,
                                                             'position':(0,-200),
                                                             'flatness':1.0,
                                                             'hAlign':'center'}))

        # print 'TEXT IS',self._hostIsNavigatingText.node.text
        if not gDidInitialTransition and hasattr(self,'myName') and hasattr(self,'modpack'):
            bs.animate(self.myName.node,'opacity',{2300:0,3000:1.0})
            bs.animate(self.modpack.node,'opacity',{2300:0,3000:1.0})

        # FIXME - shouldn't be doing things conditionally based on whether the host is vr mode or not
        # (clients may not be or vice versa) - any differences need to happen at the engine level
        # so everyone sees things in their own optimal way
        vrMode = env['vrMode']
        interfaceType = env['interfaceType']

        # in cases where we're doing lots of dev work lets always show the build number
        forceShowBuildNumber = False

        if not bs.getEnvironment().get('toolbarTest',True):
            self.version = bs.NodeActor(bs.newNode('text',
                                                   attrs={'vAttach':'bottom',
                                                          'hAttach':'right',
                                                          'hAlign':'right',
                                                          'flatness':1.0,
                                                          'vrDepth':-10,
                                                          'shadow':1.0 if vrMode else 0.5,
                                                          'color':(1,1,1,1) if vrMode else (0.5,0.6,0.5,0.7),
                                                          'scale':0.9 if (interfaceType == 'small' or vrMode) else 0.7,
                                                          'position':(60,10) if vrMode else (-10,10),
                                                          'text':'Joyride Modpack 2.7 (Dafido Mod v1.2.0)'
                                                   }))
            if not gDidInitialTransition:
                bs.animate(self.version.node,'opacity',{2300:0,3000:1.0})
            
        # throw in beta info..
        self.betaInfo = self.betaInfo2 = None
        #if env['testBuild'] and not env['kioskMode']:
        #    self.betaInfo = bs.NodeActor(bs.newNode('text',
        #                                            attrs={'vAttach':'center',
        #                                                   'hAlign':'center',
        #                                                   'color':(1,1,1,1),
        #                                                   'shadow':0.5,
        #                                                   'flatness':0.5,
        #                                                   'scale':2,
        #                                                   'vrDepth':-60,
        #                                                   'position':(230,125) if env['kioskMode'] else (5,0),
        #                                                   'text':bs.Lstr(resource='testBuildText')
        #                                            }))
        #    if not gDidInitialTransition:
        #        bs.animate(self.betaInfo.node,'opacity',{1300:0,1800:1.0})
        
        modelOpaque = bs.getModel('jrmpSubtextOpaque')
        modelTransparent = bs.getModel('jrmpSubtextTransparent')
        jrmpTex = bs.getTexture('jrmpSubtext')
        jrmpY = 45
        scale = 0.1
        self.jrmpSubtext = bs.NodeActor(bs.newNode('image',
                                             attrs={'position': (5,jrmpY),
                                                    'texture': jrmpTex,
                                                    'scale':(600*scale,600*scale),
                                                    'modelOpaque':modelOpaque,
                                                    'modelTransparent':modelTransparent,
                                                    'attach':"center"}))
                                                    
        # Waving animation
        keyframeDelay = 500
        difference = 3
        timeV = 0
        f = bs.newNode("combine",owner=self.jrmpSubtext.node,attrs={'input0':5,'size':2})
        bs.animate(f,"input1",{0:jrmpY,
                               keyframeDelay:jrmpY-difference,
                               keyframeDelay*2:jrmpY},loop=True)
        f.connectAttr('output',self.jrmpSubtext.node,'position')
        
        # Splash text
        self.splashText = bs.NodeActor(bs.newNode('text',
                                           attrs={'vAttach':'center',
                                                  'vAlign':'bottom',
                                                  'hAlign':'left',
                                                  'color':(0.3,0.8,1,1),
                                                  'shadow':1.0,
                                                  'flatness':0.0,
                                                  'scale':0.8,
                                                  'vrDepth':-60,
                                                  'maxWidth':280,
                                                  'position':(79,200),
                                                  'text':random.choice(bsServerData.splashText)
                                           }))
                                                    
        if not gDidInitialTransition:
            c = bs.newNode("combine",owner=self.jrmpSubtext.node,attrs={"size":2})
            delay = 2000
            keys = {delay:0,delay+100:700*scale,delay+200:600*scale}
            bs.animate(c,"input0",keys)
            bs.animate(c,"input1",keys)
            c.connectAttr("output",self.jrmpSubtext.node,"scale")
            bs.animate(self.splashText.node,"scale",{delay:0,
                                                     delay+200:0.10,
                                                     delay+300:0.95,
                                                     delay+400:0.8})

        model = bs.getModel('thePadLevel')
        treesModel = bs.getModel('trees')
        bottomModel = bs.getModel('thePadLevelBottom')
        testColorTexture = bs.getTexture('thePadLevelColor')
        treesTexture = bs.getTexture('treesColor')

        if timeOfDay == 'day':
            bgTex = bs.getTexture('menu2BG')
            bgModel = bs.getModel('thePadBG')
        elif timeOfDay == 'night':
            bgTex = bs.getTexture('nightBG')
            bgModel = bs.getModel('thePadBG')
        elif timeOfDay == 'morning':
            bgTex = bs.getTexture('sunnyBG')
            bgModel = bs.getModel('thePadBG')
        elif timeOfDay == 'evening':
            bgTex = bs.getTexture('mushFeudSky')
            bgModel = bs.getModel('skysphere')
        else:
            bgTex = bs.getTexture('menu2BG')
            bgModel = bs.getModel('thePadBG')

        # (load these last since most platforms don't use them..)
        vrBottomFillModel = bs.getModel('thePadVRFillBottom')
        vrTopFillModel = bs.getModel('thePadVRFillTop')
        
        bsGlobals = bs.getSharedObject('globals')
        
        bsGlobals.cameraMode = 'rotate'

        if False:
            node = bs.newNode('timeDisplay',
                              attrs={'timeMin':2000,
                                     'timeMax':10000,
                                     'showSubSeconds':True})
            self._fooText = bs.NodeActor(bs.newNode('text',
                                                    attrs={'position':(500,-220),
                                                           'flatness':1.0,
                                                           'hAlign':'center'}))
            bsGlobals.connectAttr('gameTime',node,'time2')
            node.connectAttr('output',self._fooText.node,'text')
        
        if timeOfDay == 'day':
            tint = (1.1,1.11,1.14)
            bsGlobals.tint = tint
                
            bsGlobals.ambientColor = (1.05,1.06,1.08)
            bsGlobals.vignetteOuter = (0.55,0.55,0.62)
            bsGlobals.vignetteInner = (0.97,0.97,0.99)
        elif timeOfDay == 'night':
            tint = (0.35,0.35,0.8)
            bsGlobals.tint = tint
                
            bsGlobals.ambientColor = (0.51,0.71,0.97)
            bsGlobals.vignetteOuter = (0.8,0.8,0.9)
            bsGlobals.vignetteInner = (1.0,1.0,1.1)
        elif timeOfDay == 'morning':
            tint = (1.1,1.0,0.9)
            bsGlobals.tint = tint
                
            bsGlobals.ambientColor = (1.05,1.06,0.8)
            bsGlobals.vignetteOuter = (0.6,0.55,0.4)
            bsGlobals.vignetteInner = (0.99,0.95,0.9)
        elif timeOfDay == 'evening':
            tint = (0.8,0.8,1.14)
            bsGlobals.tint = tint
                
            bsGlobals.ambientColor = (1.0,1.0,1.1)
            bsGlobals.vignetteOuter = (0.55,0.55,0.62)
            bsGlobals.vignetteInner = (0.95,0.9,0.9)
        else:
            tint = (1.1,1.11,1.14)
            bsGlobals.tint = tint
                
            bsGlobals.ambientColor = (1.05,1.06,1.08)
            bsGlobals.vignetteOuter = (0.55,0.55,0.62)
            bsGlobals.vignetteInner = (0.97,0.97,0.99)

        self.bottom = bs.NodeActor(bs.newNode('terrain',
                                              attrs={'model':bottomModel,
                                                     'lighting':False,
                                                     'reflection':'soft',
                                                     'reflectionScale':[0.45],
                                                     'colorTexture':testColorTexture}))
        self.vrBottomFill = bs.NodeActor(bs.newNode('terrain',
                                                    attrs={'model':vrBottomFillModel,
                                                           'lighting':False,
                                                           'vrOnly':True,
                                                           'colorTexture':testColorTexture}))
        self.vrTopFill = bs.NodeActor(bs.newNode('terrain',
                                                 attrs={'model':vrTopFillModel,
                                                        'vrOnly':True,
                                                        'lighting':False,
                                                        'colorTexture':bgTex}))
        self.terrain = bs.NodeActor(bs.newNode('terrain',
                                               attrs={'model':model,
                                                      'colorTexture':testColorTexture,
                                                      'reflection':'soft',
                                                      'reflectionScale':[0.3]}))
                            

        self.trees = bs.NodeActor(bs.newNode('terrain',
                                             attrs={'model':treesModel,
                                                    'lighting':False,
                                                    'reflection':'char',
                                                    'reflectionScale':[0.1],
                                                    'colorTexture':treesTexture}))

        self.bg = bs.NodeActor(bs.newNode('terrain',
                                          attrs={'model':bgModel,
                                                 'color':(0.92,0.91,0.9),
                                                 'lighting':False,
                                                 'background':True,
                                                 'colorTexture':bgTex}))
        textOffsetV = 0
        self._ts = 0.86

        self._language = None
        self._updateTimer = bs.Timer(1000, self._update, repeat=True)
        self._update()

        # hopefully this won't hitch but lets space these out anyway..
        bsInternal._addCleanFrameCallback(bs.WeakCall(self._startPreloads))

        random.seed()

        # on the main menu, also show our news..
        class News(object):
            
            def __init__(self,activity):
                self._valid = True

                self._messageDuration = 10000
                self._messageSpacing = 2000
                self._text = None
                self._activity = weakref.ref(activity)

                # if we're signed in, fetch news immediately.. otherwise wait until we are signed in
                self._fetchTimer = bs.Timer(1000,bs.WeakCall(self._tryFetchingNews),repeat=True)
                self._tryFetchingNews()

            # we now want to wait until we're signed in before fetching news
            def _tryFetchingNews(self):
                if bsInternal._getAccountState() == 'SIGNED_IN':
                    self._fetchNews()
                    self._fetchTimer = None
                
            def _fetchNews(self):
                try: launchCount = bs.getConfig()['launchCount']
                except Exception: launchCount = None
                global gLastNewsFetchTime
                gLastNewsFetchTime = time.time()
                
                #bsUtils.serverGet('bsNews',{'v':'2','lc':launchCount,'b':bs.getEnvironment()['buildNumber'],'t':int(gLastNewsFetchTime-gStartTime)},bs.WeakCall(self._gotNews))
                env = bs.getEnvironment()
                bsInternal._newsQuery(args={'v':2,'lc':launchCount,'t':int(gLastNewsFetchTime-gStartTime),'p':env['platform'],'sp':env['subplatform']},callback=bs.WeakCall(self._gotNews))

            def _changePhrase(self):

                global gLastNewsFetchTime
                
                # if our news is way out of date, lets re-request it.. otherwise, rotate our phrase
                if time.time()-gLastNewsFetchTime > 600.0:
                    self._fetchNews()
                    self._text = None
                else:
                    if self._text is not None:
                        if len(self._phrases) == 0:
                            for p in self._usedPhrases:
                                self._phrases.insert(0,p)
                        val = self._phrases.pop()
                        if val == '__ACH__':
                            vr = bs.getEnvironment()['vrMode']
                            bsUtils.Text(bs.Lstr(resource='nextAchievementsText'),
                                         color=(1,1,1,1) if vr else (0.95,0.9,1,0.4),
                                         hostOnly=True,
                                         maxWidth=200,
                                         position=(-300, -35),
                                         hAlign='right',
                                         transition='fadeIn',
                                         scale=0.9 if vr else 0.7,
                                         flatness=1.0 if vr else 0.6,
                                         shadow=1.0 if vr else 0.5,
                                         hAttach="center",
                                         vAttach="top",
                                         transitionDelay=1000,
                                         transitionOutDelay=self._messageDuration).autoRetain()
                            import bsAchievement
                            achs = [a for a in bsAchievement.gAchievements if not a.isComplete()]
                            if len(achs) > 0:
                                a = achs.pop(random.randrange(min(4,len(achs))))
                                a.createDisplay(-180,-35,1000,outDelay=self._messageDuration,style='news')
                            if len(achs) > 0:
                                a = achs.pop(random.randrange(min(8,len(achs))))
                                a.createDisplay(180,-35,1250,outDelay=self._messageDuration,style='news')
                        else:
                            s = self._messageSpacing
                            keys = {s:0,s+1000:1.0,s+self._messageDuration-1000:1.0,s+self._messageDuration:0.0}
                            bs.animate(self._text.node,"opacity",dict([[k,v] for k,v in keys.items()]))
                            self._text.node.text = val

            def _gotNews(self,data):
                
                # run this stuff in the context of our activity since we need to make nodes and stuff..
                # we should fix the serverGet call so it 
                activity = self._activity()
                if activity is None or activity.isFinalized(): return
                with bs.Context(activity):
                
                    if data is None: return
                    news = str(data['news'])
                    #news = data['news']

                    # our news data now starts with 'BSNews:' so we can filter out
                    # result that arent actually coming in from our server
                    # (such as wireless access point setup pages)
                    if not news.startswith("BSNews:"): return
                    news = news[7:]
                    # if news == '' or not self._valid: return
                    self._phrases = []
                    # show upcoming achievements in non-vr versions
                    # (currently too hard to read in vr)
                    self._usedPhrases = (['__ACH__'] if not bs.getEnvironment()['vrMode'] else []) + [s for s in news.split('<br>\r\n') if s != '']
                    self._phraseChangeTimer = bs.Timer(self._messageDuration+self._messageSpacing,bs.WeakCall(self._changePhrase),repeat=True)

                    sc = 1.2 if (bs.getEnvironment()['interfaceType'] == 'small' or bs.getEnvironment()['vrMode']) else 0.8

                    self._text = bs.NodeActor(bs.newNode('text',
                                                         attrs={'vAttach':'top',
                                                                'hAttach':'center',
                                                                'hAlign':'center',
                                                                'vrDepth':-20,
                                                                'shadow':1.0 if bs.getEnvironment()['vrMode'] else 0.4,
                                                                'flatness':0.8,
                                                                'vAlign':'top',
                                                                'color':(1,1,1,1) if bs.getEnvironment()['vrMode'] else (0.7,0.65,0.75,1.0),
                                                                'scale':sc,
                                                                'maxWidth':900.0/sc,
                                                                'position':(0,-10)}))
                    self._changePhrase()
                    
        if not env['kioskMode'] and not env.get('toolbarTest',True):
            self._news = News(self)

        # bring up the last place we were at, or start at the main menu otherwise
        with bs.Context('UI'):
            try: mainWindow = bsUI.gMainWindow
            except Exception: mainWindow = None

            # when coming back from a kiosk-mode game, jump to the kiosk start screen..
            if bsUtils.gRunningKioskModeGame:
                bsUI.uiGlobals['mainMenuWindow'] = bsUI.KioskWindow().getRootWidget()
            # ..or in normal cases go back to the main menu
            else:
                if mainWindow == 'Gather': bsUI.uiGlobals['mainMenuWindow'] = bsUI.GatherWindow(transition=None).getRootWidget()
                elif mainWindow == 'Watch': bsUI.uiGlobals['mainMenuWindow'] = bsUI.WatchWindow(transition=None).getRootWidget()
                elif mainWindow == 'Team Game Select': bsUI.uiGlobals['mainMenuWindow'] = bsUI.TeamsWindow(sessionType=bs.TeamsSession,transition=None).getRootWidget()
                elif mainWindow == 'Free-for-All Game Select': bsUI.uiGlobals['mainMenuWindow'] = bsUI.TeamsWindow(sessionType=bs.FreeForAllSession,transition=None).getRootWidget()
                elif mainWindow == 'Coop Select': bsUI.uiGlobals['mainMenuWindow'] = bsUI.CoopWindow(transition=None).getRootWidget()
                else: bsUI.uiGlobals['mainMenuWindow'] = bsUI.MainMenuWindow(transition=None).getRootWidget()

                # attempt to show any pending offers immediately.  If that doesn't work, try again in a few seconds (we may not have heard back from the server)
                # ..if that doesn't work they'll just have to wait until the next opportunity.
                if not bsUI._showOffer():
                    def tryAgain():
                        if not bsUI._showOffer():
                            bs.realTimer(2000,bsUI._showOffer) # try one last time..
                    bs.realTimer(2000,tryAgain)
                bs.realTimer(1000,bsUI._showHowToPlay)
            
        gDidInitialTransition = True

    def _update(self):

        # update logo in case it changes..
        if self._logoNode is not None and self._logoNode.exists():
            customTexture = self._getCustomLogoTexName()
            if customTexture != self._customLogoTexName:
                self._customLogoTexName = customTexture
                self._logoNode.texture = bs.getTexture(customTexture if customTexture is not None else 'logo')
                self._logoNode.modelOpaque = None if customTexture is not None else bs.getModel('logo')
                self._logoNode.modelTransparent = None if customTexture is not None else bs.getModel('logoTransparent')
        
        # if language has changed, recreate our logo text/graphics
        l = bs.getLanguage()
        if l != self._language:
            self._language = l

            env = bs.getEnvironment()

            
            y = 20
            gScale = 1.1
            self._wordActors = []
            baseDelay = 1000
            delay = baseDelay
            delayInc = 20

            # come on faster after the first time
            if gDidInitialTransition:
                baseDelay = 0
                delay = baseDelay
                delayInc = 20

                
            # we draw higher in kiosk mode (make sure to test this when making adjustments)
            # for now we're hard-coded for a few languages.. should maybe look into generalizing this?..
            baseX = -170
            x = baseX-20
            spacing = 55*gScale
            yExtra = 80 if env['kioskMode'] else 0

            x1 = x
            delay1 = delay
            for shadow in (True, False):
                x = x1
                delay = delay1
                self._makeWord('B',x-50,y-23+0.8*yExtra,scale=1.3*gScale,delay=delay,vrDepthOffset=3,shadow=shadow)
                x += spacing; delay += delayInc
                self._makeWord('m',x,y+yExtra,delay=delay,scale=gScale,shadow=shadow)
                x += spacing*1.25; delay += delayInc
                self._makeWord('b',x,y+yExtra,delay=delay,scale=gScale,vrDepthOffset=5,shadow=shadow)
                x += spacing*0.85; delay += delayInc

                self._makeWord('S',x,y-16+0.8*yExtra,scale=1.3*gScale,delay=delay,vrDepthOffset=14,shadow=shadow)
                x += spacing; delay += delayInc
                self._makeWord('q',x,y+yExtra,delay=delay,scale=gScale,shadow=shadow)
                x += spacing*0.9; delay += delayInc
                self._makeWord('u',x,y+yExtra,delay=delay,scale=gScale,vrDepthOffset=7,shadow=shadow)
                x += spacing*0.9; delay += delayInc
                self._makeWord('a',x,y+yExtra,delay=delay,scale=gScale,shadow=shadow)
                x += spacing*0.95; delay += delayInc
                self._makeWord('d',x,y+yExtra,delay=delay,scale=gScale,vrDepthOffset=6,shadow=shadow)

            self._makeLogo(baseX-28,125+y+1.2*yExtra,0.32*gScale,delay=baseDelay)

                

    def _makeWord(self, word, x, y, scale=1.0, delay=0, vrDepthOffset=0, shadow=False):

        if shadow:
            wordShadowObj = bs.NodeActor(bs.newNode('text',
                                                    attrs={'position':(x,y),
                                                           'big':True,
                                                           'color':(0.0,0.0,0.2,0.08),
                                                           'tiltTranslate':0.09,
                                                           'opacityScalesShadow':False,
                                                           'shadow':0.2,
                                                           'vrDepth':-130,
                                                           'vAlign':'center',
                                                           'projectScale':0.97*scale,
                                                           'scale':1.0,
                                                           'text':word}))
            self._wordActors.append(wordShadowObj)
        else:
            wordObj = bs.NodeActor(bs.newNode('text',
                                              attrs={'position':(x,y),
                                                     'big':True,
                                                     'color':(1.2,1.15,1.15,1.0),
                                                     'tiltTranslate':0.11,
                                                     'shadow':0.2,
                                                     'vrDepth':-40+vrDepthOffset,
                                                     'vAlign':'center',
                                                     'projectScale':scale,
                                                     'scale':1.0,
                                                     'text':word}))
            self._wordActors.append(wordObj)


        # add a bit of stop-motion-y jitter to the logo
        # (unless we're in VR mode in which case its best to leave things still)
        if not bs.getEnvironment()['vrMode']:
            if not shadow: c = bs.newNode("combine",owner=wordObj.node,attrs={'size':2})
            else: c = None
            if shadow: c2 = bs.newNode("combine",owner=wordShadowObj.node,attrs={'size':2})
            else: c2 = None
                
            if not shadow:
                c.connectAttr('output',wordObj.node,'position')
            if shadow:
                c2.connectAttr('output',wordShadowObj.node,'position')
            keys = {}
            keys2 = {}
            timeV = 0
            for i in range(10):
                val = x+(random.random()-0.5)*0.8
                val2 = x+(random.random()-0.5)*0.8
                keys[timeV*self._ts] = val
                keys2[timeV*self._ts] = val2+5
                timeV += random.random() * 100
            if c is not None: bs.animate(c,"input0",keys,loop=True)
            if c2 is not None: bs.animate(c2,"input0",keys2,loop=True)
            keys = {}
            keys2 = {}
            timeV = 0
            for i in range(10):
                val = y+(random.random()-0.5)*0.8
                val2 = y+(random.random()-0.5)*0.8
                keys[timeV*self._ts] = val
                keys2[timeV*self._ts] = val2-9
                timeV += random.random() * 100
            if c is not None: bs.animate(c,"input1",keys,loop=True)
            if c2 is not None: bs.animate(c2,"input1",keys2,loop=True)

        if not shadow:
            bs.animate(wordObj.node,"projectScale",{delay:0.0, delay+100:scale*1.1, delay+200:scale})
        else:
            bs.animate(wordShadowObj.node,"projectScale",{delay:0.0, delay+100:scale*1.1, delay+200:scale})

    def _getCustomLogoTexName(self):
        return 'logoJRMP'
                
        
    # pop the logo and menu in
    def _makeLogo(self, x, y, scale, delay, customTexture=None, jitterScale=1.0, rotate=0, vrDepthOffset=0):
        # temp easter googness
        if customTexture is None:
            customTexture = self._getCustomLogoTexName()
        self._customLogoTexName = customTexture
        logo = bs.NodeActor(bs.newNode('image',
                                             attrs={'texture': bs.getTexture(customTexture if customTexture is not None else 'logo'),
                                                    'modelOpaque':None if customTexture is not None else bs.getModel('logo'),
                                                    'modelTransparent':None if customTexture is not None else bs.getModel('logoTransparent'),
                                                    'vrDepth':-10+vrDepthOffset,
                                                    'rotate':rotate,
                                                    'attach':"center",
                                                    'tiltTranslate':0.21,
                                                    'absoluteScale':True}))
        self._logoNode = logo.node
        self._wordActors.append(logo)

        # add a bit of stop-motion-y jitter to the logo
        # (unless we're in VR mode in which case its best to leave things still)
        if not bs.getEnvironment()['vrMode']:
            c = bs.newNode("combine",owner=logo.node,attrs={'size':2})
            c.connectAttr('output',logo.node,'position')

            keys = {}
            timeV = 0
            # gen some random keys for that stop-motion-y look
            for i in range(10):
                keys[timeV] = x+(random.random()-0.5)*0.7*jitterScale
                timeV += random.random() * 100
            bs.animate(c,"input0",keys,loop=True)
            keys = {}
            timeV = 0
            for i in range(10):
                keys[timeV*self._ts] = y+(random.random()-0.5)*0.7*jitterScale
                timeV += random.random() * 100
            bs.animate(c,"input1",keys,loop=True)
        else:
            logo.node.position = (x,y)

        c = bs.newNode("combine",owner=logo.node,attrs={"size":2})

        keys = {delay:0,delay+100:700*scale,delay+200:600*scale}
        bs.animate(c,"input0",keys)
        bs.animate(c,"input1",keys)
        c.connectAttr("output",logo.node,"scale")
            
    def _startPreloads(self):
        # FIXME - the func that calls us back doesn't save/restore state
        # or check for a dead activity so we have to do that ourself..
        if self.isFinalized(): return
        with bs.Context(self): _preload1()

        if timeOfDay in ['evening','night']: music = 'Menu Night'
        else: music = 'Menu'
        bs.gameTimer(500,lambda: bs.playMusic(music))
        
        
# a second or two into the main menu is a good time to preload some stuff we'll need elsewhere
# to avoid hitches later on..
def _preload1():
    for m in ['plasticEyesTransparent','playerLineup1Transparent','playerLineup2Transparent',
              'playerLineup3Transparent','playerLineup4Transparent','angryComputerTransparent',
              'scrollWidgetShort','windowBGBlotch']: bs.getModel(m)
    for t in ["playerLineup","lock"]: bs.getTexture(t)
    for tex in ['iconRunaround','iconOnslaught',
                'medalComplete','medalBronze','medalSilver',
                'medalGold','characterIconMask']: bs.getTexture(tex)

    bs.getTexture("bg")

    bs.Powerup.getFactory()

    bs.gameTimer(100,_preload2)

def _preload2():

    # FIXME - could integrate these loads with the classes that use them
    # so they don't have to redundantly call the load (even if the actual result is cached)
    for m in ["powerup","powerupSimple"]: bs.getModel(m)
    for t in ["powerupBomb","powerupBlast","powerupDynamitePack","powerupCurse",
              "powerupCombatBombs","powerupCake","powerupSpeed","powerupPunch",
              "powerupFireBombs","powerupGrenade","powerupHealBombs","powerupHijump",
              "powerupKnockerBombs","powerupOverdrive","powerupRangerBombs",
              "powerupIceBombs","powerupStickyBombs","powerupShield",
              "powerupImpactBombs","powerupHealth","powerupGlueBombs","powerupMagnet"]: bs.getTexture(t)
    for s in ["powerup01","overdrivePowerup","boxDrop","boxingBell","scoreHit01",
              "scoreHit02","dripity","spawn","gong"]: bs.getSound(s)

    bs.Bomb.getFactory()

    bs.gameTimer(100,_preload3)

def _preload3():

    for m in ["bomb","bombBasketball","bombGrenade","bombHealing",
              "bombKnocker","bombRanger","bombSticky","combatBomb",
              "dizzyCake","dynamitePack","landMine","impactBomb",
              "bombMagnet","bombGlue"]: bs.getModel(m)
    for t in ["bombColor","bombColorIce","bombStickyColor",
              "impactBombColor","impactBombColorLit","magnetBombColor"]: bs.getTexture(t)
    for s in ["freeze","fuse01","activateBeep","warnBeep",
              "combatBombDeployed","combatBombReady","fuseDynamite","dizzyCakePull","dizzyCakeImpact",
              "hijump"]: bs.getSound(s)

    spazFactory = bs.Spaz.getFactory()

    # go through and load our existing spazzes
    # (spread these out quite a bit)
    def _load(spaz):
        spazFactory._preload(spaz)
        # icons also..
        bs.getTexture(bsSpaz.appearances[spaz].iconTexture)
        bs.getTexture(bsSpaz.appearances[spaz].iconMaskTexture)

    # FIXME - need to come up with a standin texture mechanism or something
    # ..preloading won't scale too much farther..
    t = 50
    # for spaz in bsSpaz.appearances:
    #     bs.gameTimer(t,bs.Call(_load,spaz))
    #     t += 100

    bs.gameTimer(200,_preload4)


def _preload4():
    # bs.playMusic('Menu')

    for t in ['bar','meter',
              'null','flagColor','achievementOutline']: bs.getTexture(t)
    for m in ['frameInset','meterTransparent','achievementOutline']: bs.getModel(m)
    for s in ['metalHit','metalSkid','refWhistle','achievement']: bs.getSound(s)

    bs.Flag.getFactory()
    bs.Powerup.getFactory()

class SplashScreenActivity(bs.Activity):

    def __init__(self,settings={}):
        bs.Activity.__init__(self,settings)
        self._part1Duration = 4000
        self._tex = bs.getTexture('aliSplash')
        self._tex2 = bs.getTexture('aliControllerQR')
        
    def _startPreloads(self):
        # FIXME - the func that calls us back doesn't save/restore state
        # or check for a dead activity so we have to do that ourself..
        if self.isFinalized(): return
        with bs.Context(self): _preload1()
        
    def onTransitionIn(self):
        import bsInternal
        bs.Activity.onTransitionIn(self)
        bsInternal._addCleanFrameCallback(bs.WeakCall(self._startPreloads))
        self._background = bsUtils.Background(fadeTime=500, startFaded=True, showLogo=False)
        self._part = 1
        self._image = bsUtils.Image(self._tex, transition='fadeIn', modelTransparent=bs.getModel('image4x1'), scale=(800, 200), transitionDelay=500, transitionOutDelay=self._part1Duration-1300)
        bs.gameTimer(self._part1Duration, self.end)

    def _startPart2(self):
        if self._part != 1: return
        self._part = 2
        self._image = bsUtils.Image(self._tex2, transition='fadeIn', scale=(400, 400), transitionDelay=0)
        t = bsUtils._translate('tips','If you are short on controllers, install the \'${REMOTE_APP_NAME}\' app\n'
                               'on your mobile devices to use them as controllers.')
        t = t.replace('${REMOTE_APP_NAME}',bsUtils._getRemoteAppName())
        self._text = bsUtils.Text(t,
                                  maxWidth=900,
                                  hAlign='center',
                                  vAlign='center',
                                  position=(0,270),
                                  color=(1,1,1,1),
                                  transition='fadeIn')
        
    def onSomethingPressed(self):
        self.end()

gFirstRun = True

class MainMenuSession(bs.Session):

    def __init__(self):
        bs.Session.__init__(self)

        self._locked = False
        
        # update Discord Rich Presence
        import richPresence
        richPresence.discordMenu()
        
        self.setActivity(bs.newActivity(MainMenuActivity))

    def onActivityEnd(self,activity,results):
        if self._locked:
            bsInternal._unlockAllInput()
        # any ending activity leads us into the main menu one..
        self.setActivity(bs.newActivity(MainMenuActivity))
        
    def onPlayerRequest(self,player):
        
        # reject player requests, but if we're in a splash-screen, take the opportunity to tell it to leave
        # FIXME - should add a blanket way to capture all input for cases like this
        activity = self.getActivity()
        if isinstance(activity, SplashScreenActivity):
            with bs.Context(activity): activity.onSomethingPressed()
            
        return False

