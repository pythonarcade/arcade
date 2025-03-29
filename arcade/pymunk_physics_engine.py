"""
Pymunk Physics Engine
"""

import logging
import math
from typing import Callable

import pymunk
from pyglet.math import Vec2

from arcade import Sprite

__all__ = ["PymunkPhysicsObject", "PymunkException", "PymunkPhysicsEngine"]

from arcade.utils import copy_dunders_unimplemented

LOG = logging.getLogger(__name__)


class PymunkPhysicsObject:
    """Object that holds pymunk body/shape for a sprite."""

    def __init__(self, body: pymunk.Body | None = None, shape: pymunk.Shape | None = None):
        self.body: pymunk.Body | None = body
        self.shape: pymunk.Shape | None = shape


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

    DYNAMIC = pymunk.Body.DYNAMIC
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
    STATIC = pymunk.Body.STATIC
    """A ``body_type`` for objects which do not move.

    This is best used for terrain or non-moving platforms.

    .. note:: This value is an alias of :py:attr:`pymunk.Body.STATIC`.

              Please see the Pymunk page linked above to learn more.
    """
    KINEMATIC = pymunk.Body.KINEMATIC
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
        # -- Pymunk
        self.space = pymunk.Space()
        self.space.gravity = gravity
        self.space.damping = damping
        self.collision_types: list[str] = []
        self.sprites: dict[Sprite, PymunkPhysicsObject] = {}
        self.non_static_sprite_list: list = []
        self.maximum_incline_on_ground = maximum_incline_on_ground

    def add_sprite(
        self,
        sprite: Sprite,
        mass: float = 1.0,
        friction: float = 0.2,
        elasticity: float | None = None,
        moment_of_inertia: float | None = None,  # correct spelling
        body_type: int = DYNAMIC,
        damping: float | None = None,
        gravity: pymunk.Vec2d | tuple[float, float] | Vec2 | None = None,
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

        if damping is not None:
            sprite.pymunk.damping = damping  # pyright: ignore [reportGeneralTypeIssues=false]

        if gravity is not None:
            sprite.pymunk.gravity = gravity  # pyright: ignore [reportGeneralTypeIssues=false]

        if max_velocity is not None:
            sprite.pymunk.max_velocity = (  # pyright: ignore [reportGeneralTypeIssues=false]
                max_velocity
            )

        if max_vertical_velocity is not None:
            sprite.pymunk.max_vertical_velocity = max_vertical_velocity  # pyright: ignore

        if max_horizontal_velocity is not None:
            sprite.pymunk.max_horizontal_velocity = max_horizontal_velocity  # pyright: ignore

        # See if the sprite already has been added
        if sprite in self.sprites:
            LOG.warning("Attempt to add a Sprite that has already been added. Ignoring.")
            return

        # Keep track of collision types
        if collision_type not in self.collision_types:
            # LOG.debug(f"Adding new collision type of {collision_type}.")
            self.collision_types.append(collision_type)  # type: ignore

        # Get a number associated with the string of collision_type
        collision_type_id = self.collision_types.index(collision_type)  # type: ignore

        # Default to a box moment_of_inertia
        if moment_of_inertia is None:
            moment_of_inertia = pymunk.moment_for_box(mass, (sprite.width, sprite.height))

        # Create the physics body
        body = pymunk.Body(mass, moment_of_inertia, body_type=body_type)

        # Set the body's position
        body.position = pymunk.Vec2d(sprite.center_x, sprite.center_y)
        body.angle = math.radians(sprite.angle)

        # Callback used if we need custom gravity, damping, velocity, etc.
        def velocity_callback(
            my_body: pymunk.Body, my_gravity: tuple[float, float], my_damping: float, dt: float
        ):
            """Used for custom damping, gravity, and max_velocity."""

            # Custom damping
            if sprite.pymunk.damping is not None:
                adj_damping = ((sprite.pymunk.damping * 100.0) / 100.0) ** dt
                # print(
                #     f"Custom damping {sprite.pymunk.damping} {my_damping} "
                #     "default to {adj_damping}"
                # )
                my_damping = adj_damping

            # Custom gravity
            if sprite.pymunk.gravity is not None:
                my_gravity = sprite.pymunk.gravity

            # Go ahead and update velocity
            pymunk.Body.update_velocity(my_body, my_gravity, my_damping, dt)

            # Now see if we are going too fast...

            # Support max velocity
            if sprite.pymunk.max_velocity:
                velocity = my_body.velocity.length
                if velocity > sprite.pymunk.max_velocity:
                    scale = sprite.pymunk.max_velocity / velocity
                    my_body.velocity = my_body.velocity * scale

            # Support max horizontal velocity
            if sprite.pymunk.max_horizontal_velocity:
                velocity = my_body.velocity.x
                if abs(velocity) > sprite.pymunk.max_horizontal_velocity:
                    velocity = sprite.pymunk.max_horizontal_velocity * math.copysign(1, velocity)
                    my_body.velocity = pymunk.Vec2d(velocity, my_body.velocity.y)

            # Support max vertical velocity
            if max_vertical_velocity:
                velocity = my_body.velocity[1]
                if abs(velocity) > max_vertical_velocity:
                    velocity = max_vertical_velocity * math.copysign(1, velocity)
                    my_body.velocity = pymunk.Vec2d(my_body.velocity.x, velocity)

        # Add callback if we need to do anything custom on this body
        # if damping or gravity or max_velocity or max_horizontal_velocity or max_vertical_velocity:
        if body_type == self.DYNAMIC:
            body.velocity_func = velocity_callback

        # Set the physics shape to the sprite's hitbox
        poly = sprite.hit_box.points
        scaled_poly = [[x * sprite.scale_x for x in z] for z in poly]
        shape = pymunk.Poly(body, scaled_poly, radius=radius)  # type: ignore

        # Set collision type, used in collision callbacks
        if collision_type:
            shape.collision_type = collision_type_id

        # How bouncy is the shape?
        if elasticity is not None:
            shape.elasticity = elasticity

        # Set shapes friction
        shape.friction = friction

        # Create physics object and add to list
        physics_object = PymunkPhysicsObject(body, shape)
        self.sprites[sprite] = physics_object
        if body_type != self.STATIC:
            self.non_static_sprite_list.append(sprite)

        # Add body and shape to pymunk engine
        self.space.add(body, shape)

        # Register physics engine with sprite, so we can remove from physics engine
        # if we tell the sprite to go away.
        sprite.register_physics_engine(self)

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
        for sprite in sprite_list:
            self.add_sprite(
                sprite=sprite,
                mass=mass,
                friction=friction,
                elasticity=elasticity,
                moment_of_inertia=moment_of_inertia,
                body_type=body_type,
                damping=damping,
                collision_type=collision_type,
            )

    def remove_sprite(self, sprite: Sprite) -> None:
        """Remove a sprite from the physics engine."""
        physics_object = self.sprites[sprite]
        self.space.remove(physics_object.body)  # type: ignore
        self.space.remove(physics_object.shape)  # type: ignore
        self.sprites.pop(sprite)
        if sprite in self.non_static_sprite_list:
            self.non_static_sprite_list.remove(sprite)

    def get_sprite_for_shape(self, shape: pymunk.Shape | None) -> Sprite | None:
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
        for sprite in self.sprites:
            if self.sprites[sprite].shape is shape:
                return sprite
        return None

    def get_sprites_from_arbiter(
        self, arbiter: pymunk.Arbiter
    ) -> tuple[Sprite | None, Sprite | None]:
        """Given a collision arbiter, return the sprites associated with the collision."""
        shape1, shape2 = arbiter.shapes
        sprite1 = self.get_sprite_for_shape(shape1)
        sprite2 = self.get_sprite_for_shape(shape2)
        return sprite1, sprite2

    def is_on_ground(self, sprite: Sprite) -> bool:
        """Return true of sprite is on top of something."""
        grounding = self.check_grounding(sprite)
        return grounding["body"] is not None

    def apply_impulse(self, sprite: Sprite, impulse: tuple[float, float]) -> None:
        """Apply an impulse force on a sprite"""
        physics_object = self.get_physics_object(sprite)
        if physics_object.body is None:
            raise PymunkException(
                "Tried to apply an impulse, but this physics object has no 'body' set."
            )
        physics_object.body.apply_impulse_at_local_point(impulse)

    def set_position(self, sprite: Sprite, position: pymunk.Vec2d | tuple[float, float]):
        """Set the position of the sprite in the engine's simulation.

        To learn more, please see :py:attr:`pymunk.Body.position`.

        Args:
            sprite:
                An Arcade :py:class:`.Sprite` known to the engine.
            position:
                A two-dimensional position in world space.
        """
        physics_object = self.get_physics_object(sprite)
        if physics_object.body is None:
            raise PymunkException(
                "Tried to set a position, but this physics object has no 'body' set."
            )
        physics_object.body.position = position

    def set_rotation(self, sprite: Sprite, rotation: float) -> None:
        """
        Set the rotation of the sprite

        Args:
            sprite:
                A sprite known to the physics engine.
            rotation:
                The angle in degrees (clockwise).
        """
        physics_object = self.get_physics_object(sprite)
        if physics_object.body is None:
            raise PymunkException(
                "Tried to set a rotation, but this physics object has no 'body' set."
            )
        physics_object.body.angle = math.radians(rotation)

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
        physics_object = self.get_physics_object(sprite)
        if physics_object.body is None:
            raise PymunkException(
                "Tried to set a velocity, but this physics object has no 'body' set."
            )
        physics_object.body.velocity = velocity

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

        if first_type not in self.collision_types:
            # LOG.debug(f"Adding new collision type of {first_type}.")
            self.collision_types.append(first_type)
        first_type_id = self.collision_types.index(first_type)

        if second_type not in self.collision_types:
            # LOG.debug(f"Adding new collision type of {second_type}.")
            self.collision_types.append(second_type)
        second_type_id = self.collision_types.index(second_type)

        def _f1(arbiter, space, data):
            sprite_a, sprite_b = self.get_sprites_from_arbiter(arbiter)
            should_process_collision = False
            if sprite_a is not None and sprite_b is not None and begin_handler is not None:
                should_process_collision = begin_handler(sprite_a, sprite_b, arbiter, space, data)
            return should_process_collision

        def _f2(arbiter, space, data):
            sprite_a, sprite_b = self.get_sprites_from_arbiter(arbiter)
            if sprite_a is not None and sprite_b is not None and post_handler is not None:
                post_handler(sprite_a, sprite_b, arbiter, space, data)

        def _f3(arbiter, space, data):
            sprite_a, sprite_b = self.get_sprites_from_arbiter(arbiter)
            if pre_handler is not None:
                return pre_handler(sprite_a, sprite_b, arbiter, space, data)

        def _f4(arbiter, space, data):
            sprite_a, sprite_b = self.get_sprites_from_arbiter(arbiter)
            if separate_handler:
                separate_handler(sprite_a, sprite_b, arbiter, space, data)

        h = self.space.add_collision_handler(first_type_id, second_type_id)
        if begin_handler:
            h.begin = _f1
        if post_handler:
            h.post_solve = _f2
        if pre_handler:
            h.pre_solve = _f3
        if separate_handler:
            h.separate = _f4

    def resync_sprites(self) -> None:
        """
        Set visual sprites to be the same location as physics engine sprites.
        Call this after stepping the pymunk physics engine
        """
        # Create copy in case a sprite wants to remove itself from the list as
        # we iterate through the list.
        sprites = self.non_static_sprite_list.copy()

        for sprite in sprites:
            # Get physics object for this sprite
            physics_object = self.sprites[sprite]

            original_position = sprite.position

            if physics_object.body:
                # Item is sleeping, skip
                if physics_object.body.is_sleeping:
                    continue

                new_position = physics_object.body.position
                new_angle = -math.degrees(physics_object.body.angle)

                # Calculate change in location, used in call-back
                dx = new_position[0] - original_position[0]
                dy = new_position[1] - original_position[1]
                d_angle = new_angle - sprite.angle

                # Update sprite to new location
                sprite.position = new_position
                sprite.angle = new_angle

                # Notify sprite we moved, in case animation needs to be updated
                sprite.pymunk_moved(self, dx, dy, d_angle)

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
        # Update physics
        # Use a constant time step, don't use delta_time
        # See "Game loop / moving time forward"
        # http://www.pymunk.org/en/latest/overview.html#game-loop-moving-time-forward
        self.space.step(delta_time)
        if resync_sprites:
            self.resync_sprites()

    def get_physics_object(self, sprite: Sprite) -> PymunkPhysicsObject:
        """
        Get the shape/body for a sprite.

        Args:
            sprite:
                The sprite to get the physics object for.
        """
        return self.sprites[sprite]

    def apply_force(self, sprite: Sprite, force: tuple[float, float]):
        """
        Apply force to a Sprite.

        Args:
            sprite:
                The sprite to apply the force to.
            force:
                The force to apply to the sprite.
        """
        physics_object = self.sprites[sprite]
        if physics_object.body is None:
            raise PymunkException(
                "Tried to apply a force, but this physics object has no 'body' set."
            )
        physics_object.body.apply_force_at_local_point(force, (0, 0))

    def set_horizontal_velocity(self, sprite: Sprite, velocity: float) -> None:
        """
        Set a sprite's velocity.

        Args:
            sprite:
                The sprite to set the velocity for.
            velocity:
                The velocity to set the sprite to.
        """
        physics_object = self.sprites[sprite]
        if physics_object.body is None:
            raise PymunkException(
                "Tried to set a velocity, but this physics object has no 'body' set."
            )
        cv = physics_object.body.velocity
        new_cv = (velocity, cv[1])
        physics_object.body.velocity = new_cv

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
        physics_object = self.sprites[sprite]
        if physics_object.shape is None:
            raise PymunkException(
                "Tried to set friction, but this physics object has no 'shape' set."
            )
        physics_object.shape.friction = friction

    def apply_opposite_running_force(self, sprite: Sprite) -> None:
        """
        If a sprite goes left while on top of a dynamic sprite, that sprite
        should get pushed to the right.
        """
        grounding = self.check_grounding(sprite)
        body = self.get_physics_object(sprite).body
        if not body:
            raise ValueError("Physics body not set.")

        if body.force[0] and grounding and grounding["body"]:
            grounding["body"].apply_force_at_world_point((-body.force[0], 0), grounding["position"])

    def check_grounding(self, sprite: Sprite) -> dict:
        """
        See if the player is on the ground. Used to see if we can jump.

        Args:
            sprite: The sprite to check if it is on the ground.
        """
        grounding = {
            "normal": pymunk.Vec2d.zero(),
            "penetration": pymunk.Vec2d.zero(),
            "impulse": pymunk.Vec2d.zero(),
            "position": pymunk.Vec2d.zero(),
            "body": None,
        }

        # creates a unit vector (Vector of length 1) in the same direction as the gravity
        gravity_unit_vector = pymunk.Vec2d(1, 0).rotated(self.space.gravity.angle)

        def f(arbiter: pymunk.Arbiter):
            """
            Checks if the the point of collision is in a way, that the sprite is on top of the other
            """
            # Gets the normal vector of the collision. This is the point of collision.
            n = arbiter.contact_point_set.normal

            # Checks if the x component of the gravity is in range of the maximum incline,
            # same for the y component.
            # This will work, as the normal AND gravity are both points on a circle with
            # a radius of 1. (both are unit vectors)
            if (
                gravity_unit_vector.x + self.maximum_incline_on_ground
                > n.x
                > gravity_unit_vector.x - self.maximum_incline_on_ground
                and gravity_unit_vector.y + self.maximum_incline_on_ground
                > n.y
                > gravity_unit_vector.y - self.maximum_incline_on_ground
            ):
                grounding["normal"] = n
                grounding["penetration"] = -arbiter.contact_point_set.points[0].distance
                grounding["body"] = arbiter.shapes[1].body
                grounding["impulse"] = arbiter.total_impulse
                grounding["position"] = arbiter.contact_point_set.points[0].point_b

        physics_object = self.sprites[sprite]
        if not physics_object.body:
            raise ValueError("No physics body set.")
        physics_object.body.each_arbiter(f)

        return grounding
