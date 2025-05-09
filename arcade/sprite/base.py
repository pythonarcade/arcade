from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, TypeVar

import arcade
from arcade.color import BLACK, WHITE
from arcade.exceptions import ReplacementWarning, warning
from arcade.hitbox import HitBox
from arcade.texture import Texture
from arcade.types import LRBT, AsFloat, Color, Point, Point2, Point2List, Rect, RGBOrA255
from arcade.utils import copy_dunders_unimplemented

if TYPE_CHECKING:
    from arcade.sprite_list import SpriteList

# Type from sprite that can be any BasicSprite or any subclass of BasicSprite
SpriteType = TypeVar("SpriteType", bound="BasicSprite")

# Same as SpriteType, for covariant type parameters
SpriteType_co = TypeVar("SpriteType_co", bound="BasicSprite", covariant=True)


@copy_dunders_unimplemented  # See https://github.com/pythonarcade/arcade/issues/2074
class BasicSprite:
    """
    The absolute minimum needed for a sprite.

    It does not support features like rotation or changing the hitbox
    after creation. For more built-in features, please see
    :py:class:`~arcade.Sprite`.

    Args:
        texture:
            The texture data to use for this sprite.
        scale:
            The scaling factor for drawing the texture.
        center_x:
            Location of the sprite along the X axis in pixels.
        center_y:
            Location of the sprite along the Y axis in pixels.
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
        scale: float | Point2 = 1.0,
        center_x: float = 0,
        center_y: float = 0,
        visible: bool = True,
        **kwargs: Any,
    ) -> None:
        self._position = (center_x, center_y)
        self._depth = 0.0
        self._texture = texture
        width, height = texture.size
        self._scale = (scale, scale) if isinstance(scale, float | int) else (scale[0], scale[1])  # noqa: UP038
        self._width = width * self._scale[0]
        self._height = height * self._scale[1]
        self._visible = bool(visible)
        self._color: Color = WHITE

        # In a more powerful type system, this would be typed as
        # list[SpriteList[? super Self]]
        # i.e., a list of SpriteList's with varying type arguments, but where
        # each of those type arguments is known to be a supertype of Self.
        # All changes to this list should go through the pair of methods
        # register_sprite_list, _unregister_sprite_list.
        # They ensure that the above typing invariant is preserved.
        self.sprite_lists: list[SpriteList[Any]] = []
        """The sprite lists this sprite is a member of"""

        # Core properties we don't use, but spritelist expects it
        self._angle = 0.0

        self._hit_box = HitBox(self._texture.hit_box_points, self._position, self._scale)

    # --- Core Properties ---

    @property
    def position(self) -> Point2:
        """Get or set the center x and y position of the sprite."""
        return self._position

    @position.setter
    def position(self, new_value: Point2):
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

    @property
    def size(self) -> Point:
        """
        Get or set the size of the sprite as a pair of values.

        This is faster than getting or setting width and height separately.
        """
        return self._width, self._height

    @size.setter
    def size(self, new_value: Point2):
        try:
            width, height = new_value
        except ValueError:
            raise ValueError(
                "size must be a tuple-like object which unpacks to exactly 2 coordinates"
            )
        except TypeError:
            raise TypeError(
                "size must be a tuple-like object which unpacks to exactly 2 coordinates"
            )

        if width != self._width or height != self._height:
            texture_width, texture_height = self._texture.size
            self._scale = width / texture_width, height / texture_height
            self._hit_box.scale = self._scale
            self._width = width
            self._height = height

            self.update_spatial_hash()

            for sprite_list in self.sprite_lists:
                sprite_list._update_size(self)

    @property
    def scale_x(self) -> float:
        """
        Get or set the sprite's x scale value.

        .. note:: Negative values are supported. They will flip &
                  mirror the sprite.
        """
        return self._scale[0]

    @scale_x.setter
    def scale_x(self, new_scale_x: AsFloat):
        old_scale_x, old_scale_y = self._scale
        if new_scale_x == old_scale_x:
            return

        new_scale = (new_scale_x, old_scale_y)

        # Apply scale to hitbox first to raise any exceptions quickly
        self._hit_box.scale = new_scale
        self._scale = new_scale
        self._width = self._texture.width * new_scale_x

        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    @property
    def scale_y(self) -> float:
        """
        Get or set the sprite's y scale value.

        .. note:: Negative values are supported. They will flip &
                  mirror the sprite.
        """
        return self._scale[1]

    @scale_y.setter
    def scale_y(self, new_scale_y: AsFloat):
        old_scale_x, old_scale_y = self._scale
        if new_scale_y == old_scale_y:
            return

        new_scale = (old_scale_x, new_scale_y)

        # Apply scale to hitbox first to raise any exceptions quickly
        self._hit_box.scale = new_scale
        self._scale = new_scale
        self._height = self._texture.height * new_scale_y

        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    @property
    def scale(self) -> Point2:
        """Get or set the x & y scale of the sprite as a pair of values.
        You may set both the x & y with a single scalar, but scale will always return
        a length 2 tuple of the x & y scale

        See :py:attr:`.scale_x` and :py:attr:`.scale_y` for individual access.

        See :py:meth:`.scale_multiply_uniform` for uniform scaling.

        .. note:: Negative scale values are supported.

            This applies to both single-axis and dual-axis.
            Negatives will flip & mirror the sprite, but the
            with will use :py:func:`abs` to report total width
            and height instead of negatives.

        """
        return self._scale

    @scale.setter
    def scale(self, new_scale: Point2 | AsFloat):
        if isinstance(new_scale, float | int):
            scale_x = new_scale
            scale_y = new_scale

        else:  # Treat it as some sort of iterable or sequence
            # Don't abstract this. Keep it here since it's a hot code path
            try:
                scale_x, scale_y = new_scale  # type / length implicit check
            except ValueError:
                raise ValueError(
                    "scale must be a tuple-like object which unpacks to exactly 2 coordinates"
                )
            except TypeError:
                raise TypeError(
                    "scale must be a tuple-like object which unpacks to exactly 2 coordinates"
                )

        new_scale = scale_x, scale_y
        if new_scale == self._scale:
            return

        self._hit_box.scale = new_scale
        tex_width, tex_height = self._texture.size
        self._scale = new_scale
        self._width = tex_width * scale_x
        self._height = tex_height * scale_y

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
    def rect(self) -> Rect:
        """A rectangle with with the sprites left, right, bottom, and top values."""
        return LRBT(self.left, self.right, self.bottom, self.top)

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
    def rgb(self) -> tuple[int, int, int]:
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

        except ValueError:  # It's always a length issue
            raise ValueError(
                f"{self.__class__.__name__},rgb takes 3 or 4 channel"
                f" colors, but got {len(color)} channels"
            )

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
        """
        Get or set the alpha value of the sprite.

        Will be clamped to the range 0-255.
        """
        return self._color[3]

    @alpha.setter
    def alpha(self, alpha: int):
        self._color = Color(
            self._color[0], self._color[1], self._color[2], max(0, min(255, int(alpha)))
        )

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

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        """
        Generic update method. It can be called manually
        or by the SpriteList's update method.

        Args:
            delta_time: Time since last update in seconds
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        pass

    def update_animation(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        """
        Generic update animation method. Usually involves changing
        the active texture on the sprite.

        This can be called manually or by the SpriteList's update_animation method.

        Args:
            delta_time: Time since last update in seconds
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        pass

    # --- Scale methods -----

    def add_scale(self, factor: AsFloat) -> None:
        """Add to the sprite's scale by the factor.
        This adds the factor to both the x and y scale values.

        Args:
            factor: The factor to add to the sprite's scale.
        """
        self._scale = self._scale[0] + factor, self._scale[1] + factor
        self._hit_box.scale = self._scale
        tex_width, tex_height = self._texture.size
        self._width = tex_width * self._scale[0]
        self._height = tex_height * self._scale[1]

        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    def multiply_scale(self, factor: AsFloat) -> None:
        """multiply the sprite's scale by the factor.
        This multiplies both the x and y scale values by the factor.

        Args:
            factor: The factor to scale up the sprite by.
        """

        self._scale = self._scale[0] * factor, self._scale[1] * factor
        self._hit_box.scale = self._scale
        tex_width, tex_height = self._texture.size
        self._width = tex_width * factor
        self._height = tex_height * factor

        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    def rescale_relative_to_point(self, point: Point2, scale_by: AsFloat | Point2) -> None:
        """Rescale the sprite and its distance from the passed point.

        This function does two things:

        1. Multiply both values in the sprite's :py:attr:`.scale`
           value by the values in ``scale_by``:

           * If ``scale_by`` is an :py:class:`int` or :py:class:`float`,
             use it for both the x and y axes
           * If ``scale_by`` is a tuple-like object which unpacks to
             two numbers, then use
           * Otherwise, raise an exception

        2. Scale the distance between the sprite and ``point`` by
           ``factor``.

        .. note:: If ``point`` equals the sprite's :py:attr:`.position`
                  the distance will be zero and the sprite won't move.

        Args:
            point:
                The point to scale relative to.
            scale_by:
                A multiplier for both the sprite scale and its distance
                from the point. Note that although factor may be negative,
                it may have unexpected effects.

        """
        # abort if the multiplier wouldn't do anything
        if isinstance(scale_by, float | int):
            if scale_by == 1.0:
                return
            factor_x = scale_by
            factor_y = scale_by
        else:
            try:
                factor_x, factor_y = scale_by
                if factor_x == 1.0 and factor_y == 1.0:
                    return
            except ValueError:
                raise ValueError(
                    "factor must be a float, int, or tuple-like "
                    "which unpacks as two float-like values"
                )
            except TypeError:
                raise TypeError(
                    "factor must be a float, int, or tuple-like unpacks as two float-like values"
                )

        # set the scale and, if this sprite has a texture, the size data
        old_scale_x, old_scale_y = self._scale
        new_scale_x = old_scale_x * factor_x
        new_scale_y = old_scale_y * factor_y
        self._scale = new_scale_x, new_scale_y

        tex_width, tex_height = self._texture.size
        self._width = tex_width * new_scale_x
        self._height = tex_height * new_scale_y

        # If the scaling point is the sprite's center, it doesn't move
        old_position = self._position
        position_changed = point != old_position  # Stored to use below

        # be lazy about math; only do it if we have to
        if position_changed:
            point_x, point_y = point
            old_x, old_y = old_position
            self.position = (
                (old_x - point_x) * factor_x + point_x,
                (old_y - point_y) * factor_y + point_y,
            )

        # rebuild all spatial metadata
        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)
            if position_changed:
                sprite_list._update_position(self)

    @warning(warning_type=ReplacementWarning, new_name="rescale_relative_to_point")
    def rescale_xy_relative_to_point(self, point: Point, factors_xy: Iterable[float]) -> None:
        """Rescale the sprite and its distance from the passed point.

        .. deprecated:: 3.0
           Use :py:meth:`.rescale_relative_to_point` instead.

           This was added during the 3.0 development cycle before scale was
           made into a vector quantity.

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

        Args:
            point:
                The reference point for rescaling.
            factors_xy:
                A 2-length iterable containing x and y
                multipliers for ``scale`` & distance to ``point``.
        """
        self.rescale_relative_to_point(point, factors_xy)  # type: ignore

    # ---- Utility Methods ----

    @property
    def hit_box(self) -> HitBox:
        """The hit box for this sprite."""
        return self._hit_box

    def update_spatial_hash(self) -> None:
        """Update the sprites location in the spatial hash if present."""
        for sprite_list in self.sprite_lists:
            if sprite_list.spatial_hash is not None:
                sprite_list.spatial_hash.move(self)

    def register_sprite_list(self: SpriteType, new_list: SpriteList[SpriteType]) -> None:
        """
        Register this sprite as belonging to a list.

        We will automatically remove ourselves from the list when kill() is called.
        """
        self.sprite_lists.append(new_list)

    def _unregister_sprite_list(self: SpriteType, new_list: SpriteList[SpriteType]) -> None:
        """Unregister this sprite as belonging to a list."""
        self.sprite_lists.remove(new_list)

    def remove_from_sprite_lists(self) -> None:
        """Remove the sprite from all sprite lists."""
        while len(self.sprite_lists) > 0:
            self.sprite_lists[0].remove(self)

    # ----- Drawing Methods -----

    def draw_hit_box(self, color: RGBOrA255 = BLACK, line_thickness: float = 2.0) -> None:
        """
        Draw a sprite's hit-box. This is useful for debugging.

        Args:
            color:
                Color of box
            line_thickness:
                How thick the box should be
        """
        converted_color = Color.from_iterable(color)
        points: Point2List = self.hit_box.get_adjusted_points()
        # NOTE: This is a COPY operation. We don't want to modify the points.
        points = tuple(points) + tuple(points[:-1])
        arcade.draw_line_strip(points, color=converted_color, line_width=line_thickness)

    # ---- Shortcut Methods ----

    def kill(self) -> None:
        """
        Alias of ``remove_from_sprite_lists()``.
        """
        self.remove_from_sprite_lists()

    def collides_with_point(self, point: Point2) -> bool:
        """
        Check if point is within the current sprite.

        Args:
            point: Point to check.
        Returns:
            ``True`` if the point is contained within the sprite's boundary.
        """
        from arcade.geometry import is_point_in_polygon

        x, y = point
        return is_point_in_polygon(x, y, self.hit_box.get_adjusted_points())

    def collides_with_sprite(self, other: BasicSprite) -> bool:
        """Will check if a sprite is overlapping (colliding) another Sprite.

        Args:
            other: the other sprite to check against.
        Returns:
            ``True`` or ``False``, whether or not they are overlapping.
        """
        from arcade import check_for_collision

        return check_for_collision(self, other)

    def collides_with_list(self, sprite_list: SpriteList[SpriteType]) -> list[SpriteType]:
        """Check if current sprite is overlapping with any other sprite in a list

        Args:
            sprite_list: SpriteList to check against
        Returns:
            List of all overlapping Sprites from the original SpriteList
        """
        from arcade import check_for_collision_with_list

        return check_for_collision_with_list(self, sprite_list)
