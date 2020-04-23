"""
Pymunk Physics Engine
"""

import pymunk
import math
from arcade import Sprite
from arcade import SpriteList

class _PhysicsObject:
    def __init__(self, body=None, shape=None):
        self.body = body
        self.shape = shape


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
        self.sprites = {}


    def add_sprite(self,
                   sprite: Sprite,
                   mass: float=1,
                   friction: float=0.2,
                   moment=None,
                   body_type=DYNAMIC,
                   damping=None,
                   gravity=(0, 0),
                   max_velocity=None,
                   radius=0
                   ):

        if sprite in self.sprites:
            print("Sprite already in added.")

        if moment is None:
            moment = pymunk.moment_for_box(mass, (sprite.width, sprite.height))

        body = pymunk.Body(mass, moment, body_type=body_type)
        body.position = pymunk.Vec2d(sprite.center_x, sprite.center_y)

        def velocity_callback(my_body, my_gravity, my_damping, dt):
            if damping is not None:

                adj_damping = ((damping * 100) / 100) ** (dt)
                # print(damping, my_damping, adj_damping)
                my_damping = adj_damping
            if gravity is not None:
                my_gravity = gravity

            pymunk.Body.update_velocity(my_body, my_gravity, my_damping, dt)

            if max_velocity:

                l = my_body.velocity.length
                if l > max_velocity:
                    scale = max_velocity / l
                    body.velocity = body.velocity * scale

        if damping is not None:
            body.velocity_func = velocity_callback

        poly = sprite.get_hit_box()

        scaled_poly = [[x * sprite.scale for x in z] for z in poly]

        shape = pymunk.Poly(body, scaled_poly, radius=radius)
        shape.friction = friction

        physics_object = _PhysicsObject(body, shape)
        self.sprites[sprite] = physics_object

        self.space.add(body, shape)

    def add_sprite_list(self,
                        sprite_list: SpriteList,
                        mass: float = 1,
                        friction: float = 0.2,
                        moment=None,
                        body_type=DYNAMIC
                        ):

        for sprite in sprite_list:
            self.add_sprite(sprite, mass, friction, moment, body_type)

    def resync_sprites(self):
        for sprite in self.sprites:
            physics_object = self.sprites[sprite]
            sprite.center_x = physics_object.body.position.x
            sprite.center_y = physics_object.body.position.y
            sprite.angle = math.degrees(physics_object.body.angle)

    def step(self, delta_time = 1/60.0):
        # Update physics
        # Use a constant time step, don't use delta_time
        # See "Game loop / moving time forward"
        # http://www.pymunk.org/en/latest/overview.html#game-loop-moving-time-forward
        self.space.step(delta_time)

    def apply_force(self, sprite, force):
        physics_object = self.sprites[sprite]
        physics_object.body.apply_force_at_local_point(force, (0, 0))
