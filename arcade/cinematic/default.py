from typing import Optional, Tuple, Iterator, TYPE_CHECKING
from contextlib import contextmanager

from pyglet.math import Mat4

from arcade.cinematic.types import Projector
from arcade.window_commands import get_window
if TYPE_CHECKING:
    from arcade.application import Window


class _DefaultProjector:
    """
    An extremely limited projector which lacks any kind of control. This is only here to act as the default camera
    used internally by arcade. There should be no instance where a developer would want to use this class.
    """
    # TODO: ADD PARAMS TO DOC FOR __init__

    def __init__(self, *, window: Optional["Window"] = None):
        self._window: "Window" = window or get_window()

        self._viewport: Tuple[int, int, int, int] = self._window.viewport

        self._projection_matrix: Mat4 = Mat4()

    def _generate_projection_matrix(self):
        left = self._viewport[0]
        right = self._viewport[0] + self._viewport[2]

        bottom = self._viewport[1]
        top = self._viewport[1] + self._viewport[3]

        self._projection_matrix = Mat4.orthogonal_projection(left, right, bottom, top, -100, 100)

    def use(self):
        if self._viewport != self._window.viewport:
            self._viewport = self._window.viewport
            self._generate_projection_matrix()

        self._window.view = Mat4()
        self._window.projection = self._projection_matrix

    @contextmanager
    def activate(self) -> Iterator[Projector]:
        previous = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous.use()

    def get_map_coordinates(self, screen_coordinate: Tuple[float, float]) -> Tuple[float, float]:
        return screen_coordinate
