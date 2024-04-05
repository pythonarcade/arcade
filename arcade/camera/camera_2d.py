from typing import TYPE_CHECKING, Optional, Tuple, Iterator
from math import degrees, radians, atan2, cos, sin
from contextlib import contextmanager

from arcade.camera.orthographic import OrthographicProjector
from arcade.camera.data_types import CameraData, OrthographicProjectionData, Projector
from arcade.gl import Framebuffer

from arcade.window_commands import get_window
if TYPE_CHECKING:
    from arcade.application import Window


__all__ = [
    'Camera2D'
]


class Camera2D:
    """
    A simple orthographic camera. Similar to SimpleCamera, but takes better advantage of the new data structures.
    As the Simple Camera is depreciated, any new project should use this camera instead.

    It provides properties to access every important variable for controlling the camera.
    3D properties such as pos, and up are constrained to a 2D plane. There is no access to the
    forward vector (as a property).

    The method fully fulfils both the Camera and Projector protocols.

    There are also ease of use methods for matching the viewport and projector to the window size.

    Provides 4 sets of left, right, bottom, top:

    * View Data, or where the camera is in
    * Projection without zoom scaling.
    * Projection with zoom scaling.
    * Viewport in screen pixels

    .. warning:: Do not replace the ``camera_data`` and ``projection_data``
                 instances after initialization!

    Replacing the camera data and projection data may break controllers. Their
    contents are exposed via properties rather than directly to prevent this.

    :param window: The Arcade Window to bind the camera to.
            Defaults to the currently active window.
    :param camera_data: A :py:class:`~arcade.camera.data.CameraData`
        describing the viewport, position, up, and zoom.
    :param projection_data: A :py:class:`~arcade.camera.data.OrthographicProjectionData`
        which describes the left, right, top, bottom, far, near planes for an orthographic projection.
    :param render_target: The FrameBuffer that the camera uses. Defaults to the screen.
        If the framebuffer is not the default screen nothing drawn after this camera is used will
        show up. The FrameBuffer's internal viewport is ignored.
    """
    def __init__(self, *,
                 camera_data: Optional[CameraData] = None,
                 projection_data: Optional[OrthographicProjectionData] = None,
                 render_target: Optional[Framebuffer] = None,
                 window: Optional["Window"] = None):
        self._window: "Window" = window or get_window()
        self.render_target: Framebuffer = render_target or self._window.ctx.screen

        half_width = self._window.width / 2
        half_height = self._window.height / 2

        self._data = camera_data or CameraData(
            (half_width, half_height, 0.0),  # position
            (0.0, 1.0, 0.0),  # up vector
            (0.0, 0.0, -1.0),  # forward vector
            1.0  # zoom
        )
        self._projection: OrthographicProjectionData = projection_data or OrthographicProjectionData(
            -half_width, half_width,  # Left and Right.
            -half_height, half_height,  # Bottom and Top.
            0.0, 100.0,  # Near and Far.
            (0, 0, self._window.width, self._window.height)  # Viewport
        )

        self._ortho_projector: OrthographicProjector = OrthographicProjector(
            window=self._window,
            view=self._data,
            projection=self._projection
        )

    @staticmethod
    def from_raw_data(
            viewport: Optional[Tuple[int, int, int, int]] = None,
            position: Optional[Tuple[float, float]] = None,
            up: Tuple[float, float] = (0.0, 1.0),
            zoom: float = 1.0,
            projection: Optional[Tuple[float, float, float, float]] = None,
            near: float = -100,
            far: float = 100,
            *,
            render_target: Optional[Framebuffer] = None,
            window: Optional["Window"] = None
    ):
        """
        Create a Camera2D without first defining CameraData or an OrthographicProjectionData object.

        :param viewport: A 4-int tuple which defines the pixel bounds which the camera with project to.
        :param position: The 2D position of the camera in the XY plane.
        :param up: The 2D unit vector which defines the +Y-axis of the camera space.
        :param zoom: A scalar value which is inversely proportional to the size of the camera projection.
                i.e. a zoom of 2.0 halves the size of the projection, doubling the perceived size of objects.
        :param projection: A 4-float tuple which defines the world space
                    bounds which the camera projects to the viewport.
        :param near: The near clipping plane of the camera.
        :param far: The far clipping plane of the camera.
        :param render_target: The FrameBuffer that the camera uses. Defaults to the screen.
            If the framebuffer is not the default screen nothing drawn after this camera is used will
            show up. The FrameBuffer's internal viewport is ignored.
        :param window: The Arcade Window to bind the camera to.
            Defaults to the currently active window.
        """
        window = window or get_window()

        half_width = window.width / 2
        half_height = window.height / 2

        _pos = position or (half_width, half_height)
        _data: CameraData = CameraData(
            (_pos[0], _pos[1], 0.0),  # position
            (up[0], up[1], 0.0),  # up vector
            (0.0, 0.0, -1.0),  # forward vector
            zoom  # zoom
        )

        left, right, bottom, top = projection or (-half_width, half_width, -half_height, half_height)
        _projection: OrthographicProjectionData = OrthographicProjectionData(
            left, right,  # Left and Right.
            top, bottom,  # Bottom and Top.
            near or 0.0, far or 100.0,  # Near and Far.
            viewport or (0, 0, window.width, window.height)  # Viewport
        )

        return Camera2D(
            camera_data=_data,
            projection_data=_projection,
            window=window,
            render_target=(render_target or window.ctx.screen)
        )

    @property
    def view_data(self) -> CameraData:
        """The view data for the camera.

        This includes:

        * the position
        * forward vector
        * up direction
        * zoom.

        Camera controllers use this property. You will need to access
        it if you use implement a custom one.
        """
        return self._data

    @property
    def projection_data(self) -> OrthographicProjectionData:
        """The projection data for the camera.

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
        return self._projection

    @property
    def position(self) -> Tuple[float, float]:
        """The 2D world position of the camera along the X and Y axes."""
        return self._data.position[:2]

    @position.setter
    def position(self, _pos: Tuple[float, float]) -> None:
        self._data.position = (_pos[0], _pos[1], self._data.position[2])

    @property
    def left(self) -> float:
        """The left side of the camera in world space.

        Useful for checking if a :py:class:`~arcade.Sprite` is on screen.
        """
        return self._data.position[0] + self._projection.left/self._data.zoom

    @left.setter
    def left(self, _left: float) -> None:
        self._data.position = (_left - self._projection.left/self._data.zoom,) + self._data.position[1:]

    @property
    def right(self) -> float:
        """The right edge of the camera in world space.

        Useful for checking if a :py:class:`~arcade.Sprite` is on screen.
        """
        return self._data.position[0] + self._projection.right/self._data.zoom

    @right.setter
    def right(self, _right: float) -> None:
        self._data.position = (_right - self._projection.right/self._data.zoom,) + self._data.position[1:]

    @property
    def bottom(self) -> float:
        """The bottom edge of the camera in world space.

        Useful for checking if a :py:class:`~arcade.Sprite` is on screen.
        """
        return self._data.position[1] + self._projection.bottom/self._data.zoom

    @bottom.setter
    def bottom(self, _bottom: float) -> None:
        self._data.position = (
            self._data.position[0],
            _bottom - self._projection.bottom/self._data.zoom,
            self._data.position[2]
        )

    @property
    def top(self) -> float:
        """The top edge of the camera in world space.

        Useful for checking if a :py:class:`~arcade.Sprite` is on screen.
        """
        return self._data.position[1] + self._projection.top/self._data.zoom

    @top.setter
    def top(self, _top: float) -> None:
        self._data.position = (
            self._data.position[0],
            _top - self._projection.top/self._data.zoom,
            self._data.position[2]
        )

    @property
    def projection(self) -> Tuple[float, float, float, float]:
        """The camera's left, right, bottom, top projection values.

        These control how the camera projects the world onto the pixels
        of the screen.
        """
        _p = self._projection
        return _p.left, _p.right, _p.bottom, _p.top

    @projection.setter
    def projection(self, value: Tuple[float, float, float, float]) -> None:
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
    def projection_width(self, _width: float) -> None:
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
        self._projection.far = _far

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """
        The pixel area that will be drawn to while the camera is active.
        (left, right, bottom, top)
        """
        return self._projection.viewport

    @viewport.setter
    def viewport(self, _viewport: Tuple[int, int, int, int]) -> None:
        self._projection.viewport = _viewport

    @property
    def viewport_width(self) -> int:
        """
        The width of the viewport.
        Defines the number of pixels drawn too horizontally.
        """
        return self._projection.viewport[2]

    @viewport_width.setter
    def viewport_width(self, _width: int) -> None:
        self._projection.viewport = (self._projection.viewport[0], self._projection.viewport[1],
                                     _width, self._projection.viewport[3])

    @property
    def viewport_height(self) -> int:
        """
        The height of the viewport.
        Defines the number of pixels drawn too vertically.
        """
        return self._projection.viewport[3]

    @viewport_height.setter
    def viewport_height(self, _height: int) -> None:
        self._projection.viewport = (self._projection.viewport[0], self._projection.viewport[1],
                                     self._projection.viewport[2], _height)

    @property
    def viewport_left(self) -> int:
        """
        The left most pixel drawn to on the X axis.
        """
        return self._projection.viewport[0]

    @viewport_left.setter
    def viewport_left(self, _left: int) -> None:
        self._projection.viewport = (_left,) + self._projection.viewport[1:]

    @property
    def viewport_right(self) -> int:
        """
        The right most pixel drawn to on the X axis.
        """
        return self._projection.viewport[0] + self._projection.viewport[2]

    @viewport_right.setter
    def viewport_right(self, _right: int) -> None:
        """
        Set the right most pixel drawn to on the X axis.
        This moves the position of the viewport, not change the size.
        """
        self._projection.viewport = (_right - self._projection.viewport[2], self._projection.viewport[1],
                               self._projection.viewport[2], self._projection.viewport[3])

    @property
    def viewport_bottom(self) -> int:
        """
        The bottom most pixel drawn to on the Y axis.
        """
        return self._projection.viewport[1]

    @viewport_bottom.setter
    def viewport_bottom(self, _bottom: int) -> None:
        """
        Set the bottom most pixel drawn to on the Y axis.
        """
        self._projection.viewport = (self._projection.viewport[0], _bottom,
                                     self._projection.viewport[2], self._projection.viewport[3])

    @property
    def viewport_top(self) -> int:
        """
        The top most pixel drawn to on the Y axis.
        """
        return self._projection.viewport[1] + self._projection.viewport[3]

    @viewport_top.setter
    def viewport_top(self, _top: int) -> None:
        """
        Set the top most pixel drawn to on the Y axis.
        This moves the position of the viewport, not change the size.
        """
        self._projection.viewport = (self._projection.viewport[0], _top - self._projection.viewport[3],
                               self._projection.viewport[2], self._projection.viewport[3])

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
        self._data.up = (_up[0], _up[1], 0.0)

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
    def angle(self, value: float) -> None:
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

        Args:
            and_projection: Flag whether to also equalise the projection to the viewport.
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
        self.render_target.use()
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
        previous_framebuffer = self._window.ctx.active_framebuffer
        try:
            self.render_target.use()
            self.use()
            yield self
        finally:
            previous_framebuffer.use()
            previous_projection.use()

    def map_screen_to_world_coordinate(
            self,
            screen_coordinate: Tuple[float, float],
            depth: float = 0.0
    ) -> Tuple[float, float]:
        """
        Take in a pixel coordinate from within
        the range of the window size and returns
        the world space coordinates.

        Essentially reverses the effects of the projector.

        Args:
            screen_coordinate: A 2D position in pixels from the bottom left of the screen.
                               This should ALWAYS be in the range of 0.0 - screen size.
            depth: The depth value which is mapped along with the screen coordinates. Because of how
                   Orthographic perspectives work this does not impact how the screen_coordinates are mapped.
        Returns:
            A 2D vector (Along the XY plane) in world space (same as sprites).
            perfect for finding if the mouse overlaps with a sprite or ui element irrespective
            of the camera.
        """

        return self._ortho_projector.map_screen_to_world_coordinate(screen_coordinate, depth)[:2]
