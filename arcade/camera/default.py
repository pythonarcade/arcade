from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from pyglet.math import Mat4, Vec2, Vec3
from pyglet.window.camera import CameraScissor
from typing_extensions import Self

from arcade.camera.data_types import DEFAULT_FAR, DEFAULT_NEAR_ORTHO
from arcade.types import Point
from arcade.window_commands import get_window

if TYPE_CHECKING:
    from arcade.context import ArcadeContext

__all__ = ()


class DefaultProjector:
    """
    An extremely limited projector which lacks any kind of control. This is only
    here to act as the default camera used internally by Arcade. There should be
    no instance where a developer would want to use this class.

    The job of the default projector is to ensure that when no other Projector
    (Camera2D, OthrographicProjector, PerspectiveProjector, etc) is in use the
    projection and view matrices are correct such at (0.0, 0.0) is in the bottom
    left corner of the viewport and that one pixel equals one 'unit'.

    Args:
        context: The window context to bind the camera to. Defaults to the currently active context.
    """

    def __init__(self, *, context: ArcadeContext | None = None):
        self._ctx: ArcadeContext = context or get_window().ctx
        self._viewport: tuple[int, int, int, int] | None = None
        self._scissor: tuple[int, int, int, int] | None = None
        self._matrix: Mat4 | None = None

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
        if self._ctx.current_camera != self:
            return

        if (
            self._ctx.viewport[2] != self._ctx.fbo.width
            or self._ctx.viewport[3] != self._ctx.fbo.height
        ):
            self.viewport = self._ctx.viewport
        else:
            self.viewport = None

        self.use()

    @property
    def viewport(self) -> tuple[int, int, int, int] | None:
        return self._viewport

    @viewport.setter
    def viewport(self, viewport: tuple[int, int, int, int] | None) -> None:
        self._viewport = viewport
        self._matrix = Mat4.orthogonal_projection(
            0, self.width, 0, self.height, DEFAULT_NEAR_ORTHO, DEFAULT_FAR
        )

    @viewport.deleter
    def viewport(self):
        self.viewport = None

    @property
    def scissor(self) -> tuple[int, int, int, int] | None:
        return self._scissor

    @scissor.setter
    def scissor(self, scissor: tuple[int, int, int, int] | None) -> None:
        self._scissor = scissor

    @scissor.deleter
    def scissor(self) -> None:
        self._scissor = None

    @property
    def width(self) -> int:
        if self._viewport is not None:
            return int(self._viewport[2])
        return self._ctx.fbo.width

    @property
    def height(self) -> int:
        if self._viewport is not None:
            return int(self._viewport[3])
        return self._ctx.fbo.height

    def get_current_viewport(self) -> tuple[int, int, int, int]:
        if self._viewport is not None:
            return self._viewport
        return (0, 0, self._ctx.fbo.width, self._ctx.fbo.height)

    def use(self) -> None:
        """
        Set the window's Projection and View matrices.
        """

        viewport = self.get_current_viewport()

        self._ctx.current_camera = self
        if self._ctx.viewport != viewport:
            self._ctx.active_framebuffer.viewport = viewport
        self._ctx.scissor = None if self._scissor is None else self._scissor

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
        previous_projector = self._ctx.current_camera
        previous_view = self._ctx.view_matrix
        previous_projection = self._ctx.projection_matrix
        previous_scissor = self._ctx.scissor
        previous_viewport = self._ctx.viewport
        try:
            self.use()
            yield self
        finally:
            self._ctx.viewport = previous_viewport
            self._ctx.scissor = previous_scissor
            self._ctx.projection_matrix = previous_projection
            self._ctx.view_matrix = previous_view
            self._ctx.current_camera = previous_projector

    # --- pyglet dev6 batch-draw compatibility shim ---
    #
    # pyglet's own Batch.draw() (used e.g. by pyglet.text.Label.draw(), which
    # arcade.Text delegates to) falls back to `window.default_camera` when no
    # explicit camera is given. Since Arcade overrides `default_camera` to
    # return this class instead of pyglet's own Camera2D, pyglet's batch
    # pipeline needs DefaultProjector to satisfy its internal
    # CameraScopeProtocol (`.view.scissor`, `.begin()`,
    # `.get_group_scissor_area()`) or it raises AttributeError.
    @property
    def view(self) -> Self:
        return self

    def begin(self, *, draw_context, commit: bool = True) -> None:
        pass

    def get_group_scissor_area(self) -> CameraScissor:
        # MUST NOT return None here. pyglet's GL renderer treats a scissor
        # of None as "disable scissor testing entirely"
        # (pyglet/graphics/api/gl/renderer.py: `set_scissor(None)` calls
        # `glDisable(GL_SCISSOR_TEST)`) — but Arcade enables scissor testing
        # once at context creation and never revisits it (it's not one of
        # the flags `Context.enable`/`disable` manage), relying on the
        # scissor *rectangle* alone to control the visible area. Returning
        # None here let any pyglet-native draw with no camera set (e.g. any
        # `arcade.Text`/`draw_text()` call, since those go through
        # `pyglet.text.Label.draw()`) permanently disable scissor testing
        # for the rest of the process — breaking any later viewport-scoped
        # clear (`Framebuffer.clear(viewport=...)`) anywhere in the
        # session. Returning a real scissor rectangle matching the current
        # viewport keeps scissor testing enabled without restricting
        # anything beyond what's already visible.
        return CameraScissor(*(self._scissor or self.get_current_viewport()))

    # pyglet's base Window.projection/.view properties (dev6+) delegate to
    # `self.default_camera.projection` / `.view_matrix` respectively
    # (`pyglet/window/__init__.py`). Any code that reads/writes
    # `window.projection`/`window.view` — pyglet's own internals, test
    # infrastructure, or downstream user code — routes through here once
    # Arcade's `default_camera` override is in the MRO, so these need to
    # exist and behave sensibly rather than raise AttributeError.
    @property
    def projection(self) -> Mat4:
        if self._matrix is None:
            self._matrix = Mat4.orthogonal_projection(
                0, self.width, 0, self.height, DEFAULT_NEAR_ORTHO, DEFAULT_FAR
            )
        return self._matrix

    @projection.setter
    def projection(self, value: Mat4) -> None:
        self._matrix = value
        if self._ctx.current_camera is self:
            self._ctx.projection_matrix = value

    @property
    def view_matrix(self) -> Mat4:
        # DefaultProjector always uses an identity view (see .use()) — this
        # mirrors that rather than tracking a separate, never-applied state.
        return Mat4()

    @view_matrix.setter
    def view_matrix(self, value: Mat4) -> None:
        if self._ctx.current_camera is self:
            self._ctx.view_matrix = value

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
