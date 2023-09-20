from typing import TYPE_CHECKING, Optional, Tuple, Iterator
from contextlib import contextmanager
from math import atan2, cos, sin, degrees, radians

from pyglet.math import Vec3

from arcade.camera.data import CameraData, OrthographicProjectionData
from arcade.camera.types import Projector
from arcade.camera.orthographic import OrthographicProjector

from arcade.window_commands import get_window
if TYPE_CHECKING:
    from arcade import Window


__all__ = [
    'SimpleCamera'
]


class SimpleCamera:
    """
    A simple camera which uses an orthographic camera and a simple 2D Camera Controller.
    It also implements an update method that allows for an interpolation between two points

    Written to be backwards compatible with the old SimpleCamera.
    """
    # TODO: ADD PARAMS TO DOC FOR __init__

    def __init__(self, *,
                 window: Optional["Window"] = None,
                 viewport: Optional[Tuple[int, int, int, int]] = None,
                 projection: Optional[Tuple[float, float, float, float]] = None,
                 position: Optional[Tuple[float, float]] = None,
                 up: Optional[Tuple[float, float]] = None,
                 zoom: Optional[float] = None,
                 near: Optional[float] = None,
                 far: Optional[float] = None,
                 camera_data: Optional[CameraData] = None,
                 projection_data: Optional[OrthographicProjectionData] = None
                 ):
        self._window = window or get_window()

        if any((viewport, projection, position, up, zoom, near, far)) and any((camera_data, projection_data)):
            raise ValueError("Provided both data structures and raw values."
                             "Only supply one or the other")

        if any((viewport, projection, position, up, zoom, near, far)):
            _pos = position or (0.0, 0.0)
            _up = up or (0.0, 1.0)
            self._view = CameraData(
                viewport or (0, 0, self._window.width, self._window.height),
                (_pos[0], _pos[1], 0.0),
                (_up[0], _up[1], 0.0),
                (0.0, 0.0, -1.0),
                zoom or 1.0
            )
            _projection = projection or (
                0.0, self._window.width,
                0.0, self._window.height
            )
            self._projection = OrthographicProjectionData(
                _projection[0] or 0.0, _projection[1] or self._window.hwidth,  # Left, Right
                _projection[2] or 0.0, _projection[3] or self._window.height,  # Bottom, Top
                near or -100, far or 100  # Near, Far
            )
        else:
            self._view = camera_data or CameraData(
                (0, 0, self._window.width, self._window.height),  # Viewport
                (self._window.width / 2, self._window.height / 2, 0.0),  # Position
                (0, 1.0, 0.0),  # Up
                (0.0, 0.0, -1.0),  # Forward
                1.0  # Zoom
            )
            self._projection = projection_data or OrthographicProjectionData(
                0.0, self._window.width,  # Left, Right
                0.0, self._window.height,  # Bottom, Top
                -100, 100  # Near, Far
            )

        self._camera = OrthographicProjector(
            window=self._window,
            view=self._view,
            projection=self._projection
        )

        self._easing_speed: float = 0.0
        self._position_goal: Tuple[float, float] = self.position

    # Basic properties for modifying the viewport and orthographic projection

    @property
    def viewport_width(self) -> int:
        """ Returns the width of the viewport """
        return self._view.viewport[2]

    @property
    def viewport_height(self) -> int:
        """ Returns the height of the viewport """
        return self._view.viewport[3]

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """ The pixel area that will be drawn to while this camera is active (left, bottom, width, height) """
        return self._view.viewport

    @viewport.setter
    def viewport(self, viewport: Tuple[int, int, int, int]) -> None:
        """ Set the viewport (left, bottom, width, height) """
        self.set_viewport(viewport)

    def set_viewport(self, viewport: Tuple[int, int, int, int]) -> None:
        self._view.viewport = viewport

    @property
    def projection(self) -> Tuple[float, float, float, float]:
        """
        The dimensions that will be projected to the viewport. (left, right, bottom, top).
        """
        return self._projection.left, self._projection.right, self._projection.bottom, self._projection.top

    @projection.setter
    def projection(self, projection: Tuple[float, float, float, float]) -> None:
        """
        Update the orthographic projection of the camera. (left, right, bottom, top).
        """
        self._projection.left = projection[0]
        self._projection.right = projection[1]
        self._projection.bottom = projection[2]
        self._projection.top = projection[3]

    # Methods for retrieving the viewport - projection ratios. Originally written by Alejandro Casanovas.
    @property
    def viewport_to_projection_width_ratio(self) -> float:
        """
        The ratio of viewport width to projection width.
        A value of 1.0 represents that an object that moves one unit will move one pixel.
        A value less than one means that one pixel is equivalent to more than one unit (Zoom out).
        """
        return (self.viewport_width * self.zoom) / (self._projection.left - self._projection.right)

    @property
    def viewport_to_projection_height_ratio(self) -> float:
        """
        The ratio of viewport height to projection height.
        A value of 1.0 represents that an object that moves one unit will move one pixel.
        A value less than one means that one pixel is equivalent to more than one unit (Zoom out).
        """
        return (self.viewport_height * self.zoom) / (self._projection.bottom - self._projection.top)

    @property
    def projection_to_viewport_width_ratio(self) -> float:
        """
        The ratio of projection width to viewport width.
        A value of 1.0 represents that an object that moves one unit will move one pixel.
        A value less than one means that one pixel is equivalent to less than one unit (Zoom in).
        """
        return (self._projection.left - self._projection.right) / (self.zoom * self.viewport_width)

    @property
    def projection_to_viewport_height_ratio(self) -> float:
        """
        The ratio of projection height to viewport height.
        A value of 1.0 represents that an object that moves one unit will move one pixel.
        A value less than one means that one pixel is equivalent to less than one unit (Zoom in).
        """
        return (self._projection.bottom - self._projection.top) / (self.zoom * self.viewport_height)

    # Control methods (movement, zooming, rotation)
    @property
    def position(self) -> Tuple[float, float]:
        """
        The position of the camera based on the bottom left coordinate.
        """
        return self._view.position[0], self._view.position[1]

    @position.setter
    def position(self, pos: Tuple[float, float]) -> None:
        """
        Set the position of the camera based on the bottom left coordinate.
        """
        self._view.position = (pos[0], pos[1], self._view.position[2])

    @property
    def zoom(self) -> float:
        """
        A scaler which adjusts the size of the orthographic projection.
        A higher zoom value means larger pixels.
        For best results keep the zoom value an integer to an integer or an integer to the power of -1.
        """
        return self._view.zoom

    @zoom.setter
    def zoom(self, zoom: float) -> None:
        """
        A scaler which adjusts the size of the orthographic projection.
        A higher zoom value means larger pixels.
        For best results keep the zoom value an integer to an integer or an integer to the power of -1.
        """
        self._view.zoom = zoom

    @property
    def up(self) -> Tuple[float, float]:
        """
        A 2D normalised vector which defines which direction corresponds to the +Y axis.
        """
        return self._view.up[0], self._view.up[1]

    @up.setter
    def up(self, up: Tuple[float, float]) -> None:
        """
        A 2D normalised vector which defines which direction corresponds to the +Y axis.
        generally easier to use the `rotate` and `rotate_to` methods as they use an angle value.
        """
        _up = Vec3(up[0], up[1], 0.0).normalize()
        self._view.up = (_up[0], _up[1], _up[2])

    @property
    def angle(self) -> float:
        """
        An alternative way of setting the up vector of the camera.
        The angle value goes clock-wise starting from (0.0, 1.0).
        """
        return degrees(atan2(self.up[0], self.up[1]))

    @angle.setter
    def angle(self, angle: float) -> None:
        """
        An alternative way of setting the up vector of the camera.
        The angle value goes clock-wise starting from (0.0, 1.0).
        """
        rad = radians(angle)
        self.up = (
            sin(rad),
            cos(rad)
        )

    def move_to(self, vector: Tuple[float, float], speed: float = 1.0) -> None:
        """
        Sets the goal position of the camera.

        The camera will lerp towards this position based on the provided speed,
        updating its position every time the use() function is called.

        :param Vec2 vector: Vector to move the camera towards.
        :param Vec2 speed: How fast to move the camera, 1.0 is instant, 0.1 moves slowly
        """
        self._position_goal = vector
        self._easing_speed = speed

    def move(self, vector: Tuple[float, float]) -> None:
        """
        Moves the camera with a speed of 1.0, aka instant move

        This is equivalent to calling move_to(my_pos, 1.0)
        """
        self.move_to(vector, 1.0)

    def center(self, vector: Tuple[float, float], speed: float = 1.0) -> None:
        """
        Centers the camera. Allows for a linear lerp like the move_to() method.
        """
        viewport_center = self.viewport_width / 2, self.viewport_height / 2

        adjusted_vector = (
            vector[0] * self.viewport_to_projection_width_ratio,
            vector[1] * self.viewport_to_projection_height_ratio
        )

        target = (
            adjusted_vector[0] - viewport_center[0],
            adjusted_vector[1] - viewport_center[1]
        )

        self.move_to(target, speed)

    # General Methods

    def update(self):
        """
        Update the camera's position.
        """
        if self._easing_speed > 0.0:
            x_a = self.position[0]
            x_b = self._position_goal[0]

            y_a = self.position[1]
            y_b = self._position_goal[1]

            self.position = (
                x_a + (x_b - x_a) * self._easing_speed,  # Linear Lerp X position
                y_a + (y_b - y_a) * self._easing_speed  # Linear Lerp Y position
            )
            if self.position == self._position_goal:
                self._easing_speed = 0.0

    def use(self):
        """
        Sets the active camera to this object.
        Then generates the view and projection matrices.
        Finally, the gl context viewport is set, as well as the projection and view matrices.
        This method also calls the update method. This can cause the camera to move faster than expected
        if the camera is used multiple times in a single frame.
        """

        # Updated the position
        self.update()

        # set matrices
        self._camera.use()

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

        return self._camera.map_coordinate(screen_coordinate)

    def resize(self, viewport_width: int, viewport_height: int, *,
               resize_projection: bool = True) -> None:
        """
        Resize the camera's viewport. Call this when the window resizes.

        :param int viewport_width: Width of the viewport
        :param int viewport_height: Height of the viewport
        :param bool resize_projection: if True the projection will also be resized
        """
        new_viewport = (self.viewport[0], self.viewport[1], viewport_width, viewport_height)
        self.set_viewport(new_viewport)
        if resize_projection:
            self.projection = (self._projection.left, viewport_width,
                               self._projection.bottom, viewport_height)
