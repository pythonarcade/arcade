import math
from math import sin, cos, radians
from typing import (
    Any,
    Tuple,
    Iterable,
    Dict,
    List,
    Optional,
    TYPE_CHECKING,
)
from pathlib import Path

import arcade
from arcade.geometry_generic import get_angle_degrees
from arcade import (
    load_texture,
    Texture,
)
from arcade.color import BLACK
from arcade.types import Color, RGBA, Point, PointList, PathOrTexture

if TYPE_CHECKING:  # handle import cycle caused by type hinting
    from arcade.sprite_list import SpriteList


class PyMunk:
    """Object used to hold pymunk info for a sprite."""
    __slots__ = (
        "damping",
        "gravity",
        "max_velocity",
        "max_horizontal_velocity",
        "max_vertical_velocity",
    )

    def __init__(self):
        """Set up pymunk object"""
        self.damping = None
        self.gravity = None
        self.max_velocity = None
        self.max_horizontal_velocity = None
        self.max_vertical_velocity = None


class Sprite:
    """
    Class that represents a 'sprite' on-screen. Most games center around sprites.
    For examples on how to use this class, see:
    https://api.arcade.academy/en/latest/examples/index.html#sprites

    :param str path_or_texture: Path to the image file, or a texture object.
    :param float center_x: Location of the sprite
    :param float center_y: Location of the sprite
    :param float scale: Scale the image up or down. Scale of 1.0 is none.
    :param float angle: The initial rotation of the sprite in degrees
    """
    def __init__(
        self,
        path_or_texture: PathOrTexture = None,
        scale: float = 1.0,
        center_x: float = 0.0,
        center_y: float = 0.0,
        angle: float = 0.0,
        **kwargs,
    ):
        """ Constructor """
        # Position, size and orientation properties
        self._width: float = 0.0
        self._height: float = 0.0
        self._depth: float = 0.0
        self._scale: Tuple[float, float] = scale, scale
        self._position: Point = center_x, center_y
        self._angle = angle
        self._velocity = 0.0, 0.0
        self.change_angle: float = 0.0

        # Hit box and collision property
        self._points: Optional[PointList] = None
        self._point_list_cache: Optional[PointList] = None

        # Color
        self._color: RGBA = 255, 255, 255, 255

        # Custom sprite properties
        self._properties: Optional[Dict[str, Any]] = None

        # Boundaries for moving platforms in tilemaps
        self.boundary_left: Optional[float] = None
        self.boundary_right: Optional[float] = None
        self.boundary_top: Optional[float] = None
        self.boundary_bottom: Optional[float] = None

        # Texture properties
        self._texture: Optional[Texture] = None
        self.textures: List[Texture] = []
        self.cur_texture_index: int = 0

        self.sprite_lists: List["SpriteList"] = []
        self.physics_engines: List[Any] = []
        self._sprite_list: Optional["SpriteList"] = None

        # Pymunk specific properties
        self._pymunk: Optional[PyMunk] = None
        self.force = [0.0, 0.0]

        # Debug properties
        self.guid: Optional[str] = None

        if isinstance(path_or_texture, Texture):
            self._texture = path_or_texture
        elif isinstance(path_or_texture, (str, Path)):
            self._texture = load_texture(path_or_texture)

        if self._texture:
            self.textures = [self._texture]
            self._width = self._texture.width * scale
            self._height = self._texture.height * scale
            if not self._points:
                self._points = self._texture.hit_box_points

    @property
    def properties(self) -> Dict[str, Any]:
        """
        Get or set custom sprite properties.

        :rtype: Dict[str, Any]
        """
        if self._properties is None:
            self._properties = {}
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value

    @property
    def pymunk(self) -> PyMunk:
        """
        Get or set the Pymunk property objects.
        This is used by the pymunk physics engine.
        """
        if self._pymunk is None:
            self._pymunk = PyMunk()
        return self._pymunk

    @pymunk.setter
    def pymunk(self, value):
        self._pymunk = value

    def append_texture(self, texture: Texture):
        """
        Appends a new texture to the list of textures that can be
        applied to this sprite.

        :param arcade.Texture texture: Texture to add to the list of available textures

        """
        self.textures.append(texture)

    @property
    def position(self) -> Point:
        """
        Get the center x and y coordinates of the sprite.

        Returns:
            (center_x, center_y)
        """
        return self._position

    @position.setter
    def position(self, new_value: Point):
        """
        Set the center x and y coordinates of the sprite.

        :param Point new_value: New position.
        """
        if new_value == self._position:
            return

        self.clear_spatial_hashes()
        self._point_list_cache = None
        self._position = new_value
        self.add_spatial_hashes()

        for sprite_list in self.sprite_lists:
            sprite_list._update_location(self)

    def set_position(self, center_x: float, center_y: float) -> None:
        """
        Set a sprite's position

        :param float center_x: New x position of sprite
        :param float center_y: New y position of sprite
        """
        self.position = (center_x, center_y)

    def set_hit_box(self, points: PointList) -> None:
        """
        Set a sprite's hit box. Hit box should be relative to a sprite's center,
        and with a scale of 1.0.
        Points will be scaled with get_adjusted_hit_box.
        """
        self._point_list_cache = None
        self._points = points

    def get_hit_box(self) -> PointList:
        """
        Use the hit_box property to get or set a sprite's hit box.
        Hit boxes are specified assuming the sprite's center is at (0, 0).
        Specify hit boxes like:

        .. code-block::

            mySprite.hit_box = [[-10, -10], [10, -10], [10, 10]]

        Specify a hit box unadjusted for translation, rotation, or scale.
        You can get an adjusted hit box with :class:`arcade.Sprite.get_adjusted_hit_box`.
        """
        # Use existing points if we have them
        if self._points is not None:
            return self._points

        # If we don't already have points, try to get them from the texture
        if self._texture:
            self._points = self._texture.hit_box_points
        else:
            raise ValueError("Sprite has no hit box points due to missing texture")

        return self._points

    @property
    def hit_box(self) -> PointList:
        return self.get_hit_box()

    @hit_box.setter
    def hit_box(self, points: PointList):
        self.set_hit_box(points)

    def get_adjusted_hit_box(self) -> PointList:
        """
        Get the points that make up the hit box for the rect that makes up the
        sprite, including rotation and scaling.
        """
        # If we've already calculated the adjusted hit box, use the cached version
        if self._point_list_cache is not None:
            return self._point_list_cache

        rad = radians(self._angle)
        scale_x, scale_y = self._scale
        position_x, position_y = self._position
        rad_cos = cos(rad)
        rad_sin = sin(rad)

        def _adjust_point(point) -> Point:
            x, y = point

            # Apply scaling
            x *= scale_x
            y *= scale_y

            # Rotate the point if needed
            if rad:
                rot_x = x * rad_cos - y * rad_sin
                rot_y = x * rad_sin + y * rad_cos
                x = rot_x
                y = rot_y

            # Apply position
            return (
                x + position_x,
                y + position_y,
            )

        # Cache the results
        self._point_list_cache = tuple([_adjust_point(point) for point in self.hit_box])
        return self._point_list_cache

    def forward(self, speed: float = 1.0) -> None:
        """
        Adjusts a Sprite's movement vector forward.
        This method does not actually move the sprite, just takes the current
        change_x/change_y and adjusts it by the speed given.

        :param speed: speed factor
        """
        self.change_x += math.cos(self.radians) * speed
        self.change_y += math.sin(self.radians) * speed

    def reverse(self, speed: float = 1.0) -> None:
        """
        Adjusts a Sprite's movement vector backwards.
        This method does not actually move the sprite, just takes the current
        change_x/change_y and adjusts it by the speed given.

        :param speed: speed factor
        """
        self.forward(-speed)

    def strafe(self, speed: float = 1.0) -> None:
        """
        Adjusts a Sprite's movement vector sideways.
        This method does not actually move the sprite, just takes the current
        change_x/change_y and adjusts it by the speed given.

        :param speed: speed factor
        """
        self.change_x += -math.sin(self.radians) * speed
        self.change_y += math.cos(self.radians) * speed

    def turn_right(self, theta: float = 90.0) -> None:
        """
        Rotate the sprite right by the passed number of degrees.

        :param theta: change in angle, in degrees
        """
        self.angle -= theta

    def turn_left(self, theta: float = 90.0) -> None:
        """
        Rotate the sprite left by the passed number of degrees.

        :param theta: change in angle, in degrees
        """
        self.angle += theta

    def stop(self) -> None:
        """
        Stop the Sprite's motion.
        """
        self.change_x = 0
        self.change_y = 0
        self.change_angle = 0

    def clear_spatial_hashes(self) -> None:
        """
        Search the sprite lists this sprite is a part of, and remove it
        from any spatial hashes it is a part of.
        """
        for sprite_list in self.sprite_lists:
            if sprite_list.spatial_hash is not None:
                try:
                    sprite_list.spatial_hash.remove_object(self)
                except ValueError:
                    print(
                        "Warning, attempt to remove item from spatial hash that doesn't exist in the hash."
                    )

    def add_spatial_hashes(self) -> None:
        """
        Add spatial hashes for this sprite in all the sprite lists it is part of.
        """
        for sprite_list in self.sprite_lists:
            if sprite_list.spatial_hash is not None:
                sprite_list.spatial_hash.insert_object_for_box(self)

    @property
    def bottom(self) -> float:
        """
        Return the y coordinate of the bottom of the sprite.
        """
        points = self.get_adjusted_hit_box()

        # This happens if our point list is empty, such as a completely
        # transparent sprite.
        if len(points) == 0:
            return self.center_y

        y_points = [point[1] for point in points]
        return min(y_points)

    @bottom.setter
    def bottom(self, amount: float):
        """
        Set the location of the sprite based on the bottom y coordinate.
        """
        lowest = self.bottom
        diff = lowest - amount
        self.center_y -= diff

    @property
    def top(self) -> float:
        """
        Return the y coordinate of the top of the sprite.
        """
        points = self.get_adjusted_hit_box()

        # This happens if our point list is empty, such as a completely
        # transparent sprite.
        if len(points) == 0:
            return self.center_y

        y_points = [point[1] for point in points]
        return max(y_points)

    @top.setter
    def top(self, amount: float):
        """The highest y coordinate."""
        highest = self.top
        diff = highest - amount
        self.center_y -= diff

    @property
    def width(self) -> float:
        """Get the width of the sprite."""
        return self._width

    @width.setter
    def width(self, new_value: float):
        """Set the width in pixels of the sprite."""
        if new_value != self._width:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._scale = new_value / self.texture.width, self._scale[1]
            self._width = new_value
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list._update_size(self)

    @property
    def height(self) -> float:
        """Get the height in pixels of the sprite."""
        return self._height

    @height.setter
    def height(self, new_value: float):
        """Set the center x coordinate of the sprite."""
        if new_value != self._height:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._scale = self._scale[0], new_value / self.texture.height
            self._height = new_value
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list._update_height(self)

    @property
    def depth(self) -> float:
        """Get the depth of the sprite."""
        return self._depth

    @depth.setter
    def depth(self, new_value: float):
        """Set the depth of the sprite."""
        if new_value != self._depth:
            self._depth = new_value
            for sprite_list in self.sprite_lists:
                sprite_list._update_depth(self)

    @property
    def scale(self) -> float:
        """
        Get the sprite's x scale value or set both x & y scale to the same value.

        .. note:: Negative values are supported. They will flip &
                  mirror the sprite.
        """
        return self._scale[0]

    @scale.setter
    def scale(self, new_value: float):
        if new_value == self._scale[0] and new_value == self._scale[1]:
            return

        self.clear_spatial_hashes()
        self._point_list_cache = None
        self._scale = new_value, new_value
        if self._texture:
            self._width = self._texture.width * self._scale[0]
            self._height = self._texture.height * self._scale[1]

        self.add_spatial_hashes()

        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    @property
    def scale_xy(self) -> Point:
        """Get or set the x & y scale of the sprite as a pair of values."""
        return self._scale

    @scale_xy.setter
    def scale_xy(self, new_value: Point):
        if new_value[0] == self._scale[0] and new_value[1] == self._scale[1]:
            return

        self.clear_spatial_hashes()
        self._point_list_cache = None
        self._scale = new_value
        if self._texture:
            self._width = self._texture.width * self._scale[0]
            self._height = self._texture.height * self._scale[1]

        self.add_spatial_hashes()

        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    def rescale_relative_to_point(self, point: Point, factor: float) -> None:
        """
        Rescale the sprite and its distance from the passed point.

        This function does two things:

        1. Multiply both values in the sprite's :py:attr:`~scale_xy`
           value by ``factor``.
        2. Scale the distance between the sprite and ``point`` by
           ``factor``.

        If ``point`` equals the sprite's :py:attr:`~position`,
        the distance will be zero and the sprite will not move.

        :param point: The reference point for rescaling.
        :param factor: Multiplier for sprite scale & distance to point.
        :return:
        """
        # abort if the multiplier wouldn't do anything
        if factor == 1.0:
            return

        # clear spatial metadata both locally and in sprite lists
        self.clear_spatial_hashes()
        self._point_list_cache = None

        # set the scale and, if this sprite has a texture, the size data
        self._scale = self._scale[0] * factor, self._scale[1] * factor
        if self._texture:
            self._width = self._texture.width * self._scale[0]
            self._height = self._texture.height * self._scale[1]

        # detect the edge case where distance to multiply is zero
        position_changed = point != self._position

        # be lazy about math; only do it if we have to
        if position_changed:
            self._position = (
                (self._position[0] - point[0]) * factor + point[0],
                (self._position[1] - point[1]) * factor + point[1]
            )

        # rebuild all spatial metadata
        self.add_spatial_hashes()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)
            if position_changed:
                sprite_list._update_location(self)

    def rescale_xy_relative_to_point(
            self,
            point: Point,
            factors_xy: Iterable[float]
    ) -> None:
        """
        Rescale the sprite and its distance from the passed point.

        This method can scale by different amounts on each axis. To
        scale along only one axis, set the other axis to ``1.0`` in
        ``factors_xy``.

        Internally, this function does the following:

        1. Multiply the x & y of the sprite's :py:attr:`~scale_xy`
           attribute by the corresponding part from ``factors_xy``.
        2. Scale the x & y of the difference between the sprite's
           position and ``point`` by the corresponding component from
           ``factors_xy``.

        If ``point`` equals the sprite's :py:attr:`~position`,
        the distance will be zero and the sprite will not move.

        :param point: The reference point for rescaling.
        :param factors_xy: A 2-length iterable containing x and y
                           multipliers for ``scale`` & distance to
                           ``point``.
        :return:
        """
        # exit early if nothing would change
        factor_x, factor_y = factors_xy
        if factor_x == 1.0 and factor_y == 1.0:
            return

        # clear spatial metadata both locally and in sprite lists
        self.clear_spatial_hashes()
        self._point_list_cache = None

        # set the scale and, if this sprite has a texture, the size data
        self._scale = self._scale[0] * factor_x, self._scale[1] * factor_y
        if self._texture:
            self._width = self._texture.width * self._scale[0]
            self._height = self._texture.height * self._scale[1]

        # detect the edge case where the distance to multiply is 0
        position_changed = point != self._position

        # be lazy about math; only do it if we have to
        if position_changed:
            self._position = (
                (self._position[0] - point[0]) * factor_x + point[0],
                (self._position[1] - point[1]) * factor_y + point[1]
            )

        # rebuild all spatial metadata
        self.add_spatial_hashes()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)
            if position_changed:
                sprite_list._update_location(self)

    @property
    def center_x(self) -> float:
        """Get the center x coordinate of the sprite."""
        return self._position[0]

    @center_x.setter
    def center_x(self, new_value: float):
        """Set the center x coordinate of the sprite."""
        if new_value == self._position[0]:
            return

        self.clear_spatial_hashes()
        self._point_list_cache = None
        self._position = (new_value, self._position[1])
        self.add_spatial_hashes()

        for sprite_list in self.sprite_lists:
            sprite_list._update_location(self)

    @property
    def center_y(self) -> float:
        """Get the center y coordinate of the sprite."""
        return self._position[1]

    @center_y.setter
    def center_y(self, new_value: float):
        """Set the center y coordinate of the sprite."""
        if new_value == self._position[1]:
            return

        self.clear_spatial_hashes()
        self._point_list_cache = None
        self._position = (self._position[0], new_value)
        self.add_spatial_hashes()

        for sprite_list in self.sprite_lists:
            sprite_list._update_location(self)

    @property
    def velocity(self) -> Point:
        """
        Get or set the velocity of the sprite.

        The x and y velocity can also be set separately using the
        ``sprite.change_x`` and ``sprite.change_y`` properties.

        Example::

            sprite.velocity = 1.0, 0.0

        Returns:
            Tuple[float, float]
        """
        return self._velocity

    @velocity.setter
    def velocity(self, new_value: Point):
        self._velocity = new_value

    @property
    def change_x(self) -> float:
        """Get the velocity in the x plane of the sprite."""
        return self.velocity[0]

    @change_x.setter
    def change_x(self, new_value: float):
        """Set the velocity in the x plane of the sprite."""
        self._velocity = new_value, self._velocity[1]

    @property
    def change_y(self) -> float:
        """Get the velocity in the y plane of the sprite."""
        return self.velocity[1]

    @change_y.setter
    def change_y(self, new_value: float):
        """Set the velocity in the y plane of the sprite."""
        self._velocity = self._velocity[0], new_value

    @property
    def angle(self) -> float:
        """Get the angle of the sprite's rotation."""
        return self._angle

    @angle.setter
    def angle(self, new_value: float):
        """Set the angle of the sprite's rotation."""
        if new_value == self._angle:
            return

        self.clear_spatial_hashes()
        self._angle = new_value
        self._point_list_cache = None

        for sprite_list in self.sprite_lists:
            sprite_list._update_angle(self)

        self.add_spatial_hashes()

    @property
    def radians(self) -> float:
        """
        Converts the degrees representation of self.angle into radians.
        :return: float
        """
        return self._angle / 180.0 * math.pi

    @radians.setter
    def radians(self, new_value: float):
        """
        Converts a radian value into degrees and stores it into angle.
        """
        self.angle = new_value * 180.0 / math.pi

    @property
    def left(self) -> float:
        """
        Return the x coordinate of the left-side of the sprite's hit box.
        """
        points = self.get_adjusted_hit_box()

        # This happens if our point list is empty, such as a completely
        # transparent sprite.
        if len(points) == 0:
            return self.center_x

        x_points = [point[0] for point in points]
        return min(x_points)

    @left.setter
    def left(self, amount: float):
        """The left most x coordinate."""
        leftmost = self.left
        diff = amount - leftmost
        self.center_x += diff

    @property
    def right(self) -> float:
        """
        Return the x coordinate of the right-side of the sprite's hit box.
        """
        points = self.get_adjusted_hit_box()

        # This happens if our point list is empty, such as a completely
        # transparent sprite.
        if len(points) == 0:
            return self.center_x

        x_points = [point[0] for point in points]
        return max(x_points)

    @right.setter
    def right(self, amount: float):
        """The right most x coordinate."""
        rightmost = self.right
        diff = rightmost - amount
        self.center_x -= diff

    @property
    def texture(self) -> Texture:
        # TODO: Remove this when we require a texture
        if not self._texture:
            raise ValueError("Sprite has not texture")
        return self._texture

    @texture.setter
    def texture(self, texture: Texture):
        """Sets texture by texture id. Should be renamed but keeping
        this for backwards compatibility."""
        if texture == self._texture:
            return

        if __debug__ and not isinstance(texture, Texture):
            raise TypeError(f"The 'texture' parameter must be an instance of arcade.Texture,"
                            f" but is an instance of '{type(texture)}'.")

        self.clear_spatial_hashes()
        self._point_list_cache = None
        self._texture = texture
        self._width = texture.width * self._scale[0]
        self._height = texture.height * self._scale[1]
        self.add_spatial_hashes()
        for sprite_list in self.sprite_lists:
            sprite_list._update_texture(self)

    def set_texture(self, texture_no: int) -> None:
        """
        Sets texture by texture id. Should be renamed because it takes
        a number rather than a texture, but keeping
        this for backwards compatibility.
        """
        texture = self.textures[texture_no]
        self.texture = texture

    @property
    def color(self) -> RGBA:
        """
        Get or set the RGB/RGBA color associated with the sprite.

        Example usage::

            print(sprite.color)
            sprite.color = arcade.color.RED
            sprite.color = 255, 0, 0
            sprite.color = 255, 0, 0, 128
        """
        return self._color

    @color.setter
    def color(self, color: RGBA):
        if len(color) == 4:
            if (
                self._color == color[0]
                and self._color[1] == color[1]
                and self._color[2] == color[2]
                and self._color[3] == color[3]
            ):
                return
            self._color = color[0], color[1], color[2], color[3]
        elif len(color) == 3:
            if (
                self._color == color[0]
                and self._color[1] == color[1]
                and self._color[2] == color[2]
            ):
                return
            self._color = color[0], color[1], color[2], self._color[3] 
        else:
            raise ValueError("Color must be three or four ints from 0-255")

        for sprite_list in self.sprite_lists:
            sprite_list._update_color(self)

    @property
    def alpha(self) -> int:
        """
        Return the alpha associated with the sprite.
        """
        return self._color[3]

    @alpha.setter
    def alpha(self, alpha: int):
        """
        Set the current sprite color as a value
        """
        self._color = self._color[0], self._color[1], self._color[2], int(alpha)

        for sprite_list in self.sprite_lists:
            sprite_list._update_color(self)

    @property
    def visible(self) -> bool:
        """
        Get or set the visibility of this sprite.
        This is a shortcut for changing the alpha value of a sprite
        to 0 or 255::

            # Make the sprite invisible
            sprite.visible = False
            # Change back to visible
            sprite.visible = True
            # Toggle visible
            sprite.visible = not sprite.visible

        :rtype: bool
        """
        return self._color[3] > 0

    @visible.setter
    def visible(self, value: bool):
        self._color = self._color[0], self._color[1], self._color[2], 255 if value else 0
        for sprite_list in self.sprite_lists:
            sprite_list._update_color(self)

    def register_sprite_list(self, new_list: "SpriteList") -> None:
        """
        Register this sprite as belonging to a list. We will automatically
        remove ourselves from the list when kill() is called.
        """
        self.sprite_lists.append(new_list)

    def register_physics_engine(self, physics_engine) -> None:
        """
        Register a physics engine on the sprite.
        This is only needed if you actually need a reference
        to your physics engine in the sprite itself.
        It has no other purposes.

        The registered physics engines can be accessed
        through the ``physics_engines`` attribute.

        It can for example be the pymunk physics engine
        or a custom one you made.
        """
        self.physics_engines.append(physics_engine)

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """Called by the pymunk physics engine if this sprite moves."""
        pass

    def face_point(self, point: Point) -> None:
        """
        Face the sprite towards a point. Assumes sprite image is facing upwards.

        :param Point point: Point to face towards.
        """
        angle = get_angle_degrees(self.center_x, self.center_y, point[0], point[1])

        # Reverse angle because sprite angles are backwards
        self.angle = -angle

    def draw(self, *, filter=None, pixelated=None, blend_function=None) -> None:
        """
        Draw the sprite.

        :param filter: Optional parameter to set OpenGL filter, such as
                       `gl.GL_NEAREST` to avoid smoothing.
        :param pixelated: ``True`` for pixelated and ``False`` for smooth interpolation.
                          Shortcut for setting filter=GL_NEAREST.
        :param blend_function: Optional parameter to set the OpenGL blend function used for drawing the sprite list,
                               such as 'arcade.Window.ctx.BLEND_ADDITIVE' or 'arcade.Window.ctx.BLEND_DEFAULT'
        """

        if self._sprite_list is None:
            from arcade import SpriteList

            self._sprite_list = SpriteList(capacity=1)
            self._sprite_list.append(self)

        self._sprite_list.draw(filter=filter, pixelated=pixelated, blend_function=blend_function)

    def draw_hit_box(self, color: Color = BLACK, line_thickness: float = 2.0) -> None:
        """
        Draw a sprite's hit-box.

        The 'hit box' drawing is cached, so if you change the color/line thickness
        later, it won't take.

        :param color: Color of box
        :param line_thickness: How thick the box should be
        """
        points = self.get_adjusted_hit_box()
        # NOTE: This is a COPY operation. We don't want to modify the points.
        points = tuple(points) + tuple(points[:-1])
        arcade.draw_line_strip(points, color=color, line_width=line_thickness)

    def update(self) -> None:
        """
        Update the sprite.
        """
        self.position = (
            self._position[0] + self.change_x,
            self._position[1] + self.change_y,
        )
        self.angle += self.change_angle

    def on_update(self, delta_time: float = 1 / 60) -> None:
        """
        Update the sprite. Similar to update, but also takes a delta-time.
        """
        pass

    def update_animation(self, delta_time: float = 1 / 60) -> None:
        """
        Override this to add code that will change
        what image is shown, so the sprite can be
        animated.

        :param float delta_time: Time since last update.
        """
        pass

    def remove_from_sprite_lists(self) -> None:
        """
        Remove the sprite from all sprite lists.
        """
        if len(self.sprite_lists) > 0:
            # We can't modify a list as we iterate through it, so create a copy.
            sprite_lists = self.sprite_lists.copy()
        else:
            # If the list is a size 1, we don't need to copy
            sprite_lists = self.sprite_lists

        for sprite_list in sprite_lists:
            if self in sprite_list:
                sprite_list.remove(self)

        for engine in self.physics_engines:
            engine.remove_sprite(self)

        self.physics_engines.clear()
        self.sprite_lists.clear()

    def kill(self) -> None:
        """
        Alias of `remove_from_sprite_lists`
        """
        self.remove_from_sprite_lists()

    def collides_with_point(self, point: Point) -> bool:
        """Check if point is within the current sprite.

        :param Point point: Point to check.
        :return: True if the point is contained within the sprite's boundary.
        :rtype: bool
        """
        from arcade.geometry import is_point_in_polygon

        x, y = point
        return is_point_in_polygon(x, y, self.get_adjusted_hit_box())

    def collides_with_sprite(self, other: "Sprite") -> bool:
        """Will check if a sprite is overlapping (colliding) another Sprite.

        :param Sprite other: the other sprite to check against.
        :return: True or False, whether or not they are overlapping.
        :rtype: bool
        """
        from arcade import check_for_collision

        return check_for_collision(self, other)

    def collides_with_list(self, sprite_list: "SpriteList") -> List["Sprite"]:
        """Check if current sprite is overlapping with any other sprite in a list

        :param SpriteList sprite_list: SpriteList to check against
        :return: List of all overlapping Sprites from the original SpriteList
        :rtype: list
        """
        from arcade import check_for_collision_with_list

        # noinspection PyTypeChecker
        return check_for_collision_with_list(self, sprite_list)
