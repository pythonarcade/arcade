from typing import Optional, Tuple, Iterator, TYPE_CHECKING
from contextlib import contextmanager

from pyglet.math import Mat4

from arcade.camera.types import Projector
from arcade.window_commands import get_window
if TYPE_CHECKING:
    from arcade.application import Window

__all__ = [
    'ViewportProjector',
    'DefaultProjector'
]


class ViewportProjector:

    def __init__(self, viewport: Optional[Tuple[int, int, int, int]] = None, *, window: Optional["Window"] = None):
        self._window = window or get_window()

        self._viewport = viewport or self._window.ctx.viewport
        self._projection_matrix: Mat4 = Mat4.orthogonal_projection(0, self._viewport[2],
                                                                   0, self._viewport[3],
                                                                   -100, 100)

    @property
    def viewport(self):
        return self._viewport

    @viewport.setter
    def viewport(self, viewport: Tuple[int, int, int, int]):
        self._viewport = viewport

        self._projection_matrix = Mat4.orthogonal_projection(0, viewport[2],
                                                             0, viewport[3],
                                                             -100, 100)

    def use(self):
        self._window.current_camera = self

        self._window.ctx.viewport = self._viewport

        self._window.ctx.view_matrix = Mat4()
        self._window.ctx.projection_matrix = self._projection_matrix

    @contextmanager
    def activate(self) -> Iterator[Projector]:
        previous = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous.use()

    def map_coordinate(self, screen_coordinate: Tuple[float, float]) -> Tuple[float, float]:
        return screen_coordinate


# As this class is only supposed to be used internally
# I wanted to place an _ in front, but the linting complains
# about it being a protected class.
class DefaultProjector(ViewportProjector):
    """
    An extremely limited projector which lacks any kind of control. This is only here to act as the default camera
    used internally by arcade. There should be no instance where a developer would want to use this class.
    """
    # TODO: ADD PARAMS TO DOC FOR __init__

    def __init__(self, *, window: Optional["Window"] = None):
        super().__init__(window=window)

    def use(self):
        if self._window.ctx.viewport != self.viewport:
            self.viewport = self._window.ctx.viewport
        super().use()
