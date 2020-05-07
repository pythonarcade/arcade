"""
Pymunk Physics Engine
"""

import pymunk
import math
from typing import Callable
from typing import List
from typing import Dict
from typing import Optional
from arcade import Sprite

import logging
LOG = logging.getLogger(__name__)

class PymunkPhysicsObject:
    """ Object that holds pymunk body/shape for a sprite. """
    def __init__(self,
                 body: pymunk.Body = None,
                 shape: pymunk.Shape = None):
        """ Init """
        self.body: pymunk.Body = body
        self.shape: pymunk.Shape = shape


class PymunkPhysicsEngine:
    """
    Pymunk Physics Engine
    """

    DYNAMIC = pymunk.Body.DYNAMIC
    STATIC = pymunk.Body.STATIC
    KINEMATIC = pymunk.Body.KINEMATIC
    MOMENT_INF = pymunk.inf

    def __init__(self, gravity=(0, 0), damping: float = 1.0):
        # -- Pymunk
        self.space = pymunk.Space()
        self.space.gravity = gravity
        self.space.damping = damping
        self.collision_types: List[str] = []
        self.sprites: Dict[Sprite, PymunkPhysicsObject] = {}

    def add_sprite(self,
                   sprite: Sprite,
                   mass: float = 1,
                   friction: float = 0.2,
                   elasticity: Optional[float] = None,
                   moment=None,
                   body_type=DYNAMIC,
                   damping=None,
                   gravity=None,
                   max_velocity=None,
                   max_horizontal_velocity=None,
                   max_vertical_velocity=None,
                   radius: float = 0,
                   collision_type: str = "default",
                   ):
        """ Add a sprite to the physics engine. """

        LOG.debug(f"collision type={collision_type}")
        # See if the sprite already has been added
        if sprite in self.sprites:
            LOG.warning("Attempt to add a Sprite that has already been added. Ignoring.")
            return

        # Keep track of collision types
        if collision_type not in self.collision_types:
            LOG.debug(f"Adding new collision type of {collision_type}.")
            self.collision_types.append(collision_type)

        # Get a number associated with the string of collision_type
        collision_type_id = self.collision_types.index(collision_type)

        # Default to a box moment
        if moment is None:
            moment = pymunk.moment_for_box(mass, (sprite.width, sprite.height))

        # Create the physics body
        body = pymunk.Body(mass, moment, body_type=body_type)

        # Set the body's position
        body.position = pymunk.Vec2d(sprite.center_x, sprite.center_y)
        body.angle = math.radians(sprite.angle)

        # Callback used if we need custom gravity, damping, velocity, etc.
        def velocity_callback(my_body, my_gravity, my_damping, dt):
            """ Used for custom damping, gravity, and max_velocity. """

            # Custom damping
            if damping is not None:
                adj_damping = ((damping * 100) / 100) ** dt
                my_damping = adj_damping

            # Custom gravity
            if gravity is not None:
                my_gravity = gravity

            # Go ahead and update velocity
            pymunk.Body.update_velocity(my_body, my_gravity, my_damping, dt)

            # Now see if we are going too fast...

            # Support max velocity
            if max_velocity:
                velocity = my_body.velocity.length
                if velocity > max_velocity:
                    scale = max_velocity / velocity
                    my_body.velocity = my_body.velocity * scale

            # Support max horizontal velocity
            if max_horizontal_velocity:
                velocity = my_body.velocity.x
                if abs(velocity) > max_horizontal_velocity:
                    velocity = max_horizontal_velocity * math.copysign(1, velocity)
                    my_body.velocity = pymunk.Vec2d(velocity, my_body.velocity.y)

            # Support max vertical velocity
            if max_vertical_velocity:
                velocity = my_body.velocity[1]
                if abs(velocity) > max_vertical_velocity:
                    velocity = max_horizontal_velocity * math.copysign(1, velocity)
                    my_body.velocity = pymunk.Vec2d(my_body.velocity.x, velocity)

        # Add callback if we need to do anything custom on this body
        if damping or gravity or max_velocity or max_horizontal_velocity or max_vertical_velocity:
            body.velocity_func = velocity_callback

        # Set the physics shape to the sprite's hitbox
        poly = sprite.get_hit_box()
        scaled_poly = [[x * sprite.scale for x in z] for z in poly]
        shape = pymunk.Poly(body, scaled_poly, radius=radius)

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
                        moment=None,
                        body_type=DYNAMIC,
                        collision_type=None
                        ):
        """ Add all sprites in a sprite list to the physics engine. """

        for sprite in sprite_list:
            self.add_sprite(sprite=sprite,
                            mass=mass,
                            friction=friction,
                            elasticity=elasticity,
                            moment=moment,
                            body_type=body_type,
                            collision_type=collision_type)

    def remove_sprite(self, sprite: Sprite):
        """ Remove a sprite from the physics engine. """
        physics_object = self.sprites[sprite]
        self.space.remove(physics_object.body)
        self.space.remove(physics_object.shape)
        self.sprites.pop(sprite)

    def get_sprite_for_shape(self, shape) -> Optional[Sprite]:
        """ Given a shape, what sprite is associated with it? """
        for sprite in self.sprites:
            if self.sprites[sprite].shape is shape:
                return sprite
        return None

    def get_sprites_from_arbiter(self, arbiter):
        """ Given a collision arbiter, return the sprites associated with the collision. """
        shape1, shape2 = arbiter.shapes
        sprite1 = self.get_sprite_for_shape(shape1)
        sprite2 = self.get_sprite_for_shape(shape2)
        return sprite1, sprite2

    def is_on_ground(self, sprite):
        """ Return true of sprite is on top of something. """
        grounding = self.check_grounding(sprite)
        return grounding['body'] is not None

    def apply_impulse(self, sprite, impulse):
        """ Apply an impulse force on a sprite """
        physics_object = self.get_physics_object(sprite)
        physics_object.body.apply_impulse_at_local_point(impulse)

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
            begin_handler(sprite_a, sprite_b, arbiter, space, data)

        def _f2(arbiter, space, data):
            sprite_a, sprite_b = self.get_sprites_from_arbiter(arbiter)
            post_handler(sprite_a, sprite_b, arbiter, space, data)

        def _f3(arbiter, space, data):
            sprite_a, sprite_b = self.get_sprites_from_arbiter(arbiter)
            pre_handler(sprite_a, sprite_b, arbiter, space, data)

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
        """ Set visual sprites to be the same location as physics engine sprites. """
        # Create copy in case a sprite wants to remove itself from the list as
        # we iterate through the list.
        sprites = self.sprites.copy()
        for sprite in sprites:
            physics_object = self.sprites[sprite]
            new_angle = math.degrees(physics_object.body.angle)

            dx = physics_object.body.position.x - sprite.center_x
            dy = physics_object.body.position.y - sprite.center_y
            d_angle = new_angle - sprite.angle

            sprite.center_x = physics_object.body.position.x
            sprite.center_y = physics_object.body.position.y
            sprite.angle = new_angle

            sprite.pymunk_moved(self, dx, dy, d_angle)

    def step(self, delta_time: float = 1 / 60.0):
        """ Tell the physics engine to perform calculations. """
        # Update physics
        # Use a constant time step, don't use delta_time
        # See "Game loop / moving time forward"
        # http://www.pymunk.org/en/latest/overview.html#game-loop-moving-time-forward
        self.space.step(delta_time)
        self.resync_sprites()

    def get_physics_object(self, sprite: Sprite) -> PymunkPhysicsObject:
        """ Get the shape/body for a sprite. """
        return self.sprites[sprite]

    def apply_force(self, sprite, force):
        """ Apply force to a Sprite. """
        physics_object = self.sprites[sprite]
        physics_object.body.apply_force_at_local_point(force, (0, 0))

    def set_velocity(self, sprite, velocity):
        """ Apply force to a Sprite. """
        physics_object = self.sprites[sprite]
        cv = physics_object.body.velocity
        new_cv = (velocity, cv[1])
        physics_object.body.velocity = new_cv

    def set_friction(self, sprite, friction):
        """ Apply force to a Sprite. """
        physics_object = self.sprites[sprite]
        physics_object.shape.friction = friction

    def apply_opposite_running_force(self, sprite: Sprite):
        """
        If a sprite goes left while on top of a dynamic sprite, that sprite
        should get pushed to the right.
        """
        grounding = self.check_grounding(sprite)
        body = self.get_physics_object(sprite).body
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

        def f(arbiter):
            """ I don't know how this works. """
            n = -arbiter.contact_point_set.normal
            if n.y > grounding['normal'].y:
                grounding['normal'] = n
                grounding['penetration'] = -arbiter.contact_point_set.points[0].distance
                grounding['body'] = arbiter.shapes[1].body
                grounding['impulse'] = arbiter.total_impulse
                grounding['position'] = arbiter.contact_point_set.points[0].point_b

        physics_object = self.sprites[sprite]
        physics_object.body.each_arbiter(f)

        return grounding
