# Released under the MIT License. See LICENSE for details.
# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations
from typing import TYPE_CHECKING
from bastd.actor.playerspaz import PlayerSpaz
import _ba, ba, json

path = _ba.env()['python_directory_user']+'/baSuperEffectzSettings.json'
with open(path, 'r') as f:
    v = json.loads(f.read())

if TYPE_CHECKING:
    pass

#####################################################
# For v1.6.4+ only
# by sam"e"_thing 
# Discord: Spritey_loved#8484

PlayerSpaz.init = PlayerSpaz.__init__
def NewSpazForPlayer(self,
                 player: ba.Player,
                 color: Sequence[float] = (1.0, 1.0, 1.0),
                 highlight: Sequence[float] = (0.5, 0.5, 0.5),
                 character: str = 'Spaz',
                 powerups_expire: bool = True) -> None:
   self.init(player,color,highlight, character, powerups_expire)
   if not v[0]['PARTICLE INTERVAL'] == "0":
      self.effect_timer = ba.Timer(v[0]['PARTICLE INTERVAL'],ba.Call(self.effectz), timeformat=ba.TimeFormat.MILLISECONDS,repeat=True)
   else:
      self.effect_timer = None
   self.angle_inc = 0
   self.angle_inc2 = 0


# import base64
# exec(base64.b64decode("").decode('UTF-8'))

radiusv,scalev,spreadv,emit,chunk,countv,tendril,pattern,height = (
v[0]["PATTERN RADIUS"],
v[0]["PARTICLE SIZE"],
v[0]["PARTICLE SPREAD"],
v[0]["EMIT TYPE"],
v[0]["CHUNK TYPE"],
v[0]["PARTICLE AMOUNT"],
v[0]["TENDRIL TYPE"],
v[0]["PATTERN TYPE"],
v[0]["PARTICLE HEIGHT"]
)

def emitfxcd(self):
     if emit == "None" and not chunk and tendril == "None":
        ba.emitfx(position=self.pos,count=int(countv),scale=scalev, spread=spreadv,
        chunk_type = chunk,
        tendril_type = tendril)
     elif emit and tendril == "None" and not chunk == "None":
        ba.emitfx(position=self.pos,count=int(countv),scale=scalev, spread=spreadv,
        chunk_type = chunk)
     elif not emit == "None" and chunk and tendril == "None":
        ba.emitfx(position=self.pos,count=int(countv),scale=scalev, spread=spreadv,
        emit_type = emit)
     elif not emit and tendril and chunk == "None":
        ba.emitfx(position=self.pos,count=int(countv),scale=scalev, spread=spreadv,
        emit_type = emit,
        tendril_type = tendril,
        chunk_type = chunk)
     elif tendril == "None" and not chunk and emit == "None":
        ba.emitfx(position=self.pos,count=int(countv),scale=scalev, spread=spreadv,
        emit_type = emit,
        chunk_type = chunk)
     elif not tendril == "None" and chunk and emit == "None":
        ba.emitfx(position=self.pos,count=int(countv),scale=scalev, spread=spreadv,
        tendril_type = emit,)

def effectz(self):
   import math
   import random
   if self.node.dead or not self.node.exists():
      self.effect_timer = None
   p = self.node.position
   if pattern == "None":
       self.pos = (p[0],p[1]+height,p[2])
       self.emitfxcd()
   elif pattern == "STAR":
      angle1 = 0
      angle2 = 240
      angle3 = 330
      angle4 = 300
      angle5 = 90
      for rad in range(1,30):
        self.rad_inc += 0.01*rad
        x1 = self.rad_inc*math.cos(angle1)
        x2 = self.rad_inc*math.cos(angle2)
        x3 = self.rad_inc*math.cos(angle3)
        x4 = self.rad_inc*math.cos(angle4)
        x5 = self.rad_inc*math.cos(angle5)
        z1 = self.rad_inc*math.sin(angle1)
        z2 = self.rad_inc*math.sin(angle2)
        z3 = self.rad_inc*math.sin(angle3)
        z4 = self.rad_inc*math.sin(angle4)
        z5 = self.rad_inc*math.sin(angle5)
        self.pos = (p[0]+x1,p[1]+height,p[2]+z1)
        self.emitfxcd()
        self.pos = (p[0]+x2,p[1]+height,p[2]+z2)
        self.emitfxcd()
        self.pos = (p[0]+x3,p[1]+height,p[2]+z3)
        self.emitfxcd()
        self.pos = (p[0]+x4,p[1]+height,p[2]+z4)
        self.emitfxcd()
        self.pos = (p[0]+x5,p[1]+height,p[2]+z5)
        self.emitfxcd()
   elif pattern == "RAIN":
      rad = ((radiusv * 0.001) * 0.25) + random.uniform(0.05,1.23)
      angle = random.randrange(0,360)
      x = rad*math.cos(angle)
      z = rad*math.sin(angle)
      self.pos = (p[0]+x,p[1]+height,p[2]+z)
      self.emitfxcd()
   elif pattern == "SINGLE TWIST CIRCLE":
      self.angle_inc += 1
      if radiusv == "RANDOM":
          radius = min(80,random.uniform(0,800))*0.0020
      else:
          radius = radiusv*0.001
      angle = 0.1*self.angle_inc
      x = radius*math.cos(angle)
      z = radius*math.sin(angle)
      self.pos = (p[0]+x,p[1]+height,p[2]+z)
      self.emitfxcd()
   elif pattern == "DOUBLE TWIST CIRCLE":
      self.angle_inc += 1
      self.angle_inc2 +=(self.angle_inc + 180)%360
      if radiusv == "RANDOM":
          radius = min(80,random.uniform(0,800))*0.0020
      else:
          radius = radiusv*0.0020
      angle = 0.1*self.angle_inc
      angle2 = 0.1*self.angle_inc2
      x = radius*math.cos(angle)
      z = radius*math.sin(angle)
      x2 = radius*math.cos(angle2)
      z2 = radius*math.sin(angle2)
      self.pos = (p[0]+x,p[1]+height,p[2]+z)
      self.emitfxcd()
      self.pos = (p[0]+x2,p[1]+height,p[2]+z2)
      self.emitfxcd()
   elif pattern == "CIRCLE":
       if radiusv == "RANDOM":
           radius = min(80,random.uniform(0,800))*0.0020
       else:
           radius = radiusv*0.0020
       for x in range(1,360):
         angle = 1*x
         x = radius*math.cos(angle)
         z = radius*math.sin(angle)
         self.pos = (p[0]+x,p[1]+height,p[2]+z)
         self.emitfxcd()

PlayerSpaz.__init__ = NewSpazForPlayer



# ba_meta export plugin
class Super_EffectzPlugin(ba.Plugin):
    def __init__(self) -> None:
      self.ReplaceSpaz()
    def ReplaceSpaz(self) -> None:
      PlayerSpaz.__init__ = NewSpazForPlayer
      PlayerSpaz.effectz = effectz
      PlayerSpaz.emitfxcd = emitfxcd
      PlayerSpaz.pos = (0,0,0)
      PlayerSpaz.angle_inc,PlayerSpaz.angle_inc2,PlayerSpaz.rad_inc, PlayerSpaz.x_r, PlayerSpaz.z_r = 0, 0, 0, 0, 0