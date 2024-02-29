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
    """
    A simple Projector which does not rely on any camera PoDs.

    Does not have a way of moving, rotating, or zooming the camera.
    perfect for something like UI or for mapping to an offscreen framebuffer.
    """

    def __init__(self, viewport: Optional[Tuple[int, int, int, int]] = None, *, window: Optional["Window"] = None):
        """
        Initialize a ViewportProjector

        Args:
            viewport: The viewport to project to.
            window: The window to bind the camera to. Defaults to the currently active window.
        """
        self._window = window or get_window()
        self._viewport = viewport or self._window.ctx.viewport
        self._projection_matrix: Mat4 = Mat4.orthogonal_projection(
            0.0, self._viewport[2],
            0.0, self._viewport[3],
            -100, 100
        )

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """
        The viewport use to derive projection and view matrix.
        """
        return self._viewport

    @viewport.setter
    def viewport(self, viewport: Tuple[int, int, int, int]) -> None:
        self._viewport = viewport
        self._projection_matrix = Mat4.orthogonal_projection(
            0, viewport[2],
            0, viewport[3],
            -100, 100)

    def use(self) -> None:
        """
        Set the window's projection and view matrix.
        Also sets the projector as the windows current camera.
        """
        self._window.current_camera = self

        self._window.ctx.viewport = self._viewport

        self._window.ctx.view_matrix = Mat4()
        self._window.ctx.projection_matrix = self._projection_matrix

    @contextmanager
    def activate(self) -> Iterator[Projector]:
        """
        The context manager version of the use method.

        usable with the 'with' block. e.g. 'with ViewportProjector.activate() as cam: ...'
        """
        previous = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous.use()

    def map_coordinate(self, screen_coordinate: Tuple[float, float], depth = 0.0) -> Tuple[float, float]:
        """
        Map the screen pos to screen_coordinates.

        Due to the nature of viewport projector this does not do anything.
        """
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
        """
        Initialise a ViewportProjector.

        Args:
            window: The window to bind the camera to. Defaults to the currently active camera.
        """
        super().__init__(window=window)

    def use(self) -> None:
        """
        Set the window's Projection and View matrices.

        cache's the window viewport to determine the projection matrix.
        """

        if self._window.ctx.viewport != self.viewport:
            self.viewport = self._window.ctx.viewport
        super().use()
