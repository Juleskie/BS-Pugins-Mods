# coding=utf-8
from bsSpaz import *
import bs,random,bsUtils,bsMap, bsGame,bsBomb,bsSpaz, bsVector,weakref
from bsUtils import Background,animate
#created by aaalligator

def _haveNewProOptions():
    return True
bsUtils._haveProOptions = _haveNewProOptions

#This is important don't delete
def _haveNewPro():
    return True
bsUtils._havePro = _haveNewPro