import math
from math import cos, radians, sin
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from arcade import Texture, load_texture
from arcade.hitbox import AdjustableHitBox, HitBox
from arcade.math import get_angle_degrees
from arcade.texture import get_default_texture
from arcade.types import PathOrTexture, Point, PointList

from .base import BasicSprite
from .mixins import PymunkMixin

if TYPE_CHECKING:  # handle import cycle caused by type hinting
    from arcade.sprite_list import SpriteList


class Sprite(BasicSprite, PymunkMixin):
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

    __slots__ = (
        "_velocity",
        "change_angle",
        "_properties",
        "boundary_left",
        "boundary_right",
        "boundary_top",
        "boundary_bottom",
        "textures",
        "cur_texture_index",
        "_hit_box_points",
        "_hit_box_points_cache",
        "physics_engines",
        "_sprite_list",
        "guid",
        "force",
    )

    def __init__(
        self,
        path_or_texture: PathOrTexture = None,
        scale: float = 1.0,
        center_x: float = 0.0,
        center_y: float = 0.0,
        angle: float = 0.0,
        **kwargs,
    ):
        if isinstance(path_or_texture, Texture):
            _texture = path_or_texture
            _textures = [_texture]
        elif isinstance(path_or_texture, (str, Path)):
            _texture = load_texture(path_or_texture)
            _textures = [_texture]
        else:
            _texture = get_default_texture()
            # Backwards compatibility:
            # When applying default texture we don't want
            # it part of the animating ones
            _textures = []
        super().__init__(
            _texture,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
            **kwargs,
        )
        PymunkMixin.__init__(self)

        self.angle = angle
        # Movement
        self._velocity = 0.0, 0.0
        self.change_angle: float = 0.0

        # Custom sprite properties
        self._properties: Optional[Dict[str, Any]] = None

        # Boundaries for moving platforms in tilemaps
        self.boundary_left: Optional[float] = None
        self.boundary_right: Optional[float] = None
        self.boundary_top: Optional[float] = None
        self.boundary_bottom: Optional[float] = None

        self.cur_texture_index: int = 0
        self.textures: List[Texture] = _textures

        self._hit_box: AdjustableHitBox = AdjustableHitBox(
            points=self._texture.hit_box.points,
            position=self._position,
            angle=self.angle,
            scale=self._scale,
        )
        print(dir(self._hit_box))
        self.physics_engines: List[Any] = []

        self._sprite_list: Optional[SpriteList] = None
        # Debug properties
        self.guid: Optional[str] = None

        self._width = self._texture.width * scale
        self._height = self._texture.height * scale

    # --- Properties ---

    @BasicSprite.center_x.setter
    def center_x(self, new_value: float):
        BasicSprite.center_x.fset(self, new_value)
        self._hit_box.position = (new_value, self._position[1])

    @BasicSprite.center_y.setter
    def center_y(self, new_value: float):
        BasicSprite.center_y.fset(self, new_value)
        self._hit_box.position = (self._position[0], new_value)

    @BasicSprite.position.setter
    def position(self, new_value: Point):
        BasicSprite.position.fset(self, new_value)
        self._hit_box.position = new_value

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
    def angle(self) -> float:
        """
        Get or set the rotation or the sprite.

        The value is in degrees and is clockwise.
        """
        return self._angle

    @angle.setter
    def angle(self, new_value: float):
        if new_value == self._angle:
            return

        self._angle = new_value
        self._hit_box.angle = new_value

        for sprite_list in self.sprite_lists:
            sprite_list._update_angle(self)

        self.update_spatial_hash()

    @property
    def radians(self) -> float:
        """
        Get or set the rotation of the sprite in radians.

        The value is in radians and is clockwise.
        """
        return self._angle / 180.0 * math.pi

    @radians.setter
    def radians(self, new_value: float):
        self.angle = new_value * 180.0 / math.pi

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
        """Get or set the velocity in the x plane of the sprite."""
        return self.velocity[0]

    @change_x.setter
    def change_x(self, new_value: float):
        self._velocity = new_value, self._velocity[1]

    @property
    def change_y(self) -> float:
        """Get or set the velocity in the y plane of the sprite."""
        return self.velocity[1]

    @change_y.setter
    def change_y(self, new_value: float):
        self._velocity = self._velocity[0], new_value

    @property
    def hit_box(self) -> HitBox:
        """
        Get or set the hit box for this sprite.
        """
        return self.get_hit_box()

    @hit_box.setter
    def hit_box(self, hit_box: HitBox):
        self.set_hit_box(hit_box)

    @property
    def texture(self) -> Texture:
        """Get or set the active texture for this sprite"""
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

        # If sprite is using default texture, update the hit box
        if self._texture is get_default_texture():
            self.hit_box = texture.hit_box.create_adjustable(
                position=self._position, angle=self.angle, scale=self._scale
            )

        self._texture = texture
        self._width = texture.width * self._scale[0]
        self._height = texture.height * self._scale[1]
        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_texture(self)

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

    # --- Hitbox methods -----

    def set_hit_box(self, hit_box: AdjustableHitBox) -> None:
        """
        Set a sprite's hit box. Hit box should be relative to a sprite's center,
        and with a scale of 1.0.

        Points will be scaled and rotated with ``get_adjusted_hit_box``.
        """
        self._hit_box = hit_box

    def get_hit_box(self) -> HitBox:
        """
        Use the hit_box property to get or set a sprite's hit box.
        Hit boxes are specified assuming the sprite's center is at (0, 0).
        Specify hit boxes like:

        .. code-block::

            mySprite.hit_box = [[-10, -10], [10, -10], [10, 10]]

        Specify a hit box unadjusted for translation, rotation, or scale.
        You can get an adjusted hit box with :class:`arcade.Sprite.get_adjusted_hit_box`.
        """
        return self._hit_box

    def get_adjusted_hit_box(self) -> PointList:
        return self._hit_box.get_adjusted_points()

    # --- Movement methods -----

    def forward(self, speed: float = 1.0) -> None:
        """
        Adjusts a Sprite's movement vector forward.
        This method does not actually move the sprite, just takes the current
        change_x/change_y and adjusts it by the speed given.

        :param speed: speed factor
        """
        self.velocity = (
            self._velocity[0] + math.cos(self.radians) * speed,
            self._velocity[1] + math.sin(self.radians) * speed,
        )

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
        self.angle = self._angle - theta

    def turn_left(self, theta: float = 90.0) -> None:
        """
        Rotate the sprite left by the passed number of degrees.

        :param theta: change in angle, in degrees
        """
        self.angle = self._angle + theta

    def stop(self) -> None:
        """
        Stop the Sprite's motion by setting the velocity and angle change to 0.
        """
        self.velocity = 0, 0
        self.change_angle = 0

    def face_point(self, point: Point) -> None:
        """
        Face the sprite towards a point. Assumes sprite image is facing upwards.

        :param Point point: Point to face towards.
        """
        angle = get_angle_degrees(self.center_x, self.center_y, point[0], point[1])

        # Reverse angle because sprite angles are backwards
        self.angle = -angle

    # ---- Draw Methods ----

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
        self._sprite_list.draw(
            filter=filter, pixelated=pixelated, blend_function=blend_function
        )
        self._sprite_list.remove(self)

    # ----Update Methods ----

    def update(self) -> None:
        """
        The default update method for a Sprite. Can be overridden by a subclass.

        This method moves the sprite based on its velocity and angle change.
        """
        self.position = (
            self._position[0] + self.change_x,
            self._position[1] + self.change_y,
        )
        self.angle += self.change_angle

    # ----Utility Methods----

    def update_spatial_hash(self) -> None:
        """
        Update the sprites location in the spatial hash.
        """
        # self._hit_box._adjusted_cache_dirty = True
        # super().update_spatial_hash()
        for sprite_list in self.sprite_lists:
            if sprite_list.spatial_hash is not None:
                sprite_list.spatial_hash.move(self)

    def append_texture(self, texture: Texture):
        """
        Appends a new texture to the list of textures that can be
        applied to this sprite.

        :param arcade.Texture texture: Texture to add to the list of available textures

        """
        self.textures.append(texture)

    def set_texture(self, texture_no: int) -> None:
        """
        Set the current texture by texture number.
        The number is the index into ``self.textures``.

        :param int texture_no: Index into ``self.textures``
        """
        texture = self.textures[texture_no]
        self.texture = texture

    def remove_from_sprite_lists(self) -> None:
        """
        Remove this sprite from all sprite lists it is in
        including registered physics engines.
        """
        super().remove_from_sprite_lists()
        for engine in self.physics_engines:
            engine.remove_sprite(self)

        self.physics_engines.clear()

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
        self.physics_engines.append(physics_engine)
