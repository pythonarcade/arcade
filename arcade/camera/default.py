from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from pyglet.math import Mat4, Vec2, Vec3
from pyglet.window.key import F
from typing_extensions import Self

from arcade.types import LBWH, Point, Rect
from arcade.window_commands import get_window
from arcade.camera.data_types import DEFAULT_NEAR_ORTHO, DEFAULT_FAR

if TYPE_CHECKING:
    from arcade.context import ArcadeContext

__all__ = ()


class DefaultProjector:
    """
    An extremely limited projector which lacks any kind of control. This is only
    here to act as the default camera used internally by Arcade. There should be
    no instance where a developer would want to use this class.

    The default viewport tries it's best to allow
    simple usecases with no need to use a camera.

    It does this by defaulting to the size of the active
    framebuffer. If the user sets the framebuffer's viewport
    without a camera then the default camera will match it
    until the framebuffer is changed again.

    Args:
        context: The window context to bind the camera to. Defaults to the currently active context.
    """

    def __init__(self, *, context: ArcadeContext | None = None):
        self._ctx: ArcadeContext = context or get_window().ctx
        self._viewport: Rect | None = None
        self._scissor: Rect | None = None
        self._matrix: Mat4 | None = None
        self._updating: bool = False

    def update_viewport(self):
        """
        Called when the ArcadeContext's viewport or active
        framebuffer has been set. It only actually updates
        the viewport if no other camera is active. Also
        setting the viewport to match the size of the active
        framebuffer sets the viewport to None.
        """
        # If another camera is active then the viewport was probably set
        # by camera.use()
        if self._ctx.current_camera != self or self._updating:
            return
        self._updating = True

            self._ctx.viewport[2] != self._ctx.fbo.width
            or self._ctx.viewport[3] != self._ctx.fbo.height
        ):
            self.viewport = LBWH(*self._ctx.viewport)
        else:
            self.viewport = None

        self.use()
        self._updating = False

    @property
    def viewport(self) -> Rect | None:
        return self._viewport

    @viewport.setter
    def viewport(self, viewport: Rect | None) -> None:
        if viewport == self._viewport:
            return
        self._viewport = viewport
        self._matrix = Mat4.orthogonal_projection(
            0, self.width, 0, self.height, DEFAULT_NEAR_ORTHO, DEFAULT_FAR
        )

    @viewport.deleter
    def viewport(self):
        self.viewport = None

    @property
    def scissor(self) -> Rect | None:
        return self._scissor

    @scissor.setter
    def scissor(self, scissor: Rect | None) -> None:
        self._scissor = scissor

    @scissor.deleter
    def scissor(self) -> None:
        self._scissor = None

    @property
    def width(self) -> int:
        if self._viewport is not None:
            return int(self._viewport.width)
        return self._ctx.fbo.width

    @property
    def height(self) -> int:
        if self._viewport is not None:
            return int(self._viewport.height)
        return self._ctx.active_framebuffer.height
        return self._ctx.fbo.height

    def get_current_viewport(self) -> tuple[int, int, int, int]:
        if self._viewport is not None:
            return self._viewport.lbwh_int
        return (0, 0, self._ctx.fbo.width, self._ctx.fbo.height)

    def use(self) -> None:
        """
        Set the window's Projection and View matrices.
        """

        viewport = self.get_current_viewport()

        self._ctx.current_camera = self
        if self._ctx.viewport != viewport:
            self._ctx.viewport = viewport
        self._ctx.scissor = None if self._scissor is None else self._scissor.lbwh_int

        self._ctx.view_matrix = Mat4()
        if self._matrix is None:
            self._matrix = Mat4.orthogonal_projection(
                0, viewport[2], 0, viewport[3], DEFAULT_NEAR_ORTHO, DEFAULT_FAR
            )
        self._ctx.projection_matrix = self._matrix

    @contextmanager
    def activate(self) -> Generator[Self, None, None]:
        """
        The context manager version of the use method.

        usable with the 'with' block. e.g. 'with ViewportProjector.activate() as cam: ...'
        """
        previous = self._ctx.current_camera
        previous_viewport = self._ctx.viewport
        try:
            self.use()
            yield self
        finally:
            self._ctx.viewport = previous_viewport
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
        x, y, *_z = screen_coordinate
        z = 0.0 if not _z else _z[0]

        return Vec3(x, y, z)
