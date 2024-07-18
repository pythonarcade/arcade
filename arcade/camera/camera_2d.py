from __future__ import annotations

from contextlib import contextmanager
from math import atan2, cos, degrees, radians, sin
from typing import TYPE_CHECKING, Generator

from pyglet.math import Vec2, Vec3
from typing_extensions import Self

from arcade.camera.data_types import (
    CameraData,
    OrthographicProjectionData,
    ZeroProjectionDimension,
)
from arcade.camera.projection_functions import (
    generate_orthographic_matrix,
    generate_view_matrix,
    project_orthographic,
    unproject_orthographic,
)
from arcade.gl import Framebuffer
from arcade.types import LBWH, LRBT, XYWH, Point, Rect
from arcade.types.vector_like import Point2
from arcade.window_commands import get_window

if TYPE_CHECKING:
    from arcade.application import Window

__all__ = ["Camera2D"]


class Camera2D:
    """
    A simple orthographic camera. Similar to SimpleCamera, but takes better advantage
    of the new data structures. As the Simple Camera is depreciated, any new project
    should use this camera instead.

    It provides properties to access every important variable for controlling the camera.
    3D properties such as pos, and up are constrained to a 2D plane. There is no access to the
    forward vector (as a property).

    The method fully fulfils both the Camera and Projector protocols.

    There are also ease of use methods for matching the viewport and projector to the window size.

    Provides many helpful values:
        * The position and rotation or the camera
        * 8 positions along the edge of the camera's viewable area
        * the bounding box of the area the camera sees
        * Viewport, and Scissor box for controlling where to draw to

    .. warning:: Do not replace the ``camera_data`` and ``projection_data``
                 instances after initialization!

    Replacing the camera data and projection data may break controllers. Their
    contents are exposed via properties rather than directly to prevent this.

    :param viewport: A 4-int tuple which defines the pixel bounds which the camera
        will project to.
    :param position: The 2D position of the camera in the XY plane.
    :param up: A 2D vector which describes which direction is up
        (defines the +Y-axis of the camera space).
    :param zoom: A scalar value which is inversely proportional to the size of the
        camera projection. i.e. a zoom of 2.0 halves the size of the projection,
        doubling the perceived size of objects.
    :param projection: A 4-float tuple which defines the world space
                bounds which the camera projects to the viewport.
    :param near: The near clipping plane of the camera.
    :param far: The far clipping plane of the camera.
    :param render_target: The FrameBuffer that the camera uses. Defaults to the screen.
        If the framebuffer is not the default screen nothing drawn after this camera is used will
        show up. The FrameBuffer's internal viewport is ignored.
    :param window: The Arcade Window to bind the camera to.
        Defaults to the currently active window.

    :attributes:
        * render_target - An optional framebuffer to activate at the same time as
            the projection data, could be the screen, or an offscreen texture
        * viewport - A rect which describes how the final projection should be mapped
            from unit-space. defaults to the size of the render_target or window
        * scissor - An optional rect which describes what pixels of the active render
            target should be drawn to when undefined the viewport rect is used.
    """

    def __init__(
        self,
        viewport: Rect | None = None,
        position: Point2 | None = None,
        up: tuple[float, float] = (0.0, 1.0),
        zoom: float = 1.0,
        projection: Rect | None = None,
        near: float = -100.0,
        far: float = 100.0,
        *,
        scissor: Rect | None = None,
        render_target: Framebuffer | None = None,
        window: Window | None = None,
    ):
        self._window: Window = window or get_window()
        self.render_target: Framebuffer | None = render_target

        # We don't want to force people to use a render target,
        # but we need to have some form of default size.
        render_target = render_target or self._window.ctx.screen
        viewport = viewport or LBWH(*render_target.viewport)
        width, height = viewport.size
        half_width = width / 2
        half_height = height / 2

        # Unpack projection, but only validate when it's given directly
        left, right, bottom, top = (
            (-half_width, half_width, -half_height, half_height)
            if projection is None
            else projection.lrbt
        )

        if projection is not None:
            if left == right:
                raise ZeroProjectionDimension(
                    (f"projection width is 0 due to equal {left=}" f"and {right=} values")
                )
            if bottom == top:
                raise ZeroProjectionDimension(
                    (f"projection height is 0 due to equal {bottom=}" f"and {top=}")
                )
        if near == far:
            raise ZeroProjectionDimension(
                f"projection depth is 0 due to equal {near=}" f"and {far=} values"
            )

        _pos = position or (half_width, half_height)
        self._camera_data = CameraData(
            position=(_pos[0], _pos[1], 0.0),
            up=(up[0], up[1], 0.0),
            forward=(0.0, 0.0, -1.0),
            zoom=zoom,
        )
        self._projection_data: OrthographicProjectionData = OrthographicProjectionData(
            left=left, right=right, top=top, bottom=bottom, near=near, far=far
        )

        self.viewport: Rect = viewport or LRBT(0, 0, width, height)
        self.scissor: Rect | None = scissor

    @classmethod
    def from_camera_data(
        cls,
        *,
        camera_data: CameraData | None = None,
        projection_data: OrthographicProjectionData | None = None,
        render_target: Framebuffer | None = None,
        viewport: Rect | None = None,
        scissor: Rect | None = None,
        window: Window | None = None,
    ) -> Self:
        """
        Make a ``Camera2D`` directly from data objects.

        This :py:class:`classmethod` allows advanced users to:

        #. skip or replace the default validation
        #. share ``camera_data`` or ``projection_data`` between cameras

        .. warning:: Be careful when sharing data objects!
                    **Any** action on a camera which changes a shared
                    object changes it for **every** camera which uses
                    the same object.

        .. list-table::
          :header-rows: 1

          * - Shared Value
            - Example Use(s)
          * - ``camera_data``
            - Mini-maps, reflection, and ghosting effects.
          * - ``projection_data``
            - Simplified rendering configuration
          * - ``render_target``
            - Complex rendering setups

        :param camera_data: A :py:class:`~arcade.camera.data.CameraData`
            describing the position, up, forward and zoom.
        :param projection_data:
            A :py:class:`~arcade.camera.data.OrthographicProjectionData`
            which describes the left, right, top, bottom, far, near
            planes and the viewport for an orthographic projection.
        :param render_target: A non-screen
            :py:class:`~arcade.gl.framebuffer.Framebuffer` for this
            camera to draw into. When specified,

            * nothing will draw directly to the screen
            * the buffer's internal viewport will be ignored

        :param viewport:
            A viewport as a :py:class:`~arcade.types.rect.Rect`.
            This overrides any viewport the ``render_target`` may have.
        :param scissor:
            The OpenGL scissor box to use when drawing.
        :param window: The Arcade Window to bind the camera to.
            Defaults to the currently active window.
        """

        if projection_data:
            left, right = projection_data.left, projection_data.right
            if projection_data.left == projection_data.right:
                raise ZeroProjectionDimension(
                    (f"projection width is 0 due to equal {left=}" f"and {right=} values")
                )
            bottom, top = projection_data.bottom, projection_data.top
            if bottom == top:
                raise ZeroProjectionDimension(
                    (f"projection height is 0 due to equal {bottom=}" f"and {top=}")
                )
            near, far = projection_data.near, projection_data.far
            if near == far:
                raise ZeroProjectionDimension(
                    f"projection depth is 0 due to equal {near=}" f"and {far=} values"
                )

        # build a new camera with defaults and then apply the provided camera objects.
        new_camera = cls(
            render_target=render_target, window=window, viewport=viewport, scissor=scissor
        )

        if camera_data:
            new_camera._camera_data = camera_data
        if projection_data:
            new_camera._projection_data = projection_data

        return new_camera

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
        return self._camera_data

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
        return self._projection_data

    @property
    def position(self) -> Vec2:
        """The 2D world position of the camera along the X and Y axes."""
        return Vec2(self._camera_data.position[0], self._camera_data.position[1])

    @position.setter
    def position(self, _pos: Point) -> None:
        x, y, *z = _pos
        z = self._camera_data.position[2] if not z else z[0]
        self._camera_data.position = (x, y, z)

    # top_left
    @property
    def top_left(self) -> Vec2:
        """Get the top left most corner the camera can see"""
        pos = self.position
        up = self._camera_data.up

        top = self.top
        left = self.left

        return Vec2(pos.x + up[0] * top + up[1] * left, pos.y + up[1] * top - up[0] * left)

    @top_left.setter
    def top_left(self, new_corner: Point2):
        up = self._camera_data.up

        top = self.top
        left = self.left

        x, y = new_corner
        self.position = (x - up[0] * top - up[1] * left, y - up[0] * top + up[0] * left)

    # top_center
    @property
    def top_center(self) -> Vec2:
        """Get the top most position the camera can see"""
        pos = self.position
        up = self._camera_data.up
        top = self.top
        return Vec2(pos.x + up[0] * top, pos.y + up[1] * top)

    @top_center.setter
    def top_center(self, new_top: Point2):
        up = self._camera_data.up
        top = self.top

        x, y = new_top
        self.position = x - up[0] * top, y - up[1] * top

    # top_right
    @property
    def top_right(self) -> Vec2:
        """Get the top right most corner the camera can see"""
        pos = self.position
        up = self._camera_data.up

        top = self.top
        right = self.right

        return Vec2(pos.x + up[0] * top + up[1] * right, pos.y + up[1] * top - up[0] * right)

    @top_right.setter
    def top_right(self, new_corner: Point2):
        up = self._camera_data.up

        top = self.top
        right = self.right

        x, y = new_corner
        self.position = (x - up[0] * top - up[1] * right, y - up[1] * top + up[0] * right)

    # bottom_right
    @property
    def bottom_right(self) -> Vec2:
        """Get the bottom right most corner the camera can see"""
        pos = self.position
        up = self._camera_data.up

        bottom = self.bottom
        right = self.right
        return Vec2(pos.x + up[0] * bottom + up[1] * right, pos.y + up[1] * bottom - up[0] * right)

    @bottom_right.setter
    def bottom_right(self, new_corner: Point2):
        up = self._camera_data.up

        bottom = self.bottom
        right = self.right

        x, y = new_corner
        self.position = (
            x - up[0] * bottom - up[1] * right,
            y - up[1] * bottom + up[0] * right,
        )

    # bottom_center
    @property
    def bottom_center(self) -> Vec2:
        """Get the bottom most position the camera can see"""
        pos = self.position
        up = self._camera_data.up
        bottom = self.bottom

        return Vec2(pos.x - up[0] * bottom, pos.y - up[1] * bottom)

    @bottom_center.setter
    def bottom_center(self, new_bottom: Point2):
        up = self._camera_data.up
        bottom = self.bottom

        x, y = new_bottom
        self.position = x - up[0] * bottom, y - up[0] * bottom

    # bottom_left
    @property
    def bottom_left(self) -> Vec2:
        """Get the bottom left most corner the camera can see"""
        pos = self.position
        up = self._camera_data.up

        bottom = self.bottom
        left = self.left

        return Vec2(pos.x + up[0] * bottom + up[1] * left, pos.y + up[1] * bottom - up[0] * left)

    @bottom_left.setter
    def bottom_left(self, new_corner: Point2):
        up = self._camera_data.up

        bottom = self.bottom
        left = self.left

        x, y = new_corner
        self.position = (x - up[0] * bottom - up[1] * left, y - up[1] * bottom + up[0] * left)

    # center_right
    @property
    def center_right(self) -> Vec2:
        """Get the right most point the camera can see"""
        pos = self.position
        up = self._camera_data.up
        right = self.right
        return Vec2(pos.x + up[1] * right, pos.y - up[0] * right)

    @center_right.setter
    def center_right(self, new_right: Point2):
        up = self._camera_data.up
        right = self.right

        x, y = new_right
        self.position = x - up[1] * right, y + up[0] * right

    # center_left
    @property
    def center_left(self) -> Vec2:
        """Get the left most point the camera can see"""
        pos = self.position
        up = self._camera_data.up
        left = self.left
        return Vec2(pos.x + up[1] * left, pos.y - up[0] * left)

    @center_left.setter
    def center_left(self, new_left: Point2):
        up = self._camera_data.up
        left = self.left

        x, y = new_left
        self.position = x - up[1] * left, y - up[0] * left

    def aabb(self) -> Rect:
        """
        Retrieve the axis-aligned bounds box of the camera's view area.
        If the camera isn't rotated , this will be precisely the view area,
        but it will cover a larger area when it is rotated.
        """
        tr_x, tr_y = self.top_right
        tl_x, tl_y = self.top_left
        br_x, br_y = self.bottom_right
        bl_x, bl_y = self.bottom_left
        left = min(tl_x, tr_x, bl_x, br_x)
        right = max(tl_x, tr_x, bl_x, br_x)
        bottom = min(tl_y, tr_y, bl_y, br_y)
        top = max(tl_y, tr_y, bl_y, br_y)
        return LRBT(left=left, right=right, bottom=bottom, top=top)

    def point_in_view(self, point: Point2) -> bool:
        """
        Take a 2D point in the world, and return whether the point is inside the
        visible area of the camera.
        """
        pos = self.position
        diff = point[0] - pos[0], point[1] - pos[1]

        up = self._camera_data.up

        h_width = self.width / 2.0
        h_height = self.height / 2.0

        dot_x = up[1] * diff[0] - up[0] * diff[1]
        dot_y = up[0] * diff[0] + up[1] * diff[1]

        return abs(dot_x) <= h_width and abs(dot_y) <= h_height

    @property
    def projection(self) -> Rect:
        """Get/set the left, right, bottom, and top projection values.

        These are world space values which control how the camera
        projects the world onto the pixel space of the current
        viewport area.

        .. warning:: The axis values cannot be equal!

                     * ``left`` cannot equal ``right``
                     * ``bottom`` cannot equal ``top``

        This property raises a :py:class:`~arcade.camera.data_types.ZeroProjectionDimension`
        exception if any axis pairs are equal. You can handle this
        exception as a :py:class:`ValueError`.
        """

        return self._projection_data.rect / self._camera_data.zoom

    @projection.setter
    def projection(self, value: Rect) -> None:

        # Unpack and validate
        if not value:
            raise ZeroProjectionDimension((f"Projection area is 0, {value.lrbt}"))

        _z = self._camera_data.zoom

        # Modify the projection data itself.
        self._projection_data.rect = value * _z

    @property
    def width(self) -> float:
        """
        The width of the projection from left to right.
        This is in world space coordinates not pixel coordinates.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        you have to calculate the value manually from projection_data
        """
        return (self._projection_data.right - self._projection_data.left) / self._camera_data.zoom

    @width.setter
    def width(self, new_width: float) -> None:
        w = self.width
        l = self.left / w  # Normalised Projection left
        r = self.right / w  # Normalised Projection Right

        self.left = l * new_width
        self.right = r * new_width

    @property
    def height(self) -> float:
        """
        The height of the projection from bottom to top.
        This is in world space coordinates not pixel coordinates.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        you have to calculate the value manually from projection_data
        """
        return (self._projection_data.top - self._projection_data.bottom) / self._camera_data.zoom

    @height.setter
    def height(self, new_height: float) -> None:
        h = self.height
        b = self.bottom / h  # Normalised Projection Bottom
        t = self.top / h  # Normalised Projection Top

        self.bottom = b * new_height
        self.top = t * new_height

    @property
    def left(self) -> float:
        """
        The left edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_data.left instead.
        """
        return self._projection_data.left / self._camera_data.zoom

    @left.setter
    def left(self, new_left: float) -> None:
        self._projection_data.left = new_left * self._camera_data.zoom

    @property
    def right(self) -> float:
        """
        The right edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_data.right instead.
        """
        return self._projection_data.right / self._camera_data.zoom

    @right.setter
    def right(self, new_right: float) -> None:
        self._projection_data.right = new_right * self._camera_data.zoom

    @property
    def bottom(self) -> float:
        """
        The bottom edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_data.bottom instead.
        """
        return self._projection_data.bottom / self._camera_data.zoom

    @bottom.setter
    def bottom(self, new_bottom: float) -> None:
        self._projection_data.bottom = new_bottom * self._camera_data.zoom

    @property
    def top(self) -> float:
        """
        The top edge of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS scaled by zoom.
        If this isn't what you want,
        use projection_data.top instead.
        """
        return self._projection_data.top / self._camera_data.zoom

    @top.setter
    def top(self, new_top: float) -> None:
        self._projection_data.top = new_top * self._camera_data.zoom

    @property
    def projection_near(self) -> float:
        """
        The near plane of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        """
        return self._projection_data.near

    @projection_near.setter
    def projection_near(self, new_near: float) -> None:
        self._projection_data.near = new_near

    @property
    def projection_far(self) -> float:
        """
        The far plane of the projection in world space.
        This is not adjusted with the camera position.

        NOTE this IS NOT scaled by zoom.
        """
        return self._projection_data.far

    @projection_far.setter
    def projection_far(self, new_far: float) -> None:
        self._projection_data.far = new_far

    @property
    def viewport_width(self) -> int:
        """
        The width of the viewport.
        Defines the number of pixels drawn too horizontally.
        """
        return int(self.viewport.width)

    @viewport_width.setter
    def viewport_width(self, new_width: int) -> None:
        self.viewport = self.viewport.resize(new_width, anchor=Vec2(0.0, 0.0))

    @property
    def viewport_height(self) -> int:
        """
        The height of the viewport.
        Defines the number of pixels drawn too vertically.
        """
        return int(self.viewport.height)

    @viewport_height.setter
    def viewport_height(self, new_height: int) -> None:
        self.viewport = self.viewport.resize(height=new_height, anchor=Vec2(0.0, 0.0))

    @property
    def viewport_left(self) -> int:
        """
        The left most pixel drawn to on the X axis.
        """
        return int(self.viewport.left)

    @viewport_left.setter
    def viewport_left(self, new_left: int) -> None:
        self.viewport = self.viewport.align_left(new_left)

    @property
    def viewport_right(self) -> int:
        """
        The right most pixel drawn to on the X axis.
        """
        return int(self.viewport.right)

    @viewport_right.setter
    def viewport_right(self, new_right: int) -> None:
        """
        Set the right most pixel drawn to on the X axis.
        This moves the position of the viewport, not change the size.
        """
        self.viewport = self.viewport.align_right(new_right)

    @property
    def viewport_bottom(self) -> int:
        """
        The bottom most pixel drawn to on the Y axis.
        """
        return int(self.viewport.bottom)

    @viewport_bottom.setter
    def viewport_bottom(self, new_bottom: int) -> None:
        """
        Set the bottom most pixel drawn to on the Y axis.
        """
        self.viewport = self.viewport.align_bottom(new_bottom)

    @property
    def viewport_top(self) -> int:
        """
        The top most pixel drawn to on the Y axis.
        """
        return int(self.viewport.top)

    @viewport_top.setter
    def viewport_top(self, new_top: int) -> None:
        """
        Set the top most pixel drawn to on the Y axis.
        This moves the position of the viewport, not change the size.
        """
        self.viewport = self.viewport.align_top(new_top)

    @property
    def up(self) -> Vec2:
        """
        A 2D vector which describes what is mapped
        to the +Y direction on screen.
        This is equivalent to rotating the screen.
        The base vector is 3D, but the simplified
        camera only provides a 2D view.
        """
        return Vec2(self._camera_data.up[0], self._camera_data.up[1])

    @up.setter
    def up(self, _up: Point2) -> None:
        """
        Set the 2D vector which describes what is
        mapped to the +Y direction on screen.
        This is equivalent to rotating the screen.
        The base vector is 3D, but the simplified
        camera only provides a 2D view.

        NOTE that this is assumed to be normalised.
        """
        x, y = _up
        self._camera_data.up = (x, y, 0.0)

    @property
    def angle(self) -> float:
        """
        An angle representation of the 2D UP vector.
        This starts with 0 degrees as [0, 1] rotating
        clock-wise.
        """
        # Note that this is flipped as we want 0 degrees to be vert.
        # Normally you have y first and then x.
        return degrees(atan2(self._camera_data.up[0], self._camera_data.up[1]))

    @angle.setter
    def angle(self, value: float) -> None:
        """
        Set the 2D UP vector using an angle.
        This starts with 0 degrees as [0, 1]
        rotating clock-wise.
        """
        _r = radians(value)
        # Note that this is flipped as we want 0 degrees to be vert.
        self._camera_data.up = (sin(_r), cos(_r), 0.0)

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
        return self._camera_data.zoom

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
        self._camera_data.zoom = _zoom

    def equalise(self) -> None:
        """
        Forces the projection to match the size of the viewport.
        When matching the projection to the viewport the method keeps
        the projections center in the same relative place.
        """
        x, y = self._projection_data.rect.x, self._projection_data.rect.y
        self._projection_data.rect = XYWH(x, y, self.viewport_width, self.viewport_height)

    def match_screen(
        self, and_projection: bool = True, and_scissor: bool = True, and_position: bool = False
    ) -> None:
        """
        Sets the viewport to the size of the screen.
        Should be called when the screen is resized.

        Args:
            and_projection: Flag whether to also equalize the projection to the viewport.
                On by default
            and_scissor: Flag whether to also equalize the scissor box to the viewport.
                On by default
            and_position: Flag whether to also center the camera to the viewport.
                Off by default
        """
        self.viewport = LBWH(0, 0, self._window.width, self._window.height)

        if and_projection:
            self.equalise()

        if and_scissor and self.scissor:
            self.scissor = self.viewport

        if and_position:
            self.position = self.viewport.center

    def use(self) -> None:
        """
        Set internal projector as window projector,
        and set the projection and view matrix.
        call every time you want to 'look through' this camera.

        If you want to use a 'with' block use activate() instead.
        """
        if self.render_target is not None:
            self.render_target.use()
        self._window.current_camera = self

        _projection = generate_orthographic_matrix(self.projection_data, self.zoom)
        _view = generate_view_matrix(self.view_data)

        self._window.ctx.viewport = self.viewport.viewport
        self._window.ctx.scissor = None if not self.scissor else self.scissor.viewport
        self._window.projection = _projection
        self._window.view = _view

    @contextmanager
    def activate(self) -> Generator[Self, None, None]:
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
            self.use()
            yield self
        finally:
            previous_framebuffer.use()
            previous_projection.use()

    def project(self, world_coordinate: Point) -> Vec2:
        """
        Take a Vec2 or Vec3 of coordinates and return the related screen coordinate
        """
        _projection = generate_orthographic_matrix(self.projection_data, self.zoom)
        _view = generate_view_matrix(self.view_data)

        return project_orthographic(
            world_coordinate,
            self.viewport.viewport,
            _view,
            _projection,
        )

    def unproject(self, screen_coordinate: Point) -> Vec3:
        """
        Take in a pixel coordinate from within
        the range of the window size and returns
        the world space coordinates.

        Essentially reverses the effects of the projector.

        Args:
            screen_coordinate: A 2D or 3D position in pixels from the bottom left of the screen.
                               This should ALWAYS be in the range of 0.0 - screen size.
        Returns:
            A 3D vector in world space (same as sprites).
            perfect for finding if the mouse overlaps with a sprite or ui element irrespective
            of the camera.
        """

        _projection = generate_orthographic_matrix(self.projection_data, self.zoom)
        _view = generate_view_matrix(self.view_data)
        return unproject_orthographic(screen_coordinate, self.viewport.viewport, _view, _projection)
