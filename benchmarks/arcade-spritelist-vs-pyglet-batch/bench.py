import math
import sys
import arcade
import pyglet
import random
import time

print(sys.argv)
if sys.argv[1] == 'arcade':
    is_arcade = True
elif sys.argv[1] == 'pyglet':
    is_arcade = False
else:
    raise Exception('')


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WALL_DIM_MIN = 10
WALL_DIM_MAX = 200
WALLS_COUNT = 10

BULLET_VELOCITY_MIN = 1/60
BULLET_VELOCITY_MAX = 10/60
BULLET_COUNT = 1000

SIMULATE_MINUTES = 1
SIMULATE_FPS = 60

# Predictable randomization so that each benchmark is identical
rng = random.Random(0)

bullets = arcade.SpriteList() if is_arcade else []
# walls = arcade.SpriteList()

window = arcade.Window()

# Seed chosen manually to create a wall distribution that looked good enough,
# like something I might create in a game.
rng.seed(2)
# for i in range(0, WALLS_COUNT):
#     wall = arcade.SpriteSolidColor(rng.randint(WALL_DIM_MIN, WALL_DIM_MAX), rng.randint(WALL_DIM_MIN, WALL_DIM_MAX), color=arcade.color.BLACK)
#     wall.position = rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT)
#     walls.append(wall)

png_path = 'benchmarks/arcade-spritelist-vs-pyglet-batch/image.png'
arcade_texture = arcade.load_texture(png_path)
def create_bullet_arcade():
    # Create a new bullet
    new_bullet = arcade.Sprite(path_or_texture=arcade_texture)
    new_bullet.position = (rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT))
    speed = rng.random() * (BULLET_VELOCITY_MAX - BULLET_VELOCITY_MIN) + BULLET_VELOCITY_MIN
    angle = rng.random() * math.pi * 2
    new_bullet.velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
    # Half of bullets are rotated, to test those code paths
    if rng.random() > 0.5:
        new_bullet.angle = 45
    return new_bullet

pyglet_batch = pyglet.graphics.Batch()
pyglet_image = pyglet.image.load(png_path)

def create_bullet_pyglet():
    # Create a new bullet
    new_bullet = pyglet.sprite.Sprite(pyglet_image, batch=pyglet_batch, subpixel=True)
    new_bullet.position = (rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT), 0)
    speed = rng.random() * (BULLET_VELOCITY_MAX - BULLET_VELOCITY_MIN) + BULLET_VELOCITY_MIN
    angle = rng.random() * math.pi * 2
    new_bullet.velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
    # Half of bullets are rotated, to test those code paths
    if rng.random() > 0.5:
        new_bullet.rotation = 45
    return new_bullet

def move_bullets_arcade():
    # Move all bullets
    for bullet in bullets:
        bullet.position = (bullet.position[0] + bullet.velocity[0], bullet.position[1] + bullet.velocity[1])
def move_bullets_pyglet():
    # Move all bullets
    for bullet in bullets:
        bullet.position = (bullet.position[0] + bullet.velocity[0], bullet.position[1] + bullet.velocity[1], 0)


def draw_bullets_arcade():
    bullets.draw()

def draw_bullets_pyglet():
    pyglet_batch.draw()

create_bullet = create_bullet_arcade if is_arcade else create_bullet_pyglet
move_bullets = move_bullets_arcade if is_arcade else move_bullets_pyglet
draw_bullets = draw_bullets_arcade if is_arcade else draw_bullets_pyglet

for i in range(0, BULLET_COUNT):
    bullets.append(create_bullet())

for i in range(0, int(SIMULATE_MINUTES * 60 * SIMULATE_FPS)):
    pyglet.clock.tick()

    window.switch_to()
    window.dispatch_events()

    move_bullets()
    window.dispatch_event('on_draw')

    window.clear(color=arcade.color.WHITE)
    # walls.draw()
    draw_bullets()
    window.flip()
