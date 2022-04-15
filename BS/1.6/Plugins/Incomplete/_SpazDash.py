# Released under the MIT License. See LICENSE for details.
# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations
from typing import TYPE_CHECKING
import ba
from bastd.actor.spazfactory import SpazFactory
from bastd.actor.spaz import Spaz
from bastd.gameutils import SharedObjects
import bastd.gameutils
if TYPE_CHECKING:
    pass

# Credits: TheMikirog (Some Codes by him)
#
# You can change the variables below
########################################
#
# Available filters for chunk type:
# spark, sweat, ice, slime, splinter, metal, rock
#
#########################################
#
# Available filters for emit type:
# stickers, tendrils, distortion
#
#########################################
#
# Available filters for tendril type:
# smoke, ice, thin_smoke
#
##########################################
#
# If you want a Chunk/Emit/Tendril, leave it to None like the code below this comment
# DASH_EFFECT_CHUNK_TYPE = None

# If you want a Chunk/Emit/Tendril, type it like this:
# DASH_EFFECT_CHUNK_TYPE = 'name'
DASH_ENABLE_EFFECT = True
DASH_EFFECT_CHUNK_TYPE = 'spark'
DASH_EFFECT_EMIT_TYPE = None
DASH_EFFECT_TENDRIL_TYPE = None
DASH_EFFECT_AMOUNT = int(20)
DASH_EFFECT_SCALE = 1.0
DASH_EFFECT_SPREAD_FACTOR = 0.6

DASH_EFFECT_ENABLE_EXPLOSION_LIGHT = False
DASH_EFFECT_EXPLOSION_LIGHT_COLOR = (0.8,0.6,0.4) #'MATCH_SPAZ_COLOR' #'MATCH_SPAZ_HIGHLIGHT'
DASH_EFFECT_EXPLOSION_LIGHT_RADIUS = 0.2

DASH_EFFECT_ENABLE_LIGHT = False
DASH_EFFECT_LIGHT_COLOR = (0.2,0.5,0.2) #'MATCH_SPAZ_COLOR' #'MATCH_SPAZ_HIGHLIGHT'
DASH_EFFECT_LIGHT_RADIUS = 0.4


DASH_TEXT_SHOW_COOLDOWN_TEXT = True
DASH_TEXT_SIZE = 1.3
DASH_TEXT_READY = "Dash Ready"
DASH_TEXT_COLOR = 'MATCH_SPAZ_COLOR'
# type MATCH_SPAZ_COLOR if you want to match color by your spaz's own color or highlight
# Example: DASH_TEXT_COLOR = 'MATCH_SPAZ_COLOR'
# Example: DASH_TEXT_COLOR = 'MATCH_SPAZ_HIGHLIGHT'


DASH_DODGE_DAMAGE_REDUCTION = 0.55
DASH_SHORT_SLOWMO_ON_DODGE = True
DASH_UPWARD_FORCE_SCALE = 0.5
DASH_COOLDOWN = 400.0
DASH_SPEED = 500

###################################



# Dash System Below
# Dont touch anything below this Line
# 


# ba_meta export plugin
class Juleskie(ba.Plugin):
    
    
    #=============================================#
    # Set up early variables if we don't have them.
    Spaz.old_on_jump_press = Spaz.on_jump_press
    Spaz.old_on_punch_press = Spaz.on_punch_press
    
    Spaz.ef_1 = DASH_EFFECT_CHUNK_TYPE
    Spaz.ef_2 = DASH_EFFECT_AMOUNT
    Spaz.ef_3 = DASH_EFFECT_SCALE
    Spaz.ef_4 = DASH_EFFECT_SPREAD_FACTOR
    Spaz.ef_5 = DASH_EFFECT_TENDRIL_TYPE
    Spaz.ef_6 = DASH_EFFECT_EMIT_TYPE
    Spaz.ef_8 = DASH_EFFECT_LIGHT_COLOR
    Spaz.ef_9 = DASH_EFFECT_LIGHT_RADIUS
    Spaz.ef_10 = DASH_EFFECT_EXPLOSION_LIGHT_COLOR
    Spaz.ef_11 = DASH_EFFECT_EXPLOSION_LIGHT_RADIUS
    Spaz.dash_ready = True
    Spaz.dodging = False
    Spaz.dash_timer = None
    Spaz.dodging_timer = None
    Spaz.pressed_1 = False
    Spaz.pressed_2 = False
    #=============================================#
    def jump_press(self) -> None:
      if not self.node: return
      
      self.pressed_1 = True
      def remove1(): self.pressed_1 = False
      ba.timer(0.08,remove1)
      self.node.jump_pressed = True
      self._turbo_filter_add_press('jump')


    def punch_press(self) -> None:
        if not self.node or self.frozen or self.node.knockout > 0.0:
            return

        t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
        assert isinstance(t_ms, int)
        if t_ms - self.last_punch_time_ms >= self._punch_cooldown:
            if self.punch_callback is not None:
                self.punch_callback(self)
            self._punched_nodes = set()  # Reset this.
            self.last_punch_time_ms = t_ms
            self.node.punch_pressed = True
            if not self.node.hold_node:
                ba.timer(
                    0.1,
                    ba.WeakCall(self._safe_play_sound,
                                SpazFactory.get().swish_sound, 0.8))
        self._turbo_filter_add_press('punch')
    
    
        pos = self.node.position
        self.pressed_2 = True
        def remove2(): self.pressed_2 = False
        ba.timer(0.08,remove2)
        if self.dash_ready and self.pressed_1 and self.pressed_2 and not self.node.hold_node:
          def start(): ba.getactivity().globalsnode.slow_motion = True
          def end(): ba.getactivity().globalsnode.slow_motion = False
          if not ba.getactivity().globalsnode.slow_motion and DASH_SHORT_SLOWMO_ON_DODGE == True:
             ba.timer(0.05, start)
             ba.timer(0.08, end)
          def undodge():
            self.impact_scale = 1.0
            self.dodging = False
          def dash_ready():
            if self.node.exists():
               from bastd.actor.popuptext import PopupText 
               self.dash_ready = True
               if DASH_TEXT_SHOW_COOLDOWN_TEXT == True:
                  if DASH_TEXT_COLOR == 'MATCH_SPAZ_COLOR':
                     SUPPORT_WHO_KNOWS = self.node.color
                  elif DASH_TEXT_COLOR == 'MATCH_SPAZ_HIGHLIGHT':
                     SUPPORT_WHO_KNOWS = self.node.highlight
                  else:
                     SUPPORT_WHO_KNOWS = (DASH_TEXT_COLOR[0],DASH_TEXT_COLOR[1],DASH_TEXT_COLOR[2])
                  p = PopupText(text=DASH_TEXT_READY, scale=DASH_TEXT_SIZE, position=(self.node.position[0],self.node.position[1]-1.15,self.node.position[2]), color=SUPPORT_WHO_KNOWS).autoretain()
                  
          if DASH_EFFECT_ENABLE_LIGHT == True:
             if self.ef_8 == 'MATCH_SPAZ_HIGHLIGHT':
                color_light = self.node.highlight
             elif self.ef_8 == 'MATCH_SPAZ_COLOR':
                color_light = self.node.color
             else: color_light = self.ef_8
             self.light = ba.newnode('light',
                        attrs={'position':self.node.position,
                                'color': color_light,
                                'radius': self.ef_9,
                                'volume_intensity_scale': 1.0}) 
             ba.animate(self.light,'intensity',{0:0.5,100:0.2,150:0},loop=False)
             ba.timer(0.5,self.light.delete)
          if DASH_EFFECT_ENABLE_EXPLOSION_LIGHT == True:
             if self.ef_10 == 'MATCH_SPAZ_HIGHLIGHT':
                exp_light = self.node.highlight
             elif self.ef_10 == 'MATCH_SPAZ_COLOR':
                exp_light = self.node.color
             else: exp_light = self.ef_10
             self.radius_light = ba.newnode("explosion", attrs={
                'position':self.node.position,
                'velocity':(0,0,0),
                'color':exp_light,
                'radius':self.ef_11})
             ba.timer(0.3,self.radius_light.delete) 
                  
          self.impact_scale = self.impact_scale * DASH_DODGE_DAMAGE_REDUCTION
          self.dash_ready = False
          self.dodging = True
          self.pressed_2 = False
          self.pressed_1 = False
          self.dodging_timer = ba.Timer(0.1,ba.Call(undodge))
          self.dash_timer = ba.Timer(DASH_COOLDOWN*0.01,ba.Call(dash_ready))
          self.node.handlemessage("flash")
          self.node.handlemessage('celebrate',400)  
          self.node.handlemessage("impulse",pos[0],pos[1]+DASH_UPWARD_FORCE_SCALE,pos[2],      0,0,0,
                                    DASH_SPEED,0,0,0,self.node.move_left_right,0,-self.node.move_up_down)
          def efex():
            #FIXME - should not use too many booleans here
            for p in range(1,2):
              if not DASH_EFFECT_TENDRIL_TYPE == None and not DASH_EFFECT_EMIT_TYPE == None:
                  ba.emitfx(position=self.node.position,
                    chunk_type=self.ef_1,
                    count=self.ef_2,
                    scale=self.ef_3,
                    spread=self.ef_4,
                    tendril_type=self.ef_5,
                    emit_type=self.ef_6)
              elif not DASH_EFFECT_TENDRIL_TYPE == None and DASH_EFFECT_EMIT_TYPE == None:
                  ba.emitfx(position=self.node.position,
                    chunk_type=self.ef_1,
                    tendril_type=self.ef_5,
                    count=self.ef_2,
                    scale=self.ef_3,
                    spread=self.ef_4)
              elif DASH_EFFECT_TENDRIL_TYPE == None and not DASH_EFFECT_EMIT_TYPE == None:
                  ba.emitfx(position=self.node.position,
                    chunk_type=self.ef_1,
                    emit_type=self.ef_6,
                    count=self.ef_2,
                    scale=self.ef_3,
                    spread=self.ef_4)
              elif DASH_EFFECT_TENDRIL_TYPE == None and DASH_EFFECT_EMIT_TYPE == None:
                  ba.emitfx(position=self.node.position,
                    chunk_type=self.ef_1,
                    count=self.ef_2,
                    scale=self.ef_3,
                    spread=self.ef_4)
          if DASH_ENABLE_EFFECT == True:
            ba.timer(0.02, ba.Call(efex))
            ba.timer(0.15, ba.Call(efex))
            ba.timer(0.24, ba.Call(efex))
            ba.timer(0.26, ba.Call(efex))
    
    
    #=============================================#
    Spaz.on_jump_press = jump_press
    Spaz.on_punch_press = punch_press
    
    