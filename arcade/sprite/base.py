from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, TypeVar, Any, Tuple

import arcade
from arcade.types import Point, Color, RGBA255, RGBOrA255, PointList
from arcade.color import BLACK, WHITE
from arcade.hitbox import HitBox
from arcade.texture import Texture
from arcade.utils import copy_dunders_unimplemented

if TYPE_CHECKING:
    from arcade.sprite_list import SpriteList

# Type from sprite that can be any BasicSprite or any subclass of BasicSprite
SpriteType = TypeVar("SpriteType", bound="BasicSprite")


@copy_dunders_unimplemented # See https://github.com/pythonarcade/arcade/issues/2074
class BasicSprite:
    """
    The absolute minimum needed for a sprite.

    It does not support features like rotation or changing the hitbox
    after creation. For more built-in features, please see
    :py:class:`~arcade.Sprite`.

    :param texture: The texture data to use for this sprite.
    :param scale: The scaling factor for drawing the texture.
    :param center_x: Location of the sprite along the X axis in pixels.
    :param center_y: Location of the sprite along the Y axis in pixels.
    """

    __slots__ = (
        "_position",
        "_depth",
        "_width",
        "_height",
        "_scale",
        "_color",
        "_texture",
        "_hit_box",
        "_visible",
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
        visible: bool = True,
        **kwargs: Any,
    ) -> None:
        self._position = (center_x, center_y)
        self._depth = 0.0
        self._texture = texture
        self._width = texture.width * scale
        self._height = texture.height * scale
        self._scale = scale, scale
        self._visible = bool(visible)
        self._color: Color = WHITE
        self.sprite_lists: List["SpriteList"] = []

        # Core properties we don't use, but spritelist expects it
        self._angle = 0.0

        self._hit_box = HitBox(
            self._texture.hit_box_points, self._position, self._scale
        )

    # --- Core Properties ---

    @property
    def position(self) -> Point:
        """
        Get or set the center x and y position of the sprite.

        Returns:
            (center_x, center_y)
        """
        return self._position

    @position.setter
    def position(self, new_value: Point):
        if new_value == self._position:
            return

        self._position = new_value
        self._hit_box.position = new_value
        self.update_spatial_hash()

        for sprite_list in self.sprite_lists:
            sprite_list._update_position(self)

    @property
    def center_x(self) -> float:
        """Get or set the center x position of the sprite."""
        return self._position[0]

    @center_x.setter
    def center_x(self, new_value: float):
        if new_value == self._position[0]:
            return

        self.position = (new_value, self._position[1])

    @property
    def center_y(self) -> float:
        """Get or set the center y position of the sprite."""
        return self._position[1]

    @center_y.setter
    def center_y(self, new_value: float):
        if new_value == self._position[1]:
            return

        self.position = (self._position[0], new_value)

    @property
    def depth(self) -> float:
        """
        Get or set the depth of the sprite.

        This is really the z coordinate of the sprite
        and can be used with OpenGL depth testing with opaque
        sprites.
        """
        return self._depth

    @depth.setter
    def depth(self, new_value: float):
        if new_value != self._depth:
            self._depth = new_value
            for sprite_list in self.sprite_lists:
                sprite_list._update_depth(self)

    @property
    def width(self) -> float:
        """Get or set width or the sprite in pixels"""
        return self._width

    @width.setter
    def width(self, new_value: float):
        if new_value != self._width:
            self._scale = new_value / self._texture.width, self._scale[1]
            self._hit_box.scale = self._scale
            self._width = new_value

            self.update_spatial_hash()
            for sprite_list in self.sprite_lists:
                sprite_list._update_width(self)

    @property
    def height(self) -> float:
        """Get or set the height of the sprite in pixels."""
        return self._height

    @height.setter
    def height(self, new_value: float):
        if new_value != self._height:
            self._scale = self._scale[0], new_value / self._texture.height
            self._hit_box.scale = self._scale
            self._height = new_value

            self.update_spatial_hash()
            for sprite_list in self.sprite_lists:
                sprite_list._update_height(self)

    # @property
    # def size(self) -> Point:
    #     """Get or set the size of the sprite as a pair of values."""
    #     return self._width, self._height

    # @size.setter
    # def size(self, new_value: Point):
    #     if new_value[0] != self._width or new_value[1] != self._height:
    #         self._scale = new_value[0] / self._texture.width, new_value[1] / self._texture.height
    #         self._width = new_value[0]
    #         self._height = new_value[1]

    #         self.update_spatial_hash()
    #         for sprite_list in self.sprite_lists:
    #             sprite_list._update_size(self)

    @property
    def scale(self) -> float:
        """
        Get or set the sprite's x scale value or set both x & y scale to the same value.

        .. note:: Negative values are supported. They will flip &
                  mirror the sprite.
        """
        return self._scale[0]

    @scale.setter
    def scale(self, new_value: float):
        if new_value == self._scale[0] and new_value == self._scale[1]:
            return

        self._scale = new_value, new_value
        self._hit_box.scale = self._scale
        if self._texture:
            self._width = self._texture.width * self._scale[0]
            self._height = self._texture.height * self._scale[1]

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
        self._hit_box.scale = self._scale
        if self._texture:
            self._width = self._texture.width * self._scale[0]
            self._height = self._texture.height * self._scale[1]

        self.update_spatial_hash()

        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    @property
    def left(self) -> float:
        """
        The leftmost x coordinate in the hit box.

        When setting this property the sprite is positioned
        relative to the leftmost x coordinate in the hit box.
        """
        return self._hit_box.left

    @left.setter
    def left(self, amount: float):
        leftmost = self.left
        diff = amount - leftmost
        self.center_x += diff

    @property
    def right(self) -> float:
        """
        The rightmost x coordinate in the hit box.

        When setting this property the sprite is positioned
        relative to the rightmost x coordinate in the hit box.
        """
        return self._hit_box.right

    @right.setter
    def right(self, amount: float):
        rightmost = self.right
        diff = rightmost - amount
        self.center_x -= diff

    @property
    def bottom(self) -> float:
        """
        The lowest y coordinate in the hit box.

        When setting this property the sprite is positioned
        relative to the lowest y coordinate in the hit box.
        """
        return self._hit_box.bottom

    @bottom.setter
    def bottom(self, amount: float):
        lowest = self.bottom
        diff = lowest - amount
        self.center_y -= diff

    @property
    def top(self) -> float:
        """
        The highest y coordinate in the hit box.

        When setting this property the sprite is positioned
        relative to the highest y coordinate in the hit box.
        """
        return self._hit_box.top

    @top.setter
    def top(self, amount: float):
        highest = self.top
        diff = highest - amount
        self.center_y -= diff

    @property
    def visible(self) -> bool:
        """Get or set the visibility of this sprite.

        When set to ``False``, each :py:class:`~arcade.SpriteList` and
        its attached shaders will treat the sprite as if has an
        :py:attr:`.alpha` of 0. However, the sprite's actual values for
        :py:attr:`.alpha` and :py:attr:`.color` will not change.

        .. code-block:: python

            # The initial color of the sprite
            >>> sprite.color
            Color(255, 255, 255, 255)

            # Make the sprite invisible
            >>> sprite.visible = False
            # The sprite's color value has not changed
            >>> sprite.color
            Color(255, 255, 255, 255)
            # The sprite's alpha value hasn't either
            >>> sprite.alpha
            255

            # Restore visibility
            >>> sprite.visible = True
            # Shorthand to toggle visible
            >>> sprite.visible = not sprite.visible

        """
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        value = bool(value)
        if self._visible == value:
            return

        self._visible = value

        for sprite_list in self.sprite_lists:
            sprite_list._update_color(self)

    @property
    def rgb(self) -> Tuple[int, int, int]:
        """Get or set only the sprite's RGB color components.

        If a 4-color RGBA tuple is passed:

        * The new color's alpha value will be ignored
        * The old alpha value will be preserved

        """
        return self._color[:3]

    @rgb.setter
    def rgb(self, color: RGBOrA255):

        # Fast validation of size by unpacking channel values
        try:
            r, g, b, *_a = color
            if len(_a) > 1:  # Alpha's only used to validate here
                raise ValueError()

        except ValueError as _:  # It's always a length issue
            raise ValueError((
                f"{self.__class__.__name__},rgb takes 3 or 4 channel"
                f" colors, but got {len(color)} channels"))

        # Unpack to avoid index / . overhead & prep for repack
        current_r, current_b, current_g, a = self._color

        # Do nothing if equivalent to current color
        if current_r == r and current_g == g and current_b == b:
            return

        # Preserve the current alpha value & update sprite lists
        self._color = Color(r, g, b, a)
        for sprite_list in self.sprite_lists:
            sprite_list._update_color(self)

    @property
    def color(self) -> Color:
        """
        Get or set the RGBA multiply color for the sprite.

        When setting the color, it may be specified as any of the following:

        * an RGBA :py:class:`tuple` with each channel value between 0 and 255
        * an instance of :py:class:`~arcade.types.Color`
        * an RGB :py:class:`tuple`, in which case the color will be treated as opaque

        Example usage::

            >>> print(sprite.color)
            Color(255, 255, 255, 255)

            >>> sprite.color = arcade.color.RED

            >>> sprite.color = 255, 0, 0

            >>> sprite.color = 255, 0, 0, 128

        """
        return self._color

    @color.setter
    def color(self, color: RGBOrA255):
        if color == self._color:
            return

        r, g, b, *_a = color

        if _a:
            if len(_a) > 1:
                raise ValueError(f"iterable must unpack to 3 or 4 values not {len(color)}")
            a = _a[0]
        else:
            a = self._color.a

        # We don't handle alpha and .visible interactions here
        # because it's implemented in SpriteList._update_color
        self._color = Color(r, g, b, a)

        for sprite_list in self.sprite_lists:
            sprite_list._update_color(self)

    @property
    def alpha(self) -> int:
        """Get or set the alpha value of the sprite"""
        return self._color[3]

    @alpha.setter
    def alpha(self, alpha: int):
        self._color = Color(self._color[0], self._color[1], self._color[2], int(alpha))

        for sprite_list in self.sprite_lists:
            sprite_list._update_color(self)

    @property
    def texture(self) -> Texture:
        """
        Get or set the visible texture for this sprite
        This property can be changed over time to animate a sprite.

        Note that this doesn't change the hit box of the sprite.
        """
        return self._texture

    @texture.setter
    def texture(self, texture: Texture):
        if texture == self._texture:
            return

        if __debug__ and not isinstance(texture, Texture):
            raise TypeError(
                f"The 'texture' parameter must be an instance of arcade.Texture,"
                f" but is an instance of '{type(texture)}'."
            )

        self._texture = texture
        self._width = texture.width * self._scale[0]
        self._height = texture.height * self._scale[1]
        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_texture(self)

    # ---- Update methods ----

    def update(self) -> None:
        """
        Generic update method. It can be called manually
        or by the SpriteList's update method.
        """
        pass

    def on_update(self, delta_time: float = 1 / 60) -> None:
        """
        Update the sprite. Similar to update, but also takes a delta-time.
        It can be called manually or by the SpriteList's on_update method.

        :param delta_time: Time since last update.
        """
        pass

    def update_animation(self, delta_time: float = 1 / 60) -> None:
        """
        Generic update animation method. Usually involves changing
        the active texture on the sprite.

        This can be called manually or by the SpriteList's update_animation method.

        :param delta_time: Time since last update.
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
        self.scale_xy = self._scale[0] * factor, self._scale[1] * factor
        if self._texture:
            self._width = self._texture.width * self._scale[0]
            self._height = self._texture.height * self._scale[1]

        # detect the edge case where distance to multiply is zero
        position_changed = point != self._position

        # be lazy about math; only do it if we have to
        if position_changed:
            self.position = (
                (self._position[0] - point[0]) * factor + point[0],
                (self._position[1] - point[1]) * factor + point[1],
            )

        # rebuild all spatial metadata
        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)
            if position_changed:
                sprite_list._update_position(self)

    def rescale_xy_relative_to_point(
        self, point: Point, factors_xy: Iterable[float]
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
        self.scale_xy = self._scale[0] * factor_x, self._scale[1] * factor_y
        if self._texture:
            self._width = self._texture.width * self._scale[0]
            self._height = self._texture.height * self._scale[1]

        # detect the edge case where the distance to multiply is 0
        position_changed = point != self._position

        # be lazy about math; only do it if we have to
        if position_changed:
            self.position = (
                (self._position[0] - point[0]) * factor_x + point[0],
                (self._position[1] - point[1]) * factor_y + point[1],
            )

        # rebuild all spatial metadata
        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)
            if position_changed:
                sprite_list._update_position(self)

    # ---- Utility Methods ----

    @property
    def hit_box(self) -> HitBox:
        return self._hit_box

    def update_spatial_hash(self) -> None:
        """
        Update the sprites location in the spatial hash if present.
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
        while len(self.sprite_lists) > 0:
            self.sprite_lists[0].remove(self)

        self.sprite_lists.clear()

    # ----- Drawing Methods -----

    def draw_hit_box(self, color: RGBA255 = BLACK, line_thickness: float = 2.0) -> None:
        """
        Draw a sprite's hit-box. This is useful for debugging.

        :param color: Color of box
        :param line_thickness: How thick the box should be
        """
        points: PointList = self.hit_box.get_adjusted_points()
        # NOTE: This is a COPY operation. We don't want to modify the points.
        points = tuple(points) + tuple(points[:-1])
        arcade.draw_line_strip(points, color=color, line_width=line_thickness)

    # ---- Shortcut Methods ----

    def kill(self) -> None:
        """
        Alias of ``remove_from_sprite_lists()``.
        """
        self.remove_from_sprite_lists()

    def collides_with_point(self, point: Point) -> bool:
        """
        Check if point is within the current sprite.

        :param point: Point to check.
        :return: True if the point is contained within the sprite's boundary.
        """
        from arcade.geometry import is_point_in_polygon

        x, y = point
        return is_point_in_polygon(x, y, self.hit_box.get_adjusted_points())

    def collides_with_sprite(self: SpriteType, other: SpriteType) -> bool:
        """Will check if a sprite is overlapping (colliding) another Sprite.

        :param other: the other sprite to check against.
        :return: True or False, whether or not they are overlapping.
        """
        from arcade import check_for_collision

        return check_for_collision(self, other)

    def collides_with_list(
        self: SpriteType, sprite_list: "SpriteList"
    ) -> List[SpriteType]:
        """Check if current sprite is overlapping with any other sprite in a list

        :param sprite_list: SpriteList to check against
        :return: List of all overlapping Sprites from the original SpriteList
        """
        from arcade import check_for_collision_with_list

        # noinspection PyTypeChecker
        return check_for_collision_with_list(self, sprite_list)
