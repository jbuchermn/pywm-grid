from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar

import logging
from math import floor

from pywm import PyWMView, PyWMViewDownstreamState
from pywm.pywm_view import PyWMViewUpstreamState

from .args import args


if TYPE_CHECKING:
    from .compositor import Compositor
else:
    Compositor = TypeVar('Compositor')

logger = logging.getLogger(__name__)

class View(PyWMView[Compositor]):
    def __init__(self, wm: Compositor, handle: int):
        PyWMView.__init__(self, wm, handle)
        logger.debug("New view - %s" % self.up_state)

        self.j, self.i = self.wm.grid.find_view(self.pid) if self.pid is not None else (-1, -1)  # Transpose

    def init(self) -> PyWMViewDownstreamState:
        if self.up_state is None:
            return PyWMViewDownstreamState()

        if self.i == -1 and self.pid is not None:
            self.j, self.i = self.wm.grid.find_view(self.pid) # Transpose
            self.damage()

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

        res = PyWMViewDownstreamState(self._handle, (x, y, width, height), accepts_input=True, floating=False)

        width *= args.scale
        height *= args.scale

        logger.debug("View has size %dx%d", *self.up_state.size)

        """
        Workaround due to mpv bug - it needs to set its own size first
        to truly believe the size we're requesting is what we want
        """
        if self.up_state.size != (0, 0):
            res.size = (width, height)
            self.force_size()

        if self.up_state.size != res.size:
            res.opacity = 0.
            self.damage()

        return res

    def process(self, up_state: PyWMViewUpstreamState) -> PyWMViewDownstreamState:
        return self.init()

    def destroy(self) -> None:
        self.wm.destroy_view(self)
