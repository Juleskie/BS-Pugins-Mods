"""
This module is the public face of BombSquad.
For most modding purposes, the functionality exposed here is all you should need.
"""

# pull in our 'public' stuff
from bsInternal import *
from bsUtils import checkTime, getLanguage, writeConfig, openURL, WeakCall, Call, animate, animateArray,\
    Lstr, uni, utf8, playMusic, PopupText, getConfig, getNormalizedColor, isPointInBox, getTimeString,\
    statAdd ,printError, printErrorOnce, printException, getSharedObject, isBrowserLikelyAvailable, OnScreenTimer, OnScreenCountdown
from bsGame import Team, OutOfBoundsMessage, DieMessage, StandMessage, PickUpMessage, DropMessage, PickedUpMessage,\
    DroppedMessage, ShouldShatterMessage, ImpactDamageMessage, FreezeMessage, ThawMessage, HealMessage, FireMessage, DizzyMessage, DiceMessage, HitMessage, TeslaMessage,\
    Actor, NodeActor, Session, Activity, GameActivity
from bsCoopGame import CoopSession, CoopGameActivity, Level
from bsTeamGame import TeamBaseSession, FreeForAllSession, TeamsSession, TeamGameActivity, TeamGameResults
from bsAchievement import *
from bsBomb import Bomb, TNTSpawner, BombFactory, Blast
from bsPowerup import Powerup, PowerupMessage, PowerupAcceptMessage, PowerupFactory
from bsInteractive import InteractiveFactory, Bumper, BumperSpawner, MovingPlatform, MovingPlatformSpawner, Dice, Particle, Glue, StickyNet, BouncyBall, Blocker
from bsMap import Map, getMapsSupportingPlayType
from bsFlag import FlagFactory, Flag, FlagPickedUpMessage, FlagDeathMessage, FlagDroppedMessage
from bsScoreBoard import ScoreBoard
from bsScoreSet import PlayerScoredMessage
from bsSpaz import SpazFactory, RespawnIcon, Spaz, PlayerSpaz, PlayerSpazHurtMessage, PlayerSpazDeathMessage, BotSet, SpazBot, BunnyBot, SpazBotDeathMessage, SpazBotPunchedMessage, BomberBot, BomberBotLame, BomberBotStaticLame, BomberBotStatic, BomberBotPro,\
                   BomberBotProShielded, BomberBotProStatic, BomberBotProStaticShielded, WizardBot, ToughGuyBot, ToughGuyBotLame, BonesBot, ToughGuyBotPro, ToughGuyBotProShielded,\
                   NinjaBot, NinjaBotPro, NinjaBotProShielded, KnightBot, KnightBotPro, KnightBotProShielded, ChickBot, ChickBotStatic, PuckBot, ChickBotPro, PixelBotStatic, AgentBotPro, FrostyBotPro,\
                   ChickBotProShielded, ChickBotLame, ArmoredBot, ChickBotStaticLame, NinjaBotLame, MelBot, MelBotLame, MelBotStaticLame, MelDuperBot, MelBotStatic, PirateBot, PirateBotNoTimeLimit, PirateBotShielded, PirateBotRadius, FrostyBot, FrostyBotStatic,\
                   FrostyBotShielded, AgentBot, AgentBotShielded, CyborgBot, CyborgBotPro, SpyBot, LooieBot, LooieBotShielded, BunnyBotShielded, LooieBotPro, ZillBotPro,\
                   AliBot, TNTBot, PixelBot, PixelBotPro, PascalBot, AliBotPro, BonesBotPro, BearBot, BearBotShielded, DemonBot, ZillBot, JuiceBot, WizardBotStatic, WizardBotPro, SoldierBot, RonnieBot,\
                   RonnieBotStatic, SpyBotPro, SpyBotStatic, CowBotStatic, PascalBotShielded, JesterBot, KlayBot, KlayBotPro, KlayBotStatic, KlayBotProShielded, SantaBot, CyborgBotStatic, CowBot, CowBotShielded, DiceBot
from bsVector import Vector

# change everything's listed module to ours
import bs
for obj in [getattr(bs,attr) for attr in dir(bs) if not attr.startswith('_')]:
    if getattr(obj,'__module__',None) not in [None,'bs']: obj.__module__ = 'bs'
del bs
del obj
del attr
