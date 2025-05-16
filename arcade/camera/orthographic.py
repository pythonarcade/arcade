from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from pyglet.math import Mat4, Vec2, Vec3
from typing_extensions import Self

from arcade.camera.data_types import (
    DEFAULT_FAR,
    DEFAULT_NEAR_ORTHO,
    CameraData,
    OrthographicProjectionData,
    Projector,
)
from arcade.camera.projection_functions import (
    generate_orthographic_matrix,
    generate_view_matrix,
    project_orthographic,
    unproject_orthographic,
)
from arcade.types import LBWH, Point, Rect
from arcade.window_commands import get_window

if TYPE_CHECKING:
    from arcade import Window


__all__ = ["OrthographicProjector"]


class OrthographicProjector(Projector):
    """
    The simplest from of an orthographic camera.
    Using ViewData and OrthographicProjectionData PoDs (Pack of Data)
    it generates the correct projection and view matrices. It also
    provides methods and a context manager for using the matrices in
    glsl shaders.

    This class provides no methods for manipulating the PoDs.

    The current implementation will recreate the view and
    projection matrices every time the camera is used.
    If used every frame or multiple times per frame this may
    be inefficient. If you suspect this is causing slowdowns
    profile before optimizing with a dirty value check.

    Initialize a Projector which produces an orthographic projection matrix using
    a CameraData and PerspectiveProjectionData PoDs.

    Args:
        window:
            The window to bind the camera to. Defaults to the currently active camera.
        view:
            The CameraData PoD. contains the viewport, position, up, forward, and zoom.
        projection:
            The OrthographicProjectionData PoD.
            contains the left, right, bottom top, near, and far planes.
    """

    def __init__(
        self,
        *,
        window: Window | None = None,
        view: CameraData | None = None,
        projection: OrthographicProjectionData | None = None,
        viewport: Rect | None = None,
        scissor: Rect | None = None,
    ):
        self._window: Window = window or get_window()

        self.viewport: Rect = viewport or LBWH(0, 0, self._window.width, self._window.height)
        self.scissor: Rect | None = scissor

        self._view = view or CameraData(  # Viewport
            (self._window.width / 2, self._window.height / 2, 0),  # Position
            (0.0, 1.0, 0.0),  # Up
            (0.0, 0.0, -1.0),  # Forward
            1.0,  # Zoom
        )

        self._projection = projection or OrthographicProjectionData(
            -0.5 * self._window.width,
            0.5 * self._window.width,  # Left, Right
            -0.5 * self._window.height,
            0.5 * self._window.height,  # Bottom, Top
            DEFAULT_NEAR_ORTHO,
            DEFAULT_FAR,  # Near, Far
        )

    @property
    def view(self) -> CameraData:
        """
        The CameraData. Is a read only property.
        """
        return self._view

    @property
    def projection(self) -> OrthographicProjectionData:
        """
        The OrthographicProjectionData. Is a read only property.
        """
        return self._projection

    def generate_projection_matrix(self) -> Mat4:
        """
        alias of arcade.camera.get_orthographic_matrix method
        """
        return generate_orthographic_matrix(self._projection, self._view.zoom)

    def generate_view_matrix(self) -> Mat4:
        """
        alias of arcade.camera.get_view_matrix method
        """
        return generate_view_matrix(self._view)

    def use(self) -> None:
        """
        Sets the active camera to this object.
        Then generates the view and projection matrices.
        Finally, the gl context viewport is set, as well as the projection and view matrices.
        """

        self._window.current_camera = self

        _projection = generate_orthographic_matrix(self._projection, self._view.zoom)
        _view = generate_view_matrix(self._view)

        self._window.ctx.viewport = self.viewport.lbwh_int
        self._window.ctx.scissor = None if not self.scissor else self.scissor.lbwh_int
        self._window.projection = _projection
        self._window.view = _view

    @contextmanager
    def activate(self) -> Generator[Self, None, None]:
        """Set this camera as the current one, then undo it after.

        This method is a :external:ref:`context manager <context-managers>`
        you can use inside ``with`` blocks. Using it this way guarantees
        that the old camera and its settings will be restored, even if an
        exception occurs:

        .. code-block:: python

           # Despite an Exception, the previous camera and its settings
           # will be restored at the end of the with block below:
           with projector_instance.activate():
                sprite_list.draw()
                _ = 1 / 0  # Guaranteed ZeroDivisionError

        """
        previous_projector = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous_projector.use()

    def project(self, world_coordinate: Point) -> Vec2:
        """
        Take a Vec2 or Vec3 of coordinates and return the related screen coordinate
        """
        _projection = generate_orthographic_matrix(self._projection, self._view.zoom)
        _view = generate_view_matrix(self._view)

        return project_orthographic(
            world_coordinate,
            self.viewport.lbwh_int,
            _view,
            _projection,
        )

    def unproject(self, screen_coordinate: Point) -> Vec3:
        """
        Take in a pixel coordinate from within
        the range of the window size and returns
        the world space coordinates.

        Essentially reverses the effects of the projector.

        Args:
            screen_coordinate: A 2D position in pixels from the bottom left of the screen.
                               This should ALWAYS be in the range of 0.0 - screen size.
        Returns:
            A 3D vector in world space.
        """
        _projection = generate_orthographic_matrix(self._projection, self._view.zoom)
        _view = generate_view_matrix(self._view)
        return unproject_orthographic(screen_coordinate, self.viewport.lbwh_int, _view, _projection)
