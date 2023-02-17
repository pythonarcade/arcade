import math
import arcade
import pyglet
import random
import time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WALL_DIM_MIN = 10
WALL_DIM_MAX = 200
WALLS_COUNT = 10

SIMULATE_MINUTES = 0.1
SIMULATE_FPS = 60

# Predictable randomization so that each benchmark is identical
rng = random.Random(0)

walls = arcade.SpriteList(use_spatial_hash=True)

window = arcade.Window()

# Seed chosen manually to create a wall distribution that looked good enough,
# like something I might create in a game.
rng.seed(2)
for i in range(0, WALLS_COUNT):
    wall = arcade.SpriteSolidColor(rng.randint(WALL_DIM_MIN, WALL_DIM_MAX), rng.randint(WALL_DIM_MIN, WALL_DIM_MAX), color=arcade.color.BLACK)
    wall.position = rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT)
    walls.append(wall)

# Check for line-of-sight
def check_ray():
    x = rng.randint(0, SCREEN_WIDTH)
    y = rng.randint(0, SCREEN_HEIGHT)
    hit = arcade.has_line_of_sight(origin, (x, y), walls)
    return x, y, hit

origin = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
rays = []
for i in range(0, int(SIMULATE_MINUTES * 60 * SIMULATE_FPS)):
    pyglet.clock.tick()

    window.switch_to()
    window.dispatch_events()

    rays[:] = [check_ray() for x in range(1000)]

    window.dispatch_event('on_draw')

    window.clear(color=arcade.color.WHITE)
    walls.draw()
    
    # only draw a few:
    # A) so the benchmark isn't dominated by slow draw_line calls
    # B) to validate that the line-of-sight checks are accurate
    # C) so you get a visual indicator of framerate
    for ray in rays[:10]:
        arcade.draw_line(origin[0], origin[1], ray[0], ray[1], arcade.color.BLUE if ray[2] else arcade.color.RED, 2)
    window.flip()
