#
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
   from typing import Optional

import ba, shutil

def do_remove():
  r = shutil.rmtree
  p: str[Optional] = ba.app.python_directory_app
  r(p + '/efro/__pycache__')
  r(p + '/efro/entity/__pycache__')
  r(p + '/bacommon/__pycache__')
  r(p + '/bastd/__pycache__')
  r(p + '/bastd/actor/__pycache__')
  r(p + '/bastd/game/__pycache__')
  r(p + '/bastd/mapdata/__pycache__')
  r(p + '/bastd/ui/__pycache__')
  r(p + '/bastd/ui/account/__pycache__')
  r(p + '/bastd/ui/gather/__pycache__')
  r(p + '/bastd/ui/settings/__pycache__')
  r(p + '/bastd/ui/store/__pycache__')
  r(p + '/ba/__pycache__')

# ba_meta require api 6
# ba_meta export plugin
class desu(ba.Plugin):
  def on_app_launch(self) -> None:
    if ba.app.platform == 'windows':
       do_remove()