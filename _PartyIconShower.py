# Released under the MIT License. See LICENSE for details.
# ba_meta require api 6
from ba import app, Plugin

import _ba
import ba

def check_icon() -> None:
	if _ba.set_party_icon_always_visible == True:
		return
    else:
        _ba.set_party_icon_always_visible(True)
	
# ba_meta export plugin
class desu(ba.Plugin):
	def on_app_launch(self) -> None:
		ba.timer(1.0,check_icon,repeat=True)
