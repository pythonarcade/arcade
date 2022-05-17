"""
This module manages all of the code around Sprites.

For information on Spatial Hash Maps, see:
https://www.gamedev.net/articles/programming/general-and-gameplay-programming/spatial-hashing-r2697/
"""

import math

from arcade.texture import _build_cache_name
from arcade.geometry_generic import get_angle_degrees

import dataclasses

from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
    TYPE_CHECKING,
)

import PIL.Image

from arcade import load_texture
from arcade import Texture
from arcade import rotate_point
from arcade import create_line_loop
from arcade import ShapeElementList
from arcade import make_soft_circle_texture
from arcade import make_circle_texture
from arcade import Color
from arcade.color import BLACK
# from pyglet.math import Mat3
from arcade.resources import resolve_resource_path

from arcade.arcade_types import RGB, Point, PointList

if TYPE_CHECKING:  # handle import cycle caused by type hinting
    from arcade.sprite_list import SpriteList

FACE_RIGHT = 1
FACE_LEFT = 2
FACE_UP = 3
FACE_DOWN = 4


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

    :param str filename: Filename of an image that represents the sprite.
    :param float scale: Scale the image up or down. Scale of 1.0 is none.
    :param float image_x: X offset to sprite within sprite sheet.
    :param float image_y: Y offset to sprite within sprite sheet.
    :param float image_width: Width of the sprite
    :param float image_height: Height of the sprite
    :param float center_x: Location of the sprite
    :param float center_y: Location of the sprite
    :param bool flipped_horizontally: Mirror the sprite image. Flip left/right across vertical axis.
    :param bool flipped_vertically: Flip the image up/down across the horizontal axis.
    :param bool flipped_diagonally: Transpose the image, flip it across the diagonal.
    :param str hit_box_algorithm: One of None, 'None', 'Simple' or 'Detailed'.
          Defaults to 'Simple'. Use 'Simple' for the :data:`PhysicsEngineSimple`,
          :data:`PhysicsEnginePlatformer`
          and 'Detailed' for the :data:`PymunkPhysicsEngine`.
    :param Texture texture: Specify the texture directly.
    :param float angle: The initial rotation of the sprite in degrees

    This will ignore all hit box and image size arguments.

        .. figure:: ../images/hit_box_algorithm_none.png
           :width: 40%

           hit_box_algorithm = "None"

        .. figure:: ../images/hit_box_algorithm_simple.png
           :width: 55%

           hit_box_algorithm = "Simple"

        .. figure:: ../images/hit_box_algorithm_detailed.png
           :width: 75%

           hit_box_algorithm = "Detailed"

    :param float hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box

    Attributes:
        :alpha: Transparency of sprite. 0 is invisible, 255 is opaque.
        :angle: Rotation angle in degrees. Sprites rotate counter-clock-wise.
        :radians: Rotation angle in radians. Sprites rotate counter-clock-wise.
        :bottom: Set/query the sprite location by using the bottom coordinate. \
        This will be the 'y' of the bottom of the sprite.
        :boundary_left: Used in movement. Left boundary of moving sprite.
        :boundary_right: Used in movement. Right boundary of moving sprite.
        :boundary_top: Used in movement. Top boundary of moving sprite.
        :boundary_bottom: Used in movement. Bottom boundary of moving sprite.
        :center_x: X location of the center of the sprite
        :center_y: Y location of the center of the sprite
        :change_x: Movement vector, in the x direction.
        :change_y: Movement vector, in the y direction.
        :change_angle: Change in rotation.
        :color: Color tint the sprite
        :collision_radius: Used as a fast-check to see if this item is close \
        enough to another item. If this check works, we do a slower more accurate check. \
        You probably don't want to use this field. Instead, set points in the \
        hit box.
        :cur_texture_index: Index of current texture being used.
        :guid: Unique identifier for the sprite. Useful when debugging.
        :height: Height of the sprite.
        :force: Force being applied to the sprite. Useful when used with Pymunk \
        for physics.
        :hit_box: Points, in relation to the center of the sprite, that are used \
        for collision detection. Arcade defaults to creating a hit box via the \
        'simple' hit box algorithm \
        that encompass the image. If you are creating a ramp or making better \
        hit-boxes, you can custom-set these.
        :left: Set/query the sprite location by using the left coordinate. This \
        will be the 'x' of the left of the sprite.
        :position: A list with the (x, y) of where the sprite is.
        :right: Set/query the sprite location by using the right coordinate. \
        This will be the 'y=x' of the right of the sprite.
        :sprite_lists: List of all the sprite lists this sprite is part of.
        :texture: :class:`arcade.Texture` class with the current texture. Setting a new texture does \
        **not** update the hit box of the sprite. This can be done with \
        ``my_sprite.hit_box = my_sprite.texture.hit_box_points``. New textures will be centered \
        on the current center_x/center_y.
        :textures: List of textures associated with this sprite.
        :top: Set/query the sprite location by using the top coordinate. This \
        will be the 'y' of the top of the sprite.
        :scale: Scale the image up or down. Scale of 1.0 is original size, 0.5 \
        is 1/2 height and width.
        :velocity: Change in x, y expressed as a list. (0, 0) would be not moving.
        :width: Width of the sprite

    It is common to over-ride the `update` method and provide mechanics on
    movement or other sprite updates.
    """

    def __init__(
        self,
        filename: str = None,
        scale: float = 1,
        image_x: float = 0,
        image_y: float = 0,
        image_width: float = 0,
        image_height: float = 0,
        center_x: float = 0,
        center_y: float = 0,
        repeat_count_x: int = 1,  # Unused
        repeat_count_y: int = 1,  # Unused
        flipped_horizontally: bool = False,
        flipped_vertically: bool = False,
        flipped_diagonally: bool = False,
        hit_box_algorithm: Optional[str] = "Simple",
        hit_box_detail: float = 4.5,
        texture: Texture = None,
        angle: float = 0,
    ):
        """ Constructor """
        # Position, size and orientation properties
        self._width: float = 0.0
        self._height: float = 0.0
        self._scale: float = scale
        self._position: Point = (center_x, center_y)
        self._angle = angle
        self.velocity = [0.0, 0.0]
        self.change_angle: float = 0.0

        # Hit box and collision property
        self._points: Optional[PointList] = None
        self._point_list_cache: Optional[PointList] = None
        self._hit_box_shape: Optional[ShapeElementList] = None
        self._hit_box_algorithm = hit_box_algorithm
        self._hit_box_detail = hit_box_detail
        self._collision_radius: Optional[float] = None

        # Color
        self._color: RGB = (255, 255, 255)
        self._alpha: int = 255

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
        self._sprite_list: Optional["SpriteList"] = None  # Used for Sprite.draw()

        # Pymunk specific properties
        self._pymunk: Optional[PyMunk] = None
        self.force = [0, 0]

        # Debug properties
        self.guid: Optional[str] = None

        # Sanity check values
        if image_width < 0:
            raise ValueError("Width of image can't be less than zero.")

        if image_height < 0:
            raise ValueError(
                "Height entered is less than zero. Height must be a positive float."
            )

        if image_width == 0 and image_height != 0:
            raise ValueError("Width can't be zero.")

        if image_height == 0 and image_width != 0:
            raise ValueError("Height can't be zero.")

        if hit_box_algorithm not in ["Simple", "Detailed", "None", None]:
            raise ValueError(
                "hit_box_algorithm must be 'Simple', 'Detailed', 'None' or None"
            )

        if texture:
            self._texture = texture
            self._textures = [texture]
            self._width = self._texture.width * scale
            self._height = self._texture.height * scale
        elif filename is not None:
            self._texture = load_texture(
                filename,
                image_x,
                image_y,
                image_width,
                image_height,
                flipped_horizontally=flipped_horizontally,
                flipped_vertically=flipped_vertically,
                flipped_diagonally=flipped_diagonally,
                hit_box_algorithm=hit_box_algorithm,
                hit_box_detail=hit_box_detail,
            )
            self.textures = [self._texture]
            # Ignore the texture's scale and use ours
            self._width = self._texture.width * scale
            self._height = self._texture.height * scale

        if self._texture and not self._points:
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
        if new_value[0] != self._position[0] or new_value[1] != self._position[1]:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._position = new_value
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_location(self)

    def set_position(self, center_x: float, center_y: float):
        """
        Set a sprite's position

        :param float center_x: New x position of sprite
        :param float center_y: New y position of sprite
        """
        self.position = (center_x, center_y)

    def set_hit_box(self, points: PointList):
        """
        Set a sprite's hit box. Hit box should be relative to a sprite's center,
        and with a scale of 1.0.
        Points will be scaled with get_adjusted_hit_box.
        """
        self._point_list_cache = None
        self._hit_box_shape = None
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
        # If there is no hitbox, use the width/height to get one
        if self._points is None and self._texture:
            self._points = self._texture.hit_box_points

        if self._points is None and self._width:
            x1, y1 = -self._width / 2, -self._height / 2
            x2, y2 = +self._width / 2, -self._height / 2
            x3, y3 = +self._width / 2, +self._height / 2
            x4, y4 = -self._width / 2, +self._height / 2

            self._points = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))

        if self._points is None and self.texture is not None:
            self._points = self.texture.hit_box_points

        if self._points is None:
            raise ValueError(
                "Error trying to get the hit box of a sprite, when no hit box is set.\nPlease make sure the "
                "Sprite.texture is set to a texture before trying to draw or do collision testing.\n"
                "Alternatively, manually call Sprite.set_hit_box with points for your hitbox."
            )

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

        def _adjust_point(point):

            # Rotate the point
            if self._angle:
                point = rotate_point(point[0], point[1], 0, 0, self._angle)

            # Get a copy of the point
            point = [point[0] * self._scale + self._position[0], point[1] * self._scale + self._position[1]]

            return point

        point_list = [_adjust_point(point) for point in self.hit_box]

        # Cache the results
        self._point_list_cache = point_list

        return self._point_list_cache

    def forward(self, speed: float = 1.0):
        """
        Adjusts a Sprite's movement vector forward.
        This method does not actually move the sprite, just takes the current
        change_x/change_y and adjusts it by the speed given.

        :param speed: speed factor
        """
        self.change_x += math.cos(self.radians) * speed
        self.change_y += math.sin(self.radians) * speed

    def reverse(self, speed: float = 1.0):
        """
        Adjusts a Sprite's movement vector backwards.
        This method does not actually move the sprite, just takes the current
        change_x/change_y and adjusts it by the speed given.

        :param speed: speed factor
        """
        self.forward(-speed)

    def strafe(self, speed: float = 1.0):
        """
        Adjusts a Sprite's movement vector sideways.
        This method does not actually move the sprite, just takes the current
        change_x/change_y and adjusts it by the speed given.

        :param speed: speed factor
        """
        self.change_x += -math.sin(self.radians) * speed
        self.change_y += math.cos(self.radians) * speed

    def turn_right(self, theta: float = 90.0):
        """
        Rotate the sprite right by the passed number of degrees.

        :param theta: change in angle, in degrees
        """
        self.angle -= theta

    def turn_left(self, theta: float = 90.0):
        """
        Rotate the sprite left by the passed number of degrees.

        :param theta: change in angle, in degrees
        """
        self.angle += theta

    def stop(self):
        """
        Stop the Sprite's motion.
        """
        self.change_x = 0
        self.change_y = 0
        self.change_angle = 0

    @property
    def collision_radius(self) -> float:
        """
        Get the collision radius.

        .. note:: Final collision checking is done via geometry that was
            set in get_points/set_points. These points are used in the
            check_for_collision function. This collision_radius variable
            is used as a "pre-check." We do a super-fast check with
            collision_radius and see if the sprites are close. If they are,
            then we look at the geometry and figure if they really are colliding.

        """
        if not self._collision_radius:
            self._collision_radius = max(self.width, self.height)
        return self._collision_radius

    @collision_radius.setter
    def collision_radius(self, collision_radius: float):
        """
        Set the collision radius.

        .. note:: Final collision checking is done via geometry that was
            set in the hit_box property. These points are used in the
            check_for_collision function. This collision_radius variable
            is used as a "pre-check." We do a super-fast check with
            collision_radius and see if the sprites are close. If they are,
            then we look at the geometry and figure if they really are colliding.

        :param float collision_radius: Collision radius
        """
        self._collision_radius = collision_radius

    def clear_spatial_hashes(self):
        """
        Search the sprite lists this sprite is a part of, and remove it
        from any spatial hashes it is a part of.

        """
        for sprite_list in self.sprite_lists:
            if sprite_list._use_spatial_hash and sprite_list.spatial_hash is not None:
                try:
                    sprite_list.spatial_hash.remove_object(self)
                except ValueError:
                    print(
                        "Warning, attempt to remove item from spatial hash that doesn't exist in the hash."
                    )

    def add_spatial_hashes(self):
        """
        Add spatial hashes for this sprite in all the sprite lists it is part of.
        """
        for sprite_list in self.sprite_lists:
            if sprite_list._use_spatial_hash:
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

            # If there is a hit box, rescale it to the new width
            if self._points:
                scale = new_value / self._width
                old_points = self._points
                self._points = [(point[0] * scale, point[1]) for point in old_points]

            self._width = new_value
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_size(self)

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

            # If there is a hit box, rescale it to the new width
            if self._points:
                scale = new_value / self._height
                old_points = self._points
                self._points = [(point[0], point[1] * scale) for point in old_points]

            self._height = new_value
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_height(self)

    @property
    def scale(self) -> float:
        """Get the scale of the sprite."""
        return self._scale

    @scale.setter
    def scale(self, new_value: float):
        """Set the center x coordinate of the sprite."""
        if new_value != self._scale:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._scale = new_value
            if self._texture:
                self._width = self._texture.width * self._scale
                self._height = self._texture.height * self._scale
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_size(self)

    def rescale_relative_to_point(self, point: Point, factor: float) -> None:
        """Rescale the sprite relative to a different point than its center."""
        self.scale *= factor
        self.center_x = (self.center_x - point[0]) * factor + point[0]
        self.center_y = (self.center_y - point[1]) * factor + point[1]

    @property
    def center_x(self) -> float:
        """Get the center x coordinate of the sprite."""
        return self._position[0]

    @center_x.setter
    def center_x(self, new_value: float):
        """Set the center x coordinate of the sprite."""
        if new_value != self._position[0]:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._position = (new_value, self._position[1])
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_location(self)

    @property
    def center_y(self) -> float:
        """Get the center y coordinate of the sprite."""
        return self._position[1]

    @center_y.setter
    def center_y(self, new_value: float):
        """Set the center y coordinate of the sprite."""
        if new_value != self._position[1]:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._position = (self._position[0], new_value)
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_location(self)

    @property
    def change_x(self) -> float:
        """Get the velocity in the x plane of the sprite."""
        return self.velocity[0]

    @change_x.setter
    def change_x(self, new_value: float):
        """Set the velocity in the x plane of the sprite."""
        self.velocity[0] = new_value

    @property
    def change_y(self) -> float:
        """Get the velocity in the y plane of the sprite."""
        return self.velocity[1]

    @change_y.setter
    def change_y(self, new_value: float):
        """Set the velocity in the y plane of the sprite."""
        self.velocity[1] = new_value

    @property
    def angle(self) -> float:
        """Get the angle of the sprite's rotation."""
        return self._angle

    @angle.setter
    def angle(self, new_value: float):
        """Set the angle of the sprite's rotation."""
        if new_value != self._angle:
            self.clear_spatial_hashes()
            self._angle = new_value
            self._point_list_cache = None

            for sprite_list in self.sprite_lists:
                sprite_list.update_angle(self)

            self.add_spatial_hashes()

    @property
    def radians(self) -> float:
        """
        Converts the degrees representation of self.angle into radians.
        :return: float
        """
        return self.angle / 180.0 * math.pi

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
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, texture: Texture):
        """Sets texture by texture id. Should be renamed but keeping
        this for backwards compatibility."""
        if texture == self._texture:
            return

        if not isinstance(texture, Texture):
            raise ValueError(f"The 'texture' parameter must be an instance of arcade.Texture."
                             f"It is an instance of '{type(texture)}'.")
        assert isinstance(texture, Texture)

        self.clear_spatial_hashes()
        self._point_list_cache = None
        self._texture = texture
        self._width = texture.width * self.scale
        self._height = texture.height * self.scale
        self.add_spatial_hashes()
        for sprite_list in self.sprite_lists:
            sprite_list.update_texture(self)

    def set_texture(self, texture_no: int):
        """
        Sets texture by texture id. Should be renamed because it takes
        a number rather than a texture, but keeping
        this for backwards compatibility.
        """
        if self.textures[texture_no] == self._texture:
            return

        texture = self.textures[texture_no]
        self.clear_spatial_hashes()
        self._point_list_cache = None
        self._texture = texture
        self._width = texture.width * self.scale
        self._height = texture.height * self.scale
        self.add_spatial_hashes()
        for sprite_list in self.sprite_lists:
            sprite_list.update_texture(self)

    @property
    def color(self) -> RGB:
        """
        Return the RGB color associated with the sprite.
        """
        return self._color

    @color.setter
    def color(self, color: Color):
        """
        Set the current sprite color as a RGB value
        """
        if color is None:
            raise ValueError("Color must be three or four ints from 0-255")

        if len(color) == 3:
            if (
                self._color[0] == color[0]
                and self._color[1] == color[1]
                and self._color[2] == color[2]
            ):
                return
        elif len(color) == 4:
            color = cast(List, color)  # Prevent typing error
            if (
                self._color[0] == color[0]
                and self._color[1] == color[1]
                and self._color[2] == color[2]
                and self.alpha == color[3]
            ):
                return
            self.alpha = color[3]
        else:
            raise ValueError("Color must be three or four ints from 0-255")

        self._color = color[0], color[1], color[2]

        for sprite_list in self.sprite_lists:
            sprite_list.update_color(self)

    @property
    def alpha(self) -> int:
        """
        Return the alpha associated with the sprite.
        """
        return self._alpha

    @alpha.setter
    def alpha(self, alpha: int):
        """
        Set the current sprite color as a value
        """
        if alpha < 0 or alpha > 255:
            raise ValueError(
                f"Invalid value for alpha. Must be 0 to 255, received {alpha}"
            )

        self._alpha = int(alpha)
        for sprite_list in self.sprite_lists:
            sprite_list.update_color(self)

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
        return self._alpha > 0

    @visible.setter
    def visible(self, value: bool):
        if value:
            self._alpha = 255
        else:
            self._alpha = 0

        for sprite_list in self.sprite_lists:
            sprite_list.update_color(self)

    def register_sprite_list(self, new_list: "SpriteList"):
        """
        Register this sprite as belonging to a list. We will automatically
        remove ourselves from the the list when kill() is called.
        """
        self.sprite_lists.append(new_list)

    def register_physics_engine(self, physics_engine):
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

    def face_point(self, point: Point):
        """
        Face the sprite towards a point. Assumes sprite image is facing upwards.

        :param Point point: Point to face towards.
        """
        angle = get_angle_degrees(self.center_x, self.center_y, point[0], point[1])

        # Reverse angle because sprite angles are backwards
        self.angle = -angle

    def draw(self, *, filter=None, pixelated=None, blend_function=None):
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

            self._sprite_list = SpriteList()
            self._sprite_list.append(self)

        self._sprite_list.draw(filter=filter, pixelated=pixelated, blend_function=blend_function)

    def draw_hit_box(self, color: Color = BLACK, line_thickness: float = 1):
        """
        Draw a sprite's hit-box.

        The 'hit box' drawing is cached, so if you change the color/line thickness
        later, it won't take.

        :param color: Color of box
        :param line_thickness: How thick the box should be
        """

        if self._hit_box_shape is None:

            # Adjust the hitbox
            point_list = []
            for point in self.hit_box:
                # Get a copy of the point
                point = [point[0], point[1]]

                # Scale the point
                if self.scale != 1:
                    point[0] *= self.scale
                    point[1] *= self.scale

                # Rotate the point (Don't, should already be rotated.)
                # if self.angle:
                #     point = rotate_point(point[0], point[1], 0, 0, self.angle)

                point_list.append(point)

            shape = create_line_loop(point_list, color, line_thickness)
            self._hit_box_shape = ShapeElementList()
            self._hit_box_shape.append(shape)

        self._hit_box_shape.center_x = self.center_x
        self._hit_box_shape.center_y = self.center_y
        self._hit_box_shape.angle = self.angle
        self._hit_box_shape.draw()

        # point_list = self.get_adjusted_hit_box()
        # draw_polygon_outline(point_list, color, line_thickness)

    def update(self):
        """
        Update the sprite.
        """
        self.position = [
            self._position[0] + self.change_x,
            self._position[1] + self.change_y,
        ]
        self.angle += self.change_angle

    def on_update(self, delta_time: float = 1 / 60):
        """
        Update the sprite. Similar to update, but also takes a delta-time.
        """
        pass

    def update_animation(self, delta_time: float = 1 / 60):
        """
        Override this to add code that will change
        what image is shown, so the sprite can be
        animated.

        :param float delta_time: Time since last update.
        """
        pass

    def remove_from_sprite_lists(self):
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

    def kill(self):
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

    def collides_with_list(self, sprite_list: "SpriteList") -> list:
        """Check if current sprite is overlapping with any other sprite in a list

        :param SpriteList sprite_list: SpriteList to check against
        :return: SpriteList of all overlapping Sprites from the original SpriteList
        :rtype: SpriteList
        """
        from arcade import check_for_collision_with_list

        # noinspection PyTypeChecker
        return check_for_collision_with_list(self, sprite_list)


@dataclasses.dataclass
class AnimationKeyframe:
    """
    Used in animated sprites.
    """

    tile_id: int
    duration: int
    texture: Texture


class AnimatedTimeBasedSprite(Sprite):
    """
    Sprite for platformer games that supports animations. These can
    be automatically created by the Tiled Map Editor.
    """

    def __init__(
        self,
        filename: str = None,
        scale: float = 1,
        image_x: float = 0,
        image_y: float = 0,
        image_width: float = 0,
        image_height: float = 0,
        center_x: float = 0,
        center_y: float = 0,
        _repeat_count_x=1,  # Unused
        _repeat_count_y=1,  # Unused
    ):

        super().__init__(
            filename=filename,
            scale=scale,
            image_x=image_x,
            image_y=image_y,
            image_width=image_width,
            image_height=image_height,
            center_x=center_x,
            center_y=center_y,
        )
        self.cur_frame_idx = 0
        self.frames: List[AnimationKeyframe] = []
        self.time_counter = 0.0

    def update_animation(self, delta_time: float = 1 / 60):
        """
        Logic for selecting the proper texture to use.
        """
        self.time_counter += delta_time
        while self.time_counter > self.frames[self.cur_frame_idx].duration / 1000.0:
            self.time_counter -= self.frames[self.cur_frame_idx].duration / 1000.0
            self.cur_frame_idx += 1
            if self.cur_frame_idx >= len(self.frames):
                self.cur_frame_idx = 0
            # source = self.frames[self.cur_frame].texture.image.source
            cur_frame = self.frames[self.cur_frame_idx]
            # print(f"Advance to frame {self.cur_frame_idx}: {cur_frame.texture.name}")
            self.texture = cur_frame.texture


class AnimatedWalkingSprite(Sprite):
    """
    Deprecated Sprite for platformer games that supports walking animations.
    Make sure to call update_animation after loading the animations so the
    initial texture can be set. Or manually set it.

    It is highly recommended you create your own version of this class rather than
    try to use this pre-packaged one.

    For an example, see this section of the platformer tutorial:
    :ref:`platformer_part_twelve`.
    """

    def __init__(
        self,
        scale: float = 1,
        image_x: float = 0,
        image_y: float = 0,
        center_x: float = 0,
        center_y: float = 0,
    ):
        super().__init__(
            scale=scale,
            image_x=image_x,
            image_y=image_y,
            center_x=center_x,
            center_y=center_y,
        )
        self.state = FACE_RIGHT
        self.stand_right_textures: List[Texture] = []
        self.stand_left_textures: List[Texture] = []
        self.walk_left_textures: List[Texture] = []
        self.walk_right_textures: List[Texture] = []
        self.walk_up_textures: List[Texture] = []
        self.walk_down_textures: List[Texture] = []
        self.cur_texture_index = 0
        self.texture_change_distance = 20
        self.last_texture_change_center_x: float = 0
        self.last_texture_change_center_y: float = 0

    def update_animation(self, delta_time: float = 1 / 60):
        """
        Logic for selecting the proper texture to use.
        """
        x1 = self.center_x
        x2 = self.last_texture_change_center_x
        y1 = self.center_y
        y2 = self.last_texture_change_center_y
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        texture_list: List[Texture] = []

        change_direction = False
        if (
            self.change_x > 0
            and self.change_y == 0
            and self.state != FACE_RIGHT
            and len(self.walk_right_textures) > 0
        ):
            self.state = FACE_RIGHT
            change_direction = True
        elif (
            self.change_x < 0
            and self.change_y == 0
            and self.state != FACE_LEFT
            and len(self.walk_left_textures) > 0
        ):
            self.state = FACE_LEFT
            change_direction = True
        elif (
            self.change_y < 0
            and self.change_x == 0
            and self.state != FACE_DOWN
            and len(self.walk_down_textures) > 0
        ):
            self.state = FACE_DOWN
            change_direction = True
        elif (
            self.change_y > 0
            and self.change_x == 0
            and self.state != FACE_UP
            and len(self.walk_up_textures) > 0
        ):
            self.state = FACE_UP
            change_direction = True

        if self.change_x == 0 and self.change_y == 0:
            if self.state == FACE_LEFT:
                self.texture = self.stand_left_textures[0]
            elif self.state == FACE_RIGHT:
                self.texture = self.stand_right_textures[0]
            elif self.state == FACE_UP:
                self.texture = self.walk_up_textures[0]
            elif self.state == FACE_DOWN:
                self.texture = self.walk_down_textures[0]

        elif change_direction or distance >= self.texture_change_distance:
            self.last_texture_change_center_x = self.center_x
            self.last_texture_change_center_y = self.center_y

            if self.state == FACE_LEFT:
                texture_list = self.walk_left_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError(
                        "update_animation was called on a sprite that doesn't have a "
                        "list of walk left textures."
                    )
            elif self.state == FACE_RIGHT:
                texture_list = self.walk_right_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError(
                        "update_animation was called on a sprite that doesn't have a list of "
                        "walk right textures."
                    )
            elif self.state == FACE_UP:
                texture_list = self.walk_up_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError(
                        "update_animation was called on a sprite that doesn't have a list of "
                        "walk up textures."
                    )
            elif self.state == FACE_DOWN:
                texture_list = self.walk_down_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError(
                        "update_animation was called on a sprite that doesn't have a list of walk down textures."
                    )

            self.cur_texture_index += 1
            if self.cur_texture_index >= len(texture_list):
                self.cur_texture_index = 0

            self.texture = texture_list[self.cur_texture_index]

        if self._texture is None:
            print("Error, no texture set")
        else:
            self.width = self._texture.width * self.scale
            self.height = self._texture.height * self.scale


def load_animated_gif(resource_name):
    """
    Given an animated gif, return a AnimatedTimeBasedSprite.

    Support for transparency in animated gifs in Python is lacking.
    There are a lot of
    older animated gifs that are saved weird. The end result is that the
    often the first frame of an animated gif is the only frame that
    we correctly get the transparency on. Until the Pillow library better
    handles this, loading animated gifs will be pretty buggy.
    """

    file_name = resolve_resource_path(resource_name)
    # print(file_name)
    image_object = PIL.Image.open(file_name)
    if not image_object.is_animated:
        raise TypeError(f"The file {resource_name} is not an animated gif.")

    # print(image_object.n_frames)

    sprite = AnimatedTimeBasedSprite()
    for frame in range(0, image_object.n_frames):
        image_object.seek(frame)
        frame_duration = image_object.info['duration']
        # print(frame_duration)
        image = image_object.convert("RGBA")
        texture = Texture(f"{resource_name}-{frame}", image)
        sprite.textures.append(texture)
        frame = AnimationKeyframe(0, frame_duration, texture)
        sprite.frames.append(frame)

    sprite.texture = sprite.textures[0]
    return sprite


class SpriteSolidColor(Sprite):
    """
    This sprite is just a rectangular sprite of one solid color. No need to
    use an image file.

    :param int width: Width of the sprite
    :param int height: Height of the sprite
    :param Color color: Color of the sprite
    """

    def __init__(self, width: int, height: int, color: Color):
        """
        Create a solid-color rectangular sprite.
        """
        super().__init__()

        cache_name = _build_cache_name("Solid", width, height, color[0], color[1], color[2])

        # use existing texture if it exists
        if cache_name in load_texture.texture_cache:  # type: ignore
            texture = load_texture.texture_cache[cache_name]  # type: ignore

        # otherwise, generate a filler sprite and add it to the cache
        else:
            texture = Texture.create_filled(cache_name, (width, height), color)
            load_texture.texture_cache[cache_name] = texture  # type: ignore

        # apply chosen texture to the current sprite
        self.texture = texture
        self._points = texture.hit_box_points


class SpriteCircle(Sprite):
    """
    This sprite is just an elliptical sprite of one solid color. No need to
    use an image file.


    :param float radius: Radius of the circle
    :param Color color: Color of the circle
    :param bool soft: If True, will add a alpha gradient

    """

    def __init__(self, radius: int, color: Color, soft: bool = False):
        super().__init__()

        diameter = radius * 2

        # determine the texture's cache name
        if soft:
            cache_name = _build_cache_name("circle_texture_soft", diameter, color[0], color[1], color[2])
        else:
            cache_name = _build_cache_name("circle_texture", diameter, color[0], color[1], color[2], 255, 0)

        # use the named texture if it was already made
        if cache_name in load_texture.texture_cache:  # type: ignore
            texture = load_texture.texture_cache[cache_name]  # type: ignore

        # generate the texture if it's not in the cache
        else:
            if soft:
                texture = make_soft_circle_texture(diameter, color, name=cache_name)
            else:
                texture = make_circle_texture(diameter, color, name=cache_name)

            load_texture.texture_cache[cache_name] = texture  # type: ignore

        # apply results to the new sprite
        self.texture = texture
        self._points = self.texture.hit_box_points


def get_distance_between_sprites(sprite1: Sprite, sprite2: Sprite) -> float:
    """
    Returns the distance between the center of two given sprites

    :param Sprite sprite1: Sprite one
    :param Sprite sprite2: Sprite two
    :return: Distance
    :rtype: float
    """
    distance = math.sqrt(
        (sprite1.center_x - sprite2.center_x) ** 2
        + (sprite1.center_y - sprite2.center_y) ** 2
    )
    return distance
