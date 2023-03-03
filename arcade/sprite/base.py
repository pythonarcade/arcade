import math
from typing import TYPE_CHECKING, List, Iterable, TypeVar

import arcade
from arcade.types import RGBA, Point, PointList, Color
from arcade.color import BLACK
from arcade.texture import Texture
if TYPE_CHECKING:
    from arcade.sprite_list import SpriteList

# Type from sprite that can be any BasicSprite or any subclass of BasicSprite
SpriteType = TypeVar("SpriteType", bound="BasicSprite")


class BasicSprite:
    """
    The absolute minimum needed for a sprite.
    """
    __slots__ = (
        "_position",
        "_depth",
        "_width",
        "_height",
        "_scale",
        "_color",
        "_texture",
        "sprite_lists",
        "_angle",
        "__weakref__",
    )

    def __init__(
        self,
        texture: Texture,
        scale: float = 1.0,
        center_x: float = 0,
        center_y: float = 0,
        **kwargs,
    ) -> None:
        self._position = (center_x, center_y)
        self._depth = 0.0
        self._texture = texture
        self._width = texture.width * scale
        self._height =texture.height * scale
        self._scale = scale, scale
        self._color: RGBA = 255, 255, 255, 255
        self.sprite_lists: List["SpriteList"] = []

        # Core properties we don't use, but spritelist expects it
        self._angle = 0.0

    # --- Core Properties ---

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

        self._position = new_value
        self.update_spatial_hash()

        for sprite_list in self.sprite_lists:
            sprite_list._update_position(self)

    @property
    def center_x(self) -> float:
        """Get the center x coordinate of the sprite."""
        return self._position[0]

    @center_x.setter
    def center_x(self, new_value: float):
        """Set the center x coordinate of the sprite."""
        if new_value == self._position[0]:
            return

        self._position = (new_value, self._position[1])
        self.update_spatial_hash()

        for sprite_list in self.sprite_lists:
            sprite_list._update_position_x(self)

    @property
    def center_y(self) -> float:
        """Get the center y coordinate of the sprite."""
        return self._position[1]

    @center_y.setter
    def center_y(self, new_value: float):
        """Set the center y coordinate of the sprite."""
        if new_value == self._position[1]:
            return

        self._position = (self._position[0], new_value)
        self.update_spatial_hash()

        for sprite_list in self.sprite_lists:
            sprite_list._update_position_y(self)

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
    def width(self) -> float:
        """Get the width of the sprite."""
        return self._width

    @width.setter
    def width(self, new_value: float):
        """Set the width in pixels of the sprite."""
        if new_value != self._width:
            self._scale = new_value / self._texture.width, self._scale[1]
            self._width = new_value

            self.update_spatial_hash()
            for sprite_list in self.sprite_lists:
                sprite_list._update_width(self)

    @property
    def height(self) -> float:
        """Get the height in pixels of the sprite."""
        return self._height

    @height.setter
    def height(self, new_value: float):
        """Set the center x coordinate of the sprite."""
        if new_value != self._height:
            self._scale = self._scale[0], new_value / self._texture.height
            self._height = new_value

            self.update_spatial_hash()
            for sprite_list in self.sprite_lists:
                sprite_list._update_height(self)


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

        self._scale = new_value, new_value
        if self._texture:
            self._width = self._texture.width * self._scale[0]
            self._height = self._texture.height * self._scale[1]
            self._hit_box_max_dimension = max(self._width, self._height) / 2

        self.update_spatial_hash()
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

        self._scale = new_value
        if self._texture:
            self._width = self._texture.width * self._scale[0]
            self._height = self._texture.height * self._scale[1]

        self.update_spatial_hash()

        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    @property
    def left(self) -> float:
        """
        Return the x coordinate of the left-side of the sprite's hit box.
        """
        return self.center_x - self.width / 2

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
        return self.center_x + self.width / 2

    @right.setter
    def right(self, amount: float):
        """The right most x coordinate."""
        rightmost = self.right
        diff = rightmost - amount
        self.center_x -= diff

    @property
    def bottom(self) -> float:
        """
        Return the y coordinate of the bottom of the sprite.
        """
        return self._position[1] - self.height / 2

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
        return self._position[1] + self.height / 2

    @top.setter
    def top(self, amount: float):
        """The highest y coordinate."""
        highest = self.top
        diff = highest - amount
        self.center_y -= diff

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

        self._texture = texture
        self._width = texture.width * self._scale[0]
        self._height = texture.height * self._scale[1]
        self._hit_box_max_dimension = math.sqrt(self._width ** 2 + self._height ** 2)
        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_texture(self)

    # ---- Update methods ----

    def update(self) -> None:
        """
        Update the sprite.
        """
        pass

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

    # --- Scale methods -----

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
        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)
            if position_changed:
                sprite_list._update_position(self)

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
        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)
            if position_changed:
                sprite_list._update_position(self)

    # ---- Utility Methods ----

    def get_adjusted_hit_box(self) -> PointList:
        """
        Return the hit box points adjusted for the sprite's position.
        """
        x, y = self._position
        w, h = self._width, self._height
        # TODO: Might might want to cache this?
        return (
            (-w / 2 + x, -h / 2 + y),
            (w / 2 + x, -h / 2 + y),
            (w / 2 + x, h / 2 + y),
            (-w / 2 + x, h / 2 + y)
        )

    def update_spatial_hash(self) -> None:
        """
        Update the sprites location in the spatial hash.
        """
        for sprite_list in self.sprite_lists:
            if sprite_list.spatial_hash is not None:
                sprite_list.spatial_hash.move(self)

    def register_sprite_list(self, new_list: "SpriteList") -> None:
        """
        Register this sprite as belonging to a list. We will automatically
        remove ourselves from the list when kill() is called.
        """
        self.sprite_lists.append(new_list)

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

        self.sprite_lists.clear()

    # ----- Drawing Methods -----

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

    # ---- Shortcut Methods ----

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

    def collides_with_sprite(self: SpriteType, other: SpriteType) -> bool:
        """Will check if a sprite is overlapping (colliding) another Sprite.

        :param Sprite other: the other sprite to check against.
        :return: True or False, whether or not they are overlapping.
        :rtype: bool
        """
        from arcade import check_for_collision

        return check_for_collision(self, other)

    def collides_with_list(self: SpriteType, sprite_list: "SpriteList") -> List[SpriteType]:
        """Check if current sprite is overlapping with any other sprite in a list

        :param SpriteList sprite_list: SpriteList to check against
        :return: List of all overlapping Sprites from the original SpriteList
        :rtype: list
        """
        from arcade import check_for_collision_with_list

        # noinspection PyTypeChecker
        return check_for_collision_with_list(self, sprite_list)
