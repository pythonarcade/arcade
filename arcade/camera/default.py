from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

from pyglet.math import Mat4, Vec2, Vec3
from typing_extensions import Self

from arcade.types import LBWH, Point, Rect
from arcade.window_commands import get_window

if TYPE_CHECKING:
    from arcade.context import ArcadeContext

__all__ = ["ViewportProjector", "DefaultProjector"]


class ViewportProjector:
    """
    A simple Projector which does not rely on any camera PoDs.

    Does not have a way of moving, rotating, or zooming the camera.
    perfect for something like UI or for mapping to an offscreen framebuffer.

    Args:
        viewport: The viewport to project to.
        window: The window to bind the camera to. Defaults to the currently active window.
    """

    def __init__(
        self,
        viewport: Rect | None = None,
        *,
        context: ArcadeContext | None = None,
    ):
        self._ctx: ArcadeContext = context or get_window().ctx
        self._viewport: Rect = viewport or LBWH(*self._ctx.viewport)
        self._projection_matrix: Mat4 = Mat4.orthogonal_projection(
            0.0, self._viewport.width, 0.0, self._viewport.height, -100, 100
        )

    @property
    def viewport(self) -> Rect:
        """
        The viewport use to derive projection and view matrix.
        """
        return self._viewport

    @viewport.setter
    def viewport(self, viewport: Rect) -> None:
        self._viewport = viewport
        self._projection_matrix = Mat4.orthogonal_projection(
            0, viewport.width, 0, viewport.height, -100, 100
        )

    def use(self) -> None:
        """
        Set the window's projection and view matrix.
        Also sets the projector as the windows current camera.
        """
        self._ctx.current_camera = self

        self._ctx.viewport = self.viewport.lbwh_int  # get the integer 4-tuple LBWH

        self._ctx.view_matrix = Mat4()
        self._ctx.projection_matrix = self._projection_matrix

    @contextmanager
    def activate(self) -> Generator[Self, None, None]:
        """
        The context manager version of the use method.

        usable with the 'with' block. e.g. 'with ViewportProjector.activate() as cam: ...'
        """
        previous = self._ctx.current_camera
        try:
            self.use()
            yield self
        finally:
            previous.use()

    def project(self, world_coordinate: Point) -> Vec2:
        """
        Take a Vec2 or Vec3 of coordinates and return the related screen coordinate
        """
        x, y, *z = world_coordinate
        return Vec2(x, y)

    def unproject(self, screen_coordinate: Point) -> Vec3:
        """
        Map the screen pos to screen_coordinates.

        Due to the nature of viewport projector this does not do anything.
        """
        x, y, *z = screen_coordinate
        z = 0.0 if not z else z[0]

        return Vec3(x, y, z)


# As this class is only supposed to be used internally
# I wanted to place an _ in front, but the linting complains
# about it being a protected class.
class DefaultProjector(ViewportProjector):
    """
    An extremely limited projector which lacks any kind of control. This is only
    here to act as the default camera used internally by Arcade. There should be
    no instance where a developer would want to use this class.

    Args:
        window: The window to bind the camera to. Defaults to the currently active window.
    """

    def __init__(self, *, context: ArcadeContext | None = None):
        super().__init__(context=context)

    def use(self) -> None:
        """
        Set the window's Projection and View matrices.

        cache's the window viewport to determine the projection matrix.
        """

        viewport = self.viewport.lbwh_int
        # If the viewport is correct and the default camera is in use,
        # then don't waste time resetting the view and projection matrices
        if self._ctx.viewport == viewport and self._ctx.current_camera == self:
            return

        # If the viewport has changed while the default camera is active then the
        # default needs to update itself.
        # If it was another camera's viewport being used the default camera should not update.
        if self._ctx.viewport != viewport and self._ctx.current_camera == self:
            self.viewport = LBWH(*self._ctx.viewport)
        else:
            self._ctx.viewport = viewport

        self._ctx.current_camera = self

        self._ctx.view_matrix = Mat4()
        self._ctx.projection_matrix = self._projection_matrix
