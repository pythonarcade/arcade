from __future__ import annotations

from contextlib import contextmanager
from math import atan2, cos, degrees, radians, sin
from typing import TYPE_CHECKING, Generator

from pyglet.math import Vec2, Vec3
from typing_extensions import Self

from arcade.camera.data_types import (
    DEFAULT_FAR,
    DEFAULT_NEAR_ORTHO,
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
from arcade.types import LBWH, LRBT, XYWH, Point, Rect
from arcade.types.vector_like import Point2
from arcade.window_commands import get_window

if TYPE_CHECKING:
    from arcade.application import Window
    from arcade.gl import Framebuffer

__all__ = ["Camera2D"]


class Camera2D:
    """
    A simple orthographic camera.

    It provides properties to access every important variable for controlling the camera.
    3D properties such as pos, and up are constrained to a 2D plane. There is no access to the
    forward vector (as a property).

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

    Args:
        viewport:
            A ``Rect`` which defines the pixel bounds which the camera fits its image to.
            If the viewport is not 1:1 with the projection then positions in world space
            won't match pixels on screen.
        position:
            The 2D position of the camera in the XY plane.
        up:
            A 2D vector which describes which direction is up
            (defines the +Y-axis of the camera space).
        zoom:
            A scalar value which is inversely proportional to the size of the
            camera projection. i.e. a zoom of 2.0 halves the size of the projection,
            doubling the perceived size of objects.
        projection:
            A ``Rect`` which defines the world space
            bounds which the camera projects to the viewport.
        near:
            The near clipping plane of the camera.
        far:
            The far clipping plane of the camera.
        scissor:
            A ``Rect`` which will crop the camera's output to this area on screen.
            Unlike the viewport this has no influence on the visuals rendered with
            the camera only the area shown.
        render_target:
            The FrameBuffer that the camera may use. Warning if the target isn't the screen
            it won't automatically show up on screen.
        window:
            The Arcade Window to bind the camera to. Defaults to the currently active window.
    """

    def __init__(
        self,
        viewport: Rect | None = None,
        position: Point2 | None = None,
        up: tuple[float, float] = (0.0, 1.0),
        zoom: float = 1.0,
        projection: Rect | None = None,
        near: float = DEFAULT_NEAR_ORTHO,
        far: float = DEFAULT_FAR,
        *,
        scissor: Rect | None = None,
        render_target: Framebuffer | None = None,
        window: Window | None = None,
    ):
        self._window: Window = window or get_window()
        self.render_target: Framebuffer | None = render_target
        """
        An optional framebuffer to activate at the same time as
        the projection data, could be the screen, or an offscreen texture
        """

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
        """
        A rect which describes how the final projection should be mapped
        from unit-space. defaults to the size of the render_target or window
        """

        self.scissor: Rect | None = scissor
        """
        An optional rect which describes what pixels of the active render
        target should be drawn to when undefined the viewport rect is used.
        """

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

        Args:
            camera_data:
                A :py:class:`~arcade.camera.data.CameraData`
                describing the position, up, forward and zoom.
            projection_data:
                A :py:class:`~arcade.camera.data.OrthographicProjectionData`
                which describes the left, right, top, bottom, far, near
                planes and the viewport for an orthographic projection.
            render_target:
                A non-screen :py:class:`~arcade.gl.framebuffer.Framebuffer` for this
                camera to draw into. When specified,

                * nothing will draw directly to the screen
                * the buffer's internal viewport will be ignored

            viewport:
                A viewport as a :py:class:`~arcade.types.rect.Rect`.
                This overrides any viewport the ``render_target`` may have.
            scissor:
                The OpenGL scissor box to use when drawing.
            window: The Arcade Window to bind the camera to.
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
        Returns:
            A 3D vector in world space (same as sprites).
            perfect for finding if the mouse overlaps with a sprite or ui element irrespective
            of the camera.
        """

        _projection = generate_orthographic_matrix(self.projection_data, self.zoom)
        _view = generate_view_matrix(self.view_data)
        return unproject_orthographic(screen_coordinate, self.viewport.viewport, _view, _projection)

    def equalise(self) -> None:
        """
        Forces the projection to match the size of the viewport.
        When matching the projection to the viewport the method keeps
        the projections center in the same relative place.
        """
        x, y = self._projection_data.rect.x, self._projection_data.rect.y
        self._projection_data.rect = XYWH(x, y, self.viewport_width, self.viewport_height)

    def match_window(
        self,
        viewport: bool = True,
        projection: bool = True,
        scissor: bool = True,
        position: bool = False,
        aspect: float | None = None,
    ) -> None:
        """
        Sets the viewport to the size of the window.
        Should be called when the window is resized.

        Args:
            and_projection: Flag whether to also equalize the projection to the viewport.
                On by default
            and_scissor: Flag whether to also equalize the scissor box to the viewport.
                On by default
            and_position: Flag whether to also center the camera to the viewport.
                Off by default
            aspect_ratio: The ratio between width and height that the viewport should
                be constrained to. If unset then the viewport just matches the window
                size. The aspect ratio describes how much larger the width should be
                compared to the height. i.e. for an aspect ratio of ``4:3`` you should
                input ``4.0/3.0`` or ``1.33333...``. Cannot be equal to zero.
        """
        self.update_values(
            self._window.rect,
            viewport=viewport,
            projection=projection,
            scissor=scissor,
            position=position,
            aspect=aspect,
        )

    def match_target(
        self,
        viewport: bool = True,
        projection: bool = True,
        scissor: bool = True,
        position: bool = False,
        aspect: float | None = None,
    ) -> None:
        """
        Sets the viewport to the size of the Camera2D's render target.

        Args:
            viewport: Flag whether to equalise the viewport to the area of the render target
            projection: Flag whether to equalise the size of the projection to
                match the render target
            The projection center stays fixed, and the new projection matches only in size.
            scissor: Flag whether to update the scissor value.
            position: Flag whether to also center the camera to the value.
                Off by default
            aspect_ratio: The ratio between width and height that the value should
                be constrained to. i.e. for an aspect ratio of ``4:3`` you should
                input ``4.0/3.0`` or ``1.33333...``. Cannot be equal to zero.
                If unset then the value will not be updated.
        Raises:
            ValueError: Will be raised if the Camera2D was has no render target.
        """
        if self.render_target is None:
            raise ValueError(
                "Tried to match a non-exsistant render target. Please use `match_window` instead"
            )

        self.update_values(
            LRBT(*self.render_target.viewport),
            viewport,
            projection,
            scissor,
            position,
            aspect=aspect,
        )

    def update_values(
        self,
        value: Rect,
        viewport: bool = True,
        projection: bool = True,
        scissor: bool = True,
        position: bool = False,
        aspect: float | None = None,
    ):
        """
        Convienence method for updating the viewport, projection, position
        and a few others with the same value.

        Args:
            value: The rect that the values will be derived from.
            viewport: Flag whether to equalise the viewport to the value.
            projection: Flag whether to equalise the size of the projection to match the value.
            The projection center stays fixed, and the new projection matches only in size.
            scissor: Flag whether to update the scissor value.
            position: Flag whether to also center the camera to the value.
                Off by default
            aspect_ratio: The ratio between width and height that the value should
                be constrained to. i.e. for an aspect ratio of ``4:3`` you should
                input ``4.0/3.0`` or ``1.33333...``. Cannot be equal to zero.
                If unset then the value will not be updated.
        """
        if aspect is not None:
            if value.height * aspect < value.width:
                w = value.height * aspect
                h = value.height
            else:
                w = value.width
                h = value.width / aspect
            value = XYWH(value.x, value.y, w, h)

        if viewport:
            self.viewport = value

        if projection:
            x, y = self._projection_data.rect.x, self._projection_data.rect.y
            self._projection_data.rect = XYWH(x, y, value.width, value.height)

        if scissor and self.scissor:
            self.scissor = value

        if position:
            self.position = value.center

    def aabb(self) -> Rect:
        """
        Retrieve the axis-aligned bounds box of the camera's view area.
        If the camera isn't rotated , this will be precisely the view area,
        but it will cover a larger area when it is rotated. Useful for CPU culling
        """
        up = self._camera_data.up
        ux, uy, *_ = up
        rx, ry = uy, -ux  # up x Z'

        l, r, b, t = self.viewport.lrbt
        x, y = self.position

        x_points = (
            x + ux * t + rx * l,  # top left
            x + ux * t + rx * r,  # top right
            x + ux * b + rx * l,  # bottom left
            x + ux * b + rx * r,  # bottom right
        )
        y_points = (
            y + uy * t + ry * l,  # top left
            y + uy * t + ry * r,  # top right
            y + uy * b + ry * l,  # bottom left
            y + uy * b + ry * r,  # bottom right
        )

        left = min(x_points)
        right = max(x_points)
        bottom = min(y_points)
        top = max(y_points)
        return LRBT(left=left, right=right, bottom=bottom, top=top)

    def point_in_view(self, point: Point2) -> bool:
        # TODO test
        """
        Take a 2D point in the world, and return whether the point is inside the
        visible area of the camera.
        """
        # This is unwrapped from standard Vec2 operations,
        # The construction and garbage collection of the vectors would
        # increase this method's cost by ~4x

        pos = self.position
        diff = point[0] - pos[0], point[1] - pos[1]

        up = self._camera_data.up

        h_width = self.width / 2.0
        h_height = self.height / 2.0

        dot_x = up[1] * diff[0] - up[0] * diff[1]
        dot_y = up[0] * diff[0] + up[1] * diff[1]

        return abs(dot_x) <= h_width and abs(dot_y) <= h_height

    @property
    def view_data(self) -> CameraData:
        """The view data for the camera.

        This includes:

        * the position
        * forward vector
        * up direction
        * zoom.

        Camera controllers use this property.
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

    @property
    def projection(self) -> Rect:
        """Get/set the left, right, bottom, and top projection values.

        These are world space values which control how the camera
        projects the world onto the pixel space of the current
        viewport area.

        .. note:: this IS scaled by zoom.
                  If this isn't what you want,
                  you have to calculate the value manually from projection_data

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

        .. note:: this IS scaled by zoom.
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

        .. note:: this IS scaled by zoom.
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

        .. note:: this IS scaled by zoom.
                  If this isn't what you want,
                  you have to calculate the value manually from projection_data
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

        .. note:: this IS scaled by zoom.
                  If this isn't what you want,
                  you have to calculate the value manually from projection_data
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

        .. note:: this IS scaled by zoom.
                  If this isn't what you want,
                  you have to calculate the value manually from projection_data
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

        .. note:: this IS scaled by zoom.
                  If this isn't what you want,
                  you have to calculate the value manually from projection_data
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

        .. note:: this IS NOT scaled by zoom.
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

        .. note:: this IS NOT scaled by zoom.
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
        """
        Set the left most pixel drawn to.
        This moves the position of the viewport, and does not change the size.
        """
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
        Set the right most pixel drawn to.
        This moves the position of the viewport, and does not change the size.
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
        Set the bottom most pixel drawn to.
        This moves the position of the viewport, and does not change the size.
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
        Set the top most pixel drawn to.
        This moves the position of the viewport, and does not change the size.
        """
        self.viewport = self.viewport.align_top(new_top)

    @property
    def up(self) -> Vec2:
        """
        A 2D vector which describes what is mapped
        to the +Y direction on screen.
        This is equivalent to rotating the screen.
        The base vector is 3D, but this
        camera only provides a 2D view.
        """
        return Vec2(self._camera_data.up[0], self._camera_data.up[1])

    @up.setter
    def up(self, _up: Point2) -> None:
        """
        Set the 2D vector which describes what is
        mapped to the +Y direction on screen.
        This is equivalent to rotating the screen.
        The base vector is 3D, but this
        camera only provides a 2D view.

        .. warning:: This is assumed to be normalized (length 1.0)
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
        # We rotate counter clockwise by 90 degrees because we want 0 deg to be directly up
        angle = degrees(atan2(self._camera_data.up[1], self._camera_data.up[0])) - 90.0
        if angle <= 0.0:
            angle += 360.0
        return 360 - angle

    @angle.setter
    def angle(self, value: float) -> None:
        """
        Set the 2D UP vector using an angle.
        This starts with 0 degrees as [0, 1]
        rotating clock-wise.
        """
        _r = radians(90.0 - value)
        # Note that this is flipped as we want 0 degrees to be vert.
        self._camera_data.up = (cos(_r), sin(_r), 0.0)

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

    # top_left
    @property
    def top_left(self) -> Vec2:
        """Get the top left most corner the camera can see"""
        pos = self.position
        ux, uy, *_ = self._camera_data.up
        rx, ry = uy, -ux

        top = self.top
        left = self.left

        return Vec2(pos.x + ux * top + rx * left, pos.y + uy * top + ry * left)

    @top_left.setter
    def top_left(self, new_corner: Point2):
        ux, uy, *_ = self._camera_data.up
        rx, ry = uy, -ux

        top = self.top
        left = self.left

        x, y = new_corner
        self.position = (x - ux * top - rx * left, y - uy * top - ry * left)

    # top_center
    @property
    def top_center(self) -> Vec2:
        """Get the top most position the camera can see"""
        pos = self.position

        ux, uy, *_ = self._camera_data.up
        top = self.top
        return Vec2(pos.x + ux * top, pos.y + uy * top)

    @top_center.setter
    def top_center(self, new_top: Point2):
        ux, uy, *_ = self._camera_data.up
        top = self.top

        x, y = new_top
        self.position = x - ux * top, y - uy * top

    # top_right
    @property
    def top_right(self) -> Vec2:
        """Get the top right most corner the camera can see"""
        pos = self.position
        ux, uy, *_ = self._camera_data.up
        rx, ry = uy, -ux

        top = self.top
        right = self.right

        return Vec2(pos.x + ux * top + rx * right, pos.y + uy * top + ry * right)

    @top_right.setter
    def top_right(self, new_corner: Point2):
        ux, uy, *_ = self._camera_data.up
        rx, ry = uy, -ux

        top = self.top
        right = self.right

        x, y = new_corner
        self.position = (x - ux * top - rx * right, y - uy * top - ry * right)

    # center_right
    @property
    def center_right(self) -> Vec2:
        """Get the right most point the camera can see"""
        pos = self.position
        ux, uy, *_ = self._camera_data.up
        right = self.right
        return Vec2(pos.x + uy * right, pos.y - ux * right)

    @center_right.setter
    def center_right(self, new_right: Point2):
        ux, uy, *_ = self._camera_data.up
        right = self.right

        x, y = new_right
        self.position = x - uy * right, y + ux * right

    # bottom_right
    @property
    def bottom_right(self) -> Vec2:
        """Get the bottom right most corner the camera can see"""
        pos = self.position
        ux, uy, *_ = self._camera_data.up
        rx, ry = uy, -ux

        bottom = self.bottom
        right = self.right
        return Vec2(pos.x + ux * bottom + rx * right, pos.y + uy * bottom + ry * right)

    @bottom_right.setter
    def bottom_right(self, new_corner: Point2):
        ux, uy, *_ = self._camera_data.up
        rx, ry = uy, -ux

        bottom = self.bottom
        right = self.right

        x, y = new_corner
        self.position = (
            x - ux * bottom - rx * right,
            y - uy * bottom - ry * right,
        )

    # bottom_center
    @property
    def bottom_center(self) -> Vec2:
        """Get the bottom most position the camera can see"""
        pos = self.position
        ux, uy, *_ = self._camera_data.up
        bottom = self.bottom

        return Vec2(pos.x + ux * bottom, pos.y + uy * bottom)

    @bottom_center.setter
    def bottom_center(self, new_bottom: Point2):
        ux, uy, *_ = self._camera_data.up
        bottom = self.bottom

        x, y = new_bottom
        self.position = x - ux * bottom, y - uy * bottom

    # bottom_left
    @property
    def bottom_left(self) -> Vec2:
        """Get the bottom left most corner the camera can see"""
        pos = self.position
        ux, uy, *_ = self._camera_data.up
        rx, ry = uy, -ux

        bottom = self.bottom
        left = self.left

        return Vec2(pos.x + ux * bottom + rx * left, pos.y + uy * bottom + ry * left)

    @bottom_left.setter
    def bottom_left(self, new_corner: Point2):
        ux, uy, *_ = self._camera_data.up
        rx, ry = uy, -ux

        bottom = self.bottom
        left = self.left

        x, y = new_corner
        self.position = (x - ux * bottom - rx * left, y - uy * bottom - ry * left)

    # center_left
    @property
    def center_left(self) -> Vec2:
        """Get the left most point the camera can see"""
        pos = self.position
        ux, uy, *_ = self._camera_data.up
        left = self.left
        return Vec2(pos.x + uy * left, pos.y - ux * left)

    @center_left.setter
    def center_left(self, new_left: Point2):
        ux, uy, *_ = self._camera_data.up
        left = self.left

        x, y = new_left
        self.position = x - uy * left, y + ux * left
