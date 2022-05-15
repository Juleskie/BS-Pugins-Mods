import bs
import bsUI
import time
import bsInternal
import copy
import bsUtils
import random

class UnlinkAccountsWindow(bsUI.Window):

    def __init__(self, transition='inRight', originWidget=None):
        if originWidget is not None:
            self._transitionOut = 'outScale'
            scaleOrigin = originWidget.getScreenSpaceCenter()
            transition = 'inScale'
        else:
            self._transitionOut = 'outRight'
            scaleOrigin = None
            transition = 'inRight'
        bgColor = (0.4,0.4,0.5)
        self._width = 540
        self._height = 350
        self._scrollWidth = 400
        self._scrollHeight = 200
        baseScale=2.0 if bsUI.gSmallUI else 1.6 if bsUI.gMedUI else 1.1
        self._rootWidget = bs.containerWidget(size=(self._width,self._height),
                                              transition=transition, scale=baseScale,
                                              scaleOriginStackOffset=scaleOrigin,
                                              stackOffset=(0,-10) if bsUI.gSmallUI else (0,0))
        self._cancelButton = bs.buttonWidget(parent=self._rootWidget, position=(30, self._height-50),
                                             size=(50,50), scale=0.7,
                                             label='', color=bgColor,
                                             onActivateCall=self._cancel, autoSelect=True,
                                             icon=bs.getTexture('crossOut'), iconScale=1.2)
        bs.textWidget(parent=self._rootWidget,position=(self._width*0.5, self._height*0.88), size=(0,0),
                      text=bs.Lstr(resource='accountSettingsWindow.unlinkAccountsInstructionsText'),
                      maxWidth=self._width*0.7,
                      color=bsUI.gInfoTextColor,
                      hAlign='center',vAlign='center')
        bs.containerWidget(edit=self._rootWidget, cancelButton=self._cancelButton)

        self._scrollWidget = bs.scrollWidget(parent=self._rootWidget,
                                             highlight=False,
                                             position=((self._width-self._scrollWidth) * 0.5, self._height - 85-self._scrollHeight),
                                             size=(self._scrollWidth, self._scrollHeight))
        bs.containerWidget(edit=self._scrollWidget, claimsLeftRight=True)
        self._columnWidget = bs.columnWidget(parent=self._scrollWidget, leftBorder=10)

        ourAccountID = bsInternal._getPublicLinkAccountID()
        if ourAccountID is None:
            entries = []
        else:
            accountInfos = bsInternal._getAccountMiscReadVal2('linkedAccounts2', [])
            entries = [{'name':ai['d'], 'id':ai['id']} for ai in accountInfos if ai['id'] != ourAccountID]
        
        # (avoid getting our selection stuck on an empty column widget)
        if len(entries) == 0: bs.containerWidget(edit=self._scrollWidget, selectable=False)
        for i, entry in enumerate(entries):
            t = bs.textWidget(parent=self._columnWidget, selectable=True,
                              text=entry['name'], size=(self._scrollWidth - 30, 30),
                              autoSelect=True, clickActivate=True,
                              onActivateCall=bs.Call(self._onEntrySelected, entry))
            bs.widget(edit=t, leftWidget=self._cancelButton)
            if i == 0:
                bs.widget(edit=t, upWidget=self._cancelButton)

    def _onEntrySelected(self, entry):
        bs.screenMessage(bs.Lstr(resource='pleaseWaitText',fallbackResource='requestingText'),color=(0,1,0))
        bsInternal._addTransaction({'type':'ACCOUNT_UNLINK_REQUEST', 'accountID':entry['id'], 'expireTime':time.time()+5})
        bsInternal._runTransactions()
        bs.containerWidget(edit=self._rootWidget, transition=self._transitionOut)
        
    def _cancel(self):
        bs.containerWidget(edit=self._rootWidget, transition=self._transitionOut)
        
class LinkAccountsWindow(bsUI.Window):

    def __init__(self,transition='inRight',originWidget=None):
        if originWidget is not None:
            self._transitionOut = 'outScale'
            scaleOrigin = originWidget.getScreenSpaceCenter()
            transition = 'inScale'
        else:
            self._transitionOut = 'outRight'
            scaleOrigin = None
            transition = 'inRight'
        bgColor = (0.4,0.4,0.5)
        self._width = 560
        self._height = 420
        baseScale=1.65 if bsUI.gSmallUI else 1.5 if bsUI.gMedUI else 1.1
        self._rootWidget = bs.containerWidget(size=(self._width,self._height),transition=transition,scale=baseScale,
                                              scaleOriginStackOffset=scaleOrigin,
                                              stackOffset=(0,-10) if bsUI.gSmallUI else (0,0))
        self._cancelButton = bs.buttonWidget(parent=self._rootWidget,position=(40,self._height-45),size=(50,50),scale=0.7,
                                             label='',color=bgColor,
                                             onActivateCall=self._cancel,autoSelect=True,
                                             icon=bs.getTexture('crossOut'),iconScale=1.2)
        bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.56),size=(0,0),
                      text=bs.Lstr(resource='accountSettingsWindow.linkAccountsInstructionsNewText',subs=[('${COUNT}',str(bsInternal._getAccountMiscReadVal('maxLinkAccounts',5)))]),
                      maxWidth=self._width*0.9,
                      color=bsUI.gInfoTextColor,
                      maxHeight=self._height*0.6,hAlign='center',vAlign='center')
        bs.containerWidget(edit=self._rootWidget, cancelButton=self._cancelButton)
        bs.buttonWidget(parent=self._rootWidget,position=(40,30),size=(200,60),
                        label=bs.Lstr(resource='accountSettingsWindow.linkAccountsGenerateCodeText'),
                        autoSelect=True,
                        onActivateCall=self._generatePress)
        self._enterCodeButton = bs.buttonWidget(parent=self._rootWidget,position=(self._width-240,30),size=(200,60),
                                                label=bs.Lstr(resource='accountSettingsWindow.linkAccountsEnterCodeText'),
                                                autoSelect=True,
                                                onActivateCall=self._enterCodePress)
    def _generatePress(self):
        if bsInternal._getAccountState() != 'SIGNED_IN':
            bsUI.showSignInPrompt()
            return
        bs.screenMessage(bs.Lstr(resource='gatherWindow.requestingAPromoCodeText'),color=(0,1,0))
        bsInternal._addTransaction({'type':'ACCOUNT_LINK_CODE_REQUEST','expireTime':time.time()+5})
        bsInternal._runTransactions()

    def _enterCodePress(self):
        bsUI.PromoCodeWindow(modal=True,originWidget=self._enterCodeButton)
        bs.containerWidget(edit=self._rootWidget,transition=self._transitionOut)
        
    def _cancel(self):
        bs.containerWidget(edit=self._rootWidget,transition=self._transitionOut)

def _handleUIRemotePress():
    #dCount = bsInternal._getLocalActiveInputDevicesCount()
    env = bs.getEnvironment()
    if env['onTV'] and (env['platform'] == 'android' and env['subplatform'] == 'alibaba'):
        GetBSRemoteWindow()
    else:
        bs.screenMessage(bs.Lstr(resource="internal.controllerForMenusOnlyText"),color=(1,0,0))
        bs.playSound(bs.getSound('error'))
    
class GetBSRemoteWindow(bsUI.PopupWindow):

    def __init__(self):

        # position=originWidget.getScreenSpaceCenter()
        position=(0,0)
        
        scale = 2.3 if bsUI.gSmallUI else 1.65 if bsUI.gMedUI else 1.23
        self._transitioningOut = False
        
        self._width = 570
        self._height = 350

        bgColor = (0.5,0.4,0.6)
        
        bsUI.PopupWindow.__init__(self,position=position,size=(self._width,self._height),
                             scale=scale,bgColor=bgColor)

        env = bs.getEnvironment()

        self._cancelButton = bs.buttonWidget(parent=self._rootWidget,position=(50,self._height-30),size=(50,50),scale=0.5,
                                             label='',color=bgColor,
                                             onActivateCall=self._onCancelPress,autoSelect=True,
                                             icon=bs.getTexture('crossOut'),iconScale=1.2)

        env = bs.getEnvironment()
        if (env['platform'] == 'android' and env['subplatform'] == 'alibaba'):
            txt = ('\xe8\xbf\x99\xe6\x98\xaf\xe4\xb8\x80\xe4\xb8\xaa\xe5\x8f\xaf\xe4\xbb\xa5\xe5\x92\x8c\xe5\xae\xb6\xe4\xba\xba\xe6\x9c\x8b\xe5\x8f\x8b\xe4\xb8\x80\xe8\xb5\xb7\xe7\x8e\xa9\xe7\x9a\x84\xe6\xb8\xb8\xe6\x88\x8f,\xe5\x90\x8c\xe6\x97\xb6\xe6\x94\xaf\xe6\x8c\x81\xe8\x81\x94 \xe2\x80\xa8\xe7\xbd\x91\xe5\xaf\xb9\xe6\x88\x98\xe3\x80\x82\n'
                   '\xe5\xa6\x82\xe6\xb2\xa1\xe6\x9c\x89\xe6\xb8\xb8\xe6\x88\x8f\xe6\x89\x8b\xe6\x9f\x84,\xe5\x8f\xaf\xe4\xbb\xa5\xe4\xbd\xbf\xe7\x94\xa8\xe7\xa7\xbb\xe5\x8a\xa8\xe8\xae\xbe\xe5\xa4\x87\xe6\x89\xab\xe7\xa0\x81\xe4\xb8\x8b\xe8\xbd\xbd\xe2\x80\x9c\xe9\x98\xbf\xe9\x87\x8c\xc2\xa0TV\xc2\xa0\xe5\x8a\xa9\xe6\x89\x8b\xe2\x80\x9d\xe7\x94\xa8 \xe6\x9d\xa5\xe4\xbb\xa3\xe6\x9b\xbf\xe5\xa4\x96\xe8\xae\xbe\xe3\x80\x82\n'
                   '\xe6\x9c\x80\xe5\xa4\x9a\xe6\x94\xaf\xe6\x8c\x81\xe6\x8e\xa5\xe5\x85\xa5\xc2\xa08\xc2\xa0\xe4\xb8\xaa\xe5\xa4\x96\xe8\xae\xbe')
            bs.textWidget(parent=self._rootWidget, size=(0,0), hAlign='center', vAlign='center', maxWidth = self._width * 0.9,
                          position=(self._width*0.5, 60), text=txt)
            bs.imageWidget(parent=self._rootWidget, position=(self._width - 260, self._height*0.63-100), size=(200, 200),
                           texture=bs.getTexture('aliControllerQR'))
            bs.imageWidget(parent=self._rootWidget, position=(40, self._height*0.58-100), size=(230, 230),
                           texture=bs.getTexture('multiplayerExamples'))
        else:
            bs.imageWidget(parent=self._rootWidget, position=(self._width*0.5-110, self._height*0.67-110), size=(220, 220),
                           texture=bs.getTexture('multiplayerExamples'))
            bs.textWidget(parent=self._rootWidget, size=(0,0), hAlign='center', vAlign='center', maxWidth = self._width * 0.9,
                          position=(self._width*0.5, 60),
                          text=bs.Lstr(resource='remoteAppInfoShortText',subs=[('${APP_NAME}',bs.Lstr(resource='titleText')),('${REMOTE_APP_NAME}',bs.Lstr(resource='remote_app.app_name'))]))
        # bs.imageWidget(parent=self._rootWidget, position=(self._width*0.5-150, self._height*0.5-150), size=(300, 300),
        #                texture=qrTex)
        
    def _onCancelPress(self):
        self._transitionOut()
        
    def _transitionOut(self):
        if not self._transitioningOut:
            self._transitioningOut = True
            bs.containerWidget(edit=self._rootWidget,transition='outScale')

    def onPopupCancel(self):
        bs.playSound(bs.getSound('swish'))
        self._transitionOut()
        
class ChallengeEntryWindow(bsUI.PopupWindow):

    def __init__(self, challengeID, challengeActivity=None,
                 position=(0,0), delegate=None, scale=None, offset=(0,0),
                 onCloseCall=None):

        self._challengeID = challengeID

        self._onCloseCall = onCloseCall
        if scale is None: scale = 2.3 if bsUI.gSmallUI else 1.65 if bsUI.gMedUI else 1.23
        self._delegate = delegate
        self._transitioningOut = False

        self._challengeActivity = challengeActivity
        
        self._width = 340
        self._height = 290

        self._canForfeit = False
        self._forfeitButton = None

        challenge = bsUI._getCachedChallenge(self._challengeID)
        # this stuff shouldn't change..
        if challenge is None:
            self._canForfeit = False
            self._prizeTickets = 0
            self._prizeTrophy = None
            self._level = 0
            self._waitTickets = 0
        else:
            self._canForfeit = challenge['canForfeit']
            self._prizeTrophy = challenge['prizeTrophy']
            self._prizeTickets = challenge['prizeTickets']
            self._level = challenge['level']
            t = time.time()
            self._waitTickets = max(1,int(challenge['waitTickets'] * (1.0 - (t-challenge['waitStart'])/(challenge['waitEnd']-challenge['waitStart']))))
            
        
        self._bgColor = (0.5,0.4,0.6)
        
        # creates our _rootWidget
        bsUI.PopupWindow.__init__(self,position=position,size=(self._width,self._height),
                                  scale=scale,bgColor=self._bgColor,offset=offset)
        self._state = None
        self._updateTimer = bs.Timer(1000,bs.WeakCall(self._update),repeat=True,timeType='real')
        self._update()

    def _rebuildForState(self,newState):

        if self._state is not None:
            self._saveState()
        
        # clear out previous state (if any)
        children = self._rootWidget.getChildren()
        for c in children: c.delete()

        self._state = newState
        
        # print 'REBUILDING FOR STATE',self._state
        self._cancelButton = bs.buttonWidget(parent=self._rootWidget,position=(20,self._height-30),size=(50,50),scale=0.5,
                                             label='',color=self._bgColor,
                                             onActivateCall=self._onCancel,autoSelect=True,
                                             icon=bs.getTexture('crossOut'),iconScale=1.2)
        titleScale = 0.6
        titleColor = (1,1,1,0.4)
        showPrizes = False
        showLevel = False
        showForfeitButton = False
        
        if self._state == 'error':
            titleStr = bs.Lstr(resource='coopSelectWindow.challengesText')
            bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.5),size=(0,0),hAlign='center',vAlign='center',
                          scale=0.7,text=bs.Lstr(resource='errorText'),maxWidth=self._width*0.8)
        elif self._state == 'skipWaitNextChallenge':
            titleStr = bs.Lstr(resource='coopSelectWindow.nextChallengeText')
            #showLevel = True
            bWidth = 140
            bHeight = 130
            imgWidth = 80
            imgHeight = 80
            bPos = (self._width*0.5,self._height*0.52)
            b = bs.buttonWidget(parent=self._rootWidget,position=(bPos[0]-bWidth*0.5,bPos[1]-bHeight*0.5),
                                onActivateCall=bs.WeakCall(self._load),
                                label='',size=(bWidth,bHeight),buttonType='square',autoSelect=True)
            bs.containerWidget(edit=self._rootWidget,selectedChild=b)
            bs.textWidget(parent=self._rootWidget,drawController=b,hAlign='center',vAlign='center',
                          text=bs.Lstr(resource='coopSelectWindow.skipWaitText'),
                          size=(0,0),maxWidth=bWidth*0.8,
                          color=(0.75,1.0,0.7),position=(bPos[0],bPos[1]-bHeight*0.0),scale=0.9)
            bs.textWidget(parent=self._rootWidget,drawController=b,hAlign='center',vAlign='center',
                          text=bs.getSpecialChar('ticket')+str(self._waitTickets),size=(0,0),scale=0.6,
                          color=(1,0.5,0),position=(bPos[0],bPos[1]-bHeight*0.23))
            # bs.imageWidget(parent=self._rootWidget,drawController=b,size=(80,80),
            #                position=(bPos[0]-imgWidth*0.5,bPos[1]-imgHeight*0.5),texture=bs.getTexture('tickets'))
            #showPrizes = True
        elif self._state == 'skipWaitNextPlay':
            showLevel = True
            showForfeitButton = True
            bWidth = 140
            bHeight = 130
            imgWidth = 80
            imgHeight = 80
            bPos = (self._width*0.5,self._height*0.52)
            b = bs.buttonWidget(parent=self._rootWidget,position=(bPos[0]-bWidth*0.5,bPos[1]-bHeight*0.5),
                                onActivateCall=bs.WeakCall(self._play),
                                label='',size=(bWidth,bHeight),buttonType='square',autoSelect=True)
            bs.widget(edit=b,upWidget=self._cancelButton)
            bs.containerWidget(edit=self._rootWidget,selectedChild=b)
            bs.textWidget(parent=self._rootWidget,drawController=b,hAlign='center',vAlign='center',
                          text=bs.Lstr(resource='coopSelectWindow.playNowText'),size=(0,0),maxWidth=bWidth*0.8,
                          color=(0.75,1.0,0.7),position=(bPos[0],bPos[1]-bHeight*0.0),scale=0.9)
            bs.textWidget(parent=self._rootWidget,drawController=b,hAlign='center',vAlign='center',
                          text=bs.getSpecialChar('ticket')+str(self._waitTickets),size=(0,0),scale=0.6,
                          color=(1,0.5,0),position=(bPos[0],bPos[1]-bHeight*0.23))
            # bs.imageWidget(parent=self._rootWidget,drawController=b,size=(80,80),
            #                position=(bPos[0]-imgWidth*0.5,bPos[1]-imgHeight*0.5),texture=bs.getTexture('tickets'))
            showPrizes = True
            
        elif self._state == 'freePlay':
            showLevel = True
            showForfeitButton = True
            bWidth = 140
            bHeight = 130
            b = bs.buttonWidget(parent=self._rootWidget,position=(self._width*0.5-bWidth*0.5,self._height*0.52-bHeight*0.5),
                                onActivateCall=bs.WeakCall(self._play),
                                label=bs.Lstr(resource='playText'),size=(bWidth,bHeight),buttonType='square',autoSelect=True)
            bs.widget(edit=b,upWidget=self._cancelButton)
            bs.containerWidget(edit=self._rootWidget,selectedChild=b)
            showPrizes = True
        elif self._state == 'ended':
            titleStr = bs.Lstr(resource='coopSelectWindow.challengesText')
            bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.5),size=(0,0),hAlign='center',vAlign='center',
                          scale=0.7,text=bs.Lstr(resource='challengeEndedText'),maxWidth=self._width*0.8)
        else:
            titleStr = ''
            print 'Unrecognized state for ChallengeEntryWindow:',self._state
        
        if showLevel:
            titleColor = (1,1,1,0.7)
            titleStr = 'Meteor Shower Blah'
            titleScale = 0.7
            bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.86),
                          size=(0,0),hAlign='center',vAlign='center',color=(0.8,0.8,0.4,0.7),
                          flatness=1.0,scale=0.55,text=bs.Lstr(resource='levelText',subs=[('${NUMBER}',str(self._level))]),maxWidth=self._width*0.8)

        self._titleText = bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height-20),size=(0,0),hAlign='center',vAlign='center',
                                        scale=titleScale,text=titleStr,maxWidth=200,color=titleColor)

        if showForfeitButton:
            bWidth = 40
            bHeight = 25
            self._forfeitButton = bs.buttonWidget(parent=self._rootWidget,position=(self._width-bWidth-16,self._height-bHeight-10),
                                                  label=bs.Lstr(resource='coopSelectWindow.forfeitText'),size=(bWidth,bHeight),buttonType='square',
                                                  color=(0.6,0.45,0.6),
                                                  onActivateCall=bs.WeakCall(self._onForfeitPress),
                                                  textColor=(0.65,0.55,0.65),
                                                  autoSelect=True)
        else: self._forfeitButton = None
            
        if showPrizes:
            bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.24),size=(0,0),hAlign='center',vAlign='center',
                          flatness=1.0,scale=0.6,text=bs.Lstr(resource='coopSelectWindow.prizesText'),maxWidth=self._width*0.8,color=(0.8,0.8,1,0.5)),
            prizes = []
            if self._prizeTrophy is not None: prizes.append(bs.getSpecialChar('trophy'+str(self._prizeTrophy)))
            if self._prizeTickets != 0: prizes.append(bs.getSpecialChar('ticketBacking')+str(self._prizeTickets))
            bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.13),size=(0,0),hAlign='center',vAlign='center',
                          scale=0.8,flatness=1.0,color=(0.7,0.7,0.7,1),
                          text='   '.join(prizes),maxWidth=self._width*0.8)

        self._restoreState()
            
    def _load(self):
        self._transitionOut()
        bs.screenMessage("WOULD LOAD CHALLENGE: "+self._challengeID,color=(0,1,0))
        
    def _play(self):
        self._transitionOut()
        bs.screenMessage("WOULD PLAY CHALLENGE: "+self._challengeID,color=(0,1,0))

    def _onForfeitPress(self):
        if self._canForfeit:
            bsUI.ConfirmWindow(bs.Lstr(resource='coopSelectWindow.forfeitConfirmText'),
                               bs.WeakCall(self._forfeit),originWidget=self._forfeitButton,
                               width=400,height=120)
        else:
            bs.screenMessage(bs.Lstr(resource='coopSelectWindow.forfeitNotAllowedYetText'),color=(1,0,0))
            bs.playSound(bs.getSound('error'))

    def _forfeit(self):
        self._transitionOut()
        bs.screenMessage("WOULD FORFEIT CHALLENGE: "+self._challengeID,color=(0,1,0))
        
    def _update(self):
        # print 'UPDATE',bs.getRealTime()

        # figure out what our state should be based on our current cached challenge data
        challenge = bsUI._getCachedChallenge(self._challengeID)
        if challenge is None: newState = 'error'
        elif challenge['end'] <= time.time(): newState = 'ended'
        elif challenge['waitEnd'] > time.time():
            if challenge['waitType'] == 'nextChallenge': newState = 'skipWaitNextChallenge'
            else: newState = 'skipWaitNextPlay'
        else:
            newState = 'freePlay'

        # if our state is changing, rebuild..
        if self._state != newState:
            self._rebuildForState(newState)

        if self._forfeitButton is not None:
            bs.buttonWidget(edit=self._forfeitButton,
                            color=(0.6,0.45,0.6) if self._canForfeit else (0.6,0.57,0.6),
                            textColor=(0.65,0.55,0.65) if self._canForfeit else (0.5,0.5,0.5))
        
            
        
    def _onCancel(self):
        self._transitionOut()
        
    def _transitionOut(self):
        if not self._transitioningOut:
            self._transitioningOut = True
            self._saveState()
            bs.containerWidget(edit=self._rootWidget,transition='outScale')
            if self._onCloseCall is not None:
                self._onCloseCall()

    def onPopupCancel(self):
        bs.playSound(bs.getSound('swish'))
        self._onCancel()

    def _saveState(self):
        # print 'saving state'
        #sel = self._rootWidget.getSelectedChild()
        # if sel == self._payWithAdButton: selName = 'Ad'
        pass
        #sel = self._rootWidget.getSelectedChild()
        # if sel == self._payWithAdButton: selName = 'Ad'
        # else: selName = 'Tickets'
        #bs.getConfig()['Challenge Pay Selection'] = selName
        #bs.writeConfig()
    
    def _restoreState(self):
        # print 'restoring state'
        pass
        # try: selName = bs.getConfig()['Tournament Pay Selection']
        # except Exception: selName = 'Tickets'
        # if selName == 'Ad' and self._payWithAdButton is not None: sel = self._payWithAdButton
        # else: sel = self._payWithTicketsButton
        # bs.containerWidget(edit=self._rootWidget,selectedChild=sel)


class AccountLinkCodeWindow(bsUI.Window):
        
    def __init__(self,data):
        self._width = 350
        self._height = 200
        self._rootWidget = bs.containerWidget(size=(self._width,self._height),
                                              color=(0.45,0.63,0.15),
                                              transition='inScale',
                                              scale=1.8 if bsUI.gSmallUI else 1.35 if bsUI.gMedUI else 1.0)
        self._data = copy.deepcopy(data)
        bs.playSound(bs.getSound('cashRegister'))
        bs.playSound(bs.getSound('swish'))

        self._cancelButton = bs.buttonWidget(parent=self._rootWidget,scale=0.5,position=(40,self._height-40),size=(50,50),
                                             label='',onActivateCall=self.close,autoSelect=True,
                                             color=(0.45,0.63,0.15),
                                             icon=bs.getTexture('crossOut'),iconScale=1.2)
        bs.containerWidget(edit=self._rootWidget,cancelButton=self._cancelButton)
        
        t = bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.5),size=(0,0),
                          color=(1.0,3.0,1.0),scale=2.0,
                          hAlign="center",vAlign="center",text=data['code'],maxWidth=self._width*0.85)
    def close(self):
        bs.containerWidget(edit=self._rootWidget,transition='outScale')
        
class ServerDialogWindow(bsUI.Window):
        
    def __init__(self,data):

        self._dialogID = data['dialogID']
        txt = bs.Lstr(translate=('serverResponses',data['text']),subs=data.get('subs',[])).evaluate()
        txt = txt.strip()
        txtScale = 1.5
        txtHeight = bsInternal._getStringHeight(txt,suppressWarning=True) * txtScale
        self._width = 500
        self._height = 130+min(200,txtHeight)
        self._rootWidget = bs.containerWidget(size=(self._width,self._height),
                                              transition='inScale',
                                              scale=1.8 if bsUI.gSmallUI else 1.35 if bsUI.gMedUI else 1.0)
        self._startTime = bs.getRealTime()

        bs.playSound(bs.getSound('swish'))
        t = bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,70+(self._height-70)*0.5),size=(0,0),
                          color=(1.0,3.0,1.0),scale=txtScale,
                          hAlign="center",vAlign="center",
                          text=txt,
                          maxWidth=self._width*0.85,
                          maxHeight=(self._height-110))
        showCancel = data.get('showCancel',True)
        if showCancel:
            self._cancelButton = bs.buttonWidget(parent=self._rootWidget,position=(30,30),size=(160,60),
                                                 autoSelect=True,label=bs.Lstr(resource='cancelText'),
                                                 onActivateCall=self._cancelPress)
        else:
            self._cancelButton = None
        self._okButton = bs.buttonWidget(parent=self._rootWidget,position=((self._width-182) if showCancel else (self._width*0.5-80),30),size=(160,60),
                                             autoSelect=True,label=bs.Lstr(resource='okText'),
                                         onActivateCall=self._okPress)
        bs.containerWidget(edit=self._rootWidget,
                           cancelButton=self._cancelButton,
                           startButton=self._okButton,
                           selectedChild=self._okButton)

    def _okPress(self):
        if bs.getRealTime()-self._startTime < 1000:
            bs.playSound(bs.getSound('error'))
            return
        bsInternal._addTransaction({'type':'DIALOG_RESPONSE','dialogID':self._dialogID,'response':1})
        bs.containerWidget(edit=self._rootWidget,transition='outScale')
        
    def _cancelPress(self):
        if bs.getRealTime()-self._startTime < 1000:
            bs.playSound(bs.getSound('error'))
            return
        bsInternal._addTransaction({'type':'DIALOG_RESPONSE','dialogID':self._dialogID,'response':0})
        bs.containerWidget(edit=self._rootWidget,transition='outScale')
        
class ReportPlayerWindow(bsUI.Window):
        
    def __init__(self,accountID,originWidget):
        self._width = 550
        self._height = 220
        self._accountID = accountID
        self._transitionOut = 'outScale'
        scaleOrigin = originWidget.getScreenSpaceCenter()
        transition = 'inScale'
        
        self._rootWidget = bs.containerWidget(size=(self._width,self._height),
                                              transition='inScale',
                                              scaleOriginStackOffset=scaleOrigin,
                                              scale=1.8 if bsUI.gSmallUI else 1.35 if bsUI.gMedUI else 1.0)
        self._cancelButton = bs.buttonWidget(parent=self._rootWidget,scale=0.7,position=(40,self._height-50),
                                             size=(50,50),
                                             label='',onActivateCall=self.close,autoSelect=True,
                                             color=(0.4,0.4,0.5),
                                             icon=bs.getTexture('crossOut'),iconScale=1.2)
        bs.containerWidget(edit=self._rootWidget,cancelButton=self._cancelButton)
        
        t = bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.64),size=(0,0),
                          color=(1,1,1,0.8),scale=1.2,
                          hAlign="center",vAlign="center",
                          text=bs.Lstr(resource='reportThisPlayerReasonText'),
                          maxWidth=self._width*0.85)
        bs.buttonWidget(parent=self._rootWidget,size=(235,60),position=(20,30),label=bs.Lstr(resource='reportThisPlayerLanguageText'),
                        onActivateCall=self._onLanguagePress,autoSelect=True)
        bs.buttonWidget(parent=self._rootWidget,size=(235,60),position=(self._width-255,30),label=bs.Lstr(resource='reportThisPlayerCheatingText'),
                        onActivateCall=self._onCheatingPress,autoSelect=True)

    def _onLanguagePress(self):
        bsInternal._addTransaction({'type':'REPORT_ACCOUNT',
                                    'reason':'language',
                                    'account':self._accountID})
        import urllib
        body = bs.Lstr(resource='reportPlayerExplanationText').evaluate()
        bs.openURL('mailto:support@froemling.net?subject=BombSquad Player Report: '+self._accountID+'&body='+urllib.quote(bs.utf8(body)))
        self.close()

    def _onCheatingPress(self):
        bsInternal._addTransaction({'type':'REPORT_ACCOUNT',
                                    'reason':'cheating',
                                    'account':self._accountID})
        import urllib
        body = bs.Lstr(resource='reportPlayerExplanationText').evaluate()
        bs.openURL('mailto:support@froemling.net?subject=BombSquad Player Report: '+self._accountID+'&body='+urllib.quote(bs.utf8(body)))
        self.close()
        
    def close(self):
        bs.containerWidget(edit=self._rootWidget,transition='outScale')
        
class SharePlaylistResultsWindow(bsUI.Window):
        
    def __init__(self,name,data,origin=(0,0)):

        print("HAH")
        self._width = 450
        self._height = 300
        self._rootWidget = bs.containerWidget(size=(self._width,self._height),
                                              color=(0.45,0.63,0.15),
                                              transition='inScale',
                                              scale=1.8 if bsUI.gSmallUI else 1.35 if bsUI.gMedUI else 1.0)
        bs.playSound(bs.getSound('cashRegister'))
        bs.playSound(bs.getSound('swish'))

        self._cancelButton = bs.buttonWidget(parent=self._rootWidget,scale=0.7,position=(40, self._height-(40)),size=(50,50),
                                             label='',onActivateCall=self.close,autoSelect=True,
                                             color=(0.45,0.63,0.15),
                                             icon=bs.getTexture('crossOut'),iconScale=1.2)
        bs.containerWidget(edit=self._rootWidget,cancelButton=self._cancelButton)

        t = bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.745),size=(0,0),
                          color=bsUI.gInfoTextColor,scale=1.0,
                          flatness=1.0,
                          hAlign="center",vAlign="center",
                          text=bs.Lstr(resource='exportSuccessText',subs=[('${NAME}',name)]),
                          maxWidth=self._width*0.85)
        
        t = bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.645),size=(0,0),
                          color=bsUI.gInfoTextColor,scale=0.6,
                          flatness=1.0,
                          hAlign="center",vAlign="center",
                          text=bs.Lstr(resource='importPlaylistCodeInstructionsText'),
                          maxWidth=self._width*0.85)
        
        t = bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height*0.4),size=(0,0),
                          color=(1.0,3.0,1.0),scale=2.3,
                          hAlign="center",vAlign="center",text=data,maxWidth=self._width*0.85)
        
        
    def close(self):
        bs.containerWidget(edit=self._rootWidget,transition='outScale')

class SharePlaylistImportWindow(bsUI.PromoCodeWindow):

    def __init__(self,originWidget=None, onSuccessCallback=None):
        bsUI.PromoCodeWindow.__init__(self,modal=True,originWidget=originWidget)
        self._onSuccessCallback = onSuccessCallback
        
    def _onImportResponse(self,response):
        
        if response is None:
            bs.screenMessage(bs.Lstr(resource='errorText'),color=(1,0,0))
            bs.playSound(bs.getSound('error'))
            return

        if response['playlistType'] == 'Team Tournament':
            playlistTypeName = bs.Lstr(resource='playModes.teamsText')
        elif response['playlistType'] == 'Free-for-All':
            playlistTypeName = bs.Lstr(resource='playModes.freeForAllText')
        else:
            playlistTypeName = bs.Lstr(value=response['playlistType'])
            
            
        playlistTypeName
        bs.screenMessage(bs.Lstr(resource='importPlaylistSuccessText',
                                 subs=[('${TYPE}',playlistTypeName),('${NAME}',response['playlistName'])]),
                         color=(0,1,0))
        bs.playSound(bs.getSound('gunCocking'))
        if self._onSuccessCallback is not None:
            self._onSuccessCallback()
        bs.containerWidget(edit=self._rootWidget,transition=self._transitionOut)
        
    def _doEnter(self):
        bsInternal._addTransaction({'type':'IMPORT_PLAYLIST',
                                    'expireTime':time.time()+5,
                                    'code':bs.textWidget(query=self._textField)},
                                   callback=bs.WeakCall(self._onImportResponse))
        bsInternal._runTransactions()
        bs.screenMessage(bs.Lstr(resource='importingText'))
        
gHavePartyQueueWindow = False
        
class PartyQueueWindow(bsUI.Window):

    class Dude(object):
        def __init__(self, parent, distance, initialOffset, isPlayer, accountID, name):
            sc = 1.0
            self._lineLeft = parent._lineLeft
            self._lineWidth = parent._lineWidth
            self._lineBottom = parent._lineBottom
            self._targetDistance = distance
            self._distance = distance + initialOffset
            self._boostBrightness = 0.0
            self._debug = False
            
            position = (parent._lineLeft + self._lineWidth * (1.0 - self._distance), parent._lineBottom + 40)
            self._sc = sc = 1.1 if isPlayer else 0.6 + random.random() * 0.2
            self._yOffs = -30.0 if isPlayer else -47.0 * sc
            self._color = (0.2,1.0,0.2) if isPlayer else (0.5 + 0.3 * random.random(),
                                                          0.4 + 0.2 * random.random(),
                                                          0.5 + 0.3 * random.random())
            self._eyeColor = (0.7*1.0+0.3*self._color[0],
                              0.7*1.0+0.3*self._color[1],
                              0.7*1.0+0.3*self._color[2])
            self._bodyImage = bs.buttonWidget(parent=parent._rootWidget,
                                              selectable=True,label='',
                                              size=(sc*60,sc*80),color=self._color, texture=parent._lineupTex,
                                              modelTransparent=parent._lineup1TransparentModel)
            bs.buttonWidget(edit=self._bodyImage,onActivateCall=bs.WeakCall(parent.onAccountPress,accountID,self._bodyImage))
            bs.widget(edit=self._bodyImage,autoSelect=True)
            self._eyesImage = bs.imageWidget(parent=parent._rootWidget, size=(sc*36,sc*18), texture=parent._lineupTex,
                                             color=self._eyeColor, modelTransparent=parent._eyesModel)
            self._nameText = bs.textWidget(parent=parent._rootWidget, size=(0,0), shadow=0, flatness=1.0, text=name,
                                           maxWidth=100, hAlign='center', vAlign='center', scale=0.75, color=(1,1,1,0.6))
            self._updateImage()

            # DEBUG: vis target pos..
            if self._debug:
                self._bodyImageTarget = bs.imageWidget(parent=parent._rootWidget, size=(sc*60,sc*80),
                                                       color=self._color, texture=parent._lineupTex,
                                                       modelTransparent=parent._lineup1TransparentModel)
                self._eyesImageTarget = bs.imageWidget(parent=parent._rootWidget,size=(sc*36,sc*18),
                                                       texture=parent._lineupTex, color=self._eyeColor, modelTransparent=parent._eyesModel)
                # (updates our image positions)
                self.setTargetDistance(self._targetDistance)
            else:
                self._bodyImageTarget = self._eyesImageTarget = None
            
        def __del__(self):

            # ew.  our destructor here may get called as part of an internal widget tear-down.
            # running further widget calls here can quietly break stuff, so we need to push
            # a deferred call to kill these as necessary instead.
            # (should bulletproof internal widget code to give a clean error in this case)
            def killWidgets(widgets):
                for widget in widgets:
                    if widget is not None and widget.exists():
                        widget.delete()
            bs.pushCall(bs.Call(killWidgets,[self._bodyImage,self._eyesImage,self._bodyImageTarget,self._eyesImageTarget,self._nameText]))

        def setTargetDistance(self, dist):
            self._targetDistance = dist
            if self._debug:
                sc = self._sc
                position = (self._lineLeft + self._lineWidth * (1.0 - self._targetDistance), self._lineBottom - 30)
                bs.imageWidget(edit=self._bodyImageTarget,position=(position[0]-sc*30,position[1]-sc*25-70))
                bs.imageWidget(edit=self._eyesImageTarget, position=(position[0]-sc*18,position[1]+sc*31-70))

        def step(self, smoothing):
            self._distance = smoothing * self._distance + (1.0 - smoothing) * self._targetDistance
            self._updateImage()
            self._boostBrightness *= 0.9
            
        def _updateImage(self):
            sc = self._sc
            position = (self._lineLeft + self._lineWidth * (1.0 - self._distance), self._lineBottom + 40)
            brightness = 1.0 + self._boostBrightness
            bs.buttonWidget(edit=self._bodyImage, position=(position[0]-sc*30,position[1]-sc*25+self._yOffs),
                           color=(self._color[0]*brightness,self._color[1]*brightness,self._color[2]*brightness))
            bs.imageWidget(edit=self._eyesImage, position=(position[0]-sc*18,position[1]+sc*31+self._yOffs),
                           color=(self._eyeColor[0]*brightness,self._eyeColor[1]*brightness,self._eyeColor[2]*brightness))
            bs.textWidget(edit=self._nameText, position=(position[0]-sc*0, position[1]+sc*40.0))
            
        def boost(self, amount, smoothing):
            self._distance = max(0.0, self._distance - amount)
            self._updateImage()
            self._lastBoostTime = time.time()
            self._boostBrightness += 0.6
            
    
    def __init__(self, queueID, address, port):
        global gHavePartyQueueWindow
        gHavePartyQueueWindow = True
        self._address = address
        self._port = port
        self._queueID = queueID
        self._width = 800
        self._height = 400
        self._lastConnectAttemptTime = None
        self._lastTransactionTime = None
        self._boostButton = None
        self._boostPrice = None
        self._boostLabel = None
        self._fieldShown = False
        self._dudes = []
        self._dudesByID = {}
        self._ticketsRemaining = None
        self._lineLeft = 40.0
        self._lineWidth = self._width - 190
        self._lineBottom = self._height * 0.4
        self._lineupTex = bs.getTexture('playerLineup')
        self._angryComputerTransparentModel = bs.getModel('angryComputerTransparent')
        self._angryComputerImage = None
        self._lineup1TransparentModel = bs.getModel('playerLineup1Transparent')
        self._lineup2TransparentModel = bs.getModel('playerLineup2Transparent')
        self._lineup3TransparentModel = bs.getModel('playerLineup3Transparent')
        self._lineup4TransparentModel = bs.getModel('playerLineup4Transparent')
        self._lineImage = None
        self._eyesModel = bs.getModel('plasticEyesTransparent')
        self._whiteTex = bs.getTexture('white')
        self._rootWidget = bs.containerWidget(size=(self._width,self._height),
                                              color=(0.45,0.63,0.15),
                                              transition='inScale',
                                              scale=1.4 if bsUI.gSmallUI else 1.2 if bsUI.gMedUI else 1.0)

        self._cancelButton = bs.buttonWidget(parent=self._rootWidget,scale=1.0,position=(60,self._height-80),size=(50,50),
                                             label='',onActivateCall=self.close,autoSelect=True,
                                             color=(0.45,0.63,0.15),
                                             icon=bs.getTexture('crossOut'),iconScale=1.2)
        bs.containerWidget(edit=self._rootWidget,cancelButton=self._cancelButton)
        
        self._titleText = bs.textWidget(parent=self._rootWidget, position=(self._width*0.5,self._height*0.55), size=(0,0),
                                        color=(1.0,3.0,1.0), scale=1.3,
                                        hAlign="center", vAlign="center",
                                        text=bs.Lstr(resource='internal.connectingToPartyText'),
                                        maxWidth=self._width*0.65)

        self._ticketsText = bs.textWidget(parent=self._rootWidget, position=(self._width - 180,self._height - 20), size=(0,0),
                                          color=(0.2, 1.0, 0.2),
                                          scale=0.7,
                                          hAlign="center", vAlign="center",
                                          text='')


        # update at roughly 30fps
        self._updateTimer = bs.Timer(33,bs.WeakCall(self.update),repeat=True,timeType='real')
        self.update()

    def __del__(self):
        try:
            global gHavePartyQueueWindow
            gHavePartyQueueWindow = False
            bsInternal._addTransaction({'type':'PARTY_QUEUE_REMOVE','q':self._queueID})
            bsInternal._runTransactions()
        except Exception:
            bs.printException('err removing self from party queue')
        

    def onAccountPress(self, accountID, originWidget):
        if accountID is None:
            bs.playSound(bs.getSound('error'))
            return
        bsUI.AccountInfoWindow(accountID=accountID,
                               position=originWidget.getScreenSpaceCenter())
        
    def close(self):
        # update Discord Rich Presence
        import richPresence
        richPresence.discordMenu()
        bs.containerWidget(edit=self._rootWidget,transition='outScale')

    def _updateField(self, response):
        if self._angryComputerImage is None:
            self._angryComputerImage = bs.imageWidget(parent=self._rootWidget,
                                                      position=(self._width - 180,self._height * 0.5 - 65),
                                                      size=(150,150),
                                                      texture=self._lineupTex,
                                                      modelTransparent=self._angryComputerTransparentModel)
        if self._lineImage is None:
            self._lineImage = bs.imageWidget(parent=self._rootWidget,
                                             color=(0.0,0.0,0.0),
                                             opacity=0.2,
                                             position=(self._lineLeft,self._lineBottom - 2.0),
                                             size=(self._lineWidth,4.0),
                                             texture=self._whiteTex)

        # now go through the data they sent, creating dudes for us and our enemies as needed
        # and updating target positions on all of them..

        # mark all as unclaimed so we know which ones to kill off..
        for dude in self._dudes:
            dude.claimed = False
        
        # always have a dude for ourself..
        if -1 not in self._dudesByID:
            dude = self.Dude(self,response['d'],self._initialOffset, True, bsInternal._getAccountMiscReadVal2('resolvedAccountID', None),bsInternal._getAccountDisplayString())
            self._dudesByID[-1] = dude
            self._dudes.append(dude)
        else:
            self._dudesByID[-1].setTargetDistance(response['d'])
        self._dudesByID[-1].claimed = True

        # now create/destroy enemies
        for enemyID, enemyDistance, enemyAccountID, enemyName in response['e']:
            if enemyID not in self._dudesByID:
                dude = self.Dude(self,enemyDistance,self._initialOffset, False, enemyAccountID, enemyName)
                self._dudesByID[enemyID] = dude
                self._dudes.append(dude)
            else:
                self._dudesByID[enemyID].setTargetDistance(enemyDistance)
            self._dudesByID[enemyID].claimed = True

        # remove unclaimed dudes from both of our lists
        self._dudesByID = dict([item for item in self._dudesByID.items() if item[1].claimed])
        self._dudes = [dude for dude in self._dudes if dude.claimed]

        
    def _hideField(self):
        self._angryComputerImage.delete()
        self._angryComputerImage = None
        self._lineImage.delete()
        self._lineImage = None
        self._dudes = []
        self._dudesByID = {}
    
    def onUpdateResponse(self, response):
        if not self._rootWidget.exists():
            return

        if response is not None:

            shouldShowField = True if response.get('d') is not None else False

            self._smoothing = response['s']
            self._initialOffset = response['o']
            
            # if they gave us a position, show the field..
            if shouldShowField:
                bs.textWidget(edit=self._titleText,text=bs.Lstr(resource='waitingInLineText'),
                              position=(self._width*0.5,self._height*0.85))
                self._updateField(response)
                self._fieldShown = True
            if not shouldShowField and self._fieldShown:
                bs.textWidget(edit=self._titleText,text=bs.Lstr(resource='internal.connectingToPartyText'),
                              position=(self._width*0.5,self._height*0.55))
                self._hideField()
                self._fieldShown = False

            # if they told us there's a boost button, update..
            if response.get('bt') is not None:
                self._boostTickets = response['bt']
                self._boostStrength = response['bs']
                if self._boostButton is None:
                    self._boostButton = bs.buttonWidget(parent=self._rootWidget,scale=1.0,position=(self._width*0.5-75,20),size=(150,100),
                                                        buttonType='square',label='',onActivateCall=self.onBoostPress,
                                                        enableSound=False,
                                                        color=(0,1,0),
                                                        autoSelect=True)
                    self._boostLabel = bs.textWidget(parent=self._rootWidget, drawController=self._boostButton,
                                                     position=(self._width*0.5,88), size=(0,0),
                                                     color=(0.8,1.0,0.8), scale=1.5,
                                                     hAlign="center", vAlign="center",
                                                     text=bs.Lstr(resource='boostText'),
                                                     maxWidth=150)
                    self._boostPrice = bs.textWidget(parent=self._rootWidget, drawController=self._boostButton,
                                                     position=(self._width*0.5,50), size=(0,0),
                                                     color=(0,1,0), scale=0.9,
                                                     hAlign="center", vAlign="center",
                                                     text=bs.getSpecialChar('ticket')+str(self._boostTickets),
                                                     maxWidth=150)
            else:
                if self._boostButton is not None:
                    self._boostButton.delete()
                    self._boostButton = None
                if self._boostPrice is not None:
                    self._boostPrice.delete()
                    self._boostPrice = None
                if self._boostLabel is not None:
                    self._boostLabel.delete()
                    self._boostLabel = None
                    
            # if they told us to go ahead and try and connect, do so..
            # (note: servers will disconnect us if we try to connect before getting this go-ahead,
            # so don't get any bright ideas...)
            if response.get('c',False):
                # enforce a delay between connection attempts
                # (in case they're jamming on the boost button)
                now = time.time()
                if self._lastConnectAttemptTime is None or now - self._lastConnectAttemptTime > 10.0:
                    bsInternal._connectToParty(address=self._address, port=self._port, printProgress=False)
                    self._lastConnectAttemptTime = now
                
    def onBoostPress(self):
        if bsInternal._getAccountState() != 'SIGNED_IN':
            bsUI.showSignInPrompt()
            return
        
        if bsInternal._getAccountTicketCount() < self._boostTickets:
            bs.playSound(bs.getSound('error'))
            bsUI.showGetTicketsPrompt()
            return
            
        bs.playSound(bs.getSound('laserReverse'))
        bsInternal._addTransaction({'type':'PARTY_QUEUE_BOOST',
                                    't':self._boostTickets,
                                    'q':self._queueID},
                                   callback=bs.WeakCall(self.onUpdateResponse))
        # lets not run these immediately (since they may be rapid-fire, just bucket them until the next tick)
        # bsInternal._runTransactions()
        
        # the transaction handles the local ticket change, but we apply our local boost vis manually here..
        # (our visualization isnt really wired up to be transaction-based)
        ourDude = self._dudesByID.get(-1)
        if ourDude is not None:
            ourDude.boost(self._boostStrength, self._smoothing)
        
    def update(self):
        if not self._rootWidget.exists():
            return

        # update boost-price
        if self._boostPrice is not None:
            bs.textWidget(edit=self._boostPrice, text=bs.getSpecialChar('ticket')+str(self._boostTickets))

        # update boost button color based on if we have enough moola
        if self._boostButton is not None:
            canBoost = True if (bsInternal._getAccountState() == 'SIGNED_IN'
                                and bsInternal._getAccountTicketCount() >= self._boostTickets) else False
            bs.buttonWidget(edit=self._boostButton, color=(0,1,0) if canBoost else (0.7,0.7,0.7))
        
        # update ticket-count
        if self._ticketsText is not None:
            if self._boostButton is not None:
                if bsInternal._getAccountState() == 'SIGNED_IN':
                    val = bs.getSpecialChar('ticket')+str(bsInternal._getAccountTicketCount())
                else:
                    val = bs.getSpecialChar('ticket')+'???'
                bs.textWidget(edit=self._ticketsText,text=val)
            else:
                bs.textWidget(edit=self._ticketsText,text='')
                
        currentTime = bs.getRealTime()
        if self._lastTransactionTime is None or currentTime - self._lastTransactionTime > bsInternal._getAccountMiscReadVal('pqInt',5000):
            self._lastTransactionTime = currentTime
            bsInternal._addTransaction({'type':'PARTY_QUEUE_QUERY','q':self._queueID},
                                       callback=bs.WeakCall(self.onUpdateResponse))
            bsInternal._runTransactions()

        # step our dudes
        for dude in self._dudes:
            dude.step(self._smoothing)

        
class ResourceTypeInfoWindow(bsUI.PopupWindow):

    def __init__(self, originWidget):

        scale = 2.3 if bsUI.gSmallUI else 1.65 if bsUI.gMedUI else 1.23
        self._transitioningOut = False
        self._width = 570
        self._height = 350
        bgColor = (0.5, 0.4, 0.6)
        bsUI.PopupWindow.__init__(self, size=(self._width, self._height),
                                  toolbarVisibility='INHERIT',
                                  scale=scale, bgColor=bgColor,
                                  position=originWidget.getScreenSpaceCenter())
        self._cancelButton = bs.buttonWidget(parent=self._rootWidget,position=(50,self._height-30),size=(50,50),scale=0.5,
                                             label='',color=bgColor,
                                             onActivateCall=self._onCancelPress,autoSelect=True,
                                             icon=bs.getTexture('crossOut'),iconScale=1.2)
        
    def _onCancelPress(self):
        self._transitionOut()
        
    def _transitionOut(self):
        if not self._transitioningOut:
            self._transitioningOut = True
            bs.containerWidget(edit=self._rootWidget,transition='outScale')

    def onPopupCancel(self):
        bs.playSound(bs.getSound('swish'))
        self._transitionOut()


class JRMPWindow(bsUI.Window):

    def __init__(self,transition='inRight',originWidget=None):
    
        bsInternal._setAnalyticsScreen('JRMP Settings Window')

        # if they provided an origin-widget, scale up from that
        if originWidget is not None:
            self._transitionOut = 'outScale'
            scaleOrigin = originWidget.getScreenSpaceCenter()
            transition = 'inScale'
        else:
            self._transitionOut = 'outRight'
            scaleOrigin = None

        self._r = 'jrmpSettingsWindow'

        spacing = 50
        width = 690
        height = 600

        baseScale=1.2 if bsUI.gSmallUI else 1.1 if bsUI.gMedUI else 1.0
        popupMenuScale = baseScale*1.2

        self._rootWidget = bs.containerWidget(size=(width,height),transition=transition,scale=baseScale,
                                              scaleOriginStackOffset=scaleOrigin)
        self._backButton = backButton = b = bs.buttonWidget(parent=self._rootWidget,position=(35,height-65),size=(120,60),scale=0.8,textScale=1.2,
                                                            label=bs.Lstr(resource='backText'),buttonType='back',onActivateCall=self._back,autoSelect=False)
        bs.containerWidget(edit=self._rootWidget,cancelButton=b)
        t = bs.textWidget(parent=self._rootWidget,position=(width*0.5,height-32),size=(0,0),
                          # text=R.titleText,
                          text=bs.Lstr(resource=self._r+'.titleText'),
                          color=bsUI.gTitleColor,
                          maxWidth=280,
                          hAlign="center",vAlign="center")

        if bsUI.gDoAndroidNav:
            bs.buttonWidget(edit=self._backButton,buttonType='backSmall',size=(60,60),label=bs.getSpecialChar('back'))
            # bs.textWidget(edit=t,hAlign='left',position=(98,height-32))
            
        v = height - 265
        v -= spacing*2
        #self._unlockablesButton = bs.buttonWidget(parent=self._rootWidget,
        #                                        position=(80,v),
        #                                        size=(width*0.4,width*0.3),
        #                                        autoSelect=True,
        #                                        color=bsUI.gJRMPColor,
        #                                        label='',
        #                                        buttonType='square',
        #                                        textScale=1.0,
        #                                        onActivateCall=self._unlockablesPress)
        #bs.imageWidget(parent=self._rootWidget,
        #                position=(140,v+50),
        #                size=(150,150),
        #                drawController=self._unlockablesButton,
        #                texture=bs.getTexture("inventoryIcon"))
        #                
        #bs.textWidget(parent=self._rootWidget,
        #                position=(130,v+70),
        #                size=(0,0),
        #                scale=1.35,
        #                drawController=self._unlockablesButton,
        #                color=bsUI.gJRMPTextColor,
        #                maxWidth=width*0.66,
        #                text=bs.Lstr(resource=self._r+'.unlockablesWindow.titleText'))
        
        # Modpack Website Button
        self._modpackWebsiteButton = bs.buttonWidget(parent=self._rootWidget,
                                                position=(50,v+40),
                                                size=(280,260),
                                                autoSelect=True,
                                                color=bsUI.gJRMPColor,
                                                buttonType='square',
                                                label='',
                                                textScale=1.0,
                                                onActivateCall=bs.Call(bs.openURL,'https://bombsquadjoyride.blogspot.com/'))
        bs.imageWidget(parent=self._rootWidget,
                        position=(105,v+115),
                        size=(170,170),
                        drawController=self._modpackWebsiteButton,
                        texture=bs.getTexture("websiteIcon"))
        bs.textWidget(parent=self._rootWidget,
                        position=(190,v+110),
                        size=(0,0),
                        scale=1.2,
                        drawController=self._modpackWebsiteButton,
                        color=bsUI.gJRMPTextColor,
                        maxWidth=270,
                        maxHeight=80,
                        text=bs.Lstr(resource=self._r+'.modpackWebpageText'),
                        hAlign='center',vAlign='center')
        
        # Statistics Button
        self._statsButton = bs.buttonWidget(parent=self._rootWidget,
                                                position=(350,v+40),
                                                size=(280,260),
                                                autoSelect=True,
                                                color=bsUI.gJRMPColor,
                                                buttonType='square',
                                                label='',
                                                textScale=1.0,
                                                onActivateCall=self._statsPress)
        bs.imageWidget(parent=self._rootWidget,
                        position=(405,v+115),
                        size=(170,170),
                        drawController=self._statsButton,
                        texture=bs.getTexture("inventoryIcon"))
        bs.textWidget(parent=self._rootWidget,
                        position=(490,v+110),
                        size=(0,0),
                        scale=1.8,
                        drawController=self._statsButton,
                        color=bsUI.gJRMPTextColor,
                        maxWidth=width*0.66,
                        text=bs.Lstr(resource=self._r+'.statsWindow.titleText'),
                        hAlign='center',vAlign='center')
                        
        #v = height - (265+100)
        #self._hp = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(65,v),
        #                      size=(width,30),scale=1.0,name="Enable Hard Powerups",defaultValue=False,
        #                      displayName=bs.Lstr(resource=self._r+'.hardPowerupsText'),
        #                      valueChangeCall=self._hardPowerupsCall,
        #                      maxWidth=width)
                
        v = height - (265+115)
        self._pppu = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(65,v),
                              size=(width,30),scale=1.0,name="Powerup Popups",defaultValue=True,
                              displayName=bs.Lstr(resource=self._r+'.powerupPopupsText'),
                              maxWidth=width)
        v = height - (300+115)
        self._ocs = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(65,v),
                              size=(width,30),scale=1.0,name="Offensive Curse Sound",defaultValue=False,
                              displayName=bs.Lstr(resource=self._r+'.offensiveCurseSoundText'),
                              valueChangeCall=self._offensiveCurseSoundCall,
                              maxWidth=430)
                              
        
        v = height - (335+115)
        self._cs = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(65,v),
                              size=(width,30),scale=1.0,name="Camera Shake",defaultValue=True,
                              displayName=bs.Lstr(resource=self._r+'.cameraShakeText'),
                              maxWidth=430)
                              
        v = height - (370+115)
        self._pm = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(65,v),
                              size=(width,30),scale=1.0,name="Party Mode",defaultValue=False,
                              displayName=bs.Lstr(resource=self._r+'.partyModeText'),
                              maxWidth=430)
                              
        v = height - (435+135)
                              
        self._powerupDistributionPopup = bsUI.PopupMenu(parent=self._rootWidget,position=(75,v),width=150,scale=1.5,
                                 choices=['JRMP','Classic','Competetive','No Powerups'],
                                 choicesDisabled=[],
                                 choicesDisplay=[bs.Lstr(resource=self._r+'.jrmpText'),
                                                 bs.Lstr(resource=self._r+'.classicText'),
                                                 bs.Lstr(resource=self._r+'.competetiveText'),
                                                 bs.Lstr(resource=self._r+'.noPowerupsText')],
                                 currentChoice=bs.getConfig().get('Powerup Distribution', 'JRMP'),onValueChangeCall=self._setPowerupDistribution,
                                 jrmp=True)
                                 
        t = bs.textWidget(parent=self._rootWidget,position=(width*0.65+15,v+40),size=(0,0),
                              text=bs.Lstr(resource=self._r+'.powerupDistributionText'),
                              scale=1,
                              color=bsUI.gJRMPTextColor,maxWidth=400,flatness=1.0,
                              hAlign="center",vAlign="center")
        d = bs.textWidget(parent=self._rootWidget,position=(width*0.65+15,v+12),size=(0,0),
                              text=bs.Lstr(resource=self._r+'.powerupDistributionDesc'),
                              scale=0.45,
                              color=bsUI.gJRMPTextColor,maxWidth=400,flatness=1.0,
                              hAlign="center",vAlign="center")    
        self._restoreState()
        
    def _setPowerupDistribution(self,powerup):
        bs.getConfig()['Powerup Distribution'] = powerup
        bs.applySettings()
        bs.writeConfig()
        
    def _hardPowerupsCall(self,val):
        if val:
            txt = bs.Lstr(resource=self._r+'.hardPowerupsInfoText')
            bsUI.ConfirmWindow(txt, cancelButton=False, width=650, height=330, textScale=2.0, originWidget=self._hp)
            
    def _offensiveCurseSoundCall(self,val):
        if val:
            txt = bs.Lstr(resource=self._r+'.offensiveCurseSoundInfoText')
            bsUI.ConfirmWindow(txt, cancelButton=False, width=650, height=330, textScale=2.0, originWidget=self._ocs)
        
    def _unlockablesPress(self):
        self._saveState()
        bs.containerWidget(edit=self._rootWidget,transition='outLeft')
        bsUI.uiGlobals['mainMenuWindow'] = UnlockablesWindow(originWidget=self._statsButton).getRootWidget()
        
    def _statsPress(self):
        self._saveState()
        bs.containerWidget(edit=self._rootWidget,transition='outLeft')
        bsUI.uiGlobals['mainMenuWindow'] = StatsWindow(originWidget=self._statsButton).getRootWidget()
        
    def _back(self):
        self._saveState()
        bs.containerWidget(edit=self._rootWidget,transition=self._transitionOut)
        bsUI.uiGlobals['mainMenuWindow'] = bsUI.MainMenuWindow(transition='inLeft').getRootWidget()

    def _saveState(self):
        try:
            sel = self._rootWidget.getSelectedChild()
            if sel == self._modpackWebsiteButton: selName = 'ModpackWebsite'
            elif sel == self._statsButton: selName = 'Stats'
            #elif sel == self._hp: selName = 'HardPowerups'
            elif sel == self._pppu: selName = 'PowerupPopup'
            elif sel == self._ocs: selName = 'CurseSound'
            elif sel == self._cs: selName = 'CameraShake'
            elif sel == self._powerupDistributionPopup.getButtonWidget(): selName = 'PowerupDistribution'
            elif sel == self._pm: selName = 'PartyMode'
            elif sel == self._backButton: selName = 'Back'
            else: raise Exception("unrecognized selection")
            bsUI.gWindowStates[self.__class__.__name__] = {'selName':selName}
        except Exception:
            bs.printException('error saving state for',self.__class__)

    def _restoreState(self):
        try:
            try: selName = bsUI.gWindowStates[self.__class__.__name__]['selName']
            except Exception: selName = None
            if selName == 'Back':
                sel = self._backButton
                subSel = None
            else:
                if selName == 'ModpackWebsite': sel = self._modpackWebsiteButton
                elif selName == 'Stats': sel = self._statsButton
                #elif selName == 'HardPowerups': sel = self._hp
                elif selName == 'PowerupPopup': sel = self._pppu
                elif selName == 'CurseSound': sel = self._ocs
                elif selName == 'CameraShake': sel = self._cs
                elif selName == 'PowerupDistribution': sel = self._powerupDistributionPopup.getButtonWidget()
                elif selName == 'PartyMode': sel = self._pm
                else: sel = None
                bs.containerWidget(edit=self._rootWidget,selectedChild=sel)
        except Exception:
            bs.printException('error restoring state for',self.__class__)
            
class GameSettingsWindow(bsUI.Window):

    def __init__(self,transition='inRight',originWidget=None):
    
        bsInternal._setAnalyticsScreen('Game Settings Window')

        # if they provided an origin-widget, scale up from that
        if originWidget is not None:
            self._transitionOut = 'outScale'
            scaleOrigin = originWidget.getScreenSpaceCenter()
            transition = 'inScale'
        else:
            self._transitionOut = 'outRight'
            scaleOrigin = None

        self._r = 'Game Settings'

        spacing = 50
        width = 700
        height = 600

        baseScale=1.2 if bsUI.gSmallUI else 1.1 if bsUI.gMedUI else 1.0
        popupMenuScale = baseScale*1.2

        self._rootWidget = bs.containerWidget(size=(width,height),transition=transition,scale=baseScale,
                                              scaleOriginStackOffset=scaleOrigin)
        self._backButton = backButton = b = bs.buttonWidget(parent=self._rootWidget,position=(20,530),size=(120,60),scale=0.9,textScale=1.2,
                                                            label=bs.Lstr(resource='backText'),buttonType='square',onActivateCall=self._back,autoSelect=False)
        bs.containerWidget(edit=self._rootWidget,cancelButton=b)
        t = bs.textWidget(parent=self._rootWidget,position=(width*0.5,height-32),size=(0,0),
                          # text=R.titleText,
                          text='Game Settings',
                          color=bsUI.gTitleColor,
                          maxWidth=280,
                          hAlign="center",vAlign="center")

        if bsUI.gDoAndroidNav:
            bs.buttonWidget(edit=self._backButton,buttonType='backSmall',size=(60,60),label=bs.getSpecialChar('back'))
            # bs.textWidget(edit=t,hAlign='left',position=(98,height-32))
            
        bva = 125
        v = height - (9+bva)
        self._gs1 = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(25,v),
                              size=(width,30),scale=1.0,name="Show Max HP In HP Bar",defaultValue=False,
                              displayName="Show Max HP In HP Bar",
                              maxWidth=430)
        v = height - (45+bva)
        self._gs2 = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(25,v),
                              size=(width,30),scale=1.0,name="Enable Backflips",defaultValue=False,
                              displayName="Enable Backflips",
                              maxWidth=430)
        v = height - (80+bva)
        self._gs3 = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(25,v),
                              size=(width,30),scale=1.0,name="Enable New Powerups",defaultValue=True,
                              displayName="Enable New Powerups",
                              maxWidth=430)
        v = height - (115+bva)
        self._gs4 = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(25,v),
                              size=(width,30),scale=1.0,name="Fancy Powerups",defaultValue=False,
                              displayName="Fancy Powerups",
                              maxWidth=430)
        v = height - (150+bva)
        self._gs5 = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(25,v),
                              size=(width,30),scale=1.0,name="Rainbow Skin",defaultValue=False,
                              displayName="Rainbow Skin",
                              maxWidth=430)
        v = height - (190+bva)
        self._gs6 = bsUI.PopupMenu(parent=self._rootWidget,position=(25,v),width=150,scale=1.48,buttonSize=(186,35),textScale=0.65,
                                 choices=['HP Bar Off','Show HP Bar','Show HP Bar (Percent)'],
                                 choicesDisabled=[],
                                 choicesDisplay=['HP Bar Off','Show HP Bar','Show HP Bar (Percent)'],
                                 currentChoice=bs.getConfig().get('HP Bar', 'HP Bar Off'),onValueChangeCall=self._setHPBsettings,
                                 jrmp=True)
                              
                              
        bva2 = 285
        v = height - (115+bva2)
        self._cht1 = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(25,v),
                              size=(width,30),scale=1.0,name="Unlimited Bombs",defaultValue=False,
                              displayName="Unlimited Bombs",
                              valueChangeCall=self._proOnlyOption,
                              maxWidth=430)
        v = height - (150+bva2)
        self._cht2 = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(25,v),
                              size=(width,30),scale=1.0,name="Invulnerable Mode",defaultValue=False,
                              displayName="Invulnerable Mode",
                              valueChangeCall=self._proOnlyOption,
                              maxWidth=430)
        v = height - (185+bva2)
        self._cht3 = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(25,v),
                              size=(width,30),scale=1.0,name="Permanent Boxing Gloves",defaultValue=False,
                              displayName="Permanent Boxing Gloves",
                              valueChangeCall=self._proOnlyOption,
                              maxWidth=430)
        v = height - (220+bva2)
        self._cht4 = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(25,v),
                              size=(width,30),scale=1.0,name="Gain Shield",defaultValue=False,
                              displayName="Gain Shield",
                              valueChangeCall=self._proOnlyOption,
                              maxWidth=430)
        v = height - (255+bva2)
        self._cht5 = bsUI.configCheckBoxMikirog(parent=self._rootWidget,position=(25,v),
                              size=(width,30),scale=1.0,name="No Time Limit Powerups",defaultValue=False,
                              displayName="No Time Limit Powerups",
                              valueChangeCall=self._proOnlyOption,
                              maxWidth=430)
        v = height - (9+bva)
        self._p1 = bsUI.PopupMenu(parent=self._rootWidget,position=(350,v),width=150,scale=1.48,buttonSize=(320,55),textScale=0.7,
                                 choices=['Powerup Text Color: Self','Powerup Text Color: Tier Based','Powerup Text Color: Rainbow'],
                                 choicesDisabled=[],
                                 choicesDisplay=['Powerup Text Color: Self','Powerup Text Color: Tier Based','Powerup Text Color: Rainbow'],
                                 currentChoice=bs.getConfig().get('Powerup Text Color', 'Powerup Text Color: Tier Based'),onValueChangeCall=self._setp1,
                                 jrmp=False)
        v = height - (75+bva)
        self._p2 = bsUI.PopupMenu(parent=self._rootWidget,position=(350,v),width=150,scale=1.48,buttonSize=(320,55),textScale=0.7,
                                 choices=['Powerup Shape: Default','Powerup Shape: Smoothed Square'],
                                 choicesDisabled=[],
                                 choicesDisplay=['Powerup Shape: Default','Powerup Shape: Smoothed Square'],
                                 currentChoice=bs.getConfig().get('Powerup Shape', 'Powerup Shape: Default'),onValueChangeCall=self._setp2,
                                 jrmp=False)
                              
                              
        txtSets1 = bs.textWidget(parent=self._rootWidget,position=(145,int(height*0.853)),size=(0,0),
                              text='- Mod Settings -',
                              scale=1,
                              color=(0.40,0.80,1.35),maxWidth=400,flatness=1.0,
                              hAlign="center",vAlign="center")    
        txtSets2 = bs.textWidget(parent=self._rootWidget,position=(139,int(height*0.419)),size=(0,0),
                              text='- Cheat Settings -',
                              scale=1,
                              color=(0.40,0.80,1.35),maxWidth=400,flatness=1.0,
                              hAlign="center",vAlign="center")    
        self._restoreState()
        
        
    def _setp1(self,p1):
        bs.getConfig()['Powerup Text Color'] = p1
        bs.applySettings()
        bs.writeConfig()  
    def _setp2(self,p2):
        bs.getConfig()['Powerup Shape'] = p2
        bs.applySettings()
        bs.writeConfig()  
    def _setHPBsettings(self,hp):
        bs.getConfig()['HP Bar'] = hp
        bs.applySettings()
        bs.writeConfig()  
    def _proOnlyOption(self,val):
        if val:
            if not bsUtils._havePro():
            	bsUI.PurchaseWindow(items=['pro'])
            	bs.getConfig()['Unlimited Bombs'] = False
                bs.getConfig()['No Time Limit Powerups'] = False
                bs.getConfig()['Gain Shield'] = False
                bs.getConfig()['Permanent Boxing Gloves'] = False
                bs.getConfig()['Invulnerable Mode'] = False
            	bs.writeConfig()
            else:
            	return
    def _back(self):
        self._saveState()
        bs.containerWidget(edit=self._rootWidget,transition=self._transitionOut)
        bsUI.uiGlobals['mainMenuWindow'] = bsUI.MainMenuWindow(transition='inLeft').getRootWidget()

    def _saveState(self):
        try:
            sel = self._rootWidget.getSelectedChild()
            if sel == self._gs1: selName = 'Show Max HP In HP Bar'
            elif sel == self._gs2: selName = 'Enable Backflips'
            elif sel == self._gs3: selName = 'Enable New Powerups'
            elif sel == self._gs4: selName = 'Fancy Powerups'
            elif sel == self._gs5: selName = 'Rainbow Skin'
            elif sel == self._gs6.getButtonWidget(): selName = 'HP Bar'
            elif sel == self._p1.getButtonWidget(): selName = 'Powerup Text Color'
            elif sel == self._p2.getButtonWidget(): selName = 'Powerup Shape'
            elif sel == self._cht1: selName = 'Unlimited Bombs'
            elif sel == self._cht2: selName = 'Invulnerable Mode'
            elif sel == self._cht3: selName = 'Permanent Boxing Gloves'
            elif sel == self._cht4: selName = 'Gain Shield'
            elif sel == self._cht5: selName = 'No Time Limit Powerups'
            else: raise Exception("unrecognized selection")
            bsUI.gWindowStates[self.__class__.__name__] = {'selName':selName}
        except Exception:
            bs.printException('error saving state for',self.__class__)

    def _restoreState(self):
        try:
            try: selName = bsUI.gWindowStates[self.__class__.__name__]['selName']
            except Exception: selName = None
            if selName == 'Back':
                sel = self._backButton
                subSel = None
            else:
                if selName == 'Show Max HP In HP Bar': sel = self._gs1
                elif selName == 'Enable Backflips': sel = self._gs2
                elif selName == 'Enable New Powerups': sel = self._gs3
                elif selName == 'Fancy Powerups': sel = self._gs4
                elif selName == 'Rainbow Skin': sel = self._gs5
                elif selName == 'HP Bar': sel = self._gs6.getButtonWidget()
                elif selName == 'Powerup Text Color': sel = self._p1.getButtonWidget()
                elif selName == 'Powerup Shape': sel = self._p2.getButtonWidget()
                elif selName == 'Unlimited Bombs': sel = self._cht1
                elif selName == 'Invulnerable Mode': sel = self._cht2
                elif selName == 'Permanent Boxing Gloves': sel = self._cht3
                elif selName == 'Gain Shield': sel = self._cht4
                elif selName == 'No Time Limit Powerups': sel = self._cht5
                else: sel = None
                bs.containerWidget(edit=self._rootWidget,selectedChild=sel)
        except Exception:
            bs.printException('error restoring state for',self.__class__)
       
class UnlockablesWindow(bsUI.Window):
    def __init__(self,originWidget=None):
        
        # if they provided an origin-widget, scale up from that
        if originWidget is not None:
            self._transitionOut = 'outScale'
            scaleOrigin = originWidget.getScreenSpaceCenter()
            transition = 'inScale'
        else:
            self._transitionOut = 'outRight'
            scaleOrigin = None
            transition = 'inRight'
        
        width = 650
        height = 700
        baseScale = 2.0 if bsUI.gSmallUI else 1.3 if bsUI.gMedUI else 1.0
        
        #currency = 50 #bs.getConfig().get('Tokens', 0)
        #bs.getConfig().get('Tokens', 0)
        #bs.writeConfig()

        self._r = 'jrmpSettingsWindow.unlockablesWindow'
        self._d = self._r+'.details'
        self._rootWidget = bs.containerWidget(size=(width,height),transition=transition,
                                              toolbarVisibility='MENU_MINIMAL',
                                              scaleOriginStackOffset=scaleOrigin,
                                              scale=baseScale,
                                              claimsLeftRight=False,claimsTab=False,
                                              stackOffset=(0,-8) if bsUI.gSmallUI else (0,0))

        if bsUI.gToolbars and bsUI.gSmallUI:
            bs.containerWidget(edit=self._rootWidget,onCancelCall=self._back)
        else:
            self._backButton = b = bs.buttonWidget(parent=self._rootWidget,position=(40,height-(68 if gSmallUI else 62)),size=(140,60),scale=0.8,
                                label=bs.Lstr(resource='backText'),buttonType='back', onActivateCall=self._back,autoSelect=True)
            bs.containerWidget(edit=self._rootWidget,cancelButton=b)

            if bsUI.gDoAndroidNav:
                bs.buttonWidget(edit=b,buttonType='backSmall',position=(40,height-(68 if gSmallUI else 62)+5),size=(60,48),label=bs.getSpecialChar('back'))
                # bs.textWidget(edit=t,hAlign='left',position=(110,height-(59 if gSmallUI else 54)))

            
        t = bs.textWidget(parent=self._rootWidget,position=(0,height-(59 if gSmallUI else 54)),size=(width,40),
                          text=bs.Lstr(resource=self._r+'.titleText'),
                          hAlign="center",
                          color=bsUI.gTitleColor,
                          maxWidth=330,vAlign="center")

        
        s = bs.scrollWidget(parent=self._rootWidget,position=(40,180),size=(width-80,height-250),captureArrows=True)
        bs.containerWidget(edit=self._rootWidget,selectedChild=s)
        
        # Locker Token owned in the corner
        self._tokenCountButton = b = bs.buttonWidget(parent=self._rootWidget,position=(width-190,height-60),
                                                     autoSelect=True,scale=0.6,size=(240,100),
                                                     label='',
                                                     color=bsUI.gJRMPColor,
                                                     onActivateCall=self._tokenCountButtonPress)
        self._tokenCountText = bs.textWidget(parent=self._rootWidget,position=(width-100,height-30),size=(0,0),
                                                    text=str(currency),
                                                    hAlign="center",
                                                    scale=1.35,
                                                    color=bsUI.gJRMPTextColor,
                                                    maxWidth=330,vAlign="center")                       
        bs.imageWidget(parent=self._rootWidget,
                       position=(width-170,height-47),
                       size=(35,35),
                       drawController=self._tokenCountButton,
                       texture=bs.getTexture("lockerToken"))
                       
        self._subWidth = width-80
        self._subHeight = height*1.275
        self._textTop = self._subHeight-20
        self._borderDistance = 15
        self._rightBorderDistance = self._borderDistance*2.5
        
        self._subContainer = bs.containerWidget(parent=s,size=(self._subWidth,self._subHeight),
                                                background=False,alwaysHighlight=True,
                                                claimsLeftRight=False,claimsTab=False)

        if bsUI.gToolbars:
            bs.widget(edit=s,rightWidget=bsInternal._getSpecialWidget('partyButton'))
            if gSmallUI:
                bs.widget(edit=s,leftWidget=bsInternal._getSpecialWidget('backButton'))
                
        # Text below the scrolling window
        #bs.imageWidget(parent=self._rootWidget, # Locker Token image
        #               position=(width-600,height-647),
        #               size=(100,100),
        #               texture=bs.getTexture("lockerToken"))
        #bs.textWidget(parent=self._rootWidget,position=(width-490,height-600),size=(0,0), # Price of the unlock
        #              text='12',
        #              hAlign="left",
        #              scale=3,
        #              color=bsUI.gJRMPTextColor,
        #              maxWidth=330,vAlign="center")
        #bs.textWidget(parent=self._rootWidget,position=(width-220,height-555),size=(0,0), # Name of the unlock
        #              text=bs.Lstr(resource=self._d+'.dummyName'),
        #              hAlign="center",
        #              scale=1.5,
        #              color=bsUI.gJRMPDarkColor,
        #              maxWidth=330,vAlign="center")
        #bs.textWidget(parent=self._rootWidget,position=(width-220,height-620),size=(0,0), # Description of the unlock
        #              text=bs.Lstr(resource=self._d+'.dummyDesc'),
        #              hAlign="center",
        #              scale=1,
        #              color=bsUI.gJRMPTextColor,
        #              maxWidth=width*0.5,vAlign="center")
                    
        v = 110 # How much we should go down with each row in our tree
        verticalRow = 0
        self._buttonTop = self._subHeight-v
        
        # Positions conveniently placed inside variables for ease of use
        posCenter = self._subWidth*0.4
        posLeft = posCenter-130
        posRight = posCenter+130
        posLeft1 = posLeft-55
        posLeft2 = posLeft+55
        posRight1 = posRight-55
        posRight2 = posRight+55
        map = False
        iconTint = None
        buttons = {}
        for i in range(4):
        
            # Item Properties (like icons)
            if i == 0: 
                icon = bs.getTexture('powerupGrenade')
                type = 'center'
                part = 0
            elif i == 1:
                icon = bs.getTexture('looieIcon')
                iconTint = (1,0.75,0.5)
                type = 'center'
                part = 0
            elif i == 2:
                icon = bs.getTexture('powerupDynamitePack')
                type = 'duo'
                part = 1
            elif i == 3:
                icon = bs.getTexture('mictlanIcon')
                type = 'duo'
                iconTint = (0.3,1,1)
                part = 0
            elif i == 4:
                icon = bs.getTexture('powerupKnockerBombs')
                type = 'separate'
                part = 3
            elif i == 5:
                icon = bs.getTexture('powerupGlueBombs')
                type = 'separate'
                part = 2
            elif i == 6:
                icon = bs.getTexture('morningUnlockIcon')
                type = 'separate'
                part = 1
            elif i == 7:
                icon = bs.getTexture('klaymanIcon')
                type = 'separate'
                iconTint = (1,0.8,0.3)
                part = 0
            
            if type == 'center': pos = posCenter
            elif type == 'duo': 
                if part == 0: pos = posRight
                else: pos = posLeft
            elif type == 'separate':
                if part == 3: pos = posLeft1
                elif part == 2: pos = posLeft2
                elif part == 1: pos = posRight1
                elif part == 0: pos = posRight2
                
            buttons[str(i)] = bs.buttonWidget(parent=self._subContainer,
                            position=(pos,self._buttonTop-verticalRow),
                            size=(90,90),
                            icon=icon,
                            iconScale=2.1,
                            iconColor=iconTint,
                            autoSelect=True,
                            color=bsUI.gJRMPColor,
                            label='',
                            buttonType='square')
                            
            if type == 'center' or part == 0: verticalRow += v
            iconTint = None
            
        # Needs to be a separate iteration loop to adjust UI controls
        # Makes it easier to move around with a controller
        for x in range(4):
            if x in [0,1]:
                left = self._backButton
                right = self._tokenCountButton
            elif x == 2:
                left = self._backButton
                right = buttons[str(x+1)]
            elif x == 3:
                left = buttons[str(x-1)]
                right = self._tokenCountButton
            else:
                # If can't find the button for whatever reason
                left = None
                right = None
            bs.widget(edit=buttons[str(x)],
                      leftWidget=left,
                      rightWidget=right)
                      
    def _tokenCountButtonPress(self):
        txt = bs.Lstr(resource=self._r+'.tokenInfoText')
        bsUI.ConfirmWindow(txt, cancelButton=False, width=650, height=330, textScale=2.0, originWidget=self._tokenCountButton)
                         
    def _back(self):
        bs.containerWidget(edit=self._rootWidget,transition=self._transitionOut)
        bsUI.uiGlobals['mainMenuWindow'] = JRMPWindow(transition='inLeft').getRootWidget()
       
class StatsWindow(bsUI.Window):
    def __init__(self,originWidget=None):
        
        # if they provided an origin-widget, scale up from that
        if originWidget is not None:
            self._transitionOut = 'outScale'
            scaleOrigin = originWidget.getScreenSpaceCenter()
            transition = 'inScale'
        else:
            self._transitionOut = 'outRight'
            scaleOrigin = None
            transition = 'inRight'
        
        self.width = 450
        height = 380 if bsUI.gSmallUI else 487

        self._r = 'jrmpSettingsWindow.statsWindow'
        self._rootWidget = bs.containerWidget(size=(self.width,height),transition=transition,
                                              toolbarVisibility='MENU_MINIMAL',
                                              scaleOriginStackOffset=scaleOrigin,
                                              scale=1.9 if bsUI.gSmallUI else 1.3 if bsUI.gMedUI else 1.0)

        if bsUI.gToolbars and bsUI.gSmallUI:
            bs.containerWidget(edit=self._rootWidget,onCancelCall=self._back)
        else:
            b = bs.buttonWidget(parent=self._rootWidget,position=(40,height-(68 if bsUI.gSmallUI else 62)),size=(140,60),scale=0.8,
                                label=bs.Lstr(resource='backText'),buttonType='back', onActivateCall=self._back,autoSelect=True)
            bs.containerWidget(edit=self._rootWidget,cancelButton=b)

            if bsUI.gDoAndroidNav:
                bs.buttonWidget(edit=b,buttonType='backSmall',position=(40,height-(68 if bsUI.gSmallUI else 62)+5),size=(60,48),label=bs.getSpecialChar('back'))
                # bs.textWidget(edit=t,hAlign='left',position=(110,height-(59 if gSmallUI else 54)))

            
        t = bs.textWidget(parent=self._rootWidget,position=(0,height-(59 if bsUI.gSmallUI else 54)),size=(self.width,30),
                          text=bs.Lstr(resource=self._r+'.titleText'),
                          hAlign="center",
                          color=bsUI.gTitleColor,
                          maxWidth=330,vAlign="center")

        
        s = bs.scrollWidget(parent=self._rootWidget,position=(40,90),size=(self.width-80,height-160),captureArrows=True)
        bs.containerWidget(edit=self._rootWidget,selectedChild=s)
        self._subWidth = self.width-80
        self._subHeight = height*1.625+28 if bsUI.gSmallUI else height*1.2750+30
        self._textTop = self._subHeight-20
        self._borderDistance = 15
        self._rightBorderDistance = self._borderDistance*2.5
        self._subContainer = bs.containerWidget(parent=s,size=(self._subWidth,self._subHeight),background=False,claimsLeftRight=False,claimsTab=False)

        if bsUI.gToolbars:
            bs.widget(edit=s,rightWidget=bsInternal._getSpecialWidget('partyButton'))
            if bsUI.gSmallUI:
                bs.widget(edit=s,leftWidget=bsInternal._getSpecialWidget('backButton'))
                
        '''
        Check the statAdd function in bsUtils in order to see what stats you can add to the table
        '''
        v = 28
        scale = 0.55
        i = 0 # Used for stat translations
        iVerticalPosition = i # Used for text position
        self.statTypes = ['Bomb Explosions', # Used to gather info from the config
                    'Powerup Total',
                    'Punches Hit',
                    'Pickups Countered',
                    'Close-Call Dodges',
                    'Dice Effects Initiated',
                    'Player Kills',
                    'Player Deaths',
                    'Bot Kills',
                    'Shiny Bots Seen',
                    'Ice Thawed',
                    'Spazes Lit on Fire',
                    'Fire Extinguishes',
                    'Dizzy Characters',
                    'Curse Cures',
                    'Shield Repairs',
                    'CRIT Count',
                    'GIBBED Count',
                    'MINEXECUTION Count',
                    'HI-JUMPED Count',
                    ' ']
        statTypesTranslation = ['bombExplosions', # Used to gather translations that describe stats from the config
                                'powerupTotal',
                                'punchesHit',
                                'pickupCounters',
                                'dodges',
                                'diceEffect',
                                'playerKills',
                                'playerDeaths',
                                'botKills',
                                'shinyBot',
                                'iceThawed',
                                'spazFire',
                                'fireExtinguishes',
                                'spazDizzy',
                                'curseCures',
                                'shieldRepairs',
                                'crit',
                                'gibKills',
                                'mineKills',
                                'hijumpKills',
                                'levelProgress']
        for s in self.statTypes:
            if i in [6,8,14]: iVerticalPosition += 1 # Which lines should have gaps?
            bs.textWidget(parent=self._subContainer,position=(self._borderDistance,self._textTop-v*iVerticalPosition),size=(0,0),
                            text=bs.Lstr(resource=self._r+'.'+statTypesTranslation[i]),
                            scale=0.75,
                            color=bsUI.gJRMPTextColor,maxWidth=400,flatness=1.0,
                            hAlign="left",vAlign="center")
            bs.textWidget(parent=self._subContainer,position=(self._subWidth-self._rightBorderDistance,self._textTop-v*iVerticalPosition),size=(0,0),
                                                 text=str(bs.getConfig().get('Stats: ' + str(s), 0)),
                                                 scale=0.75,
                                                 color=bsUI.gJRMPDarkColor,maxWidth=400,flatness=1.0,
                                                 hAlign="right",vAlign="center")
            i += 1
            iVerticalPosition += 1
            
        
            
        self._resetStats = bs.buttonWidget(parent=self._rootWidget,
                                                position=(40,20),
                                                size=(self._subWidth,60),
                                                autoSelect=True,
                                                color=bsUI.gJRMPColor,
                                                label='',
                                                textScale=1.0,
                                                onActivateCall=bs.Call(self._resetStatsPress))
        bs.textWidget(parent=self._rootWidget,
                        position=(self._subWidth*0.6,50),
                        size=(0,0),
                        scale=1.0,
                        drawController=self._resetStats,
                        color=bsUI.gJRMPTextColor,
                        maxWidth=self.width*0.66,
                        text=bs.Lstr(resource=self._r+'.resetProgressText'),
                        hAlign='center',vAlign='center')
                         
    def _resetStatsPress(self):
        def _resetStats():
            bs.playSound(bs.getSound('shieldDown'))
            for s in self.statTypes:
                stat = 0
                bs.getConfig()['Stats: ' + str(s)] = stat
                bs.writeConfig()
            bs.containerWidget(edit=self._rootWidget,transition=self._transitionOut)
            bsUI.uiGlobals['mainMenuWindow'] = JRMPWindow(transition='inLeft').getRootWidget()
            
        bsUI.ConfirmWindow(bs.Lstr(resource=self._r+'.resetProgressAskText'),
                      bs.Call(_resetStats),450,150)
                         
    def _back(self):
        bs.containerWidget(edit=self._rootWidget,transition=self._transitionOut)
        bsUI.uiGlobals['mainMenuWindow'] = JRMPWindow(transition='inLeft').getRootWidget()
