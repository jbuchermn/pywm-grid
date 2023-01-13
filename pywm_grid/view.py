from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar

import logging
from math import floor

from pywm import PyWMView, PyWMViewDownstreamState
from pywm.pywm_view import PyWMViewUpstreamState

if TYPE_CHECKING:
    from .compositor import Compositor
else:
    Compositor = TypeVar('Compositor')

logger = logging.getLogger(__name__)

class View(PyWMView[Compositor]):
    def __init__(self, wm: Compositor, handle: int):
        PyWMView.__init__(self, wm, handle)
        logger.debug("New view - %s" % self.up_state)

        self.j, self.i = self.wm.grid.find_next_app()  # Transpose

    def init(self) -> PyWMViewDownstreamState:
        if self.up_state is None:
            return PyWMViewDownstreamState()

        i, j = self.i, self.j

        x = self.wm.layout[0].pos[0] - self.up_state.offset[0] + i*floor(self.wm.layout[0].width/self.wm.grid.get_width())
        y = self.wm.layout[0].pos[1] - self.up_state.offset[1] + j*floor(self.wm.layout[0].height/self.wm.grid.get_height())


        if i == self.wm.grid.get_width() - 1:
            width = self.wm.layout[0].width - (self.wm.grid.get_width() - 1) * floor(self.wm.layout[0].width/self.wm.grid.get_width())
        else:
            width = floor(self.wm.layout[0].width/self.wm.grid.get_width())

        if j == self.wm.grid.get_height() - 1:
            height = self.wm.layout[0].height - (self.wm.grid.get_height() - 1) * floor(self.wm.layout[0].height/self.wm.grid.get_height())
        else:
            height = floor(self.wm.layout[0].height/self.wm.grid.get_height())

        res = PyWMViewDownstreamState(self._handle, (x, y, width, height), accepts_input=True)
        res.size = width, height

        self.focus()

        return res

    def process(self, up_state: PyWMViewUpstreamState) -> PyWMViewDownstreamState:
        return self.init()

    def destroy(self) -> None:
        self.wm.destroy_view(self)
