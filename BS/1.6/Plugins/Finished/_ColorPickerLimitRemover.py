# Released under the MIT License. See LICENSE for details.
# ba_meta require api 6
from __future__ import annotations
from typing import TYPE_CHECKING
import ba, _ba

if TYPE_CHECKING:
	pass
from bastd.ui.colorpicker import ColorPickerExact

def replacement(self, color_name: str, increasing: bool) -> None:
     current_time = ba.time(ba.TimeType.REAL, ba.TimeFormat.MILLISECONDS)
     since_last = current_time - self._last_press_time
     if (since_last < 200 and self._last_press_color_name == color_name
          and self._last_press_increasing == increasing):
        self._change_speed += 0.25
     else:
        self._change_speed = 1.0
     self._last_press_time = current_time
     self._last_press_color_name = color_name
     self._last_press_increasing = increasing

     color_index = ('r', 'g', 'b').index(color_name)
     offs = int(self._change_speed) * (0.01 if increasing else -0.01)
     self._color[color_index] = max(
            0.0, min(100.0, self._color[color_index] + offs))
     self._update_for_color()
     
ColorPickerExact._color_change_press = replacement

# ba_meta export plugin
class Juleskie(ba.Plugin):
	pass