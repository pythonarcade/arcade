from typing import TYPE_CHECKING, Tuple, Optional, Union
from contextlib import contextmanager

from dataclasses import dataclass

from arcade.window_commands import get_window

from pyglet.math import Mat4, Vec3

if TYPE_CHECKING:
    from arcade.application import Window


@dataclass
class CameraData:
    """
    A PoD (Packet of Data) which holds the necessary data for a functional
    2D orthographic camera

    :param viewport: The pixel bounds which will be drawn onto. (left, bottom, width, height)
    :param projection: The co-ordinate bounds which will be mapped to the viewport bounds. (left, right, bottom, top)
    :param up: A 2D vector which describes which direction is up (+y)
    :param scale: A scaler which scales the size of the projection matrix from the center.
    Is equivalent to increasing the size of the projection.
    """

    viewport: Tuple[int, int, int, int]
    projection: Tuple[float, float, float, float]
    position: Tuple[float, float, float]
    up: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    scale: float = 1.0


class Camera2DOrthographic:
    """
    The simplest form of a 2D orthographic camera.
    Using a CameraData PoD (Packet of Data) it generates
    the correct projection and view matrices. It also
    provides methods and a context manager for using the
    matrices in glsl shaders.

    This class provides no methods for manipulating the CameraData.

    There are also two static class variables which control
    the near and far clipping planes of the projection matrix. For most uses
    this should be satisfactory.

    The current implementation will recreate the view and projection matrix every time
    the camera is used. If used every frame or multiple times per frame this may be
    inefficient. If you suspect that this may be causing issues profile before optimising.

    :param data: The CameraData PoD, will create a basic screen sized camera if no provided
    """
    near_plane: float = -100.0  # the near clipping plane of the camera
    far_plane: float = 100.0  # the far clipping plane of the camera

    def __init__(self, *, data: Optional[CameraData] = None, window: Optional[Window] = None):
        # A reference to the current active Arcade Window. Used to access the current gl context.
        self._window = window or get_window()

        # The camera data used to generate the view and projection matrix.
        self._data = data or CameraData(
            (0, 0, self._window.width, self._window.height),
            (0.0, self._window.width, 0.0, self._window.height),
            (self._window.width / 2, self._window.height / 2, 0.0)
        )

    @property
    def data(self) -> CameraData:
        """
        Returns the CameraData which is used to make the matrices
        """
        return self._data

    @property
    def viewport_size(self) -> Tuple[int, int]:
        """
        Returns the width and height of the viewport
        """
        return self._data.viewport[3:]

    @property
    def viewport_width(self) -> int:
        """
        Returns the width of the viewport
        """
        return self._data.viewport[3]

    @property
    def viewport_height(self) -> int:
        """
        Returns the height of the viewport
        """
        return self._data.viewport[4]

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """
        Returns the Viewport.
        """
        return self._data.viewport

    @property
    def projection(self) -> Tuple[float, float, float, float]:
        """
        Returns the projection values used to generate the projection matrix
        """
        return self._data.projection

    @property
    def position(self) -> Tuple[float, float]:
        """
        returns the 2D position of the camera
        """
        return self._data.position[:2]

    @property
    def up(self) -> Tuple[float, float]:
        """
        returns the 2d up direction of the camera
        """
        return self._data.up[:2]

    @property
    def scale(self) -> float:
        """
        returns the zoom value of the camera
        """
        return self._data.scale

    def _generate_view_matrix(self) -> Mat4:
        """
        Generates a view matrix which always has the z axis at 0, and looks towards the positive z axis.
        Ignores the z component of the position, and up vectors.

        To protect against unexpected behaviour ensure that the up vector is unit length without the z axis as
        it is not normalised before use.
        """
        return Mat4.look_at(Vec3(*self.position[:2], 0.0),
                            Vec3(*self.position[:2], 1.0),
                            Vec3(*self.up[:2], 0.0))

    def _generate_projection_matrix(self) -> Mat4:
        """
        Generates the projection matrix. This uses the values provided by the CameraData.projection tuple.
        It is then scaled by the Camera.scale float. It is scaled from the center of the projection values not 0,0.

        Generally keep the scale value to integers or negative powers of 2 (0.5, 0.25, etc.) to keep
        the pixels uniform in size. Avoid a scale of 0.0.
        """

        # Find the center of the projection values (often 0,0 or the center of the screen)
        _projection_center = (
            (self._data.projection[0] + self._data.projection[1]) / 2,
            (self._data.projection[2] + self._data.projection[3]) / 2
        )

        # Find half the width of the projection
        _projection_half_size = (
            (self._data.projection[1] - self._data.projection[0]) / 2,
            (self._data.projection[3] - self._data.projection[2]) / 2
        )

        # Scale the projection by the scale value. Both the width and the height
        # share a scale value to avoid ugly stretching.
        _true_projection = (
            _projection_center[0] - _projection_half_size[0] * self._data.scale,
            _projection_center[0] + _projection_half_size[0] * self._data.scale,
            _projection_center[1] - _projection_half_size[1] * self._data.scale,
            _projection_center[1] + _projection_half_size[1] * self._data.scale
        )
        return Mat4.orthogonal_projection(*_true_projection, self.near_plane, self.far_plane)

    def use(self):
        """
        Sets the active camera to this object.
        Then generates the view and projection matrices.
        Finally, the gl context viewport is set, as well as the projection and view matrices.
        """

        self._window.current_camera = self

        _projection = self._generate_projection_matrix()
        _view = self._generate_view_matrix()

        self._window.ctx.viewport = self._data.viewport
        self._window.projection = _projection
        self._window.view = _view

    @contextmanager
    def activate(self):
        """
        A context manager version of Camera2DOrthographic.use() which allows for the use of
        `with` blocks. For example, `with camera.activate() as cam: ...`.
        """
        previous_camera = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous_camera.use()


class Camera2DController:
    """

    """
    def __init__(self, *, data: Optional[CameraData] = None, window: Optional[Window] = None):
        # A reference to the current active Arcade Window. Used to access the current gl context.
        self._window = window or get_window()

        # The camera data used to generate the view and projection matrix.
        self._data = data or CameraData(
            (0, 0, self._window.width, self._window.height),
            (0.0, self._window.width, 0.0, self._window.height),
            (self._window.width / 2, self._window.height / 2, 0.0)
        )


class SimpleCamera:
    """

    """

    def __init__(self, *, data: Optional[CameraData] = None, window: Optional[Window] = None,
                 viewport: Optional[Tuple[int, int, int, int]] = None,
                 projection: Optional[Tuple[float, float, float, float]] = None,
                 position: Optional[Tuple[float, float, float]] = None,
                 up: Optional[Tuple[float, float, float]] = None, scale: Optional[float] = None):
        # A reference to the current active Arcade Window. Used to access the current gl context.
        self._window: Window = window or get_window()

        # For backwards compatibility both the new camera data,
        # and the old raw tuples are available for initialisation.
        # If both are supplied the camera cannot decide which values to use and will raise a ValueError
        if any((viewport, projection, up, scale)) and data:
            raise ValueError(f"Both the CameraData {data},"
                             f" and the values {viewport, projection, position, up, scale} have been supplied."
                             f"Ensure only one of the two is provided.")

        # The camera data used to generate the view and projection matrix.
        if any((viewport, projection, up, scale)):
            self._data = CameraData(viewport, projection, position, up, scale)
        else:
            self._data = data or CameraData(
                (0, 0, self._window.width, self._window.height),
                (0.0, self._window.width, 0.0, self._window.height),
                (self._window.width / 2, self._window.height / 2, 0.0)
            )
