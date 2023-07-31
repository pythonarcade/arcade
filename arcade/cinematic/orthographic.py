from typing import Optional, Tuple, Iterator, TYPE_CHECKING
from contextlib import contextmanager

from pyglet.math import Mat4, Vec3, Vec4

from arcade.cinematic.data import CameraData, OrthographicProjectionData
from arcade.cinematic.types import Projector

from arcade.window_commands import get_window
if TYPE_CHECKING:
    from arcade import Window


__all__ = [
    'OrthographicProjector'
]


class OrthographicProjector:
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
    profile before optimising with a dirty value check.
    """
    # TODO: ADD PARAMS TO DOC FOR __init__

    def __init__(self, *,
                 window: Optional["Window"] = None,
                 view: Optional[CameraData] = None,
                 projection: Optional[OrthographicProjectionData] = None):
        self._window: "Window" = window or get_window()

        self._view = view or CameraData(
            (0, 0, self._window.width, self._window.height),  # Viewport
            (self._window.width / 2, self._window.height / 2, 0),  # Position
            (0.0, 1.0, 0.0),  # Up
            (0.0, 0.0, 1.0),  # Forward
            1.0  # Zoom
        )

        self._projection = projection or OrthographicProjectionData(
            -0.5 * self._window.width, 0.5 * self._window.width,  # Left, Right
            -0.5 * self._window.height, 0.5 * self._window.height,  # Bottom, Top
            -100, 100,  # Near, Far
        )

    @property
    def view_data(self) -> CameraData:
        return self._view

    @property
    def projection_data(self) -> OrthographicProjectionData:
        return self._projection

    def _generate_projection_matrix(self) -> Mat4:
        """
        Using the OrthographicProjectionData a projection matrix is generated where the size of the
        objects is not affected by depth.

        Generally keep the scale value to integers or negative powers of integers (2^-1, 3^-1, 2^-2, etc.) to keep
        the pixels uniform in size. Avoid a scale of 0.0.
        """

        # Find the center of the projection values (often 0,0 or the center of the screen)
        _projection_center = (
            (self._projection.left + self._projection.right) / 2,
            (self._projection.bottom + self._projection.top) / 2
        )

        # Find half the width of the projection
        _projection_half_size = (
            (self._projection.right - self._projection.left) / 2,
            (self._projection.top - self._projection.bottom) / 2
        )

        # Scale the projection by the zoom value. Both the width and the height
        # share a zoom value to avoid ugly stretching.
        _true_projection = (
            _projection_center[0] - _projection_half_size[0] / self._view.zoom,
            _projection_center[0] + _projection_half_size[0] / self._view.zoom,
            _projection_center[1] - _projection_half_size[1] / self._view.zoom,
            _projection_center[1] + _projection_half_size[1] / self._view.zoom
        )
        return Mat4.orthogonal_projection(*_true_projection, self._projection.near, self._projection.far)

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
            ri.x,  up.x,  fo.x,  0,
            ri.y,  up.y,  fo.y,  0,
            ri.z,  up.z,  fo.z,  0,
            -ri.dot(po), -up.dot(po), -fo.dot(po), 1
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

        self._window.ctx.viewport = self._view.viewport
        self._window.projection = _projection
        self._window.view = _view

    @contextmanager
    def activate(self) -> Iterator[Projector]:
        """
        A context manager version of Camera2DOrthographic.use() which allows for the use of
        `with` blocks. For example, `with camera.activate() as cam: ...`.
        """
        previous_projector = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous_projector.use()

    def map_coordinate(self, screen_coordinate: Tuple[float, float]) -> Tuple[float, float]:
        """
        Maps a screen position to a pixel position.
        """
        # TODO: better doc string

        screen_x = 2.0 * (screen_coordinate[0] - self._view.viewport[0]) / self._view.viewport[2] - 1
        screen_y = 2.0 * (screen_coordinate[1] - self._view.viewport[1]) / self._view.viewport[3] - 1

        _view = self._generate_view_matrix()
        _projection = self._generate_projection_matrix()

        screen_position = Vec4(screen_x, screen_y, 0.0, 1.0)

        _full = ~(_projection @ _view)

        _mapped_position = _full @ screen_position

        return _mapped_position[0], _mapped_position[1]
