from __future__ import annotations
from typing import Any

import logging
import time
import subprocess

from pywm import (
    PyWM,
    PyWMDownstreamState,
    PyWMBackgroundWidget,
    PyWMWidgetDownstreamState,
    PyWMOutput
)

from .view import View
from .args import args
from .grid import Grid

conf_pywm: dict[str, Any] = {
    'xkb_model': args.keyboard_model,
    'xkb_layout': args.keyboard_layout,
    'xkb_options': args.keyboard_options,

    'xcursor_theme': args.xcursor_theme,
    'xcursor_size': args.xcursor_size,

    'natural_scroll': not args.no_natural_scroll,

    'encourage_csd': False,
    'enable_xwayland': True,
    'texture_shaders': 'noeffect'
}
conf_outputs: list[dict[str, Any]] = []

logger = logging.getLogger(__name__)

class Background(PyWMBackgroundWidget):
    def __init__(self, wm: Compositor, output: PyWMOutput, *args: Any, **kwargs: Any) -> None:
        self.output: PyWMOutput = output
        super().__init__(wm, self.output, 'invalid')

    def process(self) -> PyWMWidgetDownstreamState:
        result = PyWMWidgetDownstreamState()
        result.z_index = -10000
        result.box = self.output.pos[0], self.output.pos[1], self.output.width, self.output.height
        result.opacity = 1.
        return result

class Compositor(PyWM[View]):
    def __init__(self) -> None:
        PyWM.__init__(self, View, **conf_pywm, outputs=conf_outputs, debug=True)

    def process(self) -> PyWMDownstreamState:
        return PyWMDownstreamState()

    def main(self) -> None:
        logger.debug("Compositor main...")
        self.update_cursor()

        self.background = self.create_widget(Background, self.layout[0])
        self.damage()

        if args.grid is None:
            logger.error("No grid file specified")
            self.terminate()
            return
        else:
            logger.debug("Grid file: %s", args.grid)
            self.grid = Grid(args.grid)

        while (app := self.grid.next_app()) is not None:
            logger.debug("Starting %s...", app) 
            proc = subprocess.Popen(app.split(" "))
            self.grid.started_next_app(proc.pid)


        time.sleep(5)
        if len(self._views) == 0:
            self.terminate()

    def destroy_view(self, view: View) -> None:
        logger.info("Destroying view %s", view)
        if len([v for v in self._views.values() if v._handle != view._handle]) == 0:
            self.terminate()
