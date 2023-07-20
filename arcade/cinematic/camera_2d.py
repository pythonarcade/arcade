from typing import Optional, Tuple
from warnings import warn

from arcade.cinematic.data import CameraData, OrthographicProjectionData

from arcade.application import Window
from arcade.window_commands import get_window


class Camera2D:
    """
    A simple orthographic camera. Similar to SimpleCamera, but takes better advantage of the new data structures.
    As the Simple Camera is depreciated any new project should use this camera instead.
    """
    def __init__(self, *,
                 window: Optional[Window] = None,
                 viewport: Optional[Tuple[int, int, int, int]] = None,
                 position: Optional[Tuple[float, float]] = None,
                 up: Optional[Tuple[float, float]] = None,
                 zoom: Optional[float] = None,
                 projection: Optional[Tuple[float, float, float, float]] = None,
                 near: Optional[float] = None,
                 far: Optional[float] = None,
                 camera_data: Optional[CameraData] = None,
                 projection_data: Optional[OrthographicProjectionData] = None
                 ):
        self._window = window or get_window()

        if any((viewport, position, up, zoom)) and camera_data:
            warn("Camera2D Warning: Provided both a CameraData object and raw values. Defaulting to CameraData.")

        if any((projection, near, far)) and projection_data:
            warn("Camera2D Warning: Provided both an OrthographicProjectionData object and raw values."
                 "Defaulting to OrthographicProjectionData.")

        _pos = position or (self._window.width / 2, self._window.height / 2)
        _up = up or (0.0, 1.0)
        self._data = camera_data or CameraData(
            viewport or (0, 0, self._window.width, self._window.height),
            (_pos[0], _pos[1], 0.0),
            (_up[0], _up[1], 0.0),
            (0.0, 0.0, 1.0),
            zoom or 1.0
        )

        _proj = projection or (-self._window.width/2, self._window.width/2,
                               -self._window.height/2, self._window.height/2)
        self._projection = projection_data or OrthographicProjectionData(
            _proj[0], _proj[1],  # Left and Right.
            _proj[2], _proj[3],  # Bottom and Top.
            near or 0.0, far or 100.0  # Near and Far.
        )


