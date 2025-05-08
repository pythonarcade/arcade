import math
from pathlib import Path
from typing import Any

import arcade
from arcade import Texture
from arcade.hitbox import HitBox, RotatableHitBox
from arcade.texture import get_default_texture
from arcade.types import PathOrTexture, Point2

from .base import BasicSprite
from .mixins import PymunkMixin

__all__ = ["Sprite"]


class Sprite(BasicSprite, PymunkMixin):
    """
    Sprites are used to render image data to the screen & perform collisions.

    Most games center around sprites. They are most frequently used as follows:

    1. Create ``Sprite`` instances from image data
    2. Add the sprites to a :py:class:`~arcade.SpriteList` instance
    3. Call :py:meth:`SpriteList.draw() <arcade.SpriteList.draw>` on the
       instance inside your ``on_draw`` method.

    For runnable examples of how to do this, please see Arcade's
    :ref:`built-in Sprite examples <sprites>`.

    .. tip:: Advanced users should see :py:class:`~arcade.BasicSprite`

        It uses fewer resources at the cost of having fewer features.

    Args:
        path_or_texture:
            Path to an image file, or a texture object.
        center_x:
            Location of the sprite in pixels.
        center_y:
            Location of the sprite in pixels.
        scale:
            Show the image at this many times its original size.
        angle:
            The initial rotation of the sprite in degrees
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
        "_hit_box",
        "physics_engines",
        "guid",
        "force",
    )

    def __init__(
        self,
        path_or_texture: PathOrTexture | None = None,
        scale: float | Point2 = 1.0,
        center_x: float = 0.0,
        center_y: float = 0.0,
        angle: float = 0.0,
        **kwargs: Any,
    ) -> None:
        if isinstance(path_or_texture, Texture):
            _texture = path_or_texture
            _textures = [_texture]
        elif isinstance(path_or_texture, str | Path):
            _texture = arcade.texture.default_texture_cache.load_or_get_texture(path_or_texture)
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

        self._angle = angle
        # Movement
        self._velocity = 0.0, 0.0
        self.change_angle: float = 0.0
        """Change in angle per 1/60th of a second."""

        # Custom sprite properties
        self._properties: dict[str, Any] | None = None

        # Boundaries for moving platforms in tilemaps
        self.boundary_left: float | None = None
        """
        :py:class:`~arcade.physics_engines.PhysicsEnginePlatformer`
        uses this as the left boundary for moving
        :py:attr:`~arcade.physics_engines.PhysicsEnginePlatformer.platforms`.
        """

        self.boundary_right: float | None = None
        """
        :py:class:`~arcade.physics_engines.PhysicsEnginePlatformer`
        uses this as the right boundary for moving
        :py:attr:`~arcade.physics_engines.PhysicsEnginePlatformer.platforms`.
        """

        self.boundary_top: float | None = None
        """
        :py:class:`~arcade.physics_engines.PhysicsEnginePlatformer`
        uses this as the top boundary for moving
        :py:attr:`~arcade.physics_engines.PhysicsEnginePlatformer.platforms`.
        """

        self.boundary_bottom: float | None = None
        """
        :py:class:`~arcade.physics_engines.PhysicsEnginePlatformer`
        uses this as the top boundary for moving
        :py:attr:`~arcade.physics_engines.PhysicsEnginePlatformer.platforms`.
        """

        self.cur_texture_index: int = 0
        """Current texture index for sprite animation."""
        self.textures: list[Texture] = _textures
        """List of textures stored in the sprite."""

        self.physics_engines: list[Any] = []
        """List of physics engines that have registered this sprite."""

        # Debug properties
        self.guid: str | None = None
        """A unique id for debugging purposes."""

        self._hit_box: RotatableHitBox = self._hit_box.create_rotatable(angle=self._angle)

        self._width = self._texture.width * self._scale[0]
        self._height = self._texture.height * self._scale[1]

    # --- Properties ---

    @property
    def angle(self) -> float:
        """
        Get or set the rotation or the sprite.

        The value is in degrees and is clockwise.
        """
        return self._angle

    @angle.setter
    def angle(self, new_value: float) -> None:
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
    def radians(self, new_value: float) -> None:
        self.angle = new_value * 180.0 / math.pi

    @property
    def velocity(self) -> Point2:
        """
        Get or set the velocity of the sprite.

        The x and y velocity can also be set separately using the
        ``sprite.change_x`` and ``sprite.change_y`` properties.

        Example::

            sprite.velocity = 1.0, 0.0
        """
        return self._velocity

    @velocity.setter
    def velocity(self, new_value: Point2) -> None:
        self._velocity = new_value

    @property
    def change_x(self) -> float:
        """Get or set the velocity in the x plane of the sprite."""
        return self.velocity[0]

    @change_x.setter
    def change_x(self, new_value: float) -> None:
        self._velocity = new_value, self._velocity[1]

    @property
    def change_y(self) -> float:
        """Get or set the velocity in the y plane of the sprite."""
        return self.velocity[1]

    @change_y.setter
    def change_y(self, new_value: float) -> None:
        self._velocity = self._velocity[0], new_value

    @property
    def hit_box(self) -> HitBox:
        """Get or set the hit box for this sprite."""
        return self._hit_box

    @hit_box.setter
    def hit_box(self, hit_box: HitBox | RotatableHitBox) -> None:
        if type(hit_box) is HitBox:
            self._hit_box = hit_box.create_rotatable(self.angle)
        else:
            # Mypy doesn't seem to understand the type check above
            # It still thinks hit_box can be a union here
            self._hit_box = hit_box  # type: ignore

    @property
    def texture(self) -> Texture:
        """Get or set the active texture for this sprite"""
        return self._texture

    @texture.setter
    def texture(self, texture: Texture) -> None:
        if texture == self._texture:
            return

        if __debug__ and not isinstance(texture, Texture):
            raise TypeError(
                f"The 'texture' parameter must be an instance of arcade.Texture,"
                f" but is an instance of '{type(texture)}'."
            )

        # If sprite is using default texture, update the hit box
        if self._texture is get_default_texture():
            self.hit_box = RotatableHitBox(
                texture.hit_box_points,
                position=self._position,
                angle=self.angle,
                scale=self._scale,
            )

        self._texture = texture
        self._width = texture.width * self._scale[0]
        self._height = texture.height * self._scale[1]
        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_texture(self)

    @property
    def properties(self) -> dict[str, Any]:
        """Get or set custom sprite properties."""
        if self._properties is None:
            self._properties = {}
        return self._properties

    @properties.setter
    def properties(self, value: dict[str, Any]) -> None:
        self._properties = value

    # --- Movement methods -----

    def forward(self, speed: float = 1.0) -> None:
        """
        Adjusts a Sprites forward.

        Args:
            speed: The speed at which the sprite moves.
        """
        angle_rad = math.radians(self.angle)
        self.center_x += math.sin(angle_rad) * speed
        self.center_y += math.cos(angle_rad) * speed

    def reverse(self, speed: float = 1.0) -> None:
        """
        Adjusts a Sprite backwards.

        Args:
            speed: The speed at which the sprite moves.
        """
        self.forward(-speed)

    def strafe(self, speed: float = 1.0) -> None:
        """
        Adjusts a Sprite sideways.

        Args:
            speed: The speed at which the sprite moves.
        """
        angle_rad = math.radians(self.angle + 90)
        self.center_x += math.sin(angle_rad) * speed
        self.center_y += math.cos(angle_rad) * speed

    def turn_right(self, theta: float = 90.0) -> None:
        """
        Rotate the sprite right by the passed number of degrees.

        Args:
            theta: Change in angle, in degrees
        """
        self.angle = self._angle + theta

    def turn_left(self, theta: float = 90.0) -> None:
        """
        Rotate the sprite left by the passed number of degrees.

        Args:
            theta: Change in angle, in degrees
        """
        self.angle = self._angle - theta

    def stop(self) -> None:
        """
        Stop the Sprite's motion by setting the velocity and angle change to 0.
        """
        self.velocity = 0, 0
        self.change_angle = 0.0

    # ----Update Methods ----

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        """
        The default update method for a Sprite. Can be overridden by a subclass.

        This method moves the sprite based on its velocity and angle change.

        Args:
            delta_time: Time since last update in seconds
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        # NOTE: change_x and change_y (or velocity) are historically defined as
        # the change in position per frame. To convert to change in position per
        # second, we multiply by 60 (frames per second).
        # Users can define these values in any unit they want, but this breaks
        # compatibility with physics engines. Consider changing this in the future.
        delta_time *= 60
        self.position = (
            self._position[0] + self.change_x * delta_time,
            self._position[1] + self.change_y * delta_time,
        )
        self.angle += self.change_angle * delta_time

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

    def append_texture(self, texture: Texture) -> None:
        """
        Appends a new texture to the list of textures that can be
        applied to this sprite.

        Args:
            texture: Texture to add to the list of available textures
        """
        self.textures.append(texture)

    def set_texture(self, texture_no: int) -> None:
        """
        Set the current texture by texture number.
        The number is the index into ``self.textures``.

        Args:
            texture_no: Index into ``self.textures``
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

    def register_physics_engine(self, physics_engine: Any) -> None:
        """
        Register a physics engine on the sprite.
        This is only needed if you actually need a reference
        to your physics engine in the sprite itself.
        It has no other purposes.

        The registered physics engines can be accessed
        through the ``physics_engines`` attribute.

        It can for example be the pymunk physics engine
        or a custom one you made.

        Args:
            physics_engine: The physics engine to register
        """
        self.physics_engines.append(physics_engine)

    def sync_hit_box_to_texture(self) -> None:
        """
        Update the sprite's hit box to match the current texture's hit box.
        """
        self.hit_box = RotatableHitBox(
            self.texture.hit_box_points,
            position=self._position,
            angle=self.angle,
            scale=self._scale,
        )
