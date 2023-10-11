from typing import Optional, Tuple, Iterator, TYPE_CHECKING
from contextlib import contextmanager

from pyglet.math import Mat4, Vec3, Vec4

from arcade.camera.data import CameraData, PerspectiveProjectionData
from arcade.camera.types import Projector

from arcade.window_commands import get_window
if TYPE_CHECKING:
    from arcade import Window


__all__ = [
    'PerspectiveProjector'
]


class PerspectiveProjector:
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
    be inefficient.
    """

    def __init__(self, *,
                 window: Optional["Window"] = None,
                 view: Optional[CameraData] = None,
                 projection: Optional[PerspectiveProjectionData] = None):
        """
        Initialise a Projector which produces a perspective projection matrix using
        a CameraData and PerspectiveProjectionData PoDs.

        Args:
            window: The window to bind the camera to. Defaults to the currently active camera.
            view: The CameraData PoD. contains the viewport, position, up, forward, and zoom.
            projection: The PerspectiveProjectionData PoD.
                        contains the aspect ratio, fov, near plane, and far plane.
        """
        self._window: "Window" = window or get_window()

        self._view = view or CameraData(
            (self._window.width / 2, self._window.height / 2, 0),  # Position
            (0.0, 1.0, 0.0),  # Up
            (0.0, 0.0, -1.0),  # Forward
            1.0  # Zoom
        )

        self._projection = projection or PerspectiveProjectionData(
            self._window.width / self._window.height,  # Aspect ratio
            90,  # Field of view (degrees)
            0.1, 1000,  # Near, Far
            (0, 0, self._window.width, self._window.height),  # Viewport
        )

    @property
    def view(self) -> CameraData:
        """
        Is a CameraData. Is a read only property
        """
        return self._view

    @property
    def projection(self) -> PerspectiveProjectionData:
        """
        Is the PerspectiveProjectionData. is a read only property.
        """
        return self._projection

    def _generate_projection_matrix(self) -> Mat4:
        """
        Using the PerspectiveProjectionData a projection matrix is generated where the size of the
        objects is affected by depth.

        The zoom value shrinks the effective fov of the camera. For example a zoom of two will have the
        fov resulting in 2x zoom effect.
        """

        _true_fov = self._projection.fov / self._view.zoom
        return Mat4.perspective_projection(
            self._projection.aspect,
            self._projection.near,
            self._projection.far,
            _true_fov
        )

    def _generate_view_matrix(self) -> Mat4:
        """
        Using the ViewData it generates a view matrix from the pyglet Mat4 look at function
        """
        fo = Vec3(*self._view.forward).normalize()  # Forward Vector
        up = Vec3(*self._view.up).normalize()  # Initial Up Vector (Not perfectly aligned to forward vector)
        ri = fo.cross(up)  # Right Vector
        up = ri.cross(fo)  # Up Vector
        po = Vec3(*self._view.position)
        return Mat4((
            ri.x,  up.x,  -fo.x,  0,
            ri.y,  up.y,  -fo.y,  0,
            ri.z,  up.z,  -fo.z,  0,
            -ri.dot(po), -up.dot(po), fo.dot(po), 1
        ))

    def use(self):
        """
        Sets the active camera to this object.
        Then generates the view and projection matrices.
        Finally, the gl context viewport is set, as well as the projection and view matrices.
        """

        self._window.current_camera = self

        _projection = self._generate_projection_matrix()
        _view = self._generate_view_matrix()

        self._window.ctx.viewport = self._projection.viewport
        self._window.projection = _projection
        self._window.view = _view

    @contextmanager
    def activate(self) -> Iterator[Projector]:
        """
        A context manager version of PerspectiveProjector.use() which allows for the use of
        `with` blocks. For example, `with camera.activate() as cam: ...`..
        """
        previous_projector = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous_projector.use()

    def map_coordinate(self, screen_coordinate: Tuple[float, float]) -> Tuple[float, float, float]:
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
        screen_x = 2.0 * (screen_coordinate[0] - self._projection.viewport[0]) / self._projection.viewport[2] - 1
        screen_y = 2.0 * (screen_coordinate[1] - self._projection.viewport[1]) / self._projection.viewport[3] - 1

        _view = self._generate_view_matrix()
        _projection = self._generate_projection_matrix()

        screen_position = Vec4(screen_x, screen_y, -1.0, 1.0)

        _full = ~(_projection @ _view)

        _mapped_position = _full @ screen_position

        return _mapped_position[0], _mapped_position[1], _mapped_position[2]

    def map_coordinate_at_depth(self,
                                screen_coordinate: Tuple[float, float],
                                depth: float) -> Tuple[float, float, float]:
        """
        Take in a pixel coordinate from within
        the range of the window size and returns
        the world space coordinates.

        Essentially reverses the effects of the projector.

        Args:
            screen_coordinate: A 2D position in pixels from the bottom left of the screen.
                               This should ALWAYS be in the range of 0.0 - screen size.
            depth: the depth that the mouse should be compared against.
                   Should range from near to far planes of projection.
        Returns:
            A 3D vector in world space.
        """
        screen_x = 2.0 * (screen_coordinate[0] - self._projection.viewport[0]) / self._projection.viewport[2] - 1
        screen_y = 2.0 * (screen_coordinate[1] - self._projection.viewport[1]) / self._projection.viewport[3] - 1

        _view = self._generate_view_matrix()
        _projection = self._generate_projection_matrix()

        _depth = 2.0 * depth / (self._projection.far - self._projection.near) - 1

        screen_position = Vec4(screen_x, screen_y, _depth, 1.0)

        _full = ~(_projection @ _view)

        _mapped_position = _full @ screen_position

        return _mapped_position[0], _mapped_position[1], _mapped_position[2]
