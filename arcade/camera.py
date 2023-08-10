"""
Camera class
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

from pyglet.math import Mat4, Vec2, Vec3

import arcade
from arcade.types import Point
from arcade.math import get_distance

if TYPE_CHECKING:
    from arcade import Sprite, SpriteList

# type aliases
FourIntTuple = Tuple[int, int, int, int]
FourFloatTuple = Tuple[float, float, float, float]

__all__ = [
    "SimpleCamera",
    "Camera"
]


class SimpleCamera:
    """
    A simple camera that allows to change the viewport, the projection and can move around.
    That's it.
    See arcade.Camera for more advance stuff.

    :param viewport: Size of the viewport: (left, bottom, width, height)
    :param projection: Space to allocate in the viewport of the camera (left, right, bottom, top)
    """
    def __init__(
        self,
        *,
        viewport: Optional[FourIntTuple] = None,
        projection: Optional[FourFloatTuple] = None,
        window: Optional["arcade.Window"] = None,
    ) -> None:
        # Reference to Context, used to update projection matrix
        self._window: "arcade.Window" = window or arcade.get_window()

        # store the viewport and projection tuples
        # viewport is the space the camera will hold on the screen (left, bottom, width, height)
        self._viewport: FourIntTuple = viewport or (0, 0, self._window.width, self._window.height)

        # projection is what you want to project into the camera viewport (left, right, bottom, top)
        self._projection: FourFloatTuple = projection or (0, self._window.width,
                                                          0, self._window.height)
        if viewport is not None and projection is None:
            # if viewport is provided but projection is not, projection
            # will match the provided viewport
            self._projection = (viewport[0], viewport[2], viewport[1], viewport[3])

        # Matrices

        # Projection Matrix is used to apply the camera viewport size
        self._projection_matrix: Mat4 = Mat4()
        # View Matrix is what the camera is looking at(position)
        self._view_matrix: Mat4 = Mat4()
        # We multiply projection and view matrices to get combined,
        #  this is what actually gets sent to GL context
        self._combined_matrix: Mat4 = Mat4()

        # Position
        self.position: Vec2 = Vec2(0, 0)

        # Camera movement
        self.goal_position: Vec2 = Vec2(0, 0)
        self.move_speed: float = 1.0  # 1.0 is instant
        self.moving: bool = False

        # Init matrixes
        # This will pre-compute the projection, view and combined matrixes
        self._set_projection_matrix(update_combined_matrix=False)
        self._set_view_matrix()

    @property
    def viewport_width(self) -> int:
        """ Returns the width of the viewport """
        return self._viewport[2]

    @property
    def viewport_height(self) -> int:
        """ Returns the height of the viewport """
        return self._viewport[3]

    @property
    def viewport(self) -> FourIntTuple:
        """ The space the camera will hold on the screen (left, bottom, width, height) """
        return self._viewport

    @viewport.setter
    def viewport(self, viewport: FourIntTuple) -> None:
        """ Sets the viewport """
        self.set_viewport(viewport)

    def set_viewport(self, viewport: FourIntTuple) -> None:
        """ Sets the viewport """
        self._viewport = viewport or (0, 0, self._window.width, self._window.height)

        # the viewport affects the view matrix
        self._set_view_matrix()

    @property
    def projection(self) -> FourFloatTuple:
        """
        The dimensions of the space to project in the camera viewport (left, right, bottom, top).
        The projection is what you want to project into the camera viewport.
        """
        return self._projection

    @projection.setter
    def projection(self, new_projection: FourFloatTuple) -> None:
        """
        Update the projection of the camera. This also updates the projection matrix with an orthogonal
        projection based on the projection size of the camera and the zoom applied.
        """
        self._projection = new_projection or (0, self._window.width, 0, self._window.height)
        self._set_projection_matrix()

    @property
    def viewport_to_projection_width_ratio(self):
        """ The ratio of viewport width to projection width """
        return self.viewport_width / (self._projection[1] - self._projection[0])

    @property
    def viewport_to_projection_height_ratio(self):
        """ The ratio of viewport height to projection height """
        return self.viewport_height / (self._projection[3] - self._projection[2])

    @property
    def projection_to_viewport_width_ratio(self):
        """ The ratio of projection width to viewport width """
        return (self._projection[1] - self._projection[0]) / self.viewport_width

    @property
    def projection_to_viewport_height_ratio(self):
        """ The ratio of projection height to viewport height """
        return (self._projection[3] - self._projection[2]) / self.viewport_height

    def _set_projection_matrix(self, *, update_combined_matrix: bool = True) -> None:
        """
        Helper method. This will just pre-compute the projection and combined matrix

        :param bool update_combined_matrix: if True will also update the combined matrix (projection @ view)
        """
        self._projection_matrix = Mat4.orthogonal_projection(*self._projection, -100, 100)
        if update_combined_matrix:
            self._set_combined_matrix()

    def _set_view_matrix(self, *, update_combined_matrix: bool = True) -> None:
        """
        Helper method. This will just pre-compute the view and combined matrix

        :param bool update_combined_matrix: if True will also update the combined matrix (projection @ view)
        """

        # Figure out our 'real' position
        result_position = Vec3(
            (self.position[0] / (self.viewport_width / 2)),
            (self.position[1] / (self.viewport_height / 2)),
            0
        )
        self._view_matrix = ~(Mat4.from_translation(result_position))
        if update_combined_matrix:
            self._set_combined_matrix()

    def _set_combined_matrix(self) -> None:
        """ Helper method. This will just pre-compute the combined matrix"""
        self._combined_matrix = self._view_matrix @ self._projection_matrix

    def move_to(self, vector: Union[Vec2, tuple], speed: float = 1.0) -> None:
        """
        Sets the goal position of the camera.

        The camera will lerp towards this position based on the provided speed,
        updating its position every time the use() function is called.

        :param Vec2 vector: Vector to move the camera towards.
        :param Vec2 speed: How fast to move the camera, 1.0 is instant, 0.1 moves slowly
        """
        self.goal_position = Vec2(*vector)
        self.move_speed = speed
        self.moving = True

    def move(self, vector: Union[Vec2, tuple]) -> None:
        """
        Moves the camera with a speed of 1.0, aka instant move

        This is equivalent to calling move_to(my_pos, 1.0)
        """
        self.move_to(vector, 1.0)

    def center(self, vector: Union[Vec2, tuple], speed: float = 1.0) -> None:
        """
        Centers the camera on coordinates
        """
        if not isinstance(vector, Vec2):
            vector2: Vec2 = Vec2(*vector)
        else:
            vector2 = vector

        # get the center of the camera viewport
        center = Vec2(self.viewport_width, self.viewport_height) / 2

        # adjust vector to projection ratio
        vector2 = Vec2(vector2.x * self.viewport_to_projection_width_ratio,
                       vector2.y * self.viewport_to_projection_height_ratio)

        # move to the vector subtracting the center
        target = (vector2 - center)

        self.move_to(target, speed)

    def get_map_coordinates(self, camera_vector: Union[Vec2, tuple]) -> Vec2:
        """
        Returns map coordinates in pixels from screen coordinates based on the camera position

        :param Vec2 camera_vector: Vector captured from the camera viewport
        """
        return Vec2(*self.position) + Vec2(*camera_vector)

    def resize(self, viewport_width: int, viewport_height: int, *,
               resize_projection: bool = True) -> None:
        """
        Resize the camera's viewport. Call this when the window resizes.

        :param int viewport_width: Width of the viewport
        :param int viewport_height: Height of the viewport
        :param bool resize_projection: if True the projection will also be resized
        """
        new_viewport = (self._viewport[0], self._viewport[1], viewport_width, viewport_height)
        self.set_viewport(new_viewport)
        if resize_projection:
            self.projection = (self._projection[0], viewport_width,
                               self._projection[2], viewport_height)

    def update(self):
        """
        Update the camera's viewport to the current settings.
        """
        if self.moving:
            # Apply Goal Position
            self.position = self.position.lerp(self.goal_position, self.move_speed)
            if self.position == self.goal_position:
                self.moving = False
            self._set_view_matrix()  # this will also set the combined matrix

    def use(self) -> None:
        """
        Select this camera for use. Do this right before you draw.
        """
        self._window.current_camera = self

        # update camera position and calculate matrix values if needed
        self.update()

        # set Viewport / projection
        self._window.ctx.viewport = self._viewport  # sets viewport of the camera
        self._window.projection = self._combined_matrix  # sets projection position and zoom
        self._window.view = Mat4()  # Set to identity matrix for now


class Camera(SimpleCamera):
    """
    The Camera class is used for controlling the visible viewport, the projection, zoom and rotation.
    It is very useful for separating a scrolling screen of sprites, and a GUI overlay.
    For an example of this in action, see :ref:`sprite_move_scrolling`.

    :param tuple viewport: (left, bottom, width, height) size of the viewport. If None the window size will be used.
    :param tuple projection: (left, right, bottom, top) size of the projection. If None the window size will be used.
    :param float zoom: the zoom to apply to the projection
    :param float rotation: the angle in degrees to rotate the projection
    :param tuple anchor: the x, y point where the camera rotation will anchor. Default is the center of the viewport.
    :param Window window: Window to associate with this camera, if working with a multi-window program.
    """
    def __init__(
        self, *,
        viewport: Optional[FourIntTuple] = None,
        projection: Optional[FourFloatTuple] = None,
        zoom: float = 1.0,
        rotation: float = 0.0,
        anchor: Optional[Tuple[float, float]] = None,
        window: Optional["arcade.Window"] = None,
    ):
        # scale and zoom
        # zoom it's just x scale value. Setting zoom will set scale x, y to the same value
        self._scale: Tuple[float, float] = (zoom, zoom)

        # Near and Far
        self._near: int = -1
        self._far: int = 1

        # Shake
        self.shake_velocity: Vec2 = Vec2()
        self.shake_offset: Vec2 = Vec2()
        self.shake_speed: float = 0.0
        self.shake_damping: float = 0.0
        self.shaking: bool = False

        # Call init from superclass here, previous attributes are needed before this call
        super().__init__(viewport=viewport, projection=projection, window=window)

        # Rotation
        self._rotation: float = rotation  # in degrees
        self._anchor: Optional[Tuple[float, float]] = anchor  # (x, y) to anchor the camera rotation

        # Matrixes
        # Rotation matrix holds the matrix used to compute the
        #  rotation set in window.ctx.view_matrix_2d
        self._rotation_matrix: Mat4 = Mat4()

        # Init matrixes
        # This will pre-compute the rotation matrix
        self._set_rotation_matrix()

    def set_viewport(self, viewport: FourIntTuple) -> None:
        """ Sets the viewport """
        super().set_viewport(viewport)

        # the viewport affects the rotation matrix if the rotation anchor is not set
        if self._anchor is None:
            self._set_rotation_matrix()

    def _set_projection_matrix(self, *, update_combined_matrix: bool = True) -> None:
        """
        Helper method. This will just pre-compute the projection and combined matrix

        :param bool update_combined_matrix: if True will also update the combined matrix (projection @ view)
        """
        # apply zoom
        left, right, bottom, top = self._projection
        if self._scale != (1.0, 1.0):
            right *= self._scale[0]  # x axis scale
            top *= self._scale[1]  # y axis scale

        self._projection_matrix = Mat4.orthogonal_projection(left, right, bottom, top, self._near,
                                                             self._far)
        if update_combined_matrix:
            self._set_combined_matrix()

    def _set_view_matrix(self, *, update_combined_matrix: bool = True) -> None:
        """
        Helper method. This will just pre-compute the view and combined matrix
        :param bool update_combined_matrix: if True will also update the combined matrix (projection @ view)
        """

        # Figure out our 'real' position plus the shake
        result_position = self.position + self.shake_offset
        result_position = Vec3(
            (result_position[0] / ((self.viewport_width * self._scale[0]) / 2)),
            (result_position[1] / ((self.viewport_height * self._scale[1]) / 2)),
            0
        )
        self._view_matrix = ~(Mat4.from_translation(result_position) @ Mat4().scale(
            Vec3(self._scale[0], self._scale[1], 1.0)))
        if update_combined_matrix:
            self._set_combined_matrix()

    def _set_rotation_matrix(self) -> None:
        """ Helper method that computes the rotation_matrix every time is needed """
        rotate = Mat4.from_rotation(math.radians(self._rotation), Vec3(0, 0, 1))

        # If no anchor is set, use the center of the screen
        if self._anchor is None:
            offset = Vec3(self.position.x, self.position.y, 0)
            offset += Vec3(self.viewport_width / 2, self.viewport_height / 2, 0)
        else:
            offset = Vec3(self._anchor[0], self._anchor[1], 0)

        translate_pre = Mat4.from_translation(offset)
        translate_post = Mat4.from_translation(-offset)

        self._rotation_matrix = translate_post @ rotate @ translate_pre

    @property
    def scale(self) -> Tuple[float, float]:
        """
        Returns the x, y scale.
        """
        return self._scale

    @scale.setter
    def scale(self, new_scale: Tuple[float, float]) -> None:
        """
        Sets the x, y scale (zoom property just sets scale to the same value).
        This also updates the projection matrix with an orthogonal
        projection based on the projection size of the camera and the zoom applied.
        """
        if new_scale[0] <= 0 or new_scale[1] <= 0:
            raise ValueError("Scale must be greater than zero")

        self._scale = (float(new_scale[0]), float(new_scale[1]))

        # Changing the scale (zoom) affects both projection_matrix and view_matrix
        self._set_projection_matrix(
            update_combined_matrix=False)  # combined matrix will be set in the next call
        self._set_view_matrix()

    @property
    def zoom(self) -> float:
        """ The zoom applied to the projection. Just returns the x scale value. """
        return self._scale[0]

    @zoom.setter
    def zoom(self, zoom: float) -> None:
        """ Apply a zoom to the projection """
        self.scale = zoom, zoom

    @property
    def near(self) -> int:
        """ The near applied to the projection"""
        return self._near

    @near.setter
    def near(self, near: int) -> None:
        """
        Update the near of the camera. This also updates the projection matrix with an orthogonal
        projection based on the projection size of the camera and the zoom applied.
        """
        self._near = near
        self._set_projection_matrix()

    @property
    def far(self) -> int:
        """ The far applied to the projection"""
        return self._far

    @far.setter
    def far(self, far: int) -> None:
        """
        Update the far of the camera. This also updates the projection matrix with an orthogonal
        projection based on the projection size of the camera and the zoom applied.
        """
        self._far = far
        self._set_projection_matrix()

    @property
    def rotation(self) -> float:
        """
        Get or set the rotation in degrees.

        This will rotate the camera clockwise meaning
        the contents will rotate counter-clockwise.
        """
        return self._rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        self._rotation = value
        self._set_rotation_matrix()

    @property
    def anchor(self) -> Optional[Tuple[float, float]]:
        """
        Get or set the rotation anchor for the camera.

        By default, the anchor is the center of the screen
        and the anchor value is `None`. Assigning a custom
        anchor point will override this behavior.
        The anchor point is in world / global coordinates.

        Example::

            # Set the anchor to the center of the world
            camera.anchor = 0, 0
            # Set the anchor to the center of the player
            camera.anchor = player.position
        """
        return self._anchor

    @anchor.setter
    def anchor(self, anchor: Optional[Tuple[float, float]]) -> None:
        if anchor is None:
            self._anchor = None
        else:
            self._anchor = anchor[0], anchor[1]
        self._set_rotation_matrix()

    def update(self) -> None:
        """
        Update the camera's viewport to the current settings.
        """
        update_view_matrix = False

        if self.moving:
            # Apply Goal Position
            self.position = self.position.lerp(self.goal_position, self.move_speed)
            if self.position == self.goal_position:
                self.moving = False
            update_view_matrix = True

        if self.shaking:
            # Apply Camera Shake

            # Move our offset based on shake velocity
            self.shake_offset += self.shake_velocity

            # Get x and ys
            vx = self.shake_velocity[0]
            vy = self.shake_velocity[1]

            ox = self.shake_offset[0]
            oy = self.shake_offset[1]

            # Calculate the angle our offset is at, and how far out
            angle = math.atan2(ox, oy)
            distance = get_distance(0, 0, ox, oy)
            velocity_mag = get_distance(0, 0, vx, vy)

            # Ok, what's the reverse? Pull it back in.
            reverse_speed = min(self.shake_speed, distance)
            opposite_angle = angle + math.pi
            opposite_vector = Vec2(
                math.sin(opposite_angle) * reverse_speed,
                math.cos(opposite_angle) * reverse_speed,
            )

            # Shaking almost done? Zero it out
            if velocity_mag < self.shake_speed and distance < self.shake_speed:
                self.shake_velocity = Vec2(0, 0)
                self.shake_offset = Vec2(0, 0)
                self.shaking = False

            # Come up with a new velocity, pulled by opposite vector and damped
            self.shake_velocity += opposite_vector
            self.shake_velocity *= self.shake_damping

            update_view_matrix = True

        if update_view_matrix:
            self._set_view_matrix()  # this will also set the combined matrix

    def shake(self, velocity: Union[Vec2, tuple], speed: float = 1.5, damping: float = 0.9) -> None:
        """
        Add a camera shake.

        :param Vec2 velocity: Vector to start moving the camera
        :param float speed: How fast to shake
        :param float damping: How fast to stop shaking
        """
        if not isinstance(velocity, Vec2):
            velocity = Vec2(*velocity)

        self.shake_velocity += velocity
        self.shake_speed = speed
        self.shake_damping = damping
        self.shaking = True

    def use(self) -> None:
        """
        Select this camera for use. Do this right before you draw.
        """
        super().use()  # call SimpleCamera.use()

        # set rotation matrix
        self._window.ctx.view_matrix_2d = self._rotation_matrix  # sets rotation and rotation anchor

    def get_sprites_at_point(self, point: "Point", sprite_list: "SpriteList") -> List["Sprite"]:
        """
        Get a list of sprites at a particular point when
        This function sees if any sprite overlaps
        the specified point. If a sprite has a different center_x/center_y but touches the point,
        this will return that sprite.

        :param Point point: Point to check
        :param SpriteList sprite_list: SpriteList to check against

        :returns: List of sprites colliding, or an empty list.
        :rtype: list
        """
        raise NotImplementedError()
