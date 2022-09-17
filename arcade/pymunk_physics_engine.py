"""
Pymunk Physics Engine
"""
import logging
import math
from typing import Callable, Dict, List, Optional, Union, Tuple

import pymunk

from arcade import Sprite
from pyglet.math import Vec2

LOG = logging.getLogger(__name__)


class PymunkPhysicsObject:
    """ Object that holds pymunk body/shape for a sprite. """
    def __init__(self,
                 body: pymunk.Body = None,
                 shape: pymunk.Shape = None):
        """ Init """
        self.body: Optional[pymunk.Body] = body
        self.shape: Optional[pymunk.Shape] = shape


class PymunkException(Exception):
    pass


class PymunkPhysicsEngine:
    """
    Pymunk Physics Engine

    :param gravity: The direction where gravity is pointing
    :param damping: The amount of speed which is kept to the next tick. a value of 1.0 means no speed loss,
                    while 0.9 has 10% loss of speed etc.
    :param maximum_incline_on_ground: The maximum incline the ground can have, before is_on_ground() becomes False
        default = 0.708 or a little bit over 45° angle
    """

    DYNAMIC = pymunk.Body.DYNAMIC
    STATIC = pymunk.Body.STATIC
    KINEMATIC = pymunk.Body.KINEMATIC
    MOMENT_INF = float('inf')

    def __init__(self, gravity=(0, 0), damping: float = 1.0, maximum_incline_on_ground: float = 0.708):
        # -- Pymunk
        self.space = pymunk.Space()
        self.space.gravity = gravity
        self.space.damping = damping
        self.collision_types: List[str] = []
        self.sprites: Dict[Sprite, PymunkPhysicsObject] = {}
        self.non_static_sprite_list: List = []
        self.maximum_incline_on_ground = maximum_incline_on_ground

    def add_sprite(self,
                   sprite: Sprite,
                   mass: float = 1,
                   friction: float = 0.2,
                   elasticity: Optional[float] = None,
                   moment_of_inertia: Optional[float] = None,  # correct spelling
                   body_type: int = DYNAMIC,
                   damping: Optional[float] = None,
                   gravity: Union[pymunk.Vec2d, Tuple[float, float], Vec2] = None,
                   max_velocity: int = None,
                   max_horizontal_velocity: int = None,
                   max_vertical_velocity: int = None,
                   radius: float = 0,
                   collision_type: Optional[str] = "default",
                   # the next two arguments are for backwards compatibility with prior versions
                   moment_of_intertia: Optional[float] = None,  # typo keyword, used by 2.6.2 and 2.6.3
                   moment: Optional[float] = None  # used prior to 2.6.2
                   ):
        """ Add a sprite to the physics engine.

            :param sprite: The sprite to add
            :param mass: The mass of the object. Defaults to 1
            :param friction: The friction the object has. Defaults to 0.2
            :param elasticity: How bouncy this object is. 0 is no bounce. Values of 1.0 and higher may behave badly.
            :param moment_of_inertia: The moment of inertia, or force needed to change angular momentum. \
            Providing infinite makes this object stuck in its rotation.
            :param body_type: The type of the body. Defaults to Dynamic, meaning, the body can move, rotate etc. \
            Providing STATIC makes it fixed to the world.
            :param damping: See class docs
            :param gravity: See class docs
            :param max_velocity: The maximum velocity of the object.
            :param max_horizontal_velocity: maximum velocity on the x axis
            :param max_vertical_velocity: maximum velocity on the y axis
            :param radius:
            :param collision_type:
            :param moment_of_intertia: Deprecated alias of moment_of_inertia compatible with a typo introduced in 2.6.2
            :param moment: Deprecated alias of moment_of_inertia compatible with versions <= 2.6.1
        """

        if damping is not None:
            sprite.pymunk.damping = damping

        if gravity is not None:
            sprite.pymunk.gravity = gravity

        if max_velocity is not None:
            sprite.pymunk.max_velocity = max_velocity

        if max_vertical_velocity is not None:
            sprite.pymunk.max_vertical_velocity = max_vertical_velocity

        if max_horizontal_velocity is not None:
            sprite.pymunk.max_horizontal_velocity = max_horizontal_velocity

        # See if the sprite already has been added
        if sprite in self.sprites:
            LOG.warning("Attempt to add a Sprite that has already been added. Ignoring.")
            return

        # Keep track of collision types
        if collision_type not in self.collision_types:
            LOG.debug(f"Adding new collision type of {collision_type}.")
            self.collision_types.append(collision_type)  # type: ignore

        # Get a number associated with the string of collision_type
        collision_type_id = self.collision_types.index(collision_type)  # type: ignore

        # Backwards compatibility for a typo introduced in 2.6.2 and for versions under 2.6.1
        # The current version is checked first, then the most common older form, then the typo
        moment_of_inertia = moment_of_inertia or moment or moment_of_intertia

        # Default to a box moment_of_inertia
        if moment_of_inertia is None:
            moment_of_inertia = pymunk.moment_for_box(mass, (sprite.width, sprite.height))

        # Create the physics body
        body = pymunk.Body(mass, moment_of_inertia, body_type=body_type)

        # Set the body's position
        body.position = pymunk.Vec2d(sprite.center_x, sprite.center_y)
        body.angle = math.radians(sprite.angle)

        # Callback used if we need custom gravity, damping, velocity, etc.
        def velocity_callback(my_body, my_gravity, my_damping, dt):
            """ Used for custom damping, gravity, and max_velocity. """

            # Custom damping
            if sprite.pymunk.damping is not None:
                adj_damping = ((sprite.pymunk.damping * 100.0) / 100.0) ** dt
                # print(f"Custom damping {sprite.pymunk.damping} {my_damping} default to {adj_damping}")
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
                    velocity = max_horizontal_velocity * math.copysign(1, velocity)
                    my_body.velocity = pymunk.Vec2d(my_body.velocity.x, velocity)

        # Add callback if we need to do anything custom on this body
        # if damping or gravity or max_velocity or max_horizontal_velocity or max_vertical_velocity:
        if body_type == self.DYNAMIC:
            body.velocity_func = velocity_callback

        # Set the physics shape to the sprite's hitbox
        poly = sprite.get_hit_box()
        scaled_poly = [[x * sprite.scale for x in z] for z in poly]
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

    def add_sprite_list(self,
                        sprite_list,
                        mass: float = 1,
                        friction: float = 0.2,
                        elasticity: Optional[float] = None,
                        moment_of_intertia: Optional[float] = None,
                        body_type: int = DYNAMIC,
                        damping: Optional[float] = None,
                        collision_type: Optional[str] = None
                        ):
        """ Add all sprites in a sprite list to the physics engine. """

        for sprite in sprite_list:
            self.add_sprite(sprite=sprite,
                            mass=mass,
                            friction=friction,
                            elasticity=elasticity,
                            moment_of_inertia=moment_of_intertia,
                            body_type=body_type,
                            damping=damping,
                            collision_type=collision_type)

    def remove_sprite(self, sprite: Sprite):
        """ Remove a sprite from the physics engine. """
        physics_object = self.sprites[sprite]
        self.space.remove(physics_object.body)  # type: ignore
        self.space.remove(physics_object.shape)  # type: ignore
        self.sprites.pop(sprite)
        if sprite in self.non_static_sprite_list:
            self.non_static_sprite_list.remove(sprite)

    def get_sprite_for_shape(self, shape: Optional[pymunk.Shape]) -> Optional[Sprite]:
        """ Given a shape, what sprite is associated with it? """
        for sprite in self.sprites:
            if self.sprites[sprite].shape is shape:
                return sprite
        return None

    def get_sprites_from_arbiter(self, arbiter: pymunk.Arbiter) -> Tuple[Optional[Sprite], Optional[Sprite]]:
        """ Given a collision arbiter, return the sprites associated with the collision. """
        shape1, shape2 = arbiter.shapes
        sprite1 = self.get_sprite_for_shape(shape1)
        sprite2 = self.get_sprite_for_shape(shape2)
        return sprite1, sprite2

    def is_on_ground(self, sprite: Sprite) -> bool:
        """ Return true of sprite is on top of something. """
        grounding = self.check_grounding(sprite)
        return grounding['body'] is not None

    def apply_impulse(self, sprite: Sprite, impulse: Tuple[float, float]):
        """ Apply an impulse force on a sprite """
        physics_object = self.get_physics_object(sprite)
        if physics_object.body is None:
            raise PymunkException("Tried to apply an impulse, but this physics object has no 'body' set.")
        physics_object.body.apply_impulse_at_local_point(impulse)

    def set_position(self, sprite: Sprite, position: Union[pymunk.Vec2d, Tuple[float, float]]):
        """ Apply an impulse force on a sprite """
        physics_object = self.get_physics_object(sprite)
        if physics_object.body is None:
            raise PymunkException("Tried to set a position, but this physics object has no 'body' set.")
        physics_object.body.position = position

    def set_velocity(self, sprite: Sprite, velocity: Tuple[float, float]):
        """ Apply an impulse force on a sprite """
        physics_object = self.get_physics_object(sprite)
        if physics_object.body is None:
            raise PymunkException("Tried to set a velocity, but this physics object has no 'body' set.")
        physics_object.body.velocity = velocity

    def add_collision_handler(self,
                              first_type: str,
                              second_type: str,
                              begin_handler: Callable = None,
                              pre_handler: Callable = None,
                              post_handler: Callable = None,
                              separate_handler: Callable = None):
        """ Add code to handle collisions between objects. """

        if first_type not in self.collision_types:
            LOG.debug(f"Adding new collision type of {first_type}.")
            self.collision_types.append(first_type)
        first_type_id = self.collision_types.index(first_type)

        if second_type not in self.collision_types:
            LOG.debug(f"Adding new collision type of {second_type}.")
            self.collision_types.append(second_type)
        second_type_id = self.collision_types.index(second_type)

        def _f1(arbiter, space, data):
            sprite_a, sprite_b = self.get_sprites_from_arbiter(arbiter)
            should_process_collision = begin_handler(sprite_a, sprite_b, arbiter, space, data)
            return should_process_collision

        def _f2(arbiter, space, data):
            sprite_a, sprite_b = self.get_sprites_from_arbiter(arbiter)
            if sprite_a is not None and sprite_b is not None:
                post_handler(sprite_a, sprite_b, arbiter, space, data)

        def _f3(arbiter, space, data):
            sprite_a, sprite_b = self.get_sprites_from_arbiter(arbiter)
            return pre_handler(sprite_a, sprite_b, arbiter, space, data)

        def _f4(arbiter, space, data):
            sprite_a, sprite_b = self.get_sprites_from_arbiter(arbiter)
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

    def resync_sprites(self):
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

            # Item is sleeping, skip
            if physics_object.body.is_sleeping:
                continue

            original_position = sprite.position
            new_position = physics_object.body.position
            new_angle = math.degrees(physics_object.body.angle)

            # Calculate change in location, used in call-back
            dx = new_position[0] - original_position[0]
            dy = new_position[1] - original_position[1]
            d_angle = new_angle - sprite.angle

            # Update sprite to new location
            sprite.position = new_position
            sprite.angle = new_angle

            # Notify sprite we moved, in case animation needs to be updated
            sprite.pymunk_moved(self, dx, dy, d_angle)

    def step(self,
             delta_time: float = 1 / 60.0,
             resync_sprites: bool = True):
        """
        Tell the physics engine to perform calculations.

        :param float delta_time: Time to move the simulation forward. Keep this
                                 value constant, do not use varying values for
                                 each step.
        :param bool resync_sprites: Resynchronize Arcade graphical sprites to be
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
        """ Get the shape/body for a sprite. """
        return self.sprites[sprite]

    def apply_force(self, sprite: Sprite, force: Tuple[float, float]):
        """ Apply force to a Sprite. """
        physics_object = self.sprites[sprite]
        if physics_object.body is None:
            raise PymunkException("Tried to apply a force, but this physics object has no 'body' set.")
        physics_object.body.apply_force_at_local_point(force, (0, 0))

    def set_horizontal_velocity(self, sprite: Sprite, velocity: float):
        """ Set a sprite's velocity """
        physics_object = self.sprites[sprite]
        if physics_object.body is None:
            raise PymunkException("Tried to set a velocity, but this physics object has no 'body' set.")
        cv = physics_object.body.velocity
        new_cv = (velocity, cv[1])
        physics_object.body.velocity = new_cv

    def set_friction(self, sprite: Sprite, friction: float):
        """ Apply force to a Sprite. """
        physics_object = self.sprites[sprite]
        if physics_object.shape is None:
            raise PymunkException("Tried to set friction, but this physics object has no 'shape' set.")
        physics_object.shape.friction = friction

    def apply_opposite_running_force(self, sprite: Sprite):
        """
        If a sprite goes left while on top of a dynamic sprite, that sprite
        should get pushed to the right.
        """
        grounding = self.check_grounding(sprite)
        body = self.get_physics_object(sprite).body
        if not body:
            raise ValueError("Physics body not set.")

        if body.force[0] and grounding and grounding['body']:
            grounding['body'].apply_force_at_world_point((-body.force[0], 0), grounding['position'])

    def check_grounding(self, sprite: Sprite):
        """ See if the player is on the ground. Used to see if we can jump. """
        grounding = {
            'normal': pymunk.Vec2d.zero(),
            'penetration': pymunk.Vec2d.zero(),
            'impulse': pymunk.Vec2d.zero(),
            'position': pymunk.Vec2d.zero(),
            'body': None
        }

        # creates a unit vector (Vector of length 1) in the same direction as the gravity
        gravity_unit_vector = pymunk.Vec2d(1, 0).rotated(self.space.gravity.angle)

        def f(arbiter: pymunk.Arbiter):
            """
            Checks if the the point of collision is in a way, that the sprite is on top of the other
            """
            # Gets the normal vector of the collision. This is the point of collision.
            n = arbiter.contact_point_set.normal

            # Checks if the x component of the gravity is in range of the maximum incline, same for the y component.
            # This will work, as the normal AND gravity are both points on a circle with a radius of 1.
            # (both are unit vectors)
            if gravity_unit_vector.x + self.maximum_incline_on_ground > \
               n.x > \
               gravity_unit_vector.x - self.maximum_incline_on_ground\
               and \
               gravity_unit_vector.y + self.maximum_incline_on_ground > \
               n.y > gravity_unit_vector.y - self.maximum_incline_on_ground:
                grounding['normal'] = n
                grounding['penetration'] = -arbiter.contact_point_set.points[0].distance
                grounding['body'] = arbiter.shapes[1].body
                grounding['impulse'] = arbiter.total_impulse
                grounding['position'] = arbiter.contact_point_set.points[0].point_b

        physics_object = self.sprites[sprite]
        if not physics_object.body:
            raise ValueError("No physics body set.")
        physics_object.body.each_arbiter(f)

        return grounding
