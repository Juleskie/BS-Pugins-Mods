# Released under the MIT License. See LICENSE for details.
# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations
from typing import TYPE_CHECKING
from bastd.actor import playerspaz
from bastd.actor.popuptext import PopupText
import ba, math, random, _ba

if TYPE_CHECKING:
    pass

# Coded in 1.6.4



# ------------MANUAL--------------------------
#1 - Integer
#2 - Integer With Decimals
#3 - Percentage
#4 - Percentage With Decimals
DAMAGE_FORMAT = 1
DAMAGE_DECIMAL_LIMIT = 1
DAMAGE_TEXT_SCALING = 0.01
DAMAGE_TEXT_COLOR = "DAMAGE_TYPE"
# AVAILABLE OPTIONS FOR DAMAGE TEXT COLOR:
# RANDOM, MATCH, DAMAGE_TYPE
# TO USE THESE OPTIONS: REMOVE THE (1.0, 1.0, 1.0) and REPLACE THEM WITH "RANDOM" or "MATCH" or "DAMAGE_TYPE"
#
# RANDOM - RANDOMIZED RGB 
# MATCH - USES THE SPAZ's COLOR as THE COLOR TEXT
# DAMAGE_TYPE - COLORS BASED ON DAMAGE TYPE (punch, explosions, etc..)
# [RED - PUNCH] [YELLOW - BOMB] [GRAY - IMPACTS] 
#--------------------------------------------

DAMAGE_TYPES_EXCLUDED = [] #"PUNCH", "BOMB", "IMPACT"
# An example of adding a string to list: DAMAGE_TYPES_EXCLUDED = ["PUNCH","BOMB"]
# otherwise replace ["PUNCH"] with [] if you dont want to exclude
# BOMB - Explosion from bombs
# IMPACT - Damage caused by hitting your head on the ground or map
# PUNCH - Damage caused by punches
#--------------------------------------------
   

def show_dam(damage: str, position: Sequence[float],
                      direction: Sequence[float], color: Sequence[float], scale: float) -> None:
    lifespan = 1.0
    # FIXME: Should never vary game elements based on local config.
    #  (connected clients may have differing configs so they won't
    #  get the intended results).
    txtnode = _ba.newnode('text',
                          attrs={
                              'text': damage,
                              'in_world': True,
                              'h_align': 'center',
                              'flatness': 1.0,
                              'shadow': 0.7,
                              'color': color,
                              'scale': scale})
    # Translate upward.
    tcombine = _ba.newnode('combine', owner=txtnode, attrs={'size': 3})
    tcombine.connectattr('output', txtnode, 'position')
    v_vals = []
    pval = 0.0
    vval = 0.07
    count = 6
    for i in range(count):
        v_vals.append((float(i) / count, pval))
        pval += vval
        vval *= 0.5
    p_start = position[0]
    p_dir = direction[0]
    ba.animate(tcombine, 'input0',
            {i[0] * lifespan: p_start + p_dir * i[1]
             for i in v_vals})
    p_start = position[1]
    p_dir = direction[1]
    ba.animate(tcombine, 'input1',
            {i[0] * lifespan: p_start + p_dir * i[1]
             for i in v_vals})
    p_start = position[2]
    p_dir = direction[2]
    ba.animate(tcombine, 'input2',
            {i[0] * lifespan: p_start + p_dir * i[1]
             for i in v_vals})
    ba.animate(txtnode, 'opacity', {0.7 * lifespan: 1.0, lifespan: 0.0})
    _ba.timer(lifespan, txtnode.delete)

Replaceable_Spaz = playerspaz.PlayerSpaz
class DmgSpaz(Replaceable_Spaz):
   def handlemessage(self, msg: Any) -> None:
     if isinstance(msg, ba.HitMessage):
        POS = self.node.position
        damascale = 0.22
        damage = self.node.damage * damascale
        SCALING = DAMAGE_TEXT_SCALING
        if DAMAGE_FORMAT == 1:
           self.STRING_1 = str(int(damage))
        elif DAMAGE_FORMAT == 2:
           self.STRING_1 = str(round(damage, DAMAGE_DECIMAL_LIMIT))
        elif DAMAGE_FORMAT == 3:
           self.STRING_1 = str(int(damage/10))
        elif DAMAGE_FORMAT == 4:
           self.STRING_1 = str(round(damage/10, DAMAGE_DECIMAL_LIMIT))
        if DAMAGE_FORMAT == 3 or DAMAGE_FORMAT == 4:
           STRING_2 = "%"
        else: STRING_2 = ""
        if not msg.hit_type in self.FILTERING and not self.hitpoints == 0:
           if DAMAGE_TEXT_COLOR == "MATCH": COLOR_TYPE = self.node.color
           elif DAMAGE_TEXT_COLOR == "RANDOM": COLOR_TYPE = (random.random(),random.random(),random.random())
           elif DAMAGE_TEXT_COLOR == "DAMAGE_TYPE" and msg.hit_type == 'punch': COLOR_TYPE = (1.0,0.2,0.2)
           elif DAMAGE_TEXT_COLOR == "DAMAGE_TYPE" and msg.hit_type == 'explosion': COLOR_TYPE = (1.0,0.85,0)
           elif DAMAGE_TEXT_COLOR == "DAMAGE_TYPE" and msg.hit_type == 'impact': COLOR_TYPE = (0.8,0.8,0.8)
           else: COLOR_TYPE = DAMAGE_TEXT_COLOR
           if msg.hit_type == 'punch':
              show_dam('-' + self.STRING_1 + STRING_2,
                                         msg.pos, msg.force_direction, COLOR_TYPE, DAMAGE_TEXT_SCALING)
           else:
              show_dam('-' + self.STRING_1 + STRING_2,
                                         self.node.position, (self.node.position[0]+random.uniform(0.1,0.3),self.node.position[1]+random.uniform(0.1,0.3),self.node.position[2]+random.uniform(0.1,0.3)), COLOR_TYPE, DAMAGE_TEXT_SCALING)
             # PopupText(
           #  text=self.STRING_1 + STRING_2,
          #   color=COLOR_TYPE,
         #    scale=SCALING,
          #   position=(POS[0],POS[1]-(DAMAGE_TEXT_OFFSET*0.1),POS[2]
          #   )).autoretain()
             
        source_player = msg.get_source_player(type(self._player))
        if source_player:
            self.last_player_attacked_by = source_player
            self.last_attacked_time = ba.time()
            self.last_attacked_type = (msg.hit_type, msg.hit_subtype)
        super().handlemessage(msg)  # Augment standard behavior.
        activity = self._activity()
        if activity is not None and self._player.exists():
            activity.handlemessage(playerspaz.PlayerSpazHurtMessage)
     else:
        return super().handlemessage(msg)
     return None
      
# ba_meta export plugin
class Damage_Shower_Plugin(ba.Plugin):
    from ba._gameutils import show_damage_count
    playerspaz.PlayerSpaz = DmgSpaz
    playerspaz.PlayerSpaz.FILTERING = []
    playerspaz.PlayerSpaz.STRING_1 = ""
    if "BOMB" in DAMAGE_TYPES_EXCLUDED: playerspaz.PlayerSpaz.FILTERING += ['explosion']
    if "PUNCH" in DAMAGE_TYPES_EXCLUDED: playerspaz.PlayerSpaz.FILTERING += ['punch']
    if "IMPACT" in DAMAGE_TYPES_EXCLUDED: playerspaz.PlayerSpaz.FILTERING += ['impact']