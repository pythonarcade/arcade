from typing import Optional, Tuple, Generator, TYPE_CHECKING
from contextlib import contextmanager
from typing_extensions import Self

from pyglet.math import Mat4, Vec4

from arcade.camera.data_types import Projector, CameraData, OrthographicProjectionData
from arcade.camera.projection_functions import generate_view_matrix, generate_orthographic_matrix

from arcade.window_commands import get_window
if TYPE_CHECKING:
    from arcade import Window


__all__ = [
    'OrthographicProjector'
]


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

    :param window: The window to bind the camera to. Defaults to the currently active camera.
    :param view: The CameraData PoD. contains the viewport, position, up, forward, and zoom.
    :param projection: The OrthographicProjectionData PoD.
                contains the left, right, bottom top, near, and far planes.
    """
    def __init__(self, *,
                 window: Optional["Window"] = None,
                 view: Optional[CameraData] = None,
                 projection: Optional[OrthographicProjectionData] = None):
        self._window: "Window" = window or get_window()

        self._view = view or CameraData(  # Viewport
            (self._window.width / 2, self._window.height / 2, 0),  # Position
            (0.0, 1.0, 0.0),  # Up
            (0.0, 0.0, -1.0),  # Forward
            1.0  # Zoom
        )

        self._projection = projection or OrthographicProjectionData(
            -0.5 * self._window.width, 0.5 * self._window.width,  # Left, Right
            -0.5 * self._window.height, 0.5 * self._window.height,  # Bottom, Top
            -100, 100,  # Near, Far

            (0, 0, self._window.width, self._window.height)  # Viewport
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

        self._window.ctx.viewport = self._projection.viewport
        self._window.projection = _projection
        self._window.view = _view

    @contextmanager
    def activate(self) -> Generator[Self, None, None]:
        """Set this camera as the current one, then undo it after.

        This method is a :ref+external:`context manager <context-managers>`
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

    def project(self, world_coordinate: Tuple[float, ...]) -> Tuple[float, float]:
        """
        Take a Vec2 or Vec3 of coordinates and return the related screen coordinate
        """
        if len(world_coordinate) > 2:
            z = world_coordinate[2]
        else:
            z = 0.0
        x, y = world_coordinate[0], world_coordinate[1]

        viewport = self._projection.viewport

        world_position = Vec4(x, y, z, 1.0)

        _projection = generate_orthographic_matrix(self._projection, self._view.zoom)
        _view = generate_view_matrix(self._view)

        projected_position = _projection @ _view @ world_position

        screen_coordinate_x = viewport[0] + (0.5 * projected_position.x + 0.5) * viewport[2]
        screen_coordinate_y = viewport[1] + (0.5 * projected_position.y + 0.5) * viewport[3]

        return screen_coordinate_x, screen_coordinate_y

    def unproject(self,
            screen_coordinate: Tuple[float, float],
            depth: Optional[float] = None) -> Tuple[float, float, float]:
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

        screen_x = 2.0 * (screen_coordinate[0] - self._projection.viewport[0]) / self._projection.viewport[2] - 1
        screen_y = 2.0 * (screen_coordinate[1] - self._projection.viewport[1]) / self._projection.viewport[3] - 1

        _projection = ~generate_orthographic_matrix(self._projection, self._view.zoom)
        _view = ~generate_view_matrix(self._view)

        _unprojected_position = _projection @ Vec4(screen_x, screen_y, 0.0, 1.0)
        _world_position = _view @ Vec4(_unprojected_position.x, _unprojected_position.y, depth or 0.0, 1.0)

        return _world_position.x, _world_position.y, _world_position.z

    def map_screen_to_world_coordinate(
            self,
            screen_coordinate: Tuple[float, float],
            depth: Optional[float] = None
    ) -> Tuple[float, float, float]:
        """
        Alias of OrthographicProjector.unproject() for typing.
        """
        return self.unproject(screen_coordinate, depth)

