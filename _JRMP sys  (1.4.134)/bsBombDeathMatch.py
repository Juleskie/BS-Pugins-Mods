import bs


def bsGetAPIVersion():
    return 4


def bsGetGames():
    return [BombsGame]


class BombsGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Bomb Match!'

    @classmethod
    def getDescription(cls, sessionType):
        return 'Throw bombs to enemies and blow them up!'

    @classmethod
    def supportsSessionType(cls, sessionType):
        return True if (issubclass(sessionType, bs.TeamsSession)
                        or issubclass(sessionType, bs.FreeForAllSession)) else False

    @classmethod
    def getSupportedMaps(cls,sessionType):
        return bs.getMapsSupportingPlayType("melee")

    @classmethod
    def getSettings(cls,sessionType):
        return [("Kills to Win Per Player",{'minValue':1,'default':5,'increment':1}),
                ("Time Limit",{'choices':[('None',0),('1 Minute',60),
                                        ('2 Minutes',120),('5 Minutes',300),
                                        ('10 Minutes',600),('20 Minutes',1200)],'default':0}),
                ("Respawn Times",{'choices':[('Shorterer',0.01),('Shorter',0.25),('Normal',1.0),('Long',2.0),('Longer',4.0)],'default':1.0}),
                ("Bomb Limit",{'minValue':1,'default':2,'increment':1}),
                ("Epic Mode",{'default':False}),
                ("Enable Pickup",{'default':False}),
                ("Bomb Type",{'choices':[('Normal Bombs',1),('Ice Bombs',2),('Fire Bombs',3),('Sticky Bombs',4),('Impact Bombs',5),('Combat Bombs',6),
                                        ('Magnet Bombs',7),('Knocker Bombs',8),('Ranger Bombs',9),('Radius Bombs',10),('Healing Bombs',11),('Grenades',12),('Snowballs',13),
                                        ('Dynamites',14),('Dizzy Cakes',15),('Scatter Bombs',16),('Candy Bombs',17),('Digital Bombs',18),('Light Bombs',19)],'default':1}),
                ("Bombs Radius",{'minValue':0.1,'default':2.0,'increment':0.1})]


    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)
        if self.settings['Epic Mode']: self._isSlowMotion = True

        # print messages when players die since it matters here..
        self.announcePlayerDeaths = True

        self._scoreBoard = bs.ScoreBoard()

    def getInstanceDescription(self):
        return ('Crush ${ARG1} of your enemies.',self._scoreToWin)

    def getInstanceScoreBoardDescription(self):
        return ('kill ${ARG1} enemies',self._scoreToWin)

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Epic' if self.settings['Epic Mode'] else 'Onslaught')

    def onTeamJoin(self, team):
        team.gameData['score'] = 0
        if self.hasBegun(): self._updateScoreBoard()

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self.setupStandardTimeLimit(self.settings['Time Limit'])
        self.setupStandardPowerupDrops(enablePowerups=False,enableTNT=False,enableHazards=True)
        if len(self.teams) > 0:
            self._scoreToWin = self.settings['Kills to Win Per Player'] * max(1,max(len(t.players) for t in self.teams))
        else: self._scoreToWin = self.settings['Kills to Win Per Player']
        self._updateScoreBoard()
        self._dingSound = bs.getSound('dingSmall')

    def spawnPlayer(self, player):

        spaz = self.spawnPlayerSpaz(player)

        # lets reconnect this player's controls to this
        # spaz but *without* the ability to pick stuff up
        spaz.connectControlsToPlayer(enablePunch=False,
                                     enableBomb=True,
                                     enablePickUp=True if self.settings["Enable Pickup"] else False)

        # give players permanent triple impact bombs and wire them up
        # to tell us when they drop a bomb
        if self.settings["Bomb Type"]  == 1: bomb = 'normal'
        if self.settings["Bomb Type"]  == 2: bomb = 'ice'
        if self.settings["Bomb Type"]  == 3: bomb = 'fire'
        if self.settings["Bomb Type"]  == 4: bomb = 'sticky'
        if self.settings["Bomb Type"]  == 5: bomb = 'impact'
        if self.settings["Bomb Type"]  == 6: bomb = 'combat'
        if self.settings["Bomb Type"]  == 7: bomb = 'magnet'
        if self.settings["Bomb Type"]  == 8: bomb = 'knocker'
        if self.settings["Bomb Type"]  == 9: bomb = 'ranger'
        if self.settings["Bomb Type"]  == 10: bomb = 'radius'
        if self.settings["Bomb Type"]  == 11: bomb = 'healing'
        if self.settings["Bomb Type"]  == 12: bomb = 'grenade'
        if self.settings["Bomb Type"]  == 13: bomb = 'snowball'
        if self.settings["Bomb Type"]  == 14: bomb = 'dynamite'
        if self.settings["Bomb Type"]  == 15: bomb = 'cake'
        if self.settings["Bomb Type"]  == 16: bomb = 'scatter'
        if self.settings["Bomb Type"]  == 17: bomb = 'candy'
        if self.settings["Bomb Type"]  == 18: bomb = 'fraction'
        if self.settings["Bomb Type"]  == 19: bomb = 'light'
        spaz.bombType = bomb
        spaz.blastRadius = self.settings['Bombs Radius']
        spaz.setBombCount(self.settings['Bomb Limit'])

    def handleMessage(self, m):
        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self, m) # augment standard behavior

            player = m.spaz.getPlayer()
            self.respawnPlayer(player)

            killer = m.killerPlayer
            if killer is None: return

            # handle team-kills
            if killer.getTeam() is player.getTeam():

                # in free-for-all, killing yourself loses you a point
                if isinstance(self.getSession(), bs.FreeForAllSession):
                    player.getTeam().gameData['score'] = max(0, player.getTeam().gameData['score']-1)

                # in teams-mode it gives a point to the other team
                else:
                    bs.playSound(self._dingSound)
                    for team in self.teams:
                        if team is not killer.getTeam():
                            team.gameData['score'] += 1

            # killing someone on another team nets a kill
            else:
                killer.getTeam().gameData['score'] += 1
                bs.playSound(self._dingSound)
                # in FFA show our score since its hard to find on the scoreboard
                try: killer.actor.setScoreText(str(killer.getTeam().gameData['score'])+'/'+str(self._scoreToWin),color=killer.getTeam().color,flash=True)
                except Exception: pass

            self._updateScoreBoard()

            # if someone has won, set a timer to end shortly
            # (allows the dust to clear and draws to occur if deaths are close enough)
            if any(team.gameData['score'] >= self._scoreToWin for team in self.teams):
                bs.gameTimer(500, self.endGame)

        else: bs.TeamGameActivity.handleMessage(self, m)

    def _updateScoreBoard(self):
        for team in self.teams:
            self._scoreBoard.setTeamValue(team, team.gameData['score'], self._scoreToWin)

    def endGame(self):
        results = bs.TeamGameResults()
        for t in self.teams: results.setTeamScore(t, t.gameData['score'])
        self.end(results=results)
