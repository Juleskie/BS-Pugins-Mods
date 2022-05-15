# Released under the MIT License. See LICENSE for details.

# ba_meta require api 6

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import ba, _ba, base64
from bastd.ui import party
from bastd.ui.party import PartyWindow

if TYPE_CHECKING:
    from typing import Sequence

class TermialWindow(ba.Window):
   """class object for showing terminal"""
   def __init__(self, origin: Sequence[float] = (0, 0)):
     self._root_widget = ba.containerwidget(
                         scale_origin_stack_offset=origin,
                         transition='in_scale',
                         parent=_ba.get_special_widget('overlay_stack'),
                         color=(0.25,0.30,0.28),
                         scale=2.0,
                         size=(660,350),
                         stack_offset=(0, -10))
     self.interval_update = None
     
     def close():
        self.interval_update = None
        ba.containerwidget(edit=self._root_widget, transition='out_scale')
     
     self._scrollwidget = ba.scrollwidget(parent=self._root_widget,
                                      size=(560, 266),
                                      position=(55, 62),
                                      color=(0,0,0))
     self.ok_button = ba.buttonwidget(parent=self._root_widget,
                                      color=(0.46, 0.59, 0.62),
                                      position=(356, 15),
                                      size=(498, 79),
                                      on_activate_call=close,
                                      label='Ok',
                                      autoselect=True,
                                      button_type='square',
                                      scale=0.55)
     self.subparent = sub = ba.containerwidget(parent=self._scrollwidget,size=(900,9999),background=False,claims_left_right=False,claims_tab=False)
     self.terminal_field = ba.textwidget(parent=sub,
                                      scale=0.499,
                                      color=(1, 1, 1, 1),
                                      text='',
                                      size=(0, 0),
                                      autoselect=True,
                                      position=(0,9400),
                                      maxwidth=800.0,
                                      h_align='left',
                                      v_align='center')
     def update():
        try:
          txt = cast(str, ba.textwidget(query=self.terminal_field))
          lines = len(txt.splitlines())
          value = lines*12.5
          ba.containerwidget(parent=self._scrollwidget,edit=self.subparent, size=(900, value))
          ba.textwidget(parent=sub,edit=self.terminal_field, text=_ba.getlog(), scale=0.385, position=(0, (value - (lines * 6.16))-5))
          ba.widget(edit=self.subparent,size=(900,self.count))
        except: pass
        
     ba.containerwidget(edit=self._root_widget, cancel_button=self.ok_button)
     self.interval_update = ba.timer(0.1, update, repeat=True)

def open_party():
    _ba.set_party_icon_always_visible(True)

PartyWindow.init = PartyWindow.__init__
class Replaceables_Windows(PartyWindow):
  def __init__(self, origin: Sequence[float] = (0, 0)):
    self.init(origin)
    self._internal_button = ba.buttonwidget(parent=self._root_widget,
                                              scale=0.7,
                                              position=(518, self._height - 260),
                                              size=(100, 350),
                                              label='',
                                              button_type='square',
                                              on_activate_call=lambda: TermialWindow(),
                                              autoselect=True,
                                              color=(0.4,0.4,0.4),
                                              icon=None,
                                              iconscale=1.2)

# ba_meta export plugin
class desu(ba.Plugin):
  def __init__(self):
      ba.timer(0.9, open_party, repeat=True)
      party.PartyWindow = Replaceables_Windows
  