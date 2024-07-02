from __future__ import annotations

from contextlib import contextmanager
from math import radians, tan
from typing import TYPE_CHECKING, Generator, Optional

from pyglet.math import Mat4, Vec2, Vec3
from typing_extensions import Self

from arcade.camera.data_types import CameraData, PerspectiveProjectionData, Projector
from arcade.camera.projection_functions import (
    generate_perspective_matrix,
    generate_view_matrix,
    project_perspective,
    unproject_perspective,
)
from arcade.types import LBWH, Point, Rect
from arcade.window_commands import get_window

if TYPE_CHECKING:
    from arcade import Window


__all__ = ("PerspectiveProjector",)


class PerspectiveProjector(Projector):
    """
    The simplest from of a perspective camera.
    Using ViewData and PerspectiveProjectionData PoDs (Pack of Data)
    it generates the correct projection and view matrices. It also
    provides methods and a context manager for using the matrices in
    glsl shaders.

    This class provides no methods for manipulating the PoDs.

    The current implementation will recreate the view and
    projection matrices every time the camera is used.
    If used every frame or multiple times per frame this may
    be inefficient. If you suspect this is causing slowdowns
    profile before optimizing with a dirty value check.

    Initialize a Projector which produces a perspective projection matrix using
    a CameraData and PerspectiveProjectionData PoDs.

    :param window: The window to bind the camera to. Defaults to the currently active camera.
    :param view: The CameraData PoD. contains the viewport, position, up, forward, and zoom.
    :param projection: The PerspectiveProjectionData PoD.
                contains the field of view, aspect ratio, and then near and far planes.
    """

    def __init__(
        self,
        *,
        window: Optional["Window"] = None,
        view: Optional[CameraData] = None,
        projection: Optional[PerspectiveProjectionData] = None,
        viewport: Optional[Rect] = None,
        scissor: Optional[Rect] = None,
    ):
        self._window: "Window" = window or get_window()

        self.viewport: Rect = viewport or LBWH(0, 0, self._window.width, self._window.height)
        self.scissor: Optional[Rect] = scissor

        self._view = view or CameraData(  # Viewport
            (self._window.width / 2, self._window.height / 2, 0),  # Position
            (0.0, 1.0, 0.0),  # Up
            (0.0, 0.0, -1.0),  # Forward
            1.0,  # Zoom
        )

        self._projection = projection or PerspectiveProjectionData(
            self._window.width / self._window.height,  # Aspect
            60,  # Field of View,
            0.01,
            100.0,  # near, # far
        )

    @property
    def view(self) -> CameraData:
        """Get the internal :py:class:`~arcade.camera.data_types.CameraData`.

        This is a read-only property.
        The CameraData. Is a read only property.
        """
        return self._view

    @property
    def projection(self) -> PerspectiveProjectionData:
        """Get the :py:class:`~arcade.camera.data_types.PerspectiveProjectionData`.

        This is a read-only property.
        """
        return self._projection

    def generate_projection_matrix(self) -> Mat4:
        """Generates a projection matrix.

        This is an alias of
        :py:class:`arcade.camera.get_perspective_matrix`.
        """
        return generate_perspective_matrix(self._projection, self._view.zoom)

    def generate_view_matrix(self) -> Mat4:
        """Generates a view matrix.

        This is an alias of=
        :py:class:`arcade.camera.get_view_matrix`.
        """
        return generate_view_matrix(self._view)

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

    def use(self) -> None:
        """Set the active camera to this object and apply other config.

        This includes the following steps:

        #. Set the window's current camera to this one
        #. Generate appropriate view and projection matrices
        #. Set the GL context's viewport and scissorbox values
        #. Apply the relevant matrices to Arcade's
           :py:class:`~arcade.Window` object
        """

        self._window.current_camera = self

        _projection = generate_perspective_matrix(self._projection, self._view.zoom)
        _view = generate_view_matrix(self._view)

        self._window.ctx.viewport = self.viewport.viewport
        self._window.ctx.scissor = None if not self.scissor else self.scissor.viewport
        self._window.projection = _projection
        self._window.view = _view

    def project(self, world_coordinate: Point) -> Vec2:
        """Convert world coordinates to pixel screen coordinates.

        If a 2D :py:class:`Vec2` is provided instead of a 3D
        :py:class:`Vec3`, then one will be calculated to the best of the
        method's ability.

        Args:
            world_coordinate:
                A :py:class:`Vec2` or :py:class:`Vec3` as world
                coordinates.

        Returns:
            A 2D screen pixel coordinate.
        """
        x, y, *z = world_coordinate
        z = (
            (
                0.5
                * self.viewport.height
                / tan(radians(0.5 * self._projection.fov / self._view.zoom))
            )
            if not z
            else z[0]
        )

        _projection = generate_perspective_matrix(self._projection, self._view.zoom)
        _view = generate_view_matrix(self._view)

        pos = project_perspective(Vec3(x, y, z), self.viewport.viewport, _view, _projection)

        return pos

    # TODO: update args
    def unproject(self, screen_coordinate: Point) -> Vec3:
        """Convert a pixel coordinate into world space.

        This reverses the effects of :py:meth:`.project`.

        Args:
            screen_coordinate:
                A 2D position in pixels from the bottom left of the screen.
                This should ALWAYS be in the range of 0.0 - screen size.

        Returns: A 3D vector in world space.

        """
        x, y, *z = screen_coordinate
        z = (
            (
                0.5
                * self.viewport.height
                / tan(radians(0.5 * self._projection.fov / self._view.zoom))
            )
            if not z
            else z[0]
        )

        _projection = generate_perspective_matrix(self._projection, self._view.zoom)
        _view = generate_view_matrix(self._view)

        pos = unproject_perspective(Vec3(x, y, z), self.viewport.viewport, _view, _projection)
        return pos
