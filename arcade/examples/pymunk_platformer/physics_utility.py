import arcade
from arcade.examples.pymunk_platformer.constants import (
    DEFAULT_FRICTION,
    DEFAULT_MASS,
)

import pymunk
import math


class PymunkSprite(arcade.Sprite):
    """
    We need a Sprite and a Pymunk physics object. This class blends them
    together.
    """
    def __init__(self,
                 filename,
                 center_x=0,
                 center_y=0,
                 scale=1,
                 mass=DEFAULT_MASS,
                 moment=None,
                 friction=DEFAULT_FRICTION,
                 body_type=pymunk.Body.DYNAMIC):

        super().__init__(filename, scale=scale, center_x=center_x, center_y=center_y)

        width = self.texture.width * scale
        height = self.texture.height * scale

        if moment is None:
            moment = pymunk.moment_for_box(mass, (width, height))

        self.body = pymunk.Body(mass, moment, body_type=body_type)
        self.body.position = pymunk.Vec2d(center_x, center_y)

        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.friction = friction


def check_grounding(player):
    """ See if the player is on the ground. Used to see if we can jump. """
    grounding = {
        'normal': pymunk.Vec2d.zero(),
        'penetration': pymunk.Vec2d.zero(),
        'impulse': pymunk.Vec2d.zero(),
        'position': pymunk.Vec2d.zero(),
        'body': None
    }

    def f(arbiter):
        n = -arbiter.contact_point_set.normal
        if n.y > grounding['normal'].y:
            grounding['normal'] = n
            grounding['penetration'] = -arbiter.contact_point_set.points[0].distance
            grounding['body'] = arbiter.shapes[1].body
            grounding['impulse'] = arbiter.total_impulse
            grounding['position'] = arbiter.contact_point_set.points[0].point_b

    player.body.each_arbiter(f)

    return grounding


def resync_physics_sprites(sprite_list):
    """ Move sprites to where physics objects are """
    for sprite in sprite_list:
        sprite.center_x = sprite.shape.body.position.x
        sprite.center_y = sprite.shape.body.position.y
        sprite.angle = math.degrees(sprite.shape.body.angle)
