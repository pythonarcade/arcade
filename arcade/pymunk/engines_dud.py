"""
Pymunk Physics Engine
"""

from __future__ import annotations

from .dud import DudImplimentationError, DudImportError

from typing import Callable, TYPE_CHECKING

from pyglet.math import Vec2

if TYPE_CHECKING:
    from arcade import Sprite

__all__ = ["PymunkPhysicsObject", "PymunkException", "PymunkPhysicsEngine"]

from arcade.utils import copy_dunders_unimplemented


class PymunkPhysicsObject:
    """Object that holds pymunk body/shape for a sprite."""

    def __init__(self, body=None, shape=None):
        raise DudImplimentationError


class PymunkException(Exception):
    """Exception raised for errors in the PymunkPhysicsEngine."""

    pass


# Temp fix for https://github.com/pythonarcade/arcade/issues/2074
@copy_dunders_unimplemented
class PymunkPhysicsEngine:
    """An Arcade-specific adapter for Pymunk.

    `Pymunk`_ is itself a Python adapter for the professional-grade
    `Chipmunk2D`_ engine. However, Arcade's ``PymunkPhysicsEngine``
    and its doc are currently in need of improvement.

     .. note:: Arcade would welcome assistance with improving it.

               If you are interested, please see Arcade's
               `CONTRIBUTING.md <CONTRIBUTING.md: https://github.com/pythonarcade/arcade/blob/development/CONTRIBUTING.md>`_

    Args:
        gravity:
            The direction where gravity is pointing.
            See :py:attr:`pymunk.Space.gravity` to learn more.
        damping:
            The default velocity loss per tick across the
            :py:class:`~pymunk.Space` for all :py:attr:`DYNAMIC`
            objects.

            * Override this for objects by passing different value
              :`add_sprite` or :py:meth:`add_spritelist`
            * See :py:attr:`pymunk.Space.damping` to learn more

        maximum_incline_on_ground:
            The maximum incline the ground can have before
            :py:meth:`is_on_ground` returns ``False``.

            * Defaults to ``0.708`` radians (a bit over 45 °)
            * Not a pymunk value, but an Arcade feature

    """

    DYNAMIC = NotImplemented
    """A ``body_type`` for moving Pymunk-controlled objects.

    An indirect approach is best for controlling the velocity and
    positioning of dynamic objects:

    * :py:meth:`apply_force`
    * :py:meth:`apply_impulse`

    .. warning:: Avoid setting velocity directly on dynamic objects!

                 If you need to set velocity directly, you may want to
                 pass :py:attr:`KINEMATIC` as the ``body_type`` to
                 :py:meth:`add_sprite` instead.

    If you :py:class:`set_velocity` directly anyway, the
    following may occur:

    #. Setting velocity approaches infinite acceleration
    #. ``f = m * a`` approaches ``f = m * infinity``
    #. Collisions go haywire

    In some games, you may be able to find a way to harness this for
    comedic effect.

    .. note:: This value is an alias of :py:attr:`pymunk.Body.DYNAMIC`.

              Please see the Pymunk page linked above to learn more.
    """
    STATIC = NotImplemented
    """A ``body_type`` for objects which do not move.

    This is best used for terrain or non-moving platforms.

    .. note:: This value is an alias of :py:attr:`pymunk.Body.STATIC`.

              Please see the Pymunk page linked above to learn more.
    """
    KINEMATIC = NotImplemented
    """A ``body_type`` for objects controlled by your code or Arcade's.

    When colliding, Kinematic objects:

    * act as if they have infinite mass
    * prevent joined and touching objects from sleeping

    This makes them excellent for game elements like moving platforms or
    hazards which move or crush game objects. You can control kinematic
    objects by setting their positions and velocities directly:

    * :py:meth:`set_velocity`
    * :py:meth:`set_velocity_horizontal`
    * :py:meth:`set_velocity_vertical`
    * :py:meth:`set_position`


    .. note:: This value is an alias of :py:attr:`pymunk.Body.KINEMATIC`.

              Please see the Pymunk page linked above to learn more.
    """
    MOMENT_INF = float("inf")

    def __init__(
        self, gravity=(0, 0), damping: float = 1.0, maximum_incline_on_ground: float = 0.708
    ) -> None:
        raise DudImportError

    def add_sprite(
        self,
        sprite: Sprite,
        mass: float = 1.0,
        friction: float = 0.2,
        elasticity: float | None = None,
        moment_of_inertia: float | None = None,  # correct spelling
        body_type: int = DYNAMIC,
        damping: float | None = None,
        gravity: tuple[float, float] | Vec2 | None = None,
        max_velocity: int | None = None,
        max_horizontal_velocity: int | None = None,
        max_vertical_velocity: int | None = None,
        radius: float = 0,
        collision_type: str | None = "default",
    ) -> None:
        """Add a sprite to the physics engine.

        Args:
            sprite:
                A :py:class:`.Sprite` to add
            mass:
                The mass of the object (Defaults to ``1.0``).
            friction:
                How much the object resists sliding against surfaces:

                .. list-table::
                   :header-rows: 0

                   * - ``0.0``
                     - Absolutely slippery with no resistance at all
                   * - ``0.2``
                     - Default (Waxed wood on very wet snow)
                   * - ``friction > 1.0``
                     - Very rough

                *Higher values may not make a meaningful difference.*

                See :py:attr:`pymunk.Shape.friction` to learn more.

            elasticity:
                How bouncy the object is.

                .. list-table::
                   :header-rows: 0

                   * - ``0.0``
                     - No bounce
                   * - ``0.99``
                     - Very bouncy
                   * - ``elasticity >= 1.0``
                     - May behave badly (breaks conservation of energy)

                See :py:attr:`pymunk.Shape.elasticity` to learn more.

            moment_of_inertia:
                How much force is needed to change the object's rotation (
                pass :py:attr:`MOMENT_INF` or ``float('inf')`` to "lock"
                its angle).

                See :py:attr:`pymunk.Shape.moment_of_inertia` to learn more.

            body_type:
                :py:attr:`DYNAMIC` (default), :py:attr:`KINEMATIC`, or
                :py:attr:`STATIC`.
            damping:
                Like air resistance. See the :py:class:`.PymunkPhysicsEngine`
                top-level doc.
            gravity:
                See the :py:class:`.PymunkPhysicsEngine` top-level doc.
            max_velocity:
                The maximum velocity of this object.
            max_horizontal_velocity:
                Clamp the velocity on the x axis to this.
            max_vertical_velocity:
                Clamp the velocity along the y axis to this.
            radius:
                The radius for the :py:class:`pymunk.Shape` created for
                the :py:class:`sprite <.Sprite>`.
            collision_type:
                Assign a collision name to this sprite. It will be used
                by :py:meth:`add_collision_handler` if called.
        """
        raise DudImplimentationError

    def add_sprite_list(
        self,
        sprite_list,
        mass: float = 1,
        friction: float = 0.2,
        elasticity: float | None = None,
        moment_of_inertia: float | None = None,
        body_type: int = DYNAMIC,
        damping: float | None = None,
        collision_type: str | None = None,
    ) -> None:
        """
        Add all sprites in a sprite list to the physics engine.

        Args:
            sprite_list:
                A list of sprites to add
            mass:
                The mass of the object (Defaults to ``1.0``).
            friction:
                How much the object resists sliding against surfaces:

                .. list-table::
                   :header-rows: 0

                   * - ``0.0``
                     - Absolutely slippery with no resistance at all
                   * - ``0.2``
                     - Default (Waxed wood on very wet snow)
                   * - ``friction > 1.0``
                     - Very rough

                *Higher values may not make a meaningful difference.*

                See :py:attr:`pymunk.Shape.friction` to learn more.

            elasticity:
                How bouncy the object is.

                .. list-table::
                   :header-rows: 0

                   * - ``0.0``
                     - No bounce
                   * - ``0.99``
                     - Very bouncy
                   * - ``elasticity >= 1.0``
                     - May behave badly (breaks conservation of energy)

                See :py:attr:`pymunk.Shape.elasticity` to learn more.

            moment_of_inertia:
                How much force is needed to change the object's rotation (
                pass :py:attr:`MOMENT_INF` or ``float('inf')`` to "lock"
                its angle).

                See :py:attr:`pymunk.Shape.moment_of_inertia` to learn more.

            body_type:
                :py:attr:`DYNAMIC` (default), :py:attr:`KINEMATIC`, or
                :py:attr:`STATIC`.
            damping:
                Like air resistance. See the :py:class:`.PymunkPhysicsEngine`
                top-level doc.
            collision_type:
                Assign a collision name to this sprite. It will be used
                by :py:meth:`add_collision_handler` if called.
        """
        raise DudImplimentationError

    def remove_sprite(self, sprite: Sprite) -> None:
        """Remove a sprite from the physics engine."""
        raise DudImplimentationError

    def get_sprite_for_shape(self, shape) -> Sprite | None:
        """Try to get the sprite registered with this engine for ``shape``.

        This method returns ``None`` when:

        * ``shape`` is ``None``
        * No :py:class:`.Sprite` was to this engine for ``shape``

        The second item may occur if you are using multiple instances of
        :py:class:`.PymunkPhysicsEngine`.

        Args:
            shape:
                A Pymunk shape to perform lookup for.
        Returns:
            A sprite for the ``shape``; ``None`` if no sprite is known.
        """
        raise DudImplimentationError

    def get_sprites_from_arbiter(self, arbiter) -> tuple[Sprite | None, Sprite | None]:
        """Given a collision arbiter, return the sprites associated with the collision."""
        raise DudImplimentationError

    def is_on_ground(self, sprite: Sprite) -> bool:
        """Return true of sprite is on top of something."""
        raise DudImplimentationError

    def apply_impulse(self, sprite: Sprite, impulse: tuple[float, float]) -> None:
        """Apply an impulse force on a sprite"""
        raise DudImplimentationError

    def set_position(self, sprite: Sprite, position: tuple[float, float]):
        """Set the position of the sprite in the engine's simulation.

        To learn more, please see :py:attr:`pymunk.Body.position`.

        Args:
            sprite:
                An Arcade :py:class:`.Sprite` known to the engine.
            position:
                A two-dimensional position in world space.
        """
        raise DudImplimentationError

    def set_rotation(self, sprite: Sprite, rotation: float) -> None:
        raise DudImplimentationError

    def set_velocity(self, sprite: Sprite, velocity: tuple[float, float]) -> None:
        """Directly set the velocity of a sprite known to the engine.

        .. warning:: Avoid using this on any :py:attr:`DYNAMIC` objects!

        This function is meant for :py:attr:`KINEMATIC` objects. Using
        it on a sprite added as :py:attr:`DYNAMIC` can cause strange and
        very broken behavior.

        To learn more, please see:

        * Pymunk's documentation on :py:attr:`~pymunk.Body.DYNAMIC` and
          :py:attr:`~pymunk.Body.KINEMATIC`

        """
        raise DudImplimentationError

    def add_collision_handler(
        self,
        first_type: str,
        second_type: str,
        begin_handler: Callable | None = None,
        pre_handler: Callable | None = None,
        post_handler: Callable | None = None,
        separate_handler: Callable | None = None,
    ) -> None:
        """
        Add code to handle collisions between objects.

        Args:
            first_type: The first type of object to check for collisions.
            second_type: The second type of object to check for collisions.
            begin_handler: Function to call when a collision begins.
            pre_handler: Function to call before a collision is resolved.
            post_handler: Function to call after a collision is resolved.
            separate_handler: Function to call when two objects
        """
        raise DudImplimentationError

    def resync_sprites(self) -> None:
        """
        Set visual sprites to be the same location as physics engine sprites.
        Call this after stepping the pymunk physics engine
        """
        raise DudImplimentationError

    def step(self, delta_time: float = 1 / 60.0, resync_sprites: bool = True) -> None:
        """
        Tell the physics engine to perform calculations.

        Args:
            delta_time: Time to move the simulation forward. Keep this
                value constant, do not use varying values for each step.
            resync_sprites: Resynchronize Arcade graphical sprites to be
                at the same location as their Pymunk counterparts.
                If running multiple steps per frame, set this to
                false for the first steps, and true for the last
                step that's part of the update.
        """
        raise DudImplimentationError

    def get_physics_object(self, sprite: Sprite) -> PymunkPhysicsObject:
        """
        Get the shape/body for a sprite.

        Args:
            sprite:
                The sprite to get the physics object for.
        """
        raise DudImplimentationError

    def apply_force(self, sprite: Sprite, force: tuple[float, float]):
        """
        Apply force to a Sprite.

        Args:
            sprite:
                The sprite to apply the force to.
            force:
                The force to apply to the sprite.
        """
        raise DudImplimentationError

    def set_horizontal_velocity(self, sprite: Sprite, velocity: float) -> None:
        """
        Set a sprite's velocity.

        Args:
            sprite:
                The sprite to set the velocity for.
            velocity:
                The velocity to set the sprite to.
        """
        raise DudImplimentationError

    def set_friction(self, sprite: Sprite, friction: float) -> None:
        """Set the friction a sprite experiences against other surfaces.

        This is how "rough" a sprite is during a collision with others:

        * ``0.0`` is the lowest value allowed (absolute slipperiness)
        * Higher values slide less on surfaces and other objects

        Pymunk allows setting ``friction`` higher than ``1.0``, but very
        high values might not have meaningful gameplay impact.

        .. _Simple Wikipedia's Article on Friction: https://simple.wikipedia.org/wiki/Friction

        To learn more, please see:

        * The :ref:`pymunk_platformer_tutorial-add_physics_engine` step
          of the :ref:`pymunk_platformer_tutorial`
        * `Simple Wikipedia's Article on Friction`_
        * :py:attr:`pymunk.Poly.friction`

        Args:
            sprite:
                The sprite to set the friction for.
            friction:
                How much the object resists sliding against surfaces.
        """
        raise DudImplimentationError

    def apply_opposite_running_force(self, sprite: Sprite) -> None:
        """
        If a sprite goes left while on top of a dynamic sprite, that sprite
        should get pushed to the right.
        """
        raise DudImplimentationError

    def check_grounding(self, sprite: Sprite) -> dict:
        """
        See if the player is on the ground. Used to see if we can jump.

        Args:
            sprite: The sprite to check if it is on the ground.
        """
        raise DudImplimentationError
