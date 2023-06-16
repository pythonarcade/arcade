from typing import TYPE_CHECKING, Tuple, Optional, Protocol, Union
from contextlib import contextmanager

from dataclasses import dataclass

from arcade.window_commands import get_window

from pyglet.math import Mat4, Vec3, Vec4, Vec2

if TYPE_CHECKING:
    from arcade.application import Window

from arcade import Window

FourIntTuple = Tuple[int, int, int, int]
FourFloatTuple = Union[Tuple[float, float, float, float], Vec4]
ThreeFloatTuple = Union[Tuple[float, float, float], Vec3]
TwoFloatTuple = Union[Tuple[float, float], Vec2]


@dataclass
class ViewData:
    """
    A PoD (Packet of Data) which holds the necessary data for a functional camera excluding the projection data

    :param viewport: The pixel bounds which will be drawn onto. (left, bottom, width, height)

    :param position: A 3D vector which describes where the camera is located.
    :param up: A 3D vector which describes which direction is up (+y).
    :param forward: a 3D vector which describes which direction is forwards (+z).
    :param zoom: A scaler that records the zoom of the camera. While this most often affects the projection matrix
                 it allows camera controllers access to the zoom functionality
                 without interacting with the projection data.
    """
    # Viewport data
    viewport: FourIntTuple

    # View matrix data
    position: ThreeFloatTuple
    up: ThreeFloatTuple
    forward: ThreeFloatTuple

    # Zoom
    zoom: float


@dataclass
class OrthographicProjectionData:
    """
    A PoD (Packet of Data) which holds the necessary data for a functional Orthographic Projection matrix.

    This is by default a Left-handed system. with the X axis going from left to right, The Y axis going from
    bottom to top, and the Z axis going from towards the screen to away from the screen. This can be made
    right-handed by making the near value greater than the far value.

    :param left: The left most value, which gets mapped to x = -1.0 (anything below this value is not visible).
    :param right: The right most value, which gets mapped to x = 1.0 (anything above this value is not visible).
    :param bottom: The bottom most value, which gets mapped to y = -1.0 (anything below this value is not visible).
    :param top: The top most value, which gets mapped to y = 1.0 (anything above this value is not visible).
    :param near: The 'closest' value, which gets mapped to z = -1.0 (anything below this value is not visible).
    :param far: The 'furthest' value, Which gets mapped to z = 1.0 (anything above this value is not visible).
    """
    left: float
    right: float
    bottom: float
    top: float
    near: float
    far: float


@dataclass
class PerspectiveProjectionData:
    """
    A PoD (Packet of Data) which holds the necessary data for a functional Perspective matrix.

    :param aspect: The aspect ratio of the screen (width over height).
    :param fov: The field of view in degrees. With the aspect ratio defines
                the size of the projection at any given depth.
    :param near: The 'closest' value, which gets mapped to z = -1.0 (anything below this value is not visible).
    :param far: The 'furthest' value, Which gets mapped to z = 1.0 (anything above this value is not visible).
    """
    aspect: float
    fov: float
    near: float
    far: float


class Projection(Protocol):
    near: float
    far: float


class Projector(Protocol):

    def use(self) -> None:
        ...

    @contextmanager
    def activate(self) -> "Projector":
        ...

    def get_map_coordinates(self, screen_coordinate: TwoFloatTuple) -> TwoFloatTuple:
        ...


class Camera(Protocol):
    _view: ViewData
    _projection: Projection


class OrthographicCamera:
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

    def __init__(self, *,
                 window: Optional["Window"] = None,
                 view: Optional[ViewData] = None,
                 projection: Optional[OrthographicProjectionData] = None):
        self._window: "Window" = window or get_window()

        self._view = view or ViewData(
            (0, 0, self._window.width, self._window.height),  # Viewport
            Vec3(self._window.width / 2, self._window.height / 2, 0),  # Position
            Vec3(0.0, 1.0, 0.0),  # Up
            Vec3(0.0, 0.0, 1.0),  # Forward
            1.0  # Zoom
        )

        self._projection = projection or OrthographicProjectionData(
            -0.5 * self._window.width, 0.5 * self._window.width,  # Left, Right
            -0.5 * self._window.height, 0.5 * self._window.height,  # Bottom, Top
            -100, 100,  # Near, Far
        )

    @property
    def view(self):
        return self._view

    @property
    def projection(self):
        return self._projection

    @property
    def viewport(self):
        return self._view.viewport

    @property
    def position(self):
        return self._view.position

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
    def activate(self) -> Projector:
        """
        A context manager version of Camera2DOrthographic.use() which allows for the use of
        `with` blocks. For example, `with camera.activate() as cam: ...`.

        :WARNING:
            Currently there is no 'default' camera within arcade. This means this method will raise a value error
            as self._window.current_camera is None initially. To solve this issue you only need to make a default
            camera and call the use() method.
        """
        previous_projector = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous_projector.use()

    def get_map_coordinates(self, screen_coordinate: TwoFloatTuple) -> TwoFloatTuple:
        """
        Maps a screen position to a pixel position.
        """

        screen_x = 2.0 * (screen_coordinate[0] - self._view.viewport[0]) / self._view.viewport[2] - 1
        screen_y = 2.0 * (screen_coordinate[1] - self._view.viewport[1]) / self._view.viewport[3] - 1

        _view = self._generate_view_matrix()
        _projection = self._generate_projection_matrix()

        screen_position = Vec4(screen_x, screen_y, 0.0, 1.0)

        _full = ~(_projection @ _view)

        return _full @ screen_position


class PerspectiveCamera:
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
                 view: Optional[ViewData] = None,
                 projection: Optional[PerspectiveProjectionData] = None):
        self._window: "Window" = window or get_window()

        self._view = view or ViewData(
            (0, 0, self._window.width, self._window.height),  # Viewport
            (self._window.width / 2, self._window.height / 2, 0),  # Position
            (0.0, 1.0, 0.0),  # Up
            (0.0, 0.0, 1.0),  # Forward
            1.0  # Zoom
        )

        self._projection = projection or PerspectiveProjectionData(
            self._window.width / self._window.height,  # Aspect ratio
            90,  # Field of view (degrees)
            0.1, 100  # Near, Far
        )

    @property
    def viewport(self):
        return self._view.viewport

    @property
    def position(self):
        return self._view.position

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
    def activate(self) -> Projector:
        """
        A context manager version of Camera2DOrthographic.use() which allows for the use of
        `with` blocks. For example, `with camera.activate() as cam: ...`.

        :WARNING:
            Currently there is no 'default' camera within arcade. This means this method will raise a value error
            as self._window.current_camera is None initially. To solve this issue you only need to make a default
            camera and call the use() method.
        """
        previous_projector = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous_projector.use()

    def get_map_coordinates(self, screen_coordinate: TwoFloatTuple) -> TwoFloatTuple:
        """
        Maps a screen position to a pixel position at the near clipping plane of the camera.
        """
        ...

    def get_map_coordinates_at_depth(self,
                                     screen_coordinate: TwoFloatTuple,
                                     depth: float) -> TwoFloatTuple:
        """
        Maps a screen position to a pixel position at the specific depth supplied.
        """
        ...


class SimpleCamera:
    """
    A simple camera which uses an orthographic camera and a simple 2D Camera Controller.
    It also implements an update method that allows for an interpolation between two points

    Written to be backwards compatible with the old SimpleCamera.
    """

    def __init__(self, *,
                 window: Optional["Window"] = None,
                 viewport: Optional[FourIntTuple] = None,
                 projection: Optional[FourFloatTuple] = None,
                 position: Optional[TwoFloatTuple] = None,
                 up: Optional[TwoFloatTuple] = None,
                 zoom: Optional[float] = None,
                 near: Optional[float] = None,
                 far: Optional[float] = None,
                 view_data: Optional[ViewData] = None,
                 projection_data: Optional[OrthographicProjectionData] = None
                 ):
        self._window = window or get_window()

        if any((viewport, projection, position, up, zoom, near, far)) and any((view_data, projection_data)):
            raise ValueError("Provided both view data or projection data, and raw values."
                             "You only need to supply one or the other")

        if any((viewport, projection, position, up, zoom, near, far)):
            self._view = ViewData(
                viewport or (0, 0, self._window.width, self._window.height),
                position or (self._window.width / 2, self._window.height / 2, 0.0),
                up or (0, 1.0, 0.0),
                (0.0, 0.0, 1.0),
                zoom or 1.0
            )
            _projection = OrthographicProjectionData(
                projection[0] or 0.0, projection[1] or self._window.height,  # Left, Right
                projection[2] or 0.0, projection[3] or self._window.height,  # Bottom, Top
                near or -100, far or 100  # Near, Far
            )
        else:
            self._view = view_data or ViewData(
                (0, 0, self._window.width, self._window.height),  # Viewport
                (self._window.width / 2, self._window.height / 2, 0.0),  # Position
                (0, 1.0, 0.0),  # Up
                (0.0, 0.0, 1.0),  # Forward
                1.0  # Zoom
            )
            _projection = projection_data or OrthographicProjectionData(
                0.0, self._window.width,  # Left, Right
                0.0, self._window.height,  # Bottom, Top
                -100, 100  # Near, Far
            )

        self._camera = OrthographicCamera(
            window=self._window,
            view=self._view,
            projection=_projection
        )

    def use(self):
        """
        Sets the active camera to this object.
        Then generates the view and projection matrices.
        Finally, the gl context viewport is set, as well as the projection and view matrices.
        """

        ...

    @contextmanager
    def activate(self) -> Projector:
        """
        A context manager version of Camera2DOrthographic.use() which allows for the use of
        `with` blocks. For example, `with camera.activate() as cam: ...`.

        :WARNING:
            Currently there is no 'default' camera within arcade. This means this method will raise a value error
            as self._window.current_camera is None initially. To solve this issue you only need to make a default
            camera and call the use() method.
        """
        previous_projector = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous_projector.use()

    def get_map_coordinates(self, screen_coordinate: Tuple[float, float]) -> Tuple[float, float]:
        """
        Maps a screen position to a pixel position.
        """

        ...
