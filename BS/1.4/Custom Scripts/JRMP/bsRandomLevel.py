import bs
import bsInternal
import bsGame
import random
import math
import weakref

def bsGetAPIVersion():
    return 4
    
def bsGetLevels():
    return [bs.Level('RandomizedLevel',
            displayName='${GAME}',
            gameType=RandomizedLevel,
            settings={},
            previewTexName='courtyardPreview')]
            
def bsGetGames():
    return [RandomizedLevel]

class RandomizedLevel(bs.CoopGameActivity):


    @classmethod
    def getName(cls):
        return 'Randomized Level'

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
        bs.playMusic(random.choice(['Last Stand','Epic','FlagBomber','FlagSlip','FlagCatcher','FlagDropper','FlagRunner','Onslaught','Flying','Marching','Nightmare','Marathon','JRMP Onslaught','Where Eagles Dare','Toilet','Spy Brothers','Cardboard']))

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
        
        
        def levelGen():
        
            # try getting the time from an online server
            # if that fails, use device time
            
            firstWord = [['Concrete','gray'],
                         ['Misty','gray'],
                         ['Patient','gray'],
                         ['Scrappy','gray'],
                         ['Sharpened','gray'],
                         ['Unknown','gray'],
                         ['Crescent','gray'],
                         ['Convenient','gray'],
                         ['Foggy','white'],
                         ['Forbidden','white'],
                         ['Truncated','white'],
                         ['Locked','white'],
                         ['Broken','white'],
                         ['Wrathful','white'],
                         ['Hasty','white'],
                         ['Playful','white'],
                         ['Universal','navy'],
                         ['Twilight','navy'],
                         ['Midnight','navy'],
                         ['Lunatic','navy'],
                         ['Happy','navy'],
                         ['Intrepid','navy'],
                         ['Heartless','navy'],
                         ['Intense','navy'],
                         ['Snowy','blue'],
                         ['Breezy','blue'],
                         ['Cold','blue'],
                         ['Haily','blue'],
                         ['Calm','blue'],
                         ['Aerial','blue'],
                         ['Oceanic','blue'],
                         ['Slowed','blue'],
                         ['Tactical','yellow'],
                         ['Epic','yellow'],
                         ['Sunny','yellow'],
                         ['Focused','yellow'],
                         ['Sandy','yellow'],
                         ['Odd','yellow'],
                         ['Abrasive','yellow'],
                         ['Warped','yellow'],
                         ['Wonderful','purple'],
                         ['Mystical','purple'],
                         ['Magical','purple'],
                         ['Special','purple'],
                         ['Sparkly','purple'],
                         ['Euphoric','purple'],
                         ['Supernatural','purple'],
                         ['Forgotten','purple'],
                         ['Tricky','purple'],
                         ['Lovely','purple'],
                         ['Sweet','purple'],
                         ['Beautiful','purple'],
                         ['Extraordinary','green'],
                         ['Poison','green'],
                         ['Flabby','green'],
                         ['Lucky','green'],
                         ['Careful','green'],
                         ['Ruinous','green'],
                         ['Strong','green'],
                         ['Glossy','green'],
                         ['Violent','green'],
                         ['Stunted','green'],
                         ['Lurid','red'],
                         ['Hellish','red'],
                         ['Smoldered','red'],
                         ['Spicy','red'],
                         ['Warm','red'],
                         ['Exotic','red'],
                         ['Sizzling','red'],
                         ['Unsure','red'],
                         ['Hazard','red'],
                         ['Angry','red'],
                         ['Joyful','red'],
                         ['Diluted','black'],
                         ['Inky','black'],
                         ['Hazy','black'],
                         ['Blind','black'],
                         ['Dusky','black'],
                         ['Futile','black'],
                         ['Concealed','black'],
                         ['Redacted','black'],
                         ['Level Headed','default'],
                         ['Crazy','default'],
                         ['Ordinary','default'],
                         ['Classic','default'],
                         ['Competitive','default'],
                         ['Strategic','default'],
                         ['Invalid','default'],
                         ['Savage','default'],
                         ['Plain','default'],
                         ['Tough','default'],
                         ['Average','default']]
            firstWordChoice = random.choice(firstWord)
            
            if firstWordChoice[1] == 'default': color = (1.2,1.17,1.1)
            elif firstWordChoice[1] == 'gray': color = (0.85,0.85,0.85)
            elif firstWordChoice[1] == 'white': color = (1.35,1.35,1.35)
            elif firstWordChoice[1] == 'navy': color = (0.5,0.7,1.0)
            elif firstWordChoice[1] == 'black': color = (0.63,0.64,0.65)
            elif firstWordChoice[1] == 'blue': color = (1.1,1.2,1.4)
            elif firstWordChoice[1] == 'yellow': color = (1.1,1.1,0.7)
            elif firstWordChoice[1] == 'purple': color = (1.1,0.9,1.25)
            elif firstWordChoice[1] == 'green': color = (1.05,1.2,1.0)
            elif firstWordChoice[1] == 'red': color = (1.3,1.05,1.05)
            bs.getSharedObject('globals').tint = color
                               
            secondWord = ['Mayhem','Chaos','Mess','Pizza','Oatmeal','Lagoon','Navy','Overturn','Trap','Fun','Snap','Surprise','Fright','Spot','Face-off','Conflict',
                          'Meatballs','Arena','Limbo','Eye','Box','Consequences','Approachment','Party','Match','Zone','Show','Quest','Result','Warfare',
                          'Completion','Trip','Outskirts','Battle','War','Skirmish','Brawl','Road','Stage','Snake','Rampage','Match','Petals','Nature','Clash',
                          'Fight','Challenge','Contest','Hustle','Combat','Bingo','Place','Land','Time','Ivy','Explosions','Duel','Storm','Attack']
            
            self._waveName = firstWordChoice[0] + ' ' + random.choice(secondWord)
            
            self.mt = '1'
            if self.mt == '1':
                botPF = []
                botF = []
                botT = []
                if firstWordChoice[0] == 'Concrete':
                    botF = [bs.ChickBot,bs.ToughGuyBot,bs.BearBot,bs.BomberBot,bs.KnightBot]
                    botPF = [bs.ChickBotPro,bs.ToughGuyBotPro,bs.BearBotShielded,bs.BomberBotPro,bs.KnightBotPro]
                    botT = [bs.BomberBotStatic,bs.CyborgBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Misty':
                    botF = [bs.NinjaBot,bs.AgentBot,bs.LooieBot,bs.ToughGuyBot,bs.BomberBot]
                    botPF = [bs.NinjaBot,bs.AgentBotPro,bs.LooieBotShielded,bs.BomberBotPro]
                    botT = [bs.BomberBotStatic,bs.ChickBot,bs.KlayBotStatic]
                elif firstWordChoice[0] == 'Patient':
                    botF = [bs.BonesBot,bs.SpyBot,bs.ChickBot,bs.ZillBot,bs.AliBot]
                    botPF = [bs.BonesBotPro,bs.ChickBotPro,bs.ZillBotPro,bs.AliBotPro]
                    botT = [bs.MelBot,bs.BomberBotStatic]
                elif firstWordChoice[0] == 'Scrappy':
                    botF = [bs.PuckBot,bs.CyborgBot,bs.PixelBot,bs.BunnyBot,bs.PirateBot]
                    botPF = [bs.CyborgBotPro,bs.PixelBotPro,bs.BunnyBotShielded,bs.PirateBotShielded]
                    botT = [bs.BomberBotProStatic,bs.BomberBotStatic,bs.PixelBotStatic]
                elif firstWordChoice[0] == 'Sharpened':
                    botF = [bs.PuckBot,bs.ZillBot,bs.CyborgBot,bs.BearBot,bs.ChickBot]
                    botPF = [bs.CyborgBotPro,bs.ZillBotPro,bs.BearBotShielded,bs.ChickBotPro]
                    botT = [bs.ChickBotStatic,bs.FrostyBotStatic]
                elif firstWordChoice[0] == 'Unknown':
                    botF = [bs.JuiceBot,bs.NinjaBot,bs.JesterBot,bs.KlayBot,bs.SpyBot]
                    botPF = [bs.NinjaBotPro,bs.SpyBotPro,bs.KlayBotPro]
                    botT = [bs.KlayBotStatic,bs.MelBotStatic,bs.CyborgBotStatic]
                elif firstWordChoice[0] == 'Crescent':
                    botF = [bs.PirateBot,bs.PixelBot,bs.ToughGuyBot,bs.AgentBot]
                    botPF = [bs.PirateBotNoTimeLimit,bs.PixelBotPro,bs.ToughGuyBot,bs.AgentBotPro]
                    botT = [bs.BomberBotProStatic,bs.CyborgBotStatic]
                elif firstWordChoice[0] == 'Convenient':
                    botF = [bs.AliBot,bs.DiceBot,bs.PuckBot,bs.ToughGuyBot,bs.CowBot]
                    botPF = [bs.AliBotPro,bs.ToughGuyBotPro,bs.CowBotShielded]
                    botT = [bs.BomberBotStatic,bs.CowBotStatic,bs.PixelBotStatic]
                elif firstWordChoice[0] == 'Foggy':
                    botF = [bs.PascalBot,bs.NinjaBot,bs.BearBot,bs.DemonBot]
                    botPF = [bs.PascalBotShielded,bs.NinjaBotPro,bs.BearBotShielded]
                    botT = [bs.BomberBotStatic,bs.CowBotStatic,bs.PixelBotStatic]
                elif firstWordChoice[0] == 'Forbidden':
                    botF = [bs.JuiceBot,bs.BonesBot,bs.LooieBot,bs.WizardBot,bs.NinjaBot]
                    botPF = [bs.BonesBotPro,bs.LooieBotShielded,bs.WizardBotPro,bs.NinjaBotPro]
                    botT = [bs.WizardBotStatic]
                elif firstWordChoice[0] == 'Truncated':
                    botF = [bs.MelBot,bs.CowBot,bs.FrostyBot,bs.AliBot,bs.KnightBot]
                    botPF = [bs.MelDuperBot,bs.CowBotShielded,bs.FrostyBotPro,bs.KnightBotPro]
                    botT = [bs.MelBotStatic,bs.CowBotStatic]
                elif firstWordChoice[0] == 'Locked':
                    botF = [bs.MelBot,bs.AgentBot,bs.SantaBot,bs.KnightBot,bs.AliBot,bs.PirateBot,bs.ToughGuyBot]
                    botPF = [bs.MelDuperBot,bs.AgentBotPro,bs.AliBot,bs.PirateBotShielded,bs.KnightBotPro]
                    botT = [bs.MelBotStatic,bs.ChickBotStatic,bs.CowBotStatic]
                elif firstWordChoice[0] == 'Broken':
                    botF = [bs.PixelBot,bs.BunnyBot,bs.RonnieBot,bs.KlayBot,bs.SpyBot]
                    botPF = [bs.PixelBotPro,bs.BunnyBotShielded,bs.KlayBotPro,bs.SpyBotPro]
                    botT = [bs.ChickBotStatic,bs.PixelBotStatic,bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Wrathful':
                    botF = [bs.ToughGuyBot,bs.AgentBot,bs.CyborgBot,bs.ChickBot,bs.MelBot,bs.BunnyBot]
                    botPF = [bs.ToughGuyBotPro,bs.AgentBotPro,bs.CyborgBotPro,bs.MelDuperBot,bs.BunnyBotShielded]
                    botT = [bs.ChickBotStatic,bs.CyborgBotStatic,bs.MelBotStatic]
                elif firstWordChoice[0] == 'Hasty':
                    botF = [bs.AliBot,bs.PirateBot,bs.KnightBot,bs.NinjaBot,bs.LooieBot]
                    botPF = [bs.AliBotPro,bs.PirateBotRadius,bs.KnightBotPro,bs.LooieBotShielded]
                    botT = [bs.BomberBotProStatic,bs.BomberBotStatic]
                elif firstWordChoice[0] == 'Playful':
                    botF = [bs.BonesBot,bs.NinjaBot,bs.RonnieBot,bs.JesterBot,bs.BunnyBot,bs.AgentBot]
                    botPF = [bs.BonesBotPro,bs.NinjaBotPro,bs.BunnyBotShielded,bs.AgentBotPro]
                    botT = [bs.BomberBotProStatic,bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Universal':
                    botF = [bs.BearBot,bs.PixelBot,bs.RonnieBot,bs.JuiceBot,bs.LooieBot]
                    botPF = [bs.BearBotShielded,bs.PixelBotPro,bs.LooieBotPro]
                    botT = [bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Twilight':
                    botF = [bs.WizardBot,bs.PascalBot,bs.NinjaBot,bs.SpyBot]
                    botPF = [bs.WizardBotPro,bs.PascalBotShielded,bs.NinjaBotPro,bs.SpyBotPro]
                    botT = [bs.WizardBotStatic,bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Midnight':
                    botF = [bs.NinjaBot,bs.AgentBot,bs.ToughGuyBot,bs.BonesBot,bs.SpyBot]
                    botPF = [bs.AgentBot,bs.ToughGuyBotPro,bs.NinjaBotPro,bs.SpyBotPro]
                    botT = [bs.BomberBotProStatic,bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Lunatic':
                    botF = [bs.LooieBot,bs.AgentBot,bs.MelBot,bs.ZillBot,bs.DemonBot]
                    botPF = [bs.AgentBotPro,bs.MelDuperBot,bs.ZillBotPro,bs.SpyBotPro]
                    botT = [bs.MelBotStatic,bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Happy':
                    botF = [bs.LooieBot,bs.ZillBot,bs.RonnieBot,bs.AliBot,bs.PuckBot,bs.JuiceBot]
                    botPF = [bs.AgentBotPro,bs.MelDuperBot,bs.ZillBotPro,bs.SpyBotPro,bs.AliBotPro]
                    botT = [bs.RonnieBotStatic,bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Intrepid':
                    botF = [bs.BonesBot,bs.PuckBot,bs.AgentBot,bs.ToughGuyBot,bs.AliBot,bs.PirateBot]
                    botPF = [bs.AgentBotPro,bs.BonesBotPro,bs.AliBotPro,bs.ToughGuyBotPro,bs.PirateBotShielded]
                    botT = [bs.BomberBotProStatic]
                elif firstWordChoice[0] == 'Heartless':
                    botF = [bs.CyborgBot,bs.ZillBot,bs.BonesBot,bs.KnightBot]
                    botPF = [bs.CyborgBotPro,bs.ZillBotPro,bs.BonesBotPro,bs.KnightBotPro]
                    botT = [bs.CyborgBotStatic]
                elif firstWordChoice[0] == 'Intense':
                    botF = [bs.BunnyBot,bs.RonnieBot,bs.PascalBot,bs.AgentBot,bs.PirateBot]
                    botPF = [bs.BunnyBotShielded,bs.PascalBotShielded,bs.AgentBotPro,bs.PirateBotRadius]
                    botT = [bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Snowy':
                    botF = [bs.FrostyBot,bs.SantaBot,bs.BomberBot]
                    botPF = [bs.FrostyBotPro,bs.BomberBotPro]
                    botT = [bs.FrostyBotStatic]
                elif firstWordChoice[0] == 'Breezy':
                    botF = [bs.PascalBot,bs.WizardBot,bs.AliBot,bs.ChickBot,bs.CowBot]
                    botPF = [bs.PascalBotShielded,bs.WizardBotPro,bs.AliBotPro,bs.ChickBotPro,bs.CowBotShielded]
                    botT = [bs.WizardBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Cold':
                    botF = [bs.PascalBot,bs.SantaBot,bs.FrostyBot]
                    botPF = [bs.PascalBotShielded,bs.PascalBotShielded]
                    botT = [bs.FrostyBotStatic]
                elif firstWordChoice[0] == 'Haily':
                    botF = [bs.PascalBot,bs.FrostyBot]
                    botPF = [bs.PascalBotShielded,bs.FrostyBotPro]
                    botT = [bs.FrostyBotStatic]
                elif firstWordChoice[0] == 'Calm':
                    botF = [bs.AliBot,bs.PuckBot,bs.SpyBot,bs.PixelBot]
                    botPF = [bs.AliBotPro,bs.SpyBotPro,bs.PixelBotPro]
                    botT = [bs.WizardBotStatic,bs.PixelBotStatic]
                elif firstWordChoice[0] == 'Aerial':
                    botF = [bs.PixelBot,bs.ToughGuyBot,bs.ChickBot,bs.BunnyBot]
                    botPF = [bs.PixelBotPro,bs.ToughGuyBotPro,bs.ChickBotPro,bs.BunnyBotShielded]
                    botT = [bs.WizardBotStatic]
                elif firstWordChoice[0] == 'Oceanic':
                    botF = [bs.PascalBot,bs.BomberBot,bs.ToughGuyBot,bs.AgentBot]
                    botPF = [bs.PascalBotShielded,bs.BomberBotPro,bs.ToughGuyBotPro,bs.AgentBot]
                    botT = [bs.BomberBotProStatic]
                elif firstWordChoice[0] == 'Slowed':
                    botF = [bs.WizardBot,bs.FrostyBot,bs.SantaBot,bs.BunnyBot]
                    botPF = [bs.WizardBotPro,bs.FrostyBotPro,bs.BunnyBotShielded]
                    botT = [bs.WizardBotStatic,bs.FrostyBotStatic]
                elif firstWordChoice[0] == 'Tactical':
                    botF = [bs.MelBot,bs.AliBot,bs.NinjaBot,bs.SoldierBot,bs.CyborgBot]
                    botPF = [bs.MelDuperBot,bs.AliBotPro,bs.NinjaBotPro,bs.CyborgBotPro]
                    botT = [bs.MelBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Epic':
                    botF = [bs.CowBot,bs.NinjaBot,bs.ChickBot,bs.MelBot,bs.KnightBot,bs.SpyBot]
                    botPF = [bs.MelDuperBot,bs.ChickBotPro,bs.NinjaBotPro,bs.SpyBotPro,bs.CowBotShielded,bs.KnightBotPro]
                    botT = [bs.WizardBotStatic,bs.MelBotStatic]
                elif firstWordChoice[0] == 'Epic':
                    botF = [bs.CowBot,bs.NinjaBot,bs.ChickBot,bs.MelBot,bs.KnightBot,bs.SpyBot]
                    botPF = [bs.MelDuperBot,bs.ChickBotPro,bs.NinjaBotPro,bs.SpyBotPro,bs.CowBotShielded,bs.KnightBotPro]
                    botT = [bs.WizardBotStatic,bs.MelBotStatic]
                elif firstWordChoice[0] == 'Sunny':
                    botF = [bs.CowBot,bs.BomberBot,bs.ToughGuyBot,bs.KnightBot,bs.BearBot]
                    botPF = [bs.BomberBotPro,bs.ToughGuyBotPro,bs.BearBotShielded,bs.CowBotShielded,bs.KnightBotPro]
                    botT = [bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Focused':
                    botF = [bs.BunnyBot,bs.NinjaBot,bs.ChickBot.bs.PirateBot,bs.AliBot,bs.KlayBot]
                    botPF = [bs.BomberBotPro,bs.NinjaBotPro,bs.ChickBotPro,bs.AliBotPro,bs.KlayBotPro]
                    botT = [bs.BomberBotProStatic]
                elif firstWordChoice[0] == 'Sandy':
                    botF = [bs.BunnyBot,bs.NinjaBot,bs.ChickBot.bs.PirateBot,bs.AliBot,bs.KlayBot]
                    botPF = [bs.BomberBotPro,bs.NinjaBotPro,bs.ChickBotPro,bs.AliBotPro,bs.KlayBot]
                    botT = [bs.BomberBotProStatic,bs.MelBotStatic,bs.KlayBotStatic]
                elif firstWordChoice[0] == 'Odd':
                    botF = [bs.BomberBot,bs.RonnieBot,bs.LooieBot,bs.MelBot,bs.ToughGuyBot]
                    botPF = [bs.BomberBotPro,bs.LooieBotPro,bs.MelDuperBot,bs.ToughGuyBotPro]
                    botT = [bs.MelBotStatic,bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Abrasive':
                    botF = [bs.BunnyBot,bs.AliBot,bs.PuckBot,bs.BonesBot,bs.AgentBot]
                    botPF = [bs.BunnyBotShielded,bs.AliBotPro,bs.BonesBotPro,bs.AgentBotPro]
                    botT = [bs.WizardBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Abrasive':
                    botF = [bs.BunnyBot,bs.AliBot,bs.PuckBot,bs.BonesBot,bs.AgentBot]
                    botPF = [bs.BunnyBotShielded,bs.AliBotPro,bs.BonesBotPro,bs.AgentBotPro]
                    botT = [bs.WizardBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Warped':
                    botF = [random.choice([bs.FrostyBot,bs.RonnieBot,bs.BomberBot,bs.SpyBot,bs.AgentBot,bs.LooieBot,bs.AliBot,bs.MelBot]),bs.ToughGuyBot,random.choice([bs.CowBot,bs.WizardBot,bs.ToughGuyBot,bs.MelBot]),random.choice([bs.BomberBot,bs.ChickBot,bs.PixelBot,bs.PascalBot,bs.JesterBot]),random.choice([bs.ChickBot,bs.MelBot,bs.BearBot,bs.CyborgBot,bs.SantaBot])]
                    botPF = [random.choice([bs.MelDuperBot,bs.FrostyBotPro,bs.LooieBotPro,bs.BomberBotPro,bs.PascalBotShielded,bs.AliBotPro]),random.choice([bs.ChickBotPro,bs.ZillBotPro,bs.BonesBotPro,bs.KnightBotPro]),bs.BearBotShielded,bs.MelDuperBot,random.choice([bs.FrostyBotPro,bs.ToughGuyBotPro,bs.SpyBotPro,bs.PixelBotPro])]
                    botT = [bs.BomberBotStatic,bs.PixelBotStatic,bs.RonnieBotStatic,bs.CowBotStatic]
                elif firstWordChoice[0] == 'Wonderful':
                    botF = [bs.BunnyBot,bs.PixelBot,bs.WizardBot,bs.LooieBot,bs.BonesBot,bs.CowBot]
                    botPF = [bs.BonesBotPro,bs.PixelBotPro,bs.WizardBotPro,bs.LooieBotPro,bs.CowBotShielded]
                    botT = [bs.WizardBotStatic]
                elif firstWordChoice[0] == 'Mystical':
                    botF = [bs.KnightBot,bs.PixelBot,bs.FrostyBot,bs.SantaBot,bs.SoldierBot,bs.BomberBot]
                    botPF = [bs.KnightBotPro,bs.PixelBotPro,bs.FrostyBotPro,bs.BomberBotPro]
                    botT = [bs.PixelBotStatic]
                elif firstWordChoice[0] == 'Magical':
                    botF = [bs.JuiceBot,bs.PixelBot,bs.WizardBot,bs.KlayBot,bs.AliBot,bs.BonesBot]
                    botPF = [bs.PixelBotPro,bs.WizardBotPro,bs.KlayBotPro,bs.AliBotPro,bs.BonesBotPro]
                    botT = [bs.PixelBotStatic,bs.WizardBotStatic]
                elif firstWordChoice[0] == 'Special':
                    botF = [bs.MelBot,bs.SpyBot,bs.LooieBot,bs.KnightBot,bs.SpazBot,bs.NinjaBot]
                    botPF = [bs.MelDuperBot,bs.SpyBotPro,bs.LooieBotPro,bs.KnightBotPro,bs.BomberBotPro,bs.NinjaBotPro]
                    botT = [bs.MelBotStatic,bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Sparkly':
                    botF = [bs.PuckBot,bs.PixelBot,bs.WizardBot,bs.KlayBot,bs.CyborgBot]
                    botPF = [bs.PixelBotPro,bs.WizardBotPro,bs.KlayBotPro,bs.CyborgBotPro,bs.JesterBot]
                    botT = [bs.KlayBotStatic,bs.PixelBotStatic]
                elif firstWordChoice[0] == 'Euphoric':
                    botF = [bs.LooieBot,bs.ZillBot,bs.ToughGuyBot,bs.NinjaBot,bs.AliBot]
                    botPF = [bs.LooieBotPro,bs.ZillBotPro,bs.ToughGuyBotPro,bs.NinjaBotPro,bs.AliBotPro]
                    botT = [bs.BomberBotProStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Supernatural':
                    botF = [bs.CyborgBot,bs.AliBot,bs.BearBot,bs.ZillBot,bs.PixelBot]
                    botPF = [bs.CyborgBotPro,bs.ZillBotPro,bs.BearBotShielded,bs.PixelBotPro,bs.AliBotPro]
                    botT = [bs.CyborgBotStatic,bs.SpyBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Forgotten':
                    botF = [bs.BonesBot,bs.SpyBot,bs.AgentBot,bs.PirateBot,bs.SoldierBot]
                    botPF = [bs.BonesBotPro,bs.SpyBotPro,bs.AgentBotPro,bs.PirateBotRadius]
                    botT = [bs.SpyBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Tricky':
                    botF = [bs.NinjaBot,bs.ChickBot,bs.CyborgBot,bs.FrostyBot,bs.BearBot,bs.WizardBot]
                    botPF = [bs.NinjaBotPro,bs.ChickBotPro,bs.CyborgBotPro,bs.FrostyBotPro,bs.BearBotShielded,bs.WizardBotPro]
                    botT = [bs.CowBotStatic,bs.CyborgBotStatic]
                elif firstWordChoice[0] == 'Lovely':
                    botF = [bs.LooieBot,bs.WizardBot,bs.PascalBot,bs.BomberBot,bs.SpyBot,bs.ToughGuyBot]
                    botPF = [bs.LooieBotPro,bs.WizardBotPro,bs.PascalBotShielded,bs.BomberBotPro,bs.SpyBotPro,bs.ToughGuyBotPro]
                    botT = [bs.WizardBotStatic,bs.MelBotStatic,bs.BomberBotStatic]
                elif firstWordChoice[0] == 'Sweet':
                    botF = [bs.MelBot,bs.ChickBot,bs.PixelBot,bs.JuiceBot,bs.PuckBot,bs.NinjaBot]
                    botPF = [bs.MelDuperBot,bs.ChickBotPro,bs.PixelBotPro,bs.NinjaBotPro]
                    botT = [bs.MelBotStatic]
                elif firstWordChoice[0] == 'Beautiful':
                    botF = [bs.BunnyBot,bs.BomberBot,bs.LooieBot,bs.PixelBot,bs.KlayBot,bs.AliBot]
                    botPF = [bs.BunnyBotShielded,bs.BomberBotPro,bs.LooieBotPro,bs.KlayBotPro,bs.AliBot]
                    botT = [bs.KlayBotStatic,bs.FrostyBotStatic]
                elif firstWordChoice[0] == 'Extraordinary':
                    botF = [bs.BunnyBot,bs.BearBot,bs.SoldierBot,bs.LooieBot,bs.MelBot,bs.ChickBot]
                    botPF = [bs.BunnyBotShielded,bs.BearBotShielded,bs.LooieBotPro,bs.MelDuperBot,bs.ChickBotPro]
                    botT = [bs.MelBotStatic,bs.BomberBotStatic,bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Poison':
                    botF = [bs.NinjaBot,bs.BomberBot,bs.ChickBot,bs.SpyBot,bs.RonnieBot,bs.PirateBot]
                    botPF = [bs.NinjaBotPro,bs.BomberBotPro,bs.ChickBotPro,bs.SpyBotPro,bs.PirateBotShielded]
                    botT = [bs.CowBotStatic,bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Flabby':
                    botF = [bs.BonesBot,bs.AliBot,bs.PuckBot,bs.ToughGuyBot,bs.SpyBot]
                    botPF = [bs.BonesBotPro,bs.AliBotPro,bs.ToughGuyBotPro,bs.SpyBotPro]
                    botT = [bs.CowBotStatic,bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Lucky':
                    botF = [bs.AliBot,bs.MelBot,bs.KnightBot,bs.PuckBot,bs.DemonBot,bs.WizardBot]
                    botPF = [bs.AliBotPro,bs.MelDuperBot,bs.KnightBotPro,bs.WizardBotPro]
                    botT = [bs.MelBotStatic,bs.WizardBotStatic]
                elif firstWordChoice[0] == 'Careful':
                    botF = [bs.SpyBot,bs.KnightBot,bs.PirateBot,bs.PascalBot,bs.ZillBot]
                    botPF = [bs.SpyBotPro,bs.KnightBotPro,bs.PirateBotShielded,bs.PascalBotShielded,bs.ZillBotPro]
                    botT = [bs.ChickBotStatic,bs.WizardBotStatic,random.choice([bs.SpyBotStatic,bs.KlayBotStatic])]
                elif firstWordChoice[0] == 'Ruinous':
                    botF = [bs.PascalBot,bs.DemonBot,bs.NinjaBot,bs.KnightBot,bs.AgentBot,bs.CyborgBot]
                    botPF = [bs.PascalBotShielded,bs.NinjaBotPro,bs.KnightBotPro,bs.AgentBotPro,bs.CyborgBotPro]
                    botT = [bs.FrostyBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Strong':
                    botF = [bs.NinjaBot,bs.AgentBot,bs.PuckBot,bs.JuiceBot,bs.BonesBot,bs.PixelBot]
                    botPF = [bs.NinjaBotPro,bs.AgentBotPro,bs.BonesBotPro,bs.PixelBotPro]
                    botT = [bs.ChickBotStatic,bs.PixelBotStatic]
                elif firstWordChoice[0] == 'Glossy':
                    botF = [bs.ZillBot,bs.ToughGuyBot,bs.CyborgBot,bs.PuckBot,bs.AgentBot,bs.NinjaBot]
                    botPF = [bs.ZillBotPro,bs.ToughGuyBotPro,bs.CyborgBotPro,bs.AgentBotPro,bs.NinjaBotPro]
                    botT = [bs.CyborgBotStatic,bs.PixelBotStatic]
                elif firstWordChoice[0] == 'Violent':
                    botF = [bs.LooieBot,bs.PascalBot,bs.RonnieBot,bs.BearBot,bs.AgentBot,bs.MelBot]
                    botPF = [bs.LooieBotPro,bs.PascalBotShielded,bs.BearBotShielded,bs.AgentBotPro,bs.MelDuperBot]
                    botT = [bs.ChickBotStatic,bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Stunted':
                    botF = [bs.BonesBot,bs.AgentBot,bs.NinjaBot,bs.PuckBot,bs.SoldierBot]
                    botPF = [bs.BonesBotPro,bs.AgentBotPro,bs.NinjaBotPro]
                    botT = [bs.SpyBotStatic,bs.CowBotStatic]
                elif firstWordChoice[0] == 'Lurid':
                    botF = [bs.MelBot,bs.KnightBot,bs.WizardBot,bs.SoldierBot,bs.DemonBot,bs.BunnyBot]
                    botPF = [bs.MelBot,bs.KnightBotPro,bs.WizardBotPro,bs.BunnyBotShielded]
                    botT = [bs.MelBotStatic,bs.KlayBotStatic]
                elif firstWordChoice[0] == 'Hellish':
                    botF = [bs.AgentBot,bs.FrostyBot,bs.PirateBot,bs.LooieBot,bs.BearBot]
                    botPF = [bs.AgentBotPro,bs.FrostyBotPro,bs.PirateBotShielded,bs.BearBotShielded]
                    botT = [bs.MelBotStatic,bs.PixelBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Smoldered':
                    botF = [bs.ChickBot,bs.AliBot,bs.CyborgBot,bs.BomberBot,bs.BonesBot]
                    botPF = [bs.ChickBotPro,bs.AliBotPro,bs.CyborgBotPro,bs.BomberBotPro,bs.BonesBotPro]
                    botT = [RonnieBotStatic]
                elif firstWordChoice[0] == 'Spicy':
                    botF = [bs.ToughGuyBot,bs.CyborgBot,bs.SpyBot,bs.MelBot,bs.BonesBot]
                    botPF = [bs.ToughGuyBotPro,bs.CyborgBotPro,bs.SpyBotPro,bs.MelDuperBot,bs.BonesBotPro]
                    botT = [bs.CyborgBotStatic,bs.BomberBotProStatic]
                elif firstWordChoice[0] == 'Warm':
                    botF = [bs.RonnieBot,bs.BearBot,bs.ToughGuyBot,bs.NinjaBot,bs.KnightBot]
                    botPF = [bs.BearBotShielded,bs.ToughGuyBotPro,bs.NinjaBotPro,bs.KnightBotPro]
                    botT = [bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Exotic':
                    botF = [bs.ToughGuyBot,bs.NinjaBot,bs.FrostyBot,bs.BunnyBot,bs.BonesBot]
                    botPF = [bs.ToughGuyBotPro,bs.NinjaBotPro,bs.FrostyBotPro,bs.BunnyBotShielded,bs.BonesBotPro]
                    botT = [bs.BomberBotProStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Sizzling':
                    botF = [bs.SpyBot,bs.LooieBot,bs.ChickBot.bs.PixelBot,bs.MelBot]
                    botPF = [bs.SpyBotPro,bs.LooieBotPro,bs.ChickBotPro,bs.PixelBotPro,bs.MelDuperBot]
                    botT = [bs.WizardBotStatic,bs.CowBotStatic]
                elif firstWordChoice[0] == 'Unsure':
                    botF = [bs.CyborgBot,bs.AliBot,bs.WizardBot,bs.NinjaBot,bs.BearBot]
                    botPF = [bs.CyborgBotPro,bs.AliBotPro,bs.WizardBotPro,bs.NinjaBotPro,bs.BearBotShielded]
                    botT = [bs.CyborgBotStatic,bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Hazard':
                    botF = [bs.PirateBot,bs.ChickBot,bs.JuiceBot,bs.MelBot,bs.KlayBot,bs.AgentBot]
                    botPF = [bs.PirateBotRadius,bs.ChickBotPro,bs.MelDuperBot,bs.KlayBotPro,bs.AgentBotPro]
                    botT = [bs.ChickBotStatic,bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Hazard':
                    botF = [bs.PirateBot,bs.ChickBot,bs.JuiceBot,bs.MelBot,bs.KlayBot,bs.AgentBot]
                    botPF = [bs.PirateBotRadius,bs.ChickBotPro,bs.MelDuperBot,bs.KlayBotPro,bs.AgentBotPro]
                    botT = [bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Angry':
                    botF = [bs.AgentBot,bs.CyborgBot,bs.NinjaBot,bs.BunnyBot,bs.BomberBot,bs.ToughGuyBot]
                    botPF = [bs.AgentBotPro,bs.CyborgBotPro,bs.NinjaBotPro,bs.BunnyBotShielded,bs.BomberBotPro,bs.ToughGuyBotPro]
                    botT = [bs.CyborgBotStatic,bs.BomberBotStatic]
                elif firstWordChoice[0] == 'Joyful':
                    botF = [bs.MelBot,bs.WizardBot,bs.FrostyBot,bs.BonesBot,bs.PascalBot,bs.CyborgBot]
                    botPF = [bs.MelDuperBot,bs.WizardBotPro,bs.FrostyBotPro,bs.BonesBotPro,bs.PascalBotShielded,bs.CyborgBotPro]
                    botT = [bs.MelBotStatic,bs.WizardBotStatic]
                elif firstWordChoice[0] == 'Diluted':
                    botF = [bs.MelBot,bs.ToughGuyBot,bs.ChickBot,bs.SpazBot,bs.LooieBot]
                    botPF = [bs.MelDuperBot,bs.ToughGuyBotPro,bs.ChickBotPro,bs.BomberBotPro,bs.LooieBotPro]
                    botT = [ChickBotStatic,bs.BomberBotStatic]
                elif firstWordChoice[0] == 'Inky':
                    botF = [bs.AliBot,bs.BearBot,bs.NinjaBot,bs.PirateBot,bs.JuiceBot,bs.KlayBot]
                    botPF = [bs.AliBotPro,bs.BearBotShielded,bs.NinjaBotPro,bs.PirateBotRadius,bs.KlayBotPro]
                    botT = [bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Hazy':
                    botF = [bs.KlayBot,bs.SantaBot,bs.PascalBot,bs.PuckBot,bs.CyborgBot]
                    botPF = [bs.KlayBotPro,bs.PascalBotShielded,bs.CyborgBotPro]
                    botT = [bs.FrostyBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Blind':
                    botF = [bs.AgentBot,bs.ChickBot,bs.NinjaBot,bs.CyborgBot,bs.KnightBot]
                    botPF = [bs.AgentBotPro,bs.ChickBotPro,bs.NinjaBotPro,bs.CyborgBotPro,bs.KnightBotPro]
                    botT = [bs.CyborgBot,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Dusky':
                    botF = [bs.BomberBot,bs.KlayBot,bs.JuiceBot,bs.DemonBot,bs.NinjaBot,bs.AgentBot]
                    botPF = [bs.BomberBotPro,bs.KlayBotPro,bs.NinjaBotPro,bs.AgentBotPro]
                    botT = [bs.KlayBotStatic,bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Futile':
                    botF = [bs.CowBot,bs.BonesBot,bs.FrostyBot,bs.AliBot,bs.WizardBot]
                    botPF = [bs.CowBotShielded,bs.BonesBotPro,bs.FrostyBotPro,bs.AliBotPro,bs.WizardBotPro]
                    botT = [bs.CowBotStatic,bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Concealed':
                    botF = [bs.KnightBot,bs.NinjaBot,bs.DemonBot,bs.AgentBot,bs.SpyBot]
                    botPF = [bs.KnightBotPro,bs.NinjaBotPro,bs.AgentBotPro,bs.SpyBotPro]
                    botT = [bs.ChickBotStatic,bs.KlayBotStatic]
                elif firstWordChoice[0] == 'Redacted':
                    botF = [bs.WizardBot,bs.BearBot,bs.ToughGuyBot,bs.AgentBot,bs.LooieBot,bs.ChickBot]
                    botPF = [bs.PixelBotPro,bs.JuiceBot,bs.CyborgBotPro,bs.CowBotShielded,bs.NinjaBotPro]
                    botT = [bs.BomberBotProStatic]
                elif firstWordChoice[0] == 'Level Headed':
                    botF = [bs.ToughGuyBot,bs.MelBot,bs.PirateBot,bs.AliBot,bs.CowBot]
                    botPF = [bs.ToughGuyBotPro,bs.MelDuperBot,bs.PirateBotRadius,bs.AliBotPro,bs.CowBotShielded]
                    botT = [bs.MelBotStatic,bs.CowBotStatic,bs.BomberBotStatic]
                elif firstWordChoice[0] == 'Crazy':
                    botF = [bs.PascalBot,bs.LooieBot,bs.ZillBot,bs.MelBot,bs.AgentBot,bs.SpyBot]
                    botPF = [bs.PascalBotShielded,bs.LooieBotPro,bs.ZillBotPro,bs.MelDuperBot,bs.AgentBotPro,bs.SpyBotPro]
                    botT = [bs.MelBotStatic,bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Ordinary':
                    botF = [bs.BomberBot,bs.ToughGuyBot,bs.NinjaBot,bs.MelBot]
                    botPF = [bs.BomberBotPro,bs.ToughGuyBotPro,bs.NinjaBotPro,bs.MelDuperBot]
                    botT = [bs.BomberBotProStatic]
                elif firstWordChoice[0] in ['Classic','Plain']:
                    botF = [bs.BomberBot,bs.ToughGuyBot,bs.NinjaBot,bs.MelBot,bs.BunnyBot,bs.ChickBot,bs.PirateBot]
                    botPF = [bs.BomberBotPro,bs.ToughGuyBotPro,bs.NinjaBotPro,bs.ChickBotPro,bs.PirateBotNoTimeLimit]
                    botT = [bs.BomberBotProStatic,bs.MelBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Competitive':
                    botF = [bs.BonesBot,bs.BunnyBot,bs.MelBot,bs.NinjaBot,bs.ToughGuyBot,bs.CyborgBot]
                    botPF = [bs.BonesBotPro,bs.BunnyBotShielded,bs.MelDuperBot,bs.NinjaBotPro,bs.ToughGuyBotPro,bs.CyborgBotPro]
                    botT = [bs.FrostyBotStatic,bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Strategic':
                    botF = [bs.PuckBot,bs.CowBot,bs.ToughGuyBot,bs.SpyBot,bs.BunnyBot]
                    botPF = [bs.CowBotShielded,bs.ToughGuyBotPro,bs.SpyBotPro,bs.BunnyBotShielded]
                    botT = [bs.MelBotStatic,bs.PixelBotStatic]
                elif firstWordChoice[0] == 'Invalid':
                    botF = [bs.AgentBot,bs.JuiceBot,bs.BonesBot,bs.FrostyBot,bs.ToughGuyBot,bs.NinjaBot]
                    botPF = [bs.AgentBotPro,bs.BonesBotPro,bs.FrostyBotPro,bs.ToughGuyBotPro,bs.NinjaBotPro]
                    botT = [bs.FrostyBotStatic,bs.ChickBotStatic]
                elif firstWordChoice[0] == 'Savage':
                    botF = [bs.FrostyBot,bs.ChickBot,bs.PirateBot,bs.BomberBot,bs.LooieBot]
                    botPF = [bs.FrostyBotPro,bs.ChickBotPro,bs.PirateBotRadius,bs.BomberBotPro,bs.LooieBotPro]
                    botT = [bs.WizardBotStatic,bs.SpyBotStatic]
                elif firstWordChoice[0] == 'Tough':
                    botF = [bs.PuckBot,bs.CowBot,bs.BonesBot,bs.KnightBot,bs.PixelBot,bs.ToughGuyBot]
                    botPF = [bs.CowBotShielded,bs.BonesBotPro,bs.KnightBotPro,bs.PixelBotPro,bs.ToughGuyBotPro]
                    botT = [bs.CowBotStatic,bs.RonnieBotStatic]
                elif firstWordChoice[0] == 'Average':
                    botF = [bs.ToughGuyBot,bs.PixelBot,bs.RonnieBot,bs.MelBot,bs.ChickBot,bs.WizardBot]
                    botPF = [bs.ToughGuyBotPro,bs.PixelBotPro,bs.MelDuperBot,bs.ChickBotPro,bs.WizardBotPro]
                    botT = [bs.CyborgBotStatic,bs.ChickBotStatic,bs.BomberBotStatic]
                bot_turret_1 = random.choice(botT)
                bot_turret_2 = random.choice(botT)
                bot_fighter_1 = random.choice(botF)
                bot_fighter_2 = random.choice(botF)
                bot_fighter_3 = random.choice(botF)
                bot_pro_fighter_1 = random.choice(botPF)
                bot_pro_fighter_2 = random.choice(botPF)
                bot_pro_fighter_3 = random.choice(botPF)
                
            self._presets =[]
            result = []
            self._presets += [
                                [ # Melees
                                    {'entries':[
                                        {'type':random.choice([bot_fighter_1,bot_pro_fighter_1]),'point':random.choice(['Right','TopRight','BottomRight'])},
                                        {'type':bot_fighter_1,'point':random.choice(['Left','TopLeft','BottomLeft'])},
                                        {'type':bot_pro_fighter_1,'point':'LeftUpper'} if len(self.players) > 1 else None,
                                        {'type':bot_pro_fighter_1,'point':'RightUpper'} if len(self.players) > 2 else None,
                                    ]},
                                    random.choice([
                                        {'entries':[
                                        {'type':bot_fighter_3,'point':'RightUpper'},
                                        {'type':bot_fighter_3,'point':'RightLower'},
                                        {'type':bot_fighter_2,'point':'LeftLower'},
                                        {'type':bot_fighter_2,'point':'LeftUpper'},]},
                                        
                                        {'entries':[
                                        {'type':bot_fighter_2,'point':'RightUpper'},
                                        {'type':bot_fighter_3,'point':'RightLower'},
                                        {'type':bot_fighter_2,'point':'LeftLower'},
                                        {'type':bot_fighter_3,'point':'LeftUpper'}
                                        ]}]),
                                    random.choice([
                                        {'entries':[
                                        {'type':bot_fighter_1,'point':'RightUpper'},
                                        {'type':bot_fighter_1,'point':'LeftUpper'},
                                        {'type':bot_fighter_3,'point':'Top'},
                                        {'type':bot_fighter_2,'point':'TopHalfRight'},
                                        {'type':bot_fighter_2,'point':'TopHalfLeft'},
                                        {'type':bot_pro_fighter_1,'point':'Left'} if len(self.players) > 3 else None,
                                        {'type':bot_pro_fighter_1,'point':'Right'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bot_fighter_1,'point':'RightLower'},
                                        {'type':bot_fighter_1,'point':'LeftLower'},
                                        {'type':bot_fighter_3,'point':'Bottom'},
                                        {'type':bot_fighter_2,'point':'BottomHalfRight'},
                                        {'type':bot_fighter_2,'point':'BottomHalfLeft'},
                                        {'type':bot_pro_fighter_1,'point':'Left'} if len(self.players) > 3 else None,
                                        {'type':bot_pro_fighter_1,'point':'Right'} if len(self.players) > 2 else None
                                    ]}]),
                                    {'entries':[
                                        {'type':bot_turret_1,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                                        {'type':bot_fighter_1,'point':random.choice(['Left','Right'])},
                                        {'type':random.choice([bot_fighter_1,bot_pro_fighter_1]),'point':random.choice(['Top','Bottom'])},
                                        {'type':bot_fighter_1,'point':random.choice(['Left','Right'])},
                                        {'type':'delay','duration':1000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':random.choice(['Top','Bottom'])},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':'BottomLeft'},
                                        {'type':bs.PirateBot,'point':'BottomRight'},
                                    ]},
                                    {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bot_turret_2,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bot_turret_1,'point':'TurretTopLeft'},
                                        {'type':bot_turret_1,'point':'TurretBottomLeft'},
                                        {'type':bot_pro_fighter_1,'point':'Left'},
                                        {'type':bot_pro_fighter_2,'point':random.choice(['Top','Bottom'])},
                                        {'type':random.choice([bot_pro_fighter_3,bot_pro_fighter_1]),'point':'Right'},
                                        {'type':'delay','duration':1000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':random.choice(['Top','Bottom'])},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':'BottomLeft'},
                                        {'type':bs.PirateBot,'point':'BottomRight'},
                                    ]},
                                    {'entries':[
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':'Left'},
                                        {'type':'delay','duration':1000},
                                        {'type':bot_pro_fighter_1,'point':'RightUpper'},
                                        {'type':bot_pro_fighter_1,'point':'RightLower'},
                                        {'type':'delay','duration':4000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':'Right'},
                                        {'type':'delay','duration':1000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':'Left'},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':random.choice(['Top','Bottom'])},
                                        {'type':bs.PirateBot,'point':random.choice(['Left','Right'])},
                                        {'type':bs.PirateBot,'point':random.choice(['Top','Bottom'])},
                                        {'type':bs.PirateBot,'point':random.choice(['Left','Right'])},
                                    ]},]]
            self._presets += [
                                [ # Suicide Shits
                                    {'entries':[
                                        {'type':bot_turret_2,'point':'TurretTopLeft'},
                                        {'type':bot_turret_1,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bot_turret_2,'point':'TurretTopRight'},
                                        {'type':bs.PirateBot,'point':random.choice(['Left','TopLeft'])},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':random.choice(['Right','TopRight'])},
                                    ]},
                                    {'entries':[
                                        {'type':bot_turret_2,'point':'TurretTopRight'},
                                        {'type':bot_turret_2,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bot_turret_2,'point':'TurretTopLeft'},
                                        {'type':bs.PirateBot,'point':'Right'},
                                        {'type':bs.PirateBot,'point':'Left'},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':random.choice(['Top','Bottom'])},
                                    ]},
                                    {'entries':[
                                        {'type':bot_turret_1,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bot_turret_1,'point':'TurretBottomRight'},
                                        {'type':bot_fighter_3,'point':'Left'},
                                        {'type':bot_fighter_3,'point':'Right'},
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
                                        {'type':bot_fighter_1,'point':random.choice(['Left','Right'])},
                                        {'type':random.choice([bot_fighter_1,bot_pro_fighter_1]),'point':random.choice(['Top','Bottom'])},
                                        {'type':bot_fighter_1,'point':random.choice(['Left','Right'])},
                                        {'type':'delay','duration':1000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':random.choice(['Top','Bottom'])},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':'BottomLeft'},
                                        {'type':bs.PirateBot,'point':'BottomRight'},
                                    ]},
                                    {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bot_turret_2,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                        {'type':bot_turret_1,'point':'TurretTopLeft'},
                                        {'type':bot_turret_1,'point':'TurretBottomLeft'},
                                        {'type':bot_pro_fighter_1,'point':'Left'},
                                        {'type':bot_pro_fighter_2,'point':random.choice(['Top','Bottom'])},
                                        {'type':random.choice([bot_pro_fighter_3,bot_pro_fighter_1]),'point':'Right'},
                                        {'type':'delay','duration':1000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':random.choice(['Top','Bottom'])},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':'BottomLeft'},
                                        {'type':bs.PirateBot,'point':'BottomRight'},
                                    ]},
                                    {'entries':[
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':'Left'},
                                        {'type':'delay','duration':1000},
                                        {'type':bot_pro_fighter_1,'point':'RightUpper'},
                                        {'type':bot_pro_fighter_1,'point':'RightLower'},
                                        {'type':'delay','duration':4000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':'Right'},
                                        {'type':'delay','duration':1000},
                                        {'type':random.choice([bs.PirateBot,bs.PirateBotRadius]),'point':'Left'},
                                        {'type':'delay','duration':4000},
                                        {'type':bs.PirateBot,'point':random.choice(['Top','Bottom'])},
                                        {'type':bs.PirateBot,'point':random.choice(['Left','Right'])},
                                        {'type':bs.PirateBot,'point':random.choice(['Top','Bottom'])},
                                        {'type':bs.PirateBot,'point':random.choice(['Left','Right'])},
                                    ]},]]
            self._presets += [
                                [ # Bunnies
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':random.choice(['Top','TopLeft','TopRight','Left','Right'])},
                                        {'type':bs.BunnyBot,'point':random.choice(['Bottom','BottomLeft','BottomRight'])} if len(self.players) > 1 else None,
                                    ]},
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':'Left'},
                                        {'type':bs.BunnyBot,'point':'Right'},
                                        {'type':bs.BunnyBot,'point':'Top'} if len(self.players) > 1 else None,
                                        {'type':bs.BunnyBot,'point':'Bottom'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':'TopLeft'},
                                        {'type':bs.BunnyBot,'point':'TopRight'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,
                                    ]},
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':'TopLeft'},
                                        {'type':bs.BunnyBot,'point':'TopRight'},
                                        {'type':bs.BunnyBot,'point':'BottomRight'},
                                        {'type':bs.BunnyBot,'point':'BottomLeft'},
                                    ]},
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':'RightUpperMore'},
                                        {'type':bs.BunnyBot,'point':'Right'},
                                        {'type':bs.BunnyBot,'point':random.choice(['BottomLeft','TopLeft'])},
                                        {'type':bs.BunnyBot,'point':random.choice(['BottomRight','TopRight'])},
                                        {'type':bot_turret_1,'point':'TurretTopLeft'},
                                        {'type':bot_turret_2,'point':'TurretTopRight'},
                                        {'type':bot_turret_2,'point':'TurretTopMiddle'},
                                    ]},
                                    {'entries':[
                                        {'type':bs.BunnyBot,'point':'Center'},
                                        {'type':'delay','duration':2500},
                                        {'type':bs.BunnyBot,'point':'Right'},
                                        {'type':bs.BunnyBot,'point':'Left'},
                                        {'type':bs.BunnyBot,'point':'Top'},
                                        {'type':bs.BunnyBot,'point':'Bottom'},
                                        {'type':'delay','duration':5000},
                                        {'type':bs.BunnyBot,'point':'BottomLeft'},
                                        {'type':bs.BunnyBot,'point':'BottomRight'},
                                        {'type':bs.BunnyBot,'point':'TopLeft'},
                                        {'type':bs.BunnyBot,'point':'TopRight'},
                                    ]},]]
            self._presets += [
                                [ # Turret Preset Random
                                    random.choice([
                                        {'entries':[
                                        {'type':bot_turret_1,'point':'TurretBottomLeft'},
                                        {'type':bot_turret_1,'point':'TurretBottomRight'},
                                        {'type':bot_turret_2,'point':'TurretTopMiddleLeft'} if len(self.players) > 2 else None,
                                        {'type':bot_turret_2,'point':'TurretTopMiddleRight'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotStatic,'point':random.choice(['TurretTopLeft','TurretBottomLeft'])},
                                        {'type':bs.BomberBotStatic,'point':random.choice(['TurretTopRight','TurretBottomRight'])},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddle'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bot_fighter_2,'point':'RightUpper'},
                                        {'type':bot_fighter_3,'point':'RightLower'},
                                        {'type':bot_fighter_2,'point':'LeftLower'},
                                        {'type':bot_fighter_3,'point':'LeftUpper'}
                                        ]}]),
                                    #2
                                    random.choice([
                                        {'entries':[
                                        {'type':bot_turret_2,'point':'TurretBottomLeft'},
                                        {'type':bot_turret_2,'point':'TurretBottomRight'},
                                        {'type':bot_turret_1,'point':'TurretTopLeft'},
                                        {'type':bot_turret_1,'point':'TurretTopRight'},]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                                        {'type':bot_turret_1,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'} if len(self.players) > 2 else None
                                        ]}]),
                                    # 3
                                    random.choice([
                                        {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotPro,'point':'Bottom'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotPro,'point':'Bottom'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotPro,'point':'Bottom'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotPro,'point':'Bottom'} if len(self.players) > 2 else None
                                        ]}]),
                                    #4
                                    random.choice([
                                        {'entries':[
                                        {'type':bot_turret_1,'point':'TurretTopLeft'},
                                        {'type':bot_turret_1,'point':'TurretTopRight'},
                                        {'type':random.choice([bot_turret_2,bot_turret_1]),'point':'TurretTopMiddleLeft'},
                                        {'type':random.choice([bot_turret_2,bot_turret_1]),'point':'TurretTopMiddleRight'},
                                        {'type':'delay','duration':3473},
                                        {'type':bot_turret_2,'point':'TurretBottomLeft'},
                                        {'type':bot_turret_2,'point':'TurretBottomRight'},
                                        {'type':'delay','duration':3473},
                                        {'type':bot_turret_2,'point':'TurretTopLeft'},
                                        {'type':bot_turret_2,'point':'TurretTopRight'},]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotPro,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotPro,'point':'TopRight'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotPro,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotPro,'point':'TopRight'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bot_turret_1,'point':'TurretTopLeft'},
                                        {'type':bot_turret_1,'point':'TurretTopRight'},
                                        {'type':bot_turret_1,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotPro,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotPro,'point':'TopRight'} if len(self.players) > 2 else None
                                        ]}]),
                                    #5
                                    random.choice([
                                        {'entries':[
                                        {'type':bot_turret_1,'point':'TurretTopLeft'},
                                        {'type':bot_turret_1,'point':'TurretTopRight'},
                                        {'type':bot_turret_1,'point':'TurretBottomLeft'},
                                        {'type':bot_turret_1,'point':'TurretBottomRight'},
                                        {'type':bot_turret_1,'point':'TurretTopMiddleLeft'},
                                        {'type':bot_turret_1,'point':'TurretTopMiddleRight'},
                                        {'type':bot_turret_1,'point':'TurretTopMiddle'},
                                        {'type':bot_turret_1,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bot_turret_1,'point':'TopRight'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddleLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddleRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotStatic,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotStatic,'point':'TopRight'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotStatic,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddleLeft'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddleRight'},
                                        {'type':bs.BomberBotStatic,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotStatic,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotStatic,'point':'TopRight'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bot_turret_1,'point':'TurretTopLeft'},
                                        {'type':bot_turret_1,'point':'TurretTopRight'},
                                        {'type':bot_turret_1,'point':'TurretBottomLeft'},
                                        {'type':bot_turret_1,'point':'TurretBottomRight'},
                                        {'type':bot_turret_1,'point':'TurretTopMiddleLeft'},
                                        {'type':bot_turret_1,'point':'TurretTopMiddleRight'},
                                        {'type':bot_turret_1,'point':'TurretTopMiddle'},
                                        {'type':bot_turret_1,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bot_turret_1,'point':'TopRight'} if len(self.players) > 2 else None
                                    ]}]),
                                    #6
                                    random.choice([
                                        {'entries':[
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleRight'},
                                        {'type':random.choice([bs.FrostyBotStatic,bs.BomberBotProStaticShielded]),'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotProShielded,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotProShielded,'point':'TopRight'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotProShielded,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotProShielded,'point':'TopRight'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotProShielded,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotProShielded,'point':'TopRight'} if len(self.players) > 2 else None,]},
                                        
                                        {'entries':[
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretBottomRight'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleLeft'},
                                        {'type':bs.BomberBotProStaticShielded,'point':'TurretTopMiddleRight'},
                                        {'type':random.choice([bs.FrostyBotStatic,bs.BomberBotProStaticShielded]),'point':'TurretTopMiddle'},
                                        {'type':bs.BomberBotProShielded,'point':'TopLeft'} if len(self.players) > 2 else None,
                                        {'type':bs.BomberBotProShielded,'point':'TopRight'} if len(self.players) > 2 else None
                                    ]}]),]]
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
        super(RandomizedLevel,self).handleMessage(m)

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
