from typing import TYPE_CHECKING, Tuple, Optional, Union

from dataclasses import dataclass

from arcade.window_commands import get_window
from arcade.gl import Program, Geometry

from pyglet.math import Mat4

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
    :param zoom: A scaler which scales the size of the projection.
    Is equivalent to increasing the size of the projection.
    """

    viewport: Tuple[int, int, int, int]
    projection: Tuple[float, float, float, float]
    up: Tuple[float, float] = (0.0, 1.0)
    zoom: float = 1.0


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
            (0.0, self._window.width, 0.0, self._window.height)
        )

    @property
    def viewport_size(self):
        return self._data.viewport[3:]

    @property
    def viewport_width(self):
        return self._data.viewport[3]

    @property
    def viewport_height(self):
        return self._data.viewport[4]

