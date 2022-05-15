# Released under the MIT License. See LICENSE for details.
# bs_meta require api 6

from __future__ import annotations

from typing import TYPE_CHECKING
from bastd.gameutils import SharedObjects
from ba._gameutils import animate

import ba as bs

if TYPE_CHECKING:
    pass

# ----- data lists -----
# [body filters]: landMine, capsule, puck, box, crate, sphere

# [model filters]: check Bombsquad\ba_data\models

# [tex filters]: check Bombsquad\ba_data\texture

# [size_c]: collision size of the object
# [size_m]: the size of the visible & only thing that can be seen on the object
# [lifespan]: how long will the object last?
# [r_scl]: how high is the luster of the object is


class Particle(bs.Actor):
  def __init__(self,
               pos: float = (0,0,0),
               vel: float = (0,0,0),
               body: str = 'landMine',
               model: str = 'neoSpazHead',
               tex: str = 'neoSpazColor',
               size_c: float = 1.0,
               size_m: float = 1.0,
               r_scl: float = 1.0,
               lifespan: float = 25.0):
    super().__init__()
    self.model = model
    self.tex = tex
    self.szm = size_m
    self.szc = size_c
    self.rscale = r_scl
    self.body = body
    self.lifespan = lifespan
    
    shared = SharedObjects.get()
    
    self.mat = bs.Material()
    self.mat.add_actions(
        conditions=(
        ('they_have_material',shared.footing_material)
        ),
        actions=(
        ('modify_node_collision','collide',True)
        ))
    self.mat.add_actions(
        conditions=(
        ('they_have_material',shared.footing_material),
        'and',
        ('they_have_material',shared.object_material)),
        actions=(
        ('modify_node_collision','collide',False),
        ('modify_part_collision','physical',False)
        ))
    self.mat.add_actions(
        conditions=(
        ('they_dont_have_material',shared.footing_material)),
        actions=(
        ('modify_node_collision','collide',False),
        ('modify_part_collision','physical',False)
        ))

    self.node = bs.newnode('prop',
                           delegate=self,
                           owner=None,
                           attrs={'position':pos,
                          'velocity':vel,
                          'model':bs.getmodel(self.model),
                          'light_model':bs.getmodel(self.model),
                          'body':self.body,
                          'body_scale':self.szc,
                          'shadow_size':0.0000001,
                          'gravity_scale':1.0,
                          'color_texture':bs.gettexture(self.tex),
                          'reflection':'powerup',
                          'reflection_scale':[self.rscale],
                          'materials':[shared.object_material, self.mat]})
                                      
    animate(self.node,"model_scale",
    {
    0: self.szm, 
    self.lifespan: 0
    })
    def remove(): self.node.delete
    bs.timer(self.lifespan + 1, remove)

  def handlemessage(self, msg):

    if isinstance(msg, bs.DieMessage):
       self.node.delete()
    elif isinstance(msg ,bs.OutOfBoundsMessage): self.handlemessage(bs.DieMessage())
    else: super().handlemessage(msg)

