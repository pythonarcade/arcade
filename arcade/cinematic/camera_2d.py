from typing import Optional, Tuple, Iterator
from math import degrees, radians, atan2, cos, sin
from contextlib import contextmanager

from arcade.cinematic.data import CameraData, OrthographicProjectionData
from arcade.cinematic.orthographic import OrthographicProjector
from arcade.cinematic.types import Projector


from arcade.application import Window
from arcade.window_commands import get_window

__all__ = [
    'Camera2D'
]


class Camera2D:
    """
    A simple orthographic camera. Similar to SimpleCamera, but takes better advantage of the new data structures.
    As the Simple Camera is depreciated any new project should use this camera instead.

    It provides properties to access every important variable for controlling the camera.
    3D properties such as pos, and up are constrained to a 2D plane. There is no access to the
    forward vector (as a property).

    The method fully fulfils both the Camera and Projector protocols.

    There are also ease of use methods for matching the viewport and projector to the window size.

    Provides 4 sets of left, right, bottom, top:
        - Positional in world space.
        - Projection without zoom scaling.
        - Projection with zoom scaling.
        - Viewport.

    NOTE Once initialised, the CameraData and OrthographicProjectionData SHOULD NOT be changed.
    Only getter methods are provided through data and projection_data respectively.


    :param Window window: The Arcade Window instance that you want to bind the camera to. Uses current if undefined.
    :param tuple viewport: The pixel area bounds the camera should draw to. (can be provided through camera_data)
    :param tuple position: The X and Y position of the camera. (can be provided through camera_data)
    :param tuple up: The up vector which defines the +Y axis in screen space. (can be provided through camera_data)
    :param float zoom: A float which scales the viewport. (can be provided through camera_data)
    :param tuple projection: The area which will be mapped to screen space. (can be provided through projection_data)
    :param float near: The closest Z position before clipping. (can be provided through projection_data)
    :param float far: The furthest Z position before clipping. (can be provided through projection_data)
    :param CameraData camera_data: A data class which holds all the data needed to define the view of the camera.
    :param ProjectionData projection_data: A data class which holds all the data needed to define the projection of
                                           the camera.
    """
    # TODO: ADD PARAMS TO DOC FOR __init__

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

        assert (
            any((viewport, position, up, zoom)) and camera_data
        ), (
            "Camera2D Warning: Provided both a CameraData object and raw values. Defaulting to CameraData."
        )

        assert (
            any((projection, near, far)) and projection_data
        ), (
            "Camera2D Warning: Provided both an OrthographicProjectionData object and raw values."
            "Defaulting to OrthographicProjectionData."
        )

        _pos = position or (self._window.width / 2, self._window.height / 2)
        _up = up or (0.0, 1.0)
        self._data = camera_data or CameraData(
            viewport or (0, 0, self._window.width, self._window.height),
            (_pos[0], _pos[1], 0.0),
            (_up[0], _up[1], 0.0),
            (0.0, 0.0, 1.0),
            zoom or 1.0
        )

        _proj = projection or (
            -self._window.width/2, self._window.width/2,
            -self._window.height/2, self._window.height/2
        )
        self._projection = projection_data or OrthographicProjectionData(
            _proj[0], _proj[1],  # Left and Right.
            _proj[2], _proj[3],  # Bottom and Top.
            near or 0.0, far or 100.0  # Near and Far.
        )

        self._ortho_projector: OrthographicProjector = OrthographicProjector(
            window=self._window,
            view=self._data,
            projection=self._projection
        )

    @property
    def data(self) -> CameraData:
        """
        Return the view data for the camera. This includes the
        viewport, position, forward vector, up direction, and zoom.

        If you use any of the built-in arcade camera-controllers
        or make your own this is the property to access.
        """
        # TODO: Do not add setter
        return self._data

    @property
    def projection_data(self) -> OrthographicProjectionData:
        """
        Return the projection data for the camera.
        This is an Orthographic projection. with a
        right, left, top, bottom, near, and far value.
        An easy way to understand the use of the projection is
        that the right value of the projection tells the
        camera what value will be at the right most
        pixel in the viewport.

        Due to the view data having a zoom component
        most use cases will only change the projection
        on screen resize.
        """
        # TODO: Do not add setter
        return self._projection

    @property
    def pos(self) -> Tuple[float, float]:
        """
        The 2D position of the camera along
        the X and Y axis. Arcade has the positive
        Y direction go towards the top of the screen.
        """
        return self._data.position[:2]

    @pos.setter
    def pos(self, _pos: Tuple[float, float]) -> None:
        """
        Set the X and Y position of the camera.
        """
        self._data.position = _pos + self._data.position[2:]

    @property
    def left(self) -> float:
        """
        The left side of the camera in world space.
        Use this to check if a sprite is on screen.
        """
        return self._data.position[0] + self._projection.left/self._data.zoom

    @left.setter
    def left(self, _left: float) -> None:
        """
        Set the left side of the camera. This moves the position of the camera.
        To change the left of the projection use projection_left.
        """
        self._data.position = (_left - self._projection.left/self._data.zoom,) + self._data.position[1:]

    @property
    def right(self) -> float:
        """
        The right side of the camera in world space.
        Use this to check if a sprite is on screen.
        """
        return self._data.position[0] + self._projection.right/self._data.zoom

    @right.setter
    def right(self, _right: float) -> None:
        """
        Set the right side of the camera. This moves the position of the camera.
        To change the right of the projection use projection_right.
        """
        self._data.position = (_right - self._projection.right/self._data.zoom,) + self._data.position[1:]

    @property
    def bottom(self) -> float:
        """
        The bottom side of the camera in world space.
        Use this to check if a sprite is on screen.
        """
        return self._data.position[1] + self._projection.bottom/self._data.zoom

    @bottom.setter
    def bottom(self, _bottom: float) -> None:
        """
        Set the bottom side of the camera. This moves the position of the camera.
        To change the bottom of the projection use projection_bottom.
        """
        self._data.position = (
            self._data.position[0],
            _bottom - self._projection.bottom/self._data.zoom,
            self._data.position[2]
        )

    @property
    def top(self) -> float:
        """
        The top side of the camera in world space.
        Use this to check if a sprite is on screen.
        """
        return self._data.position[1] + self._projection.top/self._data.zoom

    @top.setter
    def top(self, _top: float) -> None:
        """
        Set the top side of the camera. This moves the position of the camera.
        To change the top of the projection use projection_top.
        """
        self._data.position = (
            self._data.position[0],
            _top - self._projection.top/self._data.zoom,
            self._data.position[2]
        )

    @property
    def projection(self) -> Tuple[float, float, float, float]:
        """
        The left, right, bottom, top values
        that maps world space coordinates to pixel positions.
        """
        _p = self._projection
        return _p.left, _p.right, _p.bottom, _p.top

    @projection.setter
    def projection(self, value: Tuple[float, float, float, float]) -> None:
        """
        Set the left, right, bottom, top values
        that maps world space coordinates to pixel positions.
        """
        _p = self._projection
        _p.left, _p.right, _p.bottom, _p.top = value

    @property
    def projection_width(self) -> float:
        """
        The width of the projection from left to right.
        This is in world space coordinates not pixel coordinates.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_width_scaled instead.
        """
        return self._projection.right - self._projection.left

    @projection_width.setter
    def projection_width(self, _width: float):
        """
        Set the width of the projection from left to right.
        This is in world space coordinates not pixel coordinates.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_width_scaled instead.
        """
        w = self.projection_width
        l = self.projection_left / w  # Normalised Projection left
        r = self.projection_right / w  # Normalised Projection Right

        self.projection_left = l * _width
        self.projection_right = r * _width

    @property
    def projection_width_scaled(self) -> float:
        """
        The width of the projection from left to right.
        This is in world space coordinates not pixel coordinates.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_width instead.
        """
        return (self._projection.right - self._projection.left) / self._data.zoom

    @projection_width_scaled.setter
    def projection_width_scaled(self, _width: float) -> None:
        """
        Set the width of the projection from left to right.
        This is in world space coordinates not pixel coordinates.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_width instead.
        """
        w = self.projection_width * self._data.zoom
        l = self.projection_left / w  # Normalised Projection left
        r = self.projection_right / w  # Normalised Projection Right

        self.projection_left = l * _width
        self.projection_right = r * _width

    @property
    def projection_height(self) -> float:
        """
        The height of the projection from bottom to top.
        This is in world space coordinates not pixel coordinates.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_height_scaled instead.
        """
        return self._projection.top - self._projection.bottom

    @projection_height.setter
    def projection_height(self, _height: float) -> None:
        """
        Set the height of the projection from bottom to top.
        This is in world space coordinates not pixel coordinates.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_height_scaled instead.
        """
        h = self.projection_height
        b = self.projection_bottom / h  # Normalised Projection Bottom
        t = self.projection_top / h  # Normalised Projection Top

        self.projection_bottom = b * _height
        self.projection_top = t * _height

    @property
    def projection_height_scaled(self) -> float:
        """
        The height of the projection from bottom to top.
        This is in world space coordinates not pixel coordinates.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_height instead.
        """
        return (self._projection.top - self._projection.bottom) / self._data.zoom

    @projection_height_scaled.setter
    def projection_height_scaled(self, _height: float) -> None:
        """
        Set the height of the projection from bottom to top.
        This is in world space coordinates not pixel coordinates.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_height instead.
        """
        h = self.projection_height * self._data.zoom
        b = self.projection_bottom / h  # Normalised Projection Bottom
        t = self.projection_top / h  # Normalised Projection Top

        self.projection_bottom = b * _height
        self.projection_top = t * _height

    @property
    def projection_left(self) -> float:
        """
        The left edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_left_scaled instead.
        """
        return self._projection.left

    @projection_left.setter
    def projection_left(self, _left: float) -> None:
        """
        Set the left edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_left_scaled instead.
        """
        self._projection.left = _left

    @property
    def projection_left_scaled(self) -> float:
        """
        The left edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_left instead.
        """
        return self._projection.left / self._data.zoom

    @projection_left_scaled.setter
    def projection_left_scaled(self, _left: float) -> None:
        """
        The left edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_left instead.
        """
        self._projection.left = _left * self._data.zoom

    @property
    def projection_right(self) -> float:
        """
        The right edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_right_scaled instead.
        """
        return self._projection.right

    @projection_right.setter
    def projection_right(self, _right: float) -> None:
        """
        Set the right edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_right_scaled instead.
        """
        self._projection.right = _right

    @property
    def projection_right_scaled(self) -> float:
        """
        The right edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_right instead.
        """
        return self._projection.right / self._data.zoom

    @projection_right_scaled.setter
    def projection_right_scaled(self, _right: float) -> None:
        """
        Set the right edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_right instead.
        """
        self._projection.right = _right * self._data.zoom

    @property
    def projection_bottom(self) -> float:
        """
        The bottom edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_bottom_scaled instead.
        """
        return self._projection.bottom

    @projection_bottom.setter
    def projection_bottom(self, _bottom: float) -> None:
        """
        Set the bottom edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_bottom_scaled instead.
        """
        self._projection.bottom = _bottom

    @property
    def projection_bottom_scaled(self) -> float:
        """
        The bottom edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_bottom instead.
        """
        return self._projection.bottom / self._data.zoom

    @projection_bottom_scaled.setter
    def projection_bottom_scaled(self, _bottom: float) -> None:
        """
        Set the bottom edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_bottom instead.
        """
        self._projection.bottom = _bottom * self._data.zoom

    @property
    def projection_top(self) -> float:
        """
        The top edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_top_scaled instead.
        """
        return self._projection.top

    @projection_top.setter
    def projection_top(self, _top: float) -> None:
        """
        Set the top edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        If this isn't what you want,
        use projection_top_scaled instead.
        """
        self._projection.top = _top

    @property
    def projection_top_scaled(self) -> float:
        """
        The top edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_top instead.
        """
        return self._projection.top / self._data.zoom

    @projection_top_scaled.setter
    def projection_top_scaled(self, _top: float) -> None:
        """
        Set the top edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_top instead.
        """
        self._projection.top = _top * self._data.zoom

    @property
    def projection_near(self) -> float:
        """
        The near plane of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        """
        return self._projection.near

    @projection_near.setter
    def projection_near(self, _near: float) -> None:
        """
        Set the near plane of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        """
        self._projection.near = _near

    @property
    def projection_far(self) -> float:
        """
        The far plane of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        """
        return self._projection.far

    @projection_far.setter
    def projection_far(self, _far: float) -> None:
        """
        Set the far plane of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        """
        self._projection.far = _far

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """
        The pixel area that will be drawn to while the camera is active.
        (left, right, bottom, top)
        """
        return self._data.viewport

    @viewport.setter
    def viewport(self, _viewport: Tuple[int, int, int, int]) -> None:
        """
        Set the pixel area that will be drawn to while the camera is active.
        (left, bottom, width, height)
        """
        self._data.viewport = _viewport

    @property
    def viewport_width(self) -> int:
        """
        The width of the viewport.
        Defines the number of pixels drawn too horizontally.
        """
        return self._data.viewport[2]

    @viewport_width.setter
    def viewport_width(self, _width: int) -> None:
        """
        Set the width of the viewport.
        Defines the number of pixels drawn too horizontally
        """
        self._data.viewport = self._data.viewport[:2] + (_width, self._data.viewport[3])

    @property
    def viewport_height(self) -> int:
        """
        The height of the viewport.
        Defines the number of pixels drawn too vertically.
        """
        return self._data.viewport[3]

    @viewport_height.setter
    def viewport_height(self, _height: int) -> None:
        """
        Set the height of the viewport.
        Defines the number of pixels drawn too vertically.
        """
        self._data.viewport = self._data.viewport[:3] + (_height,)

    @property
    def viewport_left(self) -> int:
        """
        The left most pixel drawn to on the X axis.
        """
        return self._data.viewport[0]

    @viewport_left.setter
    def viewport_left(self, _left: int) -> None:
        """
        Set the left most pixel drawn to on the X axis.
        """
        self._data.viewport = (_left,) + self._data.viewport[1:]

    @property
    def viewport_right(self) -> int:
        """
        The right most pixel drawn to on the X axis.
        """
        return self._data.viewport[0] + self._data.viewport[2]

    @viewport_right.setter
    def viewport_right(self, _right: int) -> None:
        """
        Set the right most pixel drawn to on the X axis.
        This moves the position of the viewport, not change the size.
        """
        self._data.viewport = (_right - self._data.viewport[2],) + self._data.viewport[1:]

    @property
    def viewport_bottom(self) -> int:
        """
        The bottom most pixel drawn to on the Y axis.
        """
        return self._data.viewport[1]

    @viewport_bottom.setter
    def viewport_bottom(self, _bottom: int) -> None:
        """
        Set the bottom most pixel drawn to on the Y axis.
        """
        self._data.viewport = (self._data.viewport[0], _bottom) + self._data.viewport[2:]

    @property
    def viewport_top(self) -> int:
        """
        The top most pixel drawn to on the Y axis.
        """
        return self._data.viewport[1] + self._data.viewport[3]

    @viewport_top.setter
    def viewport_top(self, _top: int) -> None:
        """
        Set the top most pixel drawn to on the Y axis.
        This moves the position of the viewport, not change the size.
        """
        self._data.viewport = (self._data.viewport[0], _top - self._data.viewport[3]) + self._data.viewport[2:]

    @property
    def up(self) -> Tuple[float, float]:
        """
        A 2D vector which describes what is mapped
        to the +Y direction on screen.
        This is equivalent to rotating the screen.
        The base vector is 3D, but the simplified
        camera only provides a 2D view.
        """
        return self._data.up[:2]

    @up.setter
    def up(self, _up: Tuple[float, float]) -> None:
        """
        Set the 2D vector which describes what is
        mapped to the +Y direction on screen.
        This is equivalent to rotating the screen.
        The base vector is 3D, but the simplified
        camera only provides a 2D view.

        NOTE that this is assumed to be normalised.
        """
        self._data.up = _up + (0,)

    @property
    def angle(self) -> float:
        """
        An angle representation of the 2D UP vector.
        This starts with 0 degrees as [0, 1] rotating
        clock-wise.
        """
        # Note that this is flipped as we want 0 degrees to be vert. Normally you have y first and then x.
        return degrees(atan2(self._data.position[0], self._data.position[1]))

    @angle.setter
    def angle(self, value: float):
        """
        Set the 2D UP vector using an angle.
        This starts with 0 degrees as [0, 1]
        rotating clock-wise.
        """
        _r = radians(value)
        # Note that this is flipped as we want 0 degrees to be vert.
        self._data.position = (sin(_r), cos(_r), 0.0)

    @property
    def zoom(self) -> float:
        """
        A scalar value which describes
        how much the projection should
        be scaled towards from its center.

        A value of 2.0 causes the projection
        to be half its original size.
        This causes sprites to appear 2.0x larger.
        """
        return self._data.zoom

    @zoom.setter
    def zoom(self, _zoom: float) -> None:
        """
        Set the scalar value which describes
        how much the projection should
        be scaled towards from its center.

        A value of 2.0 causes the projection
        to be half its original size.
        This causes sprites to appear 2.0x larger.
        """
        self._data.zoom = _zoom

    def equalise(self) -> None:
        """
        Forces the projection to match the size of the viewport.
        When matching the projection to the viewport the method keeps
        the projections center in the same relative place.
        """

        self.projection_width = self.viewport_width
        self.projection_height = self.viewport_height

    def match_screen(self, and_projection: bool = True) -> None:
        """
        Sets the viewport to the size of the screen.
        Should be called when the screen is resized.

        :param and_projection: Also equalises the projection if True.
        """
        self.viewport = (0, 0, self._window.width, self._window.height)

        if and_projection:
            self.equalise()

    def use(self) -> None:
        """
        Set internal projector as window projector,
        and set the projection and view matrix.
        call every time you want to 'look through' this camera.

        If you want to use a 'with' block use activate() instead.
        """
        self._ortho_projector.use()

    @contextmanager
    def activate(self) -> Iterator[Projector]:
        """
        Set internal projector as window projector,
        and set the projection and view matrix.

        This method works with 'with' blocks.
        After using this method it automatically resets
        the projector to the one previously in use.
        """
        previous_projection = self._window.current_camera
        try:
            self.use()
            yield self
        finally:
            previous_projection.use()

    def map_coordinate(self, screen_coordinates: Tuple[float, float]) -> Tuple[float, float]:
        """
        Take in a pixel coordinate from within
        the range of the viewport and returns
        the world space coordinates.

        Essentially reverses the effects of the projector.

        :param screen_coordinates: The pixel coordinates to map back to world coordinates.
        """

        return self._ortho_projector.get_map_coordinates(screen_coordinates)
