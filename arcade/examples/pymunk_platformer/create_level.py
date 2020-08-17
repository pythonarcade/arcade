"""
This code creates the layout of level one.
"""
import pymunk

from arcade.examples.pymunk_platformer.physics_utility import (
    PymunkSprite,
)
from arcade.examples.pymunk_platformer.constants import *


def create_floor(space, sprite_list):
    """ Create a bunch of blocks for the floor. """
    for x in range(-1000, 2000, SPRITE_SIZE):
        y = SPRITE_SIZE / 2
        sprite = PymunkSprite(":resources:images/tiles/grassMid.png", x, y, scale=0.5, body_type=pymunk.Body.STATIC)
        sprite_list.append(sprite)
        space.add(sprite.body, sprite.shape)


def create_platform(space, sprite_list, start_x, y, count):
    """ Create a platform """
    for x in range(start_x, start_x + count * SPRITE_SIZE + 1, SPRITE_SIZE):
        sprite = PymunkSprite(":resources:images/tiles/grassMid.png", x, y, scale=0.5, body_type=pymunk.Body.STATIC)
        sprite_list.append(sprite)
        space.add(sprite.body, sprite.shape)


def create_level_1(space, static_sprite_list, dynamic_sprite_list):
    """ Create level one. """
    create_floor(space, static_sprite_list)
    create_platform(space, static_sprite_list, 200, SPRITE_SIZE * 3, 3)
    create_platform(space, static_sprite_list, 500, SPRITE_SIZE * 6, 3)
    create_platform(space, static_sprite_list, 200, SPRITE_SIZE * 9, 3)

    # Create the stacks of boxes
    for column in range(6):
        for row in range(column):
            x = 600 + column * SPRITE_SIZE
            y = (3 * SPRITE_SIZE / 2) + row * SPRITE_SIZE
            sprite = PymunkSprite(":resources:images/tiles/boxCrate_double.png", x, y, scale=0.5, friction=0.4)
            dynamic_sprite_list.append(sprite)
            space.add(sprite.body, sprite.shape)
