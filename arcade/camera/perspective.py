from typing import Optional, Tuple, Generator, TYPE_CHECKING
from typing_extensions import Self
from contextlib import contextmanager

from math import tan, radians
from pyglet.math import Mat4, Vec3

from arcade.camera.data_types import Projector, CameraData, PerspectiveProjectionData
from arcade.camera.projection_functions import (
    generate_view_matrix,
    generate_perspective_matrix,
    project_perspective,
    unproject_perspective
)

from arcade.types import Point
from arcade.types.vector_like import Point2
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

    def __init__(self, *,
                 window: Optional["Window"] = None,
                 view: Optional[CameraData] = None,
                 projection: Optional[PerspectiveProjectionData] = None):
        self._window: "Window" = window or get_window()

        self._view = view or CameraData(  # Viewport
            (self._window.width / 2, self._window.height / 2, 0),  # Position
            (0.0, 1.0, 0.0),  # Up
            (0.0, 0.0, -1.0),  # Forward
            1.0  # Zoom
        )

        self._projection = projection or PerspectiveProjectionData(
            self._window.width / self._window.height,  # Aspect
            60,  # Field of View,
            0.01, 100.0,  # near, # far
            (0, 0, self._window.width, self._window.height)  # Viewport
        )

    @property
    def view(self) -> CameraData:
        """
        The CameraData. Is a read only property.
        """
        return self._view

    @property
    def projection(self) -> PerspectiveProjectionData:
        """
        The OrthographicProjectionData. Is a read only property.
        """
        return self._projection

    def generate_projection_matrix(self) -> Mat4:
        """
        alias of arcade.camera.get_perspective_matrix method
        """
        return generate_perspective_matrix(self._projection, self._view.zoom)

    def generate_view_matrix(self) -> Mat4:
        """
        alias of arcade.camera.get_view_matrix method
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
        """
        Sets the active camera to this object.
        Then generates the view and projection matrices.
        Finally, the gl context viewport is set, as well as the projection and view matrices.
        """

        self._window.current_camera = self

        _projection = generate_perspective_matrix(self._projection, self._view.zoom)
        _view = generate_view_matrix(self._view)

        self._window.ctx.viewport = self._projection.viewport
        self._window.projection = _projection
        self._window.view = _view

    def project(self, world_coordinate: Point) -> Vec2:
        """
        Take a Vec2 or Vec3 of coordinates and return the related screen coordinate
        """
        if len(world_coordinate) < 2:
            z = (0.5 * self._projection.viewport[3] / tan(
                radians(0.5 * self._projection.fov / self._view.zoom)))
        else:
            z = world_coordinate[2]
        x, y = world_coordinate[0], world_coordinate[1]

        _projection = generate_perspective_matrix(self._projection, self._view.zoom)
        _view = generate_view_matrix(self._view)

        pos = project_perspective(
            Vec3(x, y, z),
            self._projection.viewport,
            _view, _projection
        )

        return pos

    def unproject(self,
                  screen_coordinate: Point2,
                  depth: Optional[float] = None) -> Vec3:
        """
        Take in a pixel coordinate from within
        the range of the window size and returns
        the world space coordinates.

        Essentially reverses the effects of the projector.

        Args:
            screen_coordinate: A 2D position in pixels from the bottom left of the screen.
                               This should ALWAYS be in the range of 0.0 - screen size.
            depth: The depth of the query
        Returns:
            A 3D vector in world space.
        """
        depth = depth or (0.5 * self._projection.viewport[3] / tan(
            radians(0.5 * self._projection.fov / self._view.zoom)))

        _projection = generate_perspective_matrix(self._projection, self._view.zoom)
        _view = generate_view_matrix(self._view)

        pos = unproject_perspective(
            screen_coordinate, self.projection.viewport,
            _view, _projection,
            depth
        )
        return pos

    def map_screen_to_world_coordinate(
            self,
            screen_coordinate: Point2,
            depth: Optional[float] = None) -> Vec3:
        """
        Alias of PerspectiveProjector.unproject() for typing.
        """
        return self.unproject(screen_coordinate, depth)
